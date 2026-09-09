from sqlalchemy import (
    func,
    select,
)
from sqlalchemy.orm import Session

from app.core.constants import (
    INDEX_ELIGIBLE_SOURCE_CODES,
)
from app.models import (
    DataSource,
    FareQuote,
)
from app.services.validation.fare_reference_validator import (
    validate_real_fares_against_references,
)


def get_backtest_data(
    db: Session,
) -> dict:
    """
    Return the real validation status.

    Current validation layers:

    1. Real Air India fare observations
       versus official Air India tariff
       reference coverage.

    2. DGCA statistical back-test remains
       pending until a comparable DGCA
       average-fare series is imported.

    MAPE/correlation are deliberately not
    calculated between total fares and
    published base-fare ranges.
    """

    validation = (
        validate_real_fares_against_references(
            db
        )
    )

    collection_dates = db.execute(
        select(
            func.min(
                FareQuote.collected_at
            ),
            func.max(
                FareQuote.collected_at
            ),
        )
        .join(
            DataSource,
            FareQuote.source_id
            == DataSource.id,
        )
        .where(
            FareQuote.is_clean.is_(
                True
            ),
            FareQuote.is_outlier.is_(
                False
            ),
            FareQuote.availability_status
            == "available",
            FareQuote.total_fare.is_not(
                None
            ),
            DataSource.code.in_(
                INDEX_ELIGIBLE_SOURCE_CODES
            ),
        )
    ).one()

    start_datetime = (
        collection_dates[0]
    )

    end_datetime = (
        collection_dates[1]
    )

    if (
        start_datetime is not None
        and end_datetime is not None
    ):
        start_date = (
            start_datetime.date()
        )

        end_date = (
            end_datetime.date()
        )

        number_of_days = (
            (
                end_date
                - start_date
            ).days
            + 1
        )

    else:
        start_date = None
        end_date = None
        number_of_days = 0

    route_comparison = []

    for route_data in (
        validation.get(
            "routes",
            [],
        )
    ):
        observed = (
            route_data.get(
                "observed_total_fare"
            )
            or {}
        )

        reference = (
            route_data.get(
                "published_base_fare"
            )
            or {}
        )

        reference_available = (
            route_data.get(
                "reference_available",
                False,
            )
        )

        route_comparison.append(
            {
                "route":
                    route_data.get(
                        "route",
                        "",
                    ),

                "observed_average_total_fare":
                    observed.get(
                        "average"
                    ),

                "observed_minimum_total_fare":
                    observed.get(
                        "minimum"
                    ),

                "observed_maximum_total_fare":
                    observed.get(
                        "maximum"
                    ),

                "reference_minimum_base_fare":
                    reference.get(
                        "minimum"
                    ),

                "reference_maximum_base_fare":
                    reference.get(
                        "maximum"
                    ),

                "observations":
                    route_data.get(
                        "observations",
                        0,
                    ),

                "reference_available":
                    reference_available,

                "status": (
                    "Reference available"
                    if reference_available
                    else "Reference missing"
                ),
            }
        )

    real_observations = (
        validation.get(
            "real_observations",
            0,
        )
    )

    matched_observations = (
        validation.get(
            "matched_observations",
            0,
        )
    )

    routes_evaluated = (
        validation.get(
            "routes_evaluated",
            0,
        )
    )

    routes_with_reference = (
        validation.get(
            "routes_with_reference",
            0,
        )
    )

    route_coverage = (
        validation.get(
            "route_reference_coverage_pct",
            0,
        )
    )

    observation_coverage = (
        validation.get(
            "observation_reference_coverage_pct",
            0,
        )
    )

    return {
        "status":
            (
                "official_reference_available_"
                "dgca_pending"
            ),

        "data_note":
            (
                "Real Air India fare observations "
                "are matched to official Air India "
                "tariff reference data. A comparable "
                "DGCA average-fare series has not yet "
                "been imported."
            ),

        "validation_type":
            "official_tariff_reference",

        "statistical_error_comparable":
            False,

        "summary": {
            "start_date":
                start_date,

            "end_date":
                end_date,

            "number_of_days":
                number_of_days,

            "correlation":
                None,

            "mape":
                None,

            "route_coverage":
                route_coverage,

            "observation_coverage":
                observation_coverage,

            "observations":
                real_observations,

            "matched_observations":
                matched_observations,

            "routes_evaluated":
                routes_evaluated,

            "routes_with_reference":
                routes_with_reference,
        },

        "reference_validation": {
            "status":
                "available",

            "reference_type":
                (
                    "Official Air India Economy "
                    "base-fare envelope"
                ),

            "observed_value_type":
                "total_fare",

            "reference_value_type":
                "base_fare_range",

            "statistical_error_comparable":
                False,

            "reason":
                validation.get(
                    "reason"
                ),

            "observation_coverage_pct":
                observation_coverage,

            "route_coverage_pct":
                route_coverage,
        },

        "dgca": {
            "status":
                "reference_data_pending",

            "mape":
                None,

            "correlation":
                None,

            "data_note":
                (
                    "A directly comparable DGCA "
                    "route-level average-fare series "
                    "has not been imported. No DGCA "
                    "MAPE or correlation values are "
                    "fabricated."
                ),
        },

        # Kept for API compatibility.
        # These remain empty until a genuinely
        # comparable statistical series exists.
        "comparison_trend": [],

        "error_trend": [],

        "route_comparison":
            route_comparison,
    }