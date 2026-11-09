"""Διαδρομές υποσυστήματος Γ: οχήματα εξερεύνησης (rover), αποστολές και κίνδυνοι (MISSION-01…08)."""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.app.pyrinas.asfaleia import (
    DedomenaXristi,
    RolosXristi,
    apaitisi_rolou,
)
from backend.app.pyrinas.sfalmata import KodikosSfalmatos, SfalmaDomain
from backend.app.vasi.synthesi import pare_synedria_vasis
from backend.app.ypiresies.ypiresia_apostolwn import YpiresiaApostolwn

router = APIRouter(tags=["Αποστολές & Rover (Υποσύστημα Γ)"])


class AitimaDimiourgiasApostolis(BaseModel):
    """Αίτημα προγραμματισμού νέας αποστολής rover."""

    titlos: str
    skopos: str
    apostasi_km: float = Field(gt=0, default=2.0)
    ektimwmeni_diarkeia_wres: float = Field(gt=0, default=1.0)


@router.get("/kindynoi", summary="Ροή εξωτερικών περιβαλλοντικών κινδύνων (MISSION-01)")
def pare_kindynous(synedria: Session = Depends(pare_synedria_vasis)) -> List[Dict[str, Any]]:
    """Επιστρέφει μετρήσεις και προβλέψεις καταιγίδας, ορατότητας και ακτινοβολίας."""
    ypiresia = YpiresiaApostolwn(synedria)
    return ypiresia.pare_kindynous()


@router.get("/oximata", summary="Λίστα και τηλεμετρία οχημάτων εξερεύνησης (MISSION-02)")
def pare_oximata(synedria: Session = Depends(pare_synedria_vasis)) -> List[Dict[str, Any]]:
    """Επιστρέφει τα ενεργά οχήματα rover, θέση, ταχύτητα, ενέργεια και κατάσταση επικοινωνίας."""
    ypiresia = YpiresiaApostolwn(synedria)
    return ypiresia.pare_oximata()


@router.get("/oximata/{id_oximatos}/apostoles", summary="Ιστορικό αποστολών οχήματος (MISSION-02)")
def pare_apostoles_oximatos(
    id_oximatos: str,
    synedria: Session = Depends(pare_synedria_vasis),
) -> Dict[str, Any]:
    """Επιστρέφει την κατάσταση του rover και όλες τις αποστολές του."""
    ypiresia = YpiresiaApostolwn(synedria)
    return ypiresia.pare_katastasi_oximatos(id_oximatos)


@router.post(
    "/oximata/{id_oximatos}/apostoles/proepiskopisi",
    summary="Προεπισκόπηση ενεργειακής απαίτησης αποστολής (MISSION-03)",
)
def proepiskopisi_apostolis(
    id_oximatos: str,
    aitima: AitimaDimiourgiasApostolis,
    synedria: Session = Depends(pare_synedria_vasis),
) -> Dict[str, Any]:
    """Υπολογίζει μη μεταλλακτικά την απαιτούμενη ενέργεια κίνησης."""
    from backend.app.fysika_montela.fysika_montela import ypologise_energeia_kinisis_oximatos

    apothiki = YpiresiaApostolwn(synedria).apothiki_apostolwn
    oxima = apothiki.pare_oxima_ana_id(id_oximatos)
    if not oxima:
        raise SfalmaDomain(
            kodikos=KodikosSfalmatos.DEN_VRETHIKE,
            minyma=f"Το όχημα '{id_oximatos}' δεν βρέθηκε.",
            katastasi_http=404,
        )

    _, _, synoliki_kwh = ypologise_energeia_kinisis_oximatos(
        maza_kg=oxima.maza_kg,
        apostasi_m=aitima.apostasi_km * 1000.0,
    )

    return {
        "id_oximatos": id_oximatos,
        "apostasi_km": aitima.apostasi_km,
        "ektimwmeni_energeia_kwh": round(synoliki_kwh, 4),
        "diathesimi_energeia_oximatos_kwh": oxima.energeia_kwh,
        "energeiaka_efikto": oxima.energeia_kwh >= synoliki_kwh + oxima.efedreia_kwh,
    }


@router.post(
    "/oximata/{id_oximatos}/apostoles",
    summary="Δημιουργία και επιβεβαίωση αποστολής (MISSION-04)",
)
def dimiourgia_apostolis(
    id_oximatos: str,
    aitima: AitimaDimiourgiasApostolis,
    synedria: Session = Depends(pare_synedria_vasis),
    xristis: DedomenaXristi = Depends(
        apaitisi_rolou(RolosXristi.YPEFTHYNOS_APOSTOLWN, RolosXristi.SYNTONISTIS_APOIKIAS)
    ),
) -> Dict[str, Any]:
    """Καταχωρίζει νέα αποστολή εξερεύνησης για το rover."""
    from backend.app.montela.apostoles import ApostoliOximatos

    id_ap = f"apost_{uuid.uuid4().hex[:8]}"
    twrinos = datetime.now(timezone.utc)

    apostoli = ApostoliOximatos(
        id_apostolis=id_ap,
        id_oximatos=id_oximatos,
        titlos=aitima.titlos,
        skopos=aitima.skopos,
        katastasi_apostolis="se_exelixi",
        xronos_enarksis=twrinos,
    )
    synedria.add(apostoli)
    synedria.commit()
    return {
        "id_apostolis": id_ap,
        "id_oximatos": id_oximatos,
        "katastasi": "se_exelixi",
        "minyma": "Η αποστολή καταχωρίστηκε επιτυχώς.",
    }


