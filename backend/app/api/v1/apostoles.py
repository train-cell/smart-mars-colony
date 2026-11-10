"""Συμβόλαια τηλεμετρίας, σχεδίων διαδρομής και επιβεβαιωμένων εντολών rover."""

from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Header
from pydantic import BaseModel, ConfigDict, Field, FiniteFloat
from sqlalchemy.orm import Session

from backend.app.pyrinas.asfaleia import DedomenaXristi, RolosXristi, apaitisi_rolou
from backend.app.vasi.synthesi import pare_synedria_vasis
from backend.app.ypiresies.ypiresia_apostolwn import YpiresiaApostolwn

dromologitis = APIRouter(tags=["Αποστολές & Rover (Υποσύστημα Γ)"])


class VasikoSxhmaOximatos(BaseModel):
    """Αυστηρό σχήμα αιτήματος με πεπερασμένες φυσικές ποσότητες."""

    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)


class ShmeioSxediou(VasikoSxhmaOximatos):
    syntetagmeni_x: FiniteFloat = 0
    syntetagmeni_y: FiniteFloat = 0
    apostasi_apo_proigoumeno_m: FiniteFloat = Field(gt=0, le=100_000)
    klisi_rad: FiniteFloat = Field(default=0, ge=-1.0471975511965976, le=1.0471975511965976)


class AitimaDimiourgiasApostolis(VasikoSxhmaOximatos):
    titlos: str = Field(min_length=1, max_length=100)
    skopos: str = Field(min_length=1, max_length=5000)
    apostasi_km: FiniteFloat = Field(gt=0, le=100)
    ektimwmeni_diarkeia_wres: FiniteFloat = Field(gt=0, le=72, default=1)
    maza_fortiou_kg: FiniteFloat = Field(ge=0, le=1000, default=0)
    plithos_plirwmatos: int = Field(ge=0, le=6, default=0)
    shmeia_diadromis: list[ShmeioSxediou] = Field(default_factory=list, max_length=100)


class AitimaEpivevaiwsisOximatos(VasikoSxhmaOximatos):
    id_proepiskopisis: str = Field(min_length=1, max_length=50)


class ApantisiEntolisOximatos(BaseModel):
    id_entolis: str
    id_oximatos: str
    id_apostolis: str | None = None
    katastasi_entolis: str | None = None
    katastasi_oximatos: str | None = None
    katastasi: str | None = None
    minyma: str


class ApantisiAnavolis(BaseModel):
    id_apostolis: str
    id_oximatos: str
    katastasi: str
    id_entolis: str
    minyma: str


class TilemetriaOximatos(BaseModel):
    xwritikotita_energeias_kwh: float
    isxys_fortisis_kw: float
    id_oximatos: str
    onoma: str
    maza_kg: float
    maza_fortiou_kg: float
    plithos_plirwmatos: int
    syntetagmeni_x: float
    syntetagmeni_y: float
    apostasi_apo_vasi_km: float
    taxytita_kmh: float
    energeia_kwh: float
    efedreia_kwh: float
    mesi_isxys_kw: float
    isxys_kinisis_kw: float
    voithitiki_isxys_w: float
    katastasi_oximatos: str
    katastasi_epikoinwnias: str
    kathysterisi_epikoinwnias_s: float
    katastasi_plirwmatos: str
    ekdosi_katastasis: int
    eidos: str
    pigi: str
    xronos_metrisis: datetime
    poiotita: str
    avevaiotita: str | None


class KatastasiKinisis(BaseModel):
    apostasi_km: float
    taxytita_kmh: float
    katastasi: str


class KatastasiEnergeiasOximatos(BaseModel):
    trexousa_kwh: float
    efedreia_kwh: float
    diathesimi_panw_apo_efedreia_kwh: float
    mesi_isxys_kw: float
    isxys_kinisis_kw: float


class KatastasiEpikoinwniasOximatos(BaseModel):
    katastasi: str
    kathysterisi_s: float


class ShmeioApantisis(ShmeioSxediou):
    seira: int


class ApostoliApantisi(BaseModel):
    id_apostolis: str
    titlos: str
    skopos: str
    katastasi: str
    apostasi_km: float
    ektimwmeni_diarkeia_wres: float
    apaitoumeni_energeia_kwh: float
    energeia_katanalwtheisa_kwh: float
    maza_fortiou_kg: float
    plithos_plirwmatos: int
    xronos_enarksis: datetime
    xronos_oloklirwsis: datetime | None
    shmeia_diadromis: list[ShmeioApantisis]


