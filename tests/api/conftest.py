"""
API Test Fixtures
=================
Shared fixtures for all API tests.
Scoped carefully to balance speed vs isolation:
  - session: client, auth token (expensive — do once)
  - function: individual booking payloads (fresh per test)
"""
import pytest
import allure

from tests.api.clients.booking_client import BookingClient
from tests.database.db_client import DBClient
from utils.data_factory import factory


# ── Clients ───────────────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def api_client() -> BookingClient:
    """Authenticated BookingClient, shared across the whole session."""
    with BookingClient() as client:
        resp = client.create_token()
        assert resp.status_code == 200, f"Auth failed during setup: {resp.text}"
        yield client


@pytest.fixture(scope="session")
def db_client() -> DBClient:
    """Shadow DB client, shared across the whole session."""
    client = DBClient()
    yield client
    client.clear_all()


# ── Data Fixtures ─────────────────────────────────────────────────────────────

@pytest.fixture
def booking_payload() -> dict:
    """Fresh randomised booking payload for each test."""
    return factory.booking().to_dict()


@pytest.fixture
def created_booking(api_client: BookingClient, booking_payload: dict) -> dict:
    """
    Creates a booking via the API before the test and deletes it after.
    Returns the full API response body: {"bookingid": ..., "booking": {...}}
    """
    resp = api_client.create_booking(booking_payload)
    assert resp.status_code == 200, f"Setup failed — could not create booking: {resp.text}"
    data = resp.json()
    booking_id = data["bookingid"]

    allure.attach(
        str(data),
        name="Created Booking",
        attachment_type=allure.attachment_type.JSON,
    )

    yield data

    # Teardown — best-effort delete
    api_client.delete_booking(booking_id)