@router.post(
    "/oximata/{id_oximatos}/anaklisi/proepiskopisi",
    summary="Προεπισκόπηση ανάκλησης rover και πολυδιάστατη ασφάλεια (MISSION-03, MISSION-05, §6)",
)
def proepiskopisi_anaklisis(
    id_oximatos: str,
    synedria: Session = Depends(pare_synedria_vasis),
) -> Dict[str, Any]:
    """Υπολογίζει χρόνο, απαιτούμενη ενέργεια και αξιολογεί χωριστά ενέργεια, ορατότητα και επικοινωνία."""
    ypiresia = YpiresiaApostolwn(synedria)
    return ypiresia.proepiskopisi_anaklisis(id_oximatos)


@router.post(
    "/oximata/{id_oximatos}/anaklisi/entoles",
    summary="Εντολή ανάκλησης rover στη βάση (MISSION-04, MISSION-06)",
)
def ektelesi_anaklisis(
    id_oximatos: str,
    synedria: Session = Depends(pare_synedria_vasis),
    xristis: DedomenaXristi = Depends(
        apaitisi_rolou(RolosXristi.YPEFTHYNOS_APOSTOLWN, RolosXristi.SYNTONISTIS_APOIKIAS)
    ),
) -> Dict[str, Any]:
    """Εκτελεί εντολή ανάκλησης (κατάσταση 'avevaio' αν η επικοινωνία είναι υποβαθμισμένη)."""
    ypiresia = YpiresiaApostolwn(synedria)
    return ypiresia.ektelesi_anaklisis(id_oximatos, xristis)


@router.post(
    "/oximata/{id_oximatos}/asfalis-stasi/proepiskopisi",
    summary="Προεπισκόπηση επιλογών ασφαλούς στάσης rover (MISSION-08)",
)
def proepiskopisi_asfalous_stasis(
    id_oximatos: str,
    synedria: Session = Depends(pare_synedria_vasis),
) -> Dict[str, Any]:
    """Εμφανίζει τις συνέπειες ασφαλούς στάσης πριν την επιβεβαίωση της εντολής."""
    ypiresia = YpiresiaApostolwn(synedria)
    return ypiresia.proepiskopisi_asfalous_stasis(id_oximatos)


@router.post(
    "/oximata/{id_oximatos}/asfalis-stasi/entoles",
    summary="Εκτέλεση εντολής ασφαλούς στάσης rover (MISSION-04, MISSION-08)",
)
def ektelesi_asfalous_stasis(
    id_oximatos: str,
    synedria: Session = Depends(pare_synedria_vasis),
    xristis: DedomenaXristi = Depends(
        apaitisi_rolou(RolosXristi.YPEFTHYNOS_APOSTOLWN, RolosXristi.SYNTONISTIS_APOIKIAS)
    ),
) -> Dict[str, Any]:
    """Θέτει το όχημα σε ασφαλή στάση, μειώνει ισχύ και καταγράφει εντολή."""
    ypiresia = YpiresiaApostolwn(synedria)
    return ypiresia.ektelesi_asfalous_stasis(id_oximatos, xristis)


@router.post(
    "/oximata/{id_oximatos}/apostoles/{id_apostolis}/anavoli",
    summary="Αναβολή αποστολής rover (MISSION-04)",
)
def anavoli_apostolis(
    id_apostolis: str,
    synedria: Session = Depends(pare_synedria_vasis),
    xristis: DedomenaXristi = Depends(
        apaitisi_rolou(RolosXristi.YPEFTHYNOS_APOSTOLWN, RolosXristi.SYNTONISTIS_APOIKIAS)
    ),
) -> Dict[str, Any]:
    """Αναβάλλει εκκρεμή αποστολή λόγω συνθηκών."""
    from backend.app.montela.apostoles import ApostoliOximatos

    apostoli = synedria.get(ApostoliOximatos, id_apostolis)
    if not apostoli:
        raise SfalmaDomain(
            kodikos=KodikosSfalmatos.DEN_VRETHIKE,
            minyma=f"Η αποστολή '{id_apostolis}' δεν βρέθηκε.",
            katastasi_http=404,
        )
    apostoli.katastasi_apostolis = "anavolh"
    synedria.commit()
    return {"id_apostolis": id_apostolis, "katastasi": "anavolh"}