class KatastasiOximatos(TilemetriaOximatos):
    kinisi: KatastasiKinisis
    energeia: KatastasiEnergeiasOximatos
    epikoinwnia: KatastasiEpikoinwniasOximatos
    apostoles: list[ApostoliApantisi]


class KindynosApantisi(BaseModel):
    id_kindynou: str
    typos: str
    oratotita_m: float
    epipedo_aktinovolias: float
    monada_aktinovolias: str
    sovarotita: str
    eidos_dedomenwn: str
    pigi: str
    apolyti_avevaiotita: float | None
    energi: bool
    perigrafi: str
    xronos: datetime


class PerivallonOximatos(BaseModel):
    poiotita: str
    oratotita_m: float | None
    aktinovolia_msv_h: float | None
    proskrousi: bool
    id_kindynwn: list[str]


class ProepiskopisiAnaklisis(BaseModel):
    id_proepiskopisis: str
    xronos_dimiourgias: datetime
    xronos_liksis_proepiskopisis: datetime
    id_oximatos: str
    onoma_oximatos: str
    ekdosi_katastasis: int
    apostasi_km: float
    taxytita_kmh: float
    xronos_epistrofis_wres: float
    xronos_epistrofis_lepta: float
    apaitoumeni_energeia_kwh: float
    energeia_meta_epistrofi_kwh: float
    energeiaka_efikto: bool
    oratotita_asfalis: bool
    epikoinwnia_asfalis: bool
    synolika_asfalis_epistrofi: bool
    aktinovolia_asfalis: bool
    proskrousi_asfalis: bool
    diadromi_asfalis: bool
    katastasi_epikoinwnias: str
    kathysterisi_epikoinwnias_s: float
    perivallon: PerivallonOximatos
    paradoxes: list[str]
    id_montelou: str
    eidos: str
    xronos_metrisis: datetime
    proeidopoiiseis: list[str]
    apaiteitai_epivevaiwsi: bool


class EpiptwseisStasis(BaseModel):
    kinisi: str
    energeia: str
    asfaleia: str
    apostoli: str


class ProepiskopisiStasis(BaseModel):
    id_proepiskopisis: str
    xronos_dimiourgias: datetime
    xronos_liksis_proepiskopisis: datetime
    id_oximatos: str
    onoma: str
    trexousa_katastasi: str
    protinomeni_drasi: str
    ekdosi_katastasis: int
    katastasi_epikoinwnias: str
    kathysterisi_epikoinwnias_s: float
    epiptwseis: EpiptwseisStasis
    proeidopoiiseis: list[str]
    apaiteitai_epivevaiwsi: bool


class TmimaProsomoiwsis(BaseModel):
    enarksi_wres: float
    liksi_wres: float
    energeia_kwh: float
    x_arxi_m: float
    y_arxi_m: float
    x_telos_m: float
    y_telos_m: float
    apostasi_arxi_m: float
    apostasi_telos_m: float


class ProepiskopisiSxediou(BaseModel):
    id_proepiskopisis: str
    xronos_dimiourgias: datetime
    xronos_liksis_proepiskopisis: datetime
    id_oximatos: str
    zitoumeni: AitimaDimiourgiasApostolis
    tmimata_prosomoiwsis: list[TmimaProsomoiwsis]
    apostasi_km: float
    synoliki_diadromi_km: float
    xronos_kinisis_wres: float
    ektimwmeni_diarkeia_wres: float
    ektimwmeni_energeia_kwh: float
    diathesimi_energeia_oximatos_kwh: float
    energeia_meta_epistrofi_kwh: float
    energeiaka_efikto: bool
    diadromi_asfalis: bool
    epikoinwnia_asfalis: bool
    paradoxes: list[str]
    id_montelou: str
    apaiteitai_epivevaiwsi: bool
    proeidopoiiseis: list[str]


Synedria = Annotated[Session, Depends(pare_synedria_vasis)]
Xeiristis = Annotated[
    DedomenaXristi,
    Depends(apaitisi_rolou(RolosXristi.YPEFTHYNOS_APOSTOLWN, RolosXristi.SYNTONISTIS_APOIKIAS)),
]
Kleidi = Annotated[str | None, Header(alias="Idempotency-Key", max_length=100)]


@dromologitis.get(
    "/kindynoi",
    response_model=list[KindynosApantisi],
    summary="Μετρήσεις και προβλέψεις εξωτερικών κινδύνων",
)
def pare_kindynous(synedria: Synedria):
    return YpiresiaApostolwn(synedria).pare_kindynous()


@dromologitis.get(
    "/oximata",
    response_model=list[TilemetriaOximatos],
    summary="Τηλεμετρία οχημάτων, επικοινωνία και πλήρωμα",
)
def pare_oximata(synedria: Synedria):
    return YpiresiaApostolwn(synedria).pare_oximata()


