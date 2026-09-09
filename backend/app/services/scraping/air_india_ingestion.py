import hashlib

from datetime import (
    date,
    datetime,
    timezone,
)

from sqlalchemy import (
    or_,
    select,
)

from app.db.session import SessionLocal
from app.models import (
    Carrier,
    DataSource,
    FareQuote,
    Route,
    ScraperRun,
)
from app.scrapers.sources.air_india_source import (
    collect_air_india,
)
from app.services.cleaning.fare_cleaner import (
    clean_fare_quotes,
)


AIR_INDIA_SOURCE_CODE = "air_india"

AIR_INDIA_SOURCE_NAME = "Air India"

AIR_INDIA_BASE_URL = (
    "https://www.airindia.com"
)


def utc_now_naive():
    """
    Store UTC as a naive datetime because the
    existing SQLAlchemy DateTime columns are
    not timezone-aware.
    """

    return (
        datetime.now(
            timezone.utc
        )
        .replace(
            tzinfo=None
        )
    )


def get_or_create_air_india_source(
    db,
):
    source = db.scalar(
        select(DataSource)
        .where(
            or_(
                DataSource.code
                == AIR_INDIA_SOURCE_CODE,

                DataSource.name
                == AIR_INDIA_SOURCE_NAME,
            )
        )
    )

    if source is not None:
        # Keep metadata accurate.
        source.source_type = "airline"
        source.base_url = (
            AIR_INDIA_BASE_URL
        )
        source.active = True

        db.commit()

        return source

    source = DataSource(
        code=(
            AIR_INDIA_SOURCE_CODE
        ),
        name=(
            AIR_INDIA_SOURCE_NAME
        ),
        source_type="airline",
        base_url=(
            AIR_INDIA_BASE_URL
        ),
        active=True,
    )

    db.add(
        source
    )

    db.commit()

    db.refresh(
        source
    )

    return source


def get_or_create_air_india_carrier(
    db,
):
    carrier = db.scalar(
        select(Carrier)
        .where(
            or_(
                Carrier.code == "AI",
                Carrier.name
                == "Air India",
            )
        )
    )

    if carrier is not None:
        carrier.active = True

        db.commit()

        return carrier

    carrier = Carrier(
        code="AI",
        name="Air India",
        active=True,
    )

    db.add(
        carrier
    )

    db.commit()

    db.refresh(
        carrier
    )

    return carrier


def get_route(
    db,
    origin: str,
    destination: str,
):
    return db.scalar(
        select(Route)
        .where(
            Route.origin
            == origin,

            Route.destination
            == destination,
        )
    )


def create_quote_hash(
    *,
    source_id: int,
    route_id: int,
    carrier_id: int,
    departure_date: date,
    advance_purchase_days: int,
    fare_class: str,
    total_fare: float,
    currency: str,
) -> str:
    """
    The hash deliberately does NOT contain
    collected_at.

    Therefore:
      same route/date/window/fare
      -> duplicate

    but:
      fare changes
      -> new observation
    """

    raw_value = "|".join(
        [
            str(
                source_id
            ),
            str(
                route_id
            ),
            str(
                carrier_id
            ),
            departure_date.isoformat(),
            str(
                advance_purchase_days
            ),
            fare_class.strip().lower(),
            (
                f"{float(total_fare):.2f}"
            ),
            currency.strip().upper(),
        ]
    )

    return hashlib.sha256(
        raw_value.encode(
            "utf-8"
        )
    ).hexdigest()


