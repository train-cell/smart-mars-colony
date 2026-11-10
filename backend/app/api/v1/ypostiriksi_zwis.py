"""Διαδρομές υποσυστήματος Α: υποστήριξη ζωής, ατμόσφαιρα και έλεγχος θερμοκρασίας (LIFE-01…10)."""

from typing import Optional

from fastapi import APIRouter, Depends, Header
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session

from backend.app.pyrinas.asfaleia import (
    DedomenaXristi,
    RolosXristi,
    apaitisi_rolou,
    pare_trexonta_xristi,
)
from backend.app.pyrinas.sfalmata import KodikosSfalmatos, SfalmaKanona
from backend.app.sxhmata.apantiseis import (
    AkyrosiEntolisApantisi,
    EntoliPlirisApantisi,
    EpivevaiwsiSyskevisApantisi,
    EpivevaiwsiThermokrasiasApantisi,
    KatastasiXwrouApantisi,
    OxygonoApantisi,
    ProepiskopisiSyskevisApantisi,
    ProepiskopisiThermokrasiasApantisi,
    XwrosApantisi,
)
from backend.app.vasi.synthesi import pare_synedria_vasis
from backend.app.ypiresies.ypiresia_ypostiriksis_zwis import YpiresiaYpostiriksisZwis

dromologitis = APIRouter(tags=["Υποστήριξη Ζωής (Υποσύστημα Α)"])


class AitimaProepiskopisisThermokrasias(BaseModel):
    """Αίτημα προεπισκόπησης αλλαγής επιθυμητής θερμοκρασίας (§7, LIFE-06)."""

    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)

    epithymiti_thermokrasia_k: float = Field(gt=0, description="Επιθυμητή θερμοκρασία σε Kelvin")
    anamenomeni_ekdosi_katastasis: int = Field(
        ge=0, description="Αναμενόμενη έκδοση για optimistic lock"
    )


class AitimaEpivevaiwsisThermokrasias(BaseModel):
    """Αίτημα επιβεβαίωσης εντολής αλλαγής θερμοκρασίας (LIFE-07)."""

    model_config = ConfigDict(extra="forbid")

    id_proepiskopisis: str = Field(description="Το ID της εγκεκριμένης προεπισκόπησης")
    anamenomeni_ekdosi_katastasis: int = Field(ge=0)


class AitimaRythmisisSyskevis(BaseModel):
    """Επιλογή ενεργοποίησης τοπικής συσκευής υποστήριξης ζωής."""

    model_config = ConfigDict(extra="forbid")
    energopoiisi: bool
    aitiologia: str = Field(min_length=5, max_length=1000)


