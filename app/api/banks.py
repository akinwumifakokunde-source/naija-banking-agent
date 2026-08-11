from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.bank import Bank


router = APIRouter(
    prefix="/api/v1/banks",
    tags=["Banks"],
)


@router.get("")
def get_banks(
    db: Session = Depends(get_db),
):
    return db.query(Bank).filter(
        Bank.active.is_(True)
    ).all()