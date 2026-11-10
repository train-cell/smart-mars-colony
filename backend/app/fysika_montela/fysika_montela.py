"""Καθαρές μαθηματικές συναρτήσεις φυσικών μοντέλων (PHY-01 έως PHY-07).

Όλες οι συναρτήσεις είναι pure functions χωρίς εξαρτήσεις από βάση δεδομένων ή δίκτυο,
με ελέγχους ορίων, αριθμητικές δοκιμές και μονάδες SI.
"""

import math
from functools import wraps
from typing import Any, Dict, Optional, Tuple


def elegxos_peperasmenwn(synartisi):
    """Απαγορεύει μη πεπερασμένες αριθμητικές εισόδους πριν από κάθε μοντέλο."""

    @wraps(synartisi)
    def elegxe(*orismata, **onomatismena):
        for timi in (*orismata, *onomatismena.values()):
            if isinstance(timi, (float, int)) and not math.isfinite(timi):
                raise ValueError("Οι αριθμητικές τιμές πρέπει να είναι πεπερασμένες.")
        return synartisi(*orismata, **onomatismena)

    return elegxe


# Φυσικές σταθερές
STATHERA_AERIWN_J_MOL_K = 8.314462618  # Παγκόσμια σταθερά ιδανικών αερίων [J / (mol · K)]
MORIAKI_MAZA_O2_KG_MOL = 0.0319988  # Μοριακή μάζα διατομικού οξυγόνου O2 [kg / mol]
VARYTITA_ARI_M_S2 = 3.72076  # Εκπαιδευτική παράμετρος προσέγγισης βαρύτητας Άρη [m / s²]


# ============================================================================
# PHY-01: Θερμικές Απώλειες Κατοίκησης και Απαίτηση Θέρμανσης
# ============================================================================


@elegxos_peperasmenwn
def ypologise_thermikes_apwleies(
    syntelestis_thermoperatotitas_w_m2k: float,
    epifaneia_m2: float,
    thermokrasia_eswteriki_k: float,
    thermokrasia_exwteriki_k: float,
) -> float:
    """Υπολογίζει το ρυθμό θερμικών απωλειών [W] μέσω του κελύφους του χώρου.

    Εξίσωση: Q = U * A * (T_esw - T_exw)
    """
    if syntelestis_thermoperatotitas_w_m2k < 0.0:
        raise ValueError("Ο συντελεστής θερμοπερατότητας (U) δεν μπορεί να είναι αρνητικός.")
    if epifaneia_m2 <= 0.0:
        raise ValueError("Η επιφάνεια (A) πρέπει να είναι θετικός αριθμός.")
    if thermokrasia_eswteriki_k < 0.0 or thermokrasia_exwteriki_k < 0.0:
        raise ValueError("Η θερμοκρασία σε Kelvin δεν μπορεί να είναι αρνητική.")

    diafora_thermokrasias = thermokrasia_eswteriki_k - thermokrasia_exwteriki_k
    return syntelestis_thermoperatotitas_w_m2k * epifaneia_m2 * diafora_thermokrasias


@elegxos_peperasmenwn
def ypologise_apaitisi_thermansis(
    syntelestis_thermoperatotitas_w_m2k: float,
    epifaneia_m2: float,
    thermokrasia_eswteriki_k: float,
    thermokrasia_exwteriki_k: float,
    eswterika_kerdi_w: float = 0.0,
    syntelestis_apodosis_cop: float = 1.0,
) -> float:
    """Υπολογίζει την απαιτούμενη ηλεκτρική ισχύ θέρμανσης [W] (COP=1 στην καταιγίδα)."""
    if eswterika_kerdi_w < 0.0:
        raise ValueError("Τα εσωτερικά κέρδη δεν μπορούν να είναι αρνητικά.")
    if syntelestis_apodosis_cop <= 0.0:
        raise ValueError("Ο συντελεστής COP πρέπει να είναι αυστηρά θετικός.")

    apwleies_w = ypologise_thermikes_apwleies(
        syntelestis_thermoperatotitas_w_m2k,
        epifaneia_m2,
        thermokrasia_eswteriki_k,
        thermokrasia_exwteriki_k,
    )
    kathari_apaitisi_thermotitas_w = max(0.0, apwleies_w - eswterika_kerdi_w)
    return kathari_apaitisi_thermotitas_w / syntelestis_apodosis_cop


