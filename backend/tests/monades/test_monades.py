"""Δοκιμές μονάδας για μετατροπές μονάδων μέτρησης (SI και πρακτικές μονάδες)."""

import pytest

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


def test_metatropes_thermokrasias():
    """Έλεγχος Kelvin <-> Κελσίου."""
    # 273.15 K == 0.0 °C
    assert kelvin_se_vathmous_kelsiou(273.15) == pytest.approx(0.0)
    assert vathmoi_kelsiou_se_kelvin(0.0) == pytest.approx(273.15)

    # 293.15 K == 20.0 °C
    assert kelvin_se_vathmous_kelsiou(293.15) == pytest.approx(20.0)
    assert vathmoi_kelsiou_se_kelvin(20.0) == pytest.approx(293.15)

    with pytest.raises(ValueError):
        kelvin_se_vathmous_kelsiou(-1.0)

    with pytest.raises(ValueError):
        vathmoi_kelsiou_se_kelvin(-300.0)


def test_metatropes_energeias_kai_isxyos():
    """Έλεγχος Joule <-> kWh και W*s == J."""
    # 1 kWh = 3.600.000 J
    assert kilovatawres_se_joule(1.0) == 3_600_000.0
    assert joule_se_kilovatawres(3_600_000.0) == 1.0

    # 1000 W επί 3600 s = 3.600.000 J = 1 kWh
    assert isxys_kai_xronos_se_joule(1000.0, 3600.0) == 3_600_000.0


def test_metatropes_ogkou():
    """Έλεγχος m³ <-> L."""
    # 1 m³ = 1000 L, 1 L = 0.001 m³
    assert kyvika_metra_se_litra(1.5) == 1500.0
    assert litra_se_kyvika_metra(1500.0) == 1.5


def test_metatropes_piesis():
    """Έλεγχος Pa <-> kPa."""
    assert pascal_se_kpascal(101325.0) == pytest.approx(101.325)
    assert kpascal_se_pascal(101.325) == pytest.approx(101325.0)


def test_metatropes_xronou():
    """Έλεγχος h <-> s."""
    assert wres_se_defterolepta(2.5) == 9000.0
    assert defterolepta_se_wres(9000.0) == 2.5
