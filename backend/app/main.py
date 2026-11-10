"""Κεντρικό σημείο εισόδου FastAPI για το Smart Mars Colony Backend."""

import logging
import re
import time
import uuid
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import StaleDataError
from starlette.exceptions import HTTPException

from backend.app.api.v1 import (
    aisthitires,
    apostoles,
    dikaiwmata,
    istoriko,
    poroi,
    senaria,
    synagermoi,
    synopsi,
    taftopoiisi,
    ygeia,
    ypostiriksi_zwis,
)
from backend.app.arxika_dedomena.fortwsi_dedomenwn import arxikopoiisi_dedomenwn_epideiksis
from backend.app.pyrinas.katagrafi import id_trexontos_aitimatos
from backend.app.pyrinas.rythmiseis import rythmiseis
from backend.app.pyrinas.sfalmata import KodikosSfalmatos, SfalmaKanona, xeiristis_sfalmatos_domain
from backend.app.sxhmata.koina import ApantisiSfalmatosSxhma
from backend.app.vasi.synthesi import SynedriaVasis, pare_synedria_vasis


@asynccontextmanager
async def kykloforia_efarmogis(efarmogi_kykloforias: FastAPI) -> AsyncGenerator[None, None]:
    """Lifespan context manager: αρχικοποιεί τη βάση δεδομένων και τα demo δεδομένα."""
    if rythmiseis.PERIVALLON not in {"anaptyxi", "dokimes"}:
        yield
        return
    paroxeas = efarmogi_kykloforias.dependency_overrides.get(pare_synedria_vasis)
    genitria = paroxeas() if paroxeas else None
    synedria = next(genitria) if genitria else SynedriaVasis()
    try:
        arxikopoiisi_dedomenwn_epideiksis(synedria, epanarxikopoiisi=False)
    finally:
        if genitria:
            genitria.close()
        else:
            synedria.close()
    yield


