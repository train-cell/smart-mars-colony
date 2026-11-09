"""Διαδρομές υποσυστήματος Β: θερμοκήπια, νερό, φωτοβολταϊκά και ενέργεια (RES-01…14)."""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, Header
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.app.pyrinas.asfaleia import (
    DedomenaXristi,
    RolosXristi,
    apaitisi_rolou,
)
from backend.app.pyrinas.sfalmata import KodikosSfalmatos, SfalmaDomain
from backend.app.vasi.synthesi import pare_synedria_vasis
from backend.app.ypiresies.ypiresia_porwn import YpiresiaPorwn

router = APIRouter(tags=["Πόροι & Ενέργεια (Υποσύστημα Β)"])


# --- Schemas ---


class AitimaProepiskopisisArdefsis(BaseModel):
    """Αίτημα προεπισκόπησης άρδευσης (RES-05)."""

    id_zwnis: str
    posotita_nerou_l: float = Field(gt=0, description="Ποσότητα νερού σε λίτρα")
    diarkeia_lepta: int = Field(default=30, gt=0)


class AitimaDimiourgiasArdefsis(BaseModel):
    """Αίτημα επιβεβαίωσης άρδευσης (RES-06)."""

    id_proepiskopisis: str


class AitimaProepiskopisisFwtismou(BaseModel):
    """Αίτημα προεπισκόπησης φωτισμού (RES-13)."""

    id_zwnis: str
    isxys_kw: float = Field(gt=0, default=2.0)
    diarkeia_wres: float = Field(gt=0, default=4.0)


class AitimaProepiskopisisAnakyklwsis(BaseModel):
    """Αίτημα προεπισκόπησης ανακύκλωσης (RES-12)."""

    posotita_nerou_l: float = Field(gt=0)
    apodosi: float = Field(ge=0.5, le=0.99, default=0.85)


class AitimaPeriorismouFortiwn(BaseModel):
    """Αίτημα περιορισμού αναβλητών φορτίων (RES-10)."""

    pausi_anavlhtwn: bool = True
    aitiologia: str = Field(min_length=5)


# ============================================================================
# Θερμοκήπια & Ζώνες
# ============================================================================


@router.get("/thermokipia", summary="Λίστα και κατάσταση θερμοκηπίων (RES-01)")
def pare_thermokipia(synedria: Session = Depends(pare_synedria_vasis)) -> List[Dict[str, Any]]:
    """Επιστρέφει τα θερμοκήπια, θερμοκρασία και υγρασία αέρα."""
    ypiresia = YpiresiaPorwn(synedria)
    return ypiresia.pare_thermokipia()


@router.get(
    "/thermokipia/{id_thermokipiou}/zwnes",
    summary="Ζώνες θερμοκηπίου και υγρασία υποστρώματος (RES-01)",
)
def pare_zwnes_thermokipiou(
    id_thermokipiou: str,
    synedria: Session = Depends(pare_synedria_vasis),
) -> List[Dict[str, Any]]:
    """Επιστρέφει τις ζώνες καλλιέργειας, υγρασία και κατάσταση φωτισμού."""
    ypiresia = YpiresiaPorwn(synedria)
    return ypiresia.pare_zwnes(id_thermokipiou)


# ============================================================================
# Άρδευση
# ============================================================================


@router.post(
    "/thermokipia/{id_thermokipiou}/ardefsi/proepiskopisi",
    summary="Προεπισκόπηση προγράμματος άρδευσης (RES-05)",
)
def proepiskopisi_ardefsis(
    id_thermokipiou: str,
    aitima: AitimaProepiskopisisArdefsis,
    synedria: Session = Depends(pare_synedria_vasis),
    xristis: DedomenaXristi = Depends(
        apaitisi_rolou(RolosXristi.YPEFTHYNOS_PORWN, RolosXristi.SYNTONISTIS_APOIKIAS)
    ),
) -> Dict[str, Any]:
    """Υπολογίζει μη μεταλλακτικά την προβλεπόμενη στάθμη δεξαμενής και υγρασία ζώνης."""
    ypiresia = YpiresiaPorwn(synedria)
    return ypiresia.proepiskopisi_ardefsis(
        id_thermokipiou=id_thermokipiou,
        id_zwnis=aitima.id_zwnis,
        posotita_nerou_l=aitima.posotita_nerou_l,
        diarkeia_lepta=aitima.diarkeia_lepta,
    )


