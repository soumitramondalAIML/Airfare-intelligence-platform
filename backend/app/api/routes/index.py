from datetime import date, timedelta
from typing import Literal

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
)
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.constants import (
    INDEX_ELIGIBLE_SOURCE_CODES,
    REAL_SOURCE_TYPES,
)
from app.db.session import get_db
from app.models import (
    DataSource,
    FareQuote,
    PriceIndexValue,
)
from app.services.index.price_index import (
    calculate_price_index,
    rebuild_price_index_history,
)


router = APIRouter(
    prefix="/index",
    tags=["Airfare Price Index"],
)


Frequency = Literal[
    "daily",
    "weekly",
    "monthly",
]


def percentage_change(
    current: float,
    previous: float | None,
) -> float:
    if (
        previous is None
        or previous == 0
    ):
        return 0.0

    return round(
        (
            (
                current
                - previous
            )
            / previous
        )
        * 100,
        4,
    )


def historical_reference(
    values: list[PriceIndexValue],
    target_date: date,
) -> float | None:
    candidates = [
        value
        for value in values
        if (
            value.period_start
            <= target_date
        )
    ]

    if candidates:
        return float(
            candidates[
                -1
            ].index_value
        )

    if values:
        return float(
            values[
                0
            ].index_value
        )

    return None


@router.get("/current")
def get_current_index(
    db: Session = Depends(get_db),
):
    values = db.scalars(
        select(
            PriceIndexValue
        )
        .where(
            PriceIndexValue.frequency
            == "daily",
            PriceIndexValue.route_id
            .is_(None),
        )
        .order_by(
            PriceIndexValue.period_start
        )
    ).all()

    if not values:
        raise HTTPException(
            status_code=404,
            detail=(
                "No real-data APIx "
                "history available"
            ),
        )

    latest = values[-1]

    current_index = float(
        latest.index_value
    )

    previous_value = (
        float(
            values[-2].index_value
        )
        if len(values) >= 2
        else None
    )

    weekly_reference = (
        historical_reference(
            values,
            latest.period_start
            - timedelta(
                days=7
            ),
        )
    )

    monthly_reference = (
        historical_reference(
            values,
            latest.period_start
            - timedelta(
                days=30
            ),
        )
    )

    # IMPORTANT:
    # Average fare must use only
    # real airline / OTA sources.
    average_fare = db.scalar(
        select(
            func.avg(
                FareQuote.total_fare
            )
        )
        .join(
            DataSource,
            FareQuote.source_id
            == DataSource.id,
        )
        .where(
            FareQuote.is_clean
            .is_(True),

            FareQuote.is_outlier
            .is_(False),

            FareQuote.availability_status
            == "available",

            FareQuote.total_fare
            .is_not(None),

            DataSource.source_type
            .in_(
                REAL_SOURCE_TYPES
            ),

            DataSource.code.in_(
                INDEX_ELIGIBLE_SOURCE_CODES
            ),

            func.date(
                FareQuote.collected_at
            )
            == latest.period_start
            .isoformat(),
        )
    )

    # Latest REAL observation only.
    last_updated = db.scalar(
        select(
            func.max(
                FareQuote.collected_at
            )
        )
        .join(
            DataSource,
            FareQuote.source_id
            == DataSource.id,
        )
        .where(
            FareQuote.is_clean
            .is_(True),

            FareQuote.is_outlier
            .is_(False),

            FareQuote.availability_status
            == "available",

            DataSource.source_type
            .in_(
                REAL_SOURCE_TYPES
            ),

            DataSource.code.in_(
                INDEX_ELIGIBLE_SOURCE_CODES
            ),
        )
    )

    return {
        "date":
            latest.period_start,

        "index":
            round(
                current_index,
                4,
            ),

        "daily_change_pct":
            percentage_change(
                current_index,
                previous_value,
            ),

        "weekly_change_pct":
            percentage_change(
                current_index,
                weekly_reference,
            ),

        "monthly_change_pct":
            percentage_change(
                current_index,
                monthly_reference,
            ),

        "average_fare":
            (
                round(
                    float(
                        average_fare
                    ),
                    2,
                )
                if average_fare
                is not None
                else 0
            ),

        "sample_size":
            latest.sample_size,

        "last_updated":
            last_updated,

        "data_mode":
            "real",

        "synthetic_included":
            False,

        "methodology":
            (
                "Prototype weighted "
                "fixed-basket airfare "
                "price index using only "
                "real airline/OTA "
                "observations."
            ),
    }


@router.get("/history")
def get_frontend_index_history(
    frequency: Frequency = Query(
        default="daily"
    ),
    from_date: date | None = Query(
        default=None,
        alias="from",
    ),
    to_date: date | None = Query(
        default=None,
        alias="to",
    ),
    db: Session = Depends(get_db),
):
    statement = (
        select(
            PriceIndexValue
        )
        .where(
            PriceIndexValue.frequency
            == frequency,

            PriceIndexValue.route_id
            .is_(None),
        )
    )

    if from_date is not None:
        statement = (
            statement.where(
                PriceIndexValue.period_start
                >= from_date
            )
        )

    if to_date is not None:
        statement = (
            statement.where(
                PriceIndexValue.period_start
                <= to_date
            )
        )

    statement = (
        statement.order_by(
            PriceIndexValue.period_start
        )
    )

    values = db.scalars(
        statement
    ).all()

    return {
        "frequency":
            frequency,

        "data_mode":
            "real",

        "synthetic_included":
            False,

        "observations": [
            {
                "date":
                    value.period_start,

                "index":
                    value.index_value,

                "sample_size":
                    value.sample_size,
            }
            for value in values
        ],
    }


@router.post("/calculate")
def calculate_index(
    frequency: Frequency = Query(
        default="daily"
    ),
    db: Session = Depends(get_db),
):
    try:
        result = (
            calculate_price_index(
                db,
                frequency,
            )
        )

        result[
            "data_mode"
        ] = "real"

        result[
            "synthetic_included"
        ] = False

        return result

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc


@router.post("/rebuild-history")
def rebuild_index_history(
    frequency: Frequency = Query(
        default="daily"
    ),
    db: Session = Depends(get_db),
):
    try:
        result = (
            rebuild_price_index_history(
                db,
                frequency,
            )
        )

        result[
            "data_mode"
        ] = "real"

        result[
            "synthetic_included"
        ] = False

        return result

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc


@router.get("")
def get_index_history(
    frequency: Frequency = Query(
        default="daily"
    ),
    limit: int = Query(
        default=90,
        ge=1,
        le=365,
    ),
    db: Session = Depends(get_db),
):
    values = db.scalars(
        select(
            PriceIndexValue
        )
        .where(
            PriceIndexValue.frequency
            == frequency,

            PriceIndexValue.route_id
            .is_(None),
        )
        .order_by(
            PriceIndexValue
            .period_start
            .desc()
        )
        .limit(
            limit
        )
    ).all()

    return {
        "frequency":
            frequency,

        "data_mode":
            "real",

        "synthetic_included":
            False,

        "observations": [
            {
                "period_start":
                    value.period_start,

                "frequency":
                    value.frequency,

                "index_value":
                    value.index_value,

                "base_value":
                    value.base_value,

                "sample_size":
                    value.sample_size,
            }
            for value in values
        ],
    }