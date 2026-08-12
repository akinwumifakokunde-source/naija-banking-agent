import os

import httpx


API_BASE_URL = os.getenv(
    "NAIJA_API_BASE_URL",
    "http://127.0.0.1:8000",
)


def find_banks() -> list[dict]:
    """
    Return the available banks from the banking API.
    """

    url = f"{API_BASE_URL}/api/v1/banks"

    try:
        response = httpx.get(
            url,
            timeout=10.0,
            trust_env=False,
        )

        response.raise_for_status()
        return response.json()

    except httpx.HTTPError as exc:
        raise RuntimeError(
            f"Unable to retrieve banks: {exc}"
        ) from exc


def find_branches(city: str | None = None) -> list[dict]:
    """
    Return bank branches, optionally filtered by city.
    """

    url = f"{API_BASE_URL}/api/v1/branches"

    params = {}

    if city:
        params["city"] = city

    try:
        response = httpx.get(
            url,
            params=params,
            timeout=10.0,
            trust_env=False,
        )

        response.raise_for_status()
        return response.json()

    except httpx.HTTPError as exc:
        raise RuntimeError(
            f"Unable to retrieve branches: {exc}"
        ) from exc


def find_services() -> list[dict]:
    """
    Return available banking services.
    """

    url = f"{API_BASE_URL}/api/v1/services"

    try:
        response = httpx.get(
            url,
            timeout=10.0,
            trust_env=False,
        )

        response.raise_for_status()
        return response.json()

    except httpx.HTTPError as exc:
        raise RuntimeError(
            f"Unable to retrieve banking services: {exc}"
        ) from exc


def get_availability(
    branch_id: int,
    service_id: int,
    date: str | None = None,
) -> list[dict]:
    """
    Return available appointment slots for a branch and service.
    Optionally filter by date in YYYY-MM-DD format.
    """

    url = f"{API_BASE_URL}/api/v1/availability"

    params = {
        "branch_id": branch_id,
        "service_id": service_id,
    }

    if date:
        params["date"] = date

    try:
        response = httpx.get(
            url,
            params=params,
            timeout=10.0,
            trust_env=False,
        )

        response.raise_for_status()
        return response.json()

    except httpx.HTTPError as exc:
        raise RuntimeError(
            f"Unable to retrieve appointment availability: {exc}"
        ) from exc
def create_appointment(
    slot_id: int,
    full_name: str,
    phone: str,
    email: str | None = None,
) -> dict:
    """
    Book an appointment slot for a customer.
    """

    url = f"{API_BASE_URL}/api/v1/appointments"

    payload = {
        "slot_id": slot_id,
        "full_name": full_name,
        "phone": phone,
    }

    if email:
        payload["email"] = email

    try:
        response = httpx.post(
            url,
            json=payload,
            timeout=10.0,
            trust_env=False,
        )

        response.raise_for_status()

        return response.json()

    except httpx.HTTPError as exc:
        raise RuntimeError(
            f"Unable to create appointment: {exc}"
        ) from exc