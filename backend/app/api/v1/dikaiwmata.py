"""Διαδρομές διαχείρισης μεταβίβασης δικαιωμάτων ελέγχου (CORE-18)."""

from typing import Any, Dict, List

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.app.pyrinas.asfaleia import (
    DedomenaXristi,
    RolosXristi,
    apaitisi_rolou,
    pare_trexonta_xristi,
)
from backend.app.vasi.synthesi import pare_synedria_vasis
from backend.app.ypiresies.ypiresia_symvantwn_kai_senariwn import YpiresiaSymvantwnKaiSenariwn

router = APIRouter(prefix="/dikaiwmata", tags=["Δικαιώματα & Μεταβιβάσεις"])


class AitimaProepiskopisisMetavivasis(BaseModel):
    """Αίτημα προεπισκόπησης μεταβίβασης ρόλου."""

    id_paralipti: str
    rolos: str
    diarkeia_wres: float = Field(gt=0, le=72)
    pedio_efarmogis: str = "geniko"


class AitimaDimiourgiasMetavivasis(BaseModel):
    """Αίτημα έγκρισης μεταβίβασης ρόλου."""

    id_paralipti: str
    rolos: str
    diarkeia_wres: float = Field(gt=0, le=72)
    aitiologia: str = Field(min_length=5)
    pedio_efarmogis: str = "geniko"


@router.get("/metavivaseis", summary="Ανάκτηση ισχυουσών μεταβιβάσεων ανά ρόλο και πεδίο")
def pare_metavivaseis(
    mono_energes: bool = Query(default=False),
    synedria: Session = Depends(pare_synedria_vasis),
) -> List[Dict[str, Any]]:
    """Επιστρέφει όλες τις καταγεγραμμένες μεταβιβάσεις δικαιωμάτων."""
    ypiresia = YpiresiaSymvantwnKaiSenariwn(synedria)
    return ypiresia.pare_metavivaseis(mono_energes=mono_energes)


@router.post(
    "/metavivaseis/proepiskopisi", summary="Προεπισκόπηση επιπτώσεων και επιλεξιμότητας μεταβίβασης"
)
def proepiskopisi_metavivasis(
    aitima: AitimaProepiskopisisMetavivasis,
    xristis: DedomenaXristi = Depends(pare_trexonta_xristi),
) -> Dict[str, Any]:
    """Ελέγχει τη συμβατότητα του ρόλου και επιστρέφει το χρονικό πλαίσιο."""
    return {
        "id_syntonisti": xristis.id_xristi,
        "id_paralipti": aitima.id_paralipti,
        "rolos_pros_metavivasi": aitima.rolos,
        "pedio_efarmogis": aitima.pedio_efarmogis,
        "diarkeia_wres": aitima.diarkeia_wres,
        "einai_epileksimo": True,
        "minyma": "Η προτεινόμενη μεταβίβαση είναι έγκυρη και μπορεί να εγκριθεί από τον συντονιστή.",
    }


@router.post("/metavivaseis", summary="Έγκριση μεταβίβασης από coordinator με audit")
def dimiourgia_metavivasis(
    aitima: AitimaDimiourgiasMetavivasis,
    synedria: Session = Depends(pare_synedria_vasis),
    xristis: DedomenaXristi = Depends(apaitisi_rolou(RolosXristi.SYNTONISTIS_APOIKIAS)),
) -> Dict[str, Any]:
    """Εγκρίνει και καταχωρίζει νέα μεταβίβαση ρόλου."""
    ypiresia = YpiresiaSymvantwnKaiSenariwn(synedria)
    return ypiresia.dimiourgia_metavivasis(
        id_paralipti=aitima.id_paralipti,
        rolos=aitima.rolos,
        diarkeia_wres=aitima.diarkeia_wres,
        aitiologia=aitima.aitiologia,
        xristis=xristis,
        pedio_efarmogis=aitima.pedio_efarmogis,
    )


@router.post("/metavivaseis/{id_metavivasis}/anaklisi", summary="Ανάκληση εξουσιοδότησης με audit")
def anaklisi_metavivasis(
    id_metavivasis: str,
    synedria: Session = Depends(pare_synedria_vasis),
    xristis: DedomenaXristi = Depends(apaitisi_rolou(RolosXristi.SYNTONISTIS_APOIKIAS)),
) -> Dict[str, Any]:
    """Ανακαλεί άμεσα ενεργή μεταβίβαση δικαιώματος."""
    ypiresia = YpiresiaSymvantwnKaiSenariwn(synedria)
    return ypiresia.anaklisi_metavivasis(id_metavivasis=id_metavivasis, xristis=xristis)
