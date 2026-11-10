"""Απλοποιημένη θερμική και ατμοσφαιρική εξέλιξη με ισοζύγιο μάζας O₂."""

import math

from sqlalchemy import select

from backend.app.fysika_montela.fysika_montela import (
    MORIAKI_MAZA_O2_KG_MOL,
    STATHERA_AERIWN_J_MOL_K,
)
from backend.app.montela import ApothemaOxygonou, SyskeviYpostiriksisZwis, XwrosKatoikisis


def proxorise_zwi(synedria, apo, ews, pososto_trofodosias=1.0):
    """Λύνει αναλυτικά C*dT/dt=P-UA(T-Te), με σταθερές συνθήκες ανά βήμα."""
    diarkeia_s = (ews - apo).total_seconds()
    wres = diarkeia_s / 3600
    apotelesmata = []
    for xwros in synedria.scalars(select(XwrosKatoikisis)):
        syskeves = list(
            synedria.scalars(
                select(SyskeviYpostiriksisZwis).where(
                    SyskeviYpostiriksisZwis.id_xwrou == xwros.id_xwrou
                )
            )
        )
        thermantiras = next(
            (syskevi for syskevi in syskeves if syskevi.typos_syskevis == "thermantiras"), None
        )
        isxys_w = (
            thermantiras.katanalwsi_isxyos_w * pososto_trofodosias
            if thermantiras and thermantiras.katastasi_leitourgias == "energi"
            else 0
        )
        syntelestis = xwros.syntelestis_thermoperatotitas_u * xwros.epifaneia_m2
        palia_k = xwros.thermokrasia_eswteriki_k
        if syntelestis > 0:
            isorropia_k = xwros.thermokrasia_exwteriki_k + isxys_w / syntelestis
            xwros.thermokrasia_eswteriki_k = isorropia_k + (palia_k - isorropia_k) * math.exp(
                -syntelestis * diarkeia_s / xwros.thermiki_xwritikotita_j_k
            )
        else:
            xwros.thermokrasia_eswteriki_k += isxys_w * diarkeia_s / xwros.thermiki_xwritikotita_j_k
        xwros.piesi_pa = max(0, xwros.piesi_pa - xwros.rythmos_diarrois_piesis_pa_h * wres)
        apothema = synedria.scalar(
            select(ApothemaOxygonou).where(ApothemaOxygonou.id_xwrou == xwros.id_xwrou)
        )
        paragwgi_kg = 0.0
        if apothema and any(
            syskevi.typos_syskevis == "ilektrolysi" and syskevi.katastasi_leitourgias == "energi"
            for syskevi in syskeves
        ):
            paragwgi_kg = apothema.rythmos_paragwgis_kg_h * wres * pososto_trofodosias
        zitisi_kg = xwros.plithysmos * 0.04 * wres
        elleipon_kg = zitisi_kg
        yperxeilisi_kg = 0.0
        if apothema:
            diathesimo_kg = apothema.diathesimo_kg + paragwgi_kg
            apo_dexameni_kg = min(zitisi_kg, diathesimo_kg)
            elleipon_kg -= apo_dexameni_kg
            yperxeilisi_kg = max(0, diathesimo_kg - apo_dexameni_kg - apothema.xwritikotita_kg)
            apothema.diathesimo_kg = min(apothema.xwritikotita_kg, diathesimo_kg - apo_dexameni_kg)
        if elleipon_kg > 0:
            ptwsi_merikis_pa = (
                elleipon_kg
                / MORIAKI_MAZA_O2_KG_MOL
                * STATHERA_AERIWN_J_MOL_K
                * xwros.thermokrasia_eswteriki_k
                / xwros.ogkos_m3
            )
            meriki_pa = max(0, xwros.pososto_oxygonou * xwros.piesi_pa - ptwsi_merikis_pa)
            xwros.pososto_oxygonou = meriki_pa / xwros.piesi_pa if xwros.piesi_pa > 0 else 0
        katharistis = any(
            syskevi.typos_syskevis == "katharistis_dioxeidiou"
            and syskevi.katastasi_leitourgias == "energi"
            for syskevi in syskeves
        )
        afksisi_co2 = xwros.plithysmos * 25e-6 * wres
        xwros.pososto_dioxeidiou_anthraka = min(
            1,
            max(
                0.0004,
                xwros.pososto_dioxeidiou_anthraka
                + afksisi_co2 * (1 - pososto_trofodosias if katharistis else 1),
            ),
        )
        xwros.ekdosi_katastasis += 1
        apotelesmata.append(
            {
                "id_xwrou": xwros.id_xwrou,
                "thermokrasia_prin_k": palia_k,
                "thermokrasia_meta_k": xwros.thermokrasia_eswteriki_k,
                "katanalwsi_oxygonou_kg": zitisi_kg,
                "paragwgi_oxygonou_kg": paragwgi_kg,
                "yperxeilisi_oxygonou_kg": yperxeilisi_kg,
            }
        )
    synedria.flush()
    return apotelesmata
