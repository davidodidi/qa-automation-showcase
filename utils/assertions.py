"""
Custom Assertion Helpers
========================
Domain-aware assertions that produce readable failure messages.
Wrap these around raw pytest asserts to get better error output in Allure.
"""
from __future__ import annotations

import httpx
import allure
from pydantic import BaseModel, ValidationError


# ─── Pydantic Response Schemas ────────────────────────────────────────────────

class BookingDatesSchema(BaseModel):
    checkin: str
    checkout: str


class BookingSchema(BaseModel):
    firstname: str
    lastname: str
    totalprice: int
    depositpaid: bool
    bookingdates: BookingDatesSchema
    additionalneeds: str | None = None


class CreatedBookingSchema(BaseModel):
    bookingid: int
    booking: BookingSchema


class AuthTokenSchema(BaseModel):
    token: str


# ─── HTTP Assertions ─────────────────────────────────────────────────────────

def assert_status(response: httpx.Response, expected: int) -> None:
    """Assert HTTP status with a clean, descriptive failure message."""
    with allure.step(f"Assert status {expected}"):
        assert response.status_code == expected, (
            f"\n[STATUS MISMATCH]\n"
            f"  Expected : {expected}\n"
            f"  Got      : {response.status_code}\n"
            f"  URL      : {response.request.method} {response.request.url}\n"
            f"  Body     : {response.text[:500]}"
        )


def assert_response_time(response: httpx.Response, max_ms: int = 3000) -> None:
    """Assert that the response was received within an acceptable time."""
    elapsed_ms = response.elapsed.total_seconds() * 1000
    with allure.step(f"Assert response time ≤ {max_ms}ms"):
        assert elapsed_ms <= max_ms, (
            f"Response too slow: {elapsed_ms:.0f}ms > {max_ms}ms\n"
            f"  URL: {response.request.url}"
        )


def assert_booking_schema(response: httpx.Response) -> BookingSchema:
    """Validate that the response body matches the BookingSchema."""
    with allure.step("Assert booking schema"):
        try:
            return BookingSchema(**response.json())
        except ValidationError as exc:
            raise AssertionError(
                f"Response does not match BookingSchema:\n{exc}"
            ) from exc


def assert_created_booking_schema(response: httpx.Response) -> CreatedBookingSchema:
    """Validate the POST /booking response shape."""
    with allure.step("Assert created booking schema"):
        try:
            return CreatedBookingSchema(**response.json())
        except ValidationError as exc:
            raise AssertionError(
                f"Response does not match CreatedBookingSchema:\n{exc}"
            ) from exc


def assert_auth_token(response: httpx.Response) -> str:
    """Assert auth response contains a valid token and return it."""
    with allure.step("Assert auth token present"):
        data = response.json()
        assert "token" in data, f"No 'token' in auth response: {data}"
        token = data["token"]
        assert token and token != "Bad credentials", (
            f"Auth failed — received: '{token}'"
        )
        return token


# ─── Database Assertions ──────────────────────────────────────────────────────

def assert_db_record_exists(record, booking_id: int) -> None:
    """Assert that a DB record was found for the given booking ID."""
    with allure.step(f"Assert DB record exists for booking_id={booking_id}"):
        assert record is not None, (
            f"No database record found for booking_id={booking_id}"
        )


def assert_db_record_matches(record, expected: dict) -> None:
    """Assert that DB record fields match the expected values."""
    with allure.step("Assert DB record matches expected data"):
        mismatches = []
        for key, exp_val in expected.items():
            actual_val = getattr(record, key, None)
            if str(actual_val) != str(exp_val):
                mismatches.append(
                    f"  {key}: expected={exp_val!r}, got={actual_val!r}"
                )
        if mismatches:
            raise AssertionError(
                "DB record does not match expected values:\n" + "\n".join(mismatches)
            )
