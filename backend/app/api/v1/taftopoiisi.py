"""Διαδρομές τοπικής ταυτοποίησης και πληροφοριών χρήστη (CORE-06, CORE-07)."""

from typing import Any, Dict

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from backend.app.pyrinas.asfaleia import XRHSTES_DEMO, DedomenaXristi, pare_trexonta_xristi
from backend.app.pyrinas.sfalmata import KodikosSfalmatos, SfalmaDomain

router = APIRouter(prefix="/taftopoiisi", tags=["Ταυτοποίηση & Χρήστες"])


class AitimaEisodou(BaseModel):
    """Αίτημα τοπικής ταυτοποίησης επίδειξης."""

    id_xristi: str


@router.post("/eisodos", summary="Είσοδος χρήστη επίδειξης")
def eisodos_xristi(aitima: AitimaEisodou) -> Dict[str, Any]:
    """Επιστρέφει τα στοιχεία του λογαριασμού και τις κεφαλίδες εξουσιοδότησης."""
    if aitima.id_xristi not in XRHSTES_DEMO:
        raise SfalmaDomain(
            kodikos=KodikosSfalmatos.DEN_VRETHIKE,
            minyma=f"Ο χρήστης επίδειξης '{aitima.id_xristi}' δεν βρέθηκε.",
            katastasi_http=404,
            leptomereies={"diathesimoi_xristes": list(XRHSTES_DEMO.keys())},
        )

    xristis = XRHSTES_DEMO[aitima.id_xristi]
    return {
        "id_xristi": xristis.id_xristi,
        "onoma": xristis.onoma,
        "vasikos_rolos": xristis.vasikos_rolos.value,
        "energoi_roloi": [r.value for r in xristis.energoi_roloi],
        "odigies_headers": {
            "X-Id-Xristi": xristis.id_xristi,
            "X-Rolos": xristis.vasikos_rolos.value,
        },
        "minyma": "Επιτυχής ταυτοποίηση.",
    }


@router.get("/trexwn-xristis", summary="Πληροφορίες συνδεδεμένου χρήστη")
def pare_trexonta_xristi_endpoint(
    xristis: DedomenaXristi = Depends(pare_trexonta_xristi),
) -> Dict[str, Any]:
    """Επιστρέφει τα στοιχεία και τα δικαιώματα του τρέχοντος ενεργού χρήστη."""
    return {
        "id_xristi": xristis.id_xristi,
        "onoma": xristis.onoma,
        "vasikos_rolos": xristis.vasikos_rolos.value,
        "energoi_roloi": [r.value for r in xristis.energoi_roloi],
    }
