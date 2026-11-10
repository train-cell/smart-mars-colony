"""Ατομικές εντολές και μόνιμες, μοναδικές προεπισκοπήσεις.

Οι συναρτήσεις συμμετέχουν στη συναλλαγή του καλούντος και δεν κάνουν commit.
Το κλείδωμα λαμβάνεται πριν από την ανάγνωση της κατάστασης μιας μεταβολής.
"""

import hashlib
import json
import uuid
from datetime import datetime, timedelta, timezone

from fastapi.encoders import jsonable_encoder
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from backend.app.montela.koinonika_symvanta import (
    Entoli,
    IstorikoElegxou,
    KatastasiProsomoiwsis,
    Proepiskopisi,
    SymvanEntolis,
)
from backend.app.pyrinas.asfaleia import (
    DedomenaXristi,
    RolosXristi,
    elegxe_dikaiwma,
    pare_xristi_apo_vasi,
)
from backend.app.pyrinas.katagrafi import id_trexontos_aitimatos
from backend.app.pyrinas.rythmiseis import rythmiseis
from backend.app.pyrinas.sfalmata import KodikosSfalmatos, SfalmaKanona


def kanonikopoiise(dedomena: dict) -> dict:
    """Σταθερή JSON αναπαράσταση, με απόρριψη μη πεπερασμένων τιμών."""
    return json.loads(json.dumps(jsonable_encoder(dedomena), allow_nan=False, sort_keys=True))


