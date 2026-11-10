"""Προεπισκοπήσεις, δεσμεύσεις και ελεγχόμενες εντολές νερού/ενέργειας."""

import math
import uuid
from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.apothikes.apothiki_koinwn import ApothikiKoinwn
from backend.app.apothikes.apothiki_porwn import ApothikiPorwn
from backend.app.fysika_montela.fysika_montela import (
    ypologise_ilektriko_isozygio_kai_autonomia,
    ypologise_isxy_fwtovoltaikou,
)
from backend.app.montela.poroi import (
    ProgrammaAnakyklwsis,
    ProgrammaArdefsis,
    ProgrammaFwtismou,
)
from backend.app.prosomoiwsi.prosomoiosis_porwn import (
    ENERGES_KATASTASEIS,
    anavlito_fortio_diathesimo,
    efarmose_pausi_anavlitwn,
    enimerwse_fortia_programmatwn,
    liksi_programmatos,
    se_utc,
)
from backend.app.pyrinas.asfaleia import RolosXristi, elegxe_dikaiwma
from backend.app.pyrinas.sfalmata import KodikosSfalmatos, SfalmaKanona
from backend.app.ypiresies.entoles_kai_proepiskopiseis import (
    dimiourgise_proepiskopisi,
    katanalwse_proepiskopisi,
    kataxwrise_entoli,
    kleidwse_synallagi,
    pare_epanalipsi,
    pare_proepiskopisi,
)


def _sphalma(minyma: str, kodikos=KodikosSfalmatos.AKYRI_TIMI, katastasi_http=400):
    raise SfalmaKanona(kodikos=kodikos, minyma=minyma, katastasi_http=katastasi_http)