# ============================================================================
# PHY-02: Παραγωγή Φωτοβολταϊκών
# ============================================================================


@elegxos_peperasmenwn
def ypologise_isxy_fwtovoltaikou(
    apodosi_fwtovoltaikou: float,
    epifaneia_m2: float,
    aktinovolia_w_m2: float,
    syntelestis_epikathisis: float,
) -> float:
    """Υπολογίζει την παραγόμενη ηλεκτρική ισχύ [W] από φωτοβολταϊκή συστοιχία.

    Εξίσωση: P = η * A * G * f
    Σημείωση: Η μετρούμενη ακτινοβολία G περιλαμβάνει ήδη την εξασθένηση της ατμόσφαιρας.
    Ο συντελεστής f αναπαριστά την τοπική επικάθιση σκόνης στα πάνελ.
    """
    if not (0.0 <= apodosi_fwtovoltaikou <= 1.0):
        raise ValueError("Η απόδοση (η) πρέπει να βρίσκεται στο διάστημα [0, 1].")
    if epifaneia_m2 < 0.0:
        raise ValueError("Η επιφάνεια δεν μπορεί να είναι αρνητική.")
    if aktinovolia_w_m2 < 0.0:
        raise ValueError("Η ηλιακή ακτινοβολία (G) δεν μπορεί να είναι αρνητική.")
    if not (0.0 <= syntelestis_epikathisis <= 1.0):
        raise ValueError("Ο συντελεστής επικάθισης (f) πρέπει να βρίσκεται στο διάστημα [0, 1].")

    if aktinovolia_w_m2 == 0.0 or epifaneia_m2 == 0.0:
        return 0.0

    return apodosi_fwtovoltaikou * epifaneia_m2 * aktinovolia_w_m2 * syntelestis_epikathisis


# ============================================================================
# PHY-03: Οξυγόνο — Διαθέσιμη Ποσότητα, Κατώφλι και Αυτονομία
# ============================================================================


@elegxos_peperasmenwn
def ypologise_meriki_piesi_oxygonou(
    pososto_oxygonou: float,
    synoliki_piesi_pa: float,
) -> float:
    """Υπολογίζει τη μερική πίεση του οξυγόνου [Pa] από το κλάσμα όγκου."""
    if not (0.0 <= pososto_oxygonou <= 1.0):
        raise ValueError("Το ποσοστό οξυγόνου πρέπει να βρίσκεται στο διάστημα [0, 1].")
    if synoliki_piesi_pa < 0.0:
        raise ValueError("Η συνολική πίεση δεν μπορεί να είναι αρνητική.")
    return pososto_oxygonou * synoliki_piesi_pa


