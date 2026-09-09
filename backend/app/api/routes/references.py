from datetime import date

from fastapi import (
    APIRouter,
    Depends,
)
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import (
    Carrier,
    FareReference,
    Route,
)

from app.services.validation.fare_reference_validator import (
    validate_real_fares_against_references,
)


router = APIRouter(
    prefix="/references",
    tags=["Reference Data"],
)


@router.get("/fares")
def get_fare_references(
    db: Session = Depends(get_db),
):
    rows = db.execute(
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
        .order_by(
            Route.origin,
            Route.destination,
        )
    ).all()

    observations = []

    for reference, route, carrier in rows:
        observations.append(
            {
                "route": (
                    f"{route.origin}-"
                    f"{route.destination}"
                ),
                "origin":
                    route.origin,
                "destination":
                    route.destination,
                "carrier":
                    carrier.name,
                "carrier_code":
                    carrier.code,
                "reference_type":
                    reference.reference_type,
                "cabin_class":
                    reference.cabin_class,
                "valid_from":
                    reference.valid_from,
                "valid_until":
                    reference.valid_until,
                "minimum_base_fare":
                    reference.minimum_base_fare,
                "maximum_base_fare":
                    reference.maximum_base_fare,
                "currency":
                    reference.currency,
                "source_name":
                    reference.source_name,
                "source_url":
                    reference.source_url,
                "notes":
                    reference.notes,
            }
        )

    return {
        "count":
            len(
                observations
            ),
        "data_type":
            "official_reference",
        "comparison_basis":
            "base_fare_range",
        "observations":
            observations,
    }


@router.get("/fares/current")
def get_current_fare_references(
    db: Session = Depends(get_db),
):
    today = date.today()

    rows = db.execute(
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
        .where(
            FareReference.valid_from
            <= today,
            FareReference.valid_until
            >= today,
        )
        .order_by(
            Route.origin,
            Route.destination,
        )
    ).all()

    observations = []

    for reference, route, carrier in rows:
        observations.append(
            {
                "route": (
                    f"{route.origin}-"
                    f"{route.destination}"
                ),
                "carrier":
                    carrier.name,
                "minimum_base_fare":
                    reference.minimum_base_fare,
                "maximum_base_fare":
                    reference.maximum_base_fare,
                "currency":
                    reference.currency,
                "valid_from":
                    reference.valid_from,
                "valid_until":
                    reference.valid_until,
                "source_name":
                    reference.source_name,
            }
        )

    return {
        "reference_date":
            today,
        "count":
            len(
                observations
            ),
        "observations":
            observations,
    }

@router.get("/validation")
def validate_fare_references(
    db: Session = Depends(get_db),
):
    return (
        validate_real_fares_against_references(
            db
        )
    )