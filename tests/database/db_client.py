"""
Database Client — Shadow DB
============================
Maintains a local SQLite shadow database that mirrors booking state.
After every API create/delete call, the test suite writes to this DB,
then validates the data is exactly what the API returned.

This simulates the DB validation layer you'd find in a real project
where you have direct database access alongside the API.
"""
from __future__ import annotations

from datetime import datetime
from sqlalchemy import (
    create_engine,
    String,
    Integer,
    Boolean,
    DateTime,
    select,
    delete,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    Session,
)

from config.settings import settings


# ─── ORM Models ───────────────────────────────────────────────────────────────

class Base(DeclarativeBase):
    pass


class BookingRecord(Base):
    """Mirrors a booking as stored after API validation."""

    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    booking_id: Mapped[int] = mapped_column(Integer, unique=True, index=True)
    firstname: Mapped[str] = mapped_column(String(100))
    lastname: Mapped[str] = mapped_column(String(100))
    totalprice: Mapped[int] = mapped_column(Integer)
    depositpaid: Mapped[bool] = mapped_column(Boolean)
    checkin: Mapped[str] = mapped_column(String(20))
    checkout: Mapped[str] = mapped_column(String(20))
    additionalneeds: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )

    def __repr__(self) -> str:
        return (
            f"<BookingRecord id={self.booking_id} "
            f"{self.firstname} {self.lastname} "
            f"{self.checkin}→{self.checkout}>"
        )


class TestRunRecord(Base):
    """Tracks test run metadata for reporting purposes."""

    __tablename__ = "test_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    run_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    environment: Mapped[str] = mapped_column(String(50))
    total_tests: Mapped[int] = mapped_column(Integer, default=0)
    passed: Mapped[int] = mapped_column(Integer, default=0)
    failed: Mapped[int] = mapped_column(Integer, default=0)


# ─── Database Client ──────────────────────────────────────────────────────────

class DBClient:
    """Thin wrapper around SQLAlchemy for test use."""

    def __init__(self, database_url: str = None):
        url = database_url or settings.database_url
        self._engine = create_engine(url, echo=False)
        Base.metadata.create_all(self._engine)

    # ── Write ────────────────────────────────────────────────────

    def save_booking(self, booking_id: int, booking_data: dict) -> BookingRecord:
        """Persist a booking returned from the API into the shadow DB."""
        record = BookingRecord(
            booking_id=booking_id,
            firstname=booking_data["firstname"],
            lastname=booking_data["lastname"],
            totalprice=booking_data["totalprice"],
            depositpaid=booking_data["depositpaid"],
            checkin=booking_data["bookingdates"]["checkin"],
            checkout=booking_data["bookingdates"]["checkout"],
            additionalneeds=booking_data.get("additionalneeds"),
        )
        with Session(self._engine) as session:
            session.add(record)
            session.commit()
            session.refresh(record)
        return record

    def delete_booking(self, booking_id: int) -> int:
        """Remove a booking from the shadow DB. Returns rows deleted."""
        with Session(self._engine) as session:
            result = session.execute(
                delete(BookingRecord).where(BookingRecord.booking_id == booking_id)
            )
            session.commit()
            return result.rowcount

    # ── Read ─────────────────────────────────────────────────────

    def get_booking(self, booking_id: int) -> BookingRecord | None:
        with Session(self._engine) as session:
            return session.execute(
                select(BookingRecord).where(BookingRecord.booking_id == booking_id)
            ).scalar_one_or_none()

    def get_all_bookings(self) -> list[BookingRecord]:
        with Session(self._engine) as session:
            return list(session.execute(select(BookingRecord)).scalars().all())

    def count_bookings(self) -> int:
        return len(self.get_all_bookings())

    # ── Cleanup ──────────────────────────────────────────────────

    def clear_all(self) -> None:
        """Wipe the shadow DB — call in session-scoped teardown."""
        with Session(self._engine) as session:
            session.execute(delete(BookingRecord))
            session.commit()

    def booking_exists(self, booking_id: int) -> bool:
        return self.get_booking(booking_id) is not None
