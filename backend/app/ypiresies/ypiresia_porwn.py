"""Επιχειρησιακή λογική για πόρους: θερμοκήπια, νερό, φωτοβολταϊκά και ενέργεια (RES-01 έως RES-14)."""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from backend.app.apothikes.apothiki_koinwn import ApothikiKoinwn
from backend.app.apothikes.apothiki_porwn import ApothikiPorwn
from backend.app.fysika_montela.fysika_montela import (
    ypologise_ilektriko_isozygio_kai_autonomia,
)
from backend.app.montela.koinonika_symvanta import Entoli
from backend.app.montela.poroi import (
    ProgrammaArdefsis,
    RoiNerou,
)
from backend.app.pyrinas.asfaleia import DedomenaXristi, RolosXristi
from backend.app.pyrinas.sfalmata import KodikosSfalmatos, SfalmaDomain

# Προσωρινή μνήμη αποθήκευσης προεπισκοπήσεων άρδευσης
PROEPISKOPISEIS_ARDEFSIS: Dict[str, Dict[str, Any]] = {}


class YpiresiaPorwn:
    """Υπηρεσία διαχείρισης φυσικών και ενεργειακών πόρων της αποικίας."""

    def __init__(self, synedria: Session):
        self.synedria = synedria
        self.apothiki_porwn = ApothikiPorwn(synedria)
        self.apothiki_koinwn = ApothikiKoinwn(synedria)

    # ========================================================================
    # Θερμοκήπια και Ζώνες (RES-01)
    # ========================================================================

    def pare_thermokipia(self) -> List[Dict[str, Any]]:
        """Επιστρέφει κατάσταση όλων των θερμοκηπίων."""
        thermokipia = self.apothiki_porwn.pare_thermokipia()
        return [
            {
                "id_thermokipiou": t.id_thermokipiou,
                "onoma": t.onoma,
                "thermokrasia_k": t.thermokrasia_k,
                "ygrasia_aera": t.ygrasia_aera,
                "ekdosi_katastasis": t.ekdosi_katastasis,
            }
            for t in thermokipia
        ]

    def pare_zwnes(self, id_thermokipiou: str) -> List[Dict[str, Any]]:
        """Επιστρέφει τις ζώνες καλλιέργειας και την υγρασία υποστρώματος."""
        zwnes = self.apothiki_porwn.pare_zwnes_thermokipiou(id_thermokipiou)
        return [
            {
                "id_zwnis": z.id_zwnis,
                "id_thermokipiou": z.id_thermokipiou,
                "onoma_zwnis": z.onoma_zwnis,
                "fyto": z.fyto,
                "ygrasia_ypostrwmatos": z.ygrasia_ypostrwmatos,
                "epithymiti_ygrasia": z.epithymiti_ygrasia,
                "katastasi_fwtismou": z.katastasi_fwtismou,
            }
            for z in zwnes
        ]

    # ========================================================================
    # Νερό και Άρδευση (RES-03, RES-05, RES-06, RES-07, RES-12)
    # ========================================================================

    def pare_katastasi_nerou(self) -> Dict[str, Any]:
        """Συγκεντρωτική εικόνα δεξαμενών, στάθμης και ροών νερού."""
        dexamenes = self.apothiki_porwn.pare_dexamenes_nerou()
        roes = self.apothiki_porwn.pare_roes_nerou()

        synoliki_xwritikotita_l = sum(d.xwritikotita_l for d in dexamenes)
        synolikos_ogkos_l = sum(d.trexwn_ogkos_l for d in dexamenes)
        synoliki_efedreia_l = sum(d.efedreia_asfaleias_l for d in dexamenes)

        return {
            "dexamenes": [
                {
                    "id_dexamenis": d.id_dexamenis,
                    "onoma": d.onoma,
                    "xwritikotita_l": d.xwritikotita_l,
                    "trexwn_ogkos_l": d.trexwn_ogkos_l,
                    "efedreia_asfaleias_l": d.efedreia_asfaleias_l,
                    "diathesimo_panw_apo_efedreia_l": max(
                        0.0, d.trexwn_ogkos_l - d.efedreia_asfaleias_l
                    ),
                    "ekdosi_katastasis": d.ekdosi_katastasis,
                }
                for d in dexamenes
            ],
            "synolika": {
                "xwritikotita_l": synoliki_xwritikotita_l,
                "trexwn_ogkos_l": synolikos_ogkos_l,
                "efedreia_l": synoliki_efedreia_l,
                "diathesimo_xrisimo_l": max(0.0, synolikos_ogkos_l - synoliki_efedreia_l),
            },
            "roes": [
                {
                    "id_rois": r.id_rois,
                    "id_dexamenis": r.id_dexamenis,
                    "typos": r.typos_rois,
                    "rythmos_l_h": r.rythmos_l_h,
                    "perigrafi": r.perigrafi,
                    "xronos": r.xronos_katagrafis,
                }
                for r in roes
            ],
        }

    def proepiskopisi_ardefsis(
        self,
        id_thermokipiou: str,
        id_zwnis: str,
        posotita_nerou_l: float,
        diarkeia_lepta: int = 30,
        xronos_enarksis: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """Μη μεταλλακτική προεπισκόπηση προγράμματος άρδευσης (RES-05)."""
        zwni = self.apothiki_porwn.pare_zwni_ana_id(id_zwnis)
        if not zwni or zwni.id_thermokipiou != id_thermokipiou:
            raise SfalmaDomain(
                kodikos=KodikosSfalmatos.DEN_VRETHIKE,
                minyma=f"Η ζώνη '{id_zwnis}' δεν ανήκει στο θερμοκήπιο '{id_thermokipiou}'.",
                katastasi_http=404,
            )

        if posotita_nerou_l <= 0.0:
            raise SfalmaDomain(
                kodikos=KodikosSfalmatos.AKYRI_TIMI,
                minyma="Η ποσότητα νερού πρέπει να είναι θετικός αριθμός.",
                katastasi_http=400,
            )

        # Κύρια δεξαμενή
        dexamenes = self.apothiki_porwn.pare_dexamenes_nerou()
        if not dexamenes:
            raise SfalmaDomain(
                kodikos=KodikosSfalmatos.DEN_VRETHIKE,
                minyma="Δεν βρέθηκε διαθέσιμη δεξαμενή νερού.",
                katastasi_http=404,
            )
        dexameni = dexamenes[0]

        diathesimo_nero_l = dexameni.trexwn_ogkos_l - dexameni.efedreia_asfaleias_l
        if posotita_nerou_l > diathesimo_nero_l:
            raise SfalmaDomain(
                kodikos=KodikosSfalmatos.ANEPARKES_NERO,
                minyma="Το διαθέσιμο νερό πάνω από την εφεδρεία δεν επαρκεί για την άρδευση.",
                katastasi_http=400,
                leptomereies={
                    "diathesimo_l": round(diathesimo_nero_l, 2),
                    "zitoumeno_l": posotita_nerou_l,
                    "efedreia_asfaleias_l": dexameni.efedreia_asfaleias_l,
                },
            )

        id_proepiskopisis = f"proep_ardefsi_{uuid.uuid4().hex[:8]}"
        enarksi = xronos_enarksis or datetime.now(timezone.utc)

        # Προβλεπόμενη στάθμη μετά την άρδευση
        ogkos_meta_l = dexameni.trexwn_ogkos_l - posotita_nerou_l
        provolomeni_afksisi_ygrasias = min(0.15, posotita_nerou_l / 1000.0)

        proepiskopisi = {
            "id_proepiskopisis": id_proepiskopisis,
            "id_thermokipiou": id_thermokipiou,
            "id_zwnis": id_zwnis,
            "id_dexamenis": dexameni.id_dexamenis,
            "posotita_nerou_l": posotita_nerou_l,
            "diarkeia_lepta": diarkeia_lepta,
            "xronos_enarksis": enarksi.isoformat() if isinstance(enarksi, datetime) else enarksi,
            "stathmi_prin_l": dexameni.trexwn_ogkos_l,
            "stathmi_meta_l": ogkos_meta_l,
            "ygrasia_prin": zwni.ygrasia_ypostrwmatos,
            "ygrasia_meta_ektimwmeni": round(
                zwni.ygrasia_ypostrwmatos + provolomeni_afksisi_ygrasias, 3
            ),
            "eparkis_stathmi": True,
            "xronos_dimiourgias": datetime.now(timezone.utc).isoformat(),
        }
        PROEPISKOPISEIS_ARDEFSIS[id_proepiskopisis] = proepiskopisi
        return proepiskopisi

    def dimiourgia_programmatos_ardefsis(
        self,
        id_proepiskopisis: str,
        xristis: DedomenaXristi,
        id_aitimatos_monadikotitas: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Επιβεβαίωση και καταχώριση προγράμματος άρδευσης (RES-06)."""
        if id_aitimatos_monadikotitas:
            yparxousa = self.apothiki_koinwn.pare_entoli_ana_id_aitimatos(
                id_aitimatos_monadikotitas
            )
            if yparxousa:
                return {
                    "id_entolis": yparxousa.id_entolis,
                    "katastasi": yparxousa.katastasi,
                    "minyma": "Το πρόγραμμα άρδευσης έχει ήδη δημιουργηθεί (idempotent replay).",
                    "apotelesma": yparxousa.apotelesma,
                }

        if id_proepiskopisis not in PROEPISKOPISEIS_ARDEFSIS:
            raise SfalmaDomain(
                kodikos=KodikosSfalmatos.STALE_PROEPISKOPISI,
                minyma="Η προεπισκόπηση άρδευσης δεν βρέθηκε ή έχει λήξει.",
                katastasi_http=404,
            )

        proep = PROEPISKOPISEIS_ARDEFSIS[id_proepiskopisis]
        dexameni = self.apothiki_porwn.pare_dexameni_ana_id(proep["id_dexamenis"])
        zwni = self.apothiki_porwn.pare_zwni_ana_id(proep["id_zwnis"])

        if not dexameni or not zwni:
            raise SfalmaDomain(
                kodikos=KodikosSfalmatos.DEN_VRETHIKE,
                minyma="Η δεξαμενή ή η ζώνη δεν βρέθηκε.",
                katastasi_http=404,
            )

        posotita_l = proep["posotita_nerou_l"]
        if dexameni.trexwn_ogkos_l - dexameni.efedreia_asfaleias_l < posotita_l:
            raise SfalmaDomain(
                kodikos=KodikosSfalmatos.ANEPARKES_NERO,
                minyma="Το διαθέσιμο νερό δεν επαρκεί πλέον λόγω άλλης μεταβολής.",
                katastasi_http=409,
            )

        id_programmatos = f"prog_ard_{uuid.uuid4().hex[:8]}"
        id_entolis = f"entoli_{uuid.uuid4().hex[:8]}"
        twrinos_xronos = datetime.now(timezone.utc)

        # Δημιουργία προγράμματος
        programma = ProgrammaArdefsis(
            id_programmatos=id_programmatos,
            id_thermokipiou=proep["id_thermokipiou"],
            id_zwnis=proep["id_zwnis"],
            id_dexamenis=proep["id_dexamenis"],
            posotita_nerou_l=posotita_l,
            xronos_enarksis=(
                datetime.fromisoformat(proep["xronos_enarksis"])
                if isinstance(proep["xronos_enarksis"], str)
                else proep["xronos_enarksis"]
            ),
            diarkeia_lepta=proep["diarkeia_lepta"],
            katastasi="programmatismeno",
            id_proepiskopisis=id_proepiskopisis,
        )
        self.synedria.add(programma)

        # Αφαίρεση νερού και ενημέρωση ροών
        dexameni.trexwn_ogkos_l -= posotita_l
        dexameni.ekdosi_katastasis += 1

        self.synedria.add(
            RoiNerou(
                id_dexamenis=dexameni.id_dexamenis,
                typos_rois="ardefsi",
                rythmos_l_h=round(posotita_l / (proep["diarkeia_lepta"] / 60.0), 2),
                perigrafi=f"Πρόγραμμα άρδευσης {id_programmatos} για {zwni.onoma_zwnis}",
                xronos_katagrafis=twrinos_xronos,
            )
        )

        # Καταγραφή εντολής
        self.synedria.add(
            Entoli(
                id_entolis=id_entolis,
                id_xristi=xristis.id_xristi,
                rolos=xristis.vasikos_rolos.value,
                yposystima="poroi",
                drasi="programmatismos_ardefsis",
                katastasi="oloklirothike",
                id_aitimatos_monadikotitas=id_aitimatos_monadikotitas,
                id_proepiskopisis=id_proepiskopisis,
                dedomena_aitimatos=proep,
                apotelesma={
                    "id_programmatos": id_programmatos,
                    "posotita_nerou_l": posotita_l,
                    "nea_stathmi_l": dexameni.trexwn_ogkos_l,
                },
                xronos_ektelesis=twrinos_xronos,
            )
        )

        # Audit log
        self.apothiki_koinwn.kataxwrise_istoriko_elegxou(
            id_xristi=xristis.id_xristi,
            rolos=xristis.vasikos_rolos.value,
            energeia="programmatismos_ardefsis",
            ontotita="programma_ardefsis",
            id_ontotitas=id_programmatos,
            palia_timi={"stathmi_l": proep["stathmi_prin_l"]},
            nea_timi={"stathmi_l": dexameni.trexwn_ogkos_l, "ardefsi_l": posotita_l},
            aitiologia="Επιβεβαίωση άρδευσης θερμοκηπίου από χειριστή πόρων",
            id_aitimatos=id_aitimatos_monadikotitas,
        )

        self.synedria.commit()
        return {
            "id_programmatos": id_programmatos,
            "id_entolis": id_entolis,
            "katastasi": "programmatismeno",
            "nea_stathmi_dexamenis_l": dexameni.trexwn_ogkos_l,
            "minyma": "Το πρόγραμμα άρδευσης καταχωρίστηκε επιτυχώς.",
        }

    def akyrosi_programmatos_ardefsis(
        self, id_programmatos: str, xristis: DedomenaXristi
    ) -> Dict[str, Any]:
        """Ακύρωση προγράμματος άρδευσης και επιστροφή ποσότητας (RES-06)."""
        programma = self.apothiki_porwn.pare_programma_ardefsis_ana_id(id_programmatos)
        if not programma:
            raise SfalmaDomain(
                kodikos=KodikosSfalmatos.DEN_VRETHIKE,
                minyma=f"Το πρόγραμμα άρδευσης '{id_programmatos}' δεν βρέθηκε.",
                katastasi_http=404,
            )

        if programma.katastasi != "programmatismeno":
            raise SfalmaDomain(
                kodikos=KodikosSfalmatos.MH_EPITREPTI_METAVASI,
                minyma=f"Δεν επιτρέπεται η ακύρωση προγράμματος σε κατάσταση '{programma.katastasi}'.",
                katastasi_http=400,
            )

        dexameni = self.apothiki_porwn.pare_dexameni_ana_id(programma.id_dexamenis)
        if dexameni:
            dexameni.trexwn_ogkos_l += programma.posotita_nerou_l
            dexameni.ekdosi_katastasis += 1

        programma.katastasi = "akyrothike"

        self.apothiki_koinwn.kataxwrise_istoriko_elegxou(
            id_xristi=xristis.id_xristi,
            rolos=xristis.vasikos_rolos.value,
            energeia="akyrosi_ardefsis",
            ontotita="programma_ardefsis",
            id_ontotitas=id_programmatos,
            palia_timi={"katastasi": "programmatismeno"},
            nea_timi={"katastasi": "akyrothike"},
            aitiologia="Ακύρωση άρδευσης από χειριστή και επιστροφή νερού στη δεξαμενή",
        )

        self.synedria.commit()
        return {
            "id_programmatos": id_programmatos,
            "katastasi": "akyrothike",
            "epistrafen_nero_l": programma.posotita_nerou_l,
            "minyma": "Το πρόγραμμα άρδευσης ακυρώθηκε επιτυχώς.",
        }

    # ========================================================================
    # Ενέργεια, Φωτοβολταϊκά και Συσσωρευτές (RES-02, RES-04, RES-10, RES-14)
    # ========================================================================

    def pare_katastasi_energeias(self) -> Dict[str, Any]:
        """Συνοπτική και αναλυτική κατάσταση ηλεκτρικού ισοζυγίου και αυτονομίας."""
        pvs = self.apothiki_porwn.pare_fwtovoltaika()
        syssoreftes = self.apothiki_porwn.pare_syssoreftes()
        fortia = self.apothiki_porwn.pare_energeiaka_fortia()

        paragwgi_w = sum(pv.isxys_paragwgis_w for pv in pvs)
        paragwgi_kw = paragwgi_w / 1000.0

        krisima_kw = sum(f.isxys_kw for f in fortia if f.energo and f.einai_krisimo)
        anavlita_kw = sum(f.isxys_kw for f in fortia if f.energo and f.einai_anavlito)

        energeia_kwh = sum(s.energeia_kwh for s in syssoreftes)

        _, elleimma_kw, _, auto_wres, katastasi = ypologise_ilektriko_isozygio_kai_autonomia(
            paragwgi_kw=paragwgi_kw,
            krisima_fortia_kw=krisima_kw,
            anavlita_fortia_kw=anavlita_kw,
            apwleies_kw=0.0,
            energeia_syssorefti_kwh=energeia_kwh,
            efedreia_idi_afairemeni=True,
        )

        return {
            "paragwgi": {
                "synoliki_isxys_w": round(paragwgi_w, 2),
                "synoliki_isxys_kw": round(paragwgi_kw, 3),
                "fwtovoltaika": [
                    {
                        "id": pv.id_fwtovoltaikou,
                        "onoma": pv.onoma,
                        "epifaneia_m2": pv.epifaneia_m2,
                        "apodosi_eta": pv.apodosi_eta,
                        "f_skonis": pv.syntelestis_epikathisis_f,
                        "aktinovolia_w_m2": pv.aktinovolia_w_m2,
                        "isxys_w": pv.isxys_paragwgis_w,
                    }
                    for pv in pvs
                ],
            },
            "fortia": {
                "krisima_kw": round(krisima_kw, 3),
                "anavlita_kw": round(anavlita_kw, 3),
                "synolika_fortia_kw": round(krisima_kw + anavlita_kw, 3),
            },
            "sysswrefsi": {
                "energeia_kwh": round(energeia_kwh, 2),
                "syssoreftes": [
                    {
                        "id": s.id_syssorefti,
                        "onoma": s.onoma,
                        "xwritikotita_kwh": s.xwritikotita_kwh,
                        "energeia_kwh": s.energeia_kwh,
                        "efedreia_kwh": s.efedreia_kwh,
                        "katastasi": s.katastasi,
                    }
                    for s in syssoreftes
                ],
            },
            "isozygio": {
                "elleimma_kw": round(elleimma_kw, 3),
                "autonomia_wres": round(auto_wres, 3) if auto_wres is not None else None,
                "katastasi": katastasi,
            },
        }

    def pare_analytika_fortia(self) -> List[Dict[str, Any]]:
        """Επιστρέφει αναλυτική λίστα ηλεκτρικών φορτίων ανά εγκατάσταση (RES-14)."""
        fortia = self.apothiki_porwn.pare_energeiaka_fortia()
        return [
            {
                "id_fortiou": f.id_fortiou,
                "onoma": f.onoma,
                "egkatastasi": f.egkatastasi,
                "isxys_kw": f.isxys_kw,
                "einai_krisimo": f.einai_krisimo,
                "einai_anavlito": f.einai_anavlito,
                "energo": f.energo,
                "proteraiotita": f.proteraiotita,
            }
            for f in fortia
        ]

    def proepiskopisi_periorismou_fortiwn(self, pausi_anavlhtwn: bool = True) -> Dict[str, Any]:
        """Προεπισκόπηση παύσης αναβλητών φορτίων και σύγκριση αυτονομίας (RES-10)."""
        pvs = self.apothiki_porwn.pare_fwtovoltaika()
        syssoreftes = self.apothiki_porwn.pare_syssoreftes()
        fortia = self.apothiki_porwn.pare_energeiaka_fortia()

        paragwgi_kw = sum(pv.isxys_paragwgis_w for pv in pvs) / 1000.0
        energeia_kwh = sum(s.energeia_kwh for s in syssoreftes)

        krisima_kw = sum(f.isxys_kw for f in fortia if f.energo and f.einai_krisimo)
        anavlita_prin_kw = sum(f.isxys_kw for f in fortia if f.energo and f.einai_anavlito)
        anavlita_meta_kw = 0.0 if pausi_anavlhtwn else anavlita_prin_kw

        # Πριν τον περιορισμό
        _, deficit_prin, _, auto_prin, _ = ypologise_ilektriko_isozygio_kai_autonomia(
            paragwgi_kw=paragwgi_kw,
            krisima_fortia_kw=krisima_kw,
            anavlita_fortia_kw=anavlita_prin_kw,
            apwleies_kw=0.0,
            energeia_syssorefti_kwh=energeia_kwh,
            efedreia_idi_afairemeni=True,
        )

        # Μετά τον περιορισμό
        _, deficit_meta, _, auto_meta, _ = ypologise_ilektriko_isozygio_kai_autonomia(
            paragwgi_kw=paragwgi_kw,
            krisima_fortia_kw=krisima_kw,
            anavlita_fortia_kw=anavlita_meta_kw,
            apwleies_kw=0.0,
            energeia_syssorefti_kwh=energeia_kwh,
            efedreia_idi_afairemeni=True,
        )

        diafora_wres = (auto_meta - auto_prin) if (auto_meta and auto_prin) else 0.0

        return {
            "pausi_anavlhtwn": pausi_anavlhtwn,
            "katastasi_prin": {
                "fortia_kw": round(krisima_kw + anavlita_prin_kw, 3),
                "elleimma_kw": round(deficit_prin, 3),
                "autonomia_wres": round(auto_prin, 3) if auto_prin else None,
            },
            "katastasi_meta": {
                "fortia_kw": round(krisima_kw + anavlita_meta_kw, 3),
                "elleimma_kw": round(deficit_meta, 3),
                "autonomia_wres": round(auto_meta, 3) if auto_meta else None,
            },
            "ofelos": {
                "meiwsi_isxyos_kw": round(anavlita_prin_kw - anavlita_meta_kw, 3),
                "kerdos_autonomias_wres": round(diafora_wres, 3),
                "kerdos_autonomias_lepta": round(diafora_wres * 60.0, 2),
            },
            "apaiteitai_egkrisi_syntonisti": True,
        }

    def ektelesi_periorismou_fortiwn(
        self,
        pausi_anavlhtwn: bool,
        xristis: DedomenaXristi,
        aitiologia: str,
    ) -> Dict[str, Any]:
        """Εκτέλεση περιορισμού φορτίων μόνο με έγκριση συντονιστή (RES-10)."""
        if xristis.vasikos_rolos != RolosXristi.SYNTONISTIS_APOIKIAS:
            raise SfalmaDomain(
                kodikos=KodikosSfalmatos.ANARMODIOS_XRISTIS,
                minyma="Η παύση ή ενεργοποίηση φορτίων διασταυρούμενων υποσυστημάτων απαιτεί ρόλο συντονιστή αποικίας.",
                katastasi_http=403,
            )

        fortia = self.apothiki_porwn.pare_energeiaka_fortia()
        tropopoiithikan = 0
        for f in fortia:
            if f.einai_anavlito:
                f.energo = not pausi_anavlhtwn
                tropopoiithikan += 1

        self.apothiki_koinwn.kataxwrise_istoriko_elegxou(
            id_xristi=xristis.id_xristi,
            rolos=xristis.vasikos_rolos.value,
            energeia="periorismos_fortiwn",
            ontotita="energeiaka_fortia",
            id_ontotitas="anavlita",
            palia_timi={"energa": pausi_anavlhtwn},
            nea_timi={"energa": not pausi_anavlhtwn},
            aitiologia=aitiologia,
        )

        self.synedria.commit()
        return {
            "pausi_anavlhtwn": pausi_anavlhtwn,
            "arithmos_fortiwn_pou_allaksan": tropopoiithikan,
            "minyma": "Η ρύθμιση αναβλητών φορτίων εφαρμόστηκε επιτυχώς από τον συντονιστή.",
        }
