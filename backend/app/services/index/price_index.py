from collections import defaultdict
from datetime import date, timedelta

from sqlalchemy import delete, select
from sqlalchemy.orm import Session
from app.core.constants import (
    INDEX_ELIGIBLE_SOURCE_CODES,
    REAL_SOURCE_TYPES,
)

from app.models import (
    DataSource,
    FareQuote,
    PriceIndexValue,
    Route,
)


SUPPORTED_FREQUENCIES = {
    "daily",
    "weekly",
    "monthly",
}


def get_period_start(
    value: date,
    frequency: str,
) -> date:
    if frequency == "daily":
        return value

    if frequency == "weekly":
        return value - timedelta(
            days=value.weekday()
        )

    if frequency == "monthly":
        return value.replace(day=1)

    raise ValueError(
        f"Unsupported frequency: {frequency}"
    )


def average(
    values: list[float],
) -> float:
    return sum(values) / len(values)


def calculate_price_index(
    db: Session,
    frequency: str = "daily",
) -> dict:
    if frequency not in SUPPORTED_FREQUENCIES:
        raise ValueError(
            "frequency must be daily, weekly, or monthly"
        )

    quotes = db.scalars(
        select(FareQuote)
        .join(
            DataSource,
            FareQuote.source_id
            == DataSource.id, 
        )
        .where(
            FareQuote.is_clean.is_(True),
            FareQuote.is_outlier.is_(False),
            FareQuote.availability_status
            == "available",
            FareQuote.total_fare.is_not(None),


            DataSource.source_type.in_(
                REAL_SOURCE_TYPES
            ),


            DataSource.code.in_(
                INDEX_ELIGIBLE_SOURCE_CODES
            ),
        )
        .order_by(FareQuote.collected_at)
    ).all()

    if not quotes:
        raise ValueError(
            "No clean fare quotes available"
        )

    period_quotes = defaultdict(list)

    for quote in quotes:
        quote_date = quote.collected_at.date()

        period = get_period_start(
            quote_date,
            frequency,
        )

        period_quotes[period].append(quote)

    current_period = max(
        period_quotes.keys()
    )

    baseline_by_group = {}
    baseline_period_by_group = {}

    for quote in quotes:
        group_key = (
            quote.route_id,
            quote.advance_purchase_days,
        )

        quote_period = get_period_start(
            quote.collected_at.date(),
            frequency,
        )

        existing_period = (
            baseline_period_by_group.get(
                group_key
            )
        )

        if (
            existing_period is None
            or quote_period < existing_period
        ):
            baseline_period_by_group[
                group_key
            ] = quote_period

    baseline_values = defaultdict(list)

    for quote in quotes:
        group_key = (
            quote.route_id,
            quote.advance_purchase_days,
        )

        quote_period = get_period_start(
            quote.collected_at.date(),
            frequency,
        )

        if (
            quote_period
            == baseline_period_by_group[
                group_key
            ]
        ):
            baseline_values[
                group_key
            ].append(
                float(quote.total_fare)
            )

    for group_key, values in (
        baseline_values.items()
    ):
        baseline_by_group[
            group_key
        ] = average(values)

    current_values = defaultdict(list)

    for quote in period_quotes[
        current_period
    ]:
        group_key = (
            quote.route_id,
            quote.advance_purchase_days,
        )

        current_values[
            group_key
        ].append(
            float(quote.total_fare)
        )

    route_subindices = defaultdict(list)
    route_sample_sizes = defaultdict(int)

    for group_key, values in (
        current_values.items()
    ):
        route_id, advance_days = group_key

        baseline = baseline_by_group.get(
            group_key
        )

        if (
            baseline is None
            or baseline <= 0
        ):
            continue

        current_average = average(values)

        sub_index = (
            current_average / baseline
        ) * 100

        route_subindices[
            route_id
        ].append(sub_index)

        route_sample_sizes[
            route_id
        ] += len(values)

    routes = db.scalars(
        select(Route)
        .where(Route.active.is_(True))
    ).all()

    route_map = {
        route.id: route
        for route in routes
    }

    route_results = []

    weighted_sum = 0.0
    total_weight = 0.0
    total_sample_size = 0

    for route_id, indices in (
        route_subindices.items()
    ):
        route = route_map.get(route_id)

        if route is None:
            continue

        route_index = average(indices)

        weight = float(route.weight)

        sample_size = (
            route_sample_sizes[
                route_id
            ]
        )

        weighted_sum += (
            route_index * weight
        )

        total_weight += weight
        total_sample_size += sample_size

        route_results.append(
            {
                "route_id": route.id,
                "origin": route.origin,
                "destination": (
                    route.destination
                ),
                "weight": weight,
                "index_value": round(
                    route_index,
                    4,
                ),
                "sample_size": sample_size,
            }
        )

    if total_weight <= 0:
        raise ValueError(
            "No weighted route indices available"
        )

    overall_index = (
        weighted_sum / total_weight
    )

    db.execute(
        delete(PriceIndexValue)
        .where(
            PriceIndexValue.period_start
            == current_period,
            PriceIndexValue.frequency
            == frequency,
        )
    )

    for result in route_results:
        db.add(
            PriceIndexValue(
                period_start=current_period,
                frequency=frequency,
                route_id=result["route_id"],
                index_value=(
                    result["index_value"]
                ),
                base_value=100.0,
                sample_size=(
                    result["sample_size"]
                ),
            )
        )

    db.add(
        PriceIndexValue(
            period_start=current_period,
            frequency=frequency,
            route_id=None,
            index_value=round(
                overall_index,
                4,
            ),
            base_value=100.0,
            sample_size=total_sample_size,
        )
    )

    db.commit()

    route_results.sort(
        key=lambda item: (
            item["origin"],
            item["destination"],
        )
    )

    return {
        "frequency": frequency,
        "period_start": current_period,
        "index_value": round(
            overall_index,
            4,
        ),
        "base_value": 100.0,
        "sample_size": total_sample_size,
        "routes_used": len(
            route_results
        ),
        "route_indices": route_results,
        "methodology": (
            "Prototype weighted fixed-basket "
            "fare index"
        ),
    }
