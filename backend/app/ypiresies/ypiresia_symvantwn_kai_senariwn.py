"""Επιχειρησιακή λογική για κοινή σύνοψη, συναγερμούς, μεταβιβάσεις και σενάριο καταιγίδας (SHARED-01…09, STORM-01…10)."""

import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

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
from backend.app.montela.apostoles import ExwterikosKindynos, OximaExerevnis
from backend.app.montela.koinonika_symvanta import Apofasi, EktelesiSenariou
from backend.app.montela.poroi import EnergeiakoFortio, Fwtovoltaiko
from backend.app.montela.xristes import MetavivasiDikaiwmatos
from backend.app.montela.ypostiriksi_zwis import (
    SyskeviYpostiriksisZwis,
    XwrosKatoikisis,
)
from backend.app.pyrinas.asfaleia import DedomenaXristi, RolosXristi
from backend.app.pyrinas.sfalmata import KodikosSfalmatos, SfalmaDomain


class YpiresiaSymvantwnKaiSenariwn:
    """Υπηρεσία συντονισμού όλης της αποικίας και εκτέλεσης σεναρίου καταιγίδας."""

    def __init__(self, synedria: Session):
        self.synedria = synedria
        self.apothiki_koinwn = ApothikiKoinwn(synedria)
        self.apothiki_zwis = ApothikiYpostiriksisZwis(synedria)
        self.apothiki_porwn = ApothikiPorwn(synedria)
        self.apothiki_apostolwn = ApothikiApostolwn(synedria)

    # ========================================================================
    # SHARED-01: Συγκεντρωτική Σύνοψη Αποικίας (/synopsi)
    # ========================================================================

    def pare_synopsi_apoikias(self) -> Dict[str, Any]:
        """Συγκεντρώνει την κατάσταση όλων των υποσυστημάτων χωρίς frontend."""
        xwroi = self.apothiki_zwis.pare_xwrous()
        pvs = self.apothiki_porwn.pare_fwtovoltaika()
        syssoreftes = self.apothiki_porwn.pare_syssoreftes()
        fortia = self.apothiki_porwn.pare_energeiaka_fortia()
        dexamenes = self.apothiki_porwn.pare_dexamenes_nerou()
        oximata = self.apothiki_apostolwn.pare_oximata()
        synagermoi = self.apothiki_koinwn.pare_synagermous(katastasi="energos")

        paragwgi_kw = sum(pv.isxys_paragwgis_w for pv in pvs) / 1000.0
        krisima_kw = sum(f.isxys_kw for f in fortia if f.energo and f.einai_krisimo)
        anavlita_kw = sum(f.isxys_kw for f in fortia if f.energo and f.einai_anavlito)
        energeia_bat_kwh = sum(s.energeia_kwh for s in syssoreftes)

        _, elleimma_kw, _, auto_wres, katastasi_energeias = (
            ypologise_ilektriko_isozygio_kai_autonomia(
                paragwgi_kw=paragwgi_kw,
                krisima_fortia_kw=krisima_kw,
                anavlita_fortia_kw=anavlita_kw,
                apwleies_kw=0.0,
                energeia_syssorefti_kwh=energeia_bat_kwh,
                efedreia_idi_afairemeni=True,
            )
        )

        nero_trexwn_l = sum(d.trexwn_ogkos_l for d in dexamenes)
        nero_efedreia_l = sum(d.efedreia_asfaleias_l for d in dexamenes)

        return {
            "apoikia": "apoikia_olympus",
            "xronos_synopsis": datetime.now(timezone.utc),
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
                "autonomia_wres": round(auto_wres, 3) if auto_wres is not None else None,
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
                    "id": s.id_synagermou,
                    "titlos": s.titlos,
                    "sovarotita": s.sovarotita,
                    "yposystima": s.yposystima,
                }
                for s in synagermoi
            ],
        }

    # ========================================================================
    # SHARED-02, SHARED-08: Συναγερμοί — Αναγνώριση και Επίλυση
    # ========================================================================

    def pare_synagermous(
        self, katastasi: Optional[str] = None, yposystima: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Επιστρέφει τη λίστα συναγερμών με αναλυτικά στοιχεία."""
        synagermoi = self.apothiki_koinwn.pare_synagermous(
            katastasi=katastasi, yposystima=yposystima
        )
        return [
            {
                "id_synagermou": s.id_synagermou,
                "titlos": s.titlos,
                "perigrafi": s.perigrafi,
                "aitia": s.aitia,
                "epiptwsi": s.epiptwsi,
                "systasi": s.systasi,
                "yposystima": s.yposystima,
                "sovarotita": s.sovarotita,
                "katastasi": s.katastasi,
                "id_xristi_anagnwrisis": s.id_xristi_anagnwrisis,
                "xronos_anagnwrisis": s.xronos_anagnwrisis,
                "id_xristi_epilysis": s.id_xristi_epilysis,
                "xronos_epilysis": s.xronos_epilysis,
                "sxolio_epilysis": s.sxolio_epilysis,
                "xronos_dimiourgias": s.xronos_dimiourgias,
            }
            for s in synagermoi
        ]

    def anagnwrisi_synagermou(self, id_synagermou: str, xristis: DedomenaXristi) -> Dict[str, Any]:
        """Αναγνώριση συναγερμού (γνώση, ΟΧΙ επίλυση - SHARED-02, SHARED-08)."""
        synagermos = self.apothiki_koinwn.pare_synagermo_ana_id(id_synagermou)
        if not synagermos:
            raise SfalmaDomain(
                kodikos=KodikosSfalmatos.DEN_VRETHIKE,
                minyma=f"Ο συναγερμός '{id_synagermou}' δεν βρέθηκε.",
                katastasi_http=404,
            )

        if synagermos.katastasi == "epilymenos":
            raise SfalmaDomain(
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
        self, id_synagermou: str, xristis: DedomenaXristi, sxolio_epilysis: str
    ) -> Dict[str, Any]:
        """Οριστική επίλυση συναγερμού με έλεγχο και αιτιολόγηση (SHARED-08)."""
        synagermos = self.apothiki_koinwn.pare_synagermo_ana_id(id_synagermou)
        if not synagermos:
            raise SfalmaDomain(
                kodikos=KodikosSfalmatos.DEN_VRETHIKE,
                minyma=f"Ο συναγερμός '{id_synagermou}' δεν βρέθηκε.",
                katastasi_http=404,
            )

        if not sxolio_epilysis.strip():
            raise SfalmaDomain(
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
                "id_metavivasis": m.id_metavivasis,
                "id_syntonisti": m.id_syntonisti,
                "id_paralipti": m.id_paralipti,
                "rolos": m.rolos,
                "pedio_efarmogis": m.pedio_efarmogis,
                "xronos_enarksis": m.xronos_enarksis,
                "xronos_liksis": m.xronos_liksis,
                "energo": m.energo,
                "aitiologia": m.aitiologia,
                "xronos_anaklisis": m.xronos_anaklisis,
            }
            for m in metavivaseis
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
            raise SfalmaDomain(
                kodikos=KodikosSfalmatos.ANARMODIOS_XRISTIS,
                minyma="Μόνο ο συντονιστής αποικίας μπορεί να εκχωρήσει μεταβίβαση δικαιωμάτων.",
                katastasi_http=403,
            )

        if diarkeia_wres <= 0.0 or diarkeia_wres > 72.0:
            raise SfalmaDomain(
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
            raise SfalmaDomain(
                kodikos=KodikosSfalmatos.ANARMODIOS_XRISTIS,
                minyma="Μόνο ο συντονιστής αποικίας μπορεί να ανακαλέσει μεταβίβαση δικαιωμάτων.",
                katastasi_http=403,
            )

        metavivasi = self.apothiki_koinwn.pare_metavivasi_ana_id(id_metavivasis)
        if not metavivasi:
            raise SfalmaDomain(
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

    # ========================================================================
    # STORM-01 έως STORM-10: Το Ακριβές Σενάριο Καταιγίδας Σκόνης (§6)
    # ========================================================================

    def proepiskopisi_senariou_kataigidas(self) -> Dict[str, Any]:
        """Προεπισκόπηση και σύγκριση επιλογών για το σενάριο καταιγίδας σκόνης (STORM-05, §6).

        Υπολογίζει ακριβώς τις τιμές του Golden Fixture (§6):
        - PV baseline: 4.8 kW -> Storm: 0.8 kW
        - Θέρμανση baseline: 8.0 kW -> Storm: 10.0 kW (+2 kW)
        - Έλλειμμα baseline: 9.2 kW -> Αυτονομία: 3.26087 h
        - Έλλειμμα storm (με αναβλητά): 15.2 kW -> Αυτονομία: 1.97368 h
        - Έλλειμμα storm (χωρίς αναβλητά): 11.2 kW -> Αυτονομία: 2.67857 h (+42.29 min)
        - Rover επιστροφή: 0.5 h, 0.3 kWh, ενεργειακά εφικτό αλλά ορατότητα 100 m < 300 m (κίνδυνος!)
        """
        # Υπολογισμοί baseline
        isxys_pv_vasis_kw = ypologise_isxy_fwtovoltaikou(0.20, 100.0, 300.0, 0.8) / 1000.0
        isxys_thermansis_vasis_kw = ypologise_apaitisi_thermansis(0.2, 500.0, 293.0, 213.0) / 1000.0
        _, elleimma_vasis_kw, _, autonomia_vasis_wres, _ = (
            ypologise_ilektriko_isozygio_kai_autonomia(
                isxys_pv_vasis_kw,
                isxys_thermansis_vasis_kw + 2.0,
                4.0,
                0.0,
                30.0,
                efedreia_idi_afairemeni=True,
            )
        )

        # Υπολογισμοί καταιγίδας (πριν την απόφαση, με αναβλητά)
        isxys_pv_kataigidas_kw = ypologise_isxy_fwtovoltaikou(0.20, 100.0, 80.0, 0.5) / 1000.0
        isxys_thermansis_kataigidas_kw = (
            ypologise_apaitisi_thermansis(0.2, 500.0, 293.0, 193.0) / 1000.0
        )
        _, elleimma_kataigidas_me_anavlita_kw, _, autonomia_kataigidas_me_anavlita_wres, _ = (
            ypologise_ilektriko_isozygio_kai_autonomia(
                isxys_pv_kataigidas_kw,
                isxys_thermansis_kataigidas_kw + 2.0,
                4.0,
                0.0,
                30.0,
                efedreia_idi_afairemeni=True,
            )
        )

        # Υπολογισμοί καταιγίδας (με παύση αναβλητών φορτίων)
        _, elleimma_kataigidas_shed_kw, _, autonomia_kataigidas_shed_wres, _ = (
            ypologise_ilektriko_isozygio_kai_autonomia(
                isxys_pv_kataigidas_kw,
                isxys_thermansis_kataigidas_kw + 2.0,
                0.0,
                0.0,
                30.0,
                efedreia_idi_afairemeni=True,
            )
        )

        # Υπολογισμός rover
        rover_axiologisi = ypologise_xrono_epistrofis_kai_asfaleia(
            apostasi_km=2.0,
            taxytita_kmh=4.0,
            mesi_isxys_kw=0.6,
            diathesimi_energeia_kwh=0.8,
            efedreia_asfaleias_kwh=0.2,
            oratotita_m=100.0,
            katastasi_tilemetrias="ypovathmismeni",
            katwfli_asfalous_oratotitas_m=300.0,
        )

        kerdos_wres = autonomia_kataigidas_shed_wres - autonomia_kataigidas_me_anavlita_wres

        return {
            "senario": "kataigida_skonis_2026",
            "statistika_golden_fixture": {
                "fwtovoltaika": {
                    "baseline_kw": round(isxys_pv_vasis_kw, 2),
                    "kataigida_kw": round(isxys_pv_kataigidas_kw, 2),
                    "ptwsi_kw": round(isxys_pv_vasis_kw - isxys_pv_kataigidas_kw, 2),
                },
                "thermansi": {
                    "baseline_kw": round(isxys_thermansis_vasis_kw, 2),
                    "kataigida_kw": round(isxys_thermansis_kataigidas_kw, 2),
                    "afksisi_kw": round(
                        isxys_thermansis_kataigidas_kw - isxys_thermansis_vasis_kw, 2
                    ),
                },
                "fortia_kai_autonomia": {
                    "baseline": {
                        "fortia_kw": round(isxys_thermansis_vasis_kw + 2.0 + 4.0, 2),
                        "elleimma_kw": round(elleimma_vasis_kw, 2),
                        "autonomia_wres": round(autonomia_vasis_wres, 5),
                    },
                    "kataigida_me_anavlita": {
                        "fortia_kw": round(isxys_thermansis_kataigidas_kw + 2.0 + 4.0, 2),
                        "elleimma_kw": round(elleimma_kataigidas_me_anavlita_kw, 2),
                        "autonomia_wres": round(autonomia_kataigidas_me_anavlita_wres, 5),
                    },
                    "kataigida_me_pausi_anavlhtwn": {
                        "fortia_kw": round(isxys_thermansis_kataigidas_kw + 2.0, 2),
                        "elleimma_kw": round(elleimma_kataigidas_shed_kw, 2),
                        "autonomia_wres": round(autonomia_kataigidas_shed_wres, 5),
                        "kerdos_wres": round(kerdos_wres, 5),
                        "kerdos_lepta": round(kerdos_wres * 60.0, 2),
                    },
                },
                "rover": rover_axiologisi,
            },
            "epiloges_apofasis": [
                {
                    "kodikos": "kamia_allagi",
                    "titlos": "Καμία ενέργεια (Διατήρηση όλων των φορτίων)",
                    "synepies": "Εξάντληση μπαταριών σε ~1.97 ώρες. Υψηλός κίνδυνος κατάρρευσης αποικίας.",
                    "asfaleia": "katastrofiki",
                },
                {
                    "kodikos": "pausi_anavlhtwn",
                    "titlos": "Παύση αναβλητών φορτίων (θερμοκήπιο / βοηθητικά)",
                    "synepies": "Επέκταση αυτονομίας κατά ~42.29 λεπτά (από 1.97 h σε 2.68 h).",
                    "asfaleia": "eparkis",
                },
                {
                    "kodikos": "asfalis_stasi_rover",
                    "titlos": "Εντολή ασφαλούς στάσης rover στη θέση του",
                    "synepies": "Αποτροπή πρόσκρουσης λόγω ορατότητας 100 m. Διατήρηση ενέργειας.",
                    "asfaleia": "ypsili",
                },
                {
                    "kodikos": "syndyasmos_pliroys_asfaleias",
                    "titlos": "Πλήρες πακέτο ασφαλείας: Παύση αναβλητών + Ασφαλής στάση rover",
                    "synepies": "Βέλτιστη στρατηγική επιβίωσης κατά τη διάρκεια της καταιγίδας.",
                    "asfaleia": "veltiwmeni",
                },
            ],
            "apaiteitai_egkrisi_syntonisti": True,
        }

    def energopoiisi_kataigidas(self, xristis: DedomenaXristi) -> Dict[str, Any]:
        """Ενεργοποίηση των παραμέτρων καταιγίδας στα περιβαλλοντικά assets (STORM-02, STORM-03)."""
        # Ενημέρωση Φωτοβολταϊκού (G=80, f=0.5 -> 800 W = 0.8 kW)
        pv = self.synedria.get(Fwtovoltaiko, "pv_01")
        if pv:
            pv.aktinovolia_w_m2 = 80.0
            pv.syntelestis_epikathisis_f = 0.5
            pv.isxys_paragwgis_w = 800.0

        # Ενημέρωση Θαλάμου (T_exw = 193 K)
        xwros = self.synedria.get(XwrosKatoikisis, "xwros_01")
        if xwros:
            xwros.thermokrasia_exwteriki_k = 193.0
            xwros.ekdosi_katastasis += 1

        # Ενημέρωση Θερμαντήρα και φορτίου (10,000 W = 10 kW)
        sysk = self.synedria.get(SyskeviYpostiriksisZwis, "sysk_thermansis")
        if sysk:
            sysk.katanalwsi_isxyos_w = 10000.0

        fortio_heat = self.synedria.get(EnergeiakoFortio, "fortio_thermansis")
        if fortio_heat:
            fortio_heat.isxys_kw = 10.0

        # Ενημέρωση Rover και Εξωτερικού Κινδύνου (ορατότητα 100 m)
        rover = self.synedria.get(OximaExerevnis, "rover_01")
        if rover:
            rover.katastasi_epikoinwnias = "ypovathmismeni"
            rover.ekdosi_katastasis += 1

        self.synedria.add(
            ExwterikosKindynos(
                id_kindynou=f"kindynos_storm_{uuid.uuid4().hex[:6]}",
                typos_kindynou="kataigida_skonis",
                oratotita_m=100.0,
                epipedo_aktinovolias=0.25,
                sovarotita="krisimi",
                eidos_dedomenwn="metrimeno",
                perigrafi="Σοβαρή καταιγίδα σκόνης: G=80 W/m², f=0.5, T_exw=193 K, ορατότητα 100 m.",
                xronos_katagrafis=datetime.now(timezone.utc),
            )
        )

        # Δημιουργία συναγερμού καταιγίδας
        self.apothiki_koinwn.kataxwrise_synagermo(
            id_synagermou=f"synag_storm_{uuid.uuid4().hex[:6]}",
            titlos="Κρίσιμη Καταιγίδα Σκόνης σε εξέλιξη",
            perigrafi="Κατακόρυφη πτώση ηλιακής ακτινοβολίας στα 80 W/m² και αύξηση αναγκών θέρμανσης στα 10 kW.",
            aitia="Ατμοσφαιρικό μέτωπο σκόνης στον Άρη",
            epiptwsi="Έλλειμμα 15.2 kW. Αυτονομία συσσωρευτή περιορισμένη σε μόλις 1.97 ώρες.",
            systasi="Άμεση παύση αναβλητών φορτίων (curtailment) και εντολή ασφαλούς στάσης στο rover.",
            yposystima="poroi",
            sovarotita="krisimi",
        )

        # Καταγραφή στο Audit
        self.apothiki_koinwn.kataxwrise_istoriko_elegxou(
            id_xristi=xristis.id_xristi,
            rolos=xristis.vasikos_rolos.value,
            energeia="energopoiisi_senariou_kataigidas",
            ontotita="ekteleseis_senariwn",
            id_ontotitas="kataigida_skonis_2026",
            palia_timi={"katastasi": "baseline"},
            nea_timi={"katastasi": "kataigida_energi", "G": 80.0, "T_exw": 193.0},
            aitiologia="Προσομοίωση επέλασης καταιγίδας σκόνης για έλεγχο διαδικασιών κρίσης",
        )

        self.synedria.commit()
        return {
            "senario": "kataigida_skonis_2026",
            "katastasi": "energi",
            "paragwgi_pv_kw": 0.8,
            "thermansi_kw": 10.0,
            "oratotita_m": 100.0,
            "minyma": "Η καταιγίδα σκόνης ενεργοποιήθηκε. Όλοι οι δείκτες ενημερώθηκαν.",
        }

    def ypovoli_apofasis_kataigidas(
        self,
        epilogi: str,
        aitiologia: str,
        xristis: DedomenaXristi,
    ) -> Dict[str, Any]:
        """Έγκριση και εκτέλεση απόφασης αντιμετώπισης καταιγίδας από συντονιστή (STORM-06, STORM-08)."""
        if xristis.vasikos_rolos != RolosXristi.SYNTONISTIS_APOIKIAS:
            raise SfalmaDomain(
                kodikos=KodikosSfalmatos.ANARMODIOS_XRISTIS,
                minyma="Μόνο ο συντονιστής αποικίας έχει δικαίωμα έγκρισης κρίσιμης απόφασης καταιγίδας.",
                katastasi_http=403,
            )

        if epilogi not in [
            "kamia_allagi",
            "pausi_anavlhtwn",
            "asfalis_stasi_rover",
            "syndyasmos_pliroys_asfaleias",
        ]:
            raise SfalmaDomain(
                kodikos=KodikosSfalmatos.AKYRI_TIMI,
                minyma=f"Μη έγκυρη επιλογή απόφασης: {epilogi}",
                katastasi_http=400,
            )

        # Εκτέλεση ενεργειών βάσει απόφασης
        if epilogi in ["pausi_anavlhtwn", "syndyasmos_pliroys_asfaleias"]:
            fortia = self.apothiki_porwn.pare_energeiaka_fortia()
            for f in fortia:
                if f.einai_anavlito:
                    f.energo = False

        if epilogi in ["asfalis_stasi_rover", "syndyasmos_pliroys_asfaleias"]:
            rover = self.synedria.get(OximaExerevnis, "rover_01")
            if rover:
                rover.katastasi_oximatos = "asfalis_stasi"
                rover.mesi_isxys_kw = 0.1
                rover.ekdosi_katastasis += 1

        # Καταγραφή απόφασης
        id_apofasis = f"apof_{uuid.uuid4().hex[:8]}"
        twrinos_xronos = datetime.now(timezone.utc)

        # Δημιουργία ή ανάκτηση εκτέλεσης σεναρίου
        senario = self.synedria.get(EktelesiSenariou, "kataigida_skonis_2026")
        if not senario:
            senario = EktelesiSenariou(
                id_senariou="kataigida_skonis_2026",
                onoma="Καταιγίδα Σκόνης 2026",
                perigrafi="Υποχρεωτικό σενάριο προσομοίωσης §6",
                energo=True,
            )
            self.synedria.add(senario)
            self.synedria.flush()

        apofasi = Apofasi(
            id_apofasis=id_apofasis,
            id_senariou="kataigida_skonis_2026",
            id_syntonisti=xristis.id_xristi,
            epilogi=epilogi,
            aitiologia=aitiologia,
            egkekrimeni=True,
            katastasi_prin={"anavlita_energa": True},
            katastasi_meta={"epilogi_pou_efarmostike": epilogi},
            xronos_apofasis=twrinos_xronos,
        )
        self.synedria.add(apofasi)

        self.apothiki_koinwn.kataxwrise_istoriko_elegxou(
            id_xristi=xristis.id_xristi,
            rolos=xristis.vasikos_rolos.value,
            energeia="egkrisi_apofasis_kataigidas",
            ontotita="apofaseis",
            id_ontotitas=id_apofasis,
            palia_timi=None,
            nea_timi={"epilogi": epilogi},
            aitiologia=aitiologia,
        )

        self.synedria.commit()
        return {
            "id_apofasis": id_apofasis,
            "epilogi": epilogi,
            "egkekrimeni": True,
            "syntonistis": xristis.id_xristi,
            "minyma": "Η απόφαση του συντονιστή εκτελέστηκε και καταγράφηκε επιτυχώς.",
        }

    # ========================================================================
    # CORE-13: Έλεγχος Ρολογιού Προσομοίωσης
    # ========================================================================

    def proxorise_xrono(self, lepta: int = 15) -> Dict[str, Any]:
        """Προχωρά το προσομοιωμένο ρολόι κατά καθορισμένα λεπτά (CORE-13)."""
        if lepta <= 0:
            raise SfalmaDomain(
                kodikos=KodikosSfalmatos.AKYRI_TIMI,
                minyma="Τα λεπτά προώθησης πρέπει να είναι θετικός αριθμός.",
                katastasi_http=400,
            )

        katastasi = self.apothiki_koinwn.pare_katastasi_prosomoiwsis()
        katastasi.simerino_vima += 1
        katastasi.xronos_prosomoiwsis = katastasi.xronos_prosomoiwsis + timedelta(minutes=lepta)

        self.synedria.commit()
        return {
            "simerino_vima": katastasi.simerino_vima,
            "neos_xronos": katastasi.xronos_prosomoiwsis,
            "lepta_pou_prostethikan": lepta,
        }
