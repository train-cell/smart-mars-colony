# Συντονισμός Υποπρακτόρων (Multi-Agent Orchestration)

Το παρόν έγγραφο καταγράφει την οργάνωση της πολυ-πρακτορικής ανάπτυξης του backend για το **Smart Mars Colony**, σύμφωνα με τις προδιαγραφές της ενότητας §13 της αποστολής.

---

## 1. Ρόλος του Orchestrator (Κεντρικός Συντονιστής)

Ο Orchestrator (Antigravity) έχει τη συνολική ευθύνη για:
1. Την επιβολή των κανόνων ονοματοδοσίας Greeklish και των συμβολαίων API.
2. Την αποκλειστική διαχείριση των κοινών αρχείων (`main.py`, Alembic migrations, database sessions, OpenAPI, `CHANGELOG.md`, `README.md`).
3. Την ανάθεση σαφώς οριοθετημένων πακέτων εργασίας σε εξειδικευμένους υποπράκτορες (sub-agents).
4. Την αξιολόγηση και συγχώνευση των παραδοτέων (handoffs) μετά από έλεγχο δοκιμών.
5. Την εκτέλεση της τελικής ενοποίησης, ανεξάρτητου ελέγχου και αναφοράς.

---

## 2. Ομάδα Υποπρακτόρων και Πεδία Ευθύνης

| Υποπράκτορας | Κύρια Ευθύνη | Εργασίες | Ιδιόκτητα Αρχεία | Εξαρτήσεις |
|---|---|---|---|---|
| **A — Pyrinas & Vasi** | Ρυθμίσεις, SQLite σύνδεση, RBAC, Sessions, Common DTOs, Base ORM, Error Handling | CORE-01…CORE-15 | `pyrinas/`, `vasi/`, `montela/vasi_montelwn.py`, `sxhmata/koina.py` | Καμία (εκκινεί πρώτος) |
| **B — Fysika Montela** | Καθαρές μαθηματικές συναρτήσεις φυσικής & golden tests | PHY-01…PHY-07, TEST-01…TEST-07 | `fysika_montela/`, `tests/monades/` | Ανεξάρτητο από τη βάση δεδομένων |
| **C — Ypostiriksi Zwis** | Χώροι κατοίκησης, έλεγχος θερμοκρασίας, O₂/CO₂, previews & εντολές | LIFE-01…LIFE-10 | `montela/ypostiriksi_zwis.py`, `ypiresies/ypostiriksi_zwis.py`, `api/v1/ypostiriksi_zwis.py` | Συμβόλαια από A, Φυσικά από B |
| **D — Poroi** | Θερμοκήπια, άρδευση, ανακύκλωση νερού, φωτοβολταϊκά, ηλεκτρικά φορτία | RES-01…RES-14 | `montela/poroi.py`, `ypiresies/poroi.py`, `api/v1/poroi.py` | Συμβόλαια από A, Φυσικά από B |
| **E — Apostoles & Kindynoi** | Οχήματα εξερεύνησης (rover), υπολογισμός ενέργειας επιστροφής, κίνδυνοι, ασφαλής στάση | MISSION-01…MISSION-08 | `montela/apostoles.py`, `ypiresies/apostoles.py`, `api/v1/apostoles.py` | Συμβόλαια από A, Φυσικά από B |
| **F — Senario & Enopoiisi** | Διαχείριση συμβάντων, επανυπολογισμοί, fixture καταιγίδας, συναγερμοί, μεταβίβαση ελέγχου | SHARED-01…09, STORM-01…10 | `symvanta/`, `prosomoiwsi/`, `api/v1/senaria.py`, `tests/senaria/` | Μετά τα A, B, C, D, E |
| **G — Aneksartitos Elegktis** | Ανεξάρτητος έλεγχος συμμόρφωσης (Greeklish, edge cases, P0–P3 findings) | TEST-21…28 | `tests/`, αναφορά ελέγχου στο `docs/eswterika/` | Ενοποιημένο build |
| **H — Tekmiriosi & Symvolaia** | Ελληνική τεκμηρίωση backend (00-17), συμβόλαια frontend (`docs/koino/`), CHANGELOG | DOC-01…DOC-17 | `docs/backend/`, `docs/koino/` | Όλα τα ολοκληρωμένα υποσυστήματα |

---

## 3. Πρωτόκολλο Παράδοσης (Handoff Protocol)

Κάθε υποπράκτορας παραδίδει αναφορά στο φάκελο `docs/eswterika/paradoseis-praktorwn/` με τη μορφή:
- Αναγνωριστικό εργασίας και ρόλος
- Λίστα τροποποιημένων / νέων αρχείων
- Αποτελέσματα δοκιμών (ακριβή exit code και output)
- Παραδοχές και τεχνικές αποφάσεις
- Σύνοψη για το `CHANGELOG.md`
