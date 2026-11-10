"""Διαδρομές σεναρίου καταιγίδας σκόνης και ελέγχου προσομοίωσης (STORM-01…10, CORE-13)."""

from typing import List, Literal, Optional

from fastapi import APIRouter, Depends, Header
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session

from backend.app.pyrinas.asfaleia import (
    DedomenaXristi,
    RolosXristi,
    apaitisi_rolou,
    pare_trexonta_xristi,
)
from backend.app.pyrinas.rythmiseis import rythmiseis
from backend.app.pyrinas.sfalmata import KodikosSfalmatos, SfalmaKanona
from backend.app.sxhmata.apantiseis import (
    ApofasiApantisi,
    EnergopoiisiSenariouApantisi,
    EpanaforaApantisi,
    IstorikoApofasisApantisi,
    KatastasiKataigidasApantisi,
    ProepiskopisiSenariouApantisi,
    VimaApantisi,
)
from backend.app.vasi.synthesi import pare_synedria_vasis
from backend.app.ypiresies.ypiresia_symvantwn_kai_senariwn import YpiresiaSymvantwnKaiSenariwn


def mono_anaptyxi():
    if rythmiseis.PERIVALLON not in {"anaptyxi", "dokimes"}:
        raise SfalmaKanona(
            KodikosSfalmatos.ANARMODIOS_XRISTIS,
            "Τα εργαλεία προσομοίωσης επιτρέπονται μόνο σε ανάπτυξη/δοκιμές.",
            403,
        )


def elegxe_senario(id_senariou):
    if id_senariou not in {"kataigida_skonis_2026", "kataigida-skonis"}:
        raise SfalmaKanona(KodikosSfalmatos.DEN_VRETHIKE, "Το σενάριο δεν βρέθηκε.", 404)


class AitimaEpanaforas(BaseModel):
    model_config = ConfigDict(extra="forbid")
    epivevaiwsi: Literal[True]


class AitimaEpivevaiwsisProepiskopisis(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id_proepiskopisis: str


dromologitis = APIRouter(tags=["Σενάρια & Προσομοίωση"])


class AitimaApofasisKataigidas(BaseModel):
    """Αίτημα έγκρισης απόφασης αντιμετώπισης καταιγίδας (STORM-06)."""

    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)
    id_proepiskopisis: str

    epilogi: str = Field(
        description="Επιλογή: kamia_allagi, pausi_anavlhtwn, asfalis_stasi_oximatos, syndyasmos_pliroys_asfaleias"
    )
    aitiologia: str = Field(min_length=5, description="Αιτιολόγηση απόφασης συντονιστή")


class AitimaVimatosXronou(BaseModel):
    """Αίτημα προώθησης χρόνου προσομοίωσης (CORE-13)."""

    model_config = ConfigDict(extra="forbid")

    lepta: int = Field(default=15, gt=0, le=1440)


@dromologitis.get(
    "/senaria/kataigida-skonis", summary="Κατάσταση του fixture καταιγίδας σκόνης (STORM-01)"
)
def pare_katastasi_kataigidas(
    synedria: Session = Depends(pare_synedria_vasis),
) -> KatastasiKataigidasApantisi:
    """Επιστρέφει την τρέχουσα κατάσταση και τις περιβαλλοντικές παραμέτρους της καταιγίδας."""
    from backend.app.montela.poroi import Fwtovoltaiko

    pv = synedria.get(Fwtovoltaiko, "pv_01")
    einai_energi = (pv.aktinovolia_w_m2 < 100.0) if pv else False
    return {
        "senario": "kataigida_skonis_2026",
        "katastasi": "energi" if einai_energi else "arxiki_katastasi",
        "aktinovolia_w_m2": pv.aktinovolia_w_m2 if pv else 300.0,
        "syntelestis_f": pv.syntelestis_epikathisis_f if pv else 0.8,
    }


