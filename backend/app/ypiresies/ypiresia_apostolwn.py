"""Σχέδια διαδρομών, ασφαλείς εντολές και επαληθεύσιμη τηλεμετρία rover."""

import math
import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.apothikes.apothiki_apostolwn import ApothikiApostolwn
from backend.app.apothikes.apothiki_koinwn import ApothikiKoinwn
from backend.app.fysika_montela.fysika_montela import (
    ypologise_energeia_kinisis_oximatos,
    ypologise_xrono_epistrofis_kai_asfaleia,
)
from backend.app.montela.apostoles import ApostoliOximatos, OximaExerevnis, ShmeioDiadromis
from backend.app.montela.koinonika_symvanta import Entoli, KatastasiProsomoiwsis
from backend.app.pyrinas.asfaleia import DedomenaXristi
from backend.app.pyrinas.rythmiseis import rythmiseis
from backend.app.pyrinas.sfalmata import KodikosSfalmatos, SfalmaKanona
from backend.app.ypiresies.entoles_kai_proepiskopiseis import (
    dimiourgise_proepiskopisi,
    katanalwse_proepiskopisi,
    kataxwrise_entoli,
    kleidwse_synallagi,
    pare_epanalipsi,
    pare_proepiskopisi,
)


def xronos_apoikias(synedria: Session) -> datetime:
    """Επιστρέφει τη μοναδική προσομοιωμένη ώρα, με UTC offset."""
    katastasi = synedria.get(KatastasiProsomoiwsis, 1)
    if not katastasi:
        raise SfalmaKanona(KodikosSfalmatos.DEN_VRETHIKE, "Δεν έχει αρχικοποιηθεί το ρολόι.", 503)
    xronos = katastasi.xronos_prosomoiwsis
    return xronos.replace(tzinfo=timezone.utc) if xronos.tzinfo is None else xronos


