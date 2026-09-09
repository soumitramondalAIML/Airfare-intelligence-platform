import hashlib
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import (
    Carrier,
    DataSource,
    FareQuote,
    Route,
    ScraperRun,
)
from app.scrapers.sources.mock_source import MockAirfareScraper
from app.services.cleaning.fare_cleaner import clean_fare_quotes


def create_quote_hash(
    source_code: str,
    route_id: int,
    carrier_id: int,
    departure_date,
    advance_purchase_days: int,
    total_fare: float | None,
) -> str:
    raw_value = (
        f"{source_code}|"
        f"{route_id}|"
        f"{carrier_id}|"
        f"{departure_date}|"
        f"{advance_purchase_days}|"
        f"{total_fare}"
    )

    return hashlib.sha256(
        raw_value.encode("utf-8")
    ).hexdigest()


def run_mock_scraper(
    db: Session,
) -> dict:
    scraper = MockAirfareScraper()

    source = db.scalar(
        select(DataSource).where(
            DataSource.code == scraper.source_code
        )
    )

    if source is None:
        raise ValueError(
            "Mock scraper data source not found"
        )

    scraper_run = ScraperRun(
        source_id=source.id,
        status="running",
    )

    db.add(scraper_run)
    db.commit()
    db.refresh(scraper_run)

    created = 0
    duplicates = 0
    failed = 0

    try:
        scraped_fares = scraper.scrape()

        for fare in scraped_fares:
            route = db.scalar(
                select(Route).where(
                    Route.origin == fare.origin,
                    Route.destination == fare.destination,
                )
            )

            carrier = db.scalar(
                select(Carrier).where(
                    Carrier.code == fare.carrier_code
                )
            )

            if route is None or carrier is None:
                failed += 1
                continue

            quote_hash = create_quote_hash(
                source_code=fare.source_code,
                route_id=route.id,
                carrier_id=carrier.id,
                departure_date=fare.departure_date,
                advance_purchase_days=(
                    fare.advance_purchase_days
                ),
                total_fare=fare.total_fare,
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

            quote = FareQuote(
                route_id=route.id,
                carrier_id=carrier.id,
                source_id=source.id,
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
                total_fare=fare.total_fare,
                currency=fare.currency,
                availability_status=(
                    fare.availability_status
                ),
                raw_quote_hash=quote_hash,
                is_outlier=False,
                is_clean=False,
            )

            db.add(quote)
            created += 1

        scraper_run.status = "completed"
        scraper_run.records_collected = created
        scraper_run.finished_at = datetime.now()

        db.commit()

    except Exception as exc:
        db.rollback()

        scraper_run = db.get(
            ScraperRun,
            scraper_run.id,
        )

        scraper_run.status = "failed"
        scraper_run.error_message = str(exc)
        scraper_run.finished_at = datetime.now()

        db.commit()

        raise

    cleaning_result = clean_fare_quotes(db)

    return {
        "run_id": scraper_run.id,
        "status": scraper_run.status,
        "records_created": created,
        "duplicates_skipped": duplicates,
        "records_failed": failed,
        "cleaning": cleaning_result,
   }