@dromologitis.post(
    "/senaria/kataigida-skonis/proepiskopisi",
    summary="Προεπισκόπηση επιλογών καταιγίδας με υπολογισμούς Golden Fixture (§6, STORM-05)",
)
def proepiskopisi_kataigidas(
    synedria: Session = Depends(pare_synedria_vasis),
    xristis: DedomenaXristi = Depends(pare_trexonta_xristi),
) -> ProepiskopisiSenariouApantisi:
    """Υπολογίζει συγκριτικά όλες τις επιλογές (Baseline, Storm με/χωρίς αναβλητά, Rover ETA & Safe Stop)."""
    ypiresia = YpiresiaSymvantwnKaiSenariwn(synedria)
    return ypiresia.proepiskopisi_senariou_kataigidas(xristis)


@dromologitis.post(
    "/senaria/kataigida-skonis/energopoiisi",
    summary="Ενεργοποίηση συνθηκών καταιγίδας σκόνης (STORM-02)",
)
def energopoiisi_kataigidas(
    synedria: Session = Depends(pare_synedria_vasis),
    xristis: DedomenaXristi = Depends(apaitisi_rolou(RolosXristi.SYNTONISTIS_APOIKIAS)),
) -> EnergopoiisiSenariouApantisi:
    """Ενημερώνει G=80, f=0.5, T_exw=193 K, ορατότητα 100 m και παράγει συναγερμό."""
    mono_anaptyxi()
    ypiresia = YpiresiaSymvantwnKaiSenariwn(synedria)
    return ypiresia.energopoiisi_kataigidas(xristis)


@dromologitis.post(
    "/senaria/{id_senariou}/apofaseis/proepiskopisi",
    summary="Συγκρίσεις αποφάσεων σεναρίου (STORM-05)",
)
def proepiskopisi_apofasewn_senariou(
    id_senariou: str,
    xristis: DedomenaXristi = Depends(pare_trexonta_xristi),
    synedria: Session = Depends(pare_synedria_vasis),
) -> ProepiskopisiSenariouApantisi:
    """Επιστρέφει την ανάλυση κόστους/οφέλους των διαθέσιμων αποφάσεων."""
    elegxe_senario(id_senariou)
    ypiresia = YpiresiaSymvantwnKaiSenariwn(synedria)
    return ypiresia.proepiskopisi_senariou_kataigidas(xristis)


@dromologitis.post(
    "/senaria/{id_senariou}/apofaseis",
    summary="Υποβολή και έγκριση απόφασης συντονιστή για καταιγίδα (STORM-06, STORM-08)",
)
def ypovoli_apofasis_senariou(
    id_senariou: str,
    aitima: AitimaApofasisKataigidas,
    kleidi: Optional[str] = Header(default=None, alias="Idempotency-Key"),
    synedria: Session = Depends(pare_synedria_vasis),
    xristis: DedomenaXristi = Depends(apaitisi_rolou(RolosXristi.SYNTONISTIS_APOIKIAS)),
) -> ApofasiApantisi:
    """Εκτελεί την απόφαση διαχείρισης κρίσης (π.χ. curtailment, rover safe stop) και καταγράφει audit."""
    elegxe_senario(id_senariou)
    ypiresia = YpiresiaSymvantwnKaiSenariwn(synedria)
    return ypiresia.ypovoli_apofasis_kataigidas(
        epilogi=aitima.epilogi,
        aitiologia=aitima.aitiologia,
        xristis=xristis,
        id_proepiskopisis=aitima.id_proepiskopisis,
        kleidi=kleidi,
    )


