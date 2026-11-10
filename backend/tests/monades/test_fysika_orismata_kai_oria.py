"""Εξαντλητικές δοκιμές ορίων και σφαλμάτων για μονάδες και φυσικά μοντέλα.

Καλύπτει όλες τις ακραίες περιπτώσεις, αρνητικές τιμές, μηδενικά μεγέθη
και ειδικές καταστάσεις προειδοποιήσεων (PHY-01 έως PHY-07).
"""

import pytest

from backend.app.fysika_montela.fysika_montela import (
    ypologise_apaitisi_thermansis,
    ypologise_apothema_kai_autonomia_oxygonou,
    ypologise_energeia_kinisis_oximatos,
    ypologise_ilektriko_isozygio_kai_autonomia,
    ypologise_isozygio_nerou,
    ypologise_isxy_fwtovoltaikou,
    ypologise_meriki_piesi_oxygonou,
    ypologise_thermikes_apwleies,
    ypologise_xrono_epistrofis_kai_asfaleia,
)
from backend.app.pyrinas.monades import (
    defterolepta_se_wres,
    isxys_kai_xronos_se_joule,
    joule_se_kilovatawres,
    kelvin_se_vathmous_kelsiou,
    kilovatawres_se_joule,
    kpascal_se_pascal,
    kyvika_metra_se_litra,
    litra_se_kyvika_metra,
    pascal_se_kpascal,
    vathmoi_kelsiou_se_kelvin,
    wres_se_defterolepta,
)

# ============================================================================
# 1. Έλεγχοι Ορίων Μονάδων Μέτρησης (monades.py)
# ============================================================================


def test_monades_arnitikes_times_petoun_sfalma():
    """Όλες οι συναρτήσεις μετατροπής πετούν ValueError σε αρνητική είσοδο."""
    with pytest.raises(ValueError, match="Kelvin"):
        kelvin_se_vathmous_kelsiou(-1.0)

    with pytest.raises(ValueError, match="απόλυτο μηδέν"):
        vathmoi_kelsiou_se_kelvin(-300.0)

    with pytest.raises(ValueError, match="ενέργεια"):
        joule_se_kilovatawres(-100.0)

    with pytest.raises(ValueError, match="ενέργεια"):
        kilovatawres_se_joule(-5.0)

    with pytest.raises(ValueError, match="όγκος"):
        kyvika_metra_se_litra(-2.0)

    with pytest.raises(ValueError, match="όγκος"):
        litra_se_kyvika_metra(-50.0)

    with pytest.raises(ValueError, match="πίεση"):
        pascal_se_kpascal(-1000.0)

    with pytest.raises(ValueError, match="πίεση"):
        kpascal_se_pascal(-10.0)

    with pytest.raises(ValueError, match="χρόνος"):
        wres_se_defterolepta(-1.5)

    with pytest.raises(ValueError, match="χρόνος"):
        defterolepta_se_wres(-3600.0)

    with pytest.raises(ValueError, match="ισχύς και ο χρόνος"):
        isxys_kai_xronos_se_joule(-10.0, 5.0)

    with pytest.raises(ValueError, match="ισχύς και ο χρόνος"):
        isxys_kai_xronos_se_joule(10.0, -5.0)


# ============================================================================
# 2. PHY-01: Θερμικές Απώλειες & Απαίτηση Θέρμανσης
# ============================================================================