def apotypwma(dedomena: dict) -> str:
    """Αποτύπωμα του πλήρους σώματος χωρίς εξάρτηση από σειρά πεδίων."""
    return hashlib.sha256(
        json.dumps(kanonikopoiise(dedomena), sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def pare_roloi(synedria: Session) -> KatastasiProsomoiwsis:
    """Ανακτά το αρχικοποιημένο εικονικό ρολόι."""
    roloi = synedria.get(KatastasiProsomoiwsis, 1)
    if roloi is None:
        raise SfalmaKanona(
            KodikosSfalmatos.MH_ASPHALIS_KATASTASI,
            "Η προσομοίωση δεν έχει αρχικοποιηθεί.",
            503,
        )
    return roloi


def kleidwse_synallagi(synedria: Session) -> None:
    """Σειριοποιεί κρίσιμα writes στη SQLite πριν από τον επανέλεγχο πόρων."""
    synedria.execute(
        update(KatastasiProsomoiwsis)
        .where(KatastasiProsomoiwsis.id_katastasis == 1)
        .values(ekdosi_katastasis=KatastasiProsomoiwsis.ekdosi_katastasis)
        .execution_options(synchronize_session=False)
    )
    synedria.expire_all()
    pare_roloi(synedria)


def dimiourgise_proepiskopisi(
    synedria: Session,
    drasi: str,
    id_ontotitas: str,
    xristis: DedomenaXristi,
    dedomena: dict,
    stigmiotypo: dict,
) -> dict:
    """Αποθηκεύει πρόταση χωρίς αλλαγή πόρων, με λήξη πραγματικού/εικονικού χρόνου."""
    roloi = pare_roloi(synedria)
    twra = datetime.now(timezone.utc)
    diarkeia = timedelta(minutes=rythmiseis.DIASTIMA_LIKSIS_PROEPISKOPISIS_LEPTA)
    apantisi = kanonikopoiise(dedomena)
    id_proepiskopisis = "proep_" + uuid.uuid4().hex
    apantisi.update(
        id_proepiskopisis=id_proepiskopisis,
        xronos_dimiourgias=twra.isoformat(),
        xronos_liksis_proepiskopisis=(twra + diarkeia).isoformat(),
        apaiteitai_epivevaiwsi=True,
    )
    synedria.add(
        Proepiskopisi(
            id_proepiskopisis=id_proepiskopisis,
            id_xristi=xristis.id_xristi,
            drasi=drasi,
            id_ontotitas=id_ontotitas,
            dedomena=apantisi,
            stigmiotypo=kanonikopoiise(stigmiotypo),
            katastasi="energi",
            epoxi_prosomoiwsis=roloi.epoxi_prosomoiwsis,
            xronos_dimiourgias=twra,
            xronos_liksis=twra + diarkeia,
            xronos_liksis_prosomoiwsis=roloi.xronos_prosomoiwsis + diarkeia,
        )
    )
    synedria.flush()
    return apantisi


def pare_proepiskopisi(
    synedria: Session,
    id_proepiskopisis: str,
    drasi: str,
    id_ontotitas: str,
    xristis: DedomenaXristi,
    stigmiotypo: dict | None = None,
) -> dict:
    """Ελέγχει ταυτότητα, στόχο, λήξη, εποχή και έκδοση του στιγμιοτύπου."""
    # Το HTTP dependency μπορεί να προηγήθηκε άλλης συναλλαγής ανάκλησης.
    # Επανέλεγχος από τη βάση μετά το writer lock, πριν από φυσική μεταβολή.
    roloi_drasewn = {
        "allagi_thermokrasias": RolosXristi.YPEFTHYNOS_YPOSTIRIKSIS_ZWIS,
        "thermokrasia": RolosXristi.YPEFTHYNOS_YPOSTIRIKSIS_ZWIS,
        "rythmisi_syskevis": RolosXristi.YPEFTHYNOS_YPOSTIRIKSIS_ZWIS,
        "programmatismos_ardefsis": RolosXristi.YPEFTHYNOS_PORWN,
        "programmatismos_fwtismou": RolosXristi.YPEFTHYNOS_PORWN,
        "programmatismos_anakyklwsis": RolosXristi.YPEFTHYNOS_PORWN,
        "periorismos_fortiwn": RolosXristi.SYNTONISTIS_APOIKIAS,
        "apofasi_kataigidas": RolosXristi.SYNTONISTIS_APOIKIAS,
        "anaklisi_oximatos": RolosXristi.YPEFTHYNOS_APOSTOLWN,
        "asfalis_stasi": RolosXristi.YPEFTHYNOS_APOSTOLWN,
        "dimiourgia_apostolis": RolosXristi.YPEFTHYNOS_APOSTOLWN,
    }
    egkyros_xristis = pare_xristi_apo_vasi(synedria, xristis.id_xristi, pedia={id_ontotitas})
    if drasi in roloi_drasewn:
        pedio = id_ontotitas
        if drasi == "rythmisi_syskevis":
            from backend.app.montela import SyskeviYpostiriksisZwis

            syskevi = synedria.get(SyskeviYpostiriksisZwis, id_ontotitas)
            pedio = syskevi.id_xwrou if syskevi else id_ontotitas
        elegxe_dikaiwma(egkyros_xristis, roloi_drasewn[drasi], id_ontotitas=pedio)
    proepiskopisi = synedria.get(Proepiskopisi, id_proepiskopisis)
    if proepiskopisi is None:
        raise SfalmaKanona(KodikosSfalmatos.DEN_VRETHIKE, "Η προεπισκόπηση δεν βρέθηκε.", 404)
    if proepiskopisi.id_xristi != xristis.id_xristi:
        raise SfalmaKanona(
            KodikosSfalmatos.ANARMODIOS_XRISTIS,
            "Η προεπισκόπηση ανήκει σε διαφορετικό χρήστη.",
            403,
        )
    if proepiskopisi.drasi != drasi or proepiskopisi.id_ontotitas != id_ontotitas:
        raise SfalmaKanona(
            KodikosSfalmatos.SYNTHIKI_SYGGROUSIS,
            "Η προεπισκόπηση αφορά διαφορετική ενέργεια ή οντότητα.",
            409,
        )
    roloi = pare_roloi(synedria)
    if (
        proepiskopisi.katastasi != "energi"
        or proepiskopisi.xronos_liksis <= datetime.now(timezone.utc)
        or proepiskopisi.xronos_liksis_prosomoiwsis <= roloi.xronos_prosomoiwsis
        or proepiskopisi.epoxi_prosomoiwsis != roloi.epoxi_prosomoiwsis
        or (stigmiotypo is not None and proepiskopisi.stigmiotypo != kanonikopoiise(stigmiotypo))
    ):
        raise SfalmaKanona(
            KodikosSfalmatos.PALIA_PROEPISKOPISI,
            "Η προεπισκόπηση έληξε, χρησιμοποιήθηκε ή αφορά παλαιότερη κατάσταση. Δημιουργήστε νέα.",
            409,
        )
    return dict(proepiskopisi.dedomena)


def katanalwse_proepiskopisi(synedria: Session, id_proepiskopisis: str) -> None:
    """Ατομική κατανάλωση μίας προεπισκόπησης μέσα στην ίδια συναλλαγή."""
    apotelesma = synedria.execute(
        update(Proepiskopisi)
        .where(
            Proepiskopisi.id_proepiskopisis == id_proepiskopisis,
            Proepiskopisi.katastasi == "energi",
        )
        .values(katastasi="xrisimopoiithike")
        .execution_options(synchronize_session=False)
    )
    if apotelesma.rowcount != 1:
        raise SfalmaKanona(
            KodikosSfalmatos.PALIA_PROEPISKOPISI,
            "Η προεπισκόπηση έχει ήδη επιβεβαιωθεί ή ακυρωθεί.",
            409,
        )


def kleidi_entolis(xristis: DedomenaXristi, drasi: str, id_ontotitas: str, kleidi: str) -> str:
    """Οριοθετεί το κλειδί μοναδικότητας ανά χρήστη, ενέργεια και στόχο."""
    if not isinstance(kleidi, str) or not kleidi.strip() or len(kleidi) > 100:
        raise SfalmaKanona(KodikosSfalmatos.AKYRI_TIMI, "Μη έγκυρο κλειδί μοναδικότητας.", 422)
    return apotypwma(
        {"xristis": xristis.id_xristi, "drasi": drasi, "ontotita": id_ontotitas, "kleidi": kleidi}
    )


def pare_epanalipsi(
    synedria: Session,
    xristis: DedomenaXristi,
    drasi: str,
    id_ontotitas: str,
    kleidi: str | None,
    dedomena: dict,
) -> dict | None:
    """Επιστρέφει την ίδια απόκριση ή απορρίπτει αλλαγμένο σώμα ίδιου κλειδιού."""
    if kleidi is None:
        return None
    onoma_kleidiou = kleidi_entolis(xristis, drasi, id_ontotitas, kleidi)
    entoli = synedria.scalar(
        select(Entoli).where(Entoli.id_aitimatos_monadikotitas == onoma_kleidiou)
    )
    if entoli is None:
        return None
    if entoli.apotypwma_aitimatos != apotypwma(dedomena):
        raise SfalmaKanona(
            KodikosSfalmatos.SYNTHIKI_SYGGROUSIS,
            "Το ίδιο κλειδί μοναδικότητας χρησιμοποιήθηκε με διαφορετικά δεδομένα.",
            409,
        )
    return dict(entoli.apotelesma)


def kataxwrise_entoli(
    synedria: Session,
    xristis: DedomenaXristi,
    yposystima: str,
    drasi: str,
    id_ontotitas: str,
    dedomena: dict,
    apotelesma: dict,
    katastasi: str = "oloklirothike",
    id_proepiskopisis: str | None = None,
    kleidi: str | None = None,
) -> Entoli:
    """Καταγράφει εντολή, συμβάν και audit χωρίς ανεξάρτητο commit."""
    id_entolis = "entoli_" + uuid.uuid4().hex
    twra = datetime.now(timezone.utc)
    apotelesma.setdefault("id_entolis", id_entolis)
    entoli = Entoli(
        id_entolis=id_entolis,
        id_xristi=xristis.id_xristi,
        rolos=xristis.vasikos_rolos.value,
        yposystima=yposystima,
        drasi=drasi,
        id_ontotitas=id_ontotitas,
        katastasi=katastasi,
        id_proepiskopisis=id_proepiskopisis,
        id_aitimatos_monadikotitas=(
            kleidi_entolis(xristis, drasi, id_ontotitas, kleidi) if kleidi is not None else None
        ),
        apotypwma_aitimatos=apotypwma(dedomena),
        dedomena_aitimatos=kanonikopoiise(dedomena),
        apotelesma=kanonikopoiise(apotelesma),
        xronos_ektelesis=twra if katastasi in {"oloklirothike", "apetyxe"} else None,
    )
    entoli.symvanta.append(
        SymvanEntolis(
            proigoumeni_katastasi="epivevaiwthike",
            nea_katastasi=katastasi,
            minyma="Καταχώριση επιβεβαιωμένης εντολής.",
            xronos_symvantos=twra,
        )
    )
    synedria.add(entoli)
    synedria.add(
        IstorikoElegxou(
            id_xristi=xristis.id_xristi,
            rolos=xristis.vasikos_rolos.value,
            energeia=drasi,
            ontotita=yposystima,
            id_ontotitas=id_ontotitas,
            palia_timi=None,
            nea_timi=kanonikopoiise(apotelesma),
            aitiologia=str(dedomena.get("aitiologia", "Επιβεβαίωση εντολής από χειριστή")),
            id_aitimatos=id_trexontos_aitimatos.get(),
            xronos_katagrafis=twra,
        )
    )
    synedria.flush()
    return entoli
