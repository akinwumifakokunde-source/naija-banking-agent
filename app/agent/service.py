from app.agent.tools import (
    find_banks,
    find_branches,
    find_services,
    get_availability,
    create_appointment,
)


def get_banks() -> list[dict]:
    """Get available banks."""
    return find_banks()


def get_branches(city: str | None = None) -> list[dict]:
    """Get bank branches, optionally filtered by city."""
    return find_branches(city)


def get_services() -> list[dict]:
    """Get available banking services."""
    return find_services()


def get_available_slots(
    branch_id: int,
    service_id: int,
    date: str | None = None,
) -> list[dict]:
    """Get available appointment slots."""
    return get_availability(
        branch_id=branch_id,
        service_id=service_id,
        date=date,
    )


def book_appointment(
    slot_id: int,
    full_name: str,
    phone: str,
    email: str | None = None,
) -> dict:
    """Book an appointment."""
    return create_appointment(
        slot_id=slot_id,
        full_name=full_name,
        phone=phone,
        email=email,
    )