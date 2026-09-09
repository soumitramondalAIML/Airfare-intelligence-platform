from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.services.cleaning.fare_cleaner import clean_fare_quotes
from app.core.constants import ADVANCE_PURCHASE_WINDOWS
from app.db.session import get_db
from app.models import Carrier, DataSource, FareQuote, Route
from app.schemas.fare import (
    FareQuoteCreate,
    FareQuoteResponse,
)


router = APIRouter(
    prefix="/fares",
    tags=["Fare Quotes"],
)


def validate_reference_data(
    db: Session,
    fare: FareQuoteCreate,
):
    route = db.get(
        Route,
        fare.route_id,
    )

    if route is None:
        raise HTTPException(
            status_code=404,
            detail="Route not found",
        )

    carrier = db.get(
        Carrier,
        fare.carrier_id,
    )

    if carrier is None:
        raise HTTPException(
            status_code=404,
            detail="Carrier not found",
        )

    source = db.get(
        DataSource,
        fare.source_id,
    )

    if source is None:
        raise HTTPException(
            status_code=404,
            detail="Data source not found",
        )

    if (
        fare.advance_purchase_days
        not in ADVANCE_PURCHASE_WINDOWS
    ):
        raise HTTPException(
            status_code=400,
            detail=(
                "advance_purchase_days must be one of "
                f"{ADVANCE_PURCHASE_WINDOWS}"
            ),
        )


@router.post(
    "",
    response_model=FareQuoteResponse,
    status_code=201,
)
def create_fare_quote(
    fare: FareQuoteCreate,
    db: Session = Depends(get_db),
):
    validate_reference_data(
        db,
        fare,
    )

    total_fare = fare.total_fare

    if total_fare is None:
        components = [
            fare.base_fare,
            fare.taxes,
            fare.user_development_fee,
            fare.convenience_fee,
        ]

        available_components = [
            value
            for value in components
            if value is not None
        ]

        if available_components:
            total_fare = sum(
                available_components
            )

    quote = FareQuote(
        route_id=fare.route_id,
        carrier_id=fare.carrier_id,
        source_id=fare.source_id,
        departure_date=fare.departure_date,
        advance_purchase_days=(
            fare.advance_purchase_days
        ),
        fare_class=fare.fare_class,
        base_fare=fare.base_fare,
        taxes=fare.taxes,
        user_development_fee=(
            fare.user_development_fee
        ),
        convenience_fee=(
            fare.convenience_fee
        ),
        total_fare=total_fare,
        currency=fare.currency.upper(),
        availability_status=(
            fare.availability_status
        ),
        is_outlier=False,
        is_clean=False,
    )

    db.add(quote)
    db.commit()
    db.refresh(quote)

    return quote


