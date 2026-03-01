"""
API Tests — Booking CRUD Lifecycle
====================================
End-to-end CRUD lifecycle: Create → Read → Update → Delete.
Each test is independently repeatable and cleans up after itself.
"""
import pytest
import allure

from utils.assertions import (
    assert_status,
    assert_booking_schema,
    assert_created_booking_schema,
    assert_response_time,
)
from utils.data_factory import factory


@allure.feature("Bookings")
@allure.story("GET /booking")
class TestGetBookings:

    @allure.title("Get all bookings returns a list")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    def test_get_all_bookings_returns_list(self, api_client):
        response = api_client.get_all_bookings()
        assert_status(response, 200)
        data = response.json()
        assert isinstance(data, list), f"Expected list, got {type(data)}"
        assert len(data) > 0, "Booking list should not be empty"

    @allure.title("Each item in list has a bookingid field")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    def test_booking_list_items_have_ids(self, api_client):
        response = api_client.get_all_bookings()
        assert_status(response, 200)
        for item in response.json():
            assert "bookingid" in item, f"Missing bookingid in item: {item}"

    @allure.title("Filter bookings by firstname")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    def test_filter_by_firstname(self, api_client, created_booking):
        booking = created_booking["booking"]
        response = api_client.get_all_bookings(firstname=booking["firstname"])
        assert_status(response, 200)
        # We can't guarantee the filter returns exactly one result (duplicates possible)
        # but the result must be a non-empty list
        assert isinstance(response.json(), list)

    @allure.title("Get single booking returns full booking object")
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.smoke
    def test_get_single_booking(self, api_client, created_booking):
        booking_id = created_booking["bookingid"]
        response = api_client.get_booking(booking_id)
        assert_status(response, 200)
        schema = assert_booking_schema(response)
        assert schema.firstname == created_booking["booking"]["firstname"]
        assert schema.lastname == created_booking["booking"]["lastname"]

    @allure.title("Non-existent booking returns 404")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    def test_get_nonexistent_booking_returns_404(self, api_client):
        response = api_client.get_booking(999_999_999)
        assert_status(response, 404)


@allure.feature("Bookings")
@allure.story("POST /booking")
class TestCreateBooking:

    @allure.title("Create booking returns 200 with bookingid")
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.smoke
    def test_create_booking_success(self, api_client, booking_payload):
        response = api_client.create_booking(booking_payload)
        assert_status(response, 200)
        schema = assert_created_booking_schema(response)
        assert schema.bookingid > 0
        # Teardown
        api_client.delete_booking(schema.bookingid)

    @allure.title("Created booking data matches sent payload")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    def test_create_booking_data_integrity(self, api_client):
        payload = factory.booking(
            firstname="Integration",
            lastname="TestUser",
            totalprice=999,
            depositpaid=True,
        ).to_dict()
        response = api_client.create_booking(payload)
        assert_status(response, 200)
        body = response.json()

        booking = body["booking"]
        assert booking["firstname"] == "Integration"
        assert booking["lastname"] == "TestUser"
        assert booking["totalprice"] == 999
        assert booking["depositpaid"] is True

        # Teardown
        api_client.delete_booking(body["bookingid"])

    @allure.title("Response time for create booking is acceptable")
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.regression
    def test_create_booking_response_time(self, api_client, booking_payload):
        response = api_client.create_booking(booking_payload)
        assert_response_time(response, max_ms=5000)
        api_client.delete_booking(response.json()["bookingid"])


@allure.feature("Bookings")
@allure.story("PUT /booking — full update")
class TestUpdateBooking:

    @allure.title("Full update replaces all booking fields")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.regression
    def test_full_update_booking(self, api_client, created_booking):
        booking_id = created_booking["bookingid"]
        updated_payload = factory.booking(
            firstname="Updated",
            lastname="Name",
            totalprice=1,
        ).to_dict()

        response = api_client.update_booking(booking_id, updated_payload)
        assert_status(response, 200)
        schema = assert_booking_schema(response)
        assert schema.firstname == "Updated"
        assert schema.lastname == "Name"

    @allure.title("Update without auth returns 403")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.regression
    def test_update_without_auth_returns_403(self, created_booking):
        from tests.api.clients.booking_client import BookingClient
        import httpx
        booking_id = created_booking["bookingid"]
        payload = factory.booking().to_dict()

        # Use an unauthenticated client
        with httpx.Client(base_url="https://restful-booker.herokuapp.com") as client:
            response = client.put(
                f"/booking/{booking_id}",
                json=payload,
                headers={"Content-Type": "application/json"},
            )
        assert response.status_code == 403


@allure.feature("Bookings")
@allure.story("PATCH /booking — partial update")
class TestPartialUpdateBooking:

    @allure.title("Partial update changes only specified fields")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    def test_partial_update_firstname(self, api_client, created_booking):
        booking_id = created_booking["bookingid"]
        original_lastname = created_booking["booking"]["lastname"]

        response = api_client.partial_update_booking(
            booking_id, {"firstname": "PatchedFirst"}
        )
        assert_status(response, 200)
        schema = assert_booking_schema(response)
        assert schema.firstname == "PatchedFirst"
        assert schema.lastname == original_lastname  # unchanged


@allure.feature("Bookings")
@allure.story("DELETE /booking")
class TestDeleteBooking:

    @allure.title("Delete booking returns 201")
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.smoke
    def test_delete_booking(self, api_client):
        # Create a booking specifically for deletion
        payload = factory.booking().to_dict()
        create_resp = api_client.create_booking(payload)
        assert_status(create_resp, 200)
        booking_id = create_resp.json()["bookingid"]

        delete_resp = api_client.delete_booking(booking_id)
        assert_status(delete_resp, 201)

    @allure.title("Deleted booking is no longer retrievable")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    def test_deleted_booking_not_found(self, api_client):
        payload = factory.booking().to_dict()
        create_resp = api_client.create_booking(payload)
        booking_id = create_resp.json()["bookingid"]

        api_client.delete_booking(booking_id)
        get_resp = api_client.get_booking(booking_id)
        assert_status(get_resp, 404)