def test_phy01_oria_kai_sfalmata():
    """Έλεγχοι ορίων και εξαιρέσεων για το θερμικό μοντέλο."""
    # Αρνητικός συντελεστής θερμοπερατότητας
    with pytest.raises(ValueError, match="συντελεστής θερμοπερατότητας"):
        ypologise_thermikes_apwleies(-0.1, 100.0, 293.0, 213.0)

    # Μηδενική ή αρνητική επιφάνεια
    with pytest.raises(ValueError, match="επιφάνεια"):
        ypologise_thermikes_apwleies(0.2, 0.0, 293.0, 213.0)

    with pytest.raises(ValueError, match="επιφάνεια"):
        ypologise_thermikes_apwleies(0.2, -50.0, 293.0, 213.0)

    # Αρνητικά εσωτερικά κέρδη
    with pytest.raises(ValueError, match="εσωτερικά κέρδη"):
        ypologise_apaitisi_thermansis(0.2, 100.0, 293.0, 213.0, eswterika_kerdi_w=-10.0)

    # Μηδενικός ή αρνητικός COP
    with pytest.raises(ValueError, match="COP"):
        ypologise_apaitisi_thermansis(0.2, 100.0, 293.0, 213.0, syntelestis_apodosis_cop=0.0)

    with pytest.raises(ValueError, match="COP"):
        ypologise_apaitisi_thermansis(0.2, 100.0, 293.0, 213.0, syntelestis_apodosis_cop=-1.5)

    # Κανονική εκτέλεση με εσωτερικά κέρδη και COP > 1
    apaitisi = ypologise_apaitisi_thermansis(
        syntelestis_thermoperatotitas_w_m2k=0.2,
        epifaneia_m2=100.0,
        thermokrasia_eswteriki_k=293.0,
        thermokrasia_exwteriki_k=213.0,
        eswterika_kerdi_w=500.0,
        syntelestis_apodosis_cop=2.0,
    )
    # Q = 0.2 * 100 * 80 = 1600 W. Καθαρή απαίτηση = 1600 - 500 = 1100 W. COP=2 -> 550 W
    assert apaitisi == pytest.approx(550.0)


# ============================================================================
# 3. PHY-02: Φωτοβολταϊκά
# ============================================================================


def test_phy02_oria_kai_sfalmata():
    """Έλεγχοι ορίων για φωτοβολταϊκά συστήματα."""
    # Αρνητική ακτινοβολία
    with pytest.raises(ValueError, match="ακτινοβολία"):
        ypologise_isxy_fwtovoltaikou(0.2, 100.0, -10.0, 0.8)

    # Μη έγκυρος συντελεστής επικάθισης f
    with pytest.raises(ValueError, match="συντελεστής επικάθισης"):
        ypologise_isxy_fwtovoltaikou(0.2, 100.0, 200.0, -0.1)

    with pytest.raises(ValueError, match="συντελεστής επικάθισης"):
        ypologise_isxy_fwtovoltaikou(0.2, 100.0, 200.0, 1.2)

    # Μηδενική επιφάνεια επιστρέφει άμεσα 0
    assert ypologise_isxy_fwtovoltaikou(0.2, 0.0, 300.0, 0.8) == 0.0


# ============================================================================
# 4. PHY-03: Οξυγόνο & Πίεση
# ============================================================================


def test_phy03_oria_kai_sfalmata():
    """Έλεγχοι ορίων για μερική πίεση και απόθεμα οξυγόνου."""
    # Ποσοστό οξυγόνου εκτός [0, 1]
    with pytest.raises(ValueError, match="ποσοστό οξυγόνου"):
        ypologise_meriki_piesi_oxygonou(-0.05, 101325.0)

    with pytest.raises(ValueError, match="ποσοστό οξυγόνου"):
        ypologise_meriki_piesi_oxygonou(1.5, 101325.0)

    # Αρνητική πίεση
    with pytest.raises(ValueError, match="πίεση"):
        ypologise_meriki_piesi_oxygonou(0.21, -1000.0)

    # Απόθεμα οξυγόνου - όγκος <= 0
    with pytest.raises(ValueError, match="όγκος"):
        ypologise_apothema_kai_autonomia_oxygonou(0.0, 293.0, 21000.0, 16000.0, 6, 0.04)

    # Θερμοκρασία <= 0
    with pytest.raises(ValueError, match="θερμοκρασία"):
        ypologise_apothema_kai_autonomia_oxygonou(100.0, 0.0, 21000.0, 16000.0, 6, 0.04)

    # Αρνητικές πιέσεις
    with pytest.raises(ValueError, match="πιέσεις"):
        ypologise_apothema_kai_autonomia_oxygonou(100.0, 293.0, -10.0, 16000.0, 6, 0.04)

    # Αρνητικός αριθμός κατοίκων
    with pytest.raises(ValueError, match="αριθμός κατοίκων"):
        ypologise_apothema_kai_autonomia_oxygonou(100.0, 293.0, 21000.0, 16000.0, -2, 0.04)

    # Αρνητική κατανάλωση ή παραγωγή
    with pytest.raises(ValueError, match="ρυθμοί"):
        ypologise_apothema_kai_autonomia_oxygonou(100.0, 293.0, 21000.0, 16000.0, 6, -0.04)

    # Παραβίαση κατωφλίου ασφαλείας (μερική πίεση <= κατώφλι)
    posotita_mol, maza, autonomia, katastasi = ypologise_apothema_kai_autonomia_oxygonou(
        ogkos_m3=100.0,
        thermokrasia_k=293.0,
        meriki_piesi_oxygonou_pa=15000.0,  # κάτω από το κατώφλι 16000 Pa
        katwfli_asfaleias_piesis_pa=16000.0,
        arithmos_katoikwn=6,
        katanalwsi_ana_atomo_kg_h=0.04,
        rythmos_paragwgis_kg_h=0.0,
    )
    assert posotita_mol == 0.0
    assert maza == 0.0
    assert autonomia == 0.0
    assert katastasi == "katwfli_paraviasmeno"


