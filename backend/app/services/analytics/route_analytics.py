from collections import defaultdict

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import (
    FareQuote,
    PriceIndexValue,
    Route,
)


def get_latest_route_quotes(
    db: Session,
    route_id: int,
) -> list[FareQuote]:
    latest_date = db.scalar(
        select(
            func.max(
                func.date(
                    FareQuote.collected_at
                )
            )
        )
        .where(
            FareQuote.route_id == route_id,
            FareQuote.is_clean.is_(True),
            FareQuote.is_outlier.is_(False),
            FareQuote.availability_status
            == "available",
            FareQuote.total_fare.is_not(None),
        )
    )

    if latest_date is None:
        return []

    return db.scalars(
        select(FareQuote)
        .where(
            FareQuote.route_id == route_id,
            FareQuote.is_clean.is_(True),
            FareQuote.is_outlier.is_(False),
            FareQuote.availability_status
            == "available",
            FareQuote.total_fare.is_not(None),
            func.date(
                FareQuote.collected_at
            )
            == latest_date,
        )
        .order_by(
            FareQuote.advance_purchase_days
        )
    ).all()


def get_latest_route_index(
    db: Session,
    route_id: int,
) -> PriceIndexValue | None:
    return db.scalar(
        select(PriceIndexValue)
        .where(
            PriceIndexValue.route_id
            == route_id,
            PriceIndexValue.frequency
            == "daily",
        )
        .order_by(
            PriceIndexValue.period_start
            .desc()
        )
        .limit(1)
    )


def get_previous_route_index(
    db: Session,
    route_id: int,
    latest_period,
) -> PriceIndexValue | None:
    return db.scalar(
        select(PriceIndexValue)
        .where(
            PriceIndexValue.route_id
            == route_id,
            PriceIndexValue.frequency
            == "daily",
            PriceIndexValue.period_start
            < latest_period,
        )
        .order_by(
            PriceIndexValue.period_start
            .desc()
        )
        .limit(1)
    )


def calculate_change(
    current: float,
    previous: float | None,
) -> float:
    if previous is None or previous == 0:
        return 0.0

    return round(
        (
            (current - previous)
            / previous
        )
        * 100,
        4,
    )


def get_window_movements(
    db: Session,
    route_id: int,
) -> dict[str, float | None]:
    quotes = db.scalars(
        select(FareQuote)
        .where(
            FareQuote.route_id == route_id,
            FareQuote.is_clean.is_(True),
            FareQuote.is_outlier.is_(False),
            FareQuote.availability_status
            == "available",
            FareQuote.total_fare.is_not(None),
        )
        .order_by(
            FareQuote.collected_at
        )
    ).all()

    grouped = defaultdict(
        lambda: defaultdict(list)
    )

    for quote in quotes:
        grouped[
            quote.advance_purchase_days
        ][
            quote.collected_at.date()
        ].append(
            float(quote.total_fare)
        )

    result = {}

    for days in [
        1,
        7,
        15,
        30,
        45,
    ]:
        date_groups = grouped.get(
            days,
            {},
        )

        key = f"T+{days}"

        if not date_groups:
            result[key] = None
            continue

        dates = sorted(
            date_groups.keys()
        )

        first_values = date_groups[
            dates[0]
        ]

        latest_values = date_groups[
            dates[-1]
        ]

        reference_fare = (
            sum(first_values)
            / len(first_values)
        )

        latest_fare = (
            sum(latest_values)
            / len(latest_values)
        )

        if reference_fare <= 0:
            result[key] = None
            continue

        movement = (
            (
                latest_fare
                - reference_fare
            )
            / reference_fare
        ) * 100

        result[key] = round(
            movement,
            2,
        )

    return result


def get_route_summary(
    db: Session,
    route: Route,
) -> dict:
    quotes = get_latest_route_quotes(
        db,
        route.id,
    )

    fares = [
        float(quote.total_fare)
        for quote in quotes
        if quote.total_fare is not None
    ]

    average_fare = (
        sum(fares) / len(fares)
        if fares
        else 0.0
    )

    latest_index = get_latest_route_index(
        db,
        route.id,
    )

    index_value = (
        float(latest_index.index_value)
        if latest_index is not None
        else 0.0
    )

    previous_index = None

    if latest_index is not None:
        previous = get_previous_route_index(
            db,
            route.id,
            latest_index.period_start,
        )

        if previous is not None:
            previous_index = float(
                previous.index_value
            )

    return {
        "id": route.id,
        "origin": route.origin,
        "destination": route.destination,
        "weight": route.weight,

        "windows": get_window_movements(
            db,
            route.id,
        ),

        "average_fare": round(
            average_fare,
            2,
        ),
        "minimum_fare": (
            round(min(fares), 2)
            if fares
            else 0.0
        ),
        "maximum_fare": (
            round(max(fares), 2)
            if fares
            else 0.0
        ),
        "index_value": round(
            index_value,
            4,
        ),
        "daily_change_pct": (
            calculate_change(
                index_value,
                previous_index,
            )
        ),
        "sample_size": len(
            fares
        ),
    }


def get_route_detail(
    db: Session,
    route: Route,
) -> dict:
    summary = get_route_summary(
        db,
        route,
    )

    latest_quotes = (
        get_latest_route_quotes(
            db,
            route.id,
        )
    )

    lead_time_groups = defaultdict(
        list
    )

    for quote in latest_quotes:
        if quote.total_fare is not None:
            lead_time_groups[
                quote.advance_purchase_days
            ].append(
                float(
                    quote.total_fare
                )
            )

    lead_time_fares = []

    for days in sorted(
        lead_time_groups.keys()
    ):
        values = lead_time_groups[
            days
        ]

        lead_time_fares.append(
            {
                "advance_days": days,
                "average_fare": round(
                    sum(values)
                    / len(values),
                    2,
                ),
                "sample_size": len(
                    values
                ),
            }
        )

    history_values = db.scalars(
        select(PriceIndexValue)
        .where(
            PriceIndexValue.route_id
            == route.id,
            PriceIndexValue.frequency
            == "daily",
        )
        .order_by(
            PriceIndexValue.period_start
        )
    ).all()

    return {
        **summary,
        "lead_time_fares": (
            lead_time_fares
        ),
        "history": [
            {
                "date": (
                    value.period_start
                ),
                "index": (
                    value.index_value
                ),
            }
            for value in history_values
        ],
    }