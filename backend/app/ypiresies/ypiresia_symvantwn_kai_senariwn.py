"""Επιχειρησιακή λογική για κοινή σύνοψη, συναγερμούς, μεταβιβάσεις και σενάριο καταιγίδας (SHARED-01…09, STORM-01…10)."""

import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.apothikes.apothiki_apostolwn import ApothikiApostolwn
from backend.app.apothikes.apothiki_koinwn import ApothikiKoinwn
from backend.app.apothikes.apothiki_porwn import ApothikiPorwn
from backend.app.apothikes.apothiki_ypostiriksis_zwis import ApothikiYpostiriksisZwis
from backend.app.fysika_montela.fysika_montela import (
    ypologise_apaitisi_thermansis,
    ypologise_ilektriko_isozygio_kai_autonomia,
    ypologise_isxy_fwtovoltaikou,
    ypologise_xrono_epistrofis_kai_asfaleia,
)
from backend.app.montela import (
    Aisthitiras,
    DexameniNerou,
    KatastasiProsomoiwsis,
    StigmiotypoSenariou,
)
from backend.app.montela.apostoles import ExwterikosKindynos, OximaExerevnis
from backend.app.montela.koinonika_symvanta import Apofasi, EktelesiSenariou
from backend.app.montela.poroi import EnergeiakoFortio, Fwtovoltaiko
from backend.app.montela.xristes import MetavivasiDikaiwmatos
from backend.app.montela.ypostiriksi_zwis import (
    SyskeviYpostiriksisZwis,
    XwrosKatoikisis,
)
from backend.app.pyrinas.asfaleia import DedomenaXristi, RolosXristi, pare_xristi_apo_vasi
from backend.app.pyrinas.sfalmata import KodikosSfalmatos, SfalmaKanona
from backend.app.ypiresies.entoles_kai_proepiskopiseis import (
    dimiourgise_proepiskopisi,
    katanalwse_proepiskopisi,
    kataxwrise_entoli,
    kleidwse_synallagi,
    pare_epanalipsi,
    pare_proepiskopisi,
)
from backend.app.ypiresies.metriseis_kai_poiotita import (
    ananeose_metriseis,
    pare_egkyri_metrisi,
    xronos_apoikias,
)
from backend.app.ypiresies.synagermoi_kai_synthikes import enimerwse_synagermous