class AitimaEpivevaiwsisSyskevis(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id_proepiskopisis: str


@dromologitis.get(
    "/xwroi-katoikisis", summary="Λίστα κατοικήσιμων χώρων και βασικών μετρήσεων (LIFE-01)"
)
def pare_xwrous_katoikisis(
    synedria: Session = Depends(pare_synedria_vasis),
) -> list[XwrosApantisi]:
    """Επιστρέφει όλους τους θαλάμους διαβίωσης της αποικίας."""
    ypiresia = YpiresiaYpostiriksisZwis(synedria)
    return ypiresia.pare_xwrous()


@dromologitis.get(
    "/xwroi-katoikisis/{id_xwrou}/katastasi",
    summary="Πλήρες snapshot υποστήριξης ζωής θαλάμου (LIFE-02, LIFE-03)",
)
def pare_katastasi_xwrou(
    id_xwrou: str,
    synedria: Session = Depends(pare_synedria_vasis),
) -> KatastasiXwrouApantisi:
    """Επιστρέφει εσωτερική/εξωτερική θερμοκρασία, πιέσεις, O2, CO2, υγρασία και εξοπλισμό."""
    ypiresia = YpiresiaYpostiriksisZwis(synedria)
    return ypiresia.pare_katastasi_xwrou(id_xwrou)


@dromologitis.get(
    "/xwroi-katoikisis/{id_xwrou}/provlepsi-oxygonou",
    summary="Πρόβλεψη οξυγόνου και εκτίμηση αυτονομίας (LIFE-04)",
)
def pare_provlepsi_oxygonou(
    id_xwrou: str,
    synedria: Session = Depends(pare_synedria_vasis),
) -> OxygonoApantisi:
    """Επιστρέφει τη μερική πίεση O2, τη διαθέσιμη μάζα πάνω από το κατώφλι και την αυτονομία σε ώρες."""
    ypiresia = YpiresiaYpostiriksisZwis(synedria)
    return ypiresia.provlepsi_oxygonou(id_xwrou)


@dromologitis.post(
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
) -> ProepiskopisiThermokrasiasApantisi:
    """Υπολογίζει μη μεταλλακτικά τη μεταβολή ισχύος θέρμανσης [W] και επιστρέφει snapshot επιβεβαίωσης."""
    ypiresia = YpiresiaYpostiriksisZwis(synedria)
    return ypiresia.proepiskopisi_allagis_thermokrasias(
        id_xwrou=id_xwrou,
        epithymiti_thermokrasia_k=aitima.epithymiti_thermokrasia_k,
        anamenomeni_ekdosi_katastasis=aitima.anamenomeni_ekdosi_katastasis,
        xristis=xristis,
    )


@dromologitis.post(
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
    kleidi_monadikotitas: Optional[str] = Header(default=None, alias="Idempotency-Key"),
) -> EpivevaiwsiThermokrasiasApantisi:
    """Επιβεβαιώνει την προεπισκόπηση και ενημερώνει τον στόχο θερμοκρασίας και το audit log."""
    ypiresia = YpiresiaYpostiriksisZwis(synedria)
    return ypiresia.ektelesi_allagis_thermokrasias(
        id_xwrou=id_xwrou,
        id_proepiskopisis=aitima.id_proepiskopisis,
        anamenomeni_ekdosi_katastasis=aitima.anamenomeni_ekdosi_katastasis,
        xristis=xristis,
        id_aitimatos_monadikotitas=kleidi_monadikotitas,
    )


# --- Εντολές Lifecycle (CORE-10, CORE-19) ---


@dromologitis.get(
    "/entoles/{id_entolis}", summary="Ανάκτηση κατάστασης και κύκλου ζωής εντολής (CORE-10)"
)
def pare_entoli(
    id_entolis: str,
    synedria: Session = Depends(pare_synedria_vasis),
) -> EntoliPlirisApantisi:
    """Επιστρέφει την κατάσταση, τα συμβάντα και το αποτέλεσμα μιας εκτελεσθείσας εντολής."""
    from backend.app.apothikes.apothiki_koinwn import ApothikiKoinwn

    apothiki = ApothikiKoinwn(synedria)
    entoli = apothiki.pare_entoli_ana_id(id_entolis)
    if not entoli:
        raise SfalmaKanona(
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
                "proigoumeni": stoixeio_sigma.proigoumeni_katastasi,
                "nea": stoixeio_sigma.nea_katastasi,
                "minyma": stoixeio_sigma.minyma,
                "xronos": stoixeio_sigma.xronos_symvantos,
            }
            for stoixeio_sigma in entoli.symvanta
        ],
    }