@elegxos_peperasmenwn
def ypologise_apothema_kai_autonomia_oxygonou(
    ogkos_m3: float,
    thermokrasia_k: float,
    meriki_piesi_oxygonou_pa: float,
    katwfli_asfaleias_piesis_pa: float,
    arithmos_katoikwn: int,
    katanalwsi_ana_atomo_kg_h: float,
    rythmos_paragwgis_kg_h: float = 0.0,
) -> Tuple[float, float, Optional[float], str]:
    """Υπολογίζει το αξιοποιήσιμο απόθεμα οξυγόνου και την αυτονομία κατοίκων.

    Επιστρέφει:
    - mol_xrisimou_oxygonou [mol]
    - maza_xrisimou_oxygonou_kg [kg]
    - autonomia_wres [ώρες] (ή None αν η αναπλήρωση υπερκαλύπτει την κατανάλωση)
    - katastasi [str]: περιγραφή κατάστασης ασφαλείας
    """
    if ogkos_m3 <= 0.0:
        raise ValueError("Ο όγκος πρέπει να είναι θετικός.")
    if thermokrasia_k <= 0.0:
        raise ValueError("Η θερμοκρασία σε Kelvin πρέπει να είναι αυστηρά θετική.")
    if meriki_piesi_oxygonou_pa < 0.0 or katwfli_asfaleias_piesis_pa < 0.0:
        raise ValueError("Οι πιέσεις δεν μπορούν να είναι αρνητικές.")
    if arithmos_katoikwn < 0:
        raise ValueError("Ο αριθμός κατοίκων δεν μπορεί να είναι αρνητικός.")
    if katanalwsi_ana_atomo_kg_h < 0.0 or rythmos_paragwgis_kg_h < 0.0:
        raise ValueError("Οι ρυθμοί κατανάλωσης/παραγωγής δεν μπορούν να είναι αρνητικοί.")

    # Χρήσιμη μερική πίεση πάνω από το εκπαιδευτικό κατώφλι ασφαλείας
    diafora_piesis_pa = max(0.0, meriki_piesi_oxygonou_pa - katwfli_asfaleias_piesis_pa)
    mol_xrisimou = (diafora_piesis_pa * ogkos_m3) / (STATHERA_AERIWN_J_MOL_K * thermokrasia_k)
    maza_xrisimou_kg = mol_xrisimou * MORIAKI_MAZA_O2_KG_MOL

    synoliki_katanalwsi_kg_h = arithmos_katoikwn * katanalwsi_ana_atomo_kg_h
    katharos_rythmos_meiwsis_kg_h = synoliki_katanalwsi_kg_h - rythmos_paragwgis_kg_h

    if meriki_piesi_oxygonou_pa <= katwfli_asfaleias_piesis_pa:
        return 0.0, 0.0, 0.0, "katwfli_paraviasmeno"

    if katharos_rythmos_meiwsis_kg_h <= 0.0:
        return mol_xrisimou, maza_xrisimou_kg, None, "stathero_i_anaplirownomeno"

    autonomia_wres = maza_xrisimou_kg / katharos_rythmos_meiwsis_kg_h
    return mol_xrisimou, maza_xrisimou_kg, autonomia_wres, "kanoniki_leitourgia"


# ============================================================================
# PHY-04: Ηλεκτρικό Ισοζύγιο και Αυτονομία Συσσωρευτή
# ============================================================================


@elegxos_peperasmenwn
def ypologise_ilektriko_isozygio_kai_autonomia(
    paragwgi_kw: float,
    krisima_fortia_kw: float,
    anavlita_fortia_kw: float,
    apwleies_kw: float,
    energeia_syssorefti_kwh: float,
    efedreia_syssorefti_kwh: float = 0.0,
    efedreia_idi_afairemeni: bool = False,
) -> Tuple[float, float, float, Optional[float], str]:
    """Υπολογίζει συνολικά φορτία, έλλειμμα, διαθέσιμη ενέργεια και αυτονομία [h].

    Επιστρέφει:
    - synolika_fortia_kw
    - elleimma_kw
    - diathesimi_energeia_kwh
    - autonomia_wres (ή None αν παραγωγή >= φορτία)
    - katastasi
    """
    if (
        paragwgi_kw < 0.0
        or krisima_fortia_kw < 0.0
        or anavlita_fortia_kw < 0.0
        or apwleies_kw < 0.0
    ):
        raise ValueError("Οι τιμές ισχύος δεν μπορούν να είναι αρνητικές.")
    if energeia_syssorefti_kwh < 0.0 or efedreia_syssorefti_kwh < 0.0:
        raise ValueError("Η ενέργεια συσσωρευτή δεν μπορεί να είναι αρνητική.")

    synolika_fortia_kw = krisima_fortia_kw + anavlita_fortia_kw + apwleies_kw
    elleimma_kw = max(0.0, synolika_fortia_kw - paragwgi_kw)

    if efedreia_idi_afairemeni:
        diathesimi_energeia_kwh = max(0.0, energeia_syssorefti_kwh)
    else:
        diathesimi_energeia_kwh = max(0.0, energeia_syssorefti_kwh - efedreia_syssorefti_kwh)

    if elleimma_kw == 0.0:
        return synolika_fortia_kw, 0.0, diathesimi_energeia_kwh, None, "pleonasma_i_isozigio"

    if diathesimi_energeia_kwh == 0.0:
        return synolika_fortia_kw, elleimma_kw, 0.0, 0.0, "ekkenwsi_efedreias"

    autonomia_wres = diathesimi_energeia_kwh / elleimma_kw
    return (
        synolika_fortia_kw,
        elleimma_kw,
        diathesimi_energeia_kwh,
        autonomia_wres,
        "ekkenwsi_se_exelixi",
    )