class YpiresiaSymvantwnKaiSenariwn:
    """Υπηρεσία συντονισμού όλης της αποικίας και εκτέλεσης σεναρίου καταιγίδας."""

    def __init__(self, synedria: Session):
        self.synedria = synedria
        self.apothiki_koinwn = ApothikiKoinwn(synedria)
        self.apothiki_zwis = ApothikiYpostiriksisZwis(synedria)
        self.apothiki_porwn = ApothikiPorwn(synedria)
        self.apothiki_apostolwn = ApothikiApostolwn(synedria)

    def elegxe_rolo_synagermou(self, synagermos, xristis):
        """Οι εξουσιοδοτήσεις επίλυσης περιορίζονται στο αντίστοιχο υποσύστημα."""
        rolos = {
            "ypostiriksi_zwis": RolosXristi.YPEFTHYNOS_YPOSTIRIKSIS_ZWIS,
            "poroi": RolosXristi.YPEFTHYNOS_PORWN,
            "apostoles": RolosXristi.YPEFTHYNOS_APOSTOLWN,
        }.get(synagermos.yposystima)
        egkyros = pare_xristi_apo_vasi(
            self.synedria, xristis.id_xristi, pedia={synagermos.yposystima}
        )
        if (
            egkyros.vasikos_rolos != RolosXristi.SYNTONISTIS_APOIKIAS
            and rolos not in egkyros.energoi_roloi
        ):
            raise SfalmaKanona(
                KodikosSfalmatos.ANARMODIOS_XRISTIS,
                "Απαιτείται υπεύθυνος του αντίστοιχου υποσυστήματος.",
                403,
            )

    def stigmiotypo_senariou(self, apaitise_egkyres=False):
        """Ενιαία έκδοση των πραγματικών πόρων, φορτίων και εξωτερικών συνθηκών."""
        from backend.app.ypiresies.metriseis_kai_poiotita import (
            pare_metriseis_energeias,
            teleftaia_metrisi,
        )

        thermokrasia = (
            pare_egkyri_metrisi(self.synedria, "aisth_thermokrasia_exw")
            if apaitise_egkyres
            else teleftaia_metrisi(self.synedria, "aisth_thermokrasia_exw")
        )
        return {
            "metriseis_energeias": pare_metriseis_energeias(
                self.synedria, apaitise_egkyres=apaitise_egkyres
            ),
            "metrisi_thermokrasias_exw": thermokrasia.id_metrisis if thermokrasia else None,
            "xwroi": [
                [
                    x.id_xwrou,
                    x.ekdosi_katastasis,
                    x.epithymiti_thermokrasia_k,
                    x.thermokrasia_exwteriki_k,
                ]
                for x in self.apothiki_zwis.pare_xwrous()
            ],
            "pv": [
                [
                    stoixeio_pi.id_fwtovoltaikou,
                    stoixeio_pi.aktinovolia_w_m2,
                    stoixeio_pi.syntelestis_epikathisis_f,
                ]
                for stoixeio_pi in self.apothiki_porwn.pare_fwtovoltaika()
            ],
            "syssoreftes": [
                [stoixeio_sigma.id_syssorefti, stoixeio_sigma.energeia_kwh]
                for stoixeio_sigma in self.apothiki_porwn.pare_syssoreftes()
            ],
            "fortia": [
                [stoixeio_zita.id_fortiou, stoixeio_zita.isxys_kw, stoixeio_zita.energo]
                for stoixeio_zita in self.apothiki_porwn.pare_energeiaka_fortia()
            ],
            "nero": [
                [stoixeio_delta.id_dexamenis, stoixeio_delta.trexwn_ogkos_l]
                for stoixeio_delta in self.apothiki_porwn.pare_dexamenes_nerou()
            ],
            "oximata": [
                [o.id_oximatos, o.ekdosi_katastasis, o.energeia_kwh, o.katastasi_epikoinwnias]
                for o in self.apothiki_apostolwn.pare_oximata()
            ],
        }

    def proepiskopisi_senariou_kataigidas(self, xristis=None):
        """Υπολογίζει το σενάριο από τις σημερινές παραδοχές, διατηρώντας τα δοσμένα εξωτερικά inputs."""
        for onoma in ("aisth_aktinovolia", "aisth_skoni", "aisth_thermokrasia_exw"):
            pare_egkyri_metrisi(self.synedria, onoma)
        from backend.app.ypiresies.ypiresia_porwn import YpiresiaPorwn

        xwroi = self.apothiki_zwis.pare_xwrous()
        pv = self.apothiki_porwn.pare_fwtovoltaika()
        energeia = YpiresiaPorwn(self.synedria).pare_katastasi_energeias()
        synoliki_kwh = sum(
            stoixeio_sigma.energeia_kwh for stoixeio_sigma in self.apothiki_porwn.pare_syssoreftes()
        )
        thermansi_arxiki = (
            sum(
                ypologise_apaitisi_thermansis(
                    x.syntelestis_thermoperatotitas_u,
                    x.epifaneia_m2,
                    x.epithymiti_thermokrasia_k,
                    213,
                )
                for x in xwroi
            )
            / 1000
        )
        thermansi_kataigidas = (
            sum(
                ypologise_apaitisi_thermansis(
                    x.syntelestis_thermoperatotitas_u,
                    x.epifaneia_m2,
                    x.epithymiti_thermokrasia_k,
                    193,
                )
                for x in xwroi
            )
            / 1000
        )
        pv_arxiko = (
            sum(
                ypologise_isxy_fwtovoltaikou(
                    stoixeio_pi.apodosi_eta, stoixeio_pi.epifaneia_m2, 300, 0.8
                )
                for stoixeio_pi in pv
            )
            / 1000
        )
        pv_kataigidas = (
            sum(
                ypologise_isxy_fwtovoltaikou(
                    stoixeio_pi.apodosi_eta, stoixeio_pi.epifaneia_m2, 80, 0.5
                )
                for stoixeio_pi in pv
            )
            / 1000
        )
        fortia = self.apothiki_porwn.pare_energeiaka_fortia()
        loipa_krisima = sum(
            stoixeio_zita.isxys_kw
            for stoixeio_zita in fortia
            if stoixeio_zita.einai_krisimo
            and stoixeio_zita.energo
            and stoixeio_zita.id_fortiou != "fortio_thermansis"
        )
        anavlita = sum(
            stoixeio_zita.isxys_kw
            for stoixeio_zita in fortia
            if stoixeio_zita.einai_anavlito and stoixeio_zita.energo
        )

        def isozygio(thermansi, paragwgi, fortia_anavlita):
            synolika, elleimma, _, autonomia, _ = ypologise_ilektriko_isozygio_kai_autonomia(
                paragwgi,
                thermansi + loipa_krisima,
                fortia_anavlita,
                0,
                synoliki_kwh,
                efedreia_idi_afairemeni=True,
            )
            return {"fortia_kw": synolika, "elleimma_kw": elleimma, "autonomia_wres": autonomia}

        arxiki = isozygio(thermansi_arxiki, pv_arxiko, anavlita)
        kataigida = isozygio(thermansi_kataigidas, pv_kataigidas, anavlita)
        pausi = isozygio(thermansi_kataigidas, pv_kataigidas, 0)
        kerdos = (
            (pausi["autonomia_wres"] - kataigida["autonomia_wres"])
            if pausi["autonomia_wres"] is not None and kataigida["autonomia_wres"] is not None
            else None
        )
        pausi.update(kerdos_wres=kerdos, kerdos_lepta=kerdos * 60 if kerdos is not None else None)
        oxima = self.synedria.get(OximaExerevnis, "rover_01")
        axiologisi = (
            ypologise_xrono_epistrofis_kai_asfaleia(
                oxima.apostasi_apo_vasi_km,
                oxima.taxytita_kmh,
                oxima.isxys_kinisis_kw,
                oxima.energeia_kwh,
                oxima.efedreia_kwh,
                100,
                "ypovathmismeni",
            )
            if oxima
            else None
        )
        apantisi = {
            "senario": "kataigida_skonis_2026",
            "statistika_senariou": {
                "fwtovoltaika": {
                    "arxiki_kw": pv_arxiko,
                    "kataigida_kw": pv_kataigidas,
                    "ptwsi_kw": pv_arxiko - pv_kataigidas,
                },
                "thermansi": {
                    "arxiki_kw": thermansi_arxiki,
                    "kataigida_kw": thermansi_kataigidas,
                    "afksisi_kw": thermansi_kataigidas - thermansi_arxiki,
                },
                "fortia_kai_autonomia": {
                    "arxiki_katastasi": arxiki,
                    "kataigida_me_anavlita": kataigida,
                    "kataigida_me_pausi_anavlhtwn": pausi,
                },
                "oxima": axiologisi,
            },
            "trexousa_energeia": energeia["isozygio"],
            "epiloges_apofasis": [
                {"kodikos": kleidi, "titlos": stoixeio_taf}
                for kleidi, stoixeio_taf in [
                    ("kamia_allagi", "Παρακολούθηση χωρίς περιορισμό"),
                    ("pausi_anavlhtwn", "Αναστολή αναβλητών φορτίων"),
                    ("anaklisi_oximatos", "Ανάκληση μόνο εφόσον είναι ασφαλής"),
                    ("asfalis_stasi_oximatos", "Εντολή ασφαλούς στάσης"),
                    ("syndyasmos_pliroys_asfaleias", "Αναστολή φορτίων και εντολή ασφαλούς στάσης"),
                ]
            ],
            "epiptwseis": {
                "thermokipio": "Η αναστολή περιορίζει φωτισμό/ανακύκλωση/φόρτιση και μπορεί να αναβάλει προγράμματα.",
                "nero": "Ο προγραμματισμός πρέπει να επανελεγχθεί με τα αποθέματα και τη διαθέσιμη ισχύ.",
                "ypostiriksi_zwis": "Τα κρίσιμα φορτία παραμένουν προτεραιότητα.",
            },
            "paradoxes": [
                "Εξωτερικές συνθήκες καταιγίδας G=80 W/m², f=0,5, Te=193 K, ορατότητα100m.",
                "Σταθερές συνθήκες στον ορίζοντα πρόβλεψης· η κρίση παραμένει ακόμη και με μεγαλύτερη αυτονομία.",
            ],
            "apaiteitai_egkrisi_syntonisti": True,
        }
        if xristis:
            apantisi = dimiourgise_proepiskopisi(
                self.synedria,
                "apofasi_kataigidas",
                "kataigida_skonis_2026",
                xristis,
                apantisi,
                self.stigmiotypo_senariou(apaitise_egkyres=True),
            )
            self.synedria.commit()
        return apantisi

    def katagrafi_stigmiotypou(self, titlos):
        from backend.app.ypiresies.ypiresia_porwn import YpiresiaPorwn

        id_senariou = (
            self.synedria.get(KatastasiProsomoiwsis, 1).energo_senario or "arxiki_katastasi"
        )
        senario = self.synedria.get(EktelesiSenariou, id_senariou)
        if not senario:
            senario = EktelesiSenariou(
                id_senariou=id_senariou,
                onoma="Ιστορικό αποικίας",
                perigrafi="Χρονική καταγραφή πόρων",
                energo=True,
            )
            self.synedria.add(senario)
            self.synedria.flush()
        if senario:
            self.synedria.add(
                StigmiotypoSenariou(
                    id_stigmiotypou="stigmiotypo_" + uuid.uuid4().hex,
                    id_senariou=senario.id_senariou,
                    titlos=titlos,
                    dedomena_stigmiotypou={
                        **self.stigmiotypo_senariou(),
                        "poroi": {
                            "energeia": YpiresiaPorwn(self.synedria).pare_katastasi_energeias(),
                            "nero": YpiresiaPorwn(self.synedria).pare_katastasi_nerou(),
                            "fortia_egkatastasewn": YpiresiaPorwn(
                                self.synedria
                            ).pare_analytika_fortia(),
                            "logistiki": getattr(self, "logistiki_porwn", {}),
                        },
                    },
                    xronos_stigmiotypou=xronos_apoikias(self.synedria),
                )
            )

    def energopoiisi_kataigidas(self, xristis):
        return self.efarmose_prokathorismeno_senario("kataigida_skonis_2026", xristis)

    def efarmose_prokathorismeno_senario(self, kodikos, xristis):
        """Εκπαιδευτικές αστοχίες και αποκαταστάσεις με ενιαία ενημέρωση τηλεμετρίας."""
        epitrepta = {
            "kataigida_skonis_2026",
            "arxiki_katastasi",
            "xamili_aktinovolia",
            "diarroi_nerou",
            "vlavi_aisthitira_oxygonou",
            "apoleia_epikoinwnias",
            "ypsili_aktinovolia",
            "proskrousi",
            "diarroi_atmosfairas",
            "apokatastasi",
        }
        if kodikos not in epitrepta:
            raise SfalmaKanona(KodikosSfalmatos.DEN_VRETHIKE, "Το σενάριο δεν βρέθηκε.", 404)
        if xristis.vasikos_rolos != RolosXristi.SYNTONISTIS_APOIKIAS:
            raise SfalmaKanona(
                KodikosSfalmatos.ANARMODIOS_XRISTIS, "Απαιτείται συντονιστής αποικίας.", 403
            )
        kleidwse_synallagi(self.synedria)
        roloi = self.synedria.get(KatastasiProsomoiwsis, 1)
        roloi.xronos_prosomoiwsis += timedelta(microseconds=1)
        roloi.ekdosi_katastasis += 1
        xwros = self.synedria.get(XwrosKatoikisis, "xwros_01")
        oxima = self.synedria.get(OximaExerevnis, "rover_01")
        pv = self.synedria.get(Fwtovoltaiko, "pv_01")
        if kodikos in {"arxiki_katastasi", "apokatastasi"}:
            pv.aktinovolia_w_m2 = 300
            pv.syntelestis_epikathisis_f = 0.8
            xwros.thermokrasia_exwteriki_k = 213
            xwros.rythmos_diarrois_piesis_pa_h = 0
            xwros.piesi_pa = 101325
            oxima.katastasi_epikoinwnias = "statheri"
            for aisthitiras in self.synedria.scalars(select(Aisthitiras)):
                aisthitiras.katastasi = "leitourgikos"
            for dexameni in self.synedria.scalars(select(DexameniNerou)):
                dexameni.rythmos_diarrois_l_h = 0
            roloi.energo_senario = None
        elif kodikos == "kataigida_skonis_2026":
            pv.aktinovolia_w_m2 = 80
            pv.syntelestis_epikathisis_f = 0.5
            xwros.thermokrasia_exwteriki_k = 193
            oxima.katastasi_epikoinwnias = "ypovathmismeni"
            roloi.energo_senario = kodikos
        elif kodikos == "xamili_aktinovolia":
            pv.aktinovolia_w_m2 = 0
        elif kodikos == "diarroi_nerou":
            self.synedria.get(DexameniNerou, "dexameni_01").rythmos_diarrois_l_h = 100
        elif kodikos == "diarroi_atmosfairas":
            xwros.piesi_pa = 84000
            xwros.rythmos_diarrois_piesis_pa_h = 1000
        elif kodikos == "vlavi_aisthitira_oxygonou":
            self.synedria.get(Aisthitiras, "aisth_o2").katastasi = "ektos_leitourgias"
        elif kodikos == "apoleia_epikoinwnias":
            oxima.katastasi_epikoinwnias = "apousia"
        pv.isxys_paragwgis_w = ypologise_isxy_fwtovoltaikou(
            pv.apodosi_eta, pv.epifaneia_m2, pv.aktinovolia_w_m2, pv.syntelestis_epikathisis_f
        )
        xwros.ekdosi_katastasis += 1
        oxima.ekdosi_katastasis += 1
        thermansi = ypologise_apaitisi_thermansis(
            xwros.syntelestis_thermoperatotitas_u,
            xwros.epifaneia_m2,
            xwros.epithymiti_thermokrasia_k,
            xwros.thermokrasia_exwteriki_k,
        )
        self.synedria.get(EnergeiakoFortio, "fortio_thermansis").isxys_kw = thermansi / 1000
        self.synedria.get(
            SyskeviYpostiriksisZwis, "sysk_thermansis"
        ).katanalwsi_isxyos_w = thermansi
        if kodikos in {
            "kataigida_skonis_2026",
            "arxiki_katastasi",
            "apokatastasi",
            "ypsili_aktinovolia",
            "proskrousi",
        }:
            self.synedria.add(
                ExwterikosKindynos(
                    id_kindynou="kindynos_" + uuid.uuid4().hex,
                    typos_kindynou="kataigida_skonis"
                    if kodikos == "kataigida_skonis_2026"
                    else kodikos,
                    oratotita_m=100 if kodikos == "kataigida_skonis_2026" else 5000,
                    epipedo_aktinovolias=0.5
                    if kodikos == "ypsili_aktinovolia"
                    else (0.25 if kodikos == "kataigida_skonis_2026" else 0.05),
                    sovarotita="krisimi"
                    if kodikos in {"kataigida_skonis_2026", "proskrousi"}
                    else "xamili",
                    eidos_dedomenwn="metrimeno",
                    perigrafi="Ελεγχόμενο εκπαιδευτικό συμβάν: " + kodikos,
                    xronos_katagrafis=xronos_apoikias(self.synedria),
                )
            )
        senario = self.synedria.get(EktelesiSenariou, "kataigida_skonis_2026")
        if not senario:
            senario = EktelesiSenariou(
                id_senariou="kataigida_skonis_2026",
                onoma="Καταιγίδα σκόνης",
                perigrafi="Ενιαίο εκπαιδευτικό σενάριο",
                energo=False,
            )
            self.synedria.add(senario)
        senario.energo = roloi.energo_senario == "kataigida_skonis_2026"
        ananeose_metriseis(self.synedria, xronos_apoikias(self.synedria))
        enimerwse_synagermous(self.synedria)
        self.katagrafi_stigmiotypou("Εφαρμογή σεναρίου " + kodikos)
        apantisi = {
            "senario": kodikos,
            "katastasi": "energi" if senario.energo else "efarmostike",
            "paragwgi_pv_kw": pv.isxys_paragwgis_w / 1000,
            "thermansi_kw": thermansi / 1000,
            "oratotita_m": 100 if senario.energo else 5000,
            "minyma": "Οι συνθήκες και οι μετρήσεις ενημερώθηκαν.",
        }
        kataxwrise_entoli(
            self.synedria, xristis, "senaria", "efarmogi_senariou", kodikos, {}, apantisi
        )
        self.synedria.commit()
        return apantisi

    def ypovoli_apofasis_kataigidas(
        self, epilogi, aitiologia, xristis, id_proepiskopisis=None, kleidi=None
    ):
        """Μία ατομική έγκριση με δεσμευμένες παραδοχές και διακριτές εντολές rover."""
        if xristis.vasikos_rolos != RolosXristi.SYNTONISTIS_APOIKIAS:
            raise SfalmaKanona(
                KodikosSfalmatos.ANARMODIOS_XRISTIS, "Απαιτείται συντονιστής αποικίας.", 403
            )
        kleidwse_synallagi(self.synedria)
        dedomena = {
            "epilogi": epilogi,
            "aitiologia": aitiologia,
            "id_proepiskopisis": id_proepiskopisis,
        }
        epanalipsi = pare_epanalipsi(
            self.synedria, xristis, "apofasi_kataigidas", "kataigida_skonis_2026", kleidi, dedomena
        )
        if epanalipsi is not None:
            return epanalipsi
        if epilogi not in {
            "kamia_allagi",
            "pausi_anavlhtwn",
            "asfalis_stasi_oximatos",
            "anaklisi_oximatos",
            "syndyasmos_pliroys_asfaleias",
        }:
            raise SfalmaKanona(KodikosSfalmatos.AKYRI_TIMI, "Μη έγκυρη επιλογή.", 422)
        prin = self.stigmiotypo_senariou(apaitise_egkyres=True)
        pare_proepiskopisi(
            self.synedria,
            id_proepiskopisis,
            "apofasi_kataigidas",
            "kataigida_skonis_2026",
            xristis,
            prin,
        )
        katanalwse_proepiskopisi(self.synedria, id_proepiskopisis)
        if self.synedria.get(KatastasiProsomoiwsis, 1).energo_senario != "kataigida_skonis_2026":
            raise SfalmaKanona(
                KodikosSfalmatos.MH_ASPHALIS_KATASTASI,
                "Το σενάριο καταιγίδας δεν είναι ενεργό.",
                409,
            )
        if epilogi in {"pausi_anavlhtwn", "syndyasmos_pliroys_asfaleias"}:
            from backend.app.prosomoiwsi.prosomoiosis_porwn import efarmose_pausi_anavlitwn

            efarmose_pausi_anavlitwn(self.synedria, True)
        entoli_oximatos = None
        if epilogi in {
            "asfalis_stasi_oximatos",
            "syndyasmos_pliroys_asfaleias",
            "anaklisi_oximatos",
        }:
            from backend.app.ypiresies.ypiresia_apostolwn import YpiresiaApostolwn

            ypiresia = YpiresiaApostolwn(self.synedria)
            if epilogi == "anaklisi_oximatos":
                proep = ypiresia.proepiskopisi_anaklisis("rover_01", xristis)
                entoli_oximatos = ypiresia.ektelesi_anaklisis(
                    "rover_01", xristis, proep["id_proepiskopisis"], desmefsi_synallagis=False
                )
            else:
                proep = ypiresia.proepiskopisi_asfalous_stasis("rover_01", xristis)
                entoli_oximatos = ypiresia.ektelesi_asfalous_stasis(
                    "rover_01", xristis, proep["id_proepiskopisis"], desmefsi_synallagis=False
                )
        id_apofasis = "apofasi_" + uuid.uuid4().hex
        self.synedria.add(
            Apofasi(
                id_apofasis=id_apofasis,
                id_senariou="kataigida_skonis_2026",
                id_syntonisti=xristis.id_xristi,
                epilogi=epilogi,
                aitiologia=aitiologia,
                egkekrimeni=True,
                katastasi_prin=prin,
                katastasi_meta=self.stigmiotypo_senariou(),
                xronos_apofasis=xronos_apoikias(self.synedria),
            )
        )
        apantisi = {
            "id_apofasis": id_apofasis,
            "epilogi": epilogi,
            "egkekrimeni": True,
            "syntonistis": xristis.id_xristi,
            "entoli_oximatos": entoli_oximatos,
            "minyma": "Η απόφαση καταγράφηκε. Ελέγξτε χωριστά την παραλαβή εντολής rover και επανεκτιμήστε την κρίση.",
        }
        kataxwrise_entoli(
            self.synedria,
            xristis,
            "senaria",
            "apofasi_kataigidas",
            "kataigida_skonis_2026",
            dedomena,
            apantisi,
            id_proepiskopisis=id_proepiskopisis,
            kleidi=kleidi,
        )
        self.katagrafi_stigmiotypou("Απόφαση συντονιστή")
        enimerwse_synagermous(self.synedria)
        self.synedria.commit()
        return apantisi

    def proxorise_xrono(self, lepta=15, xristis=None):
        """Εκτελεί χρονικές εργασίες, ισοζύγια, κίνηση και τηλεμετρία σε διακριτά πεντάλεπτα."""
        from backend.app.prosomoiwsi.prosomoiosi_zwis import proxorise_zwi
        from backend.app.prosomoiwsi.prosomoiosis_apostolwn import proxorise_apostoles
        from backend.app.prosomoiwsi.prosomoiosis_porwn import proxorise_porous

        if not 0 < lepta <= 1440:
            raise SfalmaKanona(
                KodikosSfalmatos.AKYRI_TIMI, "Το βήμα πρέπει να είναι 1–1440 λεπτά.", 422
            )
        kleidwse_synallagi(self.synedria)
        roloi = self.synedria.get(KatastasiProsomoiwsis, 1)
        arxi = roloi.xronos_prosomoiwsis
        telos = arxi + timedelta(minutes=lepta)
        apotelesmata = []
        apo = arxi
        while apo < telos:
            ews = min(telos, apo + timedelta(minutes=5))
            poroi = proxorise_porous(self.synedria, apo, ews)
            zwi = []
            for katanomi in poroi["katanomes"]:
                zwi.extend(
                    proxorise_zwi(
                        self.synedria,
                        datetime.fromisoformat(katanomi["apo"]),
                        datetime.fromisoformat(katanomi["ews"]),
                        katanomi["trofodosia_ypostiriksis_zwis"],
                    )
                )
            apostoles = proxorise_apostoles(self.synedria, apo, ews)
            roloi.xronos_prosomoiwsis = ews
            self.synedria.flush()
            ananeose_metriseis(self.synedria, ews)
            apotelesmata.append(
                {
                    "apo": apo.isoformat(),
                    "ews": ews.isoformat(),
                    "poroi": poroi,
                    "ypostiriksi_zwis": zwi,
                    "apostoles": apostoles,
                }
            )
            apo = ews
        roloi.simerino_vima += 1
        roloi.ekdosi_katastasis += 1
        enimerwse_synagermous(self.synedria)
        self.logistiki_porwn = {
            kleidi: sum(stoixeio_taf["poroi"].get(kleidi, 0) for stoixeio_taf in apotelesmata)
            for kleidi in (
                "ardefsi_l",
                "anakyklwsi_eisodos_l",
                "anakyklwsi_epistrofi_l",
                "apwleia_anakyklwsis_l",
                "yperxeilisi_l",
                "diarros_l",
                "elleimma_nerou_l",
                "katanalwsi_kwh",
                "zitisi_energeias_kwh",
                "ekfortisi_syssoreftwn_kwh",
                "fortisi_syssoreftwn_kwh",
                "paragwgi_kwh",
                "mi_kalyptomeni_energeia_kwh",
                "fortisi_oximatwn_kwh",
                "perissevma_mi_apothikevmeno_kwh",
            )
        }
        self.katagrafi_stigmiotypou("Επανέλεγχος μετά από προώθηση χρόνου")
        apantisi = {
            "simerino_vima": roloi.simerino_vima,
            "neos_xronos": telos,
            "lepta_pou_prostethikan": lepta,
            "apotelesmata": apotelesmata,
        }
        if xristis:
            kataxwrise_entoli(
                self.synedria,
                xristis,
                "prosomoiwsi",
                "proodos_xronou",
                "apoikia",
                {"lepta": lepta},
                apantisi,
            )
        self.synedria.commit()
        return apantisi

    # ========================================================================
    # SHARED-01: Συγκεντρωτική Σύνοψη Αποικίας (/synopsi)
    # ========================================================================

    def pare_synopsi_apoikias(self) -> Dict[str, Any]:
        """Συγκεντρώνει την κατάσταση όλων των υποσυστημάτων χωρίς frontend."""
        xwroi = self.apothiki_zwis.pare_xwrous()
        pvs = self.apothiki_porwn.pare_fwtovoltaika()
        syssoreftes = self.apothiki_porwn.pare_syssoreftes()
        fortia = self.apothiki_porwn.pare_energeiaka_fortia()
        dexamenes = [
            stoixeio_delta
            for stoixeio_delta in self.apothiki_porwn.pare_dexamenes_nerou()
            if stoixeio_delta.typos_nerou == "katharo"
        ]
        oximata = self.apothiki_apostolwn.pare_oximata()
        synagermoi = [
            stoixeio_sigma
            for stoixeio_sigma in self.apothiki_koinwn.pare_synagermous()
            if stoixeio_sigma.katastasi != "epilymenos"
        ]

        paragwgi_kw = sum(pv.isxys_paragwgis_w for pv in pvs) / 1000.0
        krisima_kw = sum(
            stoixeio_zita.isxys_kw
            for stoixeio_zita in fortia
            if stoixeio_zita.energo and stoixeio_zita.einai_krisimo
        )
        anavlita_kw = sum(
            stoixeio_zita.isxys_kw
            for stoixeio_zita in fortia
            if stoixeio_zita.energo and stoixeio_zita.einai_anavlito
        )
        energeia_bat_kwh = sum(stoixeio_sigma.energeia_kwh for stoixeio_sigma in syssoreftes)

        _, elleimma_kw, _, autonomia_wres, katastasi_energeias = (
            ypologise_ilektriko_isozygio_kai_autonomia(
                paragwgi_kw=paragwgi_kw,
                krisima_fortia_kw=krisima_kw,
                anavlita_fortia_kw=anavlita_kw,
                apwleies_kw=0.0,
                energeia_syssorefti_kwh=energeia_bat_kwh,
                efedreia_idi_afairemeni=True,
            )
        )

        nero_trexwn_l = sum(stoixeio_delta.trexwn_ogkos_l for stoixeio_delta in dexamenes)
        nero_efedreia_l = sum(stoixeio_delta.efedreia_asfaleias_l for stoixeio_delta in dexamenes)

        return {
            "apoikia": "apoikia_olympus",
            "xronos_synopsis": xronos_apoikias(self.synedria),
            "ypostiriksi_zwis": {
                "plithysmos": sum(x.plithysmos for x in xwroi),
                "thermokrasia_esw_k": xwroi[0].thermokrasia_eswteriki_k if xwroi else 293.0,
                "thermokrasia_exw_k": xwroi[0].thermokrasia_exwteriki_k if xwroi else 213.0,
                "piesi_pa": xwroi[0].piesi_pa if xwroi else 101325.0,
                "pososto_oxygonou": xwroi[0].pososto_oxygonou if xwroi else 0.21,
            },
            "energeia": {
                "paragwgi_kw": round(paragwgi_kw, 3),
                "fortia_kw": round(krisima_kw + anavlita_kw, 3),
                "elleimma_kw": round(elleimma_kw, 3),
                "autonomia_wres": round(autonomia_wres, 3) if autonomia_wres is not None else None,
                "katastasi": katastasi_energeias,
            },
            "nero": {
                "diathesimo_synoliko_l": round(nero_trexwn_l, 2),
                "efedreia_asfaleias_l": round(nero_efedreia_l, 2),
                "diathesimo_xrisimo_l": round(max(0.0, nero_trexwn_l - nero_efedreia_l), 2),
            },
            "oxima_exerevnis": {
                "id_oximatos": oximata[0].id_oximatos if oximata else None,
                "katastasi": oximata[0].katastasi_oximatos if oximata else "agnwsti",
                "apostasi_km": oximata[0].apostasi_apo_vasi_km if oximata else 0.0,
                "energeia_kwh": oximata[0].energeia_kwh if oximata else 0.0,
                "epikoinwnia": oximata[0].katastasi_epikoinwnias if oximata else "agnwsti",
            },
            "energoi_synagermoi": [
                {
                    "id_synagermou": stoixeio_sigma.id_synagermou,
                    "titlos": stoixeio_sigma.titlos,
                    "sovarotita": stoixeio_sigma.sovarotita,
                    "yposystima": stoixeio_sigma.yposystima,
                }
                for stoixeio_sigma in synagermoi
            ],
        }

    def pare_synagermous(
        self, katastasi: Optional[str] = None, yposystima: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Επιστρέφει τη λίστα συναγερμών με αναλυτικά στοιχεία."""
        synagermoi = self.apothiki_koinwn.pare_synagermous(
            katastasi=katastasi, yposystima=yposystima
        )
        return [
            {
                "id_synagermou": stoixeio_sigma.id_synagermou,
                "energi_aitia": stoixeio_sigma.energi_aitia,
                "titlos": stoixeio_sigma.titlos,
                "perigrafi": stoixeio_sigma.perigrafi,
                "aitia": stoixeio_sigma.aitia,
                "epiptwsi": stoixeio_sigma.epiptwsi,
                "systasi": stoixeio_sigma.systasi,
                "yposystima": stoixeio_sigma.yposystima,
                "sovarotita": stoixeio_sigma.sovarotita,
                "katastasi": stoixeio_sigma.katastasi,
                "id_xristi_anagnwrisis": stoixeio_sigma.id_xristi_anagnwrisis,
                "xronos_anagnwrisis": stoixeio_sigma.xronos_anagnwrisis,
                "id_xristi_epilysis": stoixeio_sigma.id_xristi_epilysis,
                "xronos_epilysis": stoixeio_sigma.xronos_epilysis,
                "sxolio_epilysis": stoixeio_sigma.sxolio_epilysis,
                "xronos_dimiourgias": stoixeio_sigma.xronos_dimiourgias,
            }
            for stoixeio_sigma in synagermoi
        ]

    def anagnwrisi_synagermou(self, id_synagermou: str, xristis: DedomenaXristi) -> Dict[str, Any]:
        """Αναγνώριση συναγερμού (γνώση, ΟΧΙ επίλυση - SHARED-02, SHARED-08)."""
        kleidwse_synallagi(self.synedria)
        enimerwse_synagermous(self.synedria)
        synagermos = self.apothiki_koinwn.pare_synagermo_ana_id(id_synagermou)
        if not synagermos:
            raise SfalmaKanona(
                kodikos=KodikosSfalmatos.DEN_VRETHIKE,
                minyma=f"Ο συναγερμός '{id_synagermou}' δεν βρέθηκε.",
                katastasi_http=404,
            )

        self.elegxe_rolo_synagermou(synagermos, xristis)
        if synagermos.katastasi == "epilymenos":
            raise SfalmaKanona(
                kodikos=KodikosSfalmatos.MH_EPITREPTI_METAVASI,
                minyma="Ο συναγερμός έχει ήδη επιλυθεί.",
                katastasi_http=400,
            )

        synagermos.katastasi = "anagnwrismenos"
        synagermos.id_xristi_anagnwrisis = xristis.id_xristi
        synagermos.xronos_anagnwrisis = datetime.now(timezone.utc)

        self.apothiki_koinwn.kataxwrise_istoriko_elegxou(
            id_xristi=xristis.id_xristi,
            rolos=xristis.vasikos_rolos.value,
            energeia="anagnwrisi_synagermou",
            ontotita="synagermos",
            id_ontotitas=id_synagermou,
            palia_timi={"katastasi": "energos"},
            nea_timi={"katastasi": "anagnwrismenos"},
            aitiologia="Αναγνώριση εμφάνισης συναγερμού από αρμόδιο χειριστή",
        )

        self.synedria.commit()
        return {
            "id_synagermou": id_synagermou,
            "katastasi": "anagnwrismenos",
            "id_xristi_anagnwrisis": xristis.id_xristi,
            "minyma": "Ο συναγερμός αναγνωρίστηκε. Απαιτείται αντιμετώπιση της αιτίας για οριστική επίλυση.",
        }

    def epilysi_synagermou(
        self,
        id_synagermou: str,
        xristis: DedomenaXristi,
        sxolio_epilysis: str,
        xeirokiniti_parakampsi: bool = False,
    ) -> Dict[str, Any]:
        """Οριστική επίλυση συναγερμού με έλεγχο και αιτιολόγηση (SHARED-08)."""
        kleidwse_synallagi(self.synedria)
        enimerwse_synagermous(self.synedria)
        synagermos = self.apothiki_koinwn.pare_synagermo_ana_id(id_synagermou)
        if not synagermos:
            raise SfalmaKanona(
                kodikos=KodikosSfalmatos.DEN_VRETHIKE,
                minyma=f"Ο συναγερμός '{id_synagermou}' δεν βρέθηκε.",
                katastasi_http=404,
            )

        self.elegxe_rolo_synagermou(synagermos, xristis)
        if synagermos.energi_aitia and not (
            xeirokiniti_parakampsi and xristis.vasikos_rolos == RolosXristi.SYNTONISTIS_APOIKIAS
        ):
            raise SfalmaKanona(
                KodikosSfalmatos.MH_ASPHALIS_KATASTASI,
                "Η αιτία του συναγερμού παραμένει ενεργή. Απαιτείται αποκατάσταση ή ρητή παράκαμψη συντονιστή.",
                409,
            )
        if len(sxolio_epilysis.strip()) < 5:
            raise SfalmaKanona(
                kodikos=KodikosSfalmatos.AKYRI_TIMI,
                minyma="Απαιτείται τεκμηριωμένο σχόλιο επίλυσης για το κλείσιμο του συναγερμού.",
                katastasi_http=400,
            )

        synagermos.katastasi = "epilymenos"
        synagermos.id_xristi_epilysis = xristis.id_xristi
        synagermos.xronos_epilysis = datetime.now(timezone.utc)
        synagermos.sxolio_epilysis = sxolio_epilysis

        self.apothiki_koinwn.kataxwrise_istoriko_elegxou(
            id_xristi=xristis.id_xristi,
            rolos=xristis.vasikos_rolos.value,
            energeia="epilysi_synagermou",
            ontotita="synagermos",
            id_ontotitas=id_synagermou,
            palia_timi={"katastasi": "anagnwrismenos"},
            nea_timi={"katastasi": "epilymenos", "sxolio": sxolio_epilysis},
            aitiologia=f"Οριστική επίλυση συναγερμού: {sxolio_epilysis}",
        )

        self.synedria.commit()
        return {
            "id_synagermou": id_synagermou,
            "katastasi": "epilymenos",
            "id_xristi_epilysis": xristis.id_xristi,
            "minyma": "Ο συναγερμός επιλύθηκε επιτυχώς.",
        }

    # ========================================================================
    # CORE-18: Μεταβίβαση Δικαιωμάτων Ελέγχου (Role Delegation)
    # ========================================================================

    def pare_metavivaseis(self, mono_energes: bool = False) -> List[Dict[str, Any]]:
        """Επιστρέφει τη λίστα μεταβιβάσεων δικαιωμάτων."""
        metavivaseis = self.apothiki_koinwn.pare_metavivaseis(mono_energes=mono_energes)
        return [
            {
                "id_metavivasis": stoixeio_mi.id_metavivasis,
                "id_syntonisti": stoixeio_mi.id_syntonisti,
                "id_paralipti": stoixeio_mi.id_paralipti,
                "rolos": stoixeio_mi.rolos,
                "pedio_efarmogis": stoixeio_mi.pedio_efarmogis,
                "xronos_enarksis": stoixeio_mi.xronos_enarksis,
                "xronos_liksis": stoixeio_mi.xronos_liksis,
                "energo": stoixeio_mi.energo,
                "aitiologia": stoixeio_mi.aitiologia,
                "xronos_anaklisis": stoixeio_mi.xronos_anaklisis,
            }
            for stoixeio_mi in metavivaseis
        ]

    def dimiourgia_metavivasis(
        self,
        id_paralipti: str,
        rolos: str,
        diarkeia_wres: float,
        aitiologia: str,
        xristis: DedomenaXristi,
        pedio_efarmogis: str = "geniko",
    ) -> Dict[str, Any]:
        """Μεταβίβαση ρόλου από συντονιστή σε άλλον χρήστη (μόνο συντονιστής - CORE-18)."""
        if xristis.vasikos_rolos != RolosXristi.SYNTONISTIS_APOIKIAS:
            raise SfalmaKanona(
                kodikos=KodikosSfalmatos.ANARMODIOS_XRISTIS,
                minyma="Μόνο ο συντονιστής αποικίας μπορεί να εκχωρήσει μεταβίβαση δικαιωμάτων.",
                katastasi_http=403,
            )

        kleidwse_synallagi(self.synedria)
        try:
            RolosXristi(rolos)
        except ValueError:
            raise SfalmaKanona(KodikosSfalmatos.AKYRI_TIMI, "Ο ρόλος δεν αναγνωρίζεται.", 422)
        if rolos == RolosXristi.SYNTONISTIS_APOIKIAS.value:
            raise SfalmaKanona(
                KodikosSfalmatos.ANARMODIOS_XRISTIS,
                "Μεταβιβάζονται επιχειρησιακοί ρόλοι. Η εκχώρηση νέων δικαιωμάτων παραμένει στον βασικό συντονιστή.",
                403,
            )
        from backend.app.montela import Xristis

        paraliptis = self.synedria.get(Xristis, id_paralipti)
        if not paraliptis or not paraliptis.energos:
            raise SfalmaKanona(
                KodikosSfalmatos.DEN_VRETHIKE, "Ο παραλήπτης δεν είναι ενεργός χρήστης.", 404
            )
        if pedio_efarmogis not in {"geniko", "ypostiriksi_zwis", "poroi", "apostoles"}:
            from backend.app.montela import DexameniNerou, Thermokipio, ZwniThermokipiou

            if not any(
                self.synedria.get(montelo, pedio_efarmogis)
                for montelo in [
                    XwrosKatoikisis,
                    OximaExerevnis,
                    ZwniThermokipiou,
                    Thermokipio,
                    DexameniNerou,
                ]
            ):
                raise SfalmaKanona(
                    KodikosSfalmatos.DEN_VRETHIKE, "Το πεδίο μεταβίβασης δεν υπάρχει.", 404
                )
        if diarkeia_wres <= 0.0 or diarkeia_wres > 72.0:
            raise SfalmaKanona(
                kodikos=KodikosSfalmatos.AKYRI_TIMI,
                minyma="Η διάρκεια μεταβίβασης πρέπει να είναι από 0.1 έως 72 ώρες.",
                katastasi_http=400,
            )

        twrinos = datetime.now(timezone.utc)
        liksi = twrinos + timedelta(hours=diarkeia_wres)
        id_metavivasis = f"metav_{uuid.uuid4().hex[:8]}"

        metavivasi = MetavivasiDikaiwmatos(
            id_metavivasis=id_metavivasis,
            id_syntonisti=xristis.id_xristi,
            id_paralipti=id_paralipti,
            rolos=rolos,
            pedio_efarmogis=pedio_efarmogis,
            xronos_enarksis=twrinos,
            xronos_liksis=liksi,
            energo=True,
            aitiologia=aitiologia,
        )
        self.synedria.add(metavivasi)

        self.apothiki_koinwn.kataxwrise_istoriko_elegxou(
            id_xristi=xristis.id_xristi,
            rolos=xristis.vasikos_rolos.value,
            energeia="ekxwrisi_metavivasis",
            ontotita="metavivasi_dikaiwmatos",
            id_ontotitas=id_metavivasis,
            palia_timi=None,
            nea_timi={"paraliptis": id_paralipti, "rolos": rolos, "liksi": liksi.isoformat()},
            aitiologia=aitiologia,
        )

        self.synedria.commit()
        return {
            "id_metavivasis": id_metavivasis,
            "id_paralipti": id_paralipti,
            "rolos": rolos,
            "xronos_liksis": liksi,
            "minyma": "Η μεταβίβαση δικαιωμάτων εγκρίθηκε και καταγράφηκε επιτυχώς.",
        }

    def anaklisi_metavivasis(self, id_metavivasis: str, xristis: DedomenaXristi) -> Dict[str, Any]:
        """Ανάκληση ενεργού μεταβίβασης από συντονιστή (CORE-18)."""
        if xristis.vasikos_rolos != RolosXristi.SYNTONISTIS_APOIKIAS:
            raise SfalmaKanona(
                kodikos=KodikosSfalmatos.ANARMODIOS_XRISTIS,
                minyma="Μόνο ο συντονιστής αποικίας μπορεί να ανακαλέσει μεταβίβαση δικαιωμάτων.",
                katastasi_http=403,
            )

        kleidwse_synallagi(self.synedria)
        metavivasi = self.apothiki_koinwn.pare_metavivasi_ana_id(id_metavivasis)
        if not metavivasi:
            raise SfalmaKanona(
                kodikos=KodikosSfalmatos.DEN_VRETHIKE,
                minyma=f"Η μεταβίβαση '{id_metavivasis}' δεν βρέθηκε.",
                katastasi_http=404,
            )

        metavivasi.energo = False
        metavivasi.xronos_anaklisis = datetime.now(timezone.utc)

        self.apothiki_koinwn.kataxwrise_istoriko_elegxou(
            id_xristi=xristis.id_xristi,
            rolos=xristis.vasikos_rolos.value,
            energeia="anaklisi_metavivasis",
            ontotita="metavivasi_dikaiwmatos",
            id_ontotitas=id_metavivasis,
            palia_timi={"energo": True},
            nea_timi={"energo": False},
            aitiologia="Ανάκληση μεταβίβασης δικαιωμάτων από συντονιστή",
        )

        self.synedria.commit()
        return {
            "id_metavivasis": id_metavivasis,
            "energo": False,
            "minyma": "Η μεταβίβαση δικαιωμάτων ανακλήθηκε επιτυχώς.",
        }