@dromologitis.post(
    "/entoles/{id_entolis}/akyrosi", summary="Ακύρωση εντολής εφόσον επιτρέπεται (CORE-10)"
)
def akyrosi_entolis(
    id_entolis: str,
    synedria: Session = Depends(pare_synedria_vasis),
    xristis: DedomenaXristi = Depends(pare_trexonta_xristi),
) -> AkyrosiEntolisApantisi:
    """Ακυρώνει εντολή που βρίσκεται σε εκκρεμή ή αναστρέψιμη κατάσταση."""
    from backend.app.apothikes.apothiki_koinwn import ApothikiKoinwn

    apothiki = ApothikiKoinwn(synedria)
    entoli = apothiki.pare_entoli_ana_id(id_entolis)
    if not entoli:
        raise SfalmaKanona(
            kodikos=KodikosSfalmatos.DEN_VRETHIKE,
            minyma=f"Η εντολή '{id_entolis}' δεν βρέθηκε.",
            katastasi_http=404,
        )

    from datetime import datetime, timezone

    from backend.app.montela.koinonika_symvanta import SymvanEntolis
    from backend.app.montela.poroi import ProgrammaAnakyklwsis, ProgrammaArdefsis, ProgrammaFwtismou
    from backend.app.ypiresies.entoles_kai_proepiskopiseis import kleidwse_synallagi

    kleidwse_synallagi(synedria)
    synedria.refresh(entoli)
    if (
        entoli.id_xristi != xristis.id_xristi
        and xristis.vasikos_rolos != RolosXristi.SYNTONISTIS_APOIKIAS
    ):
        raise SfalmaKanona(
            KodikosSfalmatos.ANARMODIOS_XRISTIS,
            "Δεν επιτρέπεται ακύρωση εντολής άλλου χρήστη.",
            403,
        )
    if entoli.katastasi not in {"programmatismeno", "se_anamoni", "egkrithike"}:
        raise SfalmaKanona(
            KodikosSfalmatos.MH_EPITREPTI_METAVASI,
            "Η εντολή εκτελέστηκε ή δεν επιτρέπεται πλέον ασφαλής ακύρωση. Χρειάζεται νέα εντολή ανάκαμψης.",
            409,
        )
    if entoli.yposystima == "apostoles":
        raise SfalmaKanona(
            KodikosSfalmatos.MH_EPITREPTI_METAVASI,
            "Η εντολή οχήματος χρειάζεται τη ροή αναβολής ή νέα ασφαλή στάση και επιβεβαίωση τηλεμετρίας.",
            409,
        )
    from backend.app.pyrinas.asfaleia import elegxe_dikaiwma

    rolos_entolis = {
        "poroi": RolosXristi.YPEFTHYNOS_PORWN,
        "ypostiriksi_zwis": RolosXristi.YPEFTHYNOS_YPOSTIRIKSIS_ZWIS,
    }.get(entoli.yposystima)
    if rolos_entolis:
        elegxe_dikaiwma(xristis, rolos_entolis, id_ontotitas=entoli.id_ontotitas)
    proigoumeni = entoli.katastasi
    for montelo in (ProgrammaArdefsis, ProgrammaAnakyklwsis, ProgrammaFwtismou):
        programma = synedria.query(montelo).filter(montelo.id_entolis == id_entolis).first()
        if programma:
            if programma.katastasi != "programmatismeno":
                raise SfalmaKanona(
                    KodikosSfalmatos.MH_EPITREPTI_METAVASI, "Το πρόγραμμα έχει ήδη αρχίσει.", 409
                )
            programma.katastasi = "akyrothike"
    entoli.katastasi = "akyrothike"
    entoli.symvanta.append(
        SymvanEntolis(
            proigoumeni_katastasi=proigoumeni,
            nea_katastasi="akyrothike",
            minyma="Ακύρωση πριν από την εκτέλεση.",
            xronos_symvantos=datetime.now(timezone.utc),
        )
    )
    apothiki.kataxwrise_istoriko_elegxou(
        xristis.id_xristi,
        xristis.vasikos_rolos.value,
        "akyrosi_entolis",
        "entoles",
        id_entolis,
        {"katastasi": proigoumeni},
        {"katastasi": "akyrothike"},
        "Ακύρωση από εξουσιοδοτημένο χειριστή",
    )
    synedria.commit()
    return {
        "id_entolis": id_entolis,
        "katastasi": "akyrothike",
        "minyma": "Η εντολή ακυρώθηκε πριν από την εκτέλεσή της.",
    }


@dromologitis.post(
    "/xwroi-katoikisis/{id_xwrou}/syskeves/{id_syskevis}/proepiskopisi",
    summary="Προεπισκόπηση θέρμανσης, καθαριστή αέρα ή παραγωγής οξυγόνου",
)
def proepiskopisi_syskevis(
    id_xwrou: str,
    id_syskevis: str,
    aitima: AitimaRythmisisSyskevis,
    synedria: Session = Depends(pare_synedria_vasis),
    xristis: DedomenaXristi = Depends(
        apaitisi_rolou(RolosXristi.YPEFTHYNOS_YPOSTIRIKSIS_ZWIS, RolosXristi.SYNTONISTIS_APOIKIAS)
    ),
) -> ProepiskopisiSyskevisApantisi:
    from backend.app.montela import SyskeviYpostiriksisZwis
    from backend.app.ypiresies.entoles_kai_proepiskopiseis import dimiourgise_proepiskopisi

    syskevi = synedria.get(SyskeviYpostiriksisZwis, id_syskevis)
    if not syskevi or syskevi.id_xwrou != id_xwrou:
        raise SfalmaKanona(
            KodikosSfalmatos.DEN_VRETHIKE, "Η συσκευή δεν ανήκει στον επιλεγμένο χώρο.", 404
        )
    stigmiotypo = {
        "katastasi": syskevi.katastasi_leitourgias,
        "isxys_w": syskevi.katanalwsi_isxyos_w,
    }
    apantisi = dimiourgise_proepiskopisi(
        synedria,
        "rythmisi_syskevis",
        id_syskevis,
        xristis,
        {
            "id_xwrou": id_xwrou,
            "id_syskevis": id_syskevis,
            "energopoiisi": aitima.energopoiisi,
            "aitiologia": aitima.aitiologia,
            "isxys_w": syskevi.katanalwsi_isxyos_w,
            "proeidopoiiseis": []
            if aitima.energopoiisi
            else [
                "Η απενεργοποίηση μειώνει τη διαθεσιμότητα υποστήριξης ζωής και ενεργοποιεί προειδοποίηση."
            ],
        },
        stigmiotypo,
    )
    synedria.commit()
    return apantisi


