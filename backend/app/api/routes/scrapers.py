from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import ScraperRun
from app.services.scraping.scraper_service import (
    run_mock_scraper,
)
from app.services.scraping.source_health import (
    get_source_health,
)


router = APIRouter(
    prefix="/scrapers",
    tags=["Scrapers"],
)


@router.post("/mock/run")
def trigger_mock_scraper(
    db: Session = Depends(get_db),
):
    return run_mock_scraper(db)


@router.get("/runs")
def get_scraper_runs(
    db: Session = Depends(get_db),
):
    runs = db.scalars(
        select(ScraperRun)
        .order_by(ScraperRun.id.desc())
        .limit(100)
    ).all()

    return [
        {
            "id": run.id,
            "source_id": run.source_id,
            "started_at": run.started_at,
            "finished_at": run.finished_at,
            "status": run.status,
            "records_collected": (
                run.records_collected
            ),
            "error_message": run.error_message,
        }
        for run in runs
    ]

@router.get("/health")
def scraper_health(
    db: Session = Depends(get_db),
):
    return get_source_health(db)