@router.post(
    "/thermokipia/{id_thermokipiou}/ardefsi/programmata",
    summary="Δημιουργία προγράμματος άρδευσης μετά από confirm (RES-06)",
)
def dimiourgia_programmatos_ardefsis(
    id_thermokipiou: str,
    aitima: AitimaDimiourgiasArdefsis,
    synedria: Session = Depends(pare_synedria_vasis),
    xristis: DedomenaXristi = Depends(
        apaitisi_rolou(RolosXristi.YPEFTHYNOS_PORWN, RolosXristi.SYNTONISTIS_APOIKIAS)
    ),
    idempotency_key: Optional[str] = Header(default=None, alias="Idempotency-Key"),
) -> Dict[str, Any]:
    """Επιβεβαιώνει την προεπισκόπηση, δεσμεύει νερό από τη δεξαμενή και καταγράφει το πρόγραμμα."""
    ypiresia = YpiresiaPorwn(synedria)
    return ypiresia.dimiourgia_programmatos_ardefsis(
        id_proepiskopisis=aitima.id_proepiskopisis,
        xristis=xristis,
        id_aitimatos_monadikotitas=idempotency_key,
    )


@router.get(
    "/thermokipia/{id_thermokipiou}/ardefsi/programmata",
    summary="Λίστα προγραμμάτων άρδευσης θερμοκηπίου (RES-06)",
)
def pare_programmata_ardefsis(
    id_thermokipiou: str,
    synedria: Session = Depends(pare_synedria_vasis),
) -> List[Dict[str, Any]]:
    """Επιστρέφει όλα τα προγραμματισμένα και εκτελεσθέντα ποτίσματα."""
    from backend.app.apothikes.apothiki_porwn import ApothikiPorwn

    apothiki = ApothikiPorwn(synedria)
    programmata = apothiki.pare_programmata_ardefsis(id_thermokipiou=id_thermokipiou)
    return [
        {
            "id_programmatos": p.id_programmatos,
            "id_zwnis": p.id_zwnis,
            "posotita_nerou_l": p.posotita_nerou_l,
            "xronos_enarksis": p.xronos_enarksis,
            "diarkeia_lepta": p.diarkeia_lepta,
            "katastasi": p.katastasi,
        }
        for p in programmata
    ]


@router.post(
    "/ardefsi/programmata/{id_programmatos}/akyrosi",
    summary="Ακύρωση προγραμματισμένης άρδευσης (RES-06)",
)
def akyrosi_ardefsis(
    id_programmatos: str,
    synedria: Session = Depends(pare_synedria_vasis),
    xristis: DedomenaXristi = Depends(
        apaitisi_rolou(RolosXristi.YPEFTHYNOS_PORWN, RolosXristi.SYNTONISTIS_APOIKIAS)
    ),
) -> Dict[str, Any]:
    """Ακυρώνει μη εκτελεσμένο πρόγραμμα και επιστρέφει το δεσμευμένο νερό."""
    ypiresia = YpiresiaPorwn(synedria)
    return ypiresia.akyrosi_programmatos_ardefsis(id_programmatos, xristis)


# ============================================================================
# Φωτισμός Θερμοκηπίου (RES-13)
# ============================================================================


