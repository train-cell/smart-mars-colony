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


def test_arithmitiko_paradeigma_thermikes_apwleies_kanonikes_kai_kataigida():
    """Έλεγχος θερμικών απωλειών baseline (8 kW) και καταιγίδας (10 kW)."""
    u = 0.2  # W / (m² · K)
    stoixeio_alfa = 500.0  # m²
    t_esw = 293.0  # K

    # Κανονικές συνθήκες: T_exw = 213 K -> deltaT = 80 K -> 8000 W = 8 kW
    thermansi_arxiki = ypologise_thermikes_apwleies(u, stoixeio_alfa, t_esw, 213.0)
    assert thermansi_arxiki == pytest.approx(8000.0, rel=1e-5)

    # Συνθήκες καταιγίδας: T_exw = 193 K -> deltaT = 100 K -> 10000 W = 10 kW
    thermansi_kataigidas = ypologise_thermikes_apwleies(u, stoixeio_alfa, t_esw, 193.0)
    assert thermansi_kataigidas == pytest.approx(10000.0, rel=1e-5)

    # Αύξηση 2 kW
    assert (thermansi_kataigidas - thermansi_arxiki) == pytest.approx(2000.0, rel=1e-5)


def test_arithmitiko_paradeigma_fwtovoltaika_kanonika_kai_kataigida():
    """Έλεγχος παραγωγής PV baseline (4.8 kW) και καταιγίδας (0.8 kW)."""
    eta = 0.20
    stoixeio_alfa = 100.0

    # Κανονικές συνθήκες: G = 300 W/m², f = 0.8 -> 4800 W = 4.8 kW
    isxys_arxiki = ypologise_isxy_fwtovoltaikou(eta, stoixeio_alfa, 300.0, 0.8)
    assert isxys_arxiki == pytest.approx(4800.0, rel=1e-5)

    # Καταιγίδα: G = 80 W/m², f = 0.5 -> 800 W = 0.8 kW
    isxys_kataigidas = ypologise_isxy_fwtovoltaikou(eta, stoixeio_alfa, 80.0, 0.5)
    assert isxys_kataigidas == pytest.approx(800.0, rel=1e-5)

    # Πτώση 4.0 kW
    assert (isxys_arxiki - isxys_kataigidas) == pytest.approx(4000.0, rel=1e-5)


# ============================================================================
# TEST-02: Ηλεκτρικά Ελλείμματα και Αυτονομίες Συσσωρευτή
# ============================================================================


def test_arithmitiko_paradeigma_ilektriko_isozygio_kai_autonomia_pliris_alysida():
    """Έλεγχος ελλειμμάτων 9.2, 15.2, 11.2 kW και αυτονομιών 3.26, 1.97, 2.68 h."""
    # 1. Baseline: παραγωγή 4.8 kW, θέρμανση 8 kW, άλλα κρίσιμα 2 kW, αναβλητά 4 kW
    # Σύνολο φορτίων = 14 kW, Έλλειμμα = 9.2 kW, Μπαταρία = 30 kWh
    fortia_arxika, elleimma_arxiko, energeia_arxiki, autonomia_arxiki, _ = (
        ypologise_ilektriko_isozygio_kai_autonomia(
            paragwgi_kw=4.8,
            krisima_fortia_kw=8.0 + 2.0,
            anavlita_fortia_kw=4.0,
            apwleies_kw=0.0,
            energeia_syssorefti_kwh=30.0,
            efedreia_idi_afairemeni=True,
        )
    )
    assert fortia_arxika == pytest.approx(14.0)
    assert elleimma_arxiko == pytest.approx(9.2)
    assert autonomia_arxiki == pytest.approx(30.0 / 9.2, rel=1e-4)  # ~3.26087 h

    # 2. Καταιγίδα με αναβλητά: παραγωγή 0.8 kW, θέρμανση 10 kW, κρίσιμα 2 kW, αναβλητά 4 kW
    # Σύνολο φορτίων = 16 kW, Έλλειμμα = 15.2 kW
    fortia_kataigidas, elleimma_kataigidas, _, autonomia_kataigidas, _ = (
        ypologise_ilektriko_isozygio_kai_autonomia(
            paragwgi_kw=0.8,
            krisima_fortia_kw=10.0 + 2.0,
            anavlita_fortia_kw=4.0,
            apwleies_kw=0.0,
            energeia_syssorefti_kwh=30.0,
            efedreia_idi_afairemeni=True,
        )
    )
    assert fortia_kataigidas == pytest.approx(16.0)
    assert elleimma_kataigidas == pytest.approx(15.2)
    assert autonomia_kataigidas == pytest.approx(30.0 / 15.2, rel=1e-4)  # ~1.97368 h

    # 3. Καταιγίδα με παύση αναβλητών φορτίων (curtailment): αναβλητά = 0 kW
    # Σύνολο φορτίων = 12 kW, Έλλειμμα = 11.2 kW
    fortia_meta_pausi, elleimma_meta_pausi, _, autonomia_meta_pausi, _ = (
        ypologise_ilektriko_isozygio_kai_autonomia(
            paragwgi_kw=0.8,
            krisima_fortia_kw=10.0 + 2.0,
            anavlita_fortia_kw=0.0,
            apwleies_kw=0.0,
            energeia_syssorefti_kwh=30.0,
            efedreia_idi_afairemeni=True,
        )
    )
    assert fortia_meta_pausi == pytest.approx(12.0)
    assert elleimma_meta_pausi == pytest.approx(11.2)
    assert autonomia_meta_pausi == pytest.approx(30.0 / 11.2, rel=1e-4)  # ~2.67857 h

    # Βελτίωση αυτονομίας: ~0.70489 h (~42.29 λεπτά)
    diafora_wres = autonomia_meta_pausi - autonomia_kataigidas
    assert diafora_wres == pytest.approx(0.70489, rel=1e-3)
    diafora_lepta = diafora_wres * 60.0
    assert diafora_lepta == pytest.approx(42.29, rel=1e-2)


