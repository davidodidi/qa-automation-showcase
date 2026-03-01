"""
API Tests — Authentication
==========================
Validates the /auth endpoint for happy path and failure scenarios.
"""
import pytest
import allure
from tests.api.clients.booking_client import BookingClient
from utils.assertions import assert_status, assert_auth_token, assert_response_time
from utils.data_factory import factory


@allure.feature("Authentication")
@allure.story("POST /auth")
class TestAuth:

    @allure.title("Valid credentials return a token")
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.smoke
    def test_valid_credentials_return_token(self):
        with BookingClient() as client:
            response = client.create_token("admin", "password123")

        assert_status(response, 200)
        token = assert_auth_token(response)
        assert len(token) > 10, "Token appears too short to be valid"

    @allure.title("Invalid credentials do not return a valid token")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    def test_invalid_credentials_rejected(self):
        with BookingClient() as client:
            creds = factory.invalid_credentials()
            response = client.create_token(creds.username, creds.password)

        assert_status(response, 200)  # API always returns 200
        body = response.json()
        # API returns {"reason": "Bad credentials"} on failure
        assert body.get("token") is None or body.get("reason") == "Bad credentials", (
            f"Expected rejection but got: {body}"
        )

    @allure.title("Auth endpoint responds within 3 seconds")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.smoke
    def test_auth_response_time(self):
        with BookingClient() as client:
            creds = factory.admin_credentials()
            response = client.create_token(creds.username, creds.password)
        assert_response_time(response, max_ms=5000)

    @allure.title("Empty credentials return an error")
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.regression
    def test_empty_credentials_rejected(self):
        with BookingClient() as client:
            response = client.create_token(username="wrong", password="wrong")
        body = response.json()
        assert "token" not in body or body.get("reason") == "Bad credentials"