# ============================================================================
# PHY-05: Ισοζύγιο Νερού, Ανακύκλωση και Άρδευση
# ============================================================================


@elegxos_peperasmenwn
def ypologise_isozygio_nerou(
    trexwn_ogkos_l: float,
    xwritikotita_l: float,
    ekswteriki_eisroi_l: float,
    epistrofi_anakyklwsis_l: float,
    ardefsi_l: float,
    loipes_analwseis_l: float,
    diarros_l: float,
    efedreia_asfaleias_l: float = 0.0,
) -> Tuple[float, float, str]:
    """Υπολογίζει την επόμενη στάθμη δεξαμενής και υπερχείλιση/έλλειμμα νερού [L].

    Επιστρέφει:
    - epomenos_ogkos_l: τελική ποσότητα νερού στη δεξαμενή
    - yperxeilisi_l: ποσότητα που υπερχείλισε (0 αν δεν υπερχείλισε)
    - katastasi: κατάσταση ισοζυγίου
    """
    if trexwn_ogkos_l < 0.0 or xwritikotita_l <= 0.0:
        raise ValueError("Μη έγκυρος όγκος ή χωρητικότητα δεξαμενής.")
    if ekswteriki_eisroi_l < 0.0 or epistrofi_anakyklwsis_l < 0.0:
        raise ValueError("Οι εισροές νερού δεν μπορούν να είναι αρνητικές.")
    if ardefsi_l < 0.0 or loipes_analwseis_l < 0.0 or diarros_l < 0.0:
        raise ValueError("Οι αναλώσεις και διαρροές δεν μπορούν να είναι αρνητικές.")

    if (
        efedreia_asfaleias_l < 0
        or efedreia_asfaleias_l > xwritikotita_l
        or trexwn_ogkos_l > xwritikotita_l
    ):
        raise ValueError("Το απόθεμα και η εφεδρεία πρέπει να ανήκουν στη χωρητικότητα.")

    synoliki_zitisi_l = ardefsi_l + loipes_analwseis_l + diarros_l
    diathesimo_prin_zitisi_l = trexwn_ogkos_l + ekswteriki_eisroi_l + epistrofi_anakyklwsis_l

    if synoliki_zitisi_l > diathesimo_prin_zitisi_l:
        raise ValueError(
            f"Ανεπαρκές νερό: Ζητήθηκαν {synoliki_zitisi_l:.2f} L, αλλά διατίθενται μόλις {diathesimo_prin_zitisi_l:.2f} L."
        )

    kathari_posotita_l = diathesimo_prin_zitisi_l - synoliki_zitisi_l

    yperxeilisi_l = max(0.0, kathari_posotita_l - xwritikotita_l)
    epomenos_ogkos_l = min(kathari_posotita_l, xwritikotita_l)

    if epomenos_ogkos_l < efedreia_asfaleias_l:
        katastasi = "katw_apo_efedreia"
    elif yperxeilisi_l > 0.0:
        katastasi = "yperxeilisi"
    else:
        katastasi = "kanoniko_isozygio"

    return epomenos_ogkos_l, yperxeilisi_l, katastasi


