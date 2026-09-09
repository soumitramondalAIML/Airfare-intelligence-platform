from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.quality.data_quality import (
    get_frontend_quality_status,
)


router = APIRouter(
    prefix="/quality",
    tags=["Data Quality"],
)


@router.get("/status")
def get_quality_status(
    db: Session = Depends(get_db),
):
    return get_frontend_quality_status(db)