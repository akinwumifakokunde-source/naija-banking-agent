from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.banking_service import BankingService


router = APIRouter(
    prefix="/api/v1/services",
    tags=["Banking Services"],
)


@router.get("")
def get_services(
    db: Session = Depends(get_db),
):
    return db.query(BankingService).filter(
        BankingService.active.is_(True)
    ).all()