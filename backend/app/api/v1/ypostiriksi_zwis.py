"""Διαδρομές υποσυστήματος Α: υποστήριξη ζωής, ατμόσφαιρα και έλεγχος θερμοκρασίας (LIFE-01…10)."""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, Header
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.app.pyrinas.asfaleia import (
    DedomenaXristi,
    RolosXristi,
    apaitisi_rolou,
    pare_trexonta_xristi,
)
from backend.app.pyrinas.sfalmata import KodikosSfalmatos, SfalmaDomain
from backend.app.vasi.synthesi import pare_synedria_vasis
from backend.app.ypiresies.ypiresia_ypostiriksis_zwis import YpiresiaYpostiriksisZwis

router = APIRouter(tags=["Υποστήριξη Ζωής (Υποσύστημα Α)"])


class AitimaProepiskopisisThermokrasias(BaseModel):
    """Αίτημα προεπισκόπησης αλλαγής επιθυμητής θερμοκρασίας (§7, LIFE-06)."""

    epithymiti_thermokrasia_k: float = Field(gt=0, description="Επιθυμητή θερμοκρασία σε Kelvin")
    anamenomeni_ekdosi_katastasis: int = Field(
        ge=0, description="Αναμενόμενη έκδοση για optimistic lock"
    )


class AitimaEpivevaiwsisThermokrasias(BaseModel):
    """Αίτημα επιβεβαίωσης εντολής αλλαγής θερμοκρασίας (LIFE-07)."""

    id_proepiskopisis: str = Field(description="Το ID της εγκεκριμένης προεπισκόπησης")
    anamenomeni_ekdosi_katastasis: int = Field(ge=0)


@router.get("/xwroi-katoikisis", summary="Λίστα κατοικήσιμων χώρων και βασικών μετρήσεων (LIFE-01)")
def pare_xwrous_katoikisis(
    synedria: Session = Depends(pare_synedria_vasis),
) -> List[Dict[str, Any]]:
    """Επιστρέφει όλους τους θαλάμους διαβίωσης της αποικίας."""
    ypiresia = YpiresiaYpostiriksisZwis(synedria)
    return ypiresia.pare_xwrous()


@router.get(
    "/xwroi-katoikisis/{id_xwrou}/katastasi",
    summary="Πλήρες snapshot υποστήριξης ζωής θαλάμου (LIFE-02, LIFE-03)",
)
def pare_katastasi_xwrou(
    id_xwrou: str,
    synedria: Session = Depends(pare_synedria_vasis),
) -> Dict[str, Any]:
    """Επιστρέφει εσωτερική/εξωτερική θερμοκρασία, πιέσεις, O2, CO2, υγρασία και εξοπλισμό."""
    ypiresia = YpiresiaYpostiriksisZwis(synedria)
    return ypiresia.pare_katastasi_xwrou(id_xwrou)


@router.get(
    "/xwroi-katoikisis/{id_xwrou}/provlepsi-oxygonou",
    summary="Πρόβλεψη οξυγόνου και εκτίμηση αυτονομίας (LIFE-04)",
)
def pare_provlepsi_oxygonou(
    id_xwrou: str,
    synedria: Session = Depends(pare_synedria_vasis),
) -> Dict[str, Any]:
    """Επιστρέφει τη μερική πίεση O2, τη διαθέσιμη μάζα πάνω από το κατώφλι και την αυτονομία σε ώρες."""
    ypiresia = YpiresiaYpostiriksisZwis(synedria)
    return ypiresia.provlepsi_oxygonou(id_xwrou)


@router.post(
    "/xwroi-katoikisis/{id_xwrou}/thermokrasia/proepiskopisi",
    summary="Προεπισκόπηση αλλαγής θερμοκρασίας χωρίς μεταβολή κατάστασης (LIFE-06, §7)",
)
def proepiskopisi_thermokrasias(
    id_xwrou: str,
    aitima: AitimaProepiskopisisThermokrasias,
    synedria: Session = Depends(pare_synedria_vasis),
    xristis: DedomenaXristi = Depends(
        apaitisi_rolou(RolosXristi.YPEFTHYNOS_YPOSTIRIKSIS_ZWIS, RolosXristi.SYNTONISTIS_APOIKIAS)
    ),
) -> Dict[str, Any]:
    """Υπολογίζει μη μεταλλακτικά τη μεταβολή ισχύος θέρμανσης [W] και επιστρέφει snapshot επιβεβαίωσης."""
    ypiresia = YpiresiaYpostiriksisZwis(synedria)
    return ypiresia.proepiskopisi_allagis_thermokrasias(
        id_xwrou=id_xwrou,
        epithymiti_thermokrasia_k=aitima.epithymiti_thermokrasia_k,
        anamenomeni_ekdosi_katastasis=aitima.anamenomeni_ekdosi_katastasis,
    )


