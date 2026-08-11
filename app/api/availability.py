from datetime import date as date_type, datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import AppointmentSlot


router = APIRouter(
    prefix="/api/v1/availability",
    tags=["Availability"],
)


@router.get("")
def get_availability(
    branch_id: int = Query(...),
    service_id: int = Query(...),
    date: date_type | None = Query(None),
    db: Session = Depends(get_db),
):
    query = (
        db.query(AppointmentSlot)
        .filter(
            AppointmentSlot.branch_id == branch_id,
            AppointmentSlot.service_id == service_id,
            AppointmentSlot.is_booked == False,
        )
    )

    if date:
        query = query.filter(
            AppointmentSlot.start_time >= datetime.combine(
                date,
                datetime.min.time(),
            ),
            AppointmentSlot.start_time < datetime.combine(
                date,
                datetime.max.time(),
            ),
        )

    slots = query.order_by(
        AppointmentSlot.start_time
    ).all()

    return [
        {
            "id": slot.id,
            "branch_id": slot.branch_id,
            "service_id": slot.service_id,
            "start_time": slot.start_time,
            "end_time": slot.end_time,
            "is_booked": slot.is_booked,
        }
        for slot in slots
    ]