"""Επιχειρησιακή λογική για την υποστήριξη ζωής και τον έλεγχο θερμοκρασίας (LIFE-01 έως LIFE-10)."""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from backend.app.apothikes.apothiki_koinwn import ApothikiKoinwn
from backend.app.apothikes.apothiki_ypostiriksis_zwis import ApothikiYpostiriksisZwis
from backend.app.fysika_montela.fysika_montela import (
    ypologise_apaitisi_thermansis,
    ypologise_apothema_kai_autonomia_oxygonou,
    ypologise_meriki_piesi_oxygonou,
    ypologise_thermikes_apwleies,
)
from backend.app.montela.koinonika_symvanta import Entoli, SymvanEntolis
from backend.app.montela.poroi import EnergeiakoFortio
from backend.app.pyrinas.asfaleia import DedomenaXristi
from backend.app.pyrinas.sfalmata import KodikosSfalmatos, SfalmaDomain

# Προσωρινή μνήμη αποθήκευσης προεπισκοπήσεων για ασφαλή επιβεβαίωση (LIFE-06, LIFE-07)
PROEPISKOPISEIS_THERMOKRASIAS: Dict[str, Dict[str, Any]] = {}


class YpiresiaYpostiriksisZwis:
    """Υπηρεσία διαχείρισης θαλάμων διαβίωσης και ατμόσφαιρας."""

    def __init__(self, synedria: Session):
        self.synedria = synedria
        self.apothiki_zwis = ApothikiYpostiriksisZwis(synedria)
        self.apothiki_koinwn = ApothikiKoinwn(synedria)

    def pare_xwrous(self) -> List[Dict[str, Any]]:
        """Επιστρέφει λίστα όλων των κατοικήσιμων χώρων (LIFE-01)."""
        xwroi = self.apothiki_zwis.pare_xwrous()
        apotelesmata = []
        for xwros in xwroi:
            apotelesmata.append(
                {
                    "id_xwrou": xwros.id_xwrou,
                    "onoma": xwros.onoma,
                    "plithysmos": xwros.plithysmos,
                    "ogkos_m3": xwros.ogkos_m3,
                    "epifaneia_m2": xwros.epifaneia_m2,
                    "epithymiti_thermokrasia_k": xwros.epithymiti_thermokrasia_k,
                    "thermokrasia_eswteriki_k": xwros.thermokrasia_eswteriki_k,
                    "thermokrasia_exwteriki_k": xwros.thermokrasia_exwteriki_k,
                    "piesi_pa": xwros.piesi_pa,
                    "pososto_oxygonou": xwros.pososto_oxygonou,
                    "ekdosi_katastasis": xwros.ekdosi_katastasis,
                }
            )
        return apotelesmata

    def pare_katastasi_xwrou(self, id_xwrou: str) -> Dict[str, Any]:
        """Πλήρες στιγμιότυπο υποστήριξης ζωής ενός θαλάμου (LIFE-02, LIFE-03)."""
        xwros = self.apothiki_zwis.pare_xwro_ana_id(id_xwrou)
        if not xwros:
            raise SfalmaDomain(
                kodikos=KodikosSfalmatos.DEN_VRETHIKE,
                minyma=f"Ο χώρος κατοίκησης '{id_xwrou}' δεν βρέθηκε.",
                katastasi_http=404,
            )

        syskeves = self.apothiki_zwis.pare_syskeves_xwrou(id_xwrou)
        apothema = self.apothiki_zwis.pare_apothema_oxygonou(id_xwrou)

        # Υπολογισμός μερικής πίεσης O2 και CO2
        meriki_p_o2 = ypologise_meriki_piesi_oxygonou(xwros.pososto_oxygonou, xwros.piesi_pa)
        meriki_p_co2 = xwros.pososto_dioxeidiou_anthraka * xwros.piesi_pa

        # Υπολογισμός απωλειών θέρμανσης
        apwleies_w = ypologise_thermikes_apwleies(
            xwros.syntelestis_thermoperatotitas_u,
            xwros.epifaneia_m2,
            xwros.thermokrasia_eswteriki_k,
            xwros.thermokrasia_exwteriki_k,
        )

        return {
            "id_xwrou": xwros.id_xwrou,
            "onoma": xwros.onoma,
            "plithysmos": xwros.plithysmos,
            "ekdosi_katastasis": xwros.ekdosi_katastasis,
            "thermokrasia": {
                "eswteriki_k": xwros.thermokrasia_eswteriki_k,
                "epithymiti_k": xwros.epithymiti_thermokrasia_k,
                "exwteriki_k": xwros.thermokrasia_exwteriki_k,
                "thermikes_apwleies_w": round(apwleies_w, 2),
            },
            "atmosfaira": {
                "synoliki_piesi_pa": xwros.piesi_pa,
                "pososto_oxygonou": xwros.pososto_oxygonou,
                "meriki_piesi_oxygonou_pa": round(meriki_p_o2, 2),
                "pososto_dioxeidiou_anthraka": xwros.pososto_dioxeidiou_anthraka,
                "meriki_piesi_dioxeidiou_anthraka_pa": round(meriki_p_co2, 2),
                "sxetiki_ygrasia": xwros.sxetiki_ygrasia,
            },
            "efedreia_oxygonou": {
                "diathesimo_kg": apothema.diathesimo_kg if apothema else 0.0,
                "xwritikotita_kg": apothema.xwritikotita_kg if apothema else 0.0,
                "rythmos_paragwgis_kg_h": apothema.rythmos_paragwgis_kg_h if apothema else 0.0,
            },
            "syskeves": [
                {
                    "id_syskevis": s.id_syskevis,
                    "onoma": s.onoma,
                    "typos": s.typos_syskevis,
                    "katastasi": s.katastasi_leitourgias,
                    "isxys_w": s.katanalwsi_isxyos_w,
                }
                for s in syskeves
            ],
        }

    def provlepsi_oxygonou(self, id_xwrou: str) -> Dict[str, Any]:
        """Υπολογισμός αυτονομίας οξυγόνου βάσει φυσικού μοντέλου (LIFE-04, PHY-03)."""
        xwros = self.apothiki_zwis.pare_xwro_ana_id(id_xwrou)
        if not xwros:
            raise SfalmaDomain(
                kodikos=KodikosSfalmatos.DEN_VRETHIKE,
                minyma=f"Ο χώρος '{id_xwrou}' δεν βρέθηκε.",
                katastasi_http=404,
            )

        apothema = self.apothiki_zwis.pare_apothema_oxygonou(id_xwrou)
        paragwgi_o2_kg_h = apothema.rythmos_paragwgis_kg_h if apothema else 0.0

        meriki_p_o2 = ypologise_meriki_piesi_oxygonou(xwros.pososto_oxygonou, xwros.piesi_pa)
        katwfli_pa = 16000.0  # 16 kPa ελάχιστη ασφαλής μερική πίεση
        katanalwsi_atomo_kg_h = 0.04  # 40 g/h

        moles, maza_kg, auto_h, katastasi = ypologise_apothema_kai_autonomia_oxygonou(
            ogkos_m3=xwros.ogkos_m3,
            thermokrasia_k=xwros.thermokrasia_eswteriki_k,
            meriki_piesi_oxygonou_pa=meriki_p_o2,
            katwfli_asfaleias_piesis_pa=katwfli_pa,
            arithmos_katoikwn=xwros.plithysmos,
            katanalwsi_ana_atomo_kg_h=katanalwsi_atomo_kg_h,
            rythmos_paragwgis_kg_h=paragwgi_o2_kg_h,
        )

        return {
            "id_xwrou": id_xwrou,
            "meriki_piesi_oxygonou_pa": round(meriki_p_o2, 2),
            "katwfli_asfaleias_pa": katwfli_pa,
            "moles_xrisimou_oxygonou": round(moles, 2),
            "maza_xrisimou_oxygonou_kg": round(maza_kg, 2),
            "synoliki_katanalwsi_kg_h": round(xwros.plithysmos * katanalwsi_atomo_kg_h, 3),
            "rythmos_paragwgis_kg_h": paragwgi_o2_kg_h,
            "autonomia_wres": round(auto_h, 2) if auto_h is not None else None,
            "katastasi_asfaleias": katastasi,
        }

    def proepiskopisi_allagis_thermokrasias(
        self,
        id_xwrou: str,
        epithymiti_thermokrasia_k: float,
        anamenomeni_ekdosi_katastasis: int,
    ) -> Dict[str, Any]:
        """Μη μεταλλακτική προεπισκόπηση αλλαγής θερμοκρασίας (LIFE-06, §7)."""
        xwros = self.apothiki_zwis.pare_xwro_ana_id(id_xwrou)
        if not xwros:
            raise SfalmaDomain(
                kodikos=KodikosSfalmatos.DEN_VRETHIKE,
                minyma=f"Ο χώρος '{id_xwrou}' δεν βρέθηκε.",
                katastasi_http=404,
            )

        # Έλεγχος ορίων ασφαλούς θερμοκρασίας (280 K έως 305 K / ~7°C έως ~32°C)
        if not (280.0 <= epithymiti_thermokrasia_k <= 305.0):
            raise SfalmaDomain(
                kodikos=KodikosSfalmatos.AKYRI_THERMOKRATIA,
                minyma=f"Η επιθυμητή θερμοκρασία {epithymiti_thermokrasia_k} K είναι εκτός των επιτρεπτών ορίων [280 K, 305 K].",
                katastasi_http=400,
                leptomereies={
                    "zitoumeni_k": epithymiti_thermokrasia_k,
                    "elaxisti_k": 280.0,
                    "megisti_k": 305.0,
                },
            )

        # Έλεγχος αισιοδοξίας ταυτοχρονισμού (optimistic locking)
        if xwros.ekdosi_katastasis != anamenomeni_ekdosi_katastasis:
            raise SfalmaDomain(
                kodikos=KodikosSfalmatos.STALE_PROEPISKOPISI,
                minyma="Η κατάσταση του χώρου έχει τροποποιηθεί από άλλον χρήστη. Απαιτείται ανανέωση.",
                katastasi_http=409,
                leptomereies={
                    "anamenomeni_ekdosi": anamenomeni_ekdosi_katastasis,
                    "trexousa_ekdosi": xwros.ekdosi_katastasis,
                },
            )

        # Υπολογισμός ενεργειακής επίπτωσης με COP=1
        isxys_prin_w = ypologise_apaitisi_thermansis(
            syntelestis_thermoperatotitas_w_m2k=xwros.syntelestis_thermoperatotitas_u,
            epifaneia_m2=xwros.epifaneia_m2,
            thermokrasia_eswteriki_k=xwros.epithymiti_thermokrasia_k,
            thermokrasia_exwteriki_k=xwros.thermokrasia_exwteriki_k,
        )

        isxys_meta_w = ypologise_apaitisi_thermansis(
            syntelestis_thermoperatotitas_w_m2k=xwros.syntelestis_thermoperatotitas_u,
            epifaneia_m2=xwros.epifaneia_m2,
            thermokrasia_eswteriki_k=epithymiti_thermokrasia_k,
            thermokrasia_exwteriki_k=xwros.thermokrasia_exwteriki_k,
        )

        metavoli_w = isxys_meta_w - isxys_prin_w
        id_proepiskopisis = f"proep_therm_{uuid.uuid4().hex[:8]}"

        proepiskopisi_dedomena = {
            "id_proepiskopisis": id_proepiskopisis,
            "id_xwrou": id_xwrou,
            "ekdosi_senariou": xwros.ekdosi_katastasis,
            "trexousa": {
                "thermokrasia_k": xwros.thermokrasia_eswteriki_k,
                "epithymiti_thermokrasia_k": xwros.epithymiti_thermokrasia_k,
            },
            "zitoumeni": {
                "epithymiti_thermokrasia_k": epithymiti_thermokrasia_k,
            },
            "montelo": {
                "id_montelou": "thermikes_apwleies_v1",
                "eksiswsi": "U * A * (T_esw - T_exw)",
            },
            "eisodoi": {
                "syntelestis_thermoperatotitas_w_m2k": xwros.syntelestis_thermoperatotitas_u,
                "epifaneia_m2": xwros.epifaneia_m2,
                "thermokrasia_exwteriki_k": xwros.thermokrasia_exwteriki_k,
            },
            "epiptwsi": {
                "thermansi_prin_w": round(isxys_prin_w, 2),
                "thermansi_meta_w": round(isxys_meta_w, 2),
                "metavoli_w": round(metavoli_w, 2),
            },
            "proeidopoiiseis": (
                ["Αυξημένη κατανάλωση ισχύος θέρμανσης κατά την επιλεγμένη ρύθμιση."]
                if metavoli_w > 500.0
                else []
            ),
            "apaiteitai_epivevaiwsi": True,
            "xronos_dimiourgias": datetime.now(timezone.utc).isoformat(),
        }

        PROEPISKOPISEIS_THERMOKRASIAS[id_proepiskopisis] = proepiskopisi_dedomena
        return proepiskopisi_dedomena

    def ektelesi_allagis_thermokrasias(
        self,
        id_xwrou: str,
        id_proepiskopisis: str,
        anamenomeni_ekdosi_katastasis: int,
        xristis: DedomenaXristi,
        id_aitimatos_monadikotitas: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Επιβεβαίωση και εκτέλεση εντολής αλλαγής θερμοκρασίας (LIFE-07)."""
        # Έλεγχος idempotency
        if id_aitimatos_monadikotitas:
            yparxousa = self.apothiki_koinwn.pare_entoli_ana_id_aitimatos(
                id_aitimatos_monadikotitas
            )
            if yparxousa:
                return {
                    "id_entolis": yparxousa.id_entolis,
                    "katastasi": yparxousa.katastasi,
                    "minyma": "Η εντολή έχει ήδη εκτελεστεί (idempotent replay).",
                    "apotelesma": yparxousa.apotelesma,
                }

        xwros = self.apothiki_zwis.pare_xwro_ana_id(id_xwrou)
        if not xwros:
            raise SfalmaDomain(
                kodikos=KodikosSfalmatos.DEN_VRETHIKE,
                minyma=f"Ο χώρος '{id_xwrou}' δεν βρέθηκε.",
                katastasi_http=404,
            )

        if id_proepiskopisis not in PROEPISKOPISEIS_THERMOKRASIAS:
            raise SfalmaDomain(
                kodikos=KodikosSfalmatos.STALE_PROEPISKOPISI,
                minyma="Η προεπισκόπηση δεν βρέθηκε ή έχει λήξει.",
                katastasi_http=404,
            )

        proep = PROEPISKOPISEIS_THERMOKRASIAS[id_proepiskopisis]
        if proep["id_xwrou"] != id_xwrou:
            raise SfalmaDomain(
                kodikos=KodikosSfalmatos.AKYRI_TIMI,
                minyma="Η προεπισκόπηση αντιστοιχεί σε διαφορετικό χώρο κατοίκησης.",
                katastasi_http=400,
            )

        # Optimistic locking check
        if xwros.ekdosi_katastasis != anamenomeni_ekdosi_katastasis:
            raise SfalmaDomain(
                kodikos=KodikosSfalmatos.STALE_PROEPISKOPISI,
                minyma="Η κατάσταση του χώρου έχει τροποποιηθεί από άλλον χρήστη. Απαιτείται νέα προεπισκόπηση.",
                katastasi_http=409,
            )

        nea_epithymiti_k = proep["zitoumeni"]["epithymiti_thermokrasia_k"]
        palia_epithymiti_k = xwros.epithymiti_thermokrasia_k

        id_entolis = f"entoli_{uuid.uuid4().hex[:8]}"
        twrinos_xronos = datetime.now(timezone.utc)

        # Δημιουργία εγγραφής εντολής
        entoli = Entoli(
            id_entolis=id_entolis,
            id_xristi=xristis.id_xristi,
            rolos=xristis.vasikos_rolos.value,
            yposystima="ypostiriksi_zwis",
            drasi="allagi_thermokrasias",
            katastasi="oloklirothike",
            id_aitimatos_monadikotitas=id_aitimatos_monadikotitas,
            id_proepiskopisis=id_proepiskopisis,
            anamenomeni_ekdosi=anamenomeni_ekdosi_katastasis,
            dedomena_aitimatos=proep,
            apotelesma={
                "id_xwrou": id_xwrou,
                "palia_epithymiti_k": palia_epithymiti_k,
                "nea_epithymiti_k": nea_epithymiti_k,
                "nea_isxys_thermansis_w": proep["epiptwsi"]["thermansi_meta_w"],
            },
            xronos_ektelesis=twrinos_xronos,
        )
        self.synedria.add(entoli)

        # Συμβάν εντολής
        self.synedria.add(
            SymvanEntolis(
                id_entolis=id_entolis,
                proigoumeni_katastasi="epivevaiwthike",
                nea_katastasi="oloklirothike",
                minyma=f"Επιτυχής αλλαγή επιθυμητής θερμοκρασίας σε {nea_epithymiti_k} K.",
                xronos_symvantos=twrinos_xronos,
            )
        )

        # Ενημέρωση στόχου χώρου και έκδοσης κατάστασης
        xwros.epithymiti_thermokrasia_k = nea_epithymiti_k
        xwros.ekdosi_katastasis += 1

        # Ενημέρωση ισχύος θερμαντήρα
        syskeves = self.apothiki_zwis.pare_syskeves_xwrou(id_xwrou)
        for s in syskeves:
            if s.typos_syskevis == "thermantiras":
                s.katanalwsi_isxyos_w = proep["epiptwsi"]["thermansi_meta_w"]

        # Ενημέρωση ηλεκτρικού φορτίου θέρμανσης
        fortio_thermansis = self.synedria.get(EnergeiakoFortio, "fortio_thermansis")
        if fortio_thermansis:
            fortio_thermansis.isxys_kw = round(proep["epiptwsi"]["thermansi_meta_w"] / 1000.0, 3)

        # Καταγραφή στο Audit Log
        self.apothiki_koinwn.kataxwrise_istoriko_elegxou(
            id_xristi=xristis.id_xristi,
            rolos=xristis.vasikos_rolos.value,
            energeia="allagi_thermokrasias",
            ontotita="xwros_katoikisis",
            id_ontotitas=id_xwrou,
            palia_timi={"epithymiti_k": palia_epithymiti_k},
            nea_timi={"epithymiti_k": nea_epithymiti_k},
            aitiologia="Επιβεβαίωση αλλαγής στόχου θερμοκρασίας από χειριστή",
            id_aitimatos=id_aitimatos_monadikotitas,
        )

        self.synedria.commit()
        return {
            "id_entolis": id_entolis,
            "id_xwrou": id_xwrou,
            "katastasi": "oloklirothike",
            "epithymiti_thermokrasia_k": nea_epithymiti_k,
            "nea_ekdosi_katastasis": xwros.ekdosi_katastasis,
            "minyma": "Η επιθυμητή θερμοκρασία ενημερώθηκε επιτυχώς.",
        }
