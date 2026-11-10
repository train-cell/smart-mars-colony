"""ORM μοντέλα για την υποστήριξη ζωής, χώρους κατοίκησης και αισθητήρες."""

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.montela.vasi_montelwn import VasiMontelwn, XronikaPedia, XronosUTC


class Apoikia(VasiMontelwn, XronikaPedia):
    """Αποικία στον Άρη."""

    __tablename__ = "apoikies"

    id_apoikias: Mapped[str] = mapped_column(String(50), primary_key=True)
    onoma: Mapped[str] = mapped_column(String(100), nullable=False)
    perigrafi: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    xwroi: Mapped[list["XwrosKatoikisis"]] = relationship(
        "XwrosKatoikisis", back_populates="apoikia"
    )


class XwrosKatoikisis(VasiMontelwn, XronikaPedia):
    """Χώρος κατοίκησης / habitat της αποικίας."""

    __tablename__ = "xwroi_katoikisis"

    id_xwrou: Mapped[str] = mapped_column(String(50), primary_key=True)
    id_apoikias: Mapped[str] = mapped_column(
        String(50), ForeignKey("apoikies.id_apoikias"), nullable=False
    )
    onoma: Mapped[str] = mapped_column(String(100), nullable=False)
    plithysmos: Mapped[int] = mapped_column(Integer, default=4)
    ogkos_m3: Mapped[float] = mapped_column(Float, default=1000.0)
    epifaneia_m2: Mapped[float] = mapped_column(Float, default=500.0)
    thermiki_xwritikotita_j_k: Mapped[float] = mapped_column(
        Float, default=1e7, server_default="10000000"
    )
    rythmos_diarrois_piesis_pa_h: Mapped[float] = mapped_column(
        Float, default=0.0, server_default="0"
    )
    syntelestis_thermoperatotitas_u: Mapped[float] = mapped_column(Float, default=0.2)

    # Θερμοκρασίες [K]
    epithymiti_thermokrasia_k: Mapped[float] = mapped_column(Float, default=293.0)  # ~20°C
    thermokrasia_eswteriki_k: Mapped[float] = mapped_column(Float, default=293.0)
    thermokrasia_exwteriki_k: Mapped[float] = mapped_column(Float, default=213.0)  # -60°C baseline

    # Ατμοσφαιρικές συνθήκες
    piesi_pa: Mapped[float] = mapped_column(Float, default=101325.0)  # 1 atm
    pososto_oxygonou: Mapped[float] = mapped_column(Float, default=0.21)  # 21%
    pososto_dioxeidiou_anthraka: Mapped[float] = mapped_column(Float, default=0.0004)  # 400 ppm
    sxetiki_ygrasia: Mapped[float] = mapped_column(Float, default=0.45)  # 45%

    # Έκδοση αισιόδοξου ταυτοχρονισμού
    ekdosi_katastasis: Mapped[int] = mapped_column(Integer, default=1)

    __mapper_args__ = {"version_id_col": ekdosi_katastasis}

    apoikia: Mapped["Apoikia"] = relationship("Apoikia", back_populates="xwroi")
    syskeves: Mapped[list["SyskeviYpostiriksisZwis"]] = relationship(
        "SyskeviYpostiriksisZwis", back_populates="xwros"
    )
    apothema_oxygonou: Mapped[Optional["ApothemaOxygonou"]] = relationship(
        "ApothemaOxygonou", back_populates="xwros", uselist=False
    )


class SyskeviYpostiriksisZwis(VasiMontelwn, XronikaPedia):
    """Εξοπλισμός υποστήριξης ζωής (θερμαντήρας, scrubber CO2, ηλεκτρόλυση)."""

    __tablename__ = "syskeves_ypostiriksis_zwis"

    id_syskevis: Mapped[str] = mapped_column(String(50), primary_key=True)
    id_xwrou: Mapped[str] = mapped_column(
        String(50), ForeignKey("xwroi_katoikisis.id_xwrou"), nullable=False
    )
    onoma: Mapped[str] = mapped_column(String(100), nullable=False)
    typos_syskevis: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # thermantiras, ilektrolysi, scrubber
    katastasi_leitourgias: Mapped[str] = mapped_column(String(50), default="energi")
    katanalwsi_isxyos_w: Mapped[float] = mapped_column(Float, default=0.0)

    xwros: Mapped["XwrosKatoikisis"] = relationship("XwrosKatoikisis", back_populates="syskeves")


class ApothemaOxygonou(VasiMontelwn, XronikaPedia):
    """Αποθηκευμένο εφεδρικό οξυγόνο σε δεξαμενές πίεσης."""

    __tablename__ = "apothema_oxygonou"

    id_apothematos: Mapped[str] = mapped_column(String(50), primary_key=True)
    id_xwrou: Mapped[str] = mapped_column(
        String(50), ForeignKey("xwroi_katoikisis.id_xwrou"), nullable=False
    )
    diathesimo_kg: Mapped[float] = mapped_column(Float, default=500.0)
    xwritikotita_kg: Mapped[float] = mapped_column(Float, default=1000.0)
    rythmos_paragwgis_kg_h: Mapped[float] = mapped_column(Float, default=0.1)

    xwros: Mapped["XwrosKatoikisis"] = relationship(
        "XwrosKatoikisis", back_populates="apothema_oxygonou"
    )


class Aisthitiras(VasiMontelwn, XronikaPedia):
    """Αισθητήρας μέτρησης φυσικών μεγεθών."""

    __tablename__ = "aisthitires"

    id_aisthitira: Mapped[str] = mapped_column(String(50), primary_key=True)
    kodikos_aisthitira: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    typos_megethous: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # thermokrasia, piesi, oxygono, ktl.
    yposystima: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # ypostiriksi_zwis, poroi, apostoles
    id_xwrou: Mapped[Optional[str]] = mapped_column(
        String(50), ForeignKey("xwroi_katoikisis.id_xwrou"), nullable=True
    )
    monada: Mapped[str] = mapped_column(String(20), nullable=False)
    katastasi: Mapped[str] = mapped_column(String(30), default="leitourgikos")

    metriseis: Mapped[list["MetrisiAisthitira"]] = relationship(
        "MetrisiAisthitira", back_populates="aisthitiras", cascade="all, delete-orphan"
    )


class MetrisiAisthitira(VasiMontelwn):
    """Ιστορική μέτρηση αισθητήρα."""

    __tablename__ = "metriseis_aisthitirwn"

    id_metrisis: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_aisthitira: Mapped[str] = mapped_column(
        String(50), ForeignKey("aisthitires.id_aisthitira"), nullable=False
    )
    timi: Mapped[float] = mapped_column(Float, nullable=False)
    monada: Mapped[str] = mapped_column(String(20), nullable=False)
    eidos: Mapped[str] = mapped_column(String(30), default="metrimeno")
    pigi: Mapped[str] = mapped_column(String(50), default="prosomoiwmenos_aisthitiras")
    poiotita: Mapped[str] = mapped_column(String(30), default="egkyro")
    tasi: Mapped[str] = mapped_column(String(30), default="statheri")
    apolyti_avevaiotita: Mapped[float] = mapped_column(Float, default=0.1)
    einai_palio: Mapped[bool] = mapped_column(Boolean, default=False)
    xronos_paralavis: Mapped[Optional[datetime]] = mapped_column(XronosUTC(), nullable=True)
    xronos_metrisis: Mapped[datetime] = mapped_column(XronosUTC(), nullable=False)

    aisthitiras: Mapped["Aisthitiras"] = relationship("Aisthitiras", back_populates="metriseis")