# ============================================================================
# TEST-03: Rover Επιστροφή και Αξιολόγηση Ασφαλείας
# ============================================================================


def test_arithmitiko_paradeigma_epistrofis_oximatos_kai_asfaleias():
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
    thermokrasia = 293.0
    synoliki_piesi = 100_000.0
    meriki_piesi = ypologise_meriki_piesi_oxygonou(0.21, synoliki_piesi)
    assert meriki_piesi == 21_000.0  # 21 kPa

    katwfli = 16_000.0  # 16 kPa ελάχιστη ασφαλής μερική πίεση O2
    katoikoi = 4
    katanalwsi_atomo = 0.04  # 40 g/h ανά άτομο

    posotita_mol, maza_kg, autonomia_wres, katastasi = ypologise_apothema_kai_autonomia_oxygonou(
        ogkos_m3=ogkos,
        thermokrasia_k=thermokrasia,
        meriki_piesi_oxygonou_pa=meriki_piesi,
        katwfli_asfaleias_piesis_pa=katwfli,
        arithmos_katoikwn=katoikoi,
        katanalwsi_ana_atomo_kg_h=katanalwsi_atomo,
        rythmos_paragwgis_kg_h=0.0,
    )

    # deltaP = 5000 Pa -> moles = (5000 * 1000) / (8.31446 * 293) ≈ 2052.4 mol
    assert posotita_mol > 2000.0
    assert maza_kg > 60.0  # ~65 kg αξιοποιήσιμο O2
    assert autonomia_wres is not None and autonomia_wres > 300.0
    assert katastasi == "kanoniki_leitourgia"

    # Περίπτωση όπου η παραγωγή υπερκαλύπτει την κατανάλωση
    _, _, autonomia_anaplirwsis, katastasi_anapl = ypologise_apothema_kai_autonomia_oxygonou(
        ogkos_m3=ogkos,
        thermokrasia_k=thermokrasia,
        meriki_piesi_oxygonou_pa=meriki_piesi,
        katwfli_asfaleias_piesis_pa=katwfli,
        arithmos_katoikwn=katoikoi,
        katanalwsi_ana_atomo_kg_h=katanalwsi_atomo,
        rythmos_paragwgis_kg_h=0.5,  # Μεγαλύτερη από κατανάλωση (0.16 kg/h)
    )
    assert autonomia_anaplirwsis is None
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


def test_arithmitika_orismata_oxygonou_thermansis_kai_kinisis():
    """Ακριβείς αριθμητικές αναφορές, μαζί με τις παραδοχές κάθε ξεχωριστού μοντέλου."""
    from backend.app.fysika_montela.fysika_montela import (
        ypologise_apaitisi_thermansis,
        ypologise_energeia_kinisis_oximatos,
    )

    posotita_mol, maza, autonomia, katastasi = ypologise_apothema_kai_autonomia_oxygonou(
        1000, 293, 21000, 16000, 4, 0.04
    )
    assert posotita_mol == pytest.approx(2052.42926698)
    assert maza == pytest.approx(65.6752736282)
    assert autonomia == pytest.approx(410.470460176)
    assert katastasi == "kanoniki_leitourgia"
    assert (
        ypologise_apaitisi_thermansis(
            0.2, 500, 293, 213, eswterika_kerdi_w=1000, syntelestis_apodosis_cop=2
        )
        == 3500
    )
    kinisi, voithitika, synoliko = ypologise_energeia_kinisis_oximatos(
        800, 2000, taxytita_m_s=4 / 3.6
    )
    assert kinisi == pytest.approx(372076)
    assert voithitika == 180000
    assert synoliko == pytest.approx(0.153354444444444)
