from datetime import date

from sqlalchemy import select

from app.db.session import SessionLocal
from app.models import (
    Carrier,
    FareReference,
    Route,
)


SOURCE_URL = (
    "https://www.airindia.com/"
    "content/dam/air-india/pdfs/"
    "tariff/"
    "TARIFF-SHEET-AS-ON-01APR26.pdf"
)


REFERENCE_TYPE = (
    "official_economy_base_fare_envelope"
)


REFERENCE_DATA = [
    {
        "origin": "DEL",
        "destination": "BOM",
        "minimum": 2080,
        "maximum": 52362,
        "market": "Mumbai-Delhi V.V.",
    },
    {
        "origin": "DEL",
        "destination": "BLR",
        "minimum": 1580,
        "maximum": 61702,
        "market": "Bengaluru-Delhi V.V.",
    },
    {
        "origin": "BOM",
        "destination": "BLR",
        "minimum": 1030,
        "maximum": 41382,
        "market": "Bengaluru-Mumbai V.V.",
    },
    {
        "origin": "DEL",
        "destination": "CCU",
        "minimum": 1699,
        "maximum": 49180,
        "market": "Kolkata-Delhi V.V.",
    },
    {
        "origin": "BLR",
        "destination": "HYD",
        "minimum": 420,
        "maximum": 32638,
        "market": "Bengaluru-Hyderabad V.V.",
    },
    {
        "origin": "MAA",
        "destination": "DEL",
        "minimum": 2030,
        "maximum": 49194,
        "market": "Delhi-Chennai V.V.",
    },
]


def seed_fare_references():
    db = SessionLocal()

    try:
        carrier = db.scalar(
            select(Carrier)
            .where(
                Carrier.code == "AI"
            )
        )

        if carrier is None:
            raise RuntimeError(
                "Air India carrier not found"
            )

        created = 0
        existing = 0
        missing_routes = 0

        for item in REFERENCE_DATA:
            route = db.scalar(
                select(Route)
                .where(
                    Route.origin
                    == item["origin"],
                    Route.destination
                    == item["destination"],
                )
            )

            if route is None:
                print(
                    "Route not found:",
                    (
                        f"{item['origin']}-"
                        f"{item['destination']}"
                    ),
                )

                missing_routes += 1
                continue

            already_exists = db.scalar(
                select(FareReference)
                .where(
                    FareReference.route_id
                    == route.id,

                    FareReference.carrier_id
                    == carrier.id,

                    FareReference.reference_type
                    == REFERENCE_TYPE,

                    FareReference.valid_from
                    == date(
                        2026,
                        4,
                        1,
                    ),
                )
            )

            if already_exists:
                existing += 1
                continue

            reference = FareReference(
                route_id=route.id,
                carrier_id=carrier.id,

                reference_type=(
                    REFERENCE_TYPE
                ),

                cabin_class="Economy",

                valid_from=date(
                    2026,
                    4,
                    1,
                ),

                valid_until=date(
                    2027,
                    4,
                    30,
                ),

                minimum_base_fare=float(
                    item["minimum"]
                ),

                maximum_base_fare=float(
                    item["maximum"]
                ),

                currency="INR",

                source_name=(
                    "Air India Domestic "
                    "Fares - Tariff Sheet "
                    "as on 01 Apr 2026"
                ),

                source_url=SOURCE_URL,

                notes=(
                    "Official Air India "
                    "Economy base-fare "
                    "envelope. "
                    f"Published market: "
                    f"{item['market']} "
                    "The tariff table is "
                    "published as Market & "
                    "V.V. This is base-fare "
                    "reference data, not "
                    "DGCA average-fare data "
                    "and not a total-fare "
                    "observation."
                ),
            )

            db.add(
                reference
            )

            created += 1

        db.commit()

        print()
        print(
            "FARE REFERENCE SEED SUMMARY"
        )

        print(
            "Created:",
            created,
        )

        print(
            "Already existing:",
            existing,
        )

        print(
            "Missing routes:",
            missing_routes,
        )

    finally:
        db.close()


if __name__ == "__main__":
    seed_fare_references()