class YpiresiaApostolwn:
    """Συνδυάζει πραγματικά δεδομένα, φυσικό μοντέλο και κύκλο ζωής εντολής."""

    def __init__(self, synedria: Session):
        self.synedria = synedria
        self.apothiki_apostolwn = ApothikiApostolwn(synedria)
        self.apothiki_koinwn = ApothikiKoinwn(synedria)

    def _pare_oxima(self, id_oximatos: str) -> OximaExerevnis:
        oxima = self.apothiki_apostolwn.pare_oxima_ana_id(id_oximatos)
        if oxima is None:
            raise SfalmaKanona(KodikosSfalmatos.DEN_VRETHIKE, "Το όχημα δεν βρέθηκε.", 404)
        return oxima

    def _perivallon(self) -> dict[str, Any]:
        kindynoi = self.apothiki_apostolwn.pare_kindynous()
        energoi = [kleidi for kleidi in kindynoi if getattr(kleidi, "energi", True)]
        # Η τελευταία συνθήκη κάθε είδους υπερισχύει της ιστορικής του μέτρησης.
        teleftaioi = {}
        for kindynos in energoi:
            teleftaioi.setdefault(kindynos.typos_kindynou, kindynos)
        trexontes = list(teleftaioi.values())
        if not trexontes:
            return {
                "oratotita_m": None,
                "aktinovolia_msv_h": None,
                "proskrousi": False,
                "id_kindynwn": [],
                "poiotita": "apousia",
            }
        palia = any(
            (
                xronos_apoikias(self.synedria)
                - (
                    kindynos.xronos_katagrafis.replace(tzinfo=timezone.utc)
                    if kindynos.xronos_katagrafis.tzinfo is None
                    else kindynos.xronos_katagrafis
                )
            ).total_seconds()
            > rythmiseis.MEGISTI_ILIKIA_METRISIS_LEPTA * 60
            for kindynos in trexontes
        )
        return {
            "poiotita": "palio" if palia else "egkyro",
            "oratotita_m": None if palia else min(kleidi.oratotita_m for kleidi in trexontes),
            "aktinovolia_msv_h": None
            if palia
            else max(kleidi.epipedo_aktinovolias for kleidi in trexontes),
            "proskrousi": any(
                kleidi.typos_kindynou in {"proskrousi", "pithani_proskrousi", "ptwsi_meteoriti"}
                and kleidi.sovarotita in {"ypsili", "krisimi"}
                for kleidi in trexontes
            ),
            "id_kindynwn": [kleidi.id_kindynou for kleidi in trexontes],
        }

    def _stigmiotypo(self, oxima: OximaExerevnis) -> dict[str, Any]:
        return {
            "ekdosi_katastasis": oxima.ekdosi_katastasis,
            "energeia_kwh": oxima.energeia_kwh,
            "xwritikotita_energeias_kwh": oxima.xwritikotita_energeias_kwh,
            "isxys_fortisis_kw": oxima.isxys_fortisis_kw,
            "apostasi_km": oxima.apostasi_apo_vasi_km,
            "taxytita_kmh": oxima.taxytita_kmh,
            "maza_kg": oxima.maza_kg,
            "efedreia_kwh": oxima.efedreia_kwh,
            "isxys_kinisis_kw": oxima.isxys_kinisis_kw,
            "katastasi_epikoinwnias": oxima.katastasi_epikoinwnias,
            "kathysterisi_epikoinwnias_s": oxima.kathysterisi_epikoinwnias_s,
            "katastasi_oximatos": oxima.katastasi_oximatos,
            "perivallon": self._perivallon(),
        }

    def _tilemetria(self, oxima: OximaExerevnis) -> dict[str, Any]:
        return {
            "id_oximatos": oxima.id_oximatos,
            "onoma": oxima.onoma,
            "maza_kg": oxima.maza_kg,
            "maza_fortiou_kg": oxima.maza_fortiou_kg,
            "plithos_plirwmatos": oxima.plithos_plirwmatos,
            "syntetagmeni_x": oxima.syntetagmeni_x,
            "syntetagmeni_y": oxima.syntetagmeni_y,
            "apostasi_apo_vasi_km": oxima.apostasi_apo_vasi_km,
            "taxytita_kmh": oxima.taxytita_kmh,
            "energeia_kwh": oxima.energeia_kwh,
            "xwritikotita_energeias_kwh": oxima.xwritikotita_energeias_kwh,
            "isxys_fortisis_kw": oxima.isxys_fortisis_kw,
            "efedreia_kwh": oxima.efedreia_kwh,
            "mesi_isxys_kw": oxima.mesi_isxys_kw,
            "isxys_kinisis_kw": oxima.isxys_kinisis_kw,
            "voithitiki_isxys_w": oxima.voithitiki_isxys_w,
            "katastasi_oximatos": oxima.katastasi_oximatos,
            "katastasi_epikoinwnias": oxima.katastasi_epikoinwnias,
            "kathysterisi_epikoinwnias_s": oxima.kathysterisi_epikoinwnias_s,
            "katastasi_plirwmatos": "se_oxima" if oxima.plithos_plirwmatos else "xwris_plirwma",
            "ekdosi_katastasis": oxima.ekdosi_katastasis,
            "eidos": "metrimeno",
            "pigi": "prosomoiwmeni_tilemetria",
            "xronos_metrisis": oxima.xronos_teleftaias_tilemetrias
            or datetime(2026, 11, 10, 12, tzinfo=timezone.utc),
            "poiotita": "apousia"
            if oxima.katastasi_epikoinwnias == "apousia"
            else "ypovathmismeno"
            if oxima.katastasi_epikoinwnias == "ypovathmismeni"
            else "egkyro",
            "avevaiotita": "Η τελευταία επιβεβαιωμένη θέση δεν αποδεικνύει τη σημερινή θέση όταν απουσιάζει επικοινωνία."
            if oxima.katastasi_epikoinwnias != "statheri"
            else None,
        }

    def pare_oximata(self) -> list[dict[str, Any]]:
        return [self._tilemetria(o) for o in self.apothiki_apostolwn.pare_oximata()]

    def pare_katastasi_oximatos(self, id_oximatos: str) -> dict[str, Any]:
        oxima = self._pare_oxima(id_oximatos)
        tilemetria = self._tilemetria(oxima)
        tilemetria.update(
            {
                "kinisi": {
                    "apostasi_km": oxima.apostasi_apo_vasi_km,
                    "taxytita_kmh": oxima.taxytita_kmh,
                    "katastasi": oxima.katastasi_oximatos,
                },
                "energeia": {
                    "trexousa_kwh": oxima.energeia_kwh,
                    "efedreia_kwh": oxima.efedreia_kwh,
                    "diathesimi_panw_apo_efedreia_kwh": max(
                        0, oxima.energeia_kwh - oxima.efedreia_kwh
                    ),
                    "mesi_isxys_kw": oxima.mesi_isxys_kw,
                    "isxys_kinisis_kw": oxima.isxys_kinisis_kw,
                },
                "epikoinwnia": {
                    "katastasi": oxima.katastasi_epikoinwnias,
                    "kathysterisi_s": oxima.kathysterisi_epikoinwnias_s,
                },
                "apostoles": [
                    {
                        "id_apostolis": stoixeio_alfa.id_apostolis,
                        "titlos": stoixeio_alfa.titlos,
                        "skopos": stoixeio_alfa.skopos,
                        "katastasi": stoixeio_alfa.katastasi_apostolis,
                        "apostasi_km": stoixeio_alfa.apostasi_km,
                        "ektimwmeni_diarkeia_wres": stoixeio_alfa.ektimwmeni_diarkeia_wres,
                        "apaitoumeni_energeia_kwh": stoixeio_alfa.apaitoumeni_energeia_kwh,
                        "energeia_katanalwtheisa_kwh": stoixeio_alfa.energeia_katanalwtheisa_kwh,
                        "maza_fortiou_kg": stoixeio_alfa.maza_fortiou_kg,
                        "plithos_plirwmatos": stoixeio_alfa.plithos_plirwmatos,
                        "xronos_enarksis": stoixeio_alfa.xronos_enarksis,
                        "xronos_oloklirwsis": stoixeio_alfa.xronos_oloklirwsis,
                        "shmeia_diadromis": [
                            {
                                "seira": stoixeio_sigma.seira,
                                "syntetagmeni_x": stoixeio_sigma.syntetagmeni_x,
                                "syntetagmeni_y": stoixeio_sigma.syntetagmeni_y,
                                "apostasi_apo_proigoumeno_m": stoixeio_sigma.apostasi_apo_proigoumeno_m,
                                "klisi_rad": stoixeio_sigma.klisi_rad,
                            }
                            for stoixeio_sigma in self.apothiki_apostolwn.pare_shmeia_diadromis(
                                stoixeio_alfa.id_apostolis
                            )
                        ],
                    }
                    for stoixeio_alfa in self.apothiki_apostolwn.pare_apostoles_oximatos(
                        id_oximatos
                    )
                ],
            }
        )
        return tilemetria

    def pare_kindynous(self) -> list[dict[str, Any]]:
        return [
            {
                "id_kindynou": kleidi.id_kindynou,
                "typos": kleidi.typos_kindynou,
                "oratotita_m": kleidi.oratotita_m,
                "epipedo_aktinovolias": kleidi.epipedo_aktinovolias,
                "monada_aktinovolias": getattr(kleidi, "monada_aktinovolias", "mSv/h"),
                "sovarotita": kleidi.sovarotita,
                "eidos_dedomenwn": kleidi.eidos_dedomenwn,
                "pigi": getattr(kleidi, "pigi", "prosomoiwsi"),
                "apolyti_avevaiotita": getattr(kleidi, "apolyti_avevaiotita", None),
                "energi": getattr(kleidi, "energi", True),
                "perigrafi": kleidi.perigrafi,
                "xronos": kleidi.xronos_katagrafis,
            }
            for kleidi in self.apothiki_apostolwn.pare_kindynous()
        ]

    def _axiologisi_epistrofis(self, oxima: OximaExerevnis) -> dict[str, Any]:
        perivallon = self._perivallon()
        axiologisi = ypologise_xrono_epistrofis_kai_asfaleia(
            apostasi_km=oxima.apostasi_apo_vasi_km,
            taxytita_kmh=oxima.taxytita_kmh,
            mesi_isxys_kw=oxima.isxys_kinisis_kw,
            diathesimi_energeia_kwh=oxima.energeia_kwh,
            efedreia_asfaleias_kwh=oxima.efedreia_kwh,
            oratotita_m=perivallon["oratotita_m"] or 0.0,
            katastasi_tilemetrias=oxima.katastasi_epikoinwnias,
        )
        aktinovolia_asfalis = (
            perivallon["aktinovolia_msv_h"] is not None and perivallon["aktinovolia_msv_h"] <= 0.5
        )
        axiologisi.update(
            {
                "id_oximatos": oxima.id_oximatos,
                "onoma_oximatos": oxima.onoma,
                "ekdosi_katastasis": oxima.ekdosi_katastasis,
                "katastasi_epikoinwnias": oxima.katastasi_epikoinwnias,
                "kathysterisi_epikoinwnias_s": oxima.kathysterisi_epikoinwnias_s,
                "aktinovolia_asfalis": aktinovolia_asfalis,
                "proskrousi_asfalis": not perivallon["proskrousi"],
                "perivallon": perivallon,
                "paradoxes": [
                    "Σταθερή συνολική ισχύς κίνησης, μαζί με βοηθητικά φορτία.",
                    "Εκπαιδευτικό όριο ορατότητας 300 m και ακτινοβολίας 0,5 mSv/h.",
                    "Η ενεργειακή εφεδρεία αφαιρείται μία φορά.",
                ],
                "id_montelou": "epistrofi_oximatos_v2",
                "eidos": "provlepsi",
                "xronos_metrisis": xronos_apoikias(self.synedria),
            }
        )
        axiologisi["diadromi_asfalis"] = (
            axiologisi["oratotita_asfalis"] and aktinovolia_asfalis and not perivallon["proskrousi"]
        )
        axiologisi["synolika_asfalis_epistrofi"] = (
            axiologisi["synolika_asfalis_epistrofi"] and axiologisi["diadromi_asfalis"]
        )
        if not aktinovolia_asfalis:
            axiologisi["proeidopoiiseis"].append(
                "Υψηλή ή άγνωστη ακτινοβολία: απαιτείται επανεκτίμηση διαδρομής."
            )
        if perivallon["proskrousi"]:
            axiologisi["proeidopoiiseis"].append("Ενεργό συμβάν πιθανής πρόσκρουσης στη διαδρομή.")
        return axiologisi

    def proepiskopisi_anaklisis(
        self, id_oximatos: str, xristis: DedomenaXristi | None = None
    ) -> dict[str, Any]:
        oxima = self._pare_oxima(id_oximatos)
        dedomena = self._axiologisi_epistrofis(oxima)
        dedomena["apaiteitai_epivevaiwsi"] = True
        if xristis:
            dedomena = dimiourgise_proepiskopisi(
                self.synedria,
                "anaklisi_oximatos",
                id_oximatos,
                xristis,
                dedomena,
                self._stigmiotypo(oxima),
            )
            self.synedria.flush()
        return dedomena

    def proepiskopisi_asfalous_stasis(
        self, id_oximatos: str, xristis: DedomenaXristi | None = None
    ) -> dict[str, Any]:
        oxima = self._pare_oxima(id_oximatos)
        dedomena = {
            "id_oximatos": id_oximatos,
            "onoma": oxima.onoma,
            "trexousa_katastasi": oxima.katastasi_oximatos,
            "protinomeni_drasi": "asfalis_stasi",
            "ekdosi_katastasis": oxima.ekdosi_katastasis,
            "katastasi_epikoinwnias": oxima.katastasi_epikoinwnias,
            "kathysterisi_epikoinwnias_s": oxima.kathysterisi_epikoinwnias_s,
            "epiptwseis": {
                "kinisi": "Παύση κίνησης μόνο μετά από επιβεβαιωμένη παραλαβή εντολής.",
                "energeia": "Ισχύς αναμονής 100 W· διατηρείται χωριστά η ισχύς κίνησης.",
                "asfaleia": "Περιορισμός κινδύνου κίνησης· δεν εξαλείφονται οι εξωτερικοί κίνδυνοι.",
                "apostoli": "Αναστολή τυχόν ενεργής αποστολής.",
            },
            "proeidopoiiseis": []
            if oxima.katastasi_epikoinwnias == "statheri"
            else ["Δεν μπορεί να επιβεβαιωθεί η ακινητοποίηση όσο λείπει αξιόπιστο σήμα."],
            "apaiteitai_epivevaiwsi": True,
        }
        if xristis:
            dedomena = dimiourgise_proepiskopisi(
                self.synedria,
                "asfalis_stasi",
                id_oximatos,
                xristis,
                dedomena,
                self._stigmiotypo(oxima),
            )
            self.synedria.flush()
        return dedomena

    def proepiskopisi_apostolis(
        self, id_oximatos: str, dedomena: dict[str, Any], xristis: DedomenaXristi
    ) -> dict[str, Any]:
        oxima = self._pare_oxima(id_oximatos)
        apostasi_km = dedomena["apostasi_km"]
        shmeia = dedomena.get("shmeia_diadromis") or [
            {
                "syntetagmeni_x": apostasi_km * 1000,
                "syntetagmeni_y": 0.0,
                "apostasi_apo_proigoumeno_m": apostasi_km * 1000,
                "klisi_rad": 0.0,
            }
        ]
        apostasi_m = sum(stoixeio_sigma["apostasi_apo_proigoumeno_m"] for stoixeio_sigma in shmeia)
        if not math.isclose(apostasi_m, apostasi_km * 1000, rel_tol=1e-6, abs_tol=0.001):
            raise SfalmaKanona(
                KodikosSfalmatos.AKYRI_TIMI,
                "Το άθροισμα διαδρομής διαφέρει από τη δηλωμένη απόσταση.",
                422,
            )
        xronos_kinisis_wres = 2 * apostasi_km / oxima.taxytita_kmh
        diarkeia = dedomena.get("ektimwmeni_diarkeia_wres", xronos_kinisis_wres)
        if diarkeia < xronos_kinisis_wres:
            raise SfalmaKanona(
                KodikosSfalmatos.AKYRI_TIMI,
                "Η διάρκεια δεν επαρκεί για μετάβαση και επιστροφή.",
                422,
            )
        maza = (
            oxima.maza_kg
            + dedomena.get("maza_fortiou_kg", 0)
            + 80 * dedomena.get("plithos_plirwmatos", 0)
        )
        tmimata = []
        xronos = 0.0
        trexon_x = trexon_y = apostasi_trexousa = 0.0
        proigoumena = []
        for shmeio in shmeia:
            proigoumena.append((trexon_x, trexon_y, apostasi_trexousa))
            diastima = shmeio["apostasi_apo_proigoumeno_m"] / (oxima.taxytita_kmh * 1000)
            _, _, kostos = ypologise_energeia_kinisis_oximatos(
                maza_kg=maza,
                apostasi_m=shmeio["apostasi_apo_proigoumeno_m"],
                klisi_rad=shmeio["klisi_rad"],
                voithitiki_isxys_w=oxima.voithitiki_isxys_w,
                taxytita_m_s=oxima.taxytita_kmh / 3.6,
            )
            tmimata.append(
                {
                    "enarksi_wres": xronos,
                    "liksi_wres": xronos + diastima,
                    "energeia_kwh": kostos,
                    "x_arxi_m": trexon_x,
                    "y_arxi_m": trexon_y,
                    "x_telos_m": shmeio["syntetagmeni_x"],
                    "y_telos_m": shmeio["syntetagmeni_y"],
                    "apostasi_arxi_m": apostasi_trexousa,
                    "apostasi_telos_m": apostasi_trexousa + shmeio["apostasi_apo_proigoumeno_m"],
                }
            )
            trexon_x, trexon_y = shmeio["syntetagmeni_x"], shmeio["syntetagmeni_y"]
            apostasi_trexousa += shmeio["apostasi_apo_proigoumeno_m"]
            xronos += diastima
        xronos_epistrofis = diarkeia - xronos
        if xronos_epistrofis > xronos:
            tmimata.append(
                {
                    "enarksi_wres": xronos,
                    "liksi_wres": xronos_epistrofis,
                    "energeia_kwh": (xronos_epistrofis - xronos) * oxima.voithitiki_isxys_w / 1000,
                    "x_arxi_m": trexon_x,
                    "y_arxi_m": trexon_y,
                    "x_telos_m": trexon_x,
                    "y_telos_m": trexon_y,
                    "apostasi_arxi_m": apostasi_trexousa,
                    "apostasi_telos_m": apostasi_trexousa,
                }
            )
        xronos = xronos_epistrofis
        for seira in range(len(shmeia) - 1, -1, -1):
            shmeio = shmeia[seira]
            arxiko_x, arxiko_y, arxiki_apostasi = proigoumena[seira]
            diastima = shmeio["apostasi_apo_proigoumeno_m"] / (oxima.taxytita_kmh * 1000)
            _, _, kostos = ypologise_energeia_kinisis_oximatos(
                maza_kg=maza,
                apostasi_m=shmeio["apostasi_apo_proigoumeno_m"],
                klisi_rad=-shmeio["klisi_rad"],
                voithitiki_isxys_w=oxima.voithitiki_isxys_w,
                taxytita_m_s=oxima.taxytita_kmh / 3.6,
            )
            tmimata.append(
                {
                    "enarksi_wres": xronos,
                    "liksi_wres": xronos + diastima,
                    "energeia_kwh": kostos,
                    "x_arxi_m": trexon_x,
                    "y_arxi_m": trexon_y,
                    "x_telos_m": arxiko_x,
                    "y_telos_m": arxiko_y,
                    "apostasi_arxi_m": apostasi_trexousa,
                    "apostasi_telos_m": arxiki_apostasi,
                }
            )
            trexon_x, trexon_y, apostasi_trexousa = arxiko_x, arxiko_y, arxiki_apostasi
            xronos += diastima
        energeia = sum(stoixeio_taf["energeia_kwh"] for stoixeio_taf in tmimata)
        axiologisi = self._axiologisi_epistrofis(oxima)
        apotelesma = {
            "id_oximatos": id_oximatos,
            "zitoumeni": {**dedomena, "shmeia_diadromis": shmeia},
            "tmimata_prosomoiwsis": tmimata,
            "apostasi_km": apostasi_km,
            "synoliki_diadromi_km": 2 * apostasi_km,
            "xronos_kinisis_wres": xronos_kinisis_wres,
            "ektimwmeni_diarkeia_wres": diarkeia,
            "ektimwmeni_energeia_kwh": round(energeia, 8),
            "diathesimi_energeia_oximatos_kwh": oxima.energeia_kwh,
            "energeia_meta_epistrofi_kwh": round(oxima.energeia_kwh - energeia, 8),
            "energeiaka_efikto": oxima.energeia_kwh - energeia >= oxima.efedreia_kwh,
            "diadromi_asfalis": axiologisi["diadromi_asfalis"],
            "epikoinwnia_asfalis": axiologisi["epikoinwnia_asfalis"],
            "paradoxes": [
                "Νέα αποστολή ξεκινά από τη βάση. Διαδρομή μετάβασης και ίδια διαδρομή αντίστροφα για επιστροφή.",
                "Η μάζα περιλαμβάνει φορτίο και εκπαιδευτική παραδοχή 80 kg ανά μέλος πληρώματος.",
                "Η διάρκεια περιλαμβάνει τον χρόνο επιστημονικών εργασιών με βοηθητικά φορτία.",
            ],
            "id_montelou": "diadromi_maza_klisi_v2",
            "apaiteitai_epivevaiwsi": True,
            "proeidopoiiseis": axiologisi["proeidopoiiseis"],
        }
        apotelesma = dimiourgise_proepiskopisi(
            self.synedria,
            "dimiourgia_apostolis",
            id_oximatos,
            xristis,
            apotelesma,
            self._stigmiotypo(oxima),
        )
        self.synedria.flush()
        return apotelesma

    def dimiourgia_apostolis(
        self,
        id_oximatos: str,
        id_proepiskopisis: str,
        xristis: DedomenaXristi,
        kleidi: str | None = None,
    ) -> dict[str, Any]:
        kleidwse_synallagi(self.synedria)
        aitima = {"id_proepiskopisis": id_proepiskopisis}
        epanalipsi = pare_epanalipsi(
            self.synedria, xristis, "dimiourgia_apostolis", id_oximatos, kleidi, aitima
        )
        if epanalipsi is not None:
            return epanalipsi
        oxima = self._pare_oxima(id_oximatos)
        proep = pare_proepiskopisi(
            self.synedria,
            id_proepiskopisis,
            "dimiourgia_apostolis",
            id_oximatos,
            xristis,
            self._stigmiotypo(oxima),
        )
        if oxima.apostasi_apo_vasi_km > 1e-6:
            raise SfalmaKanona(
                KodikosSfalmatos.SYNTHIKI_SYGGROUSIS,
                "Νέα αποστολή ξεκινά από τη βάση· προηγείται επιστροφή του οχήματος.",
                409,
            )
        if not proep["energeiaka_efikto"]:
            raise SfalmaKanona(
                KodikosSfalmatos.ANEPARKIS_ENERGEIA,
                "Η αποστολή δεν διατηρεί την ελάχιστη εφεδρεία επιστροφής.",
                409,
            )
        if not proep["diadromi_asfalis"] or not proep["epikoinwnia_asfalis"]:
            raise SfalmaKanona(
                KodikosSfalmatos.MH_ASPHALIS_KATASTASI,
                "Δεν επιτρέπεται έναρξη αποστολής με ανασφαλή διαδρομή ή μη επιβεβαιωμένη επικοινωνία.",
                409,
            )
        yparxousa = self.synedria.scalars(
            select(ApostoliOximatos).where(
                ApostoliOximatos.id_oximatos == id_oximatos,
                ApostoliOximatos.katastasi_apostolis.in_(
                    ["programmatismeni", "se_anamoni", "se_exelixi"]
                ),
            )
        ).first()
        if yparxousa:
            raise SfalmaKanona(
                KodikosSfalmatos.SYNTHIKI_SYGGROUSIS,
                "Υπάρχει ήδη ενεργή ή προγραμματισμένη αποστολή.",
                409,
            )
        katanalwse_proepiskopisi(self.synedria, id_proepiskopisis)
        zitoumeni = proep["zitoumeni"]
        apostoli = ApostoliOximatos(
            id_apostolis=f"apost_{uuid.uuid4().hex}",
            id_oximatos=id_oximatos,
            titlos=zitoumeni["titlos"],
            skopos=zitoumeni["skopos"],
            katastasi_apostolis="se_anamoni",
            xronos_enarksis=xronos_apoikias(self.synedria),
            apostasi_km=proep["apostasi_km"],
            ektimwmeni_diarkeia_wres=proep["ektimwmeni_diarkeia_wres"],
            apaitoumeni_energeia_kwh=proep["ektimwmeni_energeia_kwh"],
            energeia_katanalwtheisa_kwh=0,
            maza_fortiou_kg=zitoumeni.get("maza_fortiou_kg", 0),
            plithos_plirwmatos=zitoumeni.get("plithos_plirwmatos", 0),
        )
        self.synedria.add(apostoli)
        self.synedria.flush()
        for seira, shmeio in enumerate(zitoumeni["shmeia_diadromis"]):
            self.synedria.add(
                ShmeioDiadromis(id_apostolis=apostoli.id_apostolis, seira=seira, **shmeio)
            )
        apantisi = {
            "id_apostolis": apostoli.id_apostolis,
            "id_oximatos": id_oximatos,
            "katastasi": "se_anamoni",
            "katastasi_entolis": "egkrithike",
            "minyma": "Το σχέδιο αποθηκεύτηκε· αναμένεται επιβεβαιωμένη έναρξη στο επόμενο βήμα.",
        }
        entoli = kataxwrise_entoli(
            self.synedria,
            xristis,
            "apostoles",
            "dimiourgia_apostolis",
            id_oximatos,
            aitima,
            apantisi,
            katastasi="egkrithike",
            id_proepiskopisis=id_proepiskopisis,
            kleidi=kleidi,
        )
        entoli.dedomena_aitimatos = {
            **aitima,
            "id_apostolis": apostoli.id_apostolis,
            "xronos_apostolis": xronos_apoikias(self.synedria).isoformat(),
        }
        apostoli.sxedio = {**zitoumeni, "tmimata_prosomoiwsis": proep["tmimata_prosomoiwsis"]}
        apostoli.id_entolis = entoli.id_entolis
        apantisi["id_entolis"] = entoli.id_entolis
        entoli.apotelesma = dict(apantisi)
        self.synedria.commit()
        return apantisi

    def _ektelese_xeirismo(
        self,
        id_oximatos: str,
        xristis: DedomenaXristi,
        drasi: str,
        id_proepiskopisis: str | None,
        kleidi: str | None,
        desmefsi_synallagis: bool,
    ) -> dict[str, Any]:
        if desmefsi_synallagis:
            kleidwse_synallagi(self.synedria)
        aitima = {"id_proepiskopisis": id_proepiskopisis}
        epanalipsi = pare_epanalipsi(self.synedria, xristis, drasi, id_oximatos, kleidi, aitima)
        if epanalipsi is not None:
            return epanalipsi
        oxima = self._pare_oxima(id_oximatos)
        ekkremis = self.synedria.scalars(
            select(Entoli).where(
                Entoli.id_ontotitas == id_oximatos,
                Entoli.drasi == drasi,
                Entoli.katastasi.in_(["avevaio", "se_anamoni", "egkrithike", "se_exelixi"]),
            )
        ).first()
        if ekkremis:
            raise SfalmaKanona(
                KodikosSfalmatos.SYNTHIKI_SYGGROUSIS,
                "Υπάρχει ήδη εκκρεμής εντολή της ίδιας ενέργειας· χρησιμοποιήστε το αρχικό κλειδί επανάληψης.",
                409,
            )

        if not id_proepiskopisis:
            raise SfalmaKanona(
                KodikosSfalmatos.AKYRI_TIMI,
                "Απαιτείται έγκυρη προεπισκόπηση πριν από την εντολή.",
                422,
            )
        pare_proepiskopisi(
            self.synedria, id_proepiskopisis, drasi, id_oximatos, xristis, self._stigmiotypo(oxima)
        )
        if drasi == "anaklisi_oximatos":
            axiologisi = self._axiologisi_epistrofis(oxima)
            if not axiologisi["energeiaka_efikto"]:
                raise SfalmaKanona(
                    KodikosSfalmatos.ANEPARKIS_ENERGEIA,
                    "Ανεπαρκής ενέργεια επιστροφής με εφεδρεία.",
                    409,
                )
            if not axiologisi["diadromi_asfalis"]:
                raise SfalmaKanona(
                    KodikosSfalmatos.MH_ASPHALIS_KATASTASI,
                    "Η επιστροφή είναι ανασφαλής· προτείνεται ασφαλής στάση.",
                    409,
                )
        katanalwse_proepiskopisi(self.synedria, id_proepiskopisis)
        katastasi = (
            "avevaio"
            if oxima.katastasi_epikoinwnias != "statheri"
            else "se_anamoni"
            if oxima.kathysterisi_epikoinwnias_s > 0
            else "oloklirothike"
            if drasi == "asfalis_stasi"
            else "se_exelixi"
        )
        if katastasi in {"oloklirothike", "se_exelixi"}:
            self._efarmose_xeirismo(oxima, drasi)
        apantisi = {
            "id_oximatos": id_oximatos,
            "katastasi_entolis": katastasi,
            "katastasi_oximatos": oxima.katastasi_oximatos,
            "minyma": "Η εντολή εφαρμόστηκε μετά από προσομοιωμένη επιβεβαίωση παραλαβής."
            if katastasi in {"oloklirothike", "se_exelixi"}
            else "Η εντολή παραμένει μη επιβεβαιωμένη λόγω απώλειας ή καθυστέρησης επικοινωνίας.",
        }
        entoli = kataxwrise_entoli(
            self.synedria,
            xristis,
            "apostoles",
            drasi,
            id_oximatos,
            aitima,
            apantisi,
            katastasi=katastasi,
            id_proepiskopisis=id_proepiskopisis,
            kleidi=kleidi,
        )
        entoli.dedomena_aitimatos = {
            **aitima,
            "xronos_apostolis": xronos_apoikias(self.synedria).isoformat(),
            "apostasi_enarksis_km": oxima.apostasi_apo_vasi_km,
        }
        apantisi["id_entolis"] = entoli.id_entolis
        entoli.apotelesma = dict(apantisi)
        if desmefsi_synallagis:
            self.synedria.commit()
        return apantisi

    def _efarmose_xeirismo(self, oxima: OximaExerevnis, drasi: str) -> None:
        if drasi == "asfalis_stasi":
            oxima.katastasi_oximatos = "asfalis_stasi"
            oxima.mesi_isxys_kw = oxima.voithitiki_isxys_w / 1000
            for apostoli in self.apothiki_apostolwn.pare_apostoles_oximatos(oxima.id_oximatos):
                if apostoli.katastasi_apostolis in {"se_exelixi", "se_anamoni"}:
                    apostoli.katastasi_apostolis = "anastoli"
        else:
            for apostoli in self.apothiki_apostolwn.pare_apostoles_oximatos(oxima.id_oximatos):
                if apostoli.katastasi_apostolis == "se_exelixi":
                    apostoli.katastasi_apostolis = "anastoli"
            oxima.katastasi_oximatos = "epistrofi_se_exelixi"
            oxima.mesi_isxys_kw = oxima.isxys_kinisis_kw
        oxima.ekdosi_katastasis += 1

    def ektelesi_anaklisis(
        self,
        id_oximatos: str,
        xristis: DedomenaXristi,
        id_proepiskopisis: str | None = None,
        kleidi: str | None = None,
        desmefsi_synallagis: bool = True,
    ) -> dict[str, Any]:
        return self._ektelese_xeirismo(
            id_oximatos,
            xristis,
            "anaklisi_oximatos",
            id_proepiskopisis,
            kleidi,
            desmefsi_synallagis,
        )

    def ektelesi_asfalous_stasis(
        self,
        id_oximatos: str,
        xristis: DedomenaXristi,
        id_proepiskopisis: str | None = None,
        kleidi: str | None = None,
        desmefsi_synallagis: bool = True,
    ) -> dict[str, Any]:
        return self._ektelese_xeirismo(
            id_oximatos, xristis, "asfalis_stasi", id_proepiskopisis, kleidi, desmefsi_synallagis
        )

    def anavoli_apostolis(
        self, id_oximatos: str, id_apostolis: str, xristis: DedomenaXristi
    ) -> dict[str, Any]:
        kleidwse_synallagi(self.synedria)
        self._pare_oxima(id_oximatos)
        apostoli = self.apothiki_apostolwn.pare_apostoli_ana_id(id_apostolis)
        if apostoli is None or apostoli.id_oximatos != id_oximatos:
            raise SfalmaKanona(
                KodikosSfalmatos.DEN_VRETHIKE, "Η αποστολή δεν ανήκει στο συγκεκριμένο όχημα.", 404
            )
        if apostoli.katastasi_apostolis not in {"programmatismeni", "se_anamoni"}:
            raise SfalmaKanona(
                KodikosSfalmatos.MH_EPITREPTI_METAVASI,
                "Αναβάλλεται μόνο αποστολή που δεν έχει αρχίσει.",
                409,
            )
        apostoli.katastasi_apostolis = "anavoli"
        if apostoli.id_entolis:
            entoli = self.synedria.get(Entoli, apostoli.id_entolis)
            if entoli:
                from backend.app.prosomoiwsi.prosomoiosis_apostolwn import _metavasi

                _metavasi(
                    self.synedria,
                    entoli,
                    "akyrothike",
                    xronos_apoikias(self.synedria),
                    "Η αποστολή αναβλήθηκε πριν από την αναχώρηση.",
                )
        apantisi = {
            "id_apostolis": id_apostolis,
            "id_oximatos": id_oximatos,
            "katastasi": "anavoli",
            "minyma": "Η εκκρεμής αποστολή αναβλήθηκε χωρίς κατανάλωση ενέργειας.",
        }
        kataxwrise_entoli(
            self.synedria,
            xristis,
            "apostoles",
            "anavoli_apostolis",
            id_oximatos,
            {"id_apostolis": id_apostolis},
            apantisi,
        )
        self.synedria.commit()
        return apantisi
