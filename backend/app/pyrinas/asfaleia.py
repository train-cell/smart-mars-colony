"""Διαχείριση ταυτοποίησης, ρόλων και δικαιωμάτων (RBAC & Delegations).

Παρέχει εκπαιδευτική ασφάλεια χωρίς hardcoded passwords, με υποστήριξη
ελέγχου ρόλων και μεταβίβασης δικαιωμάτων (CORE-06, CORE-07, CORE-18).
"""

from enum import Enum
from typing import List, Optional

from fastapi import Header
from pydantic import BaseModel, Field

from backend.app.pyrinas.sfalmata import KodikosSfalmatos, SfalmaDomain


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
    energpoiimenos: bool = True
    energoi_roloi: List[RolosXristi] = Field(default_factory=list)


# Προκαθορισμένοι εκπαιδευτικοί λογαριασμοί επίδειξης
XRHSTES_DEMO = {
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


def pare_trexonta_xristi(
    x_id_xristi: Optional[str] = Header(default=None, alias="X-Id-Xristi"),
    x_rolos: Optional[str] = Header(default=None, alias="X-Rolos"),
) -> DedomenaXristi:
    """Εξάγει τον τρέχοντα χρήστη από τα headers του αιτήματος.

    Αν δεν δοθεί header, προεπιλέγεται ο λογαριασμός συντονιστή για ευκολία τοπικού ελέγχου.
    """
    if x_id_xristi and x_id_xristi in XRHSTES_DEMO:
        xristis = XRHSTES_DEMO[x_id_xristi]
        # Εάν οριστεί ρητά πρόσθετος ρόλος μέσω header, ελέγχεται αν είναι έγκυρος
        if x_rolos:
            try:
                rolos_enum = RolosXristi(x_rolos)
                if rolos_enum not in xristis.energoi_roloi:
                    # Εάν δεν είναι συντονιστής, δεν επιτρέπεται αυθαίρετη ανάληψη ρόλου
                    if xristis.vasikos_rolos != RolosXristi.SYNTONISTIS_APOIKIAS:
                        raise SfalmaDomain(
                            kodikos=KodikosSfalmatos.ANARMODIOS_XRISTIS,
                            minyma="Ο χρήστης δεν διαθέτει τον ζητούμενο ρόλο.",
                            katastasi_http=403,
                        )
            except ValueError:
                raise SfalmaDomain(
                    kodikos=KodikosSfalmatos.AKYRI_TIMI,
                    minyma=f"Μη έγκυρος ρόλος: {x_rolos}",
                    katastasi_http=400,
                )
        return xristis

    if x_rolos:
        try:
            rolos_enum = RolosXristi(x_rolos)
            # Αναζήτηση ταιριαστού demo χρήστη
            for demo_x in XRHSTES_DEMO.values():
                if demo_x.vasikos_rolos == rolos_enum:
                    return demo_x
        except ValueError:
            raise SfalmaDomain(
                kodikos=KodikosSfalmatos.AKYRI_TIMI,
                minyma=f"Μη έγκυρος ρόλος: {x_rolos}",
                katastasi_http=400,
            )

    # Προεπιλογή: syntonistis για πλήρη διαγνωστική πρόσβαση
    return XRHSTES_DEMO["syntonistis"]


def apaitisi_rolou(*apaitoumenoi_roloi: RolosXristi):
    """FastAPI dependency factory για έλεγχο εξουσιοδότησης ρόλου."""

    def elegxos(
        x_id_xristi: Optional[str] = Header(default=None, alias="X-Id-Xristi"),
        x_rolos: Optional[str] = Header(default=None, alias="X-Rolos"),
    ) -> DedomenaXristi:
        energos_xristis = pare_trexonta_xristi(x_id_xristi=x_id_xristi, x_rolos=x_rolos)

        # Ο συντονιστής αποικίας έχει καθολική πρόσβαση σε όλες τις λειτουργίες
        if energos_xristis.vasikos_rolos == RolosXristi.SYNTONISTIS_APOIKIAS:
            return energos_xristis

        for rolos in apaitoumenoi_roloi:
            if rolos in energos_xristis.energoi_roloi or rolos == energos_xristis.vasikos_rolos:
                return energos_xristis

        raise SfalmaDomain(
            kodikos=KodikosSfalmatos.ANARMODIOS_XRISTIS,
            minyma=f"Απαιτείται ένας από τους ρόλους: {[r.value for r in apaitoumenoi_roloi]}",
            katastasi_http=403,
            leptomereies={
                "id_xristi": energos_xristis.id_xristi,
                "rolos": energos_xristis.vasikos_rolos.value,
            },
        )

    return elegxos
