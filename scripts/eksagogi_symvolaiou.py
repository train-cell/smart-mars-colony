"""Εξάγει το πραγματικό OpenAPI χωρίς εκκίνηση server ή μεταβολή βάσης."""

import json
from pathlib import Path

from backend.app.main import efarmogi
from backend.app.pyrinas.rythmiseis import rythmiseis


def eksagogi_symvolaiou():
    riza = Path(__file__).resolve().parents[1]
    sxhma = efarmogi.openapi()
    (riza / "docs/koino/openapi.json").write_text(
        json.dumps(sxhma, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    grammes = [
        f"# Αναφορά API · έκδοση {rythmiseis.EKDOSI}",
        "",
        "Η αναφορά εξάγεται από το πραγματικό OpenAPI. Βάση URL:`/api/v1`. Τα ακριβή σώματα, πεδία, όρια και μοντέλα απαντήσεων βρίσκονται στο [OpenAPI](../koino/openapi.json). Παραδείγματα,ρόλοι,χρόνοι και χειρισμός σφαλμάτων στη [σύμβαση διεπαφής](../koino/symvolaio-frontend-backend.md).",
        "",
        "| Μέθοδος | Διαδρομή | Λειτουργία | Σχήμα επιτυχίας |",
        "|---|---|---|---|",
    ]
    plithos = 0
    for diadromi, methodoi in sxhma["paths"].items():
        for methodos, leitourgia in methodoi.items():
            if methodos not in {"get", "post", "put", "delete", "patch"}:
                continue
            apantisi = leitourgia["responses"]["200"]["content"]["application/json"]["schema"]
            onoma = apantisi.get("$ref", apantisi.get("type", "")).rsplit("/", 1)[-1]
            if onoma == "array":
                onoma = (
                    "λίστα "
                    + apantisi["items"]
                    .get("$ref", apantisi["items"].get("type", ""))
                    .rsplit("/", 1)[-1]
                )
            grammes.append(
                f"|{methodos.upper()}|`{diadromi}`|{leitourgia.get('summary', 'Ανάκτηση / εντολή')}|`{onoma}`|"
            )
            plithos += 1
    grammes += [
        "",
        f"Σύνολο:{plithos} λειτουργίες HTTP. Τα σφάλματα400/401/403/404/409/422/500/503 χρησιμοποιούν `ApantisiSfalmatosSxhma`. Η ύπαρξη μοντέλου σφάλματος δεν σημαίνει ότι κάθε endpoint προκαλεί όλους τους κωδικούς.",
        "",
        "Η εντολή εξαγωγής είναι `uv run --frozen python -m scripts.eksagogi_symvolaiou`. Η δοκιμή συμβολαίων απαιτεί ρητό σχήμα επιτυχίας για κάθε λειτουργία. Τα ελεύθερα,ετερογενή ιστορικά στιγμιότυπα δηλώνονται ως JSON τιμές μέσα σε συγκεκριμένα πεδία· ο εξωτερικός φάκελος της απόκρισης είναι τυποποιημένος.",
    ]
    (riza / "docs/backend/04-api.md").write_text("\n".join(grammes) + "\n", encoding="utf-8")
    print(f"Εξήχθησαν {plithos} λειτουργίες API.")


if __name__ == "__main__":
    eksagogi_symvolaiou()
