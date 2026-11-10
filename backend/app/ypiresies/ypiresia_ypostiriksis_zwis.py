"""Επιχειρησιακή λογική για την υποστήριξη ζωής και τον έλεγχο θερμοκρασίας (LIFE-01 έως LIFE-10)."""

from typing import Any, Dict, List

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.apothikes.apothiki_koinwn import ApothikiKoinwn
from backend.app.apothikes.apothiki_ypostiriksis_zwis import ApothikiYpostiriksisZwis
from backend.app.fysika_montela.fysika_montela import (
    ypologise_apaitisi_thermansis,
    ypologise_apothema_kai_autonomia_oxygonou,
    ypologise_meriki_piesi_oxygonou,
    ypologise_thermikes_apwleies,
)
from backend.app.montela.poroi import EnergeiakoFortio, Syssoreftis
from backend.app.pyrinas.asfaleia import XRISTES_EPIDEIKSIS
from backend.app.pyrinas.sfalmata import KodikosSfalmatos, SfalmaKanona
from backend.app.ypiresies.energeiaki_trofodosia import (
    pare_fortia_trofodosias,
    pososta_ypostiriksis_zwis,
    ypologise_autonomia_dyo_fasewn,
    ypologise_katanomi_fortiwn,
)
from backend.app.ypiresies.entoles_kai_proepiskopiseis import (
    dimiourgise_proepiskopisi,
    katanalwse_proepiskopisi,
    kataxwrise_entoli,
    kleidwse_synallagi,
    pare_epanalipsi,
    pare_proepiskopisi,
)
from backend.app.ypiresies.metriseis_kai_poiotita import (
    pare_egkyri_metrisi,
    pare_metriseis_energeias,
)


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
            raise SfalmaKanona(
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
                    "id_syskevis": stoixeio_sigma.id_syskevis,
                    "onoma": stoixeio_sigma.onoma,
                    "typos": stoixeio_sigma.typos_syskevis,
                    "katastasi": stoixeio_sigma.katastasi_leitourgias,
                    "isxys_w": stoixeio_sigma.katanalwsi_isxyos_w,
                }
                for stoixeio_sigma in syskeves
            ],
        }

    def provlepsi_oxygonou(self, id_xwrou: str) -> Dict[str, Any]:
        """Υπολογισμός αυτονομίας οξυγόνου βάσει φυσικού μοντέλου (LIFE-04, PHY-03)."""
        xwros = self.apothiki_zwis.pare_xwro_ana_id(id_xwrou)
        if not xwros:
            raise SfalmaKanona(
                kodikos=KodikosSfalmatos.DEN_VRETHIKE,
                minyma=f"Ο χώρος '{id_xwrou}' δεν βρέθηκε.",
                katastasi_http=404,
            )

        apothema = self.apothiki_zwis.pare_apothema_oxygonou(id_xwrou)
        for id_aisthitira in ("aisth_o2", "aisth_piesi", "aisth_thermokrasia_esw"):
            pare_egkyri_metrisi(self.synedria, id_aisthitira)
        paragwgi_o2_kg_h = apothema.rythmos_paragwgis_kg_h if apothema else 0.0
        ilektrolysi = next(
            (
                syskevi
                for syskevi in self.apothiki_zwis.pare_syskeves_xwrou(id_xwrou)
                if syskevi.typos_syskevis == "ilektrolysi"
            ),
            None,
        )
        if not ilektrolysi or ilektrolysi.katastasi_leitourgias != "energi":
            paragwgi_o2_kg_h = 0.0

        from backend.app.ypiresies.ypiresia_porwn import YpiresiaPorwn

        energeia = YpiresiaPorwn(self.synedria).pare_katastasi_energeias()
        metriseis_energeias = pare_metriseis_energeias(self.synedria)
        egkyri_iliaki_pigi = metriseis_energeias["poiotita"] in {"egkyro", "ypovathmismeno"}
        iliaki_kw = energeia["paragwgi"]["synoliki_isxys_kw"] if egkyri_iliaki_pigi else 0.0
        fortia = pare_fortia_trofodosias(self.synedria)
        zitisi_kw = sum(fortio["isxys_kw"] for fortio in fortia if fortio["energo"])
        apothema_kwh = energeia["sysswrefsi"]["energeia_kwh"]
        elleimma_kw = max(0, zitisi_kw - iliaki_kw)
        diarkeia = apothema_kwh / elleimma_kw if elleimma_kw else None
        katanomi_tora = ypologise_katanomi_fortiwn(
            fortia, max(zitisi_kw, iliaki_kw) if apothema_kwh > 0 else iliaki_kw
        )
        katanomi_meta = ypologise_katanomi_fortiwn(fortia, iliaki_kw)
        pososto_tora = pososta_ypostiriksis_zwis(katanomi_tora)["loipes_syskeves"]
        pososto_meta = pososta_ypostiriksis_zwis(katanomi_meta)["loipes_syskeves"]
        onomastiki_paragwgi = paragwgi_o2_kg_h
        paragwgi_o2_kg_h *= pososto_tora
        paragwgi_meta = onomastiki_paragwgi * pososto_meta
        proeidopoiiseis = []
        if not egkyri_iliaki_pigi:
            proeidopoiiseis.append(
                "Μη έγκυρη ηλιακή τηλεμετρία: η πρόβλεψη θεωρεί μηδενική ηλιακή παραγωγή."
            )
        if diarkeia is not None:
            proeidopoiiseis.append(
                "Μετά την εξάντληση της μπαταρίας υπολογίζεται μόνο η τρέχουσα ηλιακή τροφοδοσία."
            )

        meriki_p_o2 = ypologise_meriki_piesi_oxygonou(xwros.pososto_oxygonou, xwros.piesi_pa)
        katwfli_pa = 16000.0  # 16 kPa ελάχιστη ασφαλής μερική πίεση
        katanalwsi_atomo_kg_h = 0.04  # 40 g/h

        mol, maza_kg, autonomia_wres, katastasi = ypologise_apothema_kai_autonomia_oxygonou(
            ogkos_m3=xwros.ogkos_m3,
            thermokrasia_k=xwros.thermokrasia_eswteriki_k,
            meriki_piesi_oxygonou_pa=meriki_p_o2,
            katwfli_asfaleias_piesis_pa=katwfli_pa,
            arithmos_katoikwn=xwros.plithysmos,
            katanalwsi_ana_atomo_kg_h=katanalwsi_atomo_kg_h,
            rythmos_paragwgis_kg_h=paragwgi_o2_kg_h,
        )

        katanalwsi_kg_h = xwros.plithysmos * katanalwsi_atomo_kg_h
        autonomia_wres = ypologise_autonomia_dyo_fasewn(
            maza_kg, katanalwsi_kg_h, paragwgi_o2_kg_h, paragwgi_meta, diarkeia
        )
        synoliki_autonomia = ypologise_autonomia_dyo_fasewn(
            maza_kg + (apothema.diathesimo_kg if apothema else 0),
            katanalwsi_kg_h,
            paragwgi_o2_kg_h,
            paragwgi_meta,
            diarkeia,
        )
        if katastasi == "katwfli_paraviasmeno":
            autonomia_wres = synoliki_autonomia = 0.0
        elif autonomia_wres is not None and paragwgi_o2_kg_h >= katanalwsi_kg_h:
            katastasi = "peperasmeni_trofodosia"

        return {
            "id_xwrou": id_xwrou,
            "meriki_piesi_oxygonou_pa": round(meriki_p_o2, 2),
            "katwfli_asfaleias_pa": katwfli_pa,
            "mol_xrisimou_oxygonou": round(mol, 2),
            "maza_xrisimou_oxygonou_kg": round(maza_kg, 2),
            "synoliki_katanalwsi_kg_h": round(xwros.plithysmos * katanalwsi_atomo_kg_h, 3),
            "rythmos_paragwgis_kg_h": paragwgi_o2_kg_h,
            "autonomia_wres": round(autonomia_wres, 2) if autonomia_wres is not None else None,
            "katastasi_asfaleias": katastasi,
            "apothema_ekswterikis_dexamenis_kg": apothema.diathesimo_kg if apothema else 0.0,
            "synoliki_autonomia_me_dexameni_wres": round(synoliki_autonomia, 2)
            if synoliki_autonomia is not None
            else None,
            "trofodosia": {
                "diarkeia_plirous_trofodosias_wres": diarkeia,
                "pososto_syskevwn_tora": pososto_tora,
                "pososto_syskevwn_meta": pososto_meta,
                "onomastiki_paragwgi_kg_h": onomastiki_paragwgi,
                "paragwgi_meta_kg_h": paragwgi_meta,
                "poiotita_iliakis_pigis": metriseis_energeias["poiotita"],
            },
            "proeidopoiiseis": proeidopoiiseis,
            "paradoxes": [
                "Εκπαιδευτικό κατώφλι 16 kPa· κατανάλωση 0,04 kg ανά άτομο και ώρα.",
                "Το χρήσιμο ατμοσφαιρικό απόθεμα και η εξωτερική δεξαμενή δηλώνονται χωριστά.",
                "Σταθερή τρέχουσα ζήτηση/ήλιος, χωρίς μελλοντικά προγράμματα ή πίστωση περίσσειας O₂. Δεν αποτελεί πρόγνωση καιρού.",
            ],
        }

    def _energeiako_stigmiotypo(self):
        from backend.app.ypiresies.ypiresia_porwn import YpiresiaPorwn

        pare_metriseis_energeias(self.synedria, apaitise_egkyres=True)
        return YpiresiaPorwn(self.synedria)._stigmiotypo()

    def stigmiotypo_thermokrasias(self, id_xwrou):
        """Δεσμεύει τη φυσική κατάσταση, τον εξοπλισμό και τα ενεργειακά αποθέματα."""
        xwros = self.apothiki_zwis.pare_xwro_ana_id(id_xwrou)
        if not xwros:
            raise SfalmaKanona(KodikosSfalmatos.DEN_VRETHIKE, "Ο χώρος δεν βρέθηκε.", 404)
        metriseis = [
            pare_egkyri_metrisi(self.synedria, onoma)
            for onoma in ("aisth_thermokrasia_esw", "aisth_thermokrasia_exw")
        ]
        syskeves = self.apothiki_zwis.pare_syskeves_xwrou(id_xwrou)
        if not any(
            syskevi.typos_syskevis == "thermantiras" and syskevi.katastasi_leitourgias == "energi"
            for syskevi in syskeves
        ):
            raise SfalmaKanona(
                KodikosSfalmatos.MH_ASPHALIS_KATASTASI,
                "Η θέρμανση του χώρου δεν είναι διαθέσιμη.",
                409,
            )
        return {
            "energeiako_stigmiotypo": self._energeiako_stigmiotypo(),
            "ekdosi": xwros.ekdosi_katastasis,
            "epithymiti_k": xwros.epithymiti_thermokrasia_k,
            "exwteriki_k": xwros.thermokrasia_exwteriki_k,
            "epifaneia_m2": xwros.epifaneia_m2,
            "syntelestis_u": xwros.syntelestis_thermoperatotitas_u,
            "metriseis": [metrisi.id_metrisis for metrisi in metriseis],
            "energeia_kwh": sum(
                syssoreftis.energeia_kwh
                for syssoreftis in self.synedria.scalars(select(Syssoreftis))
            ),
            "syskeves": [
                [syskevi.id_syskevis, syskevi.katastasi_leitourgias] for syskevi in syskeves
            ],
        }

    def proepiskopisi_allagis_thermokrasias(
        self, id_xwrou, epithymiti_thermokrasia_k, anamenomeni_ekdosi_katastasis, xristis=None
    ):
        """Υπολογίζει επιπτώσεις και αποθηκεύει λήγουσα πρόταση χωρίς αλλαγή στόχου."""
        xristis = xristis or XRISTES_EPIDEIKSIS["xristis_zwis"]
        stigmiotypo = self.stigmiotypo_thermokrasias(id_xwrou)
        if not 280 <= epithymiti_thermokrasia_k <= 305:
            raise SfalmaKanona(
                KodikosSfalmatos.AKYRI_THERMOKRATIA,
                "Η θερμοκρασία πρέπει να ανήκει στο εκπαιδευτικό διάστημα 280–305 K.",
                422,
            )
        if stigmiotypo["ekdosi"] != anamenomeni_ekdosi_katastasis:
            raise SfalmaKanona(
                KodikosSfalmatos.PALIA_PROEPISKOPISI,
                "Η κατάσταση άλλαξε. Ανανεώστε τις μετρήσεις.",
                409,
            )
        xwros = self.apothiki_zwis.pare_xwro_ana_id(id_xwrou)
        isxys_prin = ypologise_apaitisi_thermansis(
            xwros.syntelestis_thermoperatotitas_u,
            xwros.epifaneia_m2,
            xwros.epithymiti_thermokrasia_k,
            xwros.thermokrasia_exwteriki_k,
        )
        isxys_meta = ypologise_apaitisi_thermansis(
            xwros.syntelestis_thermoperatotitas_u,
            xwros.epifaneia_m2,
            epithymiti_thermokrasia_k,
            xwros.thermokrasia_exwteriki_k,
        )
        from backend.app.ypiresies.ypiresia_porwn import YpiresiaPorwn

        energeia = YpiresiaPorwn(self.synedria).pare_katastasi_energeias()
        if (
            stigmiotypo["energeia_kwh"] <= 0
            and isxys_meta / 1000 > energeia["paragwgi"]["synoliki_isxys_kw"]
        ):
            raise SfalmaKanona(
                KodikosSfalmatos.ANEPARKIS_ENERGEIA,
                "Δεν υπάρχει αξιοποιήσιμη ενεργειακή εφεδρεία θέρμανσης.",
                409,
            )
        elleimma_meta = max(
            0,
            energeia["fortia"]["synolika_fortia_kw"]
            + (isxys_meta - isxys_prin) / 1000
            - energeia["paragwgi"]["synoliki_isxys_kw"],
        )
        apantisi = {
            "id_xwrou": id_xwrou,
            "ekdosi_senariou": stigmiotypo["ekdosi"],
            "trexousa": {
                "thermokrasia_k": xwros.thermokrasia_eswteriki_k,
                "epithymiti_thermokrasia_k": xwros.epithymiti_thermokrasia_k,
            },
            "zitoumeni": {"epithymiti_thermokrasia_k": epithymiti_thermokrasia_k},
            "montelo": {
                "id_montelou": "thermikes_apwleies_v1",
                "eksiswsi": "U*A*(T_esw-T_exw)",
                "monada": "W",
            },
            "eisodoi": {
                "syntelestis_thermoperatotitas_w_m2k": xwros.syntelestis_thermoperatotitas_u,
                "epifaneia_m2": xwros.epifaneia_m2,
                "thermokrasia_exwteriki_k": xwros.thermokrasia_exwteriki_k,
            },
            "epiptwsi": {
                "thermansi_prin_w": isxys_prin,
                "thermansi_meta_w": isxys_meta,
                "metavoli_w": isxys_meta - isxys_prin,
                "elleimma_meta_kw": elleimma_meta,
                "autonomia_meta_wres": stigmiotypo["energeia_kwh"] / elleimma_meta
                if elleimma_meta > 0
                else None,
            },
            "paradoxes": [
                "Σταθερό U και COP=1. Η μετρούμενη θερμοκρασία εξελίσσεται με το εικονικό ρολόι."
            ],
            "proeidopoiiseis": [
                "Η αποικία λειτουργεί με έλλειμμα ισχύος και χρειάζεται επανεκτίμηση."
            ]
            if elleimma_meta
            else [],
        }
        apantisi = dimiourgise_proepiskopisi(
            self.synedria, "allagi_thermokrasias", id_xwrou, xristis, apantisi, stigmiotypo
        )
        self.synedria.commit()
        return apantisi

    def ektelesi_allagis_thermokrasias(
        self,
        id_xwrou,
        id_proepiskopisis,
        anamenomeni_ekdosi_katastasis,
        xristis,
        id_aitimatos_monadikotitas=None,
    ):
        """Ατομικός επανέλεγχος, μία επιβεβαίωση και καταγραφή πραγματικού στόχου."""
        kleidwse_synallagi(self.synedria)
        dedomena = {
            "id_proepiskopisis": id_proepiskopisis,
            "anamenomeni_ekdosi_katastasis": anamenomeni_ekdosi_katastasis,
        }
        epanalipsi = pare_epanalipsi(
            self.synedria,
            xristis,
            "allagi_thermokrasias",
            id_xwrou,
            id_aitimatos_monadikotitas,
            dedomena,
        )
        if epanalipsi is not None:
            return epanalipsi
        stigmiotypo = self.stigmiotypo_thermokrasias(id_xwrou)
        proep = pare_proepiskopisi(
            self.synedria, id_proepiskopisis, "allagi_thermokrasias", id_xwrou, xristis, stigmiotypo
        )
        if anamenomeni_ekdosi_katastasis != proep["ekdosi_senariou"]:
            raise SfalmaKanona(
                KodikosSfalmatos.PALIA_PROEPISKOPISI,
                "Απαιτείται νέα προεπισκόπηση της τρέχουσας έκδοσης.",
                409,
            )
        katanalwse_proepiskopisi(self.synedria, id_proepiskopisis)
        xwros = self.apothiki_zwis.pare_xwro_ana_id(id_xwrou)
        xwros.epithymiti_thermokrasia_k = proep["zitoumeni"]["epithymiti_thermokrasia_k"]
        xwros.ekdosi_katastasis += 1
        isxys_w = proep["epiptwsi"]["thermansi_meta_w"]
        for syskevi in self.apothiki_zwis.pare_syskeves_xwrou(id_xwrou):
            if syskevi.typos_syskevis == "thermantiras":
                syskevi.katanalwsi_isxyos_w = isxys_w
        fortio = self.synedria.get(EnergeiakoFortio, "fortio_thermansis")
        if fortio:
            fortio.isxys_kw = isxys_w / 1000
        apantisi = {
            "id_xwrou": id_xwrou,
            "katastasi": "oloklirothike",
            "epithymiti_thermokrasia_k": xwros.epithymiti_thermokrasia_k,
            "nea_ekdosi_katastasis": xwros.ekdosi_katastasis,
            "minyma": "Ο στόχος θέρμανσης έγινε αποδεκτός. Η μέτρηση θα εξελιχθεί στον χρόνο.",
        }
        kataxwrise_entoli(
            self.synedria,
            xristis,
            "ypostiriksi_zwis",
            "allagi_thermokrasias",
            id_xwrou,
            dedomena,
            apantisi,
            id_proepiskopisis=id_proepiskopisis,
            kleidi=id_aitimatos_monadikotitas,
        )
        self.synedria.commit()
        return apantisi
