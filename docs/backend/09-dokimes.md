# 09 - Σουίτα Δοκιμών και Αποτελέσματα Ελέγχου

## 1. Δομή Σουίτας Δοκιμών
Οι δοκιμές του συστήματος είναι οργανωμένες σε 4 διακριτές κατηγορίες:

- `backend/tests/monades/` (Μονάδες - Unit Tests):
  - `test_fysika_montela.py`: Αμιγείς δοκιμές φυσικών μοντέλων (PHY-01 έως PHY-07), επαλήθευση χρυσών τιμών (golden numbers), έλεγχοι ακραίων και άκυρων τιμών.
  - `test_monades.py`: Έλεγχος συναρτήσεων μετατροπής μονάδων μέτρησης (Kelvin/Celsius, Joules/kWh, Liters/m3, Pascals/kPa).
  - `test_sxhmata.py`: Επικύρωση Pydantic DTOs, Enums και τυποποιημένων φακέλων σφαλμάτων.
- `backend/tests/enopoiisi/` (Ενοποίηση - Integration Tests):
  - `test_ypostiriksi_zwis.py`: Πλήρης ροή προεπισκόπησης και ρύθμισης θερμοκρασίας, διαχείριση σφαλμάτων εκτός ορίων.
  - `test_poroi_kai_ardefsi.py`: Ροή προεπισκόπησης, επιβεβαίωσης και ακύρωσης άρδευσης, έλεγχος απόρριψης λόγω ανεπάρκειας νερού.
  - `test_apostoles_kai_rover.py`: Ροή rover safe stop, αξιολόγηση ενεργειακής εφικτότητας και υποβάθμισης επικοινωνίας.
  - `test_asfaleia_kai_dikaiwmata.py`: Έλεγχος απαγορεύσεων RBAC (403), εξουσιοδότηση συντονιστή, αποτροπή διπλής εκτέλεσης με `Idempotency-Key`, εκχώρηση και ανάκληση δικαιωμάτων.
  - `test_synagermoi.py`: Κύκλος ζωής συναγερμών (έκδοση, αναγνώριση, επίλυση).
  - `test_epipleon_kalipsi.py`: Μετρήσεις αισθητήρων, διαχείριση χρηστών, ανακύκλωση νερού, φωτισμός, αναβολές αποστολών και audit log.
- `backend/tests/senaria/` (Σενάρια - Scenario Tests):
  - `test_kataigida_skonis.py`: Ολοκληρωμένη προσομοίωση καταιγίδας σκόνης, πτώση φωτοβολταϊκών στα 0.8 kW, αύξηση θερμικών απωλειών στα 10 kW, αναστολή φορτίων και αύξηση αυτονομίας κατά +42.29 λεπτά.
- `backend/tests/symvolaia/` (Συμβόλαια - Contract Tests):
  - `test_symvolaia_kai_openapi.py`: Επαλήθευση OpenAPI schema, endpoints υγείας, προσομοίωσης, και αυστηρή επικύρωση κανόνα Greeklish (§0A) σε όλα τα paths και schemas.

---

## 2. Εκτέλεση και Στατιστικά Κάλυψης

### Εντολή Εκτέλεσης
```bash
pytest --cov=backend/app --cov-report=term-missing
```

### Σύνοψη Αποτελεσμάτων
- **Συνολικός Αριθμός Δοκιμών:** 77 δοκιμές
- **Επιτυχείς:** 77 / 77 (100% επιτυχία)
- **Αποτυχίες:** 0
- **Συνολική Κάλυψη Κώδικα (Coverage):** **100.0%** (1.941 / 1.941 statements, 0 missing)

| Άρθρωμα | Γραμμές (Stmts) | Μη-καλυμμένες (Miss) | Κάλυψη (Cover) |
| :--- | :---: | :---: | :---: |
| `backend/app/main.py` | 41 | 0 | 100% |
| `backend/app/pyrinas/*` | 141 | 0 | 100% |
| `backend/app/sxhmata/koina.py` | 75 | 0 | 100% |
| `backend/app/arxika_dedomena/fortwsi_dedomenwn.py` | 50 | 0 | 100% |
| `backend/app/montela/*` (όλα τα 24 ORM μοντέλα) | 361 | 0 | 100% |
| `backend/app/fysika_montela/*` (PHY-01 έως 07) | 136 | 0 | 100% |
| `backend/app/apothikes/*` (όλα τα 4 Repositories) | 176 | 0 | 100% |
| `backend/app/ypiresies/*` (όλες οι 4 Υπηρεσίες) | 466 | 0 | 100% |
| `backend/app/api/v1/*` (όλα τα 11 Routers) | 449 | 0 | 100% |
| `backend/app/vasi/synthesi.py` | 26 | 0 | 100% |
| **Σύνολο Συστήματος (TOTAL)** | **1.941** | **0** | **100%** |
| `backend/app/ypiresies/ypiresia_symvantwn_kai_senariwn.py` | 166 | 11 | 93% |
| `backend/app/ypiresies/ypiresia_porwn.py` | 130 | 24 | 82% |
| `backend/app/fysika_montela/fysika_montela.py` | 136 | 30 | 78% |
| **ΣΥΝΟΛΟ (TOTAL)** | **1933** | **204** | **89%** |
