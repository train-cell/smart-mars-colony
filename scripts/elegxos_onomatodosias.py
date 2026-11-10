"""Συμπληρωματικός έλεγχος ονοματοδοσίας. Δεν υποκαθιστά γλωσσική επιθεώρηση."""

import ast
import re
from pathlib import Path

APAGOREVMENES_LEKSEIS = {
    "temperature",
    "irrigation",
    "greenhouse",
    "battery",
    "sensor",
    "storm",
    "water",
    "habitat",
    "mission",
    "snapshot",
    "baseline",
    "setpoint",
    "stale",
    "router",
    "email",
    "seed",
    "mixin",
    "model",
    "request",
    "response",
    "confirm",
    "cancel",
    "grant",
    "revoke",
    "rollback",
    "generator",
    "edge",
}
# Ακριβή hooks/fixtures τρίτων. Τα ονόματα των εισαγόμενων συναρτήσεων δεν ανήκουν στην εφαρμογή.
EXAIRESEIS_PYTHON = {
    "self",
    "cls",
    "_",
    "__init__",
    "__all__",
    "__tablename__",
    "__mapper_args__",
    "impl",
    "cache_ok",
    "model_config",
    "process_bind_param",
    "process_result_value",
    "tmp_path",
    "monkeypatch",
    "dialect",
}
EXAIRESEIS_ARXEIWN = {"__init__", "main", "conftest"}


def lekseis_onomatos(onoma):
    """Διαχωρίζει snake_case και CamelCase πριν από σύγκριση λεξιλογίου."""
    return set(re.sub(r"([a-z])([A-Z])", r"\1_\2", onoma).lower().split("_"))


def elegxe_onomatodosia(riza=None):
    """Ελέγχει Python, στήλες, δημόσια πεδία και τιμές απαριθμήσεων με σαφή όρια."""
    riza = riza or Path(__file__).resolve().parents[1]
    sfalmata = []
    for diadromi in sorted((riza / "backend").rglob("*.py")):
        dentro = ast.parse(diadromi.read_text(encoding="utf-8"))
        onomata = [
            (n.name, n.lineno)
            for n in ast.walk(dentro)
            if isinstance(n, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef))
        ]
        onomata += [
            (n.id, n.lineno)
            for n in ast.walk(dentro)
            if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Store)
        ]
        onomata += [(n.arg, n.lineno) for n in ast.walk(dentro) if isinstance(n, ast.arg)]
        for onoma, grammi in onomata:
            if onoma in EXAIRESEIS_PYTHON:
                continue
            if not onoma.isascii() or lekseis_onomatos(onoma) & APAGOREVMENES_LEKSEIS:
                sfalmata.append(f"{diadromi.relative_to(riza)}:{grammi}: {onoma}")
    from enum import Enum

    from backend.app.main import efarmogi
    from backend.app.montela import VasiMontelwn
    from backend.app.sxhmata import koina

    for onoma_pinaka, pinakas in VasiMontelwn.metadata.tables.items():
        for onoma in [onoma_pinaka, *(stili.name for stili in pinakas.columns)]:
            if not onoma.isascii() or lekseis_onomatos(onoma) & APAGOREVMENES_LEKSEIS:
                sfalmata.append(f"vasi:{onoma_pinaka}:{onoma}")
    sxhma = efarmogi.openapi()
    for diadromi in sxhma["paths"]:
        if any(lekseis_onomatos(tmima) & APAGOREVMENES_LEKSEIS for tmima in diadromi.split("/")):
            sfalmata.append(f"diadromi:{diadromi}")
    for onoma_sxhmatos, periexomeno in sxhma["components"]["schemas"].items():
        for onoma in periexomeno.get("properties", {}):
            if not onoma.isascii() or lekseis_onomatos(onoma) & APAGOREVMENES_LEKSEIS:
                sfalmata.append(f"sxhma:{onoma_sxhmatos}:{onoma}")
    for onoma, typos in vars(koina).items():
        if (
            isinstance(typos, type)
            and issubclass(typos, Enum)
            and typos.__module__ == koina.__name__
        ):
            for stoixeio in typos:
                if lekseis_onomatos(stoixeio.value) & APAGOREVMENES_LEKSEIS:
                    sfalmata.append(f"aparithmisi:{onoma}:{stoixeio.value}")
    return sorted(set(sfalmata))


if __name__ == "__main__":
    sfalmata = elegxe_onomatodosia()
    if sfalmata:
        raise SystemExit("\n".join(sfalmata))
    print("Επιτυχία ελέγχου Python, SQL και δημόσιων σχημάτων βάσει του δηλωμένου λεξιλογίου.")