@router.get("")
def get_fare_quotes(
    route: str | None = Query(
        default=None,
    ),
    carrier: str | None = Query(
        default=None,
    ),
    window: str | None = Query(
        default=None,
    ),
    route_id: int | None = Query(
        default=None,
        gt=0,
    ),
    carrier_id: int | None = Query(
        default=None,
        gt=0,
    ),
    source_id: int | None = Query(
        default=None,
        gt=0,
    ),
    advance_purchase_days: int | None = Query(
        default=None,
        gt=0,
    ),
    limit: int = Query(
        default=500,
        ge=1,
        le=2000,
    ),
    db: Session = Depends(get_db),
):
    statement = (
        select(
            FareQuote,
            Route,
            Carrier,
            DataSource,
        )
        .join(
            Route,
            FareQuote.route_id == Route.id,
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
    )

    if route:
        route_value = route.strip().upper()

        if route_value not in {
            "ALL",
            "ALL ROUTES",
        }:
            parts = route_value.split("-")

            if len(parts) != 2:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        "route must use format "
                        "DEL-BOM"
                    ),
                )

            origin, destination = parts

            statement = statement.where(
                Route.origin == origin,
                Route.destination
                == destination,
            )

    if carrier:
        carrier_value = (
            carrier.strip()
        )

        if carrier_value.upper() not in {
            "ALL",
            "ALL CARRIERS",
        }:
            statement = statement.where(
                or_(
                    func.upper(
                        Carrier.code
                    )
                    == carrier_value.upper(),
                    func.upper(
                        Carrier.name
                    )
                    == carrier_value.upper(),
                )
            )

    parsed_window = None

    if window:
        window_value = (
            window.strip().upper()
        )

        if window_value not in {
            "ALL",
            "ALL WINDOWS",
        }:
            if window_value.startswith(
                "T+"
            ):
                window_value = (
                    window_value[2:]
                )

            try:
                parsed_window = int(
                    window_value
                )

            except ValueError as exc:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        "window must use "
                        "format T+7"
                    ),
                ) from exc

            if (
                parsed_window
                not in ADVANCE_PURCHASE_WINDOWS
            ):
                raise HTTPException(
                    status_code=400,
                    detail=(
                        "window must be one of "
                        "T+1, T+7, T+15, "
                        "T+30, T+45"
                    ),
                )

    if route_id is not None:
        statement = statement.where(
            FareQuote.route_id == route_id
        )

    if carrier_id is not None:
        statement = statement.where(
            FareQuote.carrier_id
            == carrier_id
        )

    if source_id is not None:
        statement = statement.where(
            FareQuote.source_id
            == source_id
        )

    selected_window = (
        parsed_window
        if parsed_window is not None
        else advance_purchase_days
    )

    if selected_window is not None:
        statement = statement.where(
            FareQuote.advance_purchase_days
            == selected_window
        )

    statement = (
        statement
        .order_by(
            FareQuote.collected_at.desc()
        )
        .limit(limit)
    )

    rows = db.execute(
        statement
    ).all()

    observations = []

    for (
        quote,
        route_record,
        carrier_record,
        source_record,
    ) in rows:
        if quote.is_outlier:
            quality = "Outlier"
        elif quote.is_clean:
            quality = "Clean"
        else:
            quality = "Pending"

        observations.append(
            {
                "id": quote.id,
                "collected_at": (
                    quote.collected_at
                ),
                "departure_date": (
                    quote.departure_date
                ),
                "origin": (
                    route_record.origin
                ),
                "destination": (
                    route_record.destination
                ),
                "route": (
                    f"{route_record.origin}-"
                    f"{route_record.destination}"
                ),
                "carrier": (
                    carrier_record.name
                ),
                "carrier_code": (
                    carrier_record.code
                ),
                "source": (
                    source_record.name
                ),
                "source_type": (
                    source_record.source_type
                ),
                "purchase_window": (
                    f"T+"
                    f"{quote.advance_purchase_days}"
                ),
                "fare_class": (
                    quote.fare_class
                ),
                "base_fare": (
                    quote.base_fare
                ),
                "taxes": quote.taxes,
                "udf": (
                    quote.user_development_fee
                ),
                "convenience_fee": (
                    quote.convenience_fee
                ),
                "total_fare": (
                    quote.total_fare
                ),
                "currency": (
                    quote.currency
                ),
                "availability_status": (
                    quote.availability_status
                ),
                "quality_status": quality,
                "source_url": (
                    source_record.base_url
                ),
            }
        )

    return {
        "count": len(observations),
        "observations": observations,
    }


@router.post(
    "/clean",
)
def run_fare_cleaning(
    db: Session = Depends(get_db),
):
    return clean_fare_quotes(
        db
    )

@router.get(
    "/{fare_id}",
    response_model=FareQuoteResponse,
)
def get_fare_quote(
    fare_id: int,
    db: Session = Depends(get_db),
):
    quote = db.get(
        FareQuote,
        fare_id,
    )

    if quote is None:
        raise HTTPException(
            status_code=404,
            detail="Fare quote not found",
        )

    return quote