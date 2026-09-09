from collections import defaultdict

from sqlalchemy import select

from app.core.constants import (
    INDEX_ELIGIBLE_SOURCE_CODES,
)
from app.models import (
    Carrier,
    DataSource,
    FareQuote,
    FareReference,
    Route,
)


def validate_real_fares_against_references(
    db,
):
    real_rows = db.execute(
        select(
            FareQuote,
            Route,
            Carrier,
            DataSource,
        )
        .join(
            Route,
            FareQuote.route_id
            == Route.id,
        )
        .join(
            Carrier,
            FareQuote.carrier_id
            == Carrier.id,
        )
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
            DataSource.code.in_(
                INDEX_ELIGIBLE_SOURCE_CODES
            ),
        )
        .order_by(
            Route.origin,
            Route.destination,
            FareQuote.advance_purchase_days,
        )
    ).all()

    reference_rows = db.execute(
        select(
            FareReference,
            Route,
            Carrier,
        )
        .join(
            Route,
            FareReference.route_id
            == Route.id,
        )
        .join(
            Carrier,
            FareReference.carrier_id
            == Carrier.id,
        )
    ).all()

    references = {}

    for reference, route, carrier in reference_rows:
        key = (
            route.id,
            carrier.id,
        )

        references.setdefault(
            key,
            [],
        ).append(
            reference
        )

    grouped = defaultdict(
        list
    )

    matched_observations = 0
    unmatched_observations = 0

    for (
        quote,
        route,
        carrier,
        source,
    ) in real_rows:
        key = (
            route.id,
            carrier.id,
        )

        matching_reference = None

        for reference in references.get(
            key,
            [],
        ):
            if (
                reference.valid_from
                <= quote.departure_date
                <= reference.valid_until
            ):
                matching_reference = (
                    reference
                )
                break

        route_code = (
            f"{route.origin}-"
            f"{route.destination}"
        )

        if matching_reference is None:
            unmatched_observations += 1

        else:
            matched_observations += 1

        grouped[
            route_code
        ].append(
            {
                "quote":
                    quote,
                "reference":
                    matching_reference,
                "source":
                    source,
                "carrier":
                    carrier,
            }
        )

    route_results = []

    routes_with_reference = 0

    for route_code, rows in sorted(
        grouped.items()
    ):
        fares = [
            float(
                row["quote"].total_fare
            )
            for row in rows
        ]

        reference = next(
            (
                row["reference"]
                for row in rows
                if row["reference"]
                is not None
            ),
            None,
        )

        if reference is not None:
            routes_with_reference += 1

        average_total_fare = (
            sum(fares)
            / len(fares)
            if fares
            else 0
        )

        route_results.append(
            {
                "route":
                    route_code,

                "observations":
                    len(rows),

                "observed_total_fare": {
                    "average":
                        round(
                            average_total_fare,
                            2,
                        ),
                    "minimum":
                        round(
                            min(fares),
                            2,
                        )
                        if fares
                        else None,
                    "maximum":
                        round(
                            max(fares),
                            2,
                        )
                        if fares
                        else None,
                },

                "reference_available":
                    reference
                    is not None,

                "reference_type":
                    (
                        reference.reference_type
                        if reference
                        else None
                    ),

                "published_base_fare": (
                    {
                        "minimum":
                            reference
                            .minimum_base_fare,
                        "maximum":
                            reference
                            .maximum_base_fare,
                        "currency":
                            reference.currency,
                        "valid_from":
                            reference.valid_from,
                        "valid_until":
                            reference.valid_until,
                        "source_name":
                            reference.source_name,
                    }
                    if reference
                    else None
                ),

                "statistical_error_comparable":
                    False,

                "validation_status": (
                    "reference_available"
                    if reference
                    else "reference_missing"
                ),

                "comparison_note": (
                    "Observed values are "
                    "total fares, while the "
                    "official tariff contains "
                    "base-fare ranges. "
                    "Direct MAPE or percentage "
                    "error is therefore not "
                    "calculated."
                ),
            }
        )

    total_observations = len(
        real_rows
    )

    total_routes = len(
        grouped
    )

    observation_coverage = (
        (
            matched_observations
            / total_observations
        )
        * 100
        if total_observations
        else 0
    )

    route_coverage = (
        (
            routes_with_reference
            / total_routes
        )
        * 100
        if total_routes
        else 0
    )

    return {
        "status":
            "completed",

        "validation_type":
            "official_tariff_reference",

        "real_observations":
            total_observations,

        "matched_observations":
            matched_observations,

        "unmatched_observations":
            unmatched_observations,

        "observation_reference_coverage_pct":
            round(
                observation_coverage,
                2,
            ),

        "routes_evaluated":
            total_routes,

        "routes_with_reference":
            routes_with_reference,

        "route_reference_coverage_pct":
            round(
                route_coverage,
                2,
            ),

        "statistical_error_comparable":
            False,

        "mape":
            None,

        "correlation":
            None,

        "reason":
            (
                "The observed Air India "
                "values are total fares, "
                "whereas the official "
                "reference document provides "
                "base-fare ranges. These "
                "quantities are not directly "
                "comparable for MAPE or "
                "correlation."
            ),

        "routes":
            route_results,
    }