def persist_observation(
    db,
    observation: dict,
    source: DataSource,
    carrier: Carrier,
) -> str:
    """
    Returns one of:

        created
        duplicate
        skipped
    """

    origin = (
        observation.get(
            "origin"
        )
        or ""
    ).strip().upper()

    destination = (
        observation.get(
            "destination"
        )
        or ""
    ).strip().upper()

    route = get_route(
        db,
        origin,
        destination,
    )

    if route is None:
        print(
            "Skipping unknown route:",
            f"{origin}-{destination}",
        )

        return "skipped"

    departure_text = (
        observation.get(
            "departure_date"
        )
    )

    if not departure_text:
        return "skipped"

    try:
        departure_date = (
            date.fromisoformat(
                departure_text
            )
        )

    except ValueError:
        return "skipped"

    advance_days = int(
        observation.get(
            "advance_purchase_days"
        )
    )

    total_fare = (
        observation.get(
            "total_fare"
        )
    )

    if total_fare is None:
        return "skipped"

    total_fare = float(
        total_fare
    )

    fare_class = (
        observation.get(
            "fare_class"
        )
        or "Economy"
    )

    currency = (
        observation.get(
            "currency"
        )
        or "INR"
    ).upper()

    quote_hash = (
        create_quote_hash(
            source_id=source.id,
            route_id=route.id,
            carrier_id=carrier.id,
            departure_date=(
                departure_date
            ),
            advance_purchase_days=(
                advance_days
            ),
            fare_class=fare_class,
            total_fare=(
                total_fare
            ),
            currency=currency,
        )
    )

    existing_quote = db.scalar(
        select(FareQuote)
        .where(
            FareQuote.raw_quote_hash
            == quote_hash
        )
    )

    if existing_quote is not None:
        return "duplicate"

    quote = FareQuote(
        route_id=route.id,
        carrier_id=carrier.id,
        source_id=source.id,

        collected_at=(
            utc_now_naive()
        ),

        departure_date=(
            departure_date
        ),

        advance_purchase_days=(
            advance_days
        ),

        fare_class=(
            fare_class
        ),

        base_fare=None,
        taxes=None,

        user_development_fee=None,

        convenience_fee=None,

        total_fare=(
            total_fare
        ),

        currency=(
            currency
        ),

        availability_status=(
            observation.get(
                "availability_status"
            )
            or "available"
        ),

        is_outlier=False,

        is_clean=False,

        raw_quote_hash=(
            quote_hash
        ),
    )

    db.add(
        quote
    )

    return "created"


def run_air_india_ingestion():
    """
    Complete Air India pipeline:

        scrape
          ->
        deduplicate
          ->
        insert
          ->
        clean
          ->
        record scraper run
    """

    db = SessionLocal()

    scraper_run = None

    try:
        source = (
            get_or_create_air_india_source(
                db
            )
        )

        carrier = (
            get_or_create_air_india_carrier(
                db
            )
        )

        scraper_run = ScraperRun(
            source_id=(
                source.id
            ),
            started_at=(
                utc_now_naive()
            ),
            status="running",
            records_collected=0,
        )

        db.add(
            scraper_run
        )

        db.commit()

        db.refresh(
            scraper_run
        )

        print()
        print(
            "Starting real Air India "
            "collection..."
        )

        observations = (
            collect_air_india()
        )

        created = 0
        duplicates = 0
        skipped = 0

        for observation in (
            observations
        ):
            result = (
                persist_observation(
                    db,
                    observation,
                    source,
                    carrier,
                )
            )

            if result == "created":
                created += 1

            elif result == "duplicate":
                duplicates += 1

            else:
                skipped += 1

        # Write all newly created quotes.
        db.commit()

        print()
        print(
            "Running fare cleaning..."
        )

        cleaning_result = (
            clean_fare_quotes(
                db
            )
        )

        scraper_run.status = (
            "completed"
        )

        scraper_run.finished_at = (
            utc_now_naive()
        )

        # Number successfully obtained
        # from the Air India source.
        scraper_run.records_collected = (
            len(
                observations
            )
        )

        scraper_run.error_message = (
            None
        )

        db.commit()

        result = {
            "status":
                "completed",

            "source":
                "Air India",

            "source_type":
                "airline",

            "collected_from_site":
                len(
                    observations
                ),

            "created":
                created,

            "duplicates":
                duplicates,

            "skipped":
                skipped,

            "cleaning":
                cleaning_result,

            "scraper_run_id":
                scraper_run.id,
        }

        print()
        print(
            "=" * 60
        )

        print(
            "DATABASE INGESTION SUMMARY"
        )

        print(
            "=" * 60
        )

        print(
            "Collected from site:",
            result[
                "collected_from_site"
            ],
        )

        print(
            "Created:",
            created,
        )

        print(
            "Duplicates:",
            duplicates,
        )

        print(
            "Skipped:",
            skipped,
        )

        print(
            "Cleaning:",
            cleaning_result,
        )

        return result

    except Exception as exc:
        db.rollback()

        if scraper_run is not None:
            try:
                failed_run = db.get(
                    ScraperRun,
                    scraper_run.id,
                )

                if failed_run is not None:
                    failed_run.status = (
                        "failed"
                    )

                    failed_run.finished_at = (
                        utc_now_naive()
                    )

                    failed_run.error_message = (
                        str(exc)[:2000]
                    )

                    db.commit()

            except Exception:
                db.rollback()

        raise

    finally:
        db.close()


if __name__ == "__main__":
    result = (
        run_air_india_ingestion()
    )

    print()
    print(
        "FINAL RESULT:"
    )

    print(
        result
    )