efarmogi = FastAPI(
    title=rythmiseis.ONOMA_EFARMOGIS,
    version=rythmiseis.EKDOSI,
    description="Εκπαιδευτικό backend προσομοίωσης έξυπνης αποικίας στον Άρη (ακαδημαϊκό έτος 2026–2027)",
    lifespan=kykloforia_efarmogis,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# CORS Middleware με ρητά επιτρεπόμενα origins
efarmogi.add_middleware(
    CORSMiddleware,
    allow_origins=rythmiseis.lista_epitrepomenwn_proelefsewn,
    allow_credentials=True,
    expose_headers=["X-Id-Aitimatos"],
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

katagrafeas = logging.getLogger("smart_mars_colony")
katagrafeas.setLevel(getattr(logging, rythmiseis.EPIPEDO_KATAGRAFIS.upper(), logging.INFO))


@efarmogi.middleware("http")
async def sysxetisi_aitimatos(aitima: Request, epomenos):
    """Καταγράφει μόνο μέθοδο, διαδρομή, αποτέλεσμα και διάρκεια, χωρίς σώματα/ταυτότητες."""
    protasi = aitima.headers.get("X-Id-Aitimatos", "")
    anagnwristiko = protasi if re.fullmatch(r"[A-Za-z0-9_-]{1,100}", protasi) else uuid.uuid4().hex
    diakritiko = id_trexontos_aitimatos.set(anagnwristiko)
    arxi = time.monotonic()
    try:
        try:
            apantisi = await epomenos(aitima)
        except Exception as sfalma:
            katagrafeas.error("aitima=%s eswteriko_sfalma=%s", anagnwristiko, type(sfalma).__name__)
            apantisi = await xeiristis_genikou_sfalmatos(aitima, sfalma)
        apantisi.headers["X-Id-Aitimatos"] = anagnwristiko
        katagrafeas.info(
            "aitima=%s methodos=%s diadromi=%s katastasi=%s diarkeia_ms=%.1f",
            anagnwristiko,
            aitima.method,
            aitima.url.path,
            apantisi.status_code,
            (time.monotonic() - arxi) * 1000,
        )
        return apantisi
    finally:
        id_trexontos_aitimatos.reset(diakritiko)


# Κοινοί χειριστές σφαλμάτων
efarmogi.add_exception_handler(SfalmaKanona, xeiristis_sfalmatos_domain)


def asfali_dedomena(dedomena):
    """Μετατρέπει μη πεπερασμένα validation inputs σε ασφαλή περιγραφή JSON."""
    import math

    if isinstance(dedomena, dict):
        return {str(kleidi): asfali_dedomena(timi) for kleidi, timi in dedomena.items()}
    if isinstance(dedomena, (list, tuple)):
        return [asfali_dedomena(timi) for timi in dedomena]
    if isinstance(dedomena, float) and not math.isfinite(dedomena):
        return str(dedomena)
    if isinstance(dedomena, (str, int, float, bool)) or dedomena is None:
        return dedomena
    return str(dedomena)


@efarmogi.exception_handler(HTTPException)
async def sfalma_http(aitima_http: Request, sfalma: HTTPException):
    return JSONResponse(
        status_code=sfalma.status_code,
        headers=sfalma.headers,
        content={
            "sfalma": {
                "kodikos": "DEN_VRETHIKE" if sfalma.status_code == 404 else "MH_EPITREPTI_ENERGEIA",
                "minyma": "Η διαδρομή δεν βρέθηκε."
                if sfalma.status_code == 404
                else "Η ζητούμενη ενέργεια δεν επιτρέπεται.",
                "leptomereies": {},
                "id_aitimatos": id_trexontos_aitimatos.get(),
                "epanalipsimo": False,
            }
        },
    )


@efarmogi.exception_handler(StaleDataError)
@efarmogi.exception_handler(IntegrityError)
async def sfalma_syggrousis(aitima_http: Request, sfalma: Exception):
    return JSONResponse(
        status_code=409,
        content={
            "sfalma": {
                "kodikos": "SYNTHIKI_SYGGROUSIS",
                "minyma": "Η κατάσταση μεταβλήθηκε ή υπάρχει αντικρουόμενη εντολή. Ανανεώστε τα δεδομένα.",
                "leptomereies": {},
                "id_aitimatos": id_trexontos_aitimatos.get(),
                "epanalipsimo": False,
            }
        },
    )


@efarmogi.exception_handler(RequestValidationError)
async def xeiristis_sfalmatos_epikyrwsis(
    aitima_http: Request, sfalma: RequestValidationError
) -> JSONResponse:
    """Τυποποιημένος φάκελος σφάλματος για αποτυχίες επικύρωσης εισόδου (§3.3)."""
    return JSONResponse(
        status_code=422,
        content={
            "sfalma": {
                "kodikos": KodikosSfalmatos.AKYRI_TIMI.value,
                "minyma": "Μη έγκυρα δεδομένα εισόδου στο αίτημα.",
                "leptomereies": {"sfalmata_pediwn": asfali_dedomena(sfalma.errors())},
                "id_aitimatos": id_trexontos_aitimatos.get(),
                "epanalipsimo": False,
            }
        },
    )


@efarmogi.exception_handler(Exception)
async def xeiristis_genikou_sfalmatos(aitima_http: Request, sfalma: Exception) -> JSONResponse:
    """Γενικός χειριστής απρόβλεπτων σφαλμάτων χωρίς έκθεση ευαίσθητων δεδομένων."""
    return JSONResponse(
        status_code=500,
        content={
            "sfalma": {
                "kodikos": KodikosSfalmatos.ESWTERIKO_SFALMA.value,
                "minyma": "Παρουσιάστηκε εσωτερικό σφάλμα διακομιστή.",
                "leptomereies": {},
                "id_aitimatos": id_trexontos_aitimatos.get(),
                "epanalipsimo": True,
            }
        },
    )


# Συμβατική ανακατεύθυνση framework-standard /health προς /api/v1/ygeia (CORE-03)
@efarmogi.get("/health", include_in_schema=False)
def elegxos_ygeias_protokollou():
    return RedirectResponse(url="/api/v1/ygeia")


# Καταχώριση όλων των δρομολογητών κάτω από το /api/v1
efarmogi.include_router(
    ygeia.dromologitis,
    prefix="/api/v1",
    responses={
        kodikos: {"model": ApantisiSfalmatosSxhma}
        for kodikos in (400, 401, 403, 404, 409, 422, 500, 503)
    },
)
efarmogi.include_router(
    taftopoiisi.dromologitis,
    prefix="/api/v1",
    responses={
        kodikos: {"model": ApantisiSfalmatosSxhma}
        for kodikos in (400, 401, 403, 404, 409, 422, 500, 503)
    },
)
efarmogi.include_router(
    dikaiwmata.dromologitis,
    prefix="/api/v1",
    responses={
        kodikos: {"model": ApantisiSfalmatosSxhma}
        for kodikos in (400, 401, 403, 404, 409, 422, 500, 503)
    },
)
efarmogi.include_router(
    synopsi.dromologitis,
    prefix="/api/v1",
    responses={
        kodikos: {"model": ApantisiSfalmatosSxhma}
        for kodikos in (400, 401, 403, 404, 409, 422, 500, 503)
    },
)
efarmogi.include_router(
    aisthitires.dromologitis,
    prefix="/api/v1",
    responses={
        kodikos: {"model": ApantisiSfalmatosSxhma}
        for kodikos in (400, 401, 403, 404, 409, 422, 500, 503)
    },
)
efarmogi.include_router(
    ypostiriksi_zwis.dromologitis,
    prefix="/api/v1",
    responses={
        kodikos: {"model": ApantisiSfalmatosSxhma}
        for kodikos in (400, 401, 403, 404, 409, 422, 500, 503)
    },
)
efarmogi.include_router(
    poroi.dromologitis,
    prefix="/api/v1",
    responses={
        kodikos: {"model": ApantisiSfalmatosSxhma}
        for kodikos in (400, 401, 403, 404, 409, 422, 500, 503)
    },
)
efarmogi.include_router(
    apostoles.dromologitis,
    prefix="/api/v1",
    responses={
        kodikos: {"model": ApantisiSfalmatosSxhma}
        for kodikos in (400, 401, 403, 404, 409, 422, 500, 503)
    },
)
efarmogi.include_router(
    synagermoi.dromologitis,
    prefix="/api/v1",
    responses={
        kodikos: {"model": ApantisiSfalmatosSxhma}
        for kodikos in (400, 401, 403, 404, 409, 422, 500, 503)
    },
)
efarmogi.include_router(
    senaria.dromologitis,
    prefix="/api/v1",
    responses={
        kodikos: {"model": ApantisiSfalmatosSxhma}
        for kodikos in (400, 401, 403, 404, 409, 422, 500, 503)
    },
)
efarmogi.include_router(
    istoriko.dromologitis,
    prefix="/api/v1",
    responses={
        kodikos: {"model": ApantisiSfalmatosSxhma}
        for kodikos in (400, 401, 403, 404, 409, 422, 500, 503)
    },
)
