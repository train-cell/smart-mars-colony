"""Διαχείριση ταυτοποίησης, ρόλων και δικαιωμάτων (RBAC & Delegations).

Παρέχει εκπαιδευτική ασφάλεια χωρίς hardcoded passwords, με υποστήριξη
ελέγχου ρόλων και μεταβίβασης δικαιωμάτων (CORE-06, CORE-07, CORE-18).
"""

from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional

from fastapi import Depends, Header, Request
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.pyrinas.sfalmata import KodikosSfalmatos, SfalmaKanona
from backend.app.vasi.synthesi import pare_synedria_vasis


class RolosXristi(str, Enum):
    """Επίσημοι ρόλοι χρηστών της αποικίας."""

    YPEFTHYNOS_YPOSTIRIKSIS_ZWIS = "ypefthynos_ypostiriksis_zwis"
    YPEFTHYNOS_PORWN = "ypefthynos_porwn"
    YPEFTHYNOS_APOSTOLWN = "ypefthynos_apostolwn"
    SYNTONISTIS_APOIKIAS = "syntonistis_apoikias"


class DedomenaXristi(BaseModel):
    """Πληροφορίες ταυτοποιημένου χρήστη."""

    id_xristi: str
    onoma: str
    vasikos_rolos: RolosXristi
    energopoiimenos: bool = True
    energoi_roloi: List[RolosXristi] = Field(default_factory=list)
    vasikoi_roloi: List[RolosXristi] = Field(default_factory=list)
    metavivaseis: list[dict] = Field(default_factory=list)


# Προκαθορισμένοι εκπαιδευτικοί λογαριασμοί επίδειξης
XRISTES_EPIDEIKSIS = {
    "xristis_zwis": DedomenaXristi(
        id_xristi="xristis_zwis",
        onoma="Ελένη Ιωάννου (Υποστήριξη Ζωής)",
        vasikos_rolos=RolosXristi.YPEFTHYNOS_YPOSTIRIKSIS_ZWIS,
        energoi_roloi=[RolosXristi.YPEFTHYNOS_YPOSTIRIKSIS_ZWIS],
    ),
    "xristis_porwn": DedomenaXristi(
        id_xristi="xristis_porwn",
        onoma="Νίκος Παπαδόπουλος (Διαχείριση Πόρων)",
        vasikos_rolos=RolosXristi.YPEFTHYNOS_PORWN,
        energoi_roloi=[RolosXristi.YPEFTHYNOS_PORWN],
    ),
    "xristis_apostolwn": DedomenaXristi(
        id_xristi="xristis_apostolwn",
        onoma="Μαρία Γεωργίου (Επιχειρήσεις Rover)",
        vasikos_rolos=RolosXristi.YPEFTHYNOS_APOSTOLWN,
        energoi_roloi=[RolosXristi.YPEFTHYNOS_APOSTOLWN],
    ),
    "syntonistis": DedomenaXristi(
        id_xristi="syntonistis",
        onoma="Διοικητής Αποικίας (Συντονιστής)",
        vasikos_rolos=RolosXristi.SYNTONISTIS_APOIKIAS,
        energoi_roloi=[
            RolosXristi.SYNTONISTIS_APOIKIAS,
            RolosXristi.YPEFTHYNOS_YPOSTIRIKSIS_ZWIS,
            RolosXristi.YPEFTHYNOS_PORWN,
            RolosXristi.YPEFTHYNOS_APOSTOLWN,
        ],
    ),
}