@router.post(
    "/thermokipia/{id_thermokipiou}/fwtismos/proepiskopisi",
    summary="Προεπισκόπηση επιπτώσεων τεχνητού φωτισμού (RES-13)",
)
def proepiskopisi_fwtismou(
    id_thermokipiou: str,
    aitima: AitimaProepiskopisisFwtismou,
) -> Dict[str, Any]:
    """Υπολογίζει την ενεργειακή απαίτηση φωτισμού σε kWh και kW."""
    synoliki_energeia_kwh = aitima.isxys_kw * aitima.diarkeia_wres
    return {
        "id_thermokipiou": id_thermokipiou,
        "id_zwnis": aitima.id_zwnis,
        "isxys_kw": aitima.isxys_kw,
        "diarkeia_wres": aitima.diarkeia_wres,
        "synoliki_energeia_kwh": synoliki_energeia_kwh,
        "minyma": "Η προεπισκόπηση φωτισμού υπολογίστηκε επιτυχώς.",
    }


@router.post(
    "/thermokipia/{id_thermokipiou}/fwtismos/entoles",
    summary="Επιβεβαίωση και προγραμματισμός φωτισμού (RES-13)",
)
def dimiourgia_programmatos_fwtismou(
    id_thermokipiou: str,
    aitima: AitimaProepiskopisisFwtismou,
    synedria: Session = Depends(pare_synedria_vasis),
    xristis: DedomenaXristi = Depends(
        apaitisi_rolou(RolosXristi.YPEFTHYNOS_PORWN, RolosXristi.SYNTONISTIS_APOIKIAS)
    ),
) -> Dict[str, Any]:
    """Καταχωρίζει πρόγραμμα τεχνητού φωτισμού."""
    from datetime import timedelta

    from backend.app.montela.poroi import ProgrammaFwtismou

    id_prog = f"prog_fwt_{uuid.uuid4().hex[:8]}"
    twrinos = datetime.now(timezone.utc)
    liksi = twrinos + timedelta(hours=aitima.diarkeia_wres)

    programma = ProgrammaFwtismou(
        id_programmatos=id_prog,
        id_thermokipiou=id_thermokipiou,
        id_zwnis=aitima.id_zwnis,
        isxys_kw=aitima.isxys_kw,
        xronos_enarksis=twrinos,
        xronos_liksis=liksi,
        katastasi="programmatismeno",
    )
    synedria.add(programma)
    synedria.commit()
    return {
        "id_programmatos": id_prog,
        "katastasi": "programmatismeno",
        "isxys_kw": aitima.isxys_kw,
        "xronos_liksis": liksi,
        "minyma": "Το πρόγραμμα τεχνητού φωτισμού καταχωρίστηκε επιτυχώς.",
    }


@router.get(
    "/thermokipia/{id_thermokipiou}/fwtismos/programmata",
    summary="Ανάκτηση προγραμμάτων φωτισμού (RES-13)",
)
def pare_programmata_fwtismou(
    id_thermokipiou: str,
    synedria: Session = Depends(pare_synedria_vasis),
) -> List[Dict[str, Any]]:
    """Επιστρέφει τα προγράμματα φωτισμού του θερμοκηπίου."""
    from backend.app.apothikes.apothiki_porwn import ApothikiPorwn

    apothiki = ApothikiPorwn(synedria)
    programmata = apothiki.pare_programmata_fwtismou(id_thermokipiou=id_thermokipiou)
    return [
        {
            "id_programmatos": p.id_programmatos,
            "id_zwnis": p.id_zwnis,
            "isxys_kw": p.isxys_kw,
            "xronos_enarksis": p.xronos_enarksis,
            "xronos_liksis": p.xronos_liksis,
            "katastasi": p.katastasi,
        }
        for p in programmata
    ]


