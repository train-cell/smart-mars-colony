"""Διαδρομές σεναρίου καταιγίδας σκόνης και ελέγχου προσομοίωσης (STORM-01…10, CORE-13)."""

from typing import Any, Dict, List

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.app.pyrinas.asfaleia import (
    DedomenaXristi,
    RolosXristi,
    apaitisi_rolou,
)
from backend.app.vasi.synthesi import pare_synedria_vasis
from backend.app.ypiresies.ypiresia_symvantwn_kai_senariwn import YpiresiaSymvantwnKaiSenariwn

router = APIRouter(tags=["Σενάρια & Προσομοίωση"])


class AitimaApofasisKataigidas(BaseModel):
    """Αίτημα έγκρισης απόφασης αντιμετώπισης καταιγίδας (STORM-06)."""

    epilogi: str = Field(
        description="Επιλογή: kamia_allagi, pausi_anavlhtwn, asfalis_stasi_rover, syndyasmos_pliroys_asfaleias"
    )
    aitiologia: str = Field(min_length=5, description="Αιτιολόγηση απόφασης συντονιστή")


class AitimaVimatosXronou(BaseModel):
    """Αίτημα προώθησης χρόνου προσομοίωσης (CORE-13)."""

    lepta: int = Field(default=15, gt=0, le=1440)


@router.get(
    "/senaria/kataigida-skonis", summary="Κατάσταση του fixture καταιγίδας σκόνης (STORM-01)"
)
def pare_katastasi_kataigidas(synedria: Session = Depends(pare_synedria_vasis)) -> Dict[str, Any]:
    """Επιστρέφει την τρέχουσα κατάσταση και τις περιβαλλοντικές παραμέτρους της καταιγίδας."""
    from backend.app.montela.poroi import Fwtovoltaiko

    pv = synedria.get(Fwtovoltaiko, "pv_01")
    einai_energi = (pv.aktinovolia_w_m2 < 100.0) if pv else False
    return {
        "senario": "kataigida_skonis_2026",
        "katastasi": "energi" if einai_energi else "baseline",
        "aktinovolia_w_m2": pv.aktinovolia_w_m2 if pv else 300.0,
        "syntelestis_f": pv.syntelestis_epikathisis_f if pv else 0.8,
    }


@router.post(
    "/senaria/kataigida-skonis/proepiskopisi",
    summary="Προεπισκόπηση επιλογών καταιγίδας με υπολογισμούς Golden Fixture (§6, STORM-05)",
)
def proepiskopisi_kataigidas(synedria: Session = Depends(pare_synedria_vasis)) -> Dict[str, Any]:
    """Υπολογίζει συγκριτικά όλες τις επιλογές (Baseline, Storm με/χωρίς αναβλητά, Rover ETA & Safe Stop)."""
    ypiresia = YpiresiaSymvantwnKaiSenariwn(synedria)
    return ypiresia.proepiskopisi_senariou_kataigidas()


@router.post(
    "/senaria/kataigida-skonis/energopoiisi",
    summary="Ενεργοποίηση συνθηκών καταιγίδας σκόνης (STORM-02)",
)
def energopoiisi_kataigidas(
    synedria: Session = Depends(pare_synedria_vasis),
    xristis: DedomenaXristi = Depends(apaitisi_rolou(RolosXristi.SYNTONISTIS_APOIKIAS)),
) -> Dict[str, Any]:
    """Ενημερώνει G=80, f=0.5, T_exw=193 K, ορατότητα 100 m και παράγει συναγερμό."""
    ypiresia = YpiresiaSymvantwnKaiSenariwn(synedria)
    return ypiresia.energopoiisi_kataigidas(xristis)