def pare_xristi_apo_vasi(
    synedria: Session,
    id_xristi: str | None,
    rolos: str | None = None,
    pedia: set[str] | None = None,
) -> DedomenaXristi:
    """Ρητή εκπαιδευτική ταυτότητα και έγκυρα δικαιώματα από την ίδια βάση."""
    from backend.app.montela.xristes import AnathesiRolouXristi, MetavivasiDikaiwmatos, Xristis

    if id_xristi == "xeiristis_oximatos":
        id_xristi = "xristis_apostolwn"
    if rolos == "xeiristis_oximatos":
        rolos = RolosXristi.YPEFTHYNOS_APOSTOLWN.value
    if not id_xristi:
        raise SfalmaKanona(
            KodikosSfalmatos.APOUSIA_TAFTOTITAS,
            "Απαιτείται ρητή επιλογή χρήστη επίδειξης με X-Id-Xristi.",
            401,
        )
    eggrafi = synedria.get(Xristis, id_xristi)
    if eggrafi is None or not eggrafi.energos:
        raise SfalmaKanona(
            KodikosSfalmatos.APOUSIA_TAFTOTITAS, "Ο χρήστης δεν υπάρχει ή είναι ανενεργός.", 401
        )
    try:
        vasikos = RolosXristi(eggrafi.vasikos_rolos)
        vasikoi = {vasikos}
        for onoma_rolou in synedria.scalars(
            select(AnathesiRolouXristi.rolos).where(AnathesiRolouXristi.id_xristi == id_xristi)
        ):
            vasikoi.add(RolosXristi(onoma_rolou))
    except ValueError:
        raise SfalmaKanona(
            KodikosSfalmatos.ANARMODIOS_XRISTIS, "Μη έγκυρη ανάθεση ρόλου στη βάση.", 403
        )
    twra = datetime.now(timezone.utc)
    metavivaseis = list(
        synedria.scalars(
            select(MetavivasiDikaiwmatos).where(
                MetavivasiDikaiwmatos.id_paralipti == id_xristi,
                MetavivasiDikaiwmatos.energo.is_(True),
                MetavivasiDikaiwmatos.xronos_enarksis <= twra,
                MetavivasiDikaiwmatos.xronos_liksis > twra,
                MetavivasiDikaiwmatos.xronos_anaklisis.is_(None),
            )
        )
    )
    energoi = set(vasikoi)
    egkyres = []
    for metavivasi in metavivaseis:
        try:
            neos_rolos = RolosXristi(metavivasi.rolos)
        except ValueError:
            continue
        egkyres.append({"rolos": neos_rolos.value, "pedio_efarmogis": metavivasi.pedio_efarmogis})
        if metavivasi.pedio_efarmogis == "geniko" or metavivasi.pedio_efarmogis in (pedia or set()):
            energoi.add(neos_rolos)
    if rolos:
        try:
            zitoumenos = RolosXristi(rolos)
        except ValueError:
            raise SfalmaKanona(KodikosSfalmatos.AKYRI_TIMI, "Μη έγκυρος ζητούμενος ρόλος.", 400)
        if zitoumenos not in energoi and vasikos != RolosXristi.SYNTONISTIS_APOIKIAS:
            raise SfalmaKanona(
                KodikosSfalmatos.ANARMODIOS_XRISTIS,
                "Ο ζητούμενος ρόλος δεν ισχύει για την οντότητα.",
                403,
            )
    return DedomenaXristi(
        id_xristi=eggrafi.id_xristi,
        onoma=eggrafi.onoma,
        vasikos_rolos=vasikos,
        energopoiimenos=True,
        vasikoi_roloi=sorted(vasikoi, key=lambda timi: timi.value),
        energoi_roloi=sorted(energoi, key=lambda timi: timi.value),
        metavivaseis=egkyres,
    )


def pare_trexonta_xristi(
    aitima_http: Request,
    x_id_xristi: Optional[str] = Header(default=None, alias="X-Id-Xristi"),
    x_rolos: Optional[str] = Header(default=None, alias="X-Rolos"),
    synedria: Session = Depends(pare_synedria_vasis),
) -> DedomenaXristi:
    """Η ταυτότητα επιλέγεται ρητά· άγνωστο ID δεν αποκτά προνόμια."""
    pedia = {str(timi) for timi in aitima_http.path_params.values()}
    if "/xwroi-katoikisis" in aitima_http.url.path:
        pedia.add("ypostiriksi_zwis")
    if any(tmima in aitima_http.url.path for tmima in ["/thermokipia", "/nero", "/energeia"]):
        pedia.add("poroi")
    if "/oximata" in aitima_http.url.path:
        pedia.add("apostoles")
    return pare_xristi_apo_vasi(synedria, x_id_xristi, x_rolos, pedia)


def elegxe_dikaiwma(
    xristis: DedomenaXristi,
    *apaitoumenoi_roloi: RolosXristi,
    id_ontotitas: str | None = None,
) -> None:
    """Επανελέγχει ρόλο και πεδίο όταν ο στόχος προκύπτει από αποθηκευμένα δεδομένα."""
    if not xristis.energopoiimenos:
        raise SfalmaKanona(KodikosSfalmatos.APOUSIA_TAFTOTITAS, "Ο χρήστης είναι ανενεργός.", 401)
    if xristis.vasikos_rolos == RolosXristi.SYNTONISTIS_APOIKIAS:
        return
    # Σε άμεση κλήση εκπαιδευτικού χρήστη χωρίς στοιχεία βάσης διατηρείται ο βασικός ρόλος.
    vasikoi = set(xristis.vasikoi_roloi or [xristis.vasikos_rolos])
    if any(rolos in vasikoi for rolos in apaitoumenoi_roloi):
        return
    if id_ontotitas is None and any(rolos in xristis.energoi_roloi for rolos in apaitoumenoi_roloi):
        return
    pedia_rolwn = {
        RolosXristi.YPEFTHYNOS_YPOSTIRIKSIS_ZWIS: "ypostiriksi_zwis",
        RolosXristi.YPEFTHYNOS_PORWN: "poroi",
        RolosXristi.YPEFTHYNOS_APOSTOLWN: "apostoles",
    }
    for metavivasi in xristis.metavivaseis:
        if metavivasi["rolos"] in [rolos.value for rolos in apaitoumenoi_roloi] and metavivasi[
            "pedio_efarmogis"
        ] in {"geniko", id_ontotitas, *(pedia_rolwn.get(rolos) for rolos in apaitoumenoi_roloi)}:
            return
    raise SfalmaKanona(
        KodikosSfalmatos.ANARMODIOS_XRISTIS,
        "Ο χρήστης δεν διαθέτει δικαίωμα για αυτή την ενέργεια και οντότητα.",
        403,
    )


def apaitisi_rolou(*apaitoumenoi_roloi: RolosXristi):
    """Εξάρτηση FastAPI που αξιολογεί τους ρόλους και τις τρέχουσες μεταβιβάσεις."""

    def elegxos(xristis: DedomenaXristi = Depends(pare_trexonta_xristi)) -> DedomenaXristi:
        elegxe_dikaiwma(xristis, *apaitoumenoi_roloi)
        return xristis

    return elegxos
