"""
API Test Fixtures
"""
import time
import pytest
import allure

from tests.api.clients.booking_client import BookingClient
from tests.database.db_client import DBClient
from utils.data_factory import factory


@pytest.fixture(scope="session")
def api_client() -> BookingClient:
    """Authenticated BookingClient with retry on auth failure."""
    client = BookingClient()

    for attempt in range(5):
        resp = client.create_token()
        if resp.status_code == 200:
            token = resp.json().get("token", "")
            if token and token != "Bad credentials":
                print(f"Auth succeeded on attempt {attempt + 1}")
                break
        print(f"Auth attempt {attempt + 1} failed, retrying in 5s...")
        time.sleep(5)
    else:
        pytest.fail("Could not authenticate after 5 attempts.")

    yield client
    client._client.close()


@pytest.fixture(scope="session")
def db_client() -> DBClient:
    client = DBClient()
    yield client
    client.clear_all()


@pytest.fixture
def booking_payload() -> dict:
    return factory.booking().to_dict()


@pytest.fixture
def created_booking(api_client: BookingClient, booking_payload: dict) -> dict:
    resp = api_client.create_booking(booking_payload)
    assert resp.status_code == 200, f"Setup failed: {resp.text}"
    data = resp.json()
    booking_id = data["bookingid"]

    allure.attach(str(data), name="Created Booking",
                  attachment_type=allure.attachment_type.JSON)
    yield data

    api_client.delete_booking(booking_id)