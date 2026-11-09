"""ORM μοντέλα για τους πόρους: θερμοκήπια, νερό, φωτοβολταϊκά και ενέργεια."""

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.montela.vasi_montelwn import VasiMontelwn, XronosStigmaMixin


class Thermokipio(VasiMontelwn, XronosStigmaMixin):
    """Θερμοκήπιο της αποικίας."""

    __tablename__ = "thermokipia"

    id_thermokipiou: Mapped[str] = mapped_column(String(50), primary_key=True)
    onoma: Mapped[str] = mapped_column(String(100), nullable=False)
    thermokrasia_k: Mapped[float] = mapped_column(Float, default=295.0)  # ~22°C
    ygrasia_aera: Mapped[float] = mapped_column(Float, default=0.65)  # 65%
    ekdosi_katastasis: Mapped[int] = mapped_column(Integer, default=1)

    zwnes: Mapped[list["ZwniThermokipiou"]] = relationship(
        "ZwniThermokipiou", back_populates="thermokipio"
    )


class ZwniThermokipiou(VasiMontelwn, XronosStigmaMixin):
    """Ζώνη καλλιέργειας εντός θερμοκηπίου."""

    __tablename__ = "zwnes_thermokipiou"

    id_zwnis: Mapped[str] = mapped_column(String(50), primary_key=True)
    id_thermokipiou: Mapped[str] = mapped_column(
        String(50), ForeignKey("thermokipia.id_thermokipiou"), nullable=False
    )
    onoma_zwnis: Mapped[str] = mapped_column(String(100), nullable=False)
    fyto: Mapped[str] = mapped_column(String(50), default="patates_kai_lachanika")
    ygrasia_ypostrwmatos: Mapped[float] = mapped_column(Float, default=0.55)  # 55%
    epithymiti_ygrasia: Mapped[float] = mapped_column(Float, default=0.60)
    katastasi_fwtismou: Mapped[str] = mapped_column(String(30), default="fysiko_kai_texnito")

    thermokipio: Mapped["Thermokipio"] = relationship("Thermokipio", back_populates="zwnes")


class DexameniNerou(VasiMontelwn, XronosStigmaMixin):
    """Κεντρική ή τοπική δεξαμενή αποθήκευσης νερού."""

    __tablename__ = "dexamenes_nerou"

    id_dexamenis: Mapped[str] = mapped_column(String(50), primary_key=True)
    onoma: Mapped[str] = mapped_column(String(100), nullable=False)
    xwritikotita_l: Mapped[float] = mapped_column(Float, default=10000.0)
    trexwn_ogkos_l: Mapped[float] = mapped_column(Float, default=7500.0)
    efedreia_asfaleias_l: Mapped[float] = mapped_column(Float, default=1500.0)
    ekdosi_katastasis: Mapped[int] = mapped_column(Integer, default=1)

    roes: Mapped[list["RoiNerou"]] = relationship("RoiNerou", back_populates="dexameni")


class RoiNerou(VasiMontelwn):
    """Καταγραφή ροών νερού (εισροή, κατανάλωση, άρδευση, διαρροή, ανακύκλωση)."""

    __tablename__ = "roes_nerou"

    id_rois: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_dexamenis: Mapped[str] = mapped_column(
        String(50), ForeignKey("dexamenes_nerou.id_dexamenis"), nullable=False
    )
    typos_rois: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # eisroi, ardefsi, anakyklwsi, diarros
    rythmos_l_h: Mapped[float] = mapped_column(Float, nullable=False)
    perigrafi: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    xronos_katagrafis: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    dexameni: Mapped["DexameniNerou"] = relationship("DexameniNerou", back_populates="roes")


class ProgrammaArdefsis(VasiMontelwn, XronosStigmaMixin):
    """Προγραμματισμένη άρδευση ζώνης θερμοκηπίου (RES-05, RES-06)."""

    __tablename__ = "programmata_ardefsis"

    id_programmatos: Mapped[str] = mapped_column(String(50), primary_key=True)
    id_thermokipiou: Mapped[str] = mapped_column(
        String(50), ForeignKey("thermokipia.id_thermokipiou"), nullable=False
    )
    id_zwnis: Mapped[str] = mapped_column(
        String(50), ForeignKey("zwnes_thermokipiou.id_zwnis"), nullable=False
    )
    id_dexamenis: Mapped[str] = mapped_column(
        String(50), ForeignKey("dexamenes_nerou.id_dexamenis"), nullable=False
    )
    posotita_nerou_l: Mapped[float] = mapped_column(Float, nullable=False)
    xronos_enarksis: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    diarkeia_lepta: Mapped[int] = mapped_column(Integer, default=30)
    katastasi: Mapped[str] = mapped_column(
        String(30), default="programmatismeno"
    )  # programmatismeno, se_exelixi, oloklirothike, akyrothike
    id_proepiskopisis: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)