@router.post(
    "/xwroi-katoikisis/{id_xwrou}/thermokrasia/entoles",
    summary="Επιβεβαίωση και εκτέλεση αλλαγής θερμοκρασίας (LIFE-07)",
)
def ektelesi_allagis_thermokrasias(
    id_xwrou: str,
    aitima: AitimaEpivevaiwsisThermokrasias,
    synedria: Session = Depends(pare_synedria_vasis),
    xristis: DedomenaXristi = Depends(
        apaitisi_rolou(RolosXristi.YPEFTHYNOS_YPOSTIRIKSIS_ZWIS, RolosXristi.SYNTONISTIS_APOIKIAS)
    ),
    idempotency_key: Optional[str] = Header(default=None, alias="Idempotency-Key"),
) -> Dict[str, Any]:
    """Επιβεβαιώνει την προεπισκόπηση και ενημερώνει τον στόχο θερμοκρασίας και το audit log."""
    ypiresia = YpiresiaYpostiriksisZwis(synedria)
    return ypiresia.ektelesi_allagis_thermokrasias(
        id_xwrou=id_xwrou,
        id_proepiskopisis=aitima.id_proepiskopisis,
        anamenomeni_ekdosi_katastasis=aitima.anamenomeni_ekdosi_katastasis,
        xristis=xristis,
        id_aitimatos_monadikotitas=idempotency_key,
    )


# --- Εντολές Lifecycle (CORE-10, CORE-19) ---


@router.get(
    "/entoles/{id_entolis}", summary="Ανάκτηση κατάστασης και κύκλου ζωής εντολής (CORE-10)"
)
def pare_entoli(
    id_entolis: str,
    synedria: Session = Depends(pare_synedria_vasis),
) -> Dict[str, Any]:
    """Επιστρέφει την κατάσταση, τα συμβάντα και το αποτέλεσμα μιας εκτελεσθείσας εντολής."""
    from backend.app.apothikes.apothiki_koinwn import ApothikiKoinwn

    apothiki = ApothikiKoinwn(synedria)
    entoli = apothiki.pare_entoli_ana_id(id_entolis)
    if not entoli:
        raise SfalmaDomain(
            kodikos=KodikosSfalmatos.DEN_VRETHIKE,
            minyma=f"Η εντολή '{id_entolis}' δεν βρέθηκε.",
            katastasi_http=404,
        )

    return {
        "id_entolis": entoli.id_entolis,
        "id_xristi": entoli.id_xristi,
        "rolos": entoli.rolos,
        "yposystima": entoli.yposystima,
        "drasi": entoli.drasi,
        "katastasi": entoli.katastasi,
        "id_proepiskopisis": entoli.id_proepiskopisis,
        "anamenomeni_ekdosi": entoli.anamenomeni_ekdosi,
        "dedomena_aitimatos": entoli.dedomena_aitimatos,
        "apotelesma": entoli.apotelesma,
        "xronos_ektelesis": entoli.xronos_ektelesis,
        "symvanta": [
            {
                "proigoumeni": s.proigoumeni_katastasi,
                "nea": s.nea_katastasi,
                "minyma": s.minyma,
                "xronos": s.xronos_symvantos,
            }
            for s in entoli.symvanta
        ],
    }


@router.post(
    "/entoles/{id_entolis}/akyrosi", summary="Ακύρωση εντολής εφόσον επιτρέπεται (CORE-10)"
)
def akyrosi_entolis(
    id_entolis: str,
    synedria: Session = Depends(pare_synedria_vasis),
    xristis: DedomenaXristi = Depends(pare_trexonta_xristi),
) -> Dict[str, Any]:
    """Ακυρώνει εντολή που βρίσκεται σε εκκρεμή ή αναστρέψιμη κατάσταση."""
    from backend.app.apothikes.apothiki_koinwn import ApothikiKoinwn

    apothiki = ApothikiKoinwn(synedria)
    entoli = apothiki.pare_entoli_ana_id(id_entolis)
    if not entoli:
        raise SfalmaDomain(
            kodikos=KodikosSfalmatos.DEN_VRETHIKE,
            minyma=f"Η εντολή '{id_entolis}' δεν βρέθηκε.",
            katastasi_http=404,
        )

    if entoli.katastasi in ["akyrothike", "apetyxe"]:
        raise SfalmaDomain(
            kodikos=KodikosSfalmatos.MH_EPITREPTI_METAVASI,
            minyma=f"Η εντολή είναι ήδη σε τελική κατάσταση '{entoli.katastasi}'.",
            katastasi_http=400,
        )

    entoli.katastasi = "akyrothike"
    synedria.commit()
    return {
        "id_entolis": id_entolis,
        "katastasi": "akyrothike",
        "minyma": "Η εντολή ακυρώθηκε επιτυχώς.",
    }