@dromologitis.get(
    "/oximata/{id_oximatos}/apostoles",
    response_model=KatastasiOximatos,
    summary="Κατάσταση οχήματος και αποθηκευμένες διαδρομές",
)
def pare_apostoles_oximatos(id_oximatos: str, synedria: Synedria):
    return YpiresiaApostolwn(synedria).pare_katastasi_oximatos(id_oximatos)


@dromologitis.post(
    "/oximata/{id_oximatos}/apostoles/proepiskopisi",
    response_model=ProepiskopisiSxediou,
    summary="Προεπισκόπηση πλήρους ενεργειακού κόστους αποστολής",
)
def proepiskopisi_apostolis(
    id_oximatos: str, aitima: AitimaDimiourgiasApostolis, synedria: Synedria, xristis: Xeiristis
):
    apantisi = YpiresiaApostolwn(synedria).proepiskopisi_apostolis(
        id_oximatos, aitima.model_dump(mode="json"), xristis
    )
    synedria.commit()
    return apantisi


@dromologitis.post(
    "/oximata/{id_oximatos}/apostoles",
    response_model=ApantisiEntolisOximatos,
    response_model_exclude_none=True,
    summary="Επιβεβαίωση προεπισκόπησης σχεδίου αποστολής",
)
def dimiourgia_apostolis(
    id_oximatos: str,
    aitima: AitimaEpivevaiwsisOximatos,
    synedria: Synedria,
    xristis: Xeiristis,
    kleidi: Kleidi = None,
):
    return YpiresiaApostolwn(synedria).dimiourgia_apostolis(
        id_oximatos, aitima.id_proepiskopisis, xristis, kleidi
    )


@dromologitis.post(
    "/oximata/{id_oximatos}/anaklisi/proepiskopisi",
    response_model=ProepiskopisiAnaklisis,
    summary="Ενέργεια, διαδρομή και επικοινωνία επιστροφής",
)
def proepiskopisi_anaklisis(id_oximatos: str, synedria: Synedria, xristis: Xeiristis):
    apantisi = YpiresiaApostolwn(synedria).proepiskopisi_anaklisis(id_oximatos, xristis)
    synedria.commit()
    return apantisi


@dromologitis.post(
    "/oximata/{id_oximatos}/anaklisi/entoles",
    response_model=ApantisiEntolisOximatos,
    response_model_exclude_none=True,
    summary="Επιβεβαίωση ανάκλησης με ορατή κατάσταση παραλαβής",
)
def ektelesi_anaklisis(
    id_oximatos: str,
    aitima: AitimaEpivevaiwsisOximatos,
    synedria: Synedria,
    xristis: Xeiristis,
    kleidi: Kleidi = None,
):
    return YpiresiaApostolwn(synedria).ektelesi_anaklisis(
        id_oximatos, xristis, aitima.id_proepiskopisis, kleidi
    )


@dromologitis.post(
    "/oximata/{id_oximatos}/asfalis-stasi/proepiskopisi",
    response_model=ProepiskopisiStasis,
    summary="Συνέπειες ακινητοποίησης πριν από επιβεβαίωση",
)
def proepiskopisi_asfalous_stasis(id_oximatos: str, synedria: Synedria, xristis: Xeiristis):
    apantisi = YpiresiaApostolwn(synedria).proepiskopisi_asfalous_stasis(id_oximatos, xristis)
    synedria.commit()
    return apantisi


@dromologitis.post(
    "/oximata/{id_oximatos}/asfalis-stasi/entoles",
    response_model=ApantisiEntolisOximatos,
    response_model_exclude_none=True,
    summary="Ασφαλής στάση μετά από επιβεβαιωμένη παραλαβή",
)
def ektelesi_asfalous_stasis(
    id_oximatos: str,
    aitima: AitimaEpivevaiwsisOximatos,
    synedria: Synedria,
    xristis: Xeiristis,
    kleidi: Kleidi = None,
):
    return YpiresiaApostolwn(synedria).ektelesi_asfalous_stasis(
        id_oximatos, xristis, aitima.id_proepiskopisis, kleidi
    )


@dromologitis.post(
    "/oximata/{id_oximatos}/apostoles/{id_apostolis}/anavoli",
    response_model=ApantisiAnavolis,
    summary="Αναβολή αποστολής πριν από την αναχώρηση",
)
def anavoli_apostolis(id_oximatos: str, id_apostolis: str, synedria: Synedria, xristis: Xeiristis):
    return YpiresiaApostolwn(synedria).anavoli_apostolis(id_oximatos, id_apostolis, xristis)