@dromologitis.post(
    "/xwroi-katoikisis/{id_xwrou}/syskeves/{id_syskevis}/entoles",
    summary="Επιβεβαίωση ρύθμισης εξοπλισμού υποστήριξης ζωής",
)
def epivevaiwsi_syskevis(
    id_xwrou: str,
    id_syskevis: str,
    aitima: AitimaEpivevaiwsisSyskevis,
    synedria: Session = Depends(pare_synedria_vasis),
    xristis: DedomenaXristi = Depends(
        apaitisi_rolou(RolosXristi.YPEFTHYNOS_YPOSTIRIKSIS_ZWIS, RolosXristi.SYNTONISTIS_APOIKIAS)
    ),
    kleidi: Optional[str] = Header(default=None, alias="Idempotency-Key"),
) -> EpivevaiwsiSyskevisApantisi:
    from sqlalchemy import select

    from backend.app.montela import EnergeiakoFortio, SyskeviYpostiriksisZwis
    from backend.app.ypiresies.entoles_kai_proepiskopiseis import (
        katanalwse_proepiskopisi,
        kataxwrise_entoli,
        kleidwse_synallagi,
        pare_epanalipsi,
        pare_proepiskopisi,
    )
    from backend.app.ypiresies.synagermoi_kai_synthikes import enimerwse_synagermous

    kleidwse_synallagi(synedria)
    dedomena = aitima.model_dump()
    epanalipsi = pare_epanalipsi(
        synedria, xristis, "rythmisi_syskevis", id_syskevis, kleidi, dedomena
    )
    if epanalipsi is not None:
        return epanalipsi
    syskevi = synedria.get(SyskeviYpostiriksisZwis, id_syskevis)
    if not syskevi or syskevi.id_xwrou != id_xwrou:
        raise SfalmaKanona(
            KodikosSfalmatos.DEN_VRETHIKE, "Η συσκευή δεν ανήκει στον επιλεγμένο χώρο.", 404
        )
    proep = pare_proepiskopisi(
        synedria,
        aitima.id_proepiskopisis,
        "rythmisi_syskevis",
        id_syskevis,
        xristis,
        {"katastasi": syskevi.katastasi_leitourgias, "isxys_w": syskevi.katanalwsi_isxyos_w},
    )
    katanalwse_proepiskopisi(synedria, aitima.id_proepiskopisis)
    syskevi.katastasi_leitourgias = "energi" if proep["energopoiisi"] else "anenergi"
    if syskevi.typos_syskevis == "thermantiras":
        synedria.get(EnergeiakoFortio, "fortio_thermansis").energo = proep["energopoiisi"]
    else:
        synedria.flush()
        synedria.get(EnergeiakoFortio, "fortio_krisimo_loipo").isxys_kw = 1.2 + sum(
            stoixeio_sigma.katanalwsi_isxyos_w / 1000
            for stoixeio_sigma in synedria.scalars(select(SyskeviYpostiriksisZwis))
            if stoixeio_sigma.typos_syskevis != "thermantiras"
            and stoixeio_sigma.katastasi_leitourgias == "energi"
        )
    apantisi = {
        "id_syskevis": id_syskevis,
        "katastasi": "oloklirothike",
        "katastasi_syskevis": syskevi.katastasi_leitourgias,
        "minyma": "Η τοπική συσκευή επιβεβαίωσε τη ρύθμιση.",
    }
    kataxwrise_entoli(
        synedria,
        xristis,
        "ypostiriksi_zwis",
        "rythmisi_syskevis",
        id_syskevis,
        dedomena,
        apantisi,
        id_proepiskopisis=aitima.id_proepiskopisis,
        kleidi=kleidi,
    )
    enimerwse_synagermous(synedria)
    synedria.commit()
    return apantisi
