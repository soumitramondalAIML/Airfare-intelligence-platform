from datetime import date, timedelta
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.core.constants import ADVANCE_PURCHASE_WINDOWS
from app.models import DataSource, FareQuote, Route


def get_data_quality_summary(
    db: Session,
) -> dict:
    total_quotes = db.scalar(
        select(func.count())
        .select_from(FareQuote)
    ) or 0

    clean_quotes = db.scalar(
        select(func.count())
        .select_from(FareQuote)
        .where(
            FareQuote.is_clean.is_(True)
        )
    ) or 0

    outlier_quotes = db.scalar(
        select(func.count())
        .select_from(FareQuote)
        .where(
            FareQuote.is_outlier.is_(True)
        )
    ) or 0

    unclean_quotes = db.scalar(
        select(func.count())
        .select_from(FareQuote)
        .where(
            FareQuote.is_clean.is_(False)
        )
    ) or 0

    available_quotes = db.scalar(
        select(func.count())
        .select_from(FareQuote)
        .where(
            FareQuote.availability_status
            == "available"
        )
    ) or 0

    sold_out_quotes = db.scalar(
        select(func.count())
        .select_from(FareQuote)
        .where(
            FareQuote.availability_status
            == "sold_out"
        )
    ) or 0

    cancelled_quotes = db.scalar(
        select(func.count())
        .select_from(FareQuote)
        .where(
            FareQuote.availability_status
            == "cancelled"
        )
    ) or 0

    missing_total_fare = db.scalar(
        select(func.count())
        .select_from(FareQuote)
        .where(
            FareQuote.total_fare.is_(None)
        )
    ) or 0

    latest_collection = db.scalar(
        select(
            func.max(
                FareQuote.collected_at
            )
        )
    )

    if total_quotes > 0:
        clean_rate = round(
            (clean_quotes / total_quotes) * 100,
            2,
        )

        outlier_rate = round(
            (outlier_quotes / total_quotes) * 100,
            2,
        )
    else:
        clean_rate = 0.0
        outlier_rate = 0.0

    return {
        "total_quotes": total_quotes,
        "clean_quotes": clean_quotes,
        "unclean_quotes": unclean_quotes,
        "outlier_quotes": outlier_quotes,
        "missing_total_fare": missing_total_fare,
        "available_quotes": available_quotes,
        "sold_out_quotes": sold_out_quotes,
        "cancelled_quotes": cancelled_quotes,
        "clean_rate_percent": clean_rate,
        "outlier_rate_percent": outlier_rate,
        "latest_collection": latest_collection,
    }