@router.post(
    "/thermokipia/{id_thermokipiou}/fwtismos/programmata/{id_programmatos}/akyrosi",
    summary="Ακύρωση προγράμματος φωτισμού (RES-13)",
)
def akyrosi_fwtismou(
    id_programmatos: str,
    synedria: Session = Depends(pare_synedria_vasis),
    xristis: DedomenaXristi = Depends(
        apaitisi_rolou(RolosXristi.YPEFTHYNOS_PORWN, RolosXristi.SYNTONISTIS_APOIKIAS)
    ),
) -> Dict[str, Any]:
    """Ακυρώνει προγραμματισμένο φωτισμό."""
    from backend.app.apothikes.apothiki_porwn import ApothikiPorwn

    apothiki = ApothikiPorwn(synedria)
    prog = apothiki.pare_programma_fwtismou_ana_id(id_programmatos)
    if not prog:
        raise SfalmaDomain(
            kodikos=KodikosSfalmatos.DEN_VRETHIKE,
            minyma=f"Το πρόγραμμα φωτισμού '{id_programmatos}' δεν βρέθηκε.",
            katastasi_http=404,
        )
    prog.katastasi = "akyrothike"
    synedria.commit()
    return {"id_programmatos": id_programmatos, "katastasi": "akyrothike"}


# ============================================================================
# Νερό, Δεξαμενές και Ανακύκλωση
# ============================================================================


@router.get("/nero/dexamenes", summary="Στάθμη, χωρητικότητα και εφεδρεία δεξαμενών (RES-03)")
def pare_dexamenes_nerou(synedria: Session = Depends(pare_synedria_vasis)) -> Dict[str, Any]:
    """Επιστρέφει την κατάσταση όλων των δεξαμενών νερού."""
    ypiresia = YpiresiaPorwn(synedria)
    return ypiresia.pare_katastasi_nerou()


@router.get("/nero/isozygio", summary="Αναλυτικό ισοζύγιο νερού και πρόβλεψη επάρκειας (RES-03)")
def pare_isozygio_nerou(synedria: Session = Depends(pare_synedria_vasis)) -> Dict[str, Any]:
    """Επιστρέφει συνολικές εισροές, αναλώσεις και καθαρό ρυθμό μεταβολής."""
    ypiresia = YpiresiaPorwn(synedria)
    katastasi = ypiresia.pare_katastasi_nerou()
    roes = katastasi["roes"]

    eisroes_l_h = sum(r["rythmos_l_h"] for r in roes if r["typos"] in ["eisroi", "anakyklwsi"])
    ekroes_l_h = sum(
        r["rythmos_l_h"] for r in roes if r["typos"] in ["analwsi", "ardefsi", "diarros"]
    )

    return {
        "apothema": katastasi["synolika"],
        "roes_l_h": {
            "synolikes_eisroes": eisroes_l_h,
            "synolikes_ekroes": ekroes_l_h,
            "katharos_rythmos": round(eisroes_l_h - ekroes_l_h, 2),
        },
    }


@router.get("/nero/roes", summary="Μετρημένοι και εκτιμώμενοι ρυθμοί ροής νερού (RES-14)")
def pare_roes_nerou(synedria: Session = Depends(pare_synedria_vasis)) -> List[Dict[str, Any]]:
    """Επιστρέφει τις τελευταίες καταγεγραμμένες ροές νερού."""
    ypiresia = YpiresiaPorwn(synedria)
    return ypiresia.pare_katastasi_nerou()["roes"]


@router.post("/nero/anakyklwsi/proepiskopisi", summary="Προεπισκόπηση ανακύκλωσης νερού (RES-12)")
def proepiskopisi_anakyklwsis(aitima: AitimaProepiskopisisAnakyklwsis) -> Dict[str, Any]:
    """Υπολογίζει μη μεταλλακτικά την επιστρεφόμενη ποσότητα καθαρού νερού."""
    epistrefomeno_l = aitima.posotita_nerou_l * aitima.apodosi
    apwleia_l = aitima.posotita_nerou_l - epistrefomeno_l
    return {
        "posotita_akarthartou_l": aitima.posotita_nerou_l,
        "apodosi_anakyklwsis": aitima.apodosi,
        "epistrefomeno_nero_l": round(epistrefomeno_l, 2),
        "apwleia_l": round(apwleia_l, 2),
    }


