"""Κεντρικό σημείο εισόδου FastAPI για το Smart Mars Colony Backend."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse

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
from backend.app.pyrinas.rythmiseis import rythmiseis
from backend.app.pyrinas.sfalmata import KodikosSfalmatos, SfalmaDomain, xeiristis_sfalmatos_domain
from backend.app.vasi.synthesi import SynedriaVasis


@asynccontextmanager
async def kykloforia_efarmogis(app: FastAPI) -> AsyncGenerator[None, None]:
    """Lifespan context manager: αρχικοποιεί τη βάση δεδομένων και τα demo δεδομένα."""
    synedria = SynedriaVasis()
    try:
        arxikopoiisi_dedomenwn_epideiksis(synedria, epanarxikopoiisi=False)
    finally:
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
    allow_origins=rythmiseis.lista_epitrepomenwn_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Exception Handlers
efarmogi.add_exception_handler(SfalmaDomain, xeiristis_sfalmatos_domain)


@efarmogi.exception_handler(RequestValidationError)
async def xeiristis_sfalmatos_epikyrwsis(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Τυποποιημένος φάκελος σφάλματος για αποτυχίες επικύρωσης εισόδου (§3.3)."""
    return JSONResponse(
        status_code=422,
        content={
            "sfalma": {
                "kodikos": KodikosSfalmatos.AKYRI_TIMI.value,
                "minyma": "Μη έγκυρα δεδομένα εισόδου στο αίτημα.",
                "leptomereies": {"sfalmata_pediwn": exc.errors()},
                "id_aitimatos": None,
                "epanalipsimo": False,
            }
        },
    )


@efarmogi.exception_handler(Exception)
async def xeiristis_genikou_sfalmatos(request: Request, exc: Exception) -> JSONResponse:
    """Γενικός χειριστής απρόβλεπτων σφαλμάτων χωρίς έκθεση ευαίσθητων δεδομένων."""
    return JSONResponse(
        status_code=500,
        content={
            "sfalma": {
                "kodikos": KodikosSfalmatos.ESWTERIKO_SFALMA.value,
                "minyma": "Παρουσιάστηκε εσωτερικό σφάλμα διακομιστή.",
                "leptomereies": {"typos": type(exc).__name__},
                "id_aitimatos": None,
                "epanalipsimo": True,
            }
        },
    )


# Συμβατική ανακατεύθυνση framework-standard /health προς /api/v1/ygeia (CORE-03)
@efarmogi.get("/health", include_in_schema=False)
def framework_health():
    return RedirectResponse(url="/api/v1/ygeia")


# Καταχώριση όλων των Routers κάτω από το /api/v1
efarmogi.include_router(ygeia.router, prefix="/api/v1")
efarmogi.include_router(taftopoiisi.router, prefix="/api/v1")
efarmogi.include_router(dikaiwmata.router, prefix="/api/v1")
efarmogi.include_router(synopsi.router, prefix="/api/v1")
efarmogi.include_router(aisthitires.router, prefix="/api/v1")
efarmogi.include_router(ypostiriksi_zwis.router, prefix="/api/v1")
efarmogi.include_router(poroi.router, prefix="/api/v1")
efarmogi.include_router(apostoles.router, prefix="/api/v1")
efarmogi.include_router(synagermoi.router, prefix="/api/v1")
efarmogi.include_router(senaria.router, prefix="/api/v1")
efarmogi.include_router(istoriko.router, prefix="/api/v1")
