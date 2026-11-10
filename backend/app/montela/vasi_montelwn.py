"""Κοινή βάση ORM και αποθήκευση χρονοσφραγίδων σε UTC."""

from datetime import datetime, timezone

from sqlalchemy import DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.types import TypeDecorator


class XronosUTC(TypeDecorator):
    """Διατηρεί την UTC ζώνη και κατά την ανάγνωση από SQLite."""

    impl = DateTime
    cache_ok = True

    def process_bind_param(self, timi, dialect):
        if timi is None:
            return None
        if timi.tzinfo is None:
            raise ValueError("Απαιτείται χρονοσφραγίδα με ζώνη ώρας.")
        return timi.astimezone(timezone.utc).replace(tzinfo=None)

    def process_result_value(self, timi, dialect):
        if timi is None:
            return None
        return (
            timi.replace(tzinfo=timezone.utc)
            if timi.tzinfo is None
            else timi.astimezone(timezone.utc)
        )


class VasiMontelwn(DeclarativeBase):
    """Κοινή βάση των μοντέλων της αποικίας."""


class XronikaPedia:
    """Αυτόματη καταγραφή χρόνων δημιουργίας και ενημέρωσης σε UTC."""

    xronos_dimiourgias: Mapped[datetime] = mapped_column(
        XronosUTC(), default=lambda: datetime.now(timezone.utc)
    )
    xronos_enimerwsis: Mapped[datetime] = mapped_column(
        XronosUTC(),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
