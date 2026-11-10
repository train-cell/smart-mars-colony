"""Συμβόλαια πόρων: μόνιμη προεπισκόπηση, επιβεβαίωση και χρονική εκτέλεση."""

from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Header
from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, FiniteFloat
from sqlalchemy.orm import Session

from backend.app.apothikes.apothiki_porwn import ApothikiPorwn
from backend.app.montela.poroi import ProgrammaAnakyklwsis, ProgrammaFwtismou
from backend.app.pyrinas.asfaleia import (
    DedomenaXristi,
    RolosXristi,
    apaitisi_rolou,
    pare_trexonta_xristi,
)
from backend.app.sxhmata.apantiseis import MetrisiApantisi
from backend.app.sxhmata.koina import ApantisiSfalmatosSxhma
from backend.app.vasi.synthesi import pare_synedria_vasis
from backend.app.ypiresies.ypiresia_porwn import YpiresiaPorwn

dromologitis = APIRouter(
    tags=["Πόροι και Ενέργεια"],
    responses={
        kleidi: {"model": ApantisiSfalmatosSxhma} for kleidi in (400, 401, 403, 404, 409, 422, 503)
    },
)
SYNEDRIA = Annotated[Session, Depends(pare_synedria_vasis)]
XEIRISTIS = Annotated[DedomenaXristi, Depends(pare_trexonta_xristi)]
SYNTONISTIS = Annotated[DedomenaXristi, Depends(apaitisi_rolou(RolosXristi.SYNTONISTIS_APOIKIAS))]
KLEIDI = Annotated[str | None, Header(alias="Idempotency-Key", max_length=100)]


class VasiAitimatos(BaseModel):
    """Αυστηρή είσοδος: δεν αγνοούνται άγνωστα πεδία ή μη πεπερασμένοι αριθμοί."""

    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)


class AitimaProepiskopisisArdefsis(VasiAitimatos):
    id_zwnis: str
    posotita_nerou_l: FiniteFloat = Field(gt=0, le=100000)
    diarkeia_lepta: int = Field(default=30, gt=0, le=1440)
    xronos_enarksis: AwareDatetime | None = None
    id_dexamenis: str | None = None


class AitimaDimiourgiasArdefsis(VasiAitimatos):
    id_proepiskopisis: str = Field(min_length=1, max_length=100)


class AitimaProepiskopisisFwtismou(VasiAitimatos):
    id_zwnis: str
    isxys_kw: FiniteFloat = Field(default=2, gt=0, le=100)
    diarkeia_wres: FiniteFloat = Field(default=4, gt=0, le=24)
    xronos_enarksis: AwareDatetime | None = None


class AitimaProepiskopisisAnakyklwsis(VasiAitimatos):
    posotita_nerou_l: FiniteFloat = Field(gt=0, le=100000)
    apodosi: FiniteFloat = Field(default=0.85, gt=0, le=1)
    diarkeia_lepta: int = Field(default=60, gt=0, le=1440)
    xronos_enarksis: AwareDatetime | None = None
    id_dexamenis_pigis: str | None = None
    id_dexamenis: str = "dexameni_01"
    isxys_kw: FiniteFloat = Field(default=0.5, gt=0, le=100)


class AitimaEpivevaiwsisAnakyklwsis(AitimaDimiourgiasArdefsis):
    id_dexamenis: str = "dexameni_01"


class AitimaPeriorismouFortiwn(VasiAitimatos):
    pausi_anavlhtwn: bool = True
    aitiologia: str = Field(min_length=5, max_length=1000)


class VasiApantisis(BaseModel):
    model_config = ConfigDict(from_attributes=True, allow_inf_nan=False)


class ThermokipioApantisi(VasiApantisis):
    id_thermokipiou: str
    onoma: str
    thermokrasia_k: float
    ygrasia_aera: float
    ekdosi_katastasis: int
    diathesimi_ardefsi: bool
    diathesimos_fwtismos: bool


class ZwniApantisi(VasiApantisis):
    id_zwnis: str
    id_thermokipiou: str
    onoma_zwnis: str
    fyto: str
    ygrasia_ypostrwmatos: float
    epithymiti_ygrasia: float
    katastasi_fwtismou: str


class StoixeiaProepiskopisis(VasiApantisis):
    id_proepiskopisis: str
    xronos_dimiourgias: datetime
    xronos_liksis_proepiskopisis: datetime
    apaiteitai_epivevaiwsi: bool


