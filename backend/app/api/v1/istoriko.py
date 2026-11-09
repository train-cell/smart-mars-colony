"""Διαδρομή καταγραφής ιστορικού ελέγχου (Audit Log - CORE-10)."""

from typing import Any, Dict, List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.app.apothikes.apothiki_koinwn import ApothikiKoinwn
from backend.app.vasi.synthesi import pare_synedria_vasis

router = APIRouter(tags=["Ιστορικό Ελέγχου"])


@router.get("/istoriko-elegxou", summary="Ανάκτηση αμετάβλητου ιστορικού ελέγχου (Audit Trail)")
def pare_istoriko_elegxou(
    orio: int = Query(default=100, ge=1, le=500),
    synedria: Session = Depends(pare_synedria_vasis),
) -> List[Dict[str, Any]]:
    """Επιστρέφει καταγεγραμμένες ενέργειες, χρήστες, ρόλους, παλιές/νέες τιμές και αιτιολογίες."""
    apothiki = ApothikiKoinwn(synedria)
    istoriko = apothiki.pare_istoriko_elegxou(orio=orio)
    return [
        {
            "id": i.id_istorikou,
            "id_xristi": i.id_xristi,
            "rolos": i.rolos,
            "energeia": i.energeia,
            "ontotita": i.ontotita,
            "id_ontotitas": i.id_ontotitas,
            "palia_timi": i.palia_timi,
            "nea_timi": i.nea_timi,
            "aitiologia": i.aitiologia,
            "id_aitimatos": i.id_aitimatos,
            "xronos_katagrafis": i.xronos_katagrafis,
        }
        for i in istoriko
    ]
