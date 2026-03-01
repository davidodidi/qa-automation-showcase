"""
Booking API Client
==================
A clean, reusable wrapper around the Restful-Booker REST API.
All methods return the raw httpx.Response so callers control assertions.

Design choices:
- httpx instead of requests → async-ready, better type hints
- tenacity retry on 503 (the free Heroku app sleeps between calls)
- Each method logs a structured Allure step automatically
"""
from __future__ import annotations

import httpx
import allure
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type

from config.settings import settings


class BookingClient:
    """HTTP client for the Restful-Booker API."""

    def __init__(self, base_url: str = None, token: str = None):
        self.base_url = (base_url or settings.base_url).rstrip("/")
        self._token = token
        self._client = httpx.Client(
            base_url=self.base_url,
            headers={"Content-Type": "application/json", "Accept": "application/json"},
            timeout=30.0,
        )

    # ── Auth ──────────────────────────────────────────────────────────────────

    @allure.step("POST /auth — create token")
    def create_token(self, username: str = None, password: str = None) -> httpx.Response:
        payload = {
            "username": username or settings.admin_username,
            "password": password or settings.admin_password,
        }
        response = self._post("/auth", json=payload)
        if response.status_code == 200 and "token" in response.json():
            self._token = response.json()["token"]
        return response

    # ── Bookings ──────────────────────────────────────────────────────────────

    @allure.step("GET /booking — list all bookings")
    def get_all_bookings(self, **filters) -> httpx.Response:
        return self._client.get("/booking", params=filters)

    @allure.step("GET /booking/{booking_id}")
    def get_booking(self, booking_id: int) -> httpx.Response:
        return self._client.get(f"/booking/{booking_id}")

    @allure.step("POST /booking — create booking")
    def create_booking(self, payload: dict) -> httpx.Response:
        return self._post("/booking", json=payload)

    @allure.step("PUT /booking/{booking_id} — full update")
    def update_booking(self, booking_id: int, payload: dict) -> httpx.Response:
        return self._client.put(
            f"/booking/{booking_id}",
            json=payload,
            headers=self._auth_headers(),
        )

    @allure.step("PATCH /booking/{booking_id} — partial update")
    def partial_update_booking(self, booking_id: int, payload: dict) -> httpx.Response:
        return self._client.patch(
            f"/booking/{booking_id}",
            json=payload,
            headers=self._auth_headers(),
        )

    @allure.step("DELETE /booking/{booking_id}")
    def delete_booking(self, booking_id: int) -> httpx.Response:
        return self._client.delete(
            f"/booking/{booking_id}",
            headers=self._auth_headers(),
        )

    # ── Helpers ───────────────────────────────────────────────────────────────

    @retry(
        stop=stop_after_attempt(settings.api_retry_attempts),
        wait=wait_fixed(settings.api_retry_wait),
        retry=retry_if_exception_type(httpx.TransportError),
    )
    def _post(self, path: str, **kwargs) -> httpx.Response:
        return self._client.post(path, **kwargs)

    def _auth_headers(self) -> dict:
        if not self._token:
            raise RuntimeError(
                "No auth token. Call create_token() before mutating bookings."
            )
        return {"Cookie": f"token={self._token}"}

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self._client.close()
