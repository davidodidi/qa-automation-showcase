"""
Test Data Factory
=================
Generates realistic, randomised test data for every layer of the test suite.
Uses Faker under the hood so data is always unique across parallel runs.
"""
from __future__ import annotations

import random
from dataclasses import dataclass, asdict
from datetime import date, timedelta
from faker import Faker

fake = Faker("en_GB")  # UK locale matches the hotel booking context


# ─── Data Models (dataclasses keep things lightweight) ────────────────────────

@dataclass
class BookingDates:
    checkin: str
    checkout: str

    @classmethod
    def generate(cls, nights: int = None) -> "BookingDates":
        nights = nights or random.randint(1, 14)
        checkin = date.today() + timedelta(days=random.randint(1, 30))
        checkout = checkin + timedelta(days=nights)
        return cls(
            checkin=checkin.strftime("%Y-%m-%d"),
            checkout=checkout.strftime("%Y-%m-%d"),
        )


@dataclass
class BookingPayload:
    firstname: str
    lastname: str
    totalprice: int
    depositpaid: bool
    bookingdates: BookingDates
    additionalneeds: str

    def to_dict(self) -> dict:
        d = asdict(self)
        return d

    @classmethod
    def generate(cls, **overrides) -> "BookingPayload":
        payload = cls(
            firstname=overrides.get("firstname", fake.first_name()),
            lastname=overrides.get("lastname", fake.last_name()),
            totalprice=overrides.get("totalprice", random.randint(50, 500)),
            depositpaid=overrides.get("depositpaid", random.choice([True, False])),
            bookingdates=overrides.get("bookingdates", BookingDates.generate()),
            additionalneeds=overrides.get(
                "additionalneeds",
                random.choice(["Breakfast", "Lunch", "Dinner", "Extra pillow", "None"]),
            ),
        )
        return payload


@dataclass
class AuthPayload:
    username: str
    password: str

    def to_dict(self) -> dict:
        return asdict(self)


# ─── Factory Functions ────────────────────────────────────────────────────────

class DataFactory:
    """Central factory — import this in conftest.py and inject as a fixture."""

    @staticmethod
    def booking(*, nights: int = None, **overrides) -> BookingPayload:
        """Generate a randomised booking payload."""
        if nights:
            overrides["bookingdates"] = BookingDates.generate(nights=nights)
        return BookingPayload.generate(**overrides)

    @staticmethod
    def admin_credentials() -> AuthPayload:
        """Return the well-known admin credentials for Restful-Booker."""
        return AuthPayload(username="admin", password="password")

    @staticmethod
    def invalid_credentials() -> AuthPayload:
        return AuthPayload(username=fake.user_name(), password=fake.password())

    @staticmethod
    def bulk_bookings(count: int = 5) -> list[BookingPayload]:
        return [BookingPayload.generate() for _ in range(count)]


# Singleton — import `factory` directly in tests
factory = DataFactory()
