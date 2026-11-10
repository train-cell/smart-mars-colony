"""Δημόσια σχήματα αναγνώσεων και κοινών ροών. Τα ανοικτά δεδομένα audit δηλώνονται ρητά."""

from datetime import datetime

from pydantic import JsonValue
from typing_extensions import NotRequired, TypedDict


class EntoliOximatosKoiniApantisi(TypedDict):
    id_entolis: str
    id_oximatos: str
    id_apostolis: NotRequired[str | None]
    katastasi_entolis: NotRequired[str | None]
    katastasi_oximatos: NotRequired[str | None]
    katastasi: NotRequired[str | None]
    minyma: str


class XwrosApantisi(TypedDict):
    id_xwrou: str
    onoma: str
    plithysmos: int
    ogkos_m3: float
    epifaneia_m2: float
    epithymiti_thermokrasia_k: float
    thermokrasia_eswteriki_k: float
    thermokrasia_exwteriki_k: float
    piesi_pa: float
    pososto_oxygonou: float
    ekdosi_katastasis: int


class ThermokrasiaXwrou(TypedDict):
    eswteriki_k: float
    epithymiti_k: float
    exwteriki_k: float
    thermikes_apwleies_w: float


class AtmosfairaXwrou(TypedDict):
    synoliki_piesi_pa: float
    pososto_oxygonou: float
    meriki_piesi_oxygonou_pa: float
    pososto_dioxeidiou_anthraka: float
    meriki_piesi_dioxeidiou_anthraka_pa: float
    sxetiki_ygrasia: float


class EfedreiaOxygonou(TypedDict):
    diathesimo_kg: float
    xwritikotita_kg: float
    rythmos_paragwgis_kg_h: float


class SyskeviApantisi(TypedDict):
    id_syskevis: str
    onoma: str
    typos: str
    katastasi: str
    isxys_w: float


class KatastasiXwrouApantisi(TypedDict):
    id_xwrou: str
    onoma: str
    plithysmos: int
    ekdosi_katastasis: int
    thermokrasia: ThermokrasiaXwrou
    atmosfaira: AtmosfairaXwrou
    efedreia_oxygonou: EfedreiaOxygonou
    syskeves: list[SyskeviApantisi]


class TrofodosiaOxygonou(TypedDict):
    diarkeia_plirous_trofodosias_wres: float | None
    pososto_syskevwn_tora: float
    pososto_syskevwn_meta: float
    onomastiki_paragwgi_kg_h: float
    paragwgi_meta_kg_h: float
    poiotita_iliakis_pigis: str


class OxygonoApantisi(TypedDict):
    id_xwrou: str
    meriki_piesi_oxygonou_pa: float
    katwfli_asfaleias_pa: float
    mol_xrisimou_oxygonou: float
    maza_xrisimou_oxygonou_kg: float
    synoliki_katanalwsi_kg_h: float
    rythmos_paragwgis_kg_h: float
    autonomia_wres: float | None
    katastasi_asfaleias: str
    apothema_ekswterikis_dexamenis_kg: float
    synoliki_autonomia_me_dexameni_wres: float | None
    trofodosia: TrofodosiaOxygonou
    proeidopoiiseis: list[str]
    paradoxes: list[str]


class ProepiskopisiThermokrasiasApantisi(TypedDict):
    id_proepiskopisis: str
    xronos_dimiourgias: datetime
    xronos_liksis_proepiskopisis: datetime
    apaiteitai_epivevaiwsi: bool
    id_xwrou: str
    ekdosi_senariou: int
    trexousa: dict[str, float]
    zitoumeni: dict[str, float]
    montelo: dict[str, str]
    eisodoi: dict[str, float]
    epiptwsi: dict[str, float | None]
    paradoxes: list[str]
    proeidopoiiseis: list[str]


class EpivevaiwsiThermokrasiasApantisi(TypedDict):
    id_entolis: str
    id_xwrou: str
    katastasi: str
    epithymiti_thermokrasia_k: float
    nea_ekdosi_katastasis: int
    minyma: str


class SymvanEntolisApantisi(TypedDict):
    proigoumeni: str
    nea: str
    minyma: str
    xronos: datetime


class EntoliPlirisApantisi(TypedDict):
    id_entolis: str
    id_xristi: str
    rolos: str
    yposystima: str
    drasi: str
    katastasi: str
    id_proepiskopisis: str | None
    anamenomeni_ekdosi: int | None
    dedomena_aitimatos: dict[str, JsonValue]
    apotelesma: dict[str, JsonValue]
    xronos_ektelesis: datetime | None
    symvanta: list[SymvanEntolisApantisi]


class AkyrosiEntolisApantisi(TypedDict):
    id_entolis: str
    katastasi: str
    minyma: str


class ProepiskopisiSyskevisApantisi(TypedDict):
    id_proepiskopisis: str
    xronos_dimiourgias: datetime
    xronos_liksis_proepiskopisis: datetime
    apaiteitai_epivevaiwsi: bool
    id_xwrou: str
    id_syskevis: str
    energopoiisi: bool
    aitiologia: str
    isxys_w: float
    proeidopoiiseis: list[str]


class EpivevaiwsiSyskevisApantisi(TypedDict):
    id_entolis: str
    id_syskevis: str
    katastasi: str
    katastasi_syskevis: str
    minyma: str


