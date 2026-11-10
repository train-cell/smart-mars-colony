"""Διαδρομές τοπικής ταυτοποίησης και πληροφοριών χρήστη (CORE-06, CORE-07)."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from backend.app.pyrinas.asfaleia import DedomenaXristi, pare_trexonta_xristi, pare_xristi_apo_vasi
from backend.app.sxhmata.apantiseis import EisodosApantisi, XristisApantisi
from backend.app.vasi.synthesi import pare_synedria_vasis

dromologitis = APIRouter(prefix="/taftopoiisi", tags=["Ταυτοποίηση & Χρήστες"])


class AitimaEisodou(BaseModel):
    """Αίτημα τοπικής ταυτοποίησης επίδειξης."""

    model_config = ConfigDict(extra="forbid")
    id_xristi: str


@dromologitis.post("/eisodos", summary="Είσοδος χρήστη επίδειξης")
def eisodos_xristi(
    aitima: AitimaEisodou, synedria: Session = Depends(pare_synedria_vasis)
) -> EisodosApantisi:
    """Επιστρέφει τα στοιχεία του λογαριασμού και τις κεφαλίδες εξουσιοδότησης."""
    xristis = pare_xristi_apo_vasi(synedria, aitima.id_xristi)
    return {
        "id_xristi": xristis.id_xristi,
        "onoma": xristis.onoma,
        "vasikos_rolos": xristis.vasikos_rolos.value,
        "energoi_roloi": [stoixeio_ro.value for stoixeio_ro in xristis.energoi_roloi],
        "odigies_kefalidwn": {
            "X-Id-Xristi": xristis.id_xristi,
            "X-Rolos": xristis.vasikos_rolos.value,
        },
        "minyma": "Επιτυχής ταυτοποίηση.",
    }


@dromologitis.get("/trexwn-xristis", summary="Πληροφορίες συνδεδεμένου χρήστη")
def plirofories_trexontos_xristi(
    xristis: DedomenaXristi = Depends(pare_trexonta_xristi),
) -> XristisApantisi:
    """Επιστρέφει τα στοιχεία και τα δικαιώματα του τρέχοντος ενεργού χρήστη."""
    return {
        "id_xristi": xristis.id_xristi,
        "onoma": xristis.onoma,
        "vasikos_rolos": xristis.vasikos_rolos.value,
        "energoi_roloi": [stoixeio_ro.value for stoixeio_ro in xristis.energoi_roloi],
    }