def rebuild_price_index_history(
    db: Session,
    frequency: str = "daily",
) -> dict:
    if frequency not in SUPPORTED_FREQUENCIES:
        raise ValueError(
            "frequency must be daily, weekly, or monthly"
        )

    quotes = db.scalars(
    select(FareQuote)
    .join(
        DataSource,
        FareQuote.source_id
        == DataSource.id,
    )
    .where(
        FareQuote.is_clean.is_(True),
        FareQuote.is_outlier.is_(False),
        FareQuote.availability_status
        == "available",
        FareQuote.total_fare.is_not(None),


        DataSource.source_type.in_(
            REAL_SOURCE_TYPES
        ),

        DataSource.code.in_(
            INDEX_ELIGIBLE_SOURCE_CODES
        ),
    )
    .order_by(FareQuote.collected_at)
).all()

    if not quotes:
        raise ValueError(
            "No clean fare quotes available"
        )

    period_quotes = defaultdict(list)

    for quote in quotes:
        period = get_period_start(
            quote.collected_at.date(),
            frequency,
        )

        period_quotes[
            period
        ].append(quote)

    periods = sorted(
        period_quotes.keys()
    )

    baseline_period_by_group = {}

    for quote in quotes:
        group_key = (
            quote.route_id,
            quote.advance_purchase_days,
        )

        period = get_period_start(
            quote.collected_at.date(),
            frequency,
        )

        existing = (
            baseline_period_by_group.get(
                group_key
            )
        )

        if (
            existing is None
            or period < existing
        ):
            baseline_period_by_group[
                group_key
            ] = period

    baseline_values = defaultdict(list)

    for quote in quotes:
        group_key = (
            quote.route_id,
            quote.advance_purchase_days,
        )

        period = get_period_start(
            quote.collected_at.date(),
            frequency,
        )

        if (
            period
            == baseline_period_by_group[
                group_key
            ]
        ):
            baseline_values[
                group_key
            ].append(
                float(quote.total_fare)
            )

    baseline_by_group = {
        group_key: average(values)
        for group_key, values
        in baseline_values.items()
    }

    routes = db.scalars(
        select(Route)
        .where(Route.active.is_(True))
    ).all()

    route_map = {
        route.id: route
        for route in routes
    }

    db.execute(
        delete(PriceIndexValue)
        .where(
            PriceIndexValue.frequency
            == frequency
        )
    )

    history = []

    for period in periods:
        current_values = defaultdict(list)

        for quote in period_quotes[
            period
        ]:
            group_key = (
                quote.route_id,
                quote.advance_purchase_days,
            )

            current_values[
                group_key
            ].append(
                float(quote.total_fare)
            )

        route_subindices = defaultdict(list)
        route_sample_sizes = defaultdict(int)

        for group_key, values in (
            current_values.items()
        ):
            route_id, _ = group_key

            baseline = (
                baseline_by_group.get(
                    group_key
                )
            )

            if (
                baseline is None
                or baseline <= 0
            ):
                continue

            current_average = average(
                values
            )

            sub_index = (
                current_average
                / baseline
            ) * 100

            route_subindices[
                route_id
            ].append(
                sub_index
            )

            route_sample_sizes[
                route_id
            ] += len(values)

        weighted_sum = 0.0
        total_weight = 0.0
        total_sample_size = 0

        route_results = []

        for route_id, indices in (
            route_subindices.items()
        ):
            route = route_map.get(
                route_id
            )

            if route is None:
                continue

            route_index = average(
                indices
            )

            weight = float(
                route.weight
            )

            sample_size = (
                route_sample_sizes[
                    route_id
                ]
            )

            weighted_sum += (
                route_index
                * weight
            )

            total_weight += weight
            total_sample_size += (
                sample_size
            )

            route_results.append(
                (
                    route,
                    route_index,
                    sample_size,
                )
            )

        if total_weight <= 0:
            continue

        overall_index = (
            weighted_sum
            / total_weight
        )

        for (
            route,
            route_index,
            sample_size,
        ) in route_results:
            db.add(
                PriceIndexValue(
                    period_start=period,
                    frequency=frequency,
                    route_id=route.id,
                    index_value=round(
                        route_index,
                        4,
                    ),
                    base_value=100.0,
                    sample_size=(
                        sample_size
                    ),
                )
            )

        db.add(
            PriceIndexValue(
                period_start=period,
                frequency=frequency,
                route_id=None,
                index_value=round(
                    overall_index,
                    4,
                ),
                base_value=100.0,
                sample_size=(
                    total_sample_size
                ),
            )
        )

        history.append(
            {
                "period_start": period,
                "index_value": round(
                    overall_index,
                    4,
                ),
                "sample_size": (
                    total_sample_size
                ),
                "routes_used": len(
                    route_results
                ),
            }
        )

    db.commit()

    return {
        "frequency": frequency,
        "periods_calculated": len(
            history
        ),
        "start_period": (
            history[0]["period_start"]
            if history
            else None
        ),
        "end_period": (
            history[-1]["period_start"]
            if history
            else None
        ),
        "history": history,
    }