class ProepiskopisiArdefsisApantisi(StoixeiaProepiskopisis):
    id_thermokipiou: str
    id_zwnis: str
    id_dexamenis: str
    posotita_nerou_l: float
    diarkeia_lepta: int
    xronos_enarksis: datetime
    xronos_liksis: datetime
    stathmi_prin_l: float
    stathmi_meta_l: float
    diathesimo_l: float
    ygrasia_prin: float
    ygrasia_meta_ektimwmeni: float
    eparkis_stathmi: bool
    isxys_antlias_kw: float


class ProgrammatismosApantisi(VasiApantisis):
    id_programmatos: str
    id_entolis: str
    katastasi: str
    minyma: str


class ArdefsiApantisi(ProgrammatismosApantisi):
    nea_stathmi_dexamenis_l: float
    desmevmeno_nero_l: float


class AkyrosiApantisi(VasiApantisis):
    id_programmatos: str
    katastasi: str
    epistrafen_nero_l: float
    minyma: str


class ProgrammaArdefsisApantisi(VasiApantisis):
    id_programmatos: str
    id_thermokipiou: str
    id_zwnis: str
    id_dexamenis: str
    posotita_nerou_l: float
    xronos_enarksis: datetime
    diarkeia_lepta: int
    katastasi: str
    ektelestheisa_posotita_l: float
    id_entolis: str | None


class ProepiskopisiFwtismouApantisi(StoixeiaProepiskopisis):
    id_thermokipiou: str
    id_zwnis: str
    isxys_kw: float
    diarkeia_wres: float
    xronos_enarksis: datetime
    xronos_liksis: datetime
    synoliki_energeia_kwh: float
    proeidopoiiseis: list[str]


class FwtismosApantisi(ProgrammatismosApantisi):
    isxys_kw: float
    xronos_liksis: datetime


class ProgrammaFwtismouApantisi(VasiApantisis):
    id_programmatos: str
    id_thermokipiou: str
    id_zwnis: str
    isxys_kw: float
    xronos_enarksis: datetime
    xronos_liksis: datetime
    katastasi: str
    ektelestheisa_energeia_kwh: float
    id_entolis: str | None


class ProepiskopisiAnakyklwsisApantisi(StoixeiaProepiskopisis):
    id_dexamenis_pigis: str
    id_dexamenis: str
    posotita_akarthartou_l: float
    apodosi_anakyklwsis: float
    epistrefomeno_nero_l: float
    apwleia_l: float
    diarkeia_lepta: int
    xronos_enarksis: datetime
    xronos_liksis: datetime
    isxys_kw: float
    energeia_kwh: float


class AnakyklwsiApantisi(ProgrammatismosApantisi):
    posotita_anakyklwsis_l: float


class ProgrammaAnakyklwsisApantisi(VasiApantisis):
    id_programmatos: str
    id_dexamenis: str
    id_dexamenis_pigis: str | None
    posotita_eisodou_l: float
    posotita_anakyklwsis_l: float
    apodosi_anakyklwsis: float
    apwleia_l: float
    xronos_enarksis: datetime
    diarkeia_lepta: int
    katastasi: str
    isxys_kw: float
    ektelestheisa_posotita_l: float
    id_entolis: str | None


class DexameniApantisi(VasiApantisis):
    id_dexamenis: str
    onoma: str
    typos_nerou: str
    xwritikotita_l: float
    trexwn_ogkos_l: float
    efedreia_asfaleias_l: float
    desmevmeno_l: float
    diathesimo_panw_apo_efedreia_l: float
    ekdosi_katastasis: int
    rythmos_diarrois_l_h: float


class SynolaNerou(VasiApantisis):
    xwritikotita_l: float
    trexwn_ogkos_l: float
    efedreia_l: float
    desmevmeno_l: float
    diathesimo_xrisimo_l: float


class RoiApantisi(VasiApantisis):
    id_rois: int
    id_dexamenis: str
    typos: str
    rythmos_l_h: float
    perigrafi: str | None
    xronos: datetime
    xronos_enarksis: datetime | None
    xronos_liksis: datetime | None
    energi: bool
    id_programmatos: str | None


class NeroApantisi(VasiApantisis):
    dexamenes: list[DexameniApantisi]
    synolika: SynolaNerou
    roes: list[RoiApantisi]


class SynolikesRoes(VasiApantisis):
    synolikes_eisroes: float
    synolikes_ekroes: float
    katharos_rythmos: float


class IsozygioNerouApantisi(VasiApantisis):
    apothema: SynolaNerou
    roes_l_h: SynolikesRoes
    provlepsi_24h_l: float
    paradoxes: list[str]