@router.post("/nero/anakyklwsi/entoles", summary="Προγραμματισμός κύκλου ανακύκλωσης (RES-12)")
@router.post("/nero/anakyklwsi/programmata", summary="Δημιουργία προγράμματος ανακύκλωσης (RES-12)")
def dimiourgia_programmatos_anakyklwsis(
    aitima: AitimaProepiskopisisAnakyklwsis,
    synedria: Session = Depends(pare_synedria_vasis),
    xristis: DedomenaXristi = Depends(
        apaitisi_rolou(RolosXristi.YPEFTHYNOS_PORWN, RolosXristi.SYNTONISTIS_APOIKIAS)
    ),
) -> Dict[str, Any]:
    """Καταχωρίζει πρόγραμμα ανακύκλωσης νερού."""
    from backend.app.montela.poroi import DexameniNerou, ProgrammaAnakyklwsis

    id_prog = f"prog_anak_{uuid.uuid4().hex[:8]}"
    twrinos = datetime.now(timezone.utc)

    dexamenes = synedria.query(DexameniNerou).all()
    id_dexameni = dexamenes[0].id_dexamenis if dexamenes else "dexameni_01"

    programma = ProgrammaAnakyklwsis(
        id_programmatos=id_prog,
        id_dexamenis=id_dexameni,
        posotita_anakyklwsis_l=aitima.posotita_nerou_l * aitima.apodosi,
        xronos_enarksis=twrinos,
        diarkeia_lepta=60,
        apodosi_anakyklwsis=aitima.apodosi,
        katastasi="programmatismeno",
    )
    synedria.add(programma)
    synedria.commit()
    return {
        "id_programmatos": id_prog,
        "katastasi": "programmatismeno",
        "posotita_anakyklwsis_l": round(aitima.posotita_nerou_l * aitima.apodosi, 2),
        "minyma": "Το πρόγραμμα ανακύκλωσης καταχωρίστηκε επιτυχώς.",
    }


@router.get("/nero/anakyklwsi/programmata", summary="Ανάκτηση προγραμμάτων ανακύκλωσης (RES-12)")
def pare_programmata_anakyklwsis(
    synedria: Session = Depends(pare_synedria_vasis),
) -> List[Dict[str, Any]]:
    """Επιστρέφει όλα τα προγράμματα ανακύκλωσης."""
    from backend.app.apothikes.apothiki_porwn import ApothikiPorwn

    apothiki = ApothikiPorwn(synedria)
    programmata = apothiki.pare_programmata_anakyklwsis()
    return [
        {
            "id_programmatos": p.id_programmatos,
            "posotita_l": p.posotita_anakyklwsis_l,
            "xronos_enarksis": p.xronos_enarksis,
            "apodosi": p.apodosi_anakyklwsis,
            "katastasi": p.katastasi,
        }
        for p in programmata
    ]


@router.post(
    "/nero/anakyklwsi/programmata/{id_programmatos}/akyrosi", summary="Ακύρωση ανακύκλωσης (RES-12)"
)
def akyrosi_anakyklwsis(
    id_programmatos: str,
    synedria: Session = Depends(pare_synedria_vasis),
    xristis: DedomenaXristi = Depends(
        apaitisi_rolou(RolosXristi.YPEFTHYNOS_PORWN, RolosXristi.SYNTONISTIS_APOIKIAS)
    ),
) -> Dict[str, Any]:
    """Ακυρώνει πρόγραμμα ανακύκλωσης."""
    from backend.app.apothikes.apothiki_porwn import ApothikiPorwn

    apothiki = ApothikiPorwn(synedria)
    prog = apothiki.pare_programma_anakyklwsis_ana_id(id_programmatos)
    if not prog:
        raise SfalmaDomain(
            kodikos=KodikosSfalmatos.DEN_VRETHIKE,
            minyma=f"Το πρόγραμμα ανακύκλωσης '{id_programmatos}' δεν βρέθηκε.",
            katastasi_http=404,
        )
    prog.katastasi = "akyrothike"
    synedria.commit()
    return {"id_programmatos": id_programmatos, "katastasi": "akyrothike"}


