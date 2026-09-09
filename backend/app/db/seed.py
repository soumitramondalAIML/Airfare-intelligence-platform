from sqlalchemy import select

from app.db.session import SessionLocal
from app.models import Carrier, DataSource, Route


ROUTES = [
    ("DEL", "BOM"),
    ("DEL", "BLR"),
    ("BOM", "BLR"),
    ("DEL", "CCU"),
    ("BLR", "HYD"),
    ("MAA", "DEL"),
]


CARRIERS = [
    {
        "code": "6E",
        "name": "IndiGo",
    },
    {
        "code": "AI",
        "name": "Air India",
    },
    {
        "code": "IX",
        "name": "Air India Express",
    },
    {
        "code": "QP",
        "name": "Akasa Air",
    },
    {
        "code": "SG",
        "name": "SpiceJet",
    },
]


DATA_SOURCES = [
    {
        "code": "indigo",
        "name": "IndiGo",
        "source_type": "airline",
    },
    {
        "code": "air_india",
        "name": "Air India",
        "source_type": "airline",
    },
    {
        "code": "air_india_express",
        "name": "Air India Express",
        "source_type": "airline",
    },
    {
        "code": "akasa_air",
        "name": "Akasa Air",
        "source_type": "airline",
    },
    {
        "code": "spicejet",
        "name": "SpiceJet",
        "source_type": "airline",
    },
    {
        "code": "makemytrip",
        "name": "MakeMyTrip",
        "source_type": "ota",
    },
    {
        "code": "yatra",
        "name": "Yatra",
        "source_type": "ota",
    },
    {
        "code": "easemytrip",
        "name": "EaseMyTrip",
        "source_type": "ota",
    },
    {
        "code": "cleartrip",
        "name": "Cleartrip",
        "source_type": "ota",
    },
    {
        "code": "ixigo",
        "name": "Ixigo",
        "source_type": "ota",
    },
    {
        "code": "goibibo",
        "name": "Goibibo",
        "source_type": "ota",
    },
]


def seed_routes(db):
    created = 0

    for origin, destination in ROUTES:
        existing = db.scalar(
            select(Route).where(
                Route.origin == origin,
                Route.destination == destination,
            )
        )

        if existing is None:
            db.add(
                Route(
                    origin=origin,
                    destination=destination,
                    weight=1.0,
                    active=True,
                )
            )
            created += 1

    return created


def seed_carriers(db):
    created = 0

    for carrier_data in CARRIERS:
        existing = db.scalar(
            select(Carrier).where(
                Carrier.code == carrier_data["code"]
            )
        )

        if existing is None:
            db.add(
                Carrier(
                    code=carrier_data["code"],
                    name=carrier_data["name"],
                    active=True,
                )
            )
            created += 1

    return created


def seed_data_sources(db):
    created = 0

    for source_data in DATA_SOURCES:
        existing = db.scalar(
            select(DataSource).where(
                DataSource.code == source_data["code"]
            )
        )

        if existing is None:
            db.add(
                DataSource(
                    code=source_data["code"],
                    name=source_data["name"],
                    source_type=source_data["source_type"],
                    active=True,
                )
            )
            created += 1

    return created


def seed_database():
    with SessionLocal() as db:
        routes_created = seed_routes(db)
        carriers_created = seed_carriers(db)
        sources_created = seed_data_sources(db)

        db.commit()

    print("Database seeding completed.")
    print(f"Routes created: {routes_created}")
    print(f"Carriers created: {carriers_created}")
    print(f"Data sources created: {sources_created}")


if __name__ == "__main__":
    seed_database()