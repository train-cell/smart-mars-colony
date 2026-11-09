"""Δοκιμές μονάδας για τα φυσικά μοντέλα (TEST-01 έως TEST-07).

Επαληθεύει τις χρυσές τιμές (golden fixtures) της ενότητας §6
και τα όρια εγκυρότητας κάθε εξίσωσης.
"""

import pytest

from backend.app.fysika_montela.fysika_montela import (
    ypologise_apothema_kai_autonomia_oxygonou,
    ypologise_ilektriko_isozygio_kai_autonomia,
    ypologise_isozygio_nerou,
    ypologise_isxy_fwtovoltaikou,
    ypologise_meriki_piesi_oxygonou,
    ypologise_thermikes_apwleies,
    ypologise_xrono_epistrofis_kai_asfaleia,
)

# ============================================================================
# TEST-01: Golden fixtures Θερμότητας και Φωτοβολταϊκών
# ============================================================================


def test_golden_thermikes_apwleies_kanonikes_kai_kataigida():
    """Έλεγχος θερμικών απωλειών baseline (8 kW) και καταιγίδας (10 kW)."""
    u = 0.2  # W / (m² · K)
    a = 500.0  # m²
    t_esw = 293.0  # K

    # Κανονικές συνθήκες: T_exw = 213 K -> deltaT = 80 K -> 8000 W = 8 kW
    q_baseline = ypologise_thermikes_apwleies(u, a, t_esw, 213.0)
    assert q_baseline == pytest.approx(8000.0, rel=1e-5)

    # Συνθήκες καταιγίδας: T_exw = 193 K -> deltaT = 100 K -> 10000 W = 10 kW
    q_storm = ypologise_thermikes_apwleies(u, a, t_esw, 193.0)
    assert q_storm == pytest.approx(10000.0, rel=1e-5)

    # Αύξηση 2 kW
    assert (q_storm - q_baseline) == pytest.approx(2000.0, rel=1e-5)


def test_golden_fwtovoltaika_kanonika_kai_kataigida():
    """Έλεγχος παραγωγής PV baseline (4.8 kW) και καταιγίδας (0.8 kW)."""
    eta = 0.20
    a = 100.0

    # Κανονικές συνθήκες: G = 300 W/m², f = 0.8 -> 4800 W = 4.8 kW
    p_baseline = ypologise_isxy_fwtovoltaikou(eta, a, 300.0, 0.8)
    assert p_baseline == pytest.approx(4800.0, rel=1e-5)

    # Καταιγίδα: G = 80 W/m², f = 0.5 -> 800 W = 0.8 kW
    p_storm = ypologise_isxy_fwtovoltaikou(eta, a, 80.0, 0.5)
    assert p_storm == pytest.approx(800.0, rel=1e-5)

    # Πτώση 4.0 kW
    assert (p_baseline - p_storm) == pytest.approx(4000.0, rel=1e-5)


# ============================================================================
# TEST-02: Ηλεκτρικά Ελλείμματα και Αυτονομίες Συσσωρευτή
# ============================================================================