# ============================================================================
# Ενέργεια, Φωτοβολταϊκά και Συσσωρευτές (RES-02, RES-04, RES-10, RES-14)
# ============================================================================


@router.get(
    "/energeia/katastasi",
    summary="Συνολική εικόνα παραγωγής, φορτίων και αυτονομίας (RES-02, RES-04)",
)
def pare_katastasi_energeias(synedria: Session = Depends(pare_synedria_vasis)) -> Dict[str, Any]:
    """Επιστρέφει συνοπτική παραγωγή, φορτία, έλλειμμα και αυτονομία μπαταριών."""
    ypiresia = YpiresiaPorwn(synedria)
    return ypiresia.pare_katastasi_energeias()


@router.get(
    "/energeia/fortia", summary="Αναλυτική κατανάλωση ανά εγκατάσταση και προτεραιότητα (RES-14)"
)
def pare_energeiaka_fortia(
    synedria: Session = Depends(pare_synedria_vasis),
) -> List[Dict[str, Any]]:
    """Επιστρέφει αναλυτικά τα ηλεκτρικά φορτία της αποικίας."""
    ypiresia = YpiresiaPorwn(synedria)
    return ypiresia.pare_analytika_fortia()


@router.get("/energeia/fwtovoltaika", summary="Τηλεμετρία φωτοβολταϊκών συστοιχιών (RES-02)")
def pare_fwtovoltaika(synedria: Session = Depends(pare_synedria_vasis)) -> List[Dict[str, Any]]:
    """Επιστρέφει επιφάνεια, G, f, απόδοση και παραγωγή ανά PV panel."""
    ypiresia = YpiresiaPorwn(synedria)
    return ypiresia.pare_katastasi_energeias()["paragwgi"]["fwtovoltaika"]


@router.get("/energeia/syssoreftes", summary="Κατάσταση και αποθέματα συσσωρευτών (RES-02)")
def pare_syssoreftes(synedria: Session = Depends(pare_synedria_vasis)) -> List[Dict[str, Any]]:
    """Επιστρέφει ενέργεια kWh, χωρητικότητα και εφεδρεία μπαταριών."""
    ypiresia = YpiresiaPorwn(synedria)
    return ypiresia.pare_katastasi_energeias()["sysswrefsi"]["syssoreftes"]


@router.post(
    "/energeia/periorismos-fortiwn/proepiskopisi",
    summary="Προεπισκόπηση επιπτώσεων παύσης αναβλητών φορτίων (RES-10)",
)
def proepiskopisi_periorismou_fortiwn(
    aitima: AitimaPeriorismouFortiwn,
    synedria: Session = Depends(pare_synedria_vasis),
) -> Dict[str, Any]:
    """Συγκρίνει την αυτονομία πριν και μετά την παύση αναβλητών φορτίων."""
    ypiresia = YpiresiaPorwn(synedria)
    return ypiresia.proepiskopisi_periorismou_fortiwn(pausi_anavlhtwn=aitima.pausi_anavlhtwn)


@router.post(
    "/energeia/periorismos-fortiwn/entoles",
    summary="Εκτέλεση περιορισμού φορτίων με έγκριση συντονιστή (RES-10)",
)
def ektelesi_periorismou_fortiwn(
    aitima: AitimaPeriorismouFortiwn,
    synedria: Session = Depends(pare_synedria_vasis),
    xristis: DedomenaXristi = Depends(apaitisi_rolou(RolosXristi.SYNTONISTIS_APOIKIAS)),
) -> Dict[str, Any]:
    """Εκτελεί την παύση των αναβλητών φορτίων (απαιτείται ρόλος coordinator)."""
    ypiresia = YpiresiaPorwn(synedria)
    return ypiresia.ektelesi_periorismou_fortiwn(
        pausi_anavlhtwn=aitima.pausi_anavlhtwn,
        xristis=xristis,
        aitiologia=aitima.aitiologia,
    )