class FwtovoltaikoApantisi(VasiApantisis):
    id_fwtovoltaikou: str
    onoma: str
    epifaneia_m2: float
    apodosi_eta: float
    syntelestis_skonis: float
    aktinovolia_w_m2: float
    isxys_w: float
    poiotita: str = "agnwsti"
    xronos_metrisis: datetime | None = None
    pigi: str = "prosomoiwsi_modelou"
    metriseis: dict[str, MetrisiApantisi | None] = Field(default_factory=dict)


class ParagwgiApantisi(VasiApantisis):
    synoliki_isxys_w: float
    synoliki_isxys_kw: float
    fwtovoltaika: list[FwtovoltaikoApantisi]


class FortioApantisi(VasiApantisis):
    id_fortiou: str
    onoma: str
    egkatastasi: str
    isxys_kw: float
    einai_krisimo: bool
    einai_anavlito: bool
    energo: bool
    proteraiotita: int


class SynolikaFortia(VasiApantisis):
    krisima_kw: float
    anavlita_kw: float
    synolika_fortia_kw: float


class SyssoreftisApantisi(VasiApantisis):
    id_syssorefti: str
    onoma: str
    xwritikotita_kwh: float
    energeia_kwh: float
    efedreia_kwh: float
    pososto_fortisis: float
    katastasi: str


class SysswrefsiApantisi(VasiApantisis):
    energeia_kwh: float
    syssoreftes: list[SyssoreftisApantisi]


class IlektrikoIsozygio(VasiApantisis):
    elleimma_kw: float
    autonomia_wres: float | None
    katastasi: str


class EnergeiaApantisi(VasiApantisis):
    paragwgi: ParagwgiApantisi
    fortia: SynolikaFortia
    sysswrefsi: SysswrefsiApantisi
    isozygio: IlektrikoIsozygio


class KatastasiPeriorismou(VasiApantisis):
    fortia_kw: float
    elleimma_kw: float
    autonomia_wres: float | None


class OfelosPeriorismou(VasiApantisis):
    meiwsi_isxyos_kw: float
    kerdos_autonomias_wres: float | None
    kerdos_autonomias_lepta: float | None


class ProepiskopisiPeriorismouApantisi(StoixeiaProepiskopisis):
    pausi_anavlhtwn: bool
    aitiologia: str
    katastasi_prin: KatastasiPeriorismou
    katastasi_meta: KatastasiPeriorismou
    ofelos: OfelosPeriorismou
    apaiteitai_egkrisi_syntonisti: bool
    epiptwseis: list[str]


class PeriorismosApantisi(VasiApantisis):
    aitiologia: str
    id_entolis: str
    pausi_anavlhtwn: bool
    arithmos_fortiwn_pou_allaksan: int
    minyma: str


@dromologitis.get("/thermokipia", response_model=list[ThermokipioApantisi])
def pare_thermokipia(synedria: SYNEDRIA):
    return YpiresiaPorwn(synedria).pare_thermokipia()


@dromologitis.get("/thermokipia/{id_thermokipiou}/zwnes", response_model=list[ZwniApantisi])
def pare_zwnes_thermokipiou(id_thermokipiou: str, synedria: SYNEDRIA):
    return YpiresiaPorwn(synedria).pare_zwnes(id_thermokipiou)


@dromologitis.post(
    "/thermokipia/{id_thermokipiou}/ardefsi/proepiskopisi",
    response_model=ProepiskopisiArdefsisApantisi,
)
def proepiskopisi_ardefsis(
    id_thermokipiou: str,
    aitima: AitimaProepiskopisisArdefsis,
    synedria: SYNEDRIA,
    xristis: XEIRISTIS,
):
    return YpiresiaPorwn(synedria).proepiskopisi_ardefsis(
        id_thermokipiou=id_thermokipiou, xristis=xristis, **aitima.model_dump()
    )


@dromologitis.post(
    "/thermokipia/{id_thermokipiou}/ardefsi/programmata", response_model=ArdefsiApantisi
)
def dimiourgia_programmatos_ardefsis(
    id_thermokipiou: str,
    aitima: AitimaDimiourgiasArdefsis,
    synedria: SYNEDRIA,
    xristis: XEIRISTIS,
    kleidi: KLEIDI = None,
):
    return YpiresiaPorwn(synedria).dimiourgia_programmatos_ardefsis(
        aitima.id_proepiskopisis, xristis, kleidi, id_thermokipiou
    )