def get_frontend_quality_status(
    db: Session,
) -> dict:
    configured_sources = db.scalar(
        select(func.count())
        .select_from(DataSource)
        .where(
            DataSource.active.is_(True)
        )
    ) or 0

    active_routes = db.scalar(
        select(func.count())
        .select_from(Route)
        .where(
            Route.active.is_(True)
        )
    ) or 0

    total_quotes = db.scalar(
        select(func.count())
        .select_from(FareQuote)
    ) or 0

    valid_observations = db.scalar(
        select(func.count())
        .select_from(FareQuote)
        .where(
            FareQuote.is_clean.is_(True),
            FareQuote.is_outlier.is_(False),
            FareQuote.availability_status
            == "available",
            FareQuote.total_fare.is_not(None),
        )
    ) or 0

    outlier_records = db.scalar(
        select(func.count())
        .select_from(FareQuote)
        .where(
            FareQuote.is_outlier.is_(True)
        )
    ) or 0

    unclean_records = db.scalar(
        select(func.count())
        .select_from(FareQuote)
        .where(
            FareQuote.is_clean.is_(False)
        )
    ) or 0

    missing_quotes = db.scalar(
        select(func.count())
        .select_from(FareQuote)
        .where(
            FareQuote.total_fare.is_(None)
        )
    ) or 0

    flagged_records = (
        outlier_records
        + unclean_records
    )

    latest_date = db.scalar(
        select(
            func.max(
                func.date(
                    FareQuote.collected_at
                )
            )
        )
    )

    expected_pairs = (
        active_routes
        * len(
            ADVANCE_PURCHASE_WINDOWS
        )
    )

    latest_pairs = set()
    observations_latest = 0

    if latest_date is not None:
        rows = db.execute(
            select(
                FareQuote.route_id,
                FareQuote.advance_purchase_days,
            )
            .where(
                FareQuote.is_clean.is_(True),
                func.date(
                    FareQuote.collected_at
                )
                == latest_date,
            )
        ).all()

        latest_pairs = {
            (
                route_id,
                advance_days,
            )
            for route_id, advance_days
            in rows
        }

        observations_latest = len(rows)

    coverage_pct = (
        round(
            (
                len(latest_pairs)
                / expected_pairs
            ) * 100,
            2,
        )
        if expected_pairs > 0
        else 0.0
    )

    if (
        coverage_pct >= 90
        and flagged_records == 0
    ):
        collection_health = "Healthy"

    elif coverage_pct >= 70:
        collection_health = "Warning"

    else:
        collection_health = "Critical"

    # -------------------------
    # SOURCE HEALTH
    # -------------------------

    source_rows = []

    sources = db.scalars(
        select(DataSource)
        .where(
            DataSource.active.is_(True)
        )
        .order_by(DataSource.name)
    ).all()

    for source in sources:
        record_count = db.scalar(
            select(func.count())
            .select_from(FareQuote)
            .where(
                FareQuote.source_id
                == source.id
            )
        ) or 0

        latest_source_update = db.scalar(
            select(
                func.max(
                    FareQuote.collected_at
                )
            )
            .where(
                FareQuote.source_id
                == source.id
            )
        )

        source_pairs = set()

        if latest_date is not None:
            rows = db.execute(
                select(
                    FareQuote.route_id,
                    FareQuote.advance_purchase_days,
                )
                .where(
                    FareQuote.source_id
                    == source.id,
                    FareQuote.is_clean.is_(True),
                    func.date(
                        FareQuote.collected_at
                    )
                    == latest_date,
                )
            ).all()

            source_pairs = {
                (
                    route_id,
                    advance_days,
                )
                for route_id, advance_days
                in rows
            }

        source_coverage = (
            round(
                (
                    len(source_pairs)
                    / expected_pairs
                ) * 100,
                2,
            )
            if expected_pairs > 0
            else 0.0
        )

        if record_count == 0:
            status = "Unknown"

        elif source_coverage >= 90:
            status = "Healthy"

        else:
            status = "Warning"

        source_rows.append(
            {
                "source": source.name,
                "type": source.source_type,
                "status": status,
                "coverage": source_coverage,
                "records": record_count,
                "last_update": (
                    latest_source_update
                ),
            }
        )

    # -------------------------
    # 7-DAY COVERAGE TREND
    # -------------------------

    trend = []

    if latest_date is not None:
        latest_day = (
            date.fromisoformat(latest_date)
            if isinstance(
                latest_date,
                str,
            )
            else latest_date
        )

        for offset in range(
            6,
            -1,
            -1,
        ):
            current_day = (
                latest_day
                - timedelta(
                    days=offset
                )
            )

            rows = db.execute(
                select(
                    FareQuote.route_id,
                    FareQuote.advance_purchase_days,
                )
                .where(
                    FareQuote.is_clean.is_(True),
                    func.date(
                        FareQuote.collected_at
                    )
                    == current_day.isoformat(),
                )
            ).all()

            pairs = {
                (
                    route_id,
                    advance_days,
                )
                for route_id, advance_days
                in rows
            }

            daily_coverage = (
                round(
                    (
                        len(pairs)
                        / expected_pairs
                    ) * 100,
                    2,
                )
                if expected_pairs > 0
                else 0.0
            )

            trend.append(
                {
                    "date": (
                        current_day.isoformat()
                    ),
                    "coverage": (
                        daily_coverage
                    ),
                }
            )

    # -------------------------
    # QUALITY ISSUES
    # -------------------------

    issue_rows = db.execute(
        select(
            FareQuote,
            Route,
            DataSource,
        )
        .join(
            Route,
            FareQuote.route_id
            == Route.id,
        )
        .join(
            DataSource,
            FareQuote.source_id
            == DataSource.id,
        )
        .where(
            or_(
                FareQuote.is_outlier.is_(
                    True
                ),
                FareQuote.is_clean.is_(
                    False
                ),
                FareQuote.total_fare.is_(
                    None
                ),
            )
        )
        .order_by(
            FareQuote.id.desc()
        )
        .limit(50)
    ).all()

    issues = []

    for (
        quote,
        route,
        source,
    ) in issue_rows:

        if quote.total_fare is None:
            issue_type = "Missing fare"
            severity = "High"
            action = "Review"

        elif quote.is_outlier:
            issue_type = "Outlier"
            severity = "High"
            action = "Excluded"

        else:
            issue_type = "Pending cleaning"
            severity = "Medium"
            action = "Review"

        issues.append(
            {
                "id": quote.id,
                "type": issue_type,
                "source": source.name,
                "route": (
                    f"{route.origin}-"
                    f"{route.destination}"
                ),
                "window": (
                    f"T+"
                    f"{quote.advance_purchase_days}"
                ),
                "severity": severity,
                "action": action,
            }
        )

    return {
        # Existing Dashboard compatibility
        "collection_health": (
            collection_health
        ),
        "coverage_pct": coverage_pct,
        "active_sources": (
            configured_sources
        ),
        "flagged_records": (
            flagged_records
        ),
        "latest_collection_date": (
            latest_date
        ),
        "coverage": coverage_pct,
        "activeSources": (
            configured_sources
        ),
        "observationsToday": (
            observations_latest
        ),

        # Full Data Quality contract
        "summary": {
            "collectionHealth": (
                coverage_pct
            ),
            "rawObservations": (
                total_quotes
            ),
            "validObservations": (
                valid_observations
            ),
            "flaggedRecords": (
                flagged_records
            ),
            "missingQuotes": (
                missing_quotes
            ),
            "duplicateRecords": 0,
            "outliersRemoved": (
                outlier_records
            ),
        },

        "sources": source_rows,
        "trend": trend,
        "issues": issues,
    }