@router.post(
    "/senaria/{id_senariou}/apofaseis/proepiskopisi",
    summary="Συγκρίσεις αποφάσεων σεναρίου (STORM-05)",
)
def proepiskopisi_apofasewn_senariou(
    id_senariou: str,
    synedria: Session = Depends(pare_synedria_vasis),
) -> Dict[str, Any]:
    """Επιστρέφει την ανάλυση κόστους/οφέλους των διαθέσιμων αποφάσεων."""
    ypiresia = YpiresiaSymvantwnKaiSenariwn(synedria)
    return ypiresia.proepiskopisi_senariou_kataigidas()


@router.post(
    "/senaria/{id_senariou}/apofaseis",
    summary="Υποβολή και έγκριση απόφασης συντονιστή για καταιγίδα (STORM-06, STORM-08)",
)
def ypovoli_apofasis_senariou(
    id_senariou: str,
    aitima: AitimaApofasisKataigidas,
    synedria: Session = Depends(pare_synedria_vasis),
    xristis: DedomenaXristi = Depends(apaitisi_rolou(RolosXristi.SYNTONISTIS_APOIKIAS)),
) -> Dict[str, Any]:
    """Εκτελεί την απόφαση διαχείρισης κρίσης (π.χ. curtailment, rover safe stop) και καταγράφει audit."""
    ypiresia = YpiresiaSymvantwnKaiSenariwn(synedria)
    return ypiresia.ypovoli_apofasis_kataigidas(
        epilogi=aitima.epilogi,
        aitiologia=aitima.aitiologia,
        xristis=xristis,
    )


@router.get(
    "/senaria/{id_senariou}/xronologio",
    summary="Χρονολόγιο και ιστορικό αποφάσεων σεναρίου (STORM-08)",
)
def pare_xronologio_senariou(
    id_senariou: str,
    synedria: Session = Depends(pare_synedria_vasis),
) -> List[Dict[str, Any]]:
    """Επιστρέφει τις αποφάσεις που εγκρίθηκαν και καταγράφηκαν για το συγκεκριμένο σενάριο."""
    from backend.app.montela.koinonika_symvanta import Apofasi

    apofaseis = (
        synedria.query(Apofasi)
        .filter(Apofasi.id_senariou == id_senariou)
        .order_by(Apofasi.xronos_apofasis.desc())
        .all()
    )
    return [
        {
            "id_apofasis": a.id_apofasis,
            "id_syntonisti": a.id_syntonisti,
            "epilogi": a.epilogi,
            "aitiologia": a.aitiologia,
            "egkekrimeni": a.egkekrimeni,
            "xronos_apofasis": a.xronos_apofasis,
        }
        for a in apofaseis
    ]


# --- Έλεγχος Προσομοίωσης (CORE-13) ---


@router.post(
    "/prosomoiwsi/vima", summary="Προώθηση προσομοιωμένου ρολογιού (Dev/Test only - CORE-13)"
)
def proxorise_prosomoiwsi(
    aitima: AitimaVimatosXronou,
    synedria: Session = Depends(pare_synedria_vasis),
) -> Dict[str, Any]:
    """Προχωρά το ρολόι της αποικίας κατά καθορισμένο αριθμό λεπτών."""
    ypiresia = YpiresiaSymvantwnKaiSenariwn(synedria)
    return ypiresia.proxorise_xrono(lepta=aitima.lepta)


@router.post(
    "/prosomoiwsi/epanafora", summary="Επαναφορά προσομοίωσης στα αρχικά δεδομένα (Dev/Test only)"
)
def epanafora_prosomoiwsis(
    synedria: Session = Depends(pare_synedria_vasis),
    xristis: DedomenaXristi = Depends(apaitisi_rolou(RolosXristi.SYNTONISTIS_APOIKIAS)),
) -> Dict[str, Any]:
    """Επαναφέρει τις παραμέτρους στις κανονικές συνθήκες baseline."""
    from backend.app.arxika_dedomena.fortwsi_dedomenwn import arxikopoiisi_dedomenwn_epideiksis

    arxikopoiisi_dedomenwn_epideiksis(synedria, epanarxikopoiisi=True)
    return {"minyma": "Η προσομοίωση επανήλθε επιτυχώς στις αρχικές συνθήκες baseline."}