@dromologitis.get(
    "/thermokipia/{id_thermokipiou}/ardefsi/programmata",
    response_model=list[ProgrammaArdefsisApantisi],
)
def pare_programmata_ardefsis(id_thermokipiou: str, synedria: SYNEDRIA):
    YpiresiaPorwn(synedria)._th(id_thermokipiou)
    return ApothikiPorwn(synedria).pare_programmata_ardefsis(id_thermokipiou)


@dromologitis.post("/ardefsi/programmata/{id_programmatos}/akyrosi", response_model=AkyrosiApantisi)
def akyrosi_ardefsis(id_programmatos: str, synedria: SYNEDRIA, xristis: XEIRISTIS):
    return YpiresiaPorwn(synedria).akyrosi_programmatos_ardefsis(id_programmatos, xristis)


@dromologitis.post(
    "/thermokipia/{id_thermokipiou}/fwtismos/proepiskopisi",
    response_model=ProepiskopisiFwtismouApantisi,
)
def proepiskopisi_fwtismou(
    id_thermokipiou: str,
    aitima: AitimaProepiskopisisFwtismou,
    synedria: SYNEDRIA,
    xristis: XEIRISTIS,
):
    return YpiresiaPorwn(synedria).proepiskopisi_fwtismou(
        id_thermokipiou=id_thermokipiou, xristis=xristis, **aitima.model_dump()
    )


@dromologitis.post(
    "/thermokipia/{id_thermokipiou}/fwtismos/entoles", response_model=FwtismosApantisi
)
def dimiourgia_programmatos_fwtismou(
    id_thermokipiou: str,
    aitima: AitimaDimiourgiasArdefsis,
    synedria: SYNEDRIA,
    xristis: XEIRISTIS,
    kleidi: KLEIDI = None,
):
    return YpiresiaPorwn(synedria).dimiourgia_programmatos_fwtismou(
        id_thermokipiou, aitima.id_proepiskopisis, xristis, kleidi
    )


@dromologitis.get(
    "/thermokipia/{id_thermokipiou}/fwtismos/programmata",
    response_model=list[ProgrammaFwtismouApantisi],
)
def pare_programmata_fwtismou(id_thermokipiou: str, synedria: SYNEDRIA):
    YpiresiaPorwn(synedria)._th(id_thermokipiou)
    return ApothikiPorwn(synedria).pare_programmata_fwtismou(id_thermokipiou)


@dromologitis.post(
    "/thermokipia/{id_thermokipiou}/fwtismos/programmata/{id_programmatos}/akyrosi",
    response_model=AkyrosiApantisi,
)
def akyrosi_fwtismou(
    id_thermokipiou: str, id_programmatos: str, synedria: SYNEDRIA, xristis: XEIRISTIS
):
    return YpiresiaPorwn(synedria).akyrosi_programmatos(
        ProgrammaFwtismou, id_programmatos, xristis, id_thermokipiou
    )


@dromologitis.get("/nero/dexamenes", response_model=NeroApantisi)
def pare_dexamenes_nerou(synedria: SYNEDRIA):
    return YpiresiaPorwn(synedria).pare_katastasi_nerou()


@dromologitis.get("/nero/isozygio", response_model=IsozygioNerouApantisi)
def pare_isozygio_nerou(synedria: SYNEDRIA):
    return YpiresiaPorwn(synedria).pare_isozygio_nerou()


@dromologitis.get("/nero/roes", response_model=list[RoiApantisi])
def pare_roes_nerou(synedria: SYNEDRIA):
    return YpiresiaPorwn(synedria).pare_katastasi_nerou()["roes"]


@dromologitis.post(
    "/nero/anakyklwsi/proepiskopisi", response_model=ProepiskopisiAnakyklwsisApantisi
)
def proepiskopisi_anakyklwsis(
    aitima: AitimaProepiskopisisAnakyklwsis, synedria: SYNEDRIA, xristis: XEIRISTIS
):
    return YpiresiaPorwn(synedria).proepiskopisi_anakyklwsis(xristis=xristis, **aitima.model_dump())


@dromologitis.post("/nero/anakyklwsi/programmata", response_model=AnakyklwsiApantisi)
@dromologitis.post("/nero/anakyklwsi/entoles", response_model=AnakyklwsiApantisi)
def dimiourgia_programmatos_anakyklwsis(
    aitima: AitimaEpivevaiwsisAnakyklwsis,
    synedria: SYNEDRIA,
    xristis: XEIRISTIS,
    kleidi: KLEIDI = None,
):
    return YpiresiaPorwn(synedria).dimiourgia_programmatos_anakyklwsis(
        aitima.id_proepiskopisis, xristis, kleidi, aitima.id_dexamenis
    )


