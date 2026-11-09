"""ORM μοντέλα για συναγερμούς, εντολές, σενάρια, αποφάσεις και audit trail."""

from datetime import datetime
from typing import Optional

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.montela.vasi_montelwn import VasiMontelwn, XronosStigmaMixin


class Synagermos(VasiMontelwn, XronosStigmaMixin):
    """Συναγερμός ασφαλείας της αποικίας (SHARED-02, SHARED-03, SHARED-08)."""

    __tablename__ = "synagermoi"

    id_synagermou: Mapped[str] = mapped_column(String(50), primary_key=True)
    titlos: Mapped[str] = mapped_column(String(100), nullable=False)
    perigrafi: Mapped[str] = mapped_column(Text, nullable=False)
    aitia: Mapped[str] = mapped_column(Text, nullable=False)
    epiptwsi: Mapped[str] = mapped_column(Text, nullable=False)
    systasi: Mapped[str] = mapped_column(Text, nullable=False)
    yposystima: Mapped[str] = mapped_column(String(50), nullable=False)
    sovarotita: Mapped[str] = mapped_column(
        String(30), default="mesaia"
    )  # xamili, mesaia, ypsili, krisimi
    katastasi: Mapped[str] = mapped_column(
        String(30), default="energos"
    )  # energos, anagnwrismenos, epilymenos

    # Αναγνώριση vs Επίλυση (διαφορετικές ενέργειες και ρόλοι)
    id_xristi_anagnwrisis: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    xronos_anagnwrisis: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    id_xristi_epilysis: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    xronos_epilysis: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    sxolio_epilysis: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    epanalamvanomenos: Mapped[bool] = mapped_column(Boolean, default=False)


class Entoli(VasiMontelwn, XronosStigmaMixin):
    """Εντολή ελέγχου αποικίας με πλήρη καταγραφή κύκλου ζωής (CORE-10, CORE-19)."""

    __tablename__ = "entoles"

    id_entolis: Mapped[str] = mapped_column(String(50), primary_key=True)
    id_xristi: Mapped[str] = mapped_column(
        String(50), ForeignKey("xristes.id_xristi"), nullable=False
    )
    rolos: Mapped[str] = mapped_column(String(50), nullable=False)
    yposystima: Mapped[str] = mapped_column(String(50), nullable=False)
    drasi: Mapped[str] = mapped_column(String(100), nullable=False)
    katastasi: Mapped[str] = mapped_column(String(50), default="protathike")
    id_aitimatos_monadikotitas: Mapped[Optional[str]] = mapped_column(
        String(100), unique=True, nullable=True
    )
    id_proepiskopisis: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    anamenomeni_ekdosi: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    dedomena_aitimatos: Mapped[dict] = mapped_column(JSON, default=dict)
    apotelesma: Mapped[dict] = mapped_column(JSON, default=dict)
    xronos_ektelesis: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    symvanta: Mapped[list["SymvanEntolis"]] = relationship(
        "SymvanEntolis", back_populates="entoli", cascade="all, delete-orphan"
    )


class SymvanEntolis(VasiMontelwn):
    """Συμβάν μετάβασης κατάστασης εντολής."""

    __tablename__ = "symvanta_entolwn"

    id_symvantos: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_entolis: Mapped[str] = mapped_column(
        String(50), ForeignKey("entoles.id_entolis"), nullable=False
    )
    proigoumeni_katastasi: Mapped[str] = mapped_column(String(50), nullable=False)
    nea_katastasi: Mapped[str] = mapped_column(String(50), nullable=False)
    minyma: Mapped[str] = mapped_column(String(255), nullable=False)
    xronos_symvantos: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    entoli: Mapped["Entoli"] = relationship("Entoli", back_populates="symvanta")


