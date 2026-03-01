"""
Database Validation Tests
==========================
Validates that data written to our shadow DB after API calls
is accurate, complete, and consistent.

This layer simulates what you'd do in a real project where you have
direct database access — verifying that the API response matches
what was actually persisted in the database.

Test flow (the "holy trinity" of QA):
  1. Call API → get response
  2. Write response to shadow DB
  3. Query DB → assert data integrity
"""
import pytest
import allure

from tests.database.db_client import DBClient
from tests.api.clients.booking_client import BookingClient
from utils.assertions import (
    assert_status,
    assert_db_record_exists,
    assert_db_record_matches,
)
from utils.data_factory import factory


@allure.feature("Database Validation")
@allure.story("Shadow DB Integrity")
class TestDatabaseIntegrity:

    @allure.title("Booking saved to DB matches API response data")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.db
    @pytest.mark.smoke
    def test_created_booking_persisted_correctly(self, api_client, db_client):
        """
        HOLY TRINITY TEST:
        API Create → Shadow DB Write → DB Read → Assert Match
        """
        payload = factory.booking(
            firstname="DbTest",
            lastname="Integrity",
            totalprice=250,
            depositpaid=True,
        ).to_dict()

        # Step 1: Create via API
        with allure.step("Step 1 — Create booking via API"):
            response = api_client.create_booking(payload)
            assert_status(response, 200)
            api_data = response.json()
            booking_id = api_data["bookingid"]

        # Step 2: Persist to shadow DB
        with allure.step("Step 2 — Save to shadow DB"):
            db_client.save_booking(booking_id, api_data["booking"])

        # Step 3: Query DB and validate
        with allure.step("Step 3 — Validate DB record"):
            record = db_client.get_booking(booking_id)
            assert_db_record_exists(record, booking_id)
            assert_db_record_matches(record, {
                "firstname": "DbTest",
                "lastname": "Integrity",
                "totalprice": 250,
                "depositpaid": True,
            })

        # Teardown
        api_client.delete_booking(booking_id)
        db_client.delete_booking(booking_id)

    @allure.title("Deleting booking removes it from DB")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.db
    @pytest.mark.smoke
    def test_deleted_booking_removed_from_db(self, api_client, db_client):
        """After API delete, the shadow DB record should also be gone."""
        payload = factory.booking().to_dict()
        create_resp = api_client.create_booking(payload)
        booking_id = create_resp.json()["bookingid"]
        db_client.save_booking(booking_id, create_resp.json()["booking"])

        # Assert it exists first
        assert db_client.booking_exists(booking_id), "Record should exist before delete"

        # Delete via API + DB
        api_client.delete_booking(booking_id)
        rows_deleted = db_client.delete_booking(booking_id)

        assert rows_deleted == 1, "Expected exactly 1 row to be deleted"
        assert not db_client.booking_exists(booking_id), "Record should be gone after delete"

    @allure.title("Bulk booking operations maintain DB count accuracy")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.db
    @pytest.mark.regression
    def test_bulk_booking_db_count(self, api_client, db_client):
        """Create N bookings, assert DB count increases by N."""
        db_client.clear_all()
        initial_count = db_client.count_bookings()
        assert initial_count == 0

        n = 3
        booking_ids = []
        for payload in factory.bulk_bookings(n):
            resp = api_client.create_booking(payload.to_dict())
            assert_status(resp, 200)
            bid = resp.json()["bookingid"]
            db_client.save_booking(bid, resp.json()["booking"])
            booking_ids.append(bid)

        with allure.step(f"Assert DB contains exactly {n} bookings"):
            assert db_client.count_bookings() == n

        # Teardown
        for bid in booking_ids:
            api_client.delete_booking(bid)
        db_client.clear_all()

    @allure.title("Booking dates stored in correct ISO format")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.db
    @pytest.mark.regression
    def test_booking_dates_format_in_db(self, api_client, db_client):
        """Checkin/checkout dates must be in YYYY-MM-DD format."""
        import re
        date_pattern = re.compile(r"^\d{4}-\d{2}-\d{2}$")

        payload = factory.booking().to_dict()
        resp = api_client.create_booking(payload)
        bid = resp.json()["bookingid"]
        db_client.save_booking(bid, resp.json()["booking"])

        record = db_client.get_booking(bid)
        assert date_pattern.match(record.checkin), f"Invalid checkin format: {record.checkin}"
        assert date_pattern.match(record.checkout), f"Invalid checkout format: {record.checkout}"

        api_client.delete_booking(bid)
        db_client.delete_booking(bid)

    @allure.title("Updated booking reflects new data in DB after PATCH")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.db
    @pytest.mark.regression
    def test_patched_booking_reflected_in_db(self, api_client, db_client):
        """PATCH → re-read from API → update shadow DB → assert new values."""
        payload = factory.booking().to_dict()
        create_resp = api_client.create_booking(payload)
        booking_id = create_resp.json()["bookingid"]
        db_client.save_booking(booking_id, create_resp.json()["booking"])

        # Patch firstname
        patch_resp = api_client.partial_update_booking(
            booking_id, {"firstname": "PatchedInDB"}
        )
        assert_status(patch_resp, 200)

        # Update shadow DB
        db_client.delete_booking(booking_id)
        db_client.save_booking(booking_id, patch_resp.json())

        record = db_client.get_booking(booking_id)
        assert record.firstname == "PatchedInDB"

        api_client.delete_booking(booking_id)
        db_client.delete_booking(booking_id)
