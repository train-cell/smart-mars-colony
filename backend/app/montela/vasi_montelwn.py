"""Βασική κλάση ORM για όλα τα μοντέλα της εφαρμογής."""

from datetime import datetime, timezone

from sqlalchemy import DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class VasiMontelwn(DeclarativeBase):
    """Κοινή βάση Declarative για όλα τα SQLAlchemy 2.0 models."""

    pass


class XronosStigmaMixin:
    """Mixin για αυτόματη καταγραφή χρόνου δημιουργίας και ενημέρωσης σε UTC."""

    xronos_dimiourgias: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
    xronos_enimerwsis: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