class ProgrammaAnakyklwsis(VasiMontelwn, XronosStigmaMixin):
    """Προγραμματισμός ανακύκλωσης γκρίζου/ακάθαρτου νερού (RES-12)."""

    __tablename__ = "programmata_anakyklwsis"

    id_programmatos: Mapped[str] = mapped_column(String(50), primary_key=True)
    id_dexamenis: Mapped[str] = mapped_column(
        String(50), ForeignKey("dexamenes_nerou.id_dexamenis"), nullable=False
    )
    posotita_anakyklwsis_l: Mapped[float] = mapped_column(Float, nullable=False)
    xronos_enarksis: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    diarkeia_lepta: Mapped[int] = mapped_column(Integer, default=60)
    apodosi_anakyklwsis: Mapped[float] = mapped_column(Float, default=0.85)  # 85% ανάκτηση
    katastasi: Mapped[str] = mapped_column(String(30), default="programmatismeno")


class ProgrammaFwtismou(VasiMontelwn, XronosStigmaMixin):
    """Προγραμματισμός τεχνητού φωτισμού θερμοκηπίου (RES-13)."""

    __tablename__ = "programmata_fwtismou"

    id_programmatos: Mapped[str] = mapped_column(String(50), primary_key=True)
    id_thermokipiou: Mapped[str] = mapped_column(
        String(50), ForeignKey("thermokipia.id_thermokipiou"), nullable=False
    )
    id_zwnis: Mapped[str] = mapped_column(
        String(50), ForeignKey("zwnes_thermokipiou.id_zwnis"), nullable=False
    )
    isxys_kw: Mapped[float] = mapped_column(Float, default=2.0)
    xronos_enarksis: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    xronos_liksis: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    katastasi: Mapped[str] = mapped_column(String(30), default="programmatismeno")


class Fwtovoltaiko(VasiMontelwn, XronosStigmaMixin):
    """Φωτοβολταϊκή συστοιχία παραγωγής ηλεκτρικής ισχύος."""

    __tablename__ = "fwtovoltaika"

    id_fwtovoltaikou: Mapped[str] = mapped_column(String(50), primary_key=True)
    onoma: Mapped[str] = mapped_column(String(100), nullable=False)
    epifaneia_m2: Mapped[float] = mapped_column(Float, default=100.0)
    apodosi_eta: Mapped[float] = mapped_column(Float, default=0.20)
    syntelestis_epikathisis_f: Mapped[float] = mapped_column(
        Float, default=0.8
    )  # 0.8 κανονικά, 0.5 καταιγίδα
    aktinovolia_w_m2: Mapped[float] = mapped_column(
        Float, default=300.0
    )  # 300 κανονικά, 80 καταιγίδα
    isxys_paragwgis_w: Mapped[float] = mapped_column(Float, default=4800.0)


class Syssoreftis(VasiMontelwn, XronosStigmaMixin):
    """Συσσωρευτής αποθήκευσης ενέργειας (μπαταρία αποικίας)."""

    __tablename__ = "syssoreftes"

    id_syssorefti: Mapped[str] = mapped_column(String(50), primary_key=True)
    onoma: Mapped[str] = mapped_column(String(100), nullable=False)
    xwritikotita_kwh: Mapped[float] = mapped_column(Float, default=50.0)
    energeia_kwh: Mapped[float] = mapped_column(
        Float, default=30.0
    )  # Αξιοποιήσιμη μετά την εφεδρεία
    efedreia_kwh: Mapped[float] = mapped_column(Float, default=10.0)
    katastasi: Mapped[str] = mapped_column(String(30), default="kanoniki_leitourgia")


class EnergeiakoFortio(VasiMontelwn, XronosStigmaMixin):
    """Ηλεκτρικό φορτίο της αποικίας ανά εγκατάσταση."""

    __tablename__ = "energeiaka_fortia"

    id_fortiou: Mapped[str] = mapped_column(String(50), primary_key=True)
    onoma: Mapped[str] = mapped_column(String(100), nullable=False)
    egkatastasi: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # xwros_katoikisis, thermokipio, vasi
    isxys_kw: Mapped[float] = mapped_column(Float, nullable=False)
    einai_krisimo: Mapped[bool] = mapped_column(Boolean, default=False)
    einai_anavlito: Mapped[bool] = mapped_column(Boolean, default=True)
    energo: Mapped[bool] = mapped_column(Boolean, default=True)
    proteraiotita: Mapped[int] = mapped_column(Integer, default=1)  # 1: μέγιστη προτεραιότητα
