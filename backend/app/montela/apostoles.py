"""ORM μοντέλα για οχήματα εξερεύνησης (rover), αποστολές και εξωτερικούς κινδύνους."""

from datetime import datetime
from typing import Optional

from sqlalchemy import JSON, Boolean, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.montela.vasi_montelwn import VasiMontelwn, XronikaPedia, XronosUTC


class OximaExerevnis(VasiMontelwn, XronikaPedia):
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

    xwritikotita_energeias_kwh: Mapped[float] = mapped_column(
        Float, default=1.0, server_default="1"
    )
    isxys_fortisis_kw: Mapped[float] = mapped_column(Float, default=0.2, server_default="0.2")

    isxys_kinisis_kw: Mapped[float] = mapped_column(Float, default=0.6, server_default="0.6")
    voithitiki_isxys_w: Mapped[float] = mapped_column(Float, default=100.0, server_default="100")
    syntetagmeni_x: Mapped[float] = mapped_column(Float, default=0.0, server_default="0")
    syntetagmeni_y: Mapped[float] = mapped_column(Float, default=0.0, server_default="0")
    maza_fortiou_kg: Mapped[float] = mapped_column(Float, default=0.0, server_default="0")
    plithos_plirwmatos: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    xronos_teleftaias_tilemetrias: Mapped[Optional[datetime]] = mapped_column(
        XronosUTC(), nullable=True
    )
    kathysterisi_epikoinwnias_s: Mapped[float] = mapped_column(
        Float, default=0.0, server_default="0"
    )
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


class ApostoliOximatos(VasiMontelwn, XronikaPedia):
    """Αποστολή εξερεύνησης οχήματος."""

    __tablename__ = "apostoles_oximatwn"

    id_apostolis: Mapped[str] = mapped_column(String(50), primary_key=True)
    id_oximatos: Mapped[str] = mapped_column(
        String(50), ForeignKey("oximata_exerevnis.id_oximatos"), nullable=False
    )
    apostasi_km: Mapped[float] = mapped_column(Float, default=0.0, server_default="0")
    ektimwmeni_diarkeia_wres: Mapped[float] = mapped_column(Float, default=0.0, server_default="0")
    apaitoumeni_energeia_kwh: Mapped[float] = mapped_column(Float, default=0.0, server_default="0")
    energeia_katanalwtheisa_kwh: Mapped[float] = mapped_column(
        Float, default=0.0, server_default="0"
    )
    maza_fortiou_kg: Mapped[float] = mapped_column(Float, default=0.0, server_default="0")
    plithos_plirwmatos: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    sxedio: Mapped[dict] = mapped_column(JSON, default=dict, server_default="{}")
    id_entolis: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    titlos: Mapped[str] = mapped_column(String(100), nullable=False)
    skopos: Mapped[str] = mapped_column(Text, nullable=False)
    katastasi_apostolis: Mapped[str] = mapped_column(String(50), default="se_exelixi")
    xronos_enarksis: Mapped[datetime] = mapped_column(XronosUTC(), nullable=False)
    xronos_oloklirwsis: Mapped[Optional[datetime]] = mapped_column(XronosUTC(), nullable=True)

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


class ExwterikosKindynos(VasiMontelwn, XronikaPedia):
    """Εξωτερικός περιβαλλοντικός κίνδυνος (καταιγίδα σκόνης, ακτινοβολία)."""

    __tablename__ = "exwterikoi_kindynoi"

    id_kindynou: Mapped[str] = mapped_column(String(50), primary_key=True)
    typos_kindynou: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # kataigida_skonis, aktinovolia, ptosi_piesis
    oratotita_m: Mapped[float] = mapped_column(Float, default=1000.0)
    epipedo_aktinovolias: Mapped[float] = mapped_column(Float, default=0.1)
    monada_aktinovolias: Mapped[str] = mapped_column(
        String(30), default="mSv/h", server_default="mSv/h"
    )
    pigi: Mapped[str] = mapped_column(
        String(100), default="prosomoiwsi", server_default="prosomoiwsi"
    )
    apolyti_avevaiotita: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    energi: Mapped[bool] = mapped_column(Boolean, default=True, server_default="1")
    sovarotita: Mapped[str] = mapped_column(String(30), default="mesaia")
    eidos_dedomenwn: Mapped[str] = mapped_column(
        String(30), default="metrimeno"
    )  # metrimeno, provlepsi
    perigrafi: Mapped[str] = mapped_column(Text, nullable=False)
    xronos_katagrafis: Mapped[datetime] = mapped_column(XronosUTC(), nullable=False)
