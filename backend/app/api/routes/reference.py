from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.constants import ADVANCE_PURCHASE_WINDOWS
from app.db.session import get_db
from app.models import Carrier, DataSource, Route
from app.schemas.reference import (
    AdvanceWindowsResponse,
    CarrierResponse,
    DataSourceResponse,
    RouteResponse,
)
from app.services.analytics.route_analytics import (
    get_route_detail,
    get_route_summary,
)


router = APIRouter(
    tags=["Reference Data"],
)


@router.get("/routes")
def get_routes(
    db: Session = Depends(get_db),
):
    routes = db.scalars(
        select(Route)
        .where(
            Route.active.is_(True)
        )
        .order_by(Route.id)
    ).all()

    return [
        get_route_summary(
            db,
            route,
        )
        for route in routes
    ]

@router.get(
    "/routes/{origin}/{destination}"
)
def get_route(
    origin: str,
    destination: str,
    db: Session = Depends(get_db),
):
    origin = origin.upper()
    destination = (
        destination.upper()
    )

    route = db.scalar(
        select(Route).where(
            Route.origin == origin,
            Route.destination
            == destination,
            Route.active.is_(True),
        )
    )

    if route is None:
        raise HTTPException(
            status_code=404,
            detail="Route not found",
        )

    return get_route_detail(
        db,
        route,
    )

@router.get(
    "/carriers",
    response_model=list[CarrierResponse],
)
def get_carriers(
    db: Session = Depends(get_db),
):
    statement = (
        select(Carrier)
        .where(Carrier.active.is_(True))
        .order_by(Carrier.id)
    )

    return db.scalars(statement).all()


@router.get(
    "/sources",
    response_model=list[DataSourceResponse],
)
def get_sources(
    db: Session = Depends(get_db),
):
    statement = (
        select(DataSource)
        .where(DataSource.active.is_(True))
        .order_by(DataSource.id)
    )

    return db.scalars(statement).all()


@router.get(
    "/config/advance-windows",
    response_model=AdvanceWindowsResponse,
)
def get_advance_windows():
    return {
        "windows": ADVANCE_PURCHASE_WINDOWS,
    }