# ============================================================================
# PHY-06: Rover — Ενέργεια Κίνησης και Επιστροφής
# ============================================================================


@elegxos_peperasmenwn
def ypologise_energeia_kinisis_oximatos(
    maza_kg: float,
    apostasi_m: float,
    klisi_rad: float = 0.0,
    syntelestis_kylisis: float = 0.05,
    apodosi_kinisis: float = 0.8,
    voithitiki_isxys_w: float = 100.0,
    taxytita_m_s: float = 1.11111,  # ~4 km/h
) -> Tuple[float, float, float]:
    """Υπολογίζει την ενέργεια κίνησης και βοηθητικών συστημάτων οχήματος [J] και [kWh].

    Εξίσωση: W_kinisi = [m * g_Mars * (max(0, sin(θ)) + Cr * cos(θ)) * d] / η
    Επιστρέφει: (energeia_kinisis_j, voithitiki_energeia_j, synoliki_energeia_kwh)
    """
    if maza_kg <= 0.0 or apostasi_m < 0.0:
        raise ValueError("Η μάζα πρέπει να είναι θετική και η απόσταση μη αρνητική.")
    if not (0.0 < apodosi_kinisis <= 1.0):
        raise ValueError("Η απόδοση κινητήρα πρέπει να βρίσκεται στο διάστημα (0, 1].")
    if syntelestis_kylisis < 0.0 or voithitiki_isxys_w < 0.0 or taxytita_m_s <= 0.0:
        raise ValueError("Μη έγκυρες παράμετροι τριβής, ισχύος ή ταχύτητας.")

    if not (-math.pi / 2 < klisi_rad < math.pi / 2):
        raise ValueError("Η κλίση πρέπει να βρίσκεται αυστηρά μεταξύ -π/2 και π/2 rad.")

    # Ανωφέρεια (η κατηφόρα sin(θ)<0 δεν θεωρείται ότι παράγει αυτόματη ανάκτηση)
    oros_anwforeias = max(0.0, math.sin(klisi_rad))
    oros_kylisis = syntelestis_kylisis * math.cos(klisi_rad)

    dynami_antistasis_n = maza_kg * VARYTITA_ARI_M_S2 * (oros_anwforeias + oros_kylisis)
    energeia_kinisis_j = (dynami_antistasis_n * apostasi_m) / apodosi_kinisis

    xronos_kinisis_s = apostasi_m / taxytita_m_s
    voithitiki_energeia_j = voithitiki_isxys_w * xronos_kinisis_s

    synoliki_energeia_j = energeia_kinisis_j + voithitiki_energeia_j
    synoliki_energeia_kwh = synoliki_energeia_j / 3_600_000.0

    return energeia_kinisis_j, voithitiki_energeia_j, synoliki_energeia_kwh


# ============================================================================
# PHY-07: Πρόβλεψη Διάρκειας Επιστροφής και Πολυδιάστατη Αξιολόγηση Ασφαλείας
# ============================================================================


