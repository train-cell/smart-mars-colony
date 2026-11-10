"""Κοινή, αναγνώσιμη κατανομή ισχύος για φυσική εκτέλεση και προβλέψεις."""

import math
from collections import defaultdict
from datetime import timedelta

from sqlalchemy import select

from backend.app.montela import (
    EnergeiakoFortio,
    KatastasiProsomoiwsis,
    OximaExerevnis,
    ProgrammaAnakyklwsis,
    ProgrammaArdefsis,
    ProgrammaFwtismou,
)
from backend.app.ypiresies.metriseis_kai_poiotita import se_utc


def pare_fortia_trofodosias(synedria, xronos=None, diarkeia_wres=None):
    """Παράγει τη ζήτηση χωρίς εγγραφή, ακόμη πριν το πρώτο βήμα νέου προγράμματος."""
    roloi = synedria.get(KatastasiProsomoiwsis, 1)
    xronos = se_utc(xronos or roloi.xronos_prosomoiwsis)
    fortia = {
        fortio.id_fortiou: {
            "id_fortiou": fortio.id_fortiou,
            "onoma": fortio.onoma,
            "egkatastasi": fortio.egkatastasi,
            "isxys_kw": fortio.isxys_kw,
            "energo": fortio.energo,
            "einai_krisimo": fortio.einai_krisimo,
            "einai_anavlito": fortio.einai_anavlito,
            "proteraiotita": fortio.proteraiotita,
            "apaitei_pliri_trofodosia": False,
        }
        for fortio in synedria.scalars(select(EnergeiakoFortio))
    }
    for onoma, fortio in fortia.items():
        if onoma.startswith(("fortio_programmatos_", "fortio_fortisis_")):
            fortio["energo"] = False
    for typos in (ProgrammaArdefsis, ProgrammaAnakyklwsis, ProgrammaFwtismou):
        for programma in synedria.scalars(select(typos)):
            if programma.katastasi not in {"programmatismeno", "se_exelixi", "anastoli"}:
                continue
            enarksi = se_utc(programma.xronos_enarksis)
            liksi = (
                se_utc(programma.xronos_liksis)
                if isinstance(programma, ProgrammaFwtismou)
                else enarksi + timedelta(minutes=programma.diarkeia_lepta)
            )
            anavlito = not isinstance(programma, ProgrammaArdefsis)
            if not enarksi <= xronos < liksi or (anavlito and roloi.pausi_anavlitwn):
                continue
            onoma = "fortio_programmatos_" + programma.id_programmatos
            fortia[onoma] = {
                "id_fortiou": onoma,
                "onoma": "Πρόγραμμα " + programma.id_programmatos,
                "egkatastasi": "anakyklwsi_nerou"
                if isinstance(programma, ProgrammaAnakyklwsis)
                else "thermokipio",
                "isxys_kw": programma.isxys_kw if anavlito else 0.2,
                "energo": True,
                "einai_krisimo": not anavlito,
                "einai_anavlito": anavlito,
                "proteraiotita": 2 if anavlito else 1,
                "apaitei_pliri_trofodosia": True,
            }
    for oxima in synedria.scalars(select(OximaExerevnis)):
        onoma = "fortio_fortisis_" + oxima.id_oximatos
        isxys = oxima.isxys_fortisis_kw
        if diarkeia_wres:
            isxys = min(
                isxys,
                max(0, oxima.xwritikotita_energeias_kwh - oxima.energeia_kwh)
                / (diarkeia_wres * 0.9),
            )
        fortia[onoma] = {
            "id_fortiou": onoma,
            "onoma": "Φόρτιση οχήματος",
            "egkatastasi": "vasi_oximatwn",
            "isxys_kw": isxys,
            "einai_krisimo": False,
            "einai_anavlito": True,
            "proteraiotita": 4,
            "apaitei_pliri_trofodosia": False,
            "energo": not roloi.pausi_anavlitwn
            and oxima.apostasi_apo_vasi_km <= 1e-6
            and oxima.katastasi_oximatos in {"stasi", "sti_vasi", "asfalis_stasi"}
            and oxima.energeia_kwh < oxima.xwritikotita_energeias_kwh - 1e-9,
        }
    return sorted(fortia.values(), key=lambda fortio: fortio["id_fortiou"])


