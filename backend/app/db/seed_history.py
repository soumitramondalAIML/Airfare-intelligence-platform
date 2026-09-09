import hashlib
import math
from datetime import date, datetime, time, timedelta

from sqlalchemy import select

from app.core.constants import ADVANCE_PURCHASE_WINDOWS
from app.db.session import SessionLocal
from app.models import (
    Carrier,
    DataSource,
    FareQuote,
    Route,
)


DAYS_OF_HISTORY = 30


WINDOW_FACTORS = {
    1: 1.25,
    7: 1.10,
    15: 1.00,
    30: 0.92,
    45: 0.88,
}


ROUTE_BASE_FARES = {
    ("DEL", "BOM"): 5200.0,
    ("DEL", "BLR"): 6100.0,
    ("BOM", "BLR"): 4500.0,
    ("DEL", "CCU"): 5800.0,
    ("BLR", "HYD"): 3200.0,
    ("MAA", "DEL"): 6400.0,
}


def get_or_create_demo_source(db):
    source = db.scalar(
        select(DataSource).where(
            DataSource.code == "synthetic_demo"
        )
    )

    if source is not None:
        return source

    source = DataSource(
        code="synthetic_demo",
        name="Synthetic Historical Demo",
        source_type="synthetic",
        base_url=None,
        active=True,
    )

    db.add(source)
    db.flush()

    return source


def create_demo_hash(
    observation_date: date,
    route_id: int,
    carrier_id: int,
    advance_days: int,
) -> str:
    raw_value = (
        f"synthetic-demo|"
        f"{observation_date}|"
        f"{route_id}|"
        f"{carrier_id}|"
        f"{advance_days}"
    )

    return hashlib.sha256(
        raw_value.encode("utf-8")
    ).hexdigest()


def calculate_demo_fare(
    route: Route,
    advance_days: int,
    day_number: int,
    observation_date: date,
) -> float:
    base_fare = ROUTE_BASE_FARES.get(
        (
            route.origin,
            route.destination,
        ),
        5000.0,
    )

    window_factor = WINDOW_FACTORS[
        advance_days
    ]

    trend_factor = (
        1.0
        + (day_number * 0.0018)
    )

    wave_factor = (
        1.0
        + (
            0.025
            * math.sin(
                (day_number + route.id)
                / 3.0
            )
        )
    )

    weekend_factor = 1.0

    if observation_date.weekday() in {
        4,
        5,
        6,
    }:
        weekend_factor = 1.02

    fare = (
        base_fare
        * window_factor
        * trend_factor
        * wave_factor
        * weekend_factor
    )

    return round(fare, 2)


def seed_history():
    with SessionLocal() as db:
        routes = db.scalars(
            select(Route)
            .where(Route.active.is_(True))
            .order_by(Route.id)
        ).all()

        carriers = db.scalars(
            select(Carrier)
            .where(Carrier.active.is_(True))
            .order_by(Carrier.id)
        ).all()

        if not routes:
            raise RuntimeError(
                "No routes found. Run reference seed first."
            )

        if not carriers:
            raise RuntimeError(
                "No carriers found. Run reference seed first."
            )

        source = get_or_create_demo_source(
            db
        )

        end_date = date.today()

        start_date = (
            end_date
            - timedelta(
                days=DAYS_OF_HISTORY - 1
            )
        )

        created = 0
        duplicates = 0

        for day_number in range(
            DAYS_OF_HISTORY
        ):
            observation_date = (
                start_date
                + timedelta(days=day_number)
            )

            collected_at = datetime.combine(
                observation_date,
                time(
                    hour=9,
                    minute=0,
                ),
            )

            for route_index, route in enumerate(
                routes
            ):
                carrier = carriers[
                    route_index
                    % len(carriers)
                ]

                for advance_days in (
                    ADVANCE_PURCHASE_WINDOWS
                ):
                    quote_hash = (
                        create_demo_hash(
                            observation_date=(
                                observation_date
                            ),
                            route_id=route.id,
                            carrier_id=carrier.id,
                            advance_days=(
                                advance_days
                            ),
                        )
                    )

                    existing = db.scalar(
                        select(FareQuote).where(
                            FareQuote.raw_quote_hash
                            == quote_hash
                        )
                    )

                    if existing is not None:
                        duplicates += 1
                        continue

                    total_fare = (
                        calculate_demo_fare(
                            route=route,
                            advance_days=(
                                advance_days
                            ),
                            day_number=day_number,
                            observation_date=(
                                observation_date
                            ),
                        )
                    )

                    base_component = round(
                        total_fare * 0.78,
                        2,
                    )

                    taxes = round(
                        total_fare * 0.15,
                        2,
                    )

                    udf = round(
                        total_fare * 0.03,
                        2,
                    )

                    convenience_fee = round(
                        total_fare
                        - base_component
                        - taxes
                        - udf,
                        2,
                    )

                    quote = FareQuote(
                        route_id=route.id,
                        carrier_id=carrier.id,
                        source_id=source.id,
                        collected_at=collected_at,
                        departure_date=(
                            observation_date
                            + timedelta(
                                days=advance_days
                            )
                        ),
                        advance_purchase_days=(
                            advance_days
                        ),
                        fare_class="Economy",
                        base_fare=base_component,
                        taxes=taxes,
                        user_development_fee=udf,
                        convenience_fee=(
                            convenience_fee
                        ),
                        total_fare=total_fare,
                        currency="INR",
                        availability_status=(
                            "available"
                        ),
                        raw_quote_hash=quote_hash,
                        is_outlier=False,
                        is_clean=True,
                    )

                    db.add(quote)
                    created += 1

        db.commit()

    print(
        "Synthetic historical dataset completed."
    )
    print(
        f"History start: {start_date}"
    )
    print(
        f"History end: {end_date}"
    )
    print(
        f"Records created: {created}"
    )
    print(
        f"Duplicates skipped: {duplicates}"
    )


if __name__ == "__main__":
    seed_history()