class EktelesiSenariou(VasiMontelwn, XronosStigmaMixin):
    """Εκτέλεση σεναρίου προσομοίωσης (π.χ. καταιγίδα σκόνης)."""

    __tablename__ = "ekteleseis_senariwn"

    id_senariou: Mapped[str] = mapped_column(String(50), primary_key=True)
    onoma: Mapped[str] = mapped_column(String(100), nullable=False)
    perigrafi: Mapped[str] = mapped_column(Text, nullable=False)
    energo: Mapped[bool] = mapped_column(Boolean, default=False)
    parametroi: Mapped[dict] = mapped_column(JSON, default=dict)

    apofaseis: Mapped[list["Apofasi"]] = relationship(
        "Apofasi", back_populates="senario", cascade="all, delete-orphan"
    )
    stigmiotypa: Mapped[list["StigmiotypoSenariou"]] = relationship(
        "StigmiotypoSenariou", back_populates="senario", cascade="all, delete-orphan"
    )


class StigmiotypoSenariou(VasiMontelwn, XronosStigmaMixin):
    """Στιγμιότυπο κατάστασης κατά την εξέλιξη σεναρίου."""

    __tablename__ = "stigmiotypa_senariwn"

    id_stigmiotypou: Mapped[str] = mapped_column(String(50), primary_key=True)
    id_senariou: Mapped[str] = mapped_column(
        String(50), ForeignKey("ekteleseis_senariwn.id_senariou"), nullable=False
    )
    titlos: Mapped[str] = mapped_column(String(100), nullable=False)
    dedomena_snapshot: Mapped[dict] = mapped_column(JSON, default=dict)
    xronos_stigmiotypou: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    senario: Mapped["EktelesiSenariou"] = relationship(
        "EktelesiSenariou", back_populates="stigmiotypa"
    )


class Apofasi(VasiMontelwn, XronosStigmaMixin):
    """Απόφαση αντιμετώπισης συμβάντος ή σεναρίου (STORM-06, STORM-08)."""

    __tablename__ = "apofaseis"

    id_apofasis: Mapped[str] = mapped_column(String(50), primary_key=True)
    id_senariou: Mapped[str] = mapped_column(
        String(50), ForeignKey("ekteleseis_senariwn.id_senariou"), nullable=False
    )
    id_syntonisti: Mapped[str] = mapped_column(
        String(50), ForeignKey("xristes.id_xristi"), nullable=False
    )
    epilogi: Mapped[str] = mapped_column(String(100), nullable=False)
    aitiologia: Mapped[str] = mapped_column(Text, nullable=False)
    egkekrimeni: Mapped[bool] = mapped_column(Boolean, default=True)
    katastasi_prin: Mapped[dict] = mapped_column(JSON, default=dict)
    katastasi_meta: Mapped[dict] = mapped_column(JSON, default=dict)
    xronos_apofasis: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    senario: Mapped["EktelesiSenariou"] = relationship(
        "EktelesiSenariou", back_populates="apofaseis"
    )


class IstorikoElegxou(VasiMontelwn):
    """Ενιαίο audit log για όλες τις κρίσιμες μεταβολές (CORE-10)."""

    __tablename__ = "istoriko_elegxou"

    id_istorikou: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_xristi: Mapped[str] = mapped_column(String(50), nullable=False)
    rolos: Mapped[str] = mapped_column(String(50), nullable=False)
    energeia: Mapped[str] = mapped_column(String(100), nullable=False)
    ontotita: Mapped[str] = mapped_column(String(50), nullable=False)
    id_ontotitas: Mapped[str] = mapped_column(String(50), nullable=False)
    palia_timi: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    nea_timi: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    aitiologia: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    id_aitimatos: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    xronos_katagrafis: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class KatastasiProsomoiwsis(VasiMontelwn, XronosStigmaMixin):
    """Κατάσταση του ελεγχόμενου προσομοιωμένου ρολογιού (CORE-13)."""

    __tablename__ = "katastasi_prosomoiwsis"

    id_katastasis: Mapped[int] = mapped_column(Integer, primary_key=True)
    simerino_vima: Mapped[int] = mapped_column(Integer, default=0)
    xronos_prosomoiwsis: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    active_scenario: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    seed: Mapped[int] = mapped_column(Integer, default=42)
    einai_se_pausi: Mapped[bool] = mapped_column(Boolean, default=False)