def test_golden_ilektriko_isozygio_kai_autonomia_pliris_alysida():
    """Έλεγχος ελλειμμάτων 9.2, 15.2, 11.2 kW και αυτονομιών 3.26, 1.97, 2.68 h."""
    # 1. Baseline: παραγωγή 4.8 kW, θέρμανση 8 kW, άλλα κρίσιμα 2 kW, αναβλητά 4 kW
    # Σύνολο φορτίων = 14 kW, Έλλειμμα = 9.2 kW, Μπαταρία = 30 kWh
    fortia_base, deficit_base, bat_base, auto_base, _ = ypologise_ilektriko_isozygio_kai_autonomia(
        paragwgi_kw=4.8,
        krisima_fortia_kw=8.0 + 2.0,
        anavlita_fortia_kw=4.0,
        apwleies_kw=0.0,
        energeia_syssorefti_kwh=30.0,
        efedreia_idi_afairemeni=True,
    )
    assert fortia_base == pytest.approx(14.0)
    assert deficit_base == pytest.approx(9.2)
    assert auto_base == pytest.approx(30.0 / 9.2, rel=1e-4)  # ~3.26087 h

    # 2. Καταιγίδα με αναβλητά: παραγωγή 0.8 kW, θέρμανση 10 kW, κρίσιμα 2 kW, αναβλητά 4 kW
    # Σύνολο φορτίων = 16 kW, Έλλειμμα = 15.2 kW
    fortia_storm, deficit_storm, _, auto_storm, _ = ypologise_ilektriko_isozygio_kai_autonomia(
        paragwgi_kw=0.8,
        krisima_fortia_kw=10.0 + 2.0,
        anavlita_fortia_kw=4.0,
        apwleies_kw=0.0,
        energeia_syssorefti_kwh=30.0,
        efedreia_idi_afairemeni=True,
    )
    assert fortia_storm == pytest.approx(16.0)
    assert deficit_storm == pytest.approx(15.2)
    assert auto_storm == pytest.approx(30.0 / 15.2, rel=1e-4)  # ~1.97368 h

    # 3. Καταιγίδα με παύση αναβλητών φορτίων (curtailment): αναβλητά = 0 kW
    # Σύνολο φορτίων = 12 kW, Έλλειμμα = 11.2 kW
    fortia_shed, deficit_shed, _, auto_shed, _ = ypologise_ilektriko_isozygio_kai_autonomia(
        paragwgi_kw=0.8,
        krisima_fortia_kw=10.0 + 2.0,
        anavlita_fortia_kw=0.0,
        apwleies_kw=0.0,
        energeia_syssorefti_kwh=30.0,
        efedreia_idi_afairemeni=True,
    )
    assert fortia_shed == pytest.approx(12.0)
    assert deficit_shed == pytest.approx(11.2)
    assert auto_shed == pytest.approx(30.0 / 11.2, rel=1e-4)  # ~2.67857 h

    # Βελτίωση αυτονομίας: ~0.70489 h (~42.29 λεπτά)
    diafora_wres = auto_shed - auto_storm
    assert diafora_wres == pytest.approx(0.70489, rel=1e-3)
    diafora_lepta = diafora_wres * 60.0
    assert diafora_lepta == pytest.approx(42.29, rel=1e-2)


# ============================================================================
# TEST-03: Rover Επιστροφή και Αξιολόγηση Ασφαλείας
# ============================================================================


def test_golden_rover_epistrofi_kai_asfaleia():
    """Έλεγχος 2 km / 4 km/h -> 0.5 h, ενέργεια 0.3 kWh και διαχωρισμός ασφαλείας."""
    apotelesma = ypologise_xrono_epistrofis_kai_asfaleia(
        apostasi_km=2.0,
        taxytita_kmh=4.0,
        mesi_isxys_kw=0.6,
        diathesimi_energeia_kwh=0.8,
        efedreia_asfaleias_kwh=0.2,
        oratotita_m=100.0,
        katastasi_tilemetrias="ypovathmismeni",
        katwfli_asfalous_oratotitas_m=300.0,
    )

    assert apotelesma["xronos_epistrofis_wres"] == 0.5
    assert apotelesma["xronos_epistrofis_lepta"] == 30.0
    assert apotelesma["apaitoumeni_energeia_kwh"] == 0.3
    assert apotelesma["energeia_meta_epistrofi_kwh"] == 0.5
    assert apotelesma["energeiaka_efikto"] is True
    # Η ορατότητα 100 m < 300 m καθιστά την επιστροφή ΜΗ ασφαλή παρά την ενεργειακή επάρκεια
    assert apotelesma["oratotita_asfalis"] is False
    assert apotelesma["synolika_asfalis_epistrofi"] is False
    assert len(apotelesma["proeidopoiiseis"]) >= 2


# ============================================================================
# TEST-04: Οξυγόνο — Νόμος Αερίων, Κατώφλια και Αυτονομία
# ============================================================================


