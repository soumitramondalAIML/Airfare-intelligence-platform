from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.backtest.backtest_service import (
    get_backtest_data,
)


router = APIRouter(
    prefix="/backtest",
    tags=["DGCA Back-test"],
)


@router.get("")
def backtest(
    db: Session = Depends(get_db),
):
    return get_backtest_data(db)