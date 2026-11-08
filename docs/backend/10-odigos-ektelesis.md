# 10 - Οδηγός Εγκατάστασης και Εκτέλεσης (Setup Guide)

Ο παρών οδηγός περιγράφει τα βήματα για τη ρύθμιση, εκτέλεση και επαλήθευση του backend συστήματος από ένα καθαρό περιβάλλον (fresh clone).

---

## 1. Προαπαιτούμενα
- Python 3.12 ή νεότερο
- Εργαλείο διαχείρισης πακέτων: `uv` (συνιστάται) ή `pip` / `venv`
- Git

---

## 2. Εγκατάσταση Εξαρτήσεων

### Χρήση `uv` (Συνιστάται)
```bash
cd smart-mars-colony

# Δημιουργία εικονικού περιβάλλοντος
uv venv .venv --python 3.12

# Ενεργοποίηση
source .venv/bin/activate

# Εγκατάσταση του πακέτου σε λειτουργία ανάπτυξης με όλες τις εξαρτήσεις
uv pip install -e ".[dev]"
```

### Χρήση κλασικού `pip`
```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

---

## 3. Ρύθμιση Περιβάλλοντος
Αντιγράψτε το αρχείο ρυθμίσεων:
```bash
cp .env.example .env
```
Προεπιλεγμένες τιμές στο `.env`:
```ini
PERIVALLON=anaptyxi
DIADROMI_VASIS=sqlite:///smart_mars_colony.db
AYTOMATI_ARXIKOPOIISI=true
LOG_LEVEL=INFO
```

---

## 4. Μεταπτώσεις Βάσης Δεδομένων (Alembic)
Για την εκτέλεση των μεταπτώσεων και τη δημιουργία του σχήματος στη SQLite βάση:
```bash
alembic upgrade head
```

---

## 5. Εκτέλεση Εξυπηρετητή (FastAPI / Uvicorn)
Εκκινήστε τον εξυπηρετητή με υποστήριξη αυτόματης επαναφόρτωσης:
```bash
uvicorn backend.app.main:efarmogi --host 0.0.0.0 --port 8000 --reload
```

Με την εκκίνηση, το σύστημα εκτελεί αυτόματα τη φόρτωση αρχικών δεδομένων επίδειξης (seed data) μέσω του `lifespan` handler.

### Επαλήθευση Λειτουργίας
- **Health Check:** `http://localhost:8000/health`
- **Διαδραστική Τεκμηρίωση Swagger UI:** `http://localhost:8000/docs`
- **Τεκμηρίωση ReDoc:** `http://localhost:8000/redoc`

---

## 6. Εκτέλεση Δοκιμών και Ελέγχων Ποιότητας

### Εκτέλεση Πλήρους Σουίτας Δοκιμών με Κάλυψη
```bash
pytest --cov=backend/app --cov-report=term-missing
```

### Έλεγχος Κώδικα και Μορφοποίηση (Ruff)
```bash
# Έλεγχος linter
ruff check .

# Έλεγχος μορφοποίησης
ruff format --check .
```
