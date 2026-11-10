"""Τυποποιημένα σφάλματα και κωδικοί domain για το Smart Mars Colony Backend.

Όλοι οι κωδικοί σφάλματος είναι Greeklish και το σχήμα απόκρισης
ακολουθεί πιστά τη σύμβαση της παραγράφου §3.3.
"""

from enum import Enum
from typing import Any, Dict, Optional

from fastapi import Request
from fastapi.responses import JSONResponse

from backend.app.pyrinas.katagrafi import id_trexontos_aitimatos


class KodikosSfalmatos(str, Enum):
    """Κωδικοί σφαλμάτων domain."""

    ANEPARKES_NERO = "ANEPARKES_NERO"
    AKYRI_THERMOKRATIA = "AKYRI_THERMOKRATIA"
    AKYRI_TIMI = "AKYRI_TIMI"
    PALIA_METRISI = "PALIA_METRISI"
    APOUSIA_METRISIS = "APOUSIA_METRISIS"
    ANARMODIOS_XRISTIS = "ANARMODIOS_XRISTIS"
    DEN_VRETHIKE = "DEN_VRETHIKE"
    SYNTHIKI_SYGGROUSIS = "SYNTHIKI_SYGGROUSIS"
    PALIA_PROEPISKOPISI = "PALIA_PROEPISKOPISI"
    APOUSIA_TAFTOTITAS = "APOUSIA_TAFTOTITAS"
    ANEPARKIS_ENERGEIA = "ANEPARKIS_ENERGEIA"
    MH_ASPHALIS_KATASTASI = "MH_ASPHALIS_KATASTASI"
    APOTYXIA_EPIKOINWNIAS = "APOTYXIA_EPIKOINWNIAS"
    MH_EPITREPTI_METAVASI = "MH_EPITREPTI_METAVASI"
    DIKAIWMA_ELIKSE = "DIKAIWMA_ELIKSE"
    ESWTERIKO_SFALMA = "ESWTERIKO_SFALMA"


class SfalmaKanona(Exception):
    """Βασική εξαίρεση domain επιχειρησιακών κανόνων."""

    def __init__(
        self,
        kodikos: KodikosSfalmatos,
        minyma: str,
        katastasi_http: int = 400,
        leptomereies: Optional[Dict[str, Any]] = None,
        id_aitimatos: Optional[str] = None,
        epanalipsimo: bool = False,
    ):
        self.kodikos = kodikos
        self.minyma = minyma
        self.katastasi_http = katastasi_http
        self.leptomereies = leptomereies or {}
        self.id_aitimatos = id_aitimatos or id_trexontos_aitimatos.get()
        self.epanalipsimo = epanalipsimo
        super().__init__(minyma)

    def se_lexiko(self) -> Dict[str, Any]:
        """Μετατροπή στο τυποποιημένο JSON σχήμα σφάλματος."""
        return {
            "sfalma": {
                "kodikos": self.kodikos.value,
                "minyma": self.minyma,
                "leptomereies": self.leptomereies,
                "id_aitimatos": self.id_aitimatos,
                "epanalipsimo": self.epanalipsimo,
            }
        }


async def xeiristis_sfalmatos_domain(aitima_http: Request, sfalma: SfalmaKanona) -> JSONResponse:
    """FastAPI handler για εξαιρέσεις SfalmaDomain."""
    return JSONResponse(
        status_code=sfalma.katastasi_http,
        content=sfalma.se_lexiko(),
    )
