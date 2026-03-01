import pytest
from tests.database.db_client import DBClient
from tests.api.clients.booking_client import BookingClient
from utils.data_factory import factory


@pytest.fixture(scope="session")
def db_client() -> DBClient:
    client = DBClient()
    yield client
    client.clear_all()


@pytest.fixture(scope="session")
def api_client() -> BookingClient:
    with BookingClient() as client:
        resp = client.create_token()
        assert resp.status_code == 200
        yield client