@dromologitis.get(
    "/senaria/{id_senariou}/xronologio",
    summary="Χρονολόγιο και ιστορικό αποφάσεων σεναρίου (STORM-08)",
)
def pare_xronologio_senariou(
    id_senariou: str,
    synedria: Session = Depends(pare_synedria_vasis),
) -> list[IstorikoApofasisApantisi]:
    """Επιστρέφει τις αποφάσεις που εγκρίθηκαν και καταγράφηκαν για το συγκεκριμένο σενάριο."""
    elegxe_senario(id_senariou)
    from backend.app.montela.koinonika_symvanta import Apofasi

    apofaseis = (
        synedria.query(Apofasi)
        .filter(Apofasi.id_senariou == id_senariou)
        .order_by(Apofasi.xronos_apofasis.desc())
        .all()
    )
    return [
        {
            "id_apofasis": stoixeio_alfa.id_apofasis,
            "id_syntonisti": stoixeio_alfa.id_syntonisti,
            "epilogi": stoixeio_alfa.epilogi,
            "aitiologia": stoixeio_alfa.aitiologia,
            "egkekrimeni": stoixeio_alfa.egkekrimeni,
            "xronos_apofasis": stoixeio_alfa.xronos_apofasis,
        }
        for stoixeio_alfa in apofaseis
    ]


# --- Έλεγχος Προσομοίωσης (CORE-13) ---


@dromologitis.post(
    "/prosomoiwsi/vima", summary="Προώθηση προσομοιωμένου ρολογιού (Dev/Test only - CORE-13)"
)
def proxorise_prosomoiwsi(
    aitima: AitimaVimatosXronou,
    xristis: DedomenaXristi = Depends(apaitisi_rolou(RolosXristi.SYNTONISTIS_APOIKIAS)),
    perivallon=Depends(mono_anaptyxi),
    synedria: Session = Depends(pare_synedria_vasis),
) -> VimaApantisi:
    """Προχωρά το ρολόι της αποικίας κατά καθορισμένο αριθμό λεπτών."""
    ypiresia = YpiresiaSymvantwnKaiSenariwn(synedria)
    return ypiresia.proxorise_xrono(lepta=aitima.lepta, xristis=xristis)


@dromologitis.post(
    "/prosomoiwsi/epanafora", summary="Επαναφορά προσομοίωσης στα αρχικά δεδομένα (Dev/Test only)"
)
def epanafora_prosomoiwsis(
    aitima: AitimaEpanaforas,
    perivallon=Depends(mono_anaptyxi),
    synedria: Session = Depends(pare_synedria_vasis),
    xristis: DedomenaXristi = Depends(apaitisi_rolou(RolosXristi.SYNTONISTIS_APOIKIAS)),
) -> EpanaforaApantisi:
    """Επαναφέρει τις παραμέτρους στις κανονικές συνθήκες baseline."""
    from backend.app.arxika_dedomena.fortwsi_dedomenwn import arxikopoiisi_dedomenwn_epideiksis

    arxikopoiisi_dedomenwn_epideiksis(synedria, epanarxikopoiisi=True)
    return {"minyma": "Η προσομοίωση επανήλθε επιτυχώς στις αρχικές συνθήκες baseline."}


@dromologitis.post(
    "/senaria/prokathorismena/{kodikos}/energopoiisi", summary="Εκπαιδευτική αστοχία ή αποκατάσταση"
)
def energopoiise_prokathorismeno_senario(
    kodikos: str,
    synedria: Session = Depends(pare_synedria_vasis),
    xristis: DedomenaXristi = Depends(apaitisi_rolou(RolosXristi.SYNTONISTIS_APOIKIAS)),
    perivallon=Depends(mono_anaptyxi),
) -> EnergopoiisiSenariouApantisi:
    return YpiresiaSymvantwnKaiSenariwn(synedria).efarmose_prokathorismeno_senario(kodikos, xristis)


@dromologitis.get("/senaria/prokathorismena", summary="Διαθέσιμα εκπαιδευτικά σενάρια")
def prokathorismena_senaria() -> List[str]:
    return [
        "arxiki_katastasi",
        "kataigida_skonis_2026",
        "xamili_aktinovolia",
        "diarroi_nerou",
        "vlavi_aisthitira_oxygonou",
        "apoleia_epikoinwnias",
        "ypsili_aktinovolia",
        "proskrousi",
        "diarroi_atmosfairas",
        "apokatastasi",
    ]
