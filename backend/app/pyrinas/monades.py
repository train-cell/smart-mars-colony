"""Μονάδες μέτρησης και αυστηρές μετατροπές SI / πρακτικών μονάδων.

Κάθε συνάρτηση είναι καθαρή (pure), χωρίς εξωτερικές εξαρτήσεις,
και συνοδεύεται από σαφείς ελέγχους ορίων.
"""

from backend.app.fysika_montela.fysika_montela import elegxos_peperasmenwn


@elegxos_peperasmenwn
def kelvin_se_vathmous_kelsiou(thermokrasia_k: float) -> float:
    """Μετατροπή θερμοκρασίας από Kelvin σε βαθμούς Κελσίου (°C)."""
    if thermokrasia_k < 0.0:
        raise ValueError("Η θερμοκρασία σε Kelvin δεν μπορεί να είναι αρνητική.")
    return thermokrasia_k - 273.15


@elegxos_peperasmenwn
def vathmoi_kelsiou_se_kelvin(thermokrasia_c: float) -> float:
    """Μετατροπή θερμοκρασίας από βαθμούς Κελσίου (°C) σε Kelvin."""
    thermokrasia_k = thermokrasia_c + 273.15
    if thermokrasia_k < 0.0:
        raise ValueError("Η θερμοκρασία δεν μπορεί να είναι χαμηλότερη από το απόλυτο μηδέν.")
    return thermokrasia_k


@elegxos_peperasmenwn
def joule_se_kilovatawres(energeia_j: float) -> float:
    """Μετατροπή ενέργειας από Joule σε κιλοβατώρες (1 kWh = 3.600.000 J)."""
    if energeia_j < 0.0:
        raise ValueError("Η ενέργεια δεν μπορεί να είναι αρνητική.")
    return energeia_j / 3_600_000.0


@elegxos_peperasmenwn
def kilovatawres_se_joule(energeia_kwh: float) -> float:
    """Μετατροπή ενέργειας από κιλοβατώρες σε Joule."""
    if energeia_kwh < 0.0:
        raise ValueError("Η ενέργεια δεν μπορεί να είναι αρνητική.")
    return energeia_kwh * 3_600_000.0


@elegxos_peperasmenwn
def kyvika_metra_se_litra(ogkos_m3: float) -> float:
    """Μετατροπή όγκου από κυβικά μέτρα (m³) σε λίτρα (L). 1 m³ = 1000 L."""
    if ogkos_m3 < 0.0:
        raise ValueError("Ο όγκος δεν μπορεί να είναι αρνητικός.")
    return ogkos_m3 * 1000.0


@elegxos_peperasmenwn
def litra_se_kyvika_metra(ogkos_l: float) -> float:
    """Μετατροπή όγκου από λίτρα (L) σε κυβικά μέτρα (m³). 1 L = 0.001 m³."""
    if ogkos_l < 0.0:
        raise ValueError("Ο όγκος δεν μπορεί να είναι αρνητικός.")
    return ogkos_l * 0.001


@elegxos_peperasmenwn
def pascal_se_kpascal(piesi_pa: float) -> float:
    """Μετατροπή πίεσης από Pascal (Pa) σε kiloPascal (kPa)."""
    if piesi_pa < 0.0:
        raise ValueError("Η πίεση δεν μπορεί να είναι αρνητική.")
    return piesi_pa / 1000.0


@elegxos_peperasmenwn
def kpascal_se_pascal(piesi_kpa: float) -> float:
    """Μετατροπή πίεσης από kiloPascal (kPa) σε Pascal (Pa)."""
    if piesi_kpa < 0.0:
        raise ValueError("Η πίεση δεν μπορεί να είναι αρνητική.")
    return piesi_kpa * 1000.0


@elegxos_peperasmenwn
def wres_se_defterolepta(wres: float) -> float:
    """Μετατροπή χρόνου από ώρες σε δευτερόλεπτα (1 h = 3600 s)."""
    if wres < 0.0:
        raise ValueError("Ο χρόνος δεν μπορεί να είναι αρνητικός.")
    return wres * 3600.0


@elegxos_peperasmenwn
def defterolepta_se_wres(defterolepta: float) -> float:
    """Μετατροπή χρόνου από δευτερόλεπτα σε ώρες."""
    if defterolepta < 0.0:
        raise ValueError("Ο χρόνος δεν μπορεί να είναι αρνητικός.")
    return defterolepta / 3600.0


@elegxos_peperasmenwn
def isxys_kai_xronos_se_joule(isxys_w: float, xronos_s: float) -> float:
    """Υπολογισμός ενέργειας σε Joule από ισχύ (Watt) και χρόνο (δευτερόλεπτα)."""
    if isxys_w < 0.0 or xronos_s < 0.0:
        raise ValueError("Η ισχύς και ο χρόνος πρέπει να είναι μη αρνητικά μεγέθη.")
    return isxys_w * xronos_s
