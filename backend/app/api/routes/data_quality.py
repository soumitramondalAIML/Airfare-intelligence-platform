from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.quality.data_quality import (
    get_data_quality_summary,
)


router = APIRouter(
    prefix="/data-quality",
    tags=["Data Quality"],
)


@router.get("")
def data_quality_summary(
    db: Session = Depends(get_db),
):
    return get_data_quality_summary(db)