class YpiresiaPorwn:
    """Ενιαίος ιδιοκτήτης επιχειρησιακών κανόνων και συναλλαγών πόρων."""

    def __init__(self, synedria: Session):
        self.synedria = synedria
        self.apothiki_porwn = ApothikiPorwn(synedria)
        self.apothiki_koinwn = ApothikiKoinwn(synedria)

    def _twra(self):
        return se_utc(self.apothiki_koinwn.pare_katastasi_prosomoiwsis().xronos_prosomoiwsis)

    def _th(self, id_thermokipiou):
        thermokipio = self.apothiki_porwn.pare_thermokipio_ana_id(id_thermokipiou)
        if not thermokipio:
            _sphalma("Το θερμοκήπιο δεν βρέθηκε.", KodikosSfalmatos.DEN_VRETHIKE, 404)
        return thermokipio

    def _zwni(self, id_thermokipiou, id_zwnis):
        self._th(id_thermokipiou)
        zwni = self.apothiki_porwn.pare_zwni_ana_id(id_zwnis)
        if not zwni or zwni.id_thermokipiou != id_thermokipiou:
            _sphalma(
                "Η ζώνη δεν ανήκει στο ζητούμενο θερμοκήπιο.", KodikosSfalmatos.DEN_VRETHIKE, 404
            )
        return zwni

    def _thetikos(self, timi, onoma):
        if not math.isfinite(timi) or timi <= 0:
            _sphalma(f"Το πεδίο {onoma} πρέπει να είναι θετικό και πεπερασμένο.")

    def _xronos(self, xronos):
        twra = self._twra()
        if xronos is None:
            return twra
        if xronos.tzinfo is None:
            _sphalma("Ο χρόνος πρέπει να περιλαμβάνει ζώνη ώρας UTC ή ρητή μετατόπιση.")
        if se_utc(xronos) < twra:
            _sphalma("Δεν επιτρέπεται προγραμματισμός στο παρελθόν.")
        return se_utc(xronos)

    def _metriseis(self, id_zwnis=None):
        from backend.app.ypiresies.metriseis_kai_poiotita import pare_egkyri_metrisi

        pare_egkyri_metrisi(self.synedria, "aisth_nero")
        if id_zwnis:
            pare_egkyri_metrisi(self.synedria, "aisth_ygrasia_" + id_zwnis)

    def _stigmiotypo(self):
        return {
            "xronos": self._twra().isoformat(),
            "fwtovoltaika": [
                [
                    f.id_fwtovoltaikou,
                    f.apodosi_eta,
                    f.epifaneia_m2,
                    f.aktinovolia_w_m2,
                    f.syntelestis_epikathisis_f,
                ]
                for f in self.apothiki_porwn.pare_fwtovoltaika()
            ],
            "thermokipia": [
                [
                    th.id_thermokipiou,
                    th.ekdosi_katastasis,
                    th.diathesimi_ardefsi,
                    th.diathesimos_fwtismos,
                ]
                for th in self.apothiki_porwn.pare_thermokipia()
            ],
            "pausi": self.apothiki_koinwn.pare_katastasi_prosomoiwsis().pausi_anavlitwn,
            "dexamenes": [
                [
                    stoixeio_delta.id_dexamenis,
                    stoixeio_delta.ekdosi_katastasis,
                    stoixeio_delta.trexwn_ogkos_l,
                    stoixeio_delta.rythmos_diarrois_l_h,
                ]
                for stoixeio_delta in self.apothiki_porwn.pare_dexamenes_nerou()
            ],
            "programmata": [
                [stoixeio_pi.id_programmatos, stoixeio_pi.katastasi]
                for typos in (ProgrammaArdefsis, ProgrammaAnakyklwsis, ProgrammaFwtismou)
                for stoixeio_pi in self.synedria.scalars(
                    select(typos).order_by(typos.id_programmatos)
                )
            ],
            "fortia": [
                [stoixeio_zita.id_fortiou, stoixeio_zita.energo, stoixeio_zita.isxys_kw]
                for stoixeio_zita in self.apothiki_porwn.pare_energeiaka_fortia()
            ],
            "syssoreftes": [
                [stoixeio_sigma.id_syssorefti, stoixeio_sigma.energeia_kwh]
                for stoixeio_sigma in self.apothiki_porwn.pare_syssoreftes()
            ],
        }

    def _desmevmeno(self, id_dexamenis):
        ardefsi = sum(
            max(0, stoixeio_pi.posotita_nerou_l - stoixeio_pi.ektelestheisa_posotita_l)
            for stoixeio_pi in self.synedria.scalars(
                select(ProgrammaArdefsis).where(ProgrammaArdefsis.id_dexamenis == id_dexamenis)
            )
            if stoixeio_pi.katastasi in ENERGES_KATASTASEIS
        )
        anakyklwsi = sum(
            max(0, stoixeio_pi.posotita_eisodou_l - stoixeio_pi.ektelestheisa_posotita_l)
            for stoixeio_pi in self.synedria.scalars(
                select(ProgrammaAnakyklwsis).where(
                    ProgrammaAnakyklwsis.id_dexamenis_pigis == id_dexamenis
                )
            )
            if stoixeio_pi.katastasi in ENERGES_KATASTASEIS
        )
        return ardefsi + anakyklwsi

    def _dexameni(self, id_dexamenis=None, typos="katharo"):
        dexameni = (
            self.apothiki_porwn.pare_dexameni_ana_id(id_dexamenis)
            if id_dexamenis
            else next(
                (
                    stoixeio_delta
                    for stoixeio_delta in self.apothiki_porwn.pare_dexamenes_nerou()
                    if stoixeio_delta.typos_nerou == typos
                ),
                None,
            )
        )
        if not dexameni or dexameni.typos_nerou != typos:
            _sphalma(
                "Δεν βρέθηκε δεξαμενή του κατάλληλου τύπου νερού.",
                KodikosSfalmatos.DEN_VRETHIKE,
                404,
            )
        return dexameni

    def _elegxe_nero(self, dexameni, posotita):
        diathesimo = (
            dexameni.trexwn_ogkos_l
            - dexameni.efedreia_asfaleias_l
            - self._desmevmeno(dexameni.id_dexamenis)
        )
        if posotita > diathesimo + 1e-8:
            raise SfalmaKanona(
                KodikosSfalmatos.ANEPARKES_NERO,
                "Το διαθέσιμο νερό μετά την εφεδρεία και τις προηγούμενες δεσμεύσεις δεν επαρκεί.",
                409,
                {
                    "diathesimo_l": max(0, diathesimo),
                    "zitoumeno_l": posotita,
                    "efedreia_asfaleias_l": dexameni.efedreia_asfaleias_l,
                },
            )
        return max(0, diathesimo)

    def _elegxe_xwritikotita_anakyklwsis(self, dexameni, epistrofi_l):
        """Δεσμεύει και μελλοντική χωρητικότητα καθαρού νερού χωρίς υπερκάλυψη."""
        desmevmeni_epistrofi_l = sum(
            max(0.0, stoixeio_pi.posotita_eisodou_l - stoixeio_pi.ektelestheisa_posotita_l)
            * stoixeio_pi.apodosi_anakyklwsis
            for stoixeio_pi in self.synedria.scalars(
                select(ProgrammaAnakyklwsis).where(
                    ProgrammaAnakyklwsis.id_dexamenis == dexameni.id_dexamenis
                )
            )
            if stoixeio_pi.katastasi in ENERGES_KATASTASEIS
        )
        if (
            dexameni.trexwn_ogkos_l + desmevmeni_epistrofi_l + epistrofi_l
            > dexameni.xwritikotita_l + 1e-8
        ):
            _sphalma(
                "Ανεπαρκής χωρητικότητα μετά τις προηγούμενες δεσμεύσεις ανακύκλωσης.",
                KodikosSfalmatos.SYNTHIKI_SYGGROUSIS,
                409,
            )

    def _elegxe_kiklo_anakyklwsis(self, id_dexamenis, enarksi, liksi):
        """Η ενιαία μονάδα ανακύκλωσης δεν εκτελεί επικαλυπτόμενους κύκλους."""
        for programma in self.synedria.scalars(
            select(ProgrammaAnakyklwsis).where(ProgrammaAnakyklwsis.id_dexamenis == id_dexamenis)
        ):
            if (
                programma.katastasi in ENERGES_KATASTASEIS
                and se_utc(programma.xronos_enarksis) < liksi
                and liksi_programmatos(programma) > enarksi
            ):
                _sphalma(
                    "Υπάρχει επικαλυπτόμενος κύκλος στην ίδια μονάδα ανακύκλωσης.",
                    KodikosSfalmatos.SYNTHIKI_SYGGROUSIS,
                    409,
                )

    def _elegxe_epikalypsi(self, typos, id_zwnis, enarksi, liksi):
        for programma in self.synedria.scalars(select(typos).where(typos.id_zwnis == id_zwnis)):
            if (
                programma.katastasi in ENERGES_KATASTASEIS
                and se_utc(programma.xronos_enarksis) < liksi
                and liksi_programmatos(programma) > enarksi
            ):
                _sphalma(
                    "Υπάρχει επικαλυπτόμενο πρόγραμμα στην ίδια ζώνη.",
                    KodikosSfalmatos.SYNTHIKI_SYGGROUSIS,
                    409,
                )

    def pare_thermokipia(self):
        return [
            {
                "id_thermokipiou": stoixeio_taf.id_thermokipiou,
                "onoma": stoixeio_taf.onoma,
                "thermokrasia_k": stoixeio_taf.thermokrasia_k,
                "ygrasia_aera": stoixeio_taf.ygrasia_aera,
                "ekdosi_katastasis": stoixeio_taf.ekdosi_katastasis,
                "diathesimi_ardefsi": stoixeio_taf.diathesimi_ardefsi,
                "diathesimos_fwtismos": stoixeio_taf.diathesimos_fwtismos,
            }
            for stoixeio_taf in self.apothiki_porwn.pare_thermokipia()
        ]

    def pare_zwnes(self, id_thermokipiou):
        self._th(id_thermokipiou)
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
            for z in self.apothiki_porwn.pare_zwnes_thermokipiou(id_thermokipiou)
        ]

    def pare_katastasi_nerou(self):
        dexamenes = self.apothiki_porwn.pare_dexamenes_nerou()
        kathares = [
            stoixeio_delta
            for stoixeio_delta in dexamenes
            if stoixeio_delta.typos_nerou == "katharo"
        ]
        return {
            "dexamenes": [
                {
                    "id_dexamenis": stoixeio_delta.id_dexamenis,
                    "onoma": stoixeio_delta.onoma,
                    "typos_nerou": stoixeio_delta.typos_nerou,
                    "xwritikotita_l": stoixeio_delta.xwritikotita_l,
                    "trexwn_ogkos_l": stoixeio_delta.trexwn_ogkos_l,
                    "efedreia_asfaleias_l": stoixeio_delta.efedreia_asfaleias_l,
                    "desmevmeno_l": self._desmevmeno(stoixeio_delta.id_dexamenis),
                    "diathesimo_panw_apo_efedreia_l": max(
                        0,
                        stoixeio_delta.trexwn_ogkos_l
                        - stoixeio_delta.efedreia_asfaleias_l
                        - self._desmevmeno(stoixeio_delta.id_dexamenis),
                    ),
                    "ekdosi_katastasis": stoixeio_delta.ekdosi_katastasis,
                    "rythmos_diarrois_l_h": stoixeio_delta.rythmos_diarrois_l_h,
                }
                for stoixeio_delta in dexamenes
            ],
            "synolika": {
                "xwritikotita_l": sum(stoixeio_delta.xwritikotita_l for stoixeio_delta in kathares),
                "trexwn_ogkos_l": sum(stoixeio_delta.trexwn_ogkos_l for stoixeio_delta in kathares),
                "efedreia_l": sum(
                    stoixeio_delta.efedreia_asfaleias_l for stoixeio_delta in kathares
                ),
                "desmevmeno_l": sum(
                    self._desmevmeno(stoixeio_delta.id_dexamenis) for stoixeio_delta in kathares
                ),
                "diathesimo_xrisimo_l": sum(
                    max(
                        0,
                        stoixeio_delta.trexwn_ogkos_l
                        - stoixeio_delta.efedreia_asfaleias_l
                        - self._desmevmeno(stoixeio_delta.id_dexamenis),
                    )
                    for stoixeio_delta in kathares
                ),
            },
            "roes": [
                {
                    "id_rois": stoixeio_ro.id_rois,
                    "id_dexamenis": stoixeio_ro.id_dexamenis,
                    "typos": stoixeio_ro.typos_rois,
                    "rythmos_l_h": stoixeio_ro.rythmos_l_h,
                    "perigrafi": stoixeio_ro.perigrafi,
                    "xronos": stoixeio_ro.xronos_katagrafis,
                    "xronos_enarksis": stoixeio_ro.xronos_enarksis,
                    "xronos_liksis": stoixeio_ro.xronos_liksis,
                    "energi": stoixeio_ro.energi,
                    "id_programmatos": stoixeio_ro.id_programmatos,
                }
                for stoixeio_ro in self.apothiki_porwn.pare_roes_nerou()
            ],
        }

    def _provlepsi_stathmis(self, wres=24):
        """Υποθετική στάθμη στο τέλος ορίζοντα, με την πραγματική χρονική επικάλυψη προγραμμάτων."""
        apo = self._twra()
        ews = apo + timedelta(hours=wres)
        dexamenes = self.apothiki_porwn.pare_dexamenes_nerou()
        times = {
            d.id_dexamenis: d.trexwn_ogkos_l - d.rythmos_diarrois_l_h * wres for d in dexamenes
        }
        for roi in self.apothiki_porwn.pare_roes_nerou():
            if not roi.energi or roi.id_programmatos:
                continue
            diarkeia = (
                max(
                    0,
                    (
                        min(ews, se_utc(roi.xronos_liksis) if roi.xronos_liksis else ews)
                        - max(apo, se_utc(roi.xronos_enarksis) if roi.xronos_enarksis else apo)
                    ).total_seconds(),
                )
                / 3600
            )
            prosimo = (
                1
                if roi.typos_rois == "eisroi"
                else -1
                if roi.typos_rois in {"analwsi", "diarros"}
                else 0
            )
            times[roi.id_dexamenis] += prosimo * roi.rythmos_l_h * diarkeia
        for montelo in [ProgrammaArdefsis, ProgrammaAnakyklwsis]:
            for programma in self.synedria.scalars(select(montelo)):
                if programma.katastasi not in ENERGES_KATASTASEIS:
                    continue
                if (
                    isinstance(programma, ProgrammaAnakyklwsis)
                    and self.apothiki_koinwn.pare_katastasi_prosomoiwsis().pausi_anavlitwn
                ):
                    continue
                diarkeia = max(
                    0,
                    (
                        min(ews, liksi_programmatos(programma))
                        - max(apo, se_utc(programma.xronos_enarksis))
                    ).total_seconds(),
                )
                synoliki = (
                    programma.posotita_nerou_l
                    if isinstance(programma, ProgrammaArdefsis)
                    else programma.posotita_eisodou_l
                )
                posotita = min(
                    max(0, synoliki - programma.ektelestheisa_posotita_l),
                    synoliki * diarkeia / (programma.diarkeia_lepta * 60),
                )
                if isinstance(programma, ProgrammaArdefsis):
                    times[programma.id_dexamenis] -= posotita
                else:
                    times[programma.id_dexamenis_pigis] -= posotita
                    times[programma.id_dexamenis] += posotita * programma.apodosi_anakyklwsis
        return sum(
            min(d.xwritikotita_l, max(0, times[d.id_dexamenis]))
            for d in dexamenes
            if d.typos_nerou == "katharo"
        )

    def pare_isozygio_nerou(self):
        katastasi = self.pare_katastasi_nerou()
        twra = self._twra()
        roes = [
            stoixeio_ro
            for stoixeio_ro in katastasi["roes"]
            if stoixeio_ro["energi"]
            and (
                not stoixeio_ro["xronos_enarksis"] or se_utc(stoixeio_ro["xronos_enarksis"]) <= twra
            )
            and (not stoixeio_ro["xronos_liksis"] or se_utc(stoixeio_ro["xronos_liksis"]) > twra)
        ]
        eisroi = sum(
            stoixeio_ro["rythmos_l_h"] for stoixeio_ro in roes if stoixeio_ro["typos"] == "eisroi"
        )
        ekroi = sum(
            stoixeio_ro["rythmos_l_h"]
            for stoixeio_ro in roes
            if stoixeio_ro["typos"] in {"analwsi", "diarros"}
        ) + sum(
            stoixeio_delta.rythmos_diarrois_l_h
            for stoixeio_delta in self.apothiki_porwn.pare_dexamenes_nerou()
            if stoixeio_delta.typos_nerou == "katharo"
        )
        return {
            "apothema": katastasi["synolika"],
            "roes_l_h": {
                "synolikes_eisroes": eisroi,
                "synolikes_ekroes": ekroi,
                "katharos_rythmos": eisroi - ekroi,
            },
            "provlepsi_24h_l": self._provlepsi_stathmis(),
            "paradoxes": [
                "Σταθερές συνθήκες για 24 ώρες και αναλογική εκτέλεση μόνο μέσα στον χρονικό ορίζοντα, εφόσον επαρκέσουν ενέργεια και νερό.",
                "Η ανακύκλωση αφαιρεί γκρίζο και επιστρέφει καθαρό νερό. Η τελική στάθμη περιορίζεται στη χωρητικότητα· οι πραγματικές απώλειες καταγράφονται κατά την εκτέλεση.",
            ],
        }

    def proepiskopisi_ardefsis(
        self,
        id_thermokipiou,
        id_zwnis,
        posotita_nerou_l,
        diarkeia_lepta=30,
        xronos_enarksis=None,
        xristis=None,
        id_dexamenis=None,
    ):
        if xristis:
            elegxe_dikaiwma(xristis, RolosXristi.YPEFTHYNOS_PORWN, id_ontotitas=id_thermokipiou)
        self._thetikos(posotita_nerou_l, "posotita_nerou_l")
        self._thetikos(diarkeia_lepta, "diarkeia_lepta")
        zwni = self._zwni(id_thermokipiou, id_zwnis)
        thermokipio = self._th(id_thermokipiou)
        if not thermokipio.diathesimi_ardefsi:
            _sphalma(
                "Ο εξοπλισμός άρδευσης δεν είναι διαθέσιμος.",
                KodikosSfalmatos.MH_ASPHALIS_KATASTASI,
                409,
            )
        self._metriseis(id_zwnis)
        enarksi = self._xronos(xronos_enarksis)
        liksi = enarksi + timedelta(minutes=diarkeia_lepta)
        self._elegxe_epikalypsi(ProgrammaArdefsis, id_zwnis, enarksi, liksi)
        dexameni = self._dexameni(id_dexamenis)
        diathesimo = self._elegxe_nero(dexameni, posotita_nerou_l)
        dedomena = {
            "id_thermokipiou": id_thermokipiou,
            "id_zwnis": id_zwnis,
            "id_dexamenis": dexameni.id_dexamenis,
            "posotita_nerou_l": posotita_nerou_l,
            "diarkeia_lepta": diarkeia_lepta,
            "xronos_enarksis": enarksi.isoformat(),
            "xronos_liksis": liksi.isoformat(),
            "stathmi_prin_l": dexameni.trexwn_ogkos_l,
            "stathmi_meta_l": dexameni.trexwn_ogkos_l - posotita_nerou_l,
            "diathesimo_l": diathesimo,
            "ygrasia_prin": zwni.ygrasia_ypostrwmatos,
            "ygrasia_meta_ektimwmeni": min(1, zwni.ygrasia_ypostrwmatos + posotita_nerou_l / 1000),
            "eparkis_stathmi": True,
            "isxys_antlias_kw": 0.2,
            "apaiteitai_epivevaiwsi": True,
        }
        if xristis is None:
            _sphalma("Απαιτείται ταυτοποιημένος χρήστης.", KodikosSfalmatos.ANARMODIOS_XRISTIS, 401)
        apantisi = dimiourgise_proepiskopisi(
            self.synedria,
            "programmatismos_ardefsis",
            id_thermokipiou,
            xristis,
            dedomena,
            self._stigmiotypo(),
        )
        self.synedria.commit()
        return apantisi

    def dimiourgia_programmatos_ardefsis(
        self, id_proepiskopisis, xristis, id_aitimatos_monadikotitas=None, id_thermokipiou=None
    ):
        if xristis:
            elegxe_dikaiwma(xristis, RolosXristi.YPEFTHYNOS_PORWN, id_ontotitas=id_thermokipiou)
        kleidwse_synallagi(self.synedria)
        # Το parent ID προέρχεται υποχρεωτικά από τη διαδρομή στο δημόσιο API.
        if id_thermokipiou is None:
            _sphalma("Απαιτείται αναγνωριστικό θερμοκηπίου.")
        aitima = {"id_proepiskopisis": id_proepiskopisis}
        apantisi = pare_epanalipsi(
            self.synedria,
            xristis,
            "programmatismos_ardefsis",
            id_thermokipiou,
            id_aitimatos_monadikotitas,
            aitima,
        )
        if apantisi:
            return apantisi
        proep = pare_proepiskopisi(
            self.synedria,
            id_proepiskopisis,
            "programmatismos_ardefsis",
            id_thermokipiou,
            xristis,
            self._stigmiotypo(),
        )
        self._metriseis(proep["id_zwnis"])
        self._zwni(id_thermokipiou, proep["id_zwnis"])
        if not self._th(id_thermokipiou).diathesimi_ardefsi:
            _sphalma(
                "Ο εξοπλισμός άρδευσης δεν είναι διαθέσιμος.",
                KodikosSfalmatos.MH_ASPHALIS_KATASTASI,
                409,
            )
        enarksi = self._xronos(datetime.fromisoformat(proep["xronos_enarksis"]))
        self._elegxe_epikalypsi(
            ProgrammaArdefsis,
            proep["id_zwnis"],
            enarksi,
            datetime.fromisoformat(proep["xronos_liksis"]),
        )
        dexameni = self._dexameni(proep["id_dexamenis"])
        self._elegxe_nero(dexameni, proep["posotita_nerou_l"])
        katanalwse_proepiskopisi(self.synedria, id_proepiskopisis)
        id_programmatos = "prog_ard_" + uuid.uuid4().hex
        apantisi = {
            "id_programmatos": id_programmatos,
            "katastasi": "programmatismeno",
            "nea_stathmi_dexamenis_l": dexameni.trexwn_ogkos_l,
            "desmevmeno_nero_l": proep["posotita_nerou_l"],
            "minyma": "Το πρόγραμμα δεσμεύτηκε. Η φυσική κατανάλωση θα γίνει στον προγραμματισμένο χρόνο.",
        }
        entoli = kataxwrise_entoli(
            self.synedria,
            xristis,
            "poroi",
            "programmatismos_ardefsis",
            id_thermokipiou,
            aitima,
            apantisi,
            katastasi="programmatismeno",
            id_proepiskopisis=id_proepiskopisis,
            kleidi=id_aitimatos_monadikotitas,
        )
        self.synedria.add(
            ProgrammaArdefsis(
                id_programmatos=id_programmatos,
                id_thermokipiou=id_thermokipiou,
                id_zwnis=proep["id_zwnis"],
                id_dexamenis=dexameni.id_dexamenis,
                posotita_nerou_l=proep["posotita_nerou_l"],
                xronos_enarksis=enarksi,
                diarkeia_lepta=proep["diarkeia_lepta"],
                id_proepiskopisis=id_proepiskopisis,
                id_entolis=entoli.id_entolis,
                katastasi="programmatismeno",
                ektelestheisa_posotita_l=0,
            )
        )
        self.synedria.commit()
        return apantisi

    def akyrosi_programmatos_ardefsis(self, id_programmatos, xristis):
        return self.akyrosi_programmatos(ProgrammaArdefsis, id_programmatos, xristis)

    def akyrosi_programmatos(self, typos, id_programmatos, xristis, id_thermokipiou=None):
        from backend.app.prosomoiwsi.prosomoiosis_porwn import _allakse_entoli

        kleidwse_synallagi(self.synedria)
        programma = self.synedria.get(typos, id_programmatos)
        if not programma or (
            id_thermokipiou is not None and programma.id_thermokipiou != id_thermokipiou
        ):
            _sphalma(
                "Το πρόγραμμα δεν βρέθηκε στο ζητούμενο πεδίο.", KodikosSfalmatos.DEN_VRETHIKE, 404
            )
        elegxe_dikaiwma(
            xristis,
            RolosXristi.YPEFTHYNOS_PORWN,
            id_ontotitas=getattr(programma, "id_thermokipiou", None) or programma.id_dexamenis,
        )
        if (
            programma.katastasi != "programmatismeno"
            or se_utc(programma.xronos_enarksis) < self._twra()
        ):
            _sphalma(
                "Το πρόγραμμα έχει ήδη αρχίσει ή είναι οριστικό· δεν επιτρέπεται ακύρωση.",
                KodikosSfalmatos.MH_EPITREPTI_METAVASI,
                409,
            )
        _allakse_entoli(
            self.synedria,
            programma,
            "akyrothike",
            self._twra(),
            "Ακύρωση πριν από τη φυσική εκτέλεση· αποδέσμευση πόρων.",
        )
        self.apothiki_koinwn.kataxwrise_istoriko_elegxou(
            xristis.id_xristi,
            xristis.vasikos_rolos.value,
            "akyrosi_programmatos",
            "programma_porwn",
            id_programmatos,
            aitiologia="Ακύρωση από εξουσιοδοτημένο χειριστή πριν την εκτέλεση.",
        )
        enimerwse_fortia_programmatwn(self.synedria, self._twra())
        self.synedria.commit()
        return {
            "id_programmatos": id_programmatos,
            "katastasi": "akyrothike",
            "epistrafen_nero_l": 0.0,
            "minyma": "Το πρόγραμμα ακυρώθηκε και η δέσμευση αποδεσμεύτηκε χωρίς φυσική κατανάλωση.",
        }

    def proepiskopisi_fwtismou(
        self, id_thermokipiou, id_zwnis, isxys_kw, diarkeia_wres, xristis, xronos_enarksis=None
    ):
        if xristis:
            elegxe_dikaiwma(xristis, RolosXristi.YPEFTHYNOS_PORWN, id_ontotitas=id_thermokipiou)
        self._thetikos(isxys_kw, "isxys_kw")
        self._thetikos(diarkeia_wres, "diarkeia_wres")
        self._zwni(id_thermokipiou, id_zwnis)
        if not self._th(id_thermokipiou).diathesimos_fwtismos:
            _sphalma(
                "Ο τεχνητός φωτισμός δεν είναι διαθέσιμος.",
                KodikosSfalmatos.MH_ASPHALIS_KATASTASI,
                409,
            )
        self._metriseis(id_zwnis)
        enarksi = self._xronos(xronos_enarksis)
        liksi = enarksi + timedelta(hours=diarkeia_wres)
        self._elegxe_epikalypsi(ProgrammaFwtismou, id_zwnis, enarksi, liksi)
        energeia = isxys_kw * diarkeia_wres
        if energeia > sum(
            stoixeio_sigma.energeia_kwh for stoixeio_sigma in self.apothiki_porwn.pare_syssoreftes()
        ):
            _sphalma(
                "Η ενέργεια φωτισμού υπερβαίνει τη σημερινή αξιοποιήσιμη αποθήκευση.",
                KodikosSfalmatos.ANEPARKIS_ENERGEIA,
                409,
            )
        dedomena = {
            "id_thermokipiou": id_thermokipiou,
            "id_zwnis": id_zwnis,
            "isxys_kw": isxys_kw,
            "diarkeia_wres": diarkeia_wres,
            "xronos_enarksis": enarksi.isoformat(),
            "xronos_liksis": liksi.isoformat(),
            "synoliki_energeia_kwh": energeia,
            "apaiteitai_epivevaiwsi": True,
            "proeidopoiiseis": [
                "Ο φωτισμός είναι αναβλητό φορτίο και αναστέλλεται με κοινή απόφαση περιορισμού."
            ],
        }
        apantisi = dimiourgise_proepiskopisi(
            self.synedria,
            "programmatismos_fwtismou",
            id_thermokipiou,
            xristis,
            dedomena,
            self._stigmiotypo(),
        )
        self.synedria.commit()
        return apantisi

    def dimiourgia_programmatos_fwtismou(
        self, id_thermokipiou, id_proepiskopisis, xristis, kleidi=None
    ):
        if xristis:
            elegxe_dikaiwma(xristis, RolosXristi.YPEFTHYNOS_PORWN, id_ontotitas=id_thermokipiou)
        kleidwse_synallagi(self.synedria)
        aitima = {"id_proepiskopisis": id_proepiskopisis}
        apantisi = pare_epanalipsi(
            self.synedria, xristis, "programmatismos_fwtismou", id_thermokipiou, kleidi, aitima
        )
        if apantisi:
            return apantisi
        proep = pare_proepiskopisi(
            self.synedria,
            id_proepiskopisis,
            "programmatismos_fwtismou",
            id_thermokipiou,
            xristis,
            self._stigmiotypo(),
        )
        self._metriseis(proep["id_zwnis"])
        self._zwni(id_thermokipiou, proep["id_zwnis"])
        if not self._th(id_thermokipiou).diathesimos_fwtismos:
            _sphalma(
                "Ο φωτισμός δεν είναι διαθέσιμος.", KodikosSfalmatos.MH_ASPHALIS_KATASTASI, 409
            )
        enarksi = self._xronos(datetime.fromisoformat(proep["xronos_enarksis"]))
        liksi = datetime.fromisoformat(proep["xronos_liksis"])
        self._elegxe_epikalypsi(ProgrammaFwtismou, proep["id_zwnis"], enarksi, liksi)
        katanalwse_proepiskopisi(self.synedria, id_proepiskopisis)
        id_prog = "prog_fwt_" + uuid.uuid4().hex
        apantisi = {
            "id_programmatos": id_prog,
            "katastasi": "programmatismeno",
            "isxys_kw": proep["isxys_kw"],
            "xronos_liksis": proep["xronos_liksis"],
            "minyma": "Ο φωτισμός προγραμματίστηκε στο προσομοιωμένο χρονικό παράθυρο.",
        }
        entoli = kataxwrise_entoli(
            self.synedria,
            xristis,
            "poroi",
            "programmatismos_fwtismou",
            id_thermokipiou,
            aitima,
            apantisi,
            katastasi="programmatismeno",
            id_proepiskopisis=id_proepiskopisis,
            kleidi=kleidi,
        )
        self.synedria.add(
            ProgrammaFwtismou(
                id_programmatos=id_prog,
                id_thermokipiou=id_thermokipiou,
                id_zwnis=proep["id_zwnis"],
                isxys_kw=proep["isxys_kw"],
                xronos_enarksis=enarksi,
                xronos_liksis=liksi,
                katastasi="programmatismeno",
                id_entolis=entoli.id_entolis,
                ektelestheisa_energeia_kwh=0,
            )
        )
        self.synedria.commit()
        return apantisi

    def proepiskopisi_anakyklwsis(
        self,
        posotita_nerou_l,
        apodosi,
        xristis,
        xronos_enarksis=None,
        diarkeia_lepta=60,
        id_dexamenis_pigis=None,
        id_dexamenis=None,
        isxys_kw=0.5,
    ):
        if xristis:
            elegxe_dikaiwma(
                xristis, RolosXristi.YPEFTHYNOS_PORWN, id_ontotitas=id_dexamenis or "dexameni_01"
            )
        self._thetikos(posotita_nerou_l, "posotita_nerou_l")
        self._thetikos(diarkeia_lepta, "diarkeia_lepta")
        self._thetikos(isxys_kw, "isxys_kw")
        if not math.isfinite(apodosi) or not 0 < apodosi <= 1:
            _sphalma("Η απόδοση πρέπει να ανήκει στο (0,1].")
        self._metriseis()
        pigi = self._dexameni(id_dexamenis_pigis, "gkrizo")
        proorismos = self._dexameni(id_dexamenis)
        if not proorismos.diathesimi_anakyklwsi:
            _sphalma(
                "Η μονάδα ανακύκλωσης δεν είναι διαθέσιμη.",
                KodikosSfalmatos.MH_ASPHALIS_KATASTASI,
                409,
            )
        self._elegxe_nero(pigi, posotita_nerou_l)
        epistrofi = posotita_nerou_l * apodosi
        if proorismos.trexwn_ogkos_l + epistrofi > proorismos.xwritikotita_l:
            _sphalma(
                "Ανεπαρκής χωρητικότητα δεξαμενής καθαρού νερού.",
                KodikosSfalmatos.SYNTHIKI_SYGGROUSIS,
                409,
            )
        enarksi = self._xronos(xronos_enarksis)
        liksi = enarksi + timedelta(minutes=diarkeia_lepta)
        self._elegxe_xwritikotita_anakyklwsis(proorismos, epistrofi)
        self._elegxe_kiklo_anakyklwsis(proorismos.id_dexamenis, enarksi, liksi)
        dedomena = {
            "id_dexamenis_pigis": pigi.id_dexamenis,
            "id_dexamenis": proorismos.id_dexamenis,
            "posotita_akarthartou_l": posotita_nerou_l,
            "apodosi_anakyklwsis": apodosi,
            "epistrefomeno_nero_l": epistrofi,
            "apwleia_l": posotita_nerou_l - epistrofi,
            "diarkeia_lepta": diarkeia_lepta,
            "xronos_enarksis": enarksi.isoformat(),
            "xronos_liksis": liksi.isoformat(),
            "isxys_kw": isxys_kw,
            "energeia_kwh": isxys_kw * diarkeia_lepta / 60,
            "apaiteitai_epivevaiwsi": True,
        }
        apantisi = dimiourgise_proepiskopisi(
            self.synedria,
            "programmatismos_anakyklwsis",
            proorismos.id_dexamenis,
            xristis,
            dedomena,
            self._stigmiotypo(),
        )
        self.synedria.commit()
        return apantisi

    def dimiourgia_programmatos_anakyklwsis(
        self, id_proepiskopisis, xristis, kleidi=None, id_dexamenis="dexameni_01"
    ):
        if xristis:
            elegxe_dikaiwma(xristis, RolosXristi.YPEFTHYNOS_PORWN, id_ontotitas=id_dexamenis)
        kleidwse_synallagi(self.synedria)
        aitima = {"id_proepiskopisis": id_proepiskopisis}
        apantisi = pare_epanalipsi(
            self.synedria, xristis, "programmatismos_anakyklwsis", id_dexamenis, kleidi, aitima
        )
        if apantisi:
            return apantisi
        proep = pare_proepiskopisi(
            self.synedria,
            id_proepiskopisis,
            "programmatismos_anakyklwsis",
            id_dexamenis,
            xristis,
            self._stigmiotypo(),
        )
        self._metriseis()
        pigi = self._dexameni(proep["id_dexamenis_pigis"], "gkrizo")
        self._elegxe_nero(pigi, proep["posotita_akarthartou_l"])
        proorismos = self._dexameni(id_dexamenis)
        if not proorismos.diathesimi_anakyklwsi:
            _sphalma(
                "Η ανακύκλωση δεν είναι διαθέσιμη.", KodikosSfalmatos.MH_ASPHALIS_KATASTASI, 409
            )
        enarksi = self._xronos(datetime.fromisoformat(proep["xronos_enarksis"]))
        self._elegxe_xwritikotita_anakyklwsis(proorismos, proep["epistrefomeno_nero_l"])
        self._elegxe_kiklo_anakyklwsis(
            proorismos.id_dexamenis, enarksi, datetime.fromisoformat(proep["xronos_liksis"])
        )
        katanalwse_proepiskopisi(self.synedria, id_proepiskopisis)
        id_prog = "prog_anak_" + uuid.uuid4().hex
        apantisi = {
            "id_programmatos": id_prog,
            "katastasi": "programmatismeno",
            "posotita_anakyklwsis_l": proep["epistrefomeno_nero_l"],
            "minyma": "Δεσμεύτηκε γκρίζο νερό για κύκλο ανακύκλωσης χωρίς δημιουργία νέας μάζας.",
        }
        entoli = kataxwrise_entoli(
            self.synedria,
            xristis,
            "poroi",
            "programmatismos_anakyklwsis",
            id_dexamenis,
            aitima,
            apantisi,
            katastasi="programmatismeno",
            id_proepiskopisis=id_proepiskopisis,
            kleidi=kleidi,
        )
        self.synedria.add(
            ProgrammaAnakyklwsis(
                id_programmatos=id_prog,
                id_dexamenis=id_dexamenis,
                id_dexamenis_pigis=pigi.id_dexamenis,
                posotita_eisodou_l=proep["posotita_akarthartou_l"],
                posotita_anakyklwsis_l=proep["epistrefomeno_nero_l"],
                apwleia_l=proep["apwleia_l"],
                isxys_kw=proep["isxys_kw"],
                xronos_enarksis=enarksi,
                diarkeia_lepta=proep["diarkeia_lepta"],
                apodosi_anakyklwsis=proep["apodosi_anakyklwsis"],
                katastasi="programmatismeno",
                id_entolis=entoli.id_entolis,
                ektelestheisa_posotita_l=0,
            )
        )
        self.synedria.commit()
        return apantisi

    def pare_katastasi_energeias(self):
        pvs = self.apothiki_porwn.pare_fwtovoltaika()
        syssoreftes = self.apothiki_porwn.pare_syssoreftes()
        fortia = self.apothiki_porwn.pare_energeiaka_fortia()
        paragwgi_w = sum(
            ypologise_isxy_fwtovoltaikou(
                pv.apodosi_eta, pv.epifaneia_m2, pv.aktinovolia_w_m2, pv.syntelestis_epikathisis_f
            )
            for pv in pvs
        )
        krisima = sum(
            stoixeio_zita.isxys_kw
            for stoixeio_zita in fortia
            if stoixeio_zita.energo and stoixeio_zita.einai_krisimo
        )
        anavlita = sum(
            stoixeio_zita.isxys_kw
            for stoixeio_zita in fortia
            if stoixeio_zita.energo and stoixeio_zita.einai_anavlito
        )
        energeia = sum(stoixeio_sigma.energeia_kwh for stoixeio_sigma in syssoreftes)
        _, elleimma, _, autonomia, katastasi = ypologise_ilektriko_isozygio_kai_autonomia(
            paragwgi_w / 1000, krisima, anavlita, 0, energeia, efedreia_idi_afairemeni=True
        )
        return {
            "paragwgi": {
                "synoliki_isxys_w": round(paragwgi_w, 4),
                "synoliki_isxys_kw": round(paragwgi_w / 1000, 6),
                "fwtovoltaika": [
                    {
                        "id_fwtovoltaikou": stoixeio_pi.id_fwtovoltaikou,
                        "onoma": stoixeio_pi.onoma,
                        "epifaneia_m2": stoixeio_pi.epifaneia_m2,
                        "apodosi_eta": stoixeio_pi.apodosi_eta,
                        "syntelestis_skonis": stoixeio_pi.syntelestis_epikathisis_f,
                        "aktinovolia_w_m2": stoixeio_pi.aktinovolia_w_m2,
                        "isxys_w": ypologise_isxy_fwtovoltaikou(
                            stoixeio_pi.apodosi_eta,
                            stoixeio_pi.epifaneia_m2,
                            stoixeio_pi.aktinovolia_w_m2,
                            stoixeio_pi.syntelestis_epikathisis_f,
                        ),
                    }
                    for stoixeio_pi in pvs
                ],
            },
            "fortia": {
                "krisima_kw": krisima,
                "anavlita_kw": anavlita,
                "synolika_fortia_kw": krisima + anavlita,
            },
            "sysswrefsi": {
                "energeia_kwh": energeia,
                "syssoreftes": [
                    {
                        "id_syssorefti": stoixeio_sigma.id_syssorefti,
                        "onoma": stoixeio_sigma.onoma,
                        "xwritikotita_kwh": stoixeio_sigma.xwritikotita_kwh,
                        "energeia_kwh": stoixeio_sigma.energeia_kwh,
                        "efedreia_kwh": stoixeio_sigma.efedreia_kwh,
                        "pososto_fortisis": (
                            stoixeio_sigma.energeia_kwh + stoixeio_sigma.efedreia_kwh
                        )
                        / stoixeio_sigma.xwritikotita_kwh,
                        "katastasi": stoixeio_sigma.katastasi,
                    }
                    for stoixeio_sigma in syssoreftes
                ],
            },
            "isozygio": {
                "elleimma_kw": round(elleimma, 6),
                "autonomia_wres": round(autonomia, 6) if autonomia is not None else None,
                "katastasi": katastasi,
            },
        }

    def pare_analytika_fortia(self):
        return [
            {
                "id_fortiou": stoixeio_zita.id_fortiou,
                "onoma": stoixeio_zita.onoma,
                "egkatastasi": stoixeio_zita.egkatastasi,
                "isxys_kw": stoixeio_zita.isxys_kw,
                "einai_krisimo": stoixeio_zita.einai_krisimo,
                "einai_anavlito": stoixeio_zita.einai_anavlito,
                "energo": stoixeio_zita.energo,
                "proteraiotita": stoixeio_zita.proteraiotita,
            }
            for stoixeio_zita in self.apothiki_porwn.pare_energeiaka_fortia()
        ]

    def proepiskopisi_periorismou_fortiwn(
        self, pausi_anavlhtwn=True, xristis=None, aitiologia="Σύγκριση επιλογών"
    ):
        katastasi = self.pare_katastasi_energeias()
        fortia = self.apothiki_porwn.pare_energeiaka_fortia()
        krisima = katastasi["fortia"]["krisima_kw"]
        anavlita_meta = (
            0.0
            if pausi_anavlhtwn
            else sum(
                stoixeio_zita.isxys_kw
                for stoixeio_zita in fortia
                if stoixeio_zita.einai_anavlito
                and anavlito_fortio_diathesimo(self.synedria, stoixeio_zita)
            )
        )
        _, elleimma, _, autonomia, _ = ypologise_ilektriko_isozygio_kai_autonomia(
            katastasi["paragwgi"]["synoliki_isxys_kw"],
            krisima,
            anavlita_meta,
            0,
            katastasi["sysswrefsi"]["energeia_kwh"],
            efedreia_idi_afairemeni=True,
        )
        prin = katastasi["isozygio"]["autonomia_wres"]
        dedomena = {
            "pausi_anavlhtwn": pausi_anavlhtwn,
            "aitiologia": aitiologia,
            "katastasi_prin": {
                "fortia_kw": katastasi["fortia"]["synolika_fortia_kw"],
                "elleimma_kw": katastasi["isozygio"]["elleimma_kw"],
                "autonomia_wres": prin,
            },
            "katastasi_meta": {
                "fortia_kw": krisima + anavlita_meta,
                "elleimma_kw": elleimma,
                "autonomia_wres": round(autonomia, 6) if autonomia is not None else None,
            },
            "ofelos": {
                "meiwsi_isxyos_kw": katastasi["fortia"]["anavlita_kw"] - anavlita_meta,
                "kerdos_autonomias_wres": autonomia - prin
                if autonomia is not None and prin is not None
                else None,
                "kerdos_autonomias_lepta": (autonomia - prin) * 60
                if autonomia is not None and prin is not None
                else None,
            },
            "apaiteitai_egkrisi_syntonisti": True,
            "epiptwseis": [
                "Αναστολή φωτισμού, ανακύκλωσης και φόρτισης rover όσο ισχύει η κοινή πολιτική· τα κρίσιμα φορτία παραμένουν."
            ],
        }
        if xristis is None:
            return dedomena
        apantisi = dimiourgise_proepiskopisi(
            self.synedria, "periorismos_fortiwn", "apoikia", xristis, dedomena, self._stigmiotypo()
        )
        self.synedria.commit()
        return apantisi

    def ektelesi_periorismou_fortiwn(
        self,
        pausi_anavlhtwn=None,
        xristis=None,
        aitiologia="Απόφαση συντονιστή",
        id_proepiskopisis=None,
        kleidi=None,
        desmefsi_synallagis=True,
    ):
        if not xristis or RolosXristi.SYNTONISTIS_APOIKIAS not in xristis.energoi_roloi:
            _sphalma("Απαιτείται έγκριση συντονιστή.", KodikosSfalmatos.ANARMODIOS_XRISTIS, 403)
        if desmefsi_synallagis:
            kleidwse_synallagi(self.synedria)
            aitima = {"id_proepiskopisis": id_proepiskopisis}
            apantisi = pare_epanalipsi(
                self.synedria, xristis, "periorismos_fortiwn", "apoikia", kleidi, aitima
            )
            if apantisi:
                return apantisi
            proep = pare_proepiskopisi(
                self.synedria,
                id_proepiskopisis,
                "periorismos_fortiwn",
                "apoikia",
                xristis,
                self._stigmiotypo(),
            )
            pausi_anavlhtwn = proep["pausi_anavlhtwn"]
            aitiologia = proep["aitiologia"]
            katanalwse_proepiskopisi(self.synedria, id_proepiskopisis)
        if pausi_anavlhtwn is None:
            _sphalma("Δεν ορίστηκε απόφαση περιορισμού.")
        plithos = efarmose_pausi_anavlitwn(self.synedria, pausi_anavlhtwn)
        apantisi = {
            "pausi_anavlhtwn": pausi_anavlhtwn,
            "arithmos_fortiwn_pou_allaksan": plithos,
            "aitiologia": aitiologia,
            "minyma": "Η κοινή πολιτική φορτίων εφαρμόστηκε και τα ενεργά προγράμματα επανεκτιμήθηκαν.",
        }
        if desmefsi_synallagis:
            kataxwrise_entoli(
                self.synedria,
                xristis,
                "poroi",
                "periorismos_fortiwn",
                "apoikia",
                aitima,
                apantisi,
                id_proepiskopisis=id_proepiskopisis,
                kleidi=kleidi,
            )
            self.synedria.commit()
        return apantisi