@elegxos_peperasmenwn
def ypologise_xrono_epistrofis_kai_asfaleia(
    apostasi_km: float,
    taxytita_kmh: float,
    mesi_isxys_kw: float,
    diathesimi_energeia_kwh: float,
    efedreia_asfaleias_kwh: float,
    oratotita_m: float,
    katastasi_tilemetrias: str = "egkyri",
    katwfli_asfalous_oratotitas_m: float = 300.0,
) -> Dict[str, Any]:
    """Υπολογίζει χρόνο και ενέργεια επιστροφής rover και διαχωρίζει τις διαστάσεις ασφαλείας.

    Επαληθεύει το Golden Fixture (§6):
    - Απόσταση: 2 km
    - Ταχύτητα: 4 km/h -> Χρόνος: 0.5 h (30 min)
    - Μέση ισχύς: 0.6 kW -> Ενέργεια: 0.3 kWh
    - Ενέργεια rover: 0.8 kWh, Εφεδρεία: 0.2 kWh
    - Διαθέσιμη ενέργεια πάνω από εφεδρεία: 0.6 kWh >= 0.3 kWh (Ενεργειακά εφικτή)
    - Ενέργεια μετά την επιστροφή: 0.8 - 0.3 = 0.5 kWh (> 0.2 kWh)
    """
    if apostasi_km < 0.0:
        raise ValueError("Η απόσταση δεν μπορεί να είναι αρνητική.")
    if taxytita_kmh <= 0.0:
        raise ValueError("Η ταχύτητα πρέπει να είναι αυστηρά θετική.")
    if mesi_isxys_kw < 0.0 or diathesimi_energeia_kwh < 0.0 or efedreia_asfaleias_kwh < 0.0:
        raise ValueError("Οι ενεργειακές παράμετροι πρέπει να είναι μη αρνητικές.")

    if oratotita_m < 0 or katwfli_asfalous_oratotitas_m < 0:
        raise ValueError("Η ορατότητα πρέπει να είναι μη αρνητική.")

    xronos_epistrofis_wres = apostasi_km / taxytita_kmh
    apaitoumeni_energeia_kwh = mesi_isxys_kw * xronos_epistrofis_wres

    energeia_meta_epistrofi_kwh = diathesimi_energeia_kwh - apaitoumeni_energeia_kwh
    energeiaka_efikto = energeia_meta_epistrofi_kwh >= efedreia_asfaleias_kwh

    # Αξιολόγηση ορατότητας
    oratotita_asfalis = oratotita_m >= katwfli_asfalous_oratotitas_m

    # Αξιολόγηση επικοινωνίας
    epikoinwnia_asfalis = katastasi_tilemetrias in ["egkyri", "statheri"]

    # Συνολική απόφαση (η ενεργειακή επάρκεια ΔΕΝ αρκεί μόνη της αν υπάρχει κίνδυνος ορατότητας ή επικοινωνίας)
    synolika_asfalis_epistrofi = energeiaka_efikto and oratotita_asfalis and epikoinwnia_asfalis

    proeidopoiiseis = []
    if not energeiaka_efikto:
        proeidopoiiseis.append("Ανεπαρκής ενέργεια για επιστροφή με διατήρηση εφεδρείας.")
    if not oratotita_asfalis:
        proeidopoiiseis.append(
            f"Πολύ χαμηλή ορατότητα ({oratotita_m} m < {katwfli_asfalous_oratotitas_m} m). Κίνδυνος πρόσκρουσης."
        )
    if not epikoinwnia_asfalis:
        proeidopoiiseis.append(
            "Υποβαθμισμένη επικοινωνία τηλεμετρίας κατά τη διάρκεια της καταιγίδας."
        )

    return {
        "apostasi_km": apostasi_km,
        "taxytita_kmh": taxytita_kmh,
        "xronos_epistrofis_wres": round(xronos_epistrofis_wres, 5),
        "xronos_epistrofis_lepta": round(xronos_epistrofis_wres * 60.0, 2),
        "apaitoumeni_energeia_kwh": round(apaitoumeni_energeia_kwh, 4),
        "energeia_meta_epistrofi_kwh": round(energeia_meta_epistrofi_kwh, 4),
        "energeiaka_efikto": energeiaka_efikto,
        "oratotita_asfalis": oratotita_asfalis,
        "epikoinwnia_asfalis": epikoinwnia_asfalis,
        "synolika_asfalis_epistrofi": synolika_asfalis_epistrofi,
        "proeidopoiiseis": proeidopoiiseis,
    }
