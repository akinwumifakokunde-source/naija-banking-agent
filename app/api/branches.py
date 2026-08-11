from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.branch import Branch


router = APIRouter(
    prefix="/api/v1/branches",
    tags=["Branches"],
)


@router.get("")
def get_branches(
    city: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    query = db.query(Branch).filter(
        Branch.active.is_(True)
    )

    if city:
        query = query.filter(
            Branch.city.ilike(city)
        )

    return query.all()