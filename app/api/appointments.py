import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import Appointment, AppointmentSlot, Customer


router = APIRouter(
    prefix="/api/v1/appointments",
    tags=["Appointments"],
)


class AppointmentCreate(BaseModel):
    slot_id: int
    full_name: str
    phone: str
    email: EmailStr | None = None


@router.post("")
def create_appointment(
    payload: AppointmentCreate,
    db: Session = Depends(get_db),
):
    # Lock the slot while booking.
    slot = db.execute(
        select(AppointmentSlot)
        .where(AppointmentSlot.id == payload.slot_id)
        .with_for_update()
    ).scalar_one_or_none()

    if slot is None:
        raise HTTPException(
            status_code=404,
            detail="Appointment slot not found.",
        )

    if slot.is_booked:
        raise HTTPException(
            status_code=409,
            detail="This appointment slot has already been booked.",
        )

    # Find existing customer by phone.
    customer = db.execute(
        select(Customer).where(
            Customer.phone == payload.phone
        )
    ).scalar_one_or_none()

    if customer is None:
        customer = Customer(
            full_name=payload.full_name,
            phone=payload.phone,
            email=payload.email,
            active=True,
        )

        db.add(customer)
        db.flush()

    else:
        if not customer.active:
            raise HTTPException(
                status_code=403,
                detail="Customer account is inactive.",
            )

        # Update customer information.
        customer.full_name = payload.full_name

        if payload.email:
            customer.email = payload.email

    # Generate appointment reference.
    reference = f"NAIJA-{uuid.uuid4().hex[:10].upper()}"

    appointment = Appointment(
        customer_id=customer.id,
        slot_id=slot.id,
        status="CONFIRMED",
        reference=reference,
    )

    # Mark slot as booked.
    slot.is_booked = True

    db.add(appointment)

    try:
        db.commit()
        db.refresh(appointment)

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=409,
            detail="This appointment could not be booked. "
                   "The slot may already be taken.",
        )

    return {
        "message": "Appointment booked successfully.",
        "appointment": {
            "id": appointment.id,
            "reference": appointment.reference,
            "status": appointment.status,
            "customer_id": appointment.customer_id,
            "slot_id": appointment.slot_id,
            "start_time": slot.start_time,
            "end_time": slot.end_time,
        },
    }


# ---------------------------------------------------------
# GET APPOINTMENT
# ---------------------------------------------------------

@router.get("/{reference}")
def get_appointment(
    reference: str,
    db: Session = Depends(get_db),
):
    appointment = db.execute(
        select(Appointment)
        .where(Appointment.reference == reference)
    ).scalar_one_or_none()

    if appointment is None:
        raise HTTPException(
            status_code=404,
            detail="Appointment not found.",
        )

    slot = db.execute(
        select(AppointmentSlot)
        .where(AppointmentSlot.id == appointment.slot_id)
    ).scalar_one_or_none()

    customer = db.execute(
        select(Customer)
        .where(Customer.id == appointment.customer_id)
    ).scalar_one_or_none()

    if slot is None or customer is None:
        raise HTTPException(
            status_code=500,
            detail="Appointment data is incomplete.",
        )

    return {
        "appointment": {
            "id": appointment.id,
            "reference": appointment.reference,
            "status": appointment.status,
            "customer": {
                "id": customer.id,
                "full_name": customer.full_name,
                "phone": customer.phone,
                "email": customer.email,
            },
            "slot": {
                "id": slot.id,
                "branch_id": slot.branch_id,
                "service_id": slot.service_id,
                "start_time": slot.start_time,
                "end_time": slot.end_time,
                "is_booked": slot.is_booked,
            },
            "created_at": appointment.created_at,
        }
    }


# ---------------------------------------------------------
# CANCEL APPOINTMENT
# ---------------------------------------------------------

@router.delete("/{reference}")
def cancel_appointment(
    reference: str,
    db: Session = Depends(get_db),
):
    # Lock the appointment while cancelling.
    appointment = db.execute(
        select(Appointment)
        .where(Appointment.reference == reference)
        .with_for_update()
    ).scalar_one_or_none()

    if appointment is None:
        raise HTTPException(
            status_code=404,
            detail="Appointment not found.",
        )

    if appointment.status == "CANCELLED":
        raise HTTPException(
            status_code=409,
            detail="This appointment has already been cancelled.",
        )

    # Lock the associated slot.
    slot = db.execute(
        select(AppointmentSlot)
        .where(AppointmentSlot.id == appointment.slot_id)
        .with_for_update()
    ).scalar_one_or_none()

    if slot is None:
        raise HTTPException(
            status_code=500,
            detail="Appointment slot not found.",
        )

    # Cancel appointment.
    appointment.status = "CANCELLED"

    # Make slot available again.
    slot.is_booked = False

    try:
        db.commit()

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=409,
            detail="Appointment could not be cancelled.",
        )

    return {
        "message": "Appointment cancelled successfully.",
        "appointment": {
            "id": appointment.id,
            "reference": appointment.reference,
            "status": appointment.status,
            "slot_id": slot.id,
            "start_time": slot.start_time,
            "end_time": slot.end_time,
        },
    }