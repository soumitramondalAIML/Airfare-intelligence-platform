from datetime import datetime, timezone

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
    ScraperRun,
)
from app.scrapers.sources.air_india_source import (
    ADVANCE_WINDOWS,
    ROUTES,
)


EXPECTED_OBSERVATIONS = (
    len(ROUTES)
    * len(ADVANCE_WINDOWS)
)


def utc_now_naive():
    return (
        datetime.now(
            timezone.utc
        )
        .replace(
            tzinfo=None
        )
    )


def get_source_health(
    db: Session,
) -> dict:

    sources = db.scalars(
        select(
            DataSource
        )
        .where(
            DataSource.code.in_(
                INDEX_ELIGIBLE_SOURCE_CODES
            )
        )
        .order_by(
            DataSource.name
        )
    ).all()

    source_results = []

    for source in sources:

        latest_run = db.scalar(
            select(
                ScraperRun
            )
            .where(
                ScraperRun.source_id
                == source.id
            )
            .order_by(
                ScraperRun.id.desc()
            )
            .limit(1)
        )

        last_successful_run = (
            db.scalar(
                select(
                    ScraperRun
                )
                .where(
                    ScraperRun.source_id
                    == source.id,
                    ScraperRun.status
                    == "completed",
                )
                .order_by(
                    ScraperRun.id.desc()
                )
                .limit(1)
            )
        )

        latest_collection_time = (
            db.scalar(
                select(
                    func.max(
                        FareQuote.collected_at
                    )
                )
                .where(
                    FareQuote.source_id
                    == source.id,
                    FareQuote.is_clean.is_(
                        True
                    ),
                    FareQuote.is_outlier.is_(
                        False
                    ),
                    FareQuote.availability_status
                    == "available",
                )
            )
        )

        latest_collection_date = (
            latest_collection_time.date()
            if latest_collection_time
            else None
        )

        stored_observations = 0

        if latest_collection_date:

            stored_observations = (
                db.scalar(
                    select(
                        func.count(
                            FareQuote.id
                        )
                    )
                    .where(
                        FareQuote.source_id
                        == source.id,
                        FareQuote.is_clean.is_(
                            True
                        ),
                        FareQuote.is_outlier.is_(
                            False
                        ),
                        FareQuote.availability_status
                        == "available",
                        func.date(
                            FareQuote.collected_at
                        )
                        == latest_collection_date,
                    )
                )
                or 0
            )

        coverage_pct = (
            (
                stored_observations
                / EXPECTED_OBSERVATIONS
            )
            * 100
            if EXPECTED_OBSERVATIONS
            else 0
        )

        data_age_hours = None

        if latest_collection_time:

            age = (
                utc_now_naive()
                - latest_collection_time
            )

            data_age_hours = round(
                max(
                    age.total_seconds()
                    / 3600,
                    0,
                ),
                2,
            )

        latest_run_status = (
            latest_run.status
            if latest_run
            else "never_run"
        )

        if (
            latest_run_status
            == "completed"
            and coverage_pct >= 100
            and (
                data_age_hours is None
                or data_age_hours <= 24
            )
        ):
            health_status = "healthy"

        elif (
            latest_run_status
            == "completed"
            and stored_observations > 0
        ):
            health_status = "degraded"

        elif (
            latest_run_status
            == "failed"
        ):
            health_status = "failed"

        else:
            health_status = "unknown"

        source_results.append(
            {
                "source":
                    source.name,

                "source_code":
                    source.code,

                "source_type":
                    source.source_type,

                "status":
                    health_status,

                "latest_run_status":
                    latest_run_status,

                "latest_run_started_at":
                    (
                        latest_run.started_at
                        if latest_run
                        else None
                    ),

                "latest_run_finished_at":
                    (
                        latest_run.finished_at
                        if latest_run
                        else None
                    ),

                "last_successful_run":
                    (
                        last_successful_run.finished_at
                        if last_successful_run
                        else None
                    ),

                "last_observation_at":
                    latest_collection_time,

                "latest_collection_date":
                    latest_collection_date,

                "stored_observations":
                    stored_observations,

                "expected_observations":
                    EXPECTED_OBSERVATIONS,

                "coverage_pct":
                    round(
                        min(
                            coverage_pct,
                            100,
                        ),
                        2,
                    ),

                "data_age_hours":
                    data_age_hours,

                "error_message":
                    (
                        latest_run.error_message
                        if (
                            latest_run
                            and latest_run.status
                            == "failed"
                        )
                        else None
                    ),
            }
        )

    statuses = {
        item["status"]
        for item in source_results
    }

    if (
        source_results
        and statuses
        == {"healthy"}
    ):
        overall_status = "healthy"

    elif "failed" in statuses:
        overall_status = "degraded"

    elif source_results:
        overall_status = "degraded"

    else:
        overall_status = "unknown"

    return {
        "overall_status":
            overall_status,

        "data_mode":
            "real",

        "synthetic_included":
            False,

        "eligible_sources":
            len(
                source_results
            ),

        "expected_observations_per_collection":
            EXPECTED_OBSERVATIONS,

        "sources":
            source_results,
    }