def ypologise_katanomi_fortiwn(fortia, diathesimi_isxys_kw):
    """Κρίσιμα πρώτα, έπειτα μικρότερη προτεραιότητα· ίδια συνεχή φορτία αναλογικά.

    Τα αδιαίρετα προγράμματα παίρνουν ολόκληρη την ισχύ ή μηδέν. Εντός της ίδιας
    προτεραιότητας προηγούνται τα συνεχή φορτία, έπειτα τα προγράμματα κατά ID.
    Δεν αλλάζει την εγκεκριμένη πολιτική ή τα δεδομένα των φορτίων.
    """
    if not math.isfinite(diathesimi_isxys_kw) or diathesimi_isxys_kw < 0:
        raise ValueError("Η διαθέσιμη ισχύς πρέπει να είναι μη αρνητική και πεπερασμένη.")
    omades = defaultdict(list)
    ana_fortio = {}
    for fortio in fortia:
        zitisi = fortio["isxys_kw"] if fortio["energo"] else 0
        if not math.isfinite(zitisi) or zitisi < 0:
            raise ValueError("Η ισχύς φορτίου πρέπει να είναι μη αρνητική και πεπερασμένη.")
        ana_fortio[fortio["id_fortiou"]] = {
            "zitoumeni_kw": zitisi,
            "paradidomeni_kw": 0.0,
            "pososto": 0.0,
        }
        if zitisi:
            omades[(not fortio["einai_krisimo"], fortio["proteraiotita"])].append(fortio)
    ypoloipo = diathesimi_isxys_kw
    for kleidi in sorted(omades):
        omada = omades[kleidi]
        synexi = [fortio for fortio in omada if not fortio.get("apaitei_pliri_trofodosia", False)]
        synolo = sum(fortio["isxys_kw"] for fortio in synexi)
        logos = min(1, ypoloipo / synolo) if synolo else 0
        for fortio in synexi:
            ana_fortio[fortio["id_fortiou"]]["paradidomeni_kw"] = fortio["isxys_kw"] * logos
        ypoloipo = max(0, ypoloipo - synolo * logos)
        for fortio in sorted(omada, key=lambda stoixeio: stoixeio["id_fortiou"]):
            if (
                fortio.get("apaitei_pliri_trofodosia", False)
                and fortio["isxys_kw"] <= ypoloipo + 1e-9
            ):
                ana_fortio[fortio["id_fortiou"]]["paradidomeni_kw"] = fortio["isxys_kw"]
                ypoloipo = max(0, ypoloipo - fortio["isxys_kw"])
    for stoixeio in ana_fortio.values():
        stoixeio["pososto"] = (
            stoixeio["paradidomeni_kw"] / stoixeio["zitoumeni_kw"]
            if stoixeio["zitoumeni_kw"]
            else 0
        )
    zitisi = sum(stoixeio["zitoumeni_kw"] for stoixeio in ana_fortio.values())
    paradidomeni = sum(stoixeio["paradidomeni_kw"] for stoixeio in ana_fortio.values())
    return {
        "ana_fortio": ana_fortio,
        "zitoumeni_kw": zitisi,
        "paradidomeni_kw": paradidomeni,
        "mi_kalyptomeni_kw": max(0, zitisi - paradidomeni),
    }


def pososta_ypostiriksis_zwis(katanomi):
    """Τα δύο δηλωμένα ηλεκτρικά κυκλώματα της εκπαιδευτικής εγκατάστασης."""
    fortia = katanomi["ana_fortio"]
    return {
        "thermansi": fortia.get("fortio_thermansis", {}).get("pososto", 0.0),
        "loipes_syskeves": fortia.get("fortio_krisimo_loipo", {}).get("pososto", 0.0),
    }


def ypologise_autonomia_dyo_fasewn(
    maza_kg, katanalwsi_kg_h, paragwgi_tora_kg_h, paragwgi_meta_kg_h, diarkeia_trofodosias_wres
):
    """Σταθερά φορτία/ήλιος, πεπερασμένη μπαταρία και συντηρητική μη πίστωση περίσσειας O₂."""
    for timi in (maza_kg, katanalwsi_kg_h, paragwgi_tora_kg_h, paragwgi_meta_kg_h):
        if not math.isfinite(timi) or timi < 0:
            raise ValueError(
                "Οι μάζες και οι ρυθμοί πρέπει να είναι μη αρνητικοί και πεπερασμένοι."
            )
    if diarkeia_trofodosias_wres is not None and (
        not math.isfinite(diarkeia_trofodosias_wres) or diarkeia_trofodosias_wres < 0
    ):
        raise ValueError("Η διάρκεια τροφοδοσίας πρέπει να είναι μη αρνητική και πεπερασμένη.")
    if maza_kg <= 0:
        return 0.0
    rythmos_tora = max(0, katanalwsi_kg_h - paragwgi_tora_kg_h)
    if diarkeia_trofodosias_wres is None:
        return maza_kg / rythmos_tora if rythmos_tora else None
    if rythmos_tora and maza_kg / rythmos_tora <= diarkeia_trofodosias_wres:
        return maza_kg / rythmos_tora
    maza_meta = max(0, maza_kg - rythmos_tora * diarkeia_trofodosias_wres)
    rythmos_meta = max(0, katanalwsi_kg_h - paragwgi_meta_kg_h)
    return diarkeia_trofodosias_wres + maza_meta / rythmos_meta if rythmos_meta else None
