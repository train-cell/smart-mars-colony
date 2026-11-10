# Από καθαρό checkout σε λειτουργικό API

```sh
uv sync --frozen --extra dev
cp .env.example .env
uv run --frozen alembic upgrade head
uv run --frozen python -m scripts.arxika_dedomena
uv run --frozen uvicorn backend.app.main:efarmogi --host 127.0.0.1 --port 8000
```
Οι εντολές εκτελούνται από τη ρίζα του repository. Χρειάζεται Python ≥3.12. Το `uv.lock` κλειδώνει τις ακριβείς εκδόσεις· το `--frozen` αποτρέπει σιωπηλή ανανέωσή τους. Η εφαρμογή δεν κατασκευάζει πίνακες στην εκκίνηση: προηγείται υποχρεωτικά το Alembic. Η αρχικοποίηση δεδομένων είναι επαναλήψιμη και συμπληρώνει παλιά δεδομένα χωρίς διαγραφή. Το `--reset` διαγράφει τα δεδομένα της επιλεγμένης εκπαιδευτικής βάσης και προορίζεται μόνο για συνειδητή επαναφορά.


```sh
curl -s http://127.0.0.1:8000/api/v1/ygeia
curl -s http://127.0.0.1:8000/api/v1/xwroi-katoikisis/xwros_01/katastasi
curl -s -X POST http://127.0.0.1:8000/api/v1/xwroi-katoikisis/xwros_01/thermokrasia/proepiskopisi \
  -H 'Content-Type: application/json' -H 'X-Id-Xristi: xristis_zwis' \
  -d '{"epithymiti_thermokrasia_k":295,"anamenomeni_ekdosi_katastasis":1}'
```

Το 1 είναι η αρχική έκδοση μετά από καθαρή αρχικοποίηση. Στην κανονική χρήση προηγείται ανάγνωση της τρέχουσας έκδοσης. Κρατήστε το `id_proepiskopisis` και επιβεβαιώστε με αυτό και την ίδια έκδοση. Η ακριβής ροή είναι στο `docs/koino/roes-epideiksis.md`.

Εάν λείπει πίνακας/στήλη, ελέγξτε ότι το `DIADROMI_VASIS` δείχνει στην ίδια βάση κατά migration και server και ότι εκτελέστηκε `alembic upgrade head`. Μην διαγράψετε την προσωπική βάση για να διορθώσετε migration. Εάν εμφανιστεί 409, ανακτήστε νέα κατάσταση και δημιουργήστε νέα προεπισκόπηση. Εάν εμφανιστεί 503, διαβάστε την ποιότητα/αισθητήρα· το reset δεν είναι απαραίτητο όταν αρκεί εκπαιδευτική αποκατάσταση. Εάν λείπει ταυτότητα, επιλέξτε ρητό χρήστη.

Τα tests δεν απαιτούν ενεργό server. Τα εργαλεία δοκιμών χρησιμοποιούν προσωρινή SQLite. Η εκκίνηση σε κενή βάση χωρίς migrations δεν υποστηρίζεται και καταλήγει σε σαφές σφάλμα εγκατάστασης. Η εξαγωγή OpenAPI γίνεται χωρίς εκκίνηση/seed μέσω `python -m scripts.eksagogi_symvolaiou`.