# ============================================================================
# 5. PHY-04: Ηλεκτρικό Ισοζύγιο & Αυτονομία
# ============================================================================


def test_phy04_oria_kai_sfalmata():
    """Έλεγχοι ορίων και ειδικών καταστάσεων για το ηλεκτρικό ισοζύγιο."""
    # Αρνητικές ισχείς
    with pytest.raises(ValueError, match="ισχύος"):
        ypologise_ilektriko_isozygio_kai_autonomia(-1.0, 10.0, 2.0, 0.0, 50.0)

    # Αρνητικές ενέργειες μπαταρίας
    with pytest.raises(ValueError, match="ενέργεια συσσωρευτή"):
        ypologise_ilektriko_isozygio_kai_autonomia(5.0, 5.0, 0.0, 0.0, -10.0)

    # Πλεόνασμα ή ισοζύγιο (παραγωγή >= φορτία)
    fortia, elleimma, diathesimi, autonomia, katastasi = ypologise_ilektriko_isozygio_kai_autonomia(
        paragwgi_kw=20.0,
        krisima_fortia_kw=10.0,
        anavlita_fortia_kw=2.0,
        apwleies_kw=0.5,
        energeia_syssorefti_kwh=50.0,
        efedreia_syssorefti_kwh=10.0,
        efedreia_idi_afairemeni=False,
    )
    assert elleimma == 0.0
    assert diathesimi == 40.0
    assert autonomia is None
    assert katastasi == "pleonasma_i_isozigio"

    # Έλλειμμα αλλά μηδενική διαθέσιμη ενέργεια (εκκένωση εφεδρείας)
    fortia, elleimma, diathesimi, autonomia, katastasi = ypologise_ilektriko_isozygio_kai_autonomia(
        paragwgi_kw=5.0,
        krisima_fortia_kw=10.0,
        anavlita_fortia_kw=0.0,
        apwleies_kw=0.0,
        energeia_syssorefti_kwh=10.0,
        efedreia_syssorefti_kwh=10.0,
        efedreia_idi_afairemeni=False,
    )
    assert elleimma == 5.0
    assert diathesimi == 0.0
    assert autonomia == 0.0
    assert katastasi == "ekkenwsi_efedreias"


# ============================================================================
# 6. PHY-05: Ισοζύγιο Νερού
# ============================================================================


def test_phy05_oria_kai_sfalmata():
    """Έλεγχοι ορίων και καταστάσεων ισοζυγίου νερού."""
    # Μη έγκυρος όγκος ή χωρητικότητα
    with pytest.raises(ValueError, match="Μη έγκυρος όγκος"):
        ypologise_isozygio_nerou(-1.0, 1000.0, 0.0, 0.0, 10.0, 0.0, 0.0)

    with pytest.raises(ValueError, match="Μη έγκυρος όγκος"):
        ypologise_isozygio_nerou(500.0, 0.0, 0.0, 0.0, 10.0, 0.0, 0.0)

    # Αρνητικές εισροές
    with pytest.raises(ValueError, match="εισροές"):
        ypologise_isozygio_nerou(500.0, 1000.0, -10.0, 0.0, 10.0, 0.0, 0.0)

    # Αρνητικές αναλώσεις
    with pytest.raises(ValueError, match="αναλώσεις"):
        ypologise_isozygio_nerou(500.0, 1000.0, 0.0, 0.0, -5.0, 0.0, 0.0)

    # Κατάσταση: Κάτω από την εφεδρεία ασφαλείας
    epomenos, yperxeilisi, katastasi = ypologise_isozygio_nerou(
        trexwn_ogkos_l=300.0,
        xwritikotita_l=1000.0,
        ekswteriki_eisroi_l=0.0,
        epistrofi_anakyklwsis_l=0.0,
        ardefsi_l=150.0,
        loipes_analwseis_l=0.0,
        diarros_l=0.0,
        efedreia_asfaleias_l=200.0,
    )
    assert epomenos == 150.0
    assert yperxeilisi == 0.0
    assert katastasi == "katw_apo_efedreia"

    # Κατάσταση: Υπερχείλιση
    epomenos, yperxeilisi, katastasi = ypologise_isozygio_nerou(
        trexwn_ogkos_l=900.0,
        xwritikotita_l=1000.0,
        ekswteriki_eisroi_l=200.0,
        epistrofi_anakyklwsis_l=0.0,
        ardefsi_l=0.0,
        loipes_analwseis_l=0.0,
        diarros_l=0.0,
        efedreia_asfaleias_l=100.0,
    )
    assert epomenos == 1000.0
    assert yperxeilisi == 100.0
    assert katastasi == "yperxeilisi"