@dromologitis.get("/nero/anakyklwsi/programmata", response_model=list[ProgrammaAnakyklwsisApantisi])
def pare_programmata_anakyklwsis(synedria: SYNEDRIA):
    return ApothikiPorwn(synedria).pare_programmata_anakyklwsis()


@dromologitis.post(
    "/nero/anakyklwsi/programmata/{id_programmatos}/akyrosi", response_model=AkyrosiApantisi
)
def akyrosi_anakyklwsis(id_programmatos: str, synedria: SYNEDRIA, xristis: XEIRISTIS):
    return YpiresiaPorwn(synedria).akyrosi_programmatos(
        ProgrammaAnakyklwsis, id_programmatos, xristis
    )


@dromologitis.get("/energeia/katastasi", response_model=EnergeiaApantisi)
def pare_katastasi_energeias(synedria: SYNEDRIA):
    return YpiresiaPorwn(synedria).pare_katastasi_energeias()


@dromologitis.get("/energeia/fortia", response_model=list[FortioApantisi])
def pare_energeiaka_fortia(synedria: SYNEDRIA):
    return YpiresiaPorwn(synedria).pare_analytika_fortia()


@dromologitis.get("/energeia/fwtovoltaika", response_model=list[FwtovoltaikoApantisi])
def pare_fwtovoltaika(synedria: SYNEDRIA):
    return YpiresiaPorwn(synedria).pare_katastasi_energeias()["paragwgi"]["fwtovoltaika"]


@dromologitis.get("/energeia/syssoreftes", response_model=list[SyssoreftisApantisi])
def pare_syssoreftes(synedria: SYNEDRIA):
    return YpiresiaPorwn(synedria).pare_katastasi_energeias()["sysswrefsi"]["syssoreftes"]


@dromologitis.post(
    "/energeia/periorismos-fortiwn/proepiskopisi", response_model=ProepiskopisiPeriorismouApantisi
)
def proepiskopisi_periorismou_fortiwn(
    aitima: AitimaPeriorismouFortiwn, synedria: SYNEDRIA, xristis: XEIRISTIS
):
    return YpiresiaPorwn(synedria).proepiskopisi_periorismou_fortiwn(
        xristis=xristis, **aitima.model_dump()
    )


@dromologitis.post("/energeia/periorismos-fortiwn/entoles", response_model=PeriorismosApantisi)
def ektelesi_periorismou_fortiwn(
    aitima: AitimaDimiourgiasArdefsis,
    synedria: SYNEDRIA,
    xristis: SYNTONISTIS,
    kleidi: KLEIDI = None,
):
    return YpiresiaPorwn(synedria).ektelesi_periorismou_fortiwn(
        xristis=xristis, id_proepiskopisis=aitima.id_proepiskopisis, kleidi=kleidi
    )


class IstorikoPorwnApantisi(BaseModel):
    """Καταγεγραμμένο στιγμιότυπο πραγματικών πόρων και ισοζυγίων ανά βήμα."""

    id_stigmiotypou: str
    xronos: datetime
    id_senariou: str
    energeia: EnergeiaApantisi
    nero: NeroApantisi
    logistiki: dict[str, float | int]
    fortia_egkatastasewn: list[FortioApantisi] = []


@dromologitis.get(
    "/energeia/istoriko",
    response_model=list[IstorikoPorwnApantisi],
    summary="Χρονοσειρά ισχύος, αποθήκευσης και υδατικών ισοζυγίων",
)
@dromologitis.get(
    "/nero/istoriko",
    response_model=list[IstorikoPorwnApantisi],
    summary="Χρονοσειρά στάθμης, ανακύκλωσης και διαρροών",
)
def istoriko_porwn(synedria: SYNEDRIA):
    from sqlalchemy import select

    from backend.app.montela import StigmiotypoSenariou

    apantisi = []
    for stigmiotypo in synedria.scalars(
        select(StigmiotypoSenariou)
        .order_by(StigmiotypoSenariou.xronos_stigmiotypou.desc())
        .limit(100)
    ):
        poroi = stigmiotypo.dedomena_stigmiotypou.get("poroi")
        if poroi:
            apantisi.append(
                {
                    "id_stigmiotypou": stigmiotypo.id_stigmiotypou,
                    "xronos": stigmiotypo.xronos_stigmiotypou,
                    "id_senariou": stigmiotypo.id_senariou,
                    **poroi,
                }
            )
    return apantisi