class MetrisiApantisi(TypedDict):
    megethos: str
    timi: float
    monada: str
    eidos: str
    pigi: str
    xronos_metrisis: datetime
    xronos_paralavis: datetime
    poiotita: str
    avevaiotita: dict[str, float | str]
    tasi: str
    einai_palio: bool
    id_metrisis: NotRequired[int]


class AisthitirasApantisi(TypedDict):
    id_aisthitira: str
    kodikos: str
    typos_megethous: str
    yposystima: str
    id_xwrou: str | None
    monada: str
    katastasi: str
    teleftaia_metrisi: MetrisiApantisi | None


class SynagermosApantisi(TypedDict):
    id_synagermou: str
    energi_aitia: bool
    titlos: str
    perigrafi: str
    aitia: str
    epiptwsi: str
    systasi: str
    yposystima: str
    sovarotita: str
    katastasi: str
    id_xristi_anagnwrisis: str | None
    xronos_anagnwrisis: datetime | None
    id_xristi_epilysis: str | None
    xronos_epilysis: datetime | None
    sxolio_epilysis: str | None
    xronos_dimiourgias: datetime


class AnagnwrisiSynagermouApantisi(TypedDict):
    id_synagermou: str
    katastasi: str
    id_xristi_anagnwrisis: str
    minyma: str


class EpilysiSynagermouApantisi(TypedDict):
    id_synagermou: str
    katastasi: str
    id_xristi_epilysis: str
    minyma: str


class SynopsiApantisi(TypedDict):
    apoikia: str
    xronos_synopsis: datetime
    ypostiriksi_zwis: dict[str, float | int]
    energeia: dict[str, float | str | None]
    nero: dict[str, float]
    oxima_exerevnis: dict[str, float | str | None]
    energoi_synagermoi: list[dict[str, str]]


class MetavivasiApantisi(TypedDict):
    id_metavivasis: str
    id_syntonisti: str
    id_paralipti: str
    rolos: str
    pedio_efarmogis: str
    xronos_enarksis: datetime
    xronos_liksis: datetime
    energo: bool
    aitiologia: str
    xronos_anaklisis: datetime | None


class ProepiskopisiMetavivasisApantisi(TypedDict):
    id_syntonisti: str
    id_paralipti: str
    rolos_pros_metavivasi: str
    pedio_efarmogis: str
    diarkeia_wres: float
    einai_epileksimo: bool
    minyma: str


class EgkrisiMetavivasisApantisi(TypedDict):
    id_metavivasis: str
    id_paralipti: str
    rolos: str
    xronos_liksis: datetime
    minyma: str


class AnaklisiMetavivasisApantisi(TypedDict):
    id_metavivasis: str
    energo: bool
    minyma: str


class YgeiaApantisi(TypedDict):
    katastasi: str
    efarmogi: str
    ekdosi: str
    perivallon: str
    vasi_dedomenwn: str


class MetadedomenaApantisi(TypedDict):
    monades_si: dict[str, str]
    praktikes_monades: dict[str, str]
    katastaseis_entolwn: list[str]
    roloi_xristwn: list[str]


class XristisApantisi(TypedDict):
    id_xristi: str
    onoma: str
    vasikos_rolos: str
    energoi_roloi: list[str]


class EisodosApantisi(XristisApantisi):
    odigies_kefalidwn: dict[str, str]
    minyma: str


class IstorikoApantisi(TypedDict):
    id_istorikou: int
    id_xristi: str
    rolos: str
    energeia: str
    ontotita: str
    id_ontotitas: str
    palia_timi: dict[str, JsonValue] | None
    nea_timi: dict[str, JsonValue] | None
    aitiologia: str | None
    id_aitimatos: str | None
    xronos_katagrafis: datetime


class KatastasiKataigidasApantisi(TypedDict):
    senario: str
    katastasi: str
    aktinovolia_w_m2: float
    syntelestis_f: float


class EnergopoiisiSenariouApantisi(TypedDict):
    id_entolis: str
    senario: str
    katastasi: str
    paragwgi_pv_kw: float
    thermansi_kw: float
    oratotita_m: float
    minyma: str


class ProepiskopisiSenariouApantisi(TypedDict):
    id_proepiskopisis: str
    xronos_dimiourgias: datetime
    xronos_liksis_proepiskopisis: datetime
    apaiteitai_epivevaiwsi: bool
    senario: str
    statistika_senariou: dict[str, JsonValue]
    trexousa_energeia: dict[str, float | str | None]
    epiloges_apofasis: list[dict[str, str]]
    epiptwseis: dict[str, str]
    paradoxes: list[str]
    apaiteitai_egkrisi_syntonisti: bool


class ApofasiApantisi(TypedDict):
    id_entolis: str
    id_apofasis: str
    epilogi: str
    egkekrimeni: bool
    syntonistis: str
    entoli_oximatos: EntoliOximatosKoiniApantisi | None
    minyma: str


class IstorikoApofasisApantisi(TypedDict):
    id_apofasis: str
    id_syntonisti: str
    epilogi: str
    aitiologia: str
    egkekrimeni: bool
    xronos_apofasis: datetime


class VimaApantisi(TypedDict):
    id_entolis: str
    simerino_vima: int
    neos_xronos: datetime
    lepta_pou_prostethikan: int
    apotelesmata: list[dict[str, JsonValue]]


class EpanaforaApantisi(TypedDict):
    minyma: str
    katastasi: NotRequired[str]