# ============================================================================
# 7. PHY-06 & PHY-07: Κίνηση & Επιστροφή Rover
# ============================================================================


def test_phy06_oria_kai_sfalmata():
    """Έλεγχοι ορίων για την ενέργεια κίνησης του rover."""
    # Μάζα <= 0 ή απόσταση < 0
    with pytest.raises(ValueError, match="μάζα"):
        ypologise_energeia_kinisis_oximatos(0.0, 1000.0)

    with pytest.raises(ValueError, match="μάζα"):
        ypologise_energeia_kinisis_oximatos(800.0, -10.0)

    # Απόδοση κινητήρα εκτός (0, 1]
    with pytest.raises(ValueError, match="απόδοση"):
        ypologise_energeia_kinisis_oximatos(800.0, 1000.0, apodosi_kinisis=0.0)

    with pytest.raises(ValueError, match="απόδοση"):
        ypologise_energeia_kinisis_oximatos(800.0, 1000.0, apodosi_kinisis=1.5)

    # Μη έγκυρη τριβή, ισχύς ή ταχύτητα
    with pytest.raises(ValueError, match="παράμετροι τριβής"):
        ypologise_energeia_kinisis_oximatos(800.0, 1000.0, syntelestis_kylisis=-0.01)

    with pytest.raises(ValueError, match="παράμετροι τριβής"):
        ypologise_energeia_kinisis_oximatos(800.0, 1000.0, voithitiki_isxys_w=-10.0)

    with pytest.raises(ValueError, match="παράμετροι τριβής"):
        ypologise_energeia_kinisis_oximatos(800.0, 1000.0, taxytita_m_s=0.0)


def test_phy07_oria_kai_sfalmata():
    """Έλεγχοι ορίων και προειδοποιήσεων για ασφάλεια επιστροφής rover."""
    # Αρνητική απόσταση
    with pytest.raises(ValueError, match="απόσταση"):
        ypologise_xrono_epistrofis_kai_asfaleia(-1.0, 4.0, 0.6, 0.8, 0.2, 500.0)

    # Αρνητικές ενεργειακές παράμετροι
    with pytest.raises(ValueError, match="ενεργειακές παράμετροι"):
        ypologise_xrono_epistrofis_kai_asfaleia(2.0, 4.0, -0.6, 0.8, 0.2, 500.0)

    # Ανεπαρκής ενέργεια (μη ενεργειακά εφικτή επιστροφή)
    apotelesma = ypologise_xrono_epistrofis_kai_asfaleia(
        apostasi_km=10.0,
        taxytita_kmh=4.0,
        mesi_isxys_kw=1.0,  # 2.5 h * 1 kW = 2.5 kWh
        diathesimi_energeia_kwh=1.0,  # διαθέσιμη < 2.5 kWh
        efedreia_asfaleias_kwh=0.2,
        oratotita_m=1000.0,
        katastasi_tilemetrias="egkyri",
    )
    assert apotelesma["energeiaka_efikto"] is False
    assert apotelesma["synolika_asfalis_epistrofi"] is False
    assert any("Ανεπαρκής ενέργεια" in stoixeio_pi for stoixeio_pi in apotelesma["proeidopoiiseis"])
