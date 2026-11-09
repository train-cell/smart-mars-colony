"""ORM μοντέλα για οχήματα εξερεύνησης (rover), αποστολές και εξωτερικούς κινδύνους."""

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.montela.vasi_montelwn import VasiMontelwn, XronosStigmaMixin


class OximaExerevnis(VasiMontelwn, XronosStigmaMixin):
    """Όχημα εξερεύνησης (rover) της αποικίας."""

    __tablename__ = "oximata_exerevnis"

    id_oximatos: Mapped[str] = mapped_column(String(50), primary_key=True)
    onoma: Mapped[str] = mapped_column(String(100), nullable=False)
    maza_kg: Mapped[float] = mapped_column(Float, default=800.0)
    apostasi_apo_vasi_km: Mapped[float] = mapped_column(Float, default=2.0)
    taxytita_kmh: Mapped[float] = mapped_column(Float, default=4.0)
    energeia_kwh: Mapped[float] = mapped_column(Float, default=0.8)
    efedreia_kwh: Mapped[float] = mapped_column(Float, default=0.2)
    mesi_isxys_kw: Mapped[float] = mapped_column(Float, default=0.6)

    katastasi_oximatos: Mapped[str] = mapped_column(
        String(50), default="se_kinisi"
    )  # stasi, se_kinisi, asfalis_stasi
    katastasi_epikoinwnias: Mapped[str] = mapped_column(
        String(50), default="statheri"
    )  # statheri, ypovathmismeni, apousia
    ekdosi_katastasis: Mapped[int] = mapped_column(Integer, default=1)

    apostoles: Mapped[list["ApostoliOximatos"]] = relationship(
        "ApostoliOximatos", back_populates="oxima", cascade="all, delete-orphan"
    )


class ApostoliOximatos(VasiMontelwn, XronosStigmaMixin):
    """Αποστολή εξερεύνησης οχήματος."""

    __tablename__ = "apostoles_oximatwn"

    id_apostolis: Mapped[str] = mapped_column(String(50), primary_key=True)
    id_oximatos: Mapped[str] = mapped_column(
        String(50), ForeignKey("oximata_exerevnis.id_oximatos"), nullable=False
    )
    titlos: Mapped[str] = mapped_column(String(100), nullable=False)
    skopos: Mapped[str] = mapped_column(Text, nullable=False)
    katastasi_apostolis: Mapped[str] = mapped_column(String(50), default="se_exelixi")
    xronos_enarksis: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    xronos_oloklirwsis: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    oxima: Mapped["OximaExerevnis"] = relationship("OximaExerevnis", back_populates="apostoles")
    shmeia_diadromis: Mapped[list["ShmeioDiadromis"]] = relationship(
        "ShmeioDiadromis", back_populates="apostoli", cascade="all, delete-orphan"
    )


class ShmeioDiadromis(VasiMontelwn):
    """Σημείο διαδρομής (waypoint) αποστολής."""

    __tablename__ = "shmeia_diadromis"

    id_shmeiou: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_apostolis: Mapped[str] = mapped_column(
        String(50), ForeignKey("apostoles_oximatwn.id_apostolis"), nullable=False
    )
    seira: Mapped[int] = mapped_column(Integer, nullable=False)
    syntetagmeni_x: Mapped[float] = mapped_column(Float, default=0.0)
    syntetagmeni_y: Mapped[float] = mapped_column(Float, default=0.0)
    apostasi_apo_proigoumeno_m: Mapped[float] = mapped_column(Float, default=500.0)
    klisi_rad: Mapped[float] = mapped_column(Float, default=0.0)

    apostoli: Mapped["ApostoliOximatos"] = relationship(
        "ApostoliOximatos", back_populates="shmeia_diadromis"
    )


class ExwterikosKindynos(VasiMontelwn, XronosStigmaMixin):
    """Εξωτερικός περιβαλλοντικός κίνδυνος (καταιγίδα σκόνης, ακτινοβολία)."""

    __tablename__ = "exwterikoi_kindynoi"

    id_kindynou: Mapped[str] = mapped_column(String(50), primary_key=True)
    typos_kindynou: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # kataigida_skonis, aktinovolia, ptosi_piesis
    oratotita_m: Mapped[float] = mapped_column(Float, default=1000.0)
    epipedo_aktinovolias: Mapped[float] = mapped_column(Float, default=0.1)
    sovarotita: Mapped[str] = mapped_column(String(30), default="mesaia")
    eidos_dedomenwn: Mapped[str] = mapped_column(
        String(30), default="metrimeno"
    )  # metrimeno, provlepsi
    perigrafi: Mapped[str] = mapped_column(Text, nullable=False)
    xronos_katagrafis: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
