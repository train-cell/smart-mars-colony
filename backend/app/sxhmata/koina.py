"""Κοινά Pydantic DTOs και Enums για όλα τα υποσυστήματα.

Όλα τα πεδία και τιμές enum ακολουθούν τους κανόνες Greeklish §0A.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel, ConfigDict, Field


class EidosMetrisis(str, Enum):
    """Είδος προέλευσης της μέτρησης."""

    METRIMENO = "metrimeno"
    EKTIMIMENO = "ektimimeno"
    PROVLEPSI = "provlepsi"
    EPITHYMITI_RYTHMISI = "epithymiti_rythmisi"


class PoiotitaMetrisis(str, Enum):
    """Ποιότητα και αξιοπιστία της μέτρησης."""

    EGKYRO = "egkyro"
    YPOVATHMISMENO = "ypovathmismeno"
    PALIO = "palio"
    APOUSIA = "apousia"
    EKTOS_ORIWN = "ektos_oriwn"


class TasiMetrisis(str, Enum):
    """Τάση μεταβολής του μεγέθους."""

    AFKSOUSA = "afksousa"
    FTHINOUSA = "fthinousa"
    STATHERI = "statheri"
    AGNWSTI = "agnwsti"


class KatastasiEntolis(str, Enum):
    """Κατάσταση κύκλου ζωής εντολής."""

    PROGRAMMATISMENO = "programmatismeno"
    SE_ANAMONI = "se_anamoni"
    ANASTOLI = "anastoli"
    PROTATHIKE = "protathike"
    PROEPISKOPITHIKE = "proepiskopithike"
    EPIVEVAIWTHIKE = "epivevaiwthike"
    APESTALI = "apestali"
    EGKRITHIKE = "egkrithike"
    SE_EXELIXI = "se_exelixi"
    OLOKLIROTHIKE = "oloklirothike"
    APETYXE = "apetyxe"
    AKYROTHIKE = "akyrothike"
    AVEVAIO = "avevaio"


class SovarotitaSynagermou(str, Enum):
    """Επίπεδο σοβαρότητας συναγερμού."""

    XAMILI = "xamili"
    MESAIA = "mesaia"
    YPSILI = "ypsili"
    KRISIMI = "krisimi"


class KatastasiSynagermou(str, Enum):
    """Κατάσταση κύκλου ζωής συναγερμού."""

    ENERGOS = "energos"
    ANAGNWRISMENOS = "anagnwrismenos"
    EPILYMENOS = "epilymenos"


class AvevaiotitaSxhma(BaseModel):
    """Περιγραφή στατιστικής αβεβαιότητας μέτρησης ή πρόβλεψης."""

    apolyti_timi: float
    monada: str
    pososto: Optional[float] = None


class MetrisiAisthitiraSxhma(BaseModel):
    """Κοινό σχήμα μέτρησης αισθητήρα (συμβατό με §3.2)."""

    model_config = ConfigDict(from_attributes=True)

    megethos: str
    timi: float
    monada: str
    eidos: EidosMetrisis = EidosMetrisis.METRIMENO
    pigi: str = "prosomoiwmenos_aisthitiras"
    xronos_metrisis: datetime
    poiotita: PoiotitaMetrisis = PoiotitaMetrisis.EGKYRO
    avevaiotita: Optional[AvevaiotitaSxhma] = None
    tasi: TasiMetrisis = TasiMetrisis.STATHERI
    einai_palio: bool = False


class SfalmaPerigrafiSxhma(BaseModel):
    """Λεπτομέρειες σφάλματος στο τυποποιημένο φάκελο."""

    kodikos: str
    minyma: str
    leptomereies: Dict[str, Any] = Field(default_factory=dict)
    id_aitimatos: Optional[str] = None
    epanalipsimo: bool = False


class ApantisiSfalmatosSxhma(BaseModel):
    """Τυποποιημένος φάκελος σφάλματος API (§3.3)."""

    sfalma: SfalmaPerigrafiSxhma


class EntoliApantisiSxhma(BaseModel):
    """Βασική απόκριση κατάστασης εντολής."""

    id_entolis: str
    yposystima: str
    drasi: str
    katastasi: KatastasiEntolis
    id_xristi: str
    rolos: str
    xronos_dimiourgias: datetime
    xronos_enimerwsis: datetime
    minyma: str
    leptomereies: Dict[str, Any] = Field(default_factory=dict)
