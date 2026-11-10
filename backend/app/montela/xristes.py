"""ORM μοντέλα για χρήστες, ρόλους και μεταβιβάσεις δικαιωμάτων."""

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.montela.vasi_montelwn import VasiMontelwn, XronikaPedia, XronosUTC


class Xristis(VasiMontelwn, XronikaPedia):
    """Χρήστης του συστήματος."""

    __tablename__ = "xristes"

    id_xristi: Mapped[str] = mapped_column(String(50), primary_key=True)
    onoma: Mapped[str] = mapped_column(String(100), nullable=False)
    ilektroniki_dieythynsi: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    vasikos_rolos: Mapped[str] = mapped_column(String(50), nullable=False)
    energos: Mapped[bool] = mapped_column(Boolean, default=True)

    roloi: Mapped[list["AnathesiRolouXristi"]] = relationship(
        "AnathesiRolouXristi", back_populates="xristis", cascade="all, delete-orphan"
    )


class AnathesiRolouXristi(VasiMontelwn):
    """Ενεργοί ρόλοι χρήστη."""

    __tablename__ = "roloi_xristwn"

    id_rolou: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_xristi: Mapped[str] = mapped_column(
        String(50), ForeignKey("xristes.id_xristi"), nullable=False
    )
    rolos: Mapped[str] = mapped_column(String(50), nullable=False)

    xristis: Mapped["Xristis"] = relationship("Xristis", back_populates="roloi")


class MetavivasiDikaiwmatos(VasiMontelwn, XronikaPedia):
    """Μεταβίβαση δικαιώματος/ρόλου από συντονιστή σε άλλον χρήστη (CORE-18)."""

    __tablename__ = "metavivaseis_dikaiwmatwn"

    id_metavivasis: Mapped[str] = mapped_column(String(50), primary_key=True)
    id_syntonisti: Mapped[str] = mapped_column(
        String(50), ForeignKey("xristes.id_xristi"), nullable=False
    )
    id_paralipti: Mapped[str] = mapped_column(
        String(50), ForeignKey("xristes.id_xristi"), nullable=False
    )
    rolos: Mapped[str] = mapped_column(String(50), nullable=False)
    pedio_efarmogis: Mapped[str] = mapped_column(String(100), default="geniko")
    xronos_enarksis: Mapped[datetime] = mapped_column(XronosUTC(), nullable=False)
    xronos_liksis: Mapped[datetime] = mapped_column(XronosUTC(), nullable=False)
    energo: Mapped[bool] = mapped_column(Boolean, default=True)
    aitiologia: Mapped[str] = mapped_column(Text, nullable=False)
    xronos_anaklisis: Mapped[Optional[datetime]] = mapped_column(XronosUTC(), nullable=True)
