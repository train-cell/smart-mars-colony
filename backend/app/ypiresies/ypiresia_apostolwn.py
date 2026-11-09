"""Επιχειρησιακή λογική για οχήματα εξερεύνησης (rover), αποστολές και κινδύνους (MISSION-01 έως MISSION-08)."""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List

from sqlalchemy.orm import Session

from backend.app.apothikes.apothiki_apostolwn import ApothikiApostolwn
from backend.app.apothikes.apothiki_koinwn import ApothikiKoinwn
from backend.app.fysika_montela.fysika_montela import (
    ypologise_xrono_epistrofis_kai_asfaleia,
)
from backend.app.montela.koinonika_symvanta import Entoli
from backend.app.pyrinas.asfaleia import DedomenaXristi
from backend.app.pyrinas.sfalmata import KodikosSfalmatos, SfalmaDomain


class YpiresiaApostolwn:
    """Υπηρεσία διαχείρισης οχημάτων rover και αποστολών εξερεύνησης."""

    def __init__(self, synedria: Session):
        self.synedria = synedria
        self.apothiki_apostolwn = ApothikiApostolwn(synedria)
        self.apothiki_koinwn = ApothikiKoinwn(synedria)

    def pare_oximata(self) -> List[Dict[str, Any]]:
        """Επιστρέφει λίστα όλων των ενεργών rover (MISSION-02)."""
        oximata = self.apothiki_apostolwn.pare_oximata()
        return [
            {
                "id_oximatos": o.id_oximatos,
                "onoma": o.onoma,
                "maza_kg": o.maza_kg,
                "apostasi_apo_vasi_km": o.apostasi_apo_vasi_km,
                "taxytita_kmh": o.taxytita_kmh,
                "energeia_kwh": o.energeia_kwh,
                "efedreia_kwh": o.efedreia_kwh,
                "mesi_isxys_kw": o.mesi_isxys_kw,
                "katastasi_oximatos": o.katastasi_oximatos,
                "katastasi_epikoinwnias": o.katastasi_epikoinwnias,
                "ekdosi_katastasis": o.ekdosi_katastasis,
            }
            for o in oximata
        ]

    def pare_katastasi_oximatos(self, id_oximatos: str) -> Dict[str, Any]:
        """Πλήρης τηλεμετρία και κατάσταση ενός rover."""
        oxima = self.apothiki_apostolwn.pare_oxima_ana_id(id_oximatos)
        if not oxima:
            raise SfalmaDomain(
                kodikos=KodikosSfalmatos.DEN_VRETHIKE,
                minyma=f"Το όχημα '{id_oximatos}' δεν βρέθηκε.",
                katastasi_http=404,
            )

        apostoles = self.apothiki_apostolwn.pare_apostoles_oximatos(id_oximatos)

        return {
            "id_oximatos": oxima.id_oximatos,
            "onoma": oxima.onoma,
            "kinisi": {
                "apostasi_km": oxima.apostasi_apo_vasi_km,
                "taxytita_kmh": oxima.taxytita_kmh,
                "katastasi": oxima.katastasi_oximatos,
            },
            "energeia": {
                "trexousa_kwh": oxima.energeia_kwh,
                "efedreia_kwh": oxima.efedreia_kwh,
                "diathesimi_panw_apo_efedreia_kwh": max(
                    0.0, oxima.energeia_kwh - oxima.efedreia_kwh
                ),
                "mesi_isxys_kw": oxima.mesi_isxys_kw,
            },
            "epikoinwnia": {
                "katastasi": oxima.katastasi_epikoinwnias,
            },
            "apostoles": [
                {
                    "id_apostolis": a.id_apostolis,
                    "titlos": a.titlos,
                    "katastasi": a.katastasi_apostolis,
                }
                for a in apostoles
            ],
            "ekdosi_katastasis": oxima.ekdosi_katastasis,
        }

    def pare_kindynous(self) -> List[Dict[str, Any]]:
        """Ροή εξωτερικών περιβαλλοντικών κινδύνων (MISSION-01)."""
        kindynoi = self.apothiki_apostolwn.pare_kindynous()
        return [
            {
                "id_kindynou": k.id_kindynou,
                "typos": k.typos_kindynou,
                "oratotita_m": k.oratotita_m,
                "epipedo_aktinovolias": k.epipedo_aktinovolias,
                "sovarotita": k.sovarotita,
                "eidos_dedomenwn": k.eidos_dedomenwn,
                "perigrafi": k.perigrafi,
                "xronos": k.xronos_katagrafis,
            }
            for k in kindynoi
        ]

    def proepiskopisi_anaklisis(self, id_oximatos: str) -> Dict[str, Any]:
        """Μη μεταλλακτική προεπισκόπηση επιστροφής rover με πολυδιάστατη ασφάλεια (MISSION-03, MISSION-05, §6)."""
        oxima = self.apothiki_apostolwn.pare_oxima_ana_id(id_oximatos)
        if not oxima:
            raise SfalmaDomain(
                kodikos=KodikosSfalmatos.DEN_VRETHIKE,
                minyma=f"Το όχημα '{id_oximatos}' δεν βρέθηκε.",
                katastasi_http=404,
            )

        # Ανάκτηση τρέχουσας ορατότητας από τους κινδύνους
        kindynoi = self.apothiki_apostolwn.pare_kindynous(orio=1)
        oratotita_m = kindynoi[0].oratotita_m if kindynoi else 5000.0

        # Αξιολόγηση μέσω του φυσικού μοντέλου PHY-07
        axiologisi = ypologise_xrono_epistrofis_kai_asfaleia(
            apostasi_km=oxima.apostasi_apo_vasi_km,
            taxytita_kmh=oxima.taxytita_kmh,
            mesi_isxys_kw=oxima.mesi_isxys_kw,
            diathesimi_energeia_kwh=oxima.energeia_kwh,
            efedreia_asfaleias_kwh=oxima.efedreia_kwh,
            oratotita_m=oratotita_m,
            katastasi_tilemetrias=oxima.katastasi_epikoinwnias,
            katwfli_asfalous_oratotitas_m=300.0,
        )

        axiologisi["id_oximatos"] = id_oximatos
        axiologisi["onoma_oximatos"] = oxima.onoma
        axiologisi["ekdosi_katastasis"] = oxima.ekdosi_katastasis
        return axiologisi

    def ektelesi_anaklisis(self, id_oximatos: str, xristis: DedomenaXristi) -> Dict[str, Any]:
        """Αποστολή εντολής ανάκλησης rover στη βάση (MISSION-04, MISSION-06)."""
        oxima = self.apothiki_apostolwn.pare_oxima_ana_id(id_oximatos)
        if not oxima:
            raise SfalmaDomain(
                kodikos=KodikosSfalmatos.DEN_VRETHIKE,
                minyma=f"Το όχημα '{id_oximatos}' δεν βρέθηκε.",
                katastasi_http=404,
            )

        id_entolis = f"entoli_anaklisis_{uuid.uuid4().hex[:8]}"
        twrinos_xronos = datetime.now(timezone.utc)

        # Έλεγχος επικοινωνίας: αν υπάρχει απώλεια ή σοβαρή υποβάθμιση, η κατάσταση γίνεται 'avevaio'
        katastasi_entolis = "se_exelixi"
        minyma = "Η εντολή ανάκλησης απεστάλη και εκτελείται."

        if oxima.katastasi_epikoinwnias == "apousia":
            katastasi_entolis = "avevaio"
            minyma = "Απώλεια επικοινωνίας με το όχημα. Η κατάσταση της εντολής παραμένει αβέβαιη."
        elif oxima.katastasi_epikoinwnias == "ypovathmismeni":
            katastasi_entolis = "avevaio"
            minyma = (
                "Υποβαθμισμένη επικοινωνία λόγω καταιγίδας. Δεν ελήφθη άμεση επιβεβαίωση εκτέλεσης."
            )

        if katastasi_entolis != "avevaio":
            oxima.katastasi_oximatos = "epistrofi_se_exelixi"
            oxima.ekdosi_katastasis += 1

        self.synedria.add(
            Entoli(
                id_entolis=id_entolis,
                id_xristi=xristis.id_xristi,
                rolos=xristis.vasikos_rolos.value,
                yposystima="apostoles",
                drasi="anaklisi_oximatos",
                katastasi=katastasi_entolis,
                dedomena_aitimatos={"id_oximatos": id_oximatos},
                apotelesma={"katastasi_entolis": katastasi_entolis, "minyma": minyma},
                xronos_ektelesis=twrinos_xronos,
            )
        )

        self.apothiki_koinwn.kataxwrise_istoriko_elegxou(
            id_xristi=xristis.id_xristi,
            rolos=xristis.vasikos_rolos.value,
            energeia="anaklisi_oximatos",
            ontotita="oxima_exerevnis",
            id_ontotitas=id_oximatos,
            palia_timi={"katastasi": "stasi"},
            nea_timi={"katastasi": oxima.katastasi_oximatos},
            aitiologia="Ανάκληση rover από χειριστή αποστολών",
        )

        self.synedria.commit()
        return {
            "id_entolis": id_entolis,
            "id_oximatos": id_oximatos,
            "katastasi_entolis": katastasi_entolis,
            "minyma": minyma,
        }

    def proepiskopisi_asfalous_stasis(self, id_oximatos: str) -> Dict[str, Any]:
        """Προεπισκόπηση επιλογών ασφαλούς στάσης (MISSION-08)."""
        oxima = self.apothiki_apostolwn.pare_oxima_ana_id(id_oximatos)
        if not oxima:
            raise SfalmaDomain(
                kodikos=KodikosSfalmatos.DEN_VRETHIKE,
                minyma=f"Το όχημα '{id_oximatos}' δεν βρέθηκε.",
                katastasi_http=404,
            )

        return {
            "id_oximatos": id_oximatos,
            "onoma": oxima.onoma,
            "trexousa_katastasi": oxima.katastasi_oximatos,
            "protinomeni_drasi": "asfalis_stasi",
            "epiptwseis": {
                "kinisi": "Άμεση παύση κίνησης και κλείδωμα φρένων",
                "energeia": "Μείωση κατανάλωσης ισχύος στα 100 W (μόνο όργανα επιβίωσης)",
                "asfaleia": "Εξάλειψη κινδύνου πρόσκρουσης λόγω μηδενικής ορατότητας στην καταιγίδα",
                "apostoli": "Προσωρινή αναστολή επιστημονικών μετρήσεων",
            },
            "apaiteitai_epivevaiwsi": True,
        }

    def ektelesi_asfalous_stasis(self, id_oximatos: str, xristis: DedomenaXristi) -> Dict[str, Any]:
        """Εκτέλεση εντολής ασφαλούς στάσης του rover (MISSION-04, MISSION-08)."""
        oxima = self.apothiki_apostolwn.pare_oxima_ana_id(id_oximatos)
        if not oxima:
            raise SfalmaDomain(
                kodikos=KodikosSfalmatos.DEN_VRETHIKE,
                minyma=f"Το όχημα '{id_oximatos}' δεν βρέθηκε.",
                katastasi_http=404,
            )

        oxima.katastasi_oximatos = "asfalis_stasi"
        oxima.mesi_isxys_kw = 0.1  # 100 W σε ασφαλή στάση
        oxima.ekdosi_katastasis += 1

        id_entolis = f"entoli_stasis_{uuid.uuid4().hex[:8]}"
        twrinos_xronos = datetime.now(timezone.utc)

        self.synedria.add(
            Entoli(
                id_entolis=id_entolis,
                id_xristi=xristis.id_xristi,
                rolos=xristis.vasikos_rolos.value,
                yposystima="apostoles",
                drasi="asfalis_stasi",
                katastasi="oloklirothike",
                dedomena_aitimatos={"id_oximatos": id_oximatos},
                apotelesma={"katastasi_oximatos": "asfalis_stasi"},
                xronos_ektelesis=twrinos_xronos,
            )
        )

        self.apothiki_koinwn.kataxwrise_istoriko_elegxou(
            id_xristi=xristis.id_xristi,
            rolos=xristis.vasikos_rolos.value,
            energeia="asfalis_stasi",
            ontotita="oxima_exerevnis",
            id_ontotitas=id_oximatos,
            palia_timi={"katastasi": "se_kinisi"},
            nea_timi={"katastasi": "asfalis_stasi"},
            aitiologia="Εντολή ασφαλούς στάσης λόγω επικίνδυνων συνθηκών",
        )

        self.synedria.commit()
        return {
            "id_entolis": id_entolis,
            "id_oximatos": id_oximatos,
            "katastasi_oximatos": "asfalis_stasi",
            "minyma": "Το όχημα τέθηκε επιτυχώς σε κατάσταση ασφαλούς στάσης.",
        }
