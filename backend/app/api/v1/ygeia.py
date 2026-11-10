"""Διαδρομές ελέγχου υγείας και μεταδεδομένων συστήματος (CORE-03)."""

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from backend.app.pyrinas.rythmiseis import rythmiseis
from backend.app.sxhmata.apantiseis import MetadedomenaApantisi, YgeiaApantisi
from backend.app.vasi.synthesi import pare_synedria_vasis

dromologitis = APIRouter(tags=["Υγεία & Μεταδεδομένα"])


@dromologitis.get("/ygeia", summary="Έλεγχος υγείας του backend και της βάσης SQLite")
def elegxos_ygeias(synedria: Session = Depends(pare_synedria_vasis)) -> YgeiaApantisi:
    """Επιστρέφει την κατάσταση λειτουργίας του API, της βάσης και της έκδοσης."""
    vasi_energi = False
    try:
        synedria.execute(text("SELECT 1"))
        vasi_energi = True
    except Exception:
        vasi_energi = False

    return {
        "katastasi": "leitourgiko" if vasi_energi else "sfalma_vasis",
        "efarmogi": rythmiseis.ONOMA_EFARMOGIS,
        "ekdosi": rythmiseis.EKDOSI,
        "perivallon": rythmiseis.PERIVALLON,
        "vasi_dedomenwn": "sqlite_energi" if vasi_energi else "provlima_syndesis",
    }


@dromologitis.get("/metadedomena", summary="Μεταδεδομένα, μονάδες μέτρησης και διαθέσιμα statuses")
def pare_metadedomena() -> MetadedomenaApantisi:
    """Επιστρέφει τις υποστηριζόμενες μονάδες SI, τα διαθέσιμα enums και συμβάσεις."""
    return {
        "monades_si": {
            "thermokrasia": "K",
            "piesi": "Pa",
            "isxys": "W",
            "energeia": "J",
            "ogkos": "m3",
            "apostasi": "m",
            "xronos": "s",
        },
        "praktikes_monades": {
            "thermokrasia": "°C",
            "piesi": "kPa",
            "isxys": "kW",
            "energeia": "kWh",
            "ogkos": "L",
            "xronos": "h",
        },
        "katastaseis_entolwn": [
            "programmatismeno",
            "se_anamoni",
            "anastoli",
            "protathike",
            "proepiskopithike",
            "epivevaiwthike",
            "apestali",
            "egkrithike",
            "se_exelixi",
            "oloklirothike",
            "apetyxe",
            "akyrothike",
            "avevaio",
        ],
        "roloi_xristwn": [
            "ypefthynos_ypostiriksis_zwis",
            "ypefthynos_porwn",
            "ypefthynos_apostolwn",
            "syntonistis_apoikias",
        ],
    }
