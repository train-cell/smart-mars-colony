# Smart Mars Colony — Σύστημα Διαχείρισης Αποικίας στον Άρη (Backend)

Το παρόν αποθετήριο περιέχει την πλήρη υλοποίηση του backend για την εκπαιδευτική προσομοίωση **Smart Mars Colony** (ακαδημαϊκό έτος 2026–2027). Το σύστημα υλοποιεί όλες τις απαραίτητες υπηρεσίες παρακολούθησης συνθηκών, ελέγχου υποστήριξης ζωής, διαχείρισης πόρων (νερό, ενέργεια), ασφάλειας αποστολών οχήματος εξερεύνησης (rover) και συντονισμού αντιμετώπισης καταιγίδας σκόνης.

> [!IMPORTANT]
> **Αποκλειστικά Backend:** Το παρόν repository περιέχει μόνο backend κώδικα, API endpoints, βάση δεδομένων, φυσικά μοντέλα και δοκιμές. Δεν περιέχει κώδικα διεπαφής χρήστη (frontend UI). Το API contract παρέχεται αναλυτικά στο φάκελο `docs/koino/` για την ανεξάρτητη ανάπτυξη frontend.

---

## Τεχνολογικό Stack

- **Γλώσσα:** Python 3.12+
- **Web Framework:** FastAPI (ασύγχρονο REST API με αυτόματο OpenAPI / Swagger)
- **Μοντελοποίηση / Επικύρωση:** Pydantic v2
- **Βάση Δεδομένων & ORM:** SQLite 3 & SQLAlchemy 2.0 (με υποστήριξη foreign keys, transactions & optimistic concurrency)
- **Διαχείριση Σχήματος:** Alembic Migrations
- **Έλεγχος Ποιότητας & Δοκιμές:** pytest, pytest-cov, httpx, Ruff
- **Σύμβαση Ονοματοδοσίας:** Greeklish σε όλα τα εσωτερικά και δημόσια identifiers (συναρτήσεις, κλάσεις, πεδία, πίνακες, διαδρομές API)
- **Γλώσσα Τεκμηρίωσης:** Ελληνικά

---

## Γρήγορη Εκκίνηση

### 1. Προετοιμασία Περιβάλλοντος

```bash
# Δημιουργία εικονικού περιβάλλοντος με Python 3.12
uv venv --python python3.12 .venv
source .venv/bin/activate

# Εγκατάσταση εξαρτήσεων
uv pip install -e ".[dev]"
```

### 2. Εκτέλεση Μεταναστεύσεων Βάσης Δεδομένων & Αρχικοποίηση Δεδομένων

```bash
# Εφαρμογή Alembic migrations
alembic upgrade head

# Φόρτωση αρχικών δεδομένων επίδειξης (seed)
python scripts/arxika_dedomena.py
```

### 3. Εκκίνηση Εξυπηρετητή (Development Server)

```bash
uvicorn backend.app.main:efarmogi --reload --port 8000
```

- **Διαδραστική Τεκμηρίωση Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **OpenAPI Schema (JSON):** [http://localhost:8000/openapi.json](http://localhost:8000/openapi.json)
- **Έλεγχος Υγείας Συστήματος:** [http://localhost:8000/api/v1/ygeia](http://localhost:8000/api/v1/ygeia)

### 4. Εκτέλεση Δοκιμών (Test Suite)

```bash
# Εκτέλεση όλων των ελέγχων
pytest

# Έλεγχος κάλυψης κώδικα (coverage)
pytest --cov=backend/app --cov-report=term-missing
```

---

## Αρχιτεκτονική Δομή Αποθετηρίου

```text
smart-mars-colony/
├── README.md                         # Κύρια τεκμηρίωση έργου (Ελληνικά)
├── CHANGELOG.md                      # Ιστορικό αλλαγών (Ελληνικά)
├── pyproject.toml                    # Ρυθμίσεις πακέτου και εξαρτήσεων
├── alembic.ini                       # Ρυθμίσεις Alembic migrations
├── migrations/                       # Ιστορικό μεταναστεύσεων βάσης
├── backend/
│   ├── app/
│   │   ├── main.py                   # Κεντρικό σημείο εισόδου FastAPI
│   │   ├── pyrinas/                  # Ρυθμίσεις, αυθεντικοποίηση, RBAC, σφάλματα, μονάδες
│   │   ├── api/v1/                   # REST Routers ανά υποσύστημα
│   │   ├── vasi/                     # Σύνδεση SQLite, συνεδρίες, Base ORM
│   │   ├── montela/                  # Πίνακες ORM (SQLAlchemy)
│   │   ├── sxhmata/                  # Pydantic DTOs & Schemas
│   │   ├── apothikes/                # Πρόσβαση δεδομένων (Repositories)
│   │   ├── ypiresies/                # Επιχειρησιακή λογική & ροές εντολών
│   │   ├── fysika_montela/           # Καθαρές μαθηματικές συναρτήσεις φυσικής
│   │   ├── prosomoiwsi/              # Ρολόι, καταστάσεις & σενάρια προσομοίωσης
│   │   ├── symvanta/                 # Διαχείριση γεγονότων & επανυπολογισμοί
│   │   └── arxika_dedomena/          # Δεδομένα επίδειξης (Seed fixtures)
│   └── tests/                        # Αυτοματοποιημένες δοκιμές (pytest)
│       ├── monades/                  # Δοκιμές μονάδας (φυσικά μοντέλα, συναρτήσεις)
│       ├── enopoiisi/                # Δοκιμές ενοποίησης υπηρεσιών και βάσης
│       ├── symvolaia/                # Δοκιμές συμβολαίων API και OpenAPI
│       └── senaria/                  # Δοκιμές ολοκληρωμένων σεναρίων (π.χ. καταιγίδα)
├── docs/
│   ├── backend/                      # Πλήρης ελληνική τεχνική τεκμηρίωση (00-17)
│   ├── koino/                        # Συμβόλαια διασύνδεσης προς τη φοιτήτρια frontend
│   └── eswterika/                    # Εσωτερικές αναφορές παράδοσης υποπρακτόρων
└── scripts/                          # Βοηθητικά σενάρια εκτέλεσης και αρχικοποίησης
```

---

## Τεκμηρίωση & Συμβόλαιο Frontend

- **Πλήρης Τεχνική Τεκμηρίωση Backend:** [`docs/backend/`](docs/backend/)
- **Συμβόλαιο Διεπαφής Frontend-Backend:** [`docs/koino/symvolaio-frontend-backend.md`](docs/koino/symvolaio-frontend-backend.md)
- **Ροές Επίδειξης (Θερμοκρασία, Άρδευση, Καταιγίδα):** [`docs/koino/roes-epideiksis.md`](docs/koino/roes-epideiksis.md)
- **Αντιστοίχιση HTA / Norman με API Endpoints:** [`docs/koino/antistoixisi-hta-norman-api.md`](docs/koino/antistoixisi-hta-norman-api.md)
- **Κανόνες Ονοματοδοσίας Greeklish:** [`docs/backend/17-kanones-onomatodosias.md`](docs/backend/17-kanones-onomatodosias.md)
