"""Διαδρομές διαχείρισης μεταβίβασης δικαιωμάτων ελέγχου (CORE-18)."""

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, ConfigDict, Field, FiniteFloat
from sqlalchemy.orm import Session

from backend.app.pyrinas.asfaleia import (
    DedomenaXristi,
    RolosXristi,
    apaitisi_rolou,
    pare_trexonta_xristi,
)
from backend.app.sxhmata.apantiseis import (
    AnaklisiMetavivasisApantisi,
    EgkrisiMetavivasisApantisi,
    MetavivasiApantisi,
    ProepiskopisiMetavivasisApantisi,
)
from backend.app.vasi.synthesi import pare_synedria_vasis
from backend.app.ypiresies.ypiresia_symvantwn_kai_senariwn import YpiresiaSymvantwnKaiSenariwn

dromologitis = APIRouter(prefix="/dikaiwmata", tags=["Δικαιώματα & Μεταβιβάσεις"])


class AitimaProepiskopisisMetavivasis(BaseModel):
    """Αίτημα προεπισκόπησης μεταβίβασης ρόλου."""

    id_paralipti: str
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)
    rolos: RolosXristi
    diarkeia_wres: FiniteFloat = Field(gt=0, le=72)
    pedio_efarmogis: str = "geniko"


class AitimaDimiourgiasMetavivasis(BaseModel):
    """Αίτημα έγκρισης μεταβίβασης ρόλου."""

    id_paralipti: str
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)
    rolos: RolosXristi
    diarkeia_wres: FiniteFloat = Field(gt=0, le=72)
    aitiologia: str = Field(min_length=5)
    pedio_efarmogis: str = "geniko"


@dromologitis.get("/metavivaseis", summary="Ανάκτηση ισχυουσών μεταβιβάσεων ανά ρόλο και πεδίο")
def pare_metavivaseis(
    mono_energes: bool = Query(default=False),
    synedria: Session = Depends(pare_synedria_vasis),
) -> list[MetavivasiApantisi]:
    """Επιστρέφει όλες τις καταγεγραμμένες μεταβιβάσεις δικαιωμάτων."""
    ypiresia = YpiresiaSymvantwnKaiSenariwn(synedria)
    return ypiresia.pare_metavivaseis(mono_energes=mono_energes)


@dromologitis.post(
    "/metavivaseis/proepiskopisi", summary="Προεπισκόπηση επιπτώσεων και επιλεξιμότητας μεταβίβασης"
)
def proepiskopisi_metavivasis(
    aitima: AitimaProepiskopisisMetavivasis,
    synedria: Session = Depends(pare_synedria_vasis),
    xristis: DedomenaXristi = Depends(pare_trexonta_xristi),
) -> ProepiskopisiMetavivasisApantisi:
    """Ελέγχει τη συμβατότητα του ρόλου και επιστρέφει το χρονικό πλαίσιο."""
    from backend.app.montela import Xristis
    from backend.app.pyrinas.sfalmata import KodikosSfalmatos, SfalmaKanona

    paraliptis = synedria.get(Xristis, aitima.id_paralipti)
    if not paraliptis or not paraliptis.energos:
        raise SfalmaKanona(
            KodikosSfalmatos.DEN_VRETHIKE, "Ο παραλήπτης δεν είναι ενεργός χρήστης.", 404
        )
    if aitima.rolos == RolosXristi.SYNTONISTIS_APOIKIAS:
        raise SfalmaKanona(
            KodikosSfalmatos.ANARMODIOS_XRISTIS, "Μεταβιβάζονται μόνο επιχειρησιακοί ρόλοι.", 403
        )
    from backend.app.montela import (
        DexameniNerou,
        OximaExerevnis,
        Thermokipio,
        XwrosKatoikisis,
        ZwniThermokipiou,
    )

    if aitima.pedio_efarmogis not in {
        "geniko",
        "ypostiriksi_zwis",
        "poroi",
        "apostoles",
    } and not any(
        synedria.get(montelo, aitima.pedio_efarmogis)
        for montelo in [
            XwrosKatoikisis,
            OximaExerevnis,
            Thermokipio,
            ZwniThermokipiou,
            DexameniNerou,
        ]
    ):
        raise SfalmaKanona(KodikosSfalmatos.DEN_VRETHIKE, "Το πεδίο μεταβίβασης δεν υπάρχει.", 404)
    return {
        "id_syntonisti": xristis.id_xristi,
        "id_paralipti": aitima.id_paralipti,
        "rolos_pros_metavivasi": aitima.rolos.value,
        "pedio_efarmogis": aitima.pedio_efarmogis,
        "diarkeia_wres": aitima.diarkeia_wres,
        "einai_epileksimo": True,
        "minyma": "Η προτεινόμενη μεταβίβαση είναι έγκυρη και μπορεί να εγκριθεί από τον συντονιστή.",
    }


@dromologitis.post("/metavivaseis", summary="Έγκριση μεταβίβασης από coordinator με audit")
def dimiourgia_metavivasis(
    aitima: AitimaDimiourgiasMetavivasis,
    synedria: Session = Depends(pare_synedria_vasis),
    xristis: DedomenaXristi = Depends(apaitisi_rolou(RolosXristi.SYNTONISTIS_APOIKIAS)),
) -> EgkrisiMetavivasisApantisi:
    """Εγκρίνει και καταχωρίζει νέα μεταβίβαση ρόλου."""
    ypiresia = YpiresiaSymvantwnKaiSenariwn(synedria)
    return ypiresia.dimiourgia_metavivasis(
        id_paralipti=aitima.id_paralipti,
        rolos=aitima.rolos.value,
        diarkeia_wres=aitima.diarkeia_wres,
        aitiologia=aitima.aitiologia,
        xristis=xristis,
        pedio_efarmogis=aitima.pedio_efarmogis,
    )


@dromologitis.post(
    "/metavivaseis/{id_metavivasis}/anaklisi", summary="Ανάκληση εξουσιοδότησης με audit"
)
def anaklisi_metavivasis(
    id_metavivasis: str,
    synedria: Session = Depends(pare_synedria_vasis),
    xristis: DedomenaXristi = Depends(apaitisi_rolou(RolosXristi.SYNTONISTIS_APOIKIAS)),
) -> AnaklisiMetavivasisApantisi:
    """Ανακαλεί άμεσα ενεργή μεταβίβαση δικαιώματος."""
    ypiresia = YpiresiaSymvantwnKaiSenariwn(synedria)
    return ypiresia.anaklisi_metavivasis(id_metavivasis=id_metavivasis, xristis=xristis)