def test_oxygono_ypologismoi_kai_autonomia():
    """Έλεγχος υπολογισμού μερικής πίεσης, μάζας οξυγόνου και αυτονομίας."""
    # Habitat 1000 m³, 293 K (~20°C), συνολική πίεση 100 kPa, 21% O2
    ogkos = 1000.0
    temp = 293.0
    p_total = 100_000.0
    p_o2 = ypologise_meriki_piesi_oxygonou(0.21, p_total)
    assert p_o2 == 21_000.0  # 21 kPa

    katwfli = 16_000.0  # 16 kPa ελάχιστη ασφαλής μερική πίεση O2
    katoikoi = 4
    katanalwsi_atomo = 0.04  # 40 g/h ανά άτομο

    moles, maza_kg, auto_h, katastasi = ypologise_apothema_kai_autonomia_oxygonou(
        ogkos_m3=ogkos,
        thermokrasia_k=temp,
        meriki_piesi_oxygonou_pa=p_o2,
        katwfli_asfaleias_piesis_pa=katwfli,
        arithmos_katoikwn=katoikoi,
        katanalwsi_ana_atomo_kg_h=katanalwsi_atomo,
        rythmos_paragwgis_kg_h=0.0,
    )

    # deltaP = 5000 Pa -> moles = (5000 * 1000) / (8.31446 * 293) ≈ 2052.4 mol
    assert moles > 2000.0
    assert maza_kg > 60.0  # ~65 kg αξιοποιήσιμο O2
    assert auto_h is not None and auto_h > 300.0
    assert katastasi == "kanoniki_leitourgia"

    # Περίπτωση όπου η παραγωγή υπερκαλύπτει την κατανάλωση
    _, _, auto_infinite, katastasi_anapl = ypologise_apothema_kai_autonomia_oxygonou(
        ogkos_m3=ogkos,
        thermokrasia_k=temp,
        meriki_piesi_oxygonou_pa=p_o2,
        katwfli_asfaleias_piesis_pa=katwfli,
        arithmos_katoikwn=katoikoi,
        katanalwsi_ana_atomo_kg_h=katanalwsi_atomo,
        rythmos_paragwgis_kg_h=0.5,  # Μεγαλύτερη από κατανάλωση (0.16 kg/h)
    )
    assert auto_infinite is None
    assert katastasi_anapl == "stathero_i_anaplirownomeno"


# ============================================================================
# TEST-05: Ισοζύγιο Νερού, Ανακύκλωση και Προστασία Ελλείμματος
# ============================================================================


def test_isozygio_nerou_apothiki_kai_aneparkeia():
    """Έλεγχος ισοζυγίου δεξαμενής και απόρριψης όταν δεν επαρκεί το νερό."""
    trexwn = 500.0
    xwritikotita = 1000.0

    # Κανονική εισροή + ανακύκλωση - άρδευση
    epomenos, yperx, katastasi = ypologise_isozygio_nerou(
        trexwn_ogkos_l=trexwn,
        xwritikotita_l=xwritikotita,
        ekswteriki_eisroi_l=20.0,
        epistrofi_anakyklwsis_l=30.0,
        ardefsi_l=50.0,
        loipes_analwseis_l=10.0,
        diarros_l=0.0,
    )
    # 500 + 20 + 30 - 50 - 10 = 490 L
    assert epomenos == 490.0
    assert yperx == 0.0
    assert katastasi == "kanoniko_isozygio"

    # Έλεγχος απόρριψης όταν ζητείται περισσότερο νερό από το διαθέσιμο
    with pytest.raises(ValueError, match="Ανεπαρκές νερό"):
        ypologise_isozygio_nerou(
            trexwn_ogkos_l=50.0,
            xwritikotita_l=xwritikotita,
            ekswteriki_eisroi_l=0.0,
            epistrofi_anakyklwsis_l=0.0,
            ardefsi_l=100.0,
            loipes_analwseis_l=0.0,
            diarros_l=0.0,
        )


# ============================================================================
# TEST-06 & TEST-07: Οριακές Συνθήκες και Έλεγχοι Ακυρότητας Εισόδων
# ============================================================================


def test_fwtovoltaika_mhdeniki_aktinovolia():
    """Έλεγχος ότι μηδενική ακτινοβολία (νύχτα) δίνει ακριβώς 0 W."""
    assert ypologise_isxy_fwtovoltaikou(0.20, 100.0, 0.0, 0.8) == 0.0


def test_akira_dedomena_eisodou_petoun_sfalmata():
    """Έλεγχος ότι αρνητικές τιμές ή άκυρες παράμετροι προκαλούν ValueError."""
    # Αρνητική θερμοκρασία Kelvin
    with pytest.raises(ValueError):
        ypologise_thermikes_apwleies(0.2, 500.0, -10.0, 200.0)

    # Αρνητική επιφάνεια
    with pytest.raises(ValueError):
        ypologise_isxy_fwtovoltaikou(0.2, -50.0, 300.0, 0.8)

    # Απόδοση εκτός [0, 1]
    with pytest.raises(ValueError):
        ypologise_isxy_fwtovoltaikou(1.5, 100.0, 300.0, 0.8)

    # Αρνητική ταχύτητα rover
    with pytest.raises(ValueError):
        ypologise_xrono_epistrofis_kai_asfaleia(2.0, -4.0, 0.6, 0.8, 0.2, 100.0)
