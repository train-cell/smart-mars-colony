# Αναφορά Παράδοσης: MISSION-01 έως MISSION-08 (Αποστολές & Rover)

- **ID Εργασίας:** MISSION-01…08, TEST-07, TEST-11, TEST-15
- **Υποπράκτορας:** E — Apostoles & Rover
- **Αρχεία Υλοποίησης:**
  - `backend/app/montela/apostoles.py`
  - `backend/app/apothikes/apothiki_apostolwn.py`
  - `backend/app/ypiresies/ypiresia_apostolwn.py`
  - `backend/app/api/v1/apostoles.py`
  - `backend/tests/enopoiisi/test_apostoles_kai_rover.py`
- **HQ Skills που χρησιμοποιήθηκαν:**
  - `api_design`: Τηλεμετρικά σχήματα rover, κατάσταση οχήματος, διαχείριση αποστολών εξωτερικής δραστηριότητας (EVA).
  - `security-and-hardening`: Αυστηρή απαίτηση ρόλου χειριστή οχήματος (`xeiristis_oximatos`) ή συντονιστή.
  - `backend_patterns`: Διαχείριση κατάστασης αβεβαιότητας (`avevaio`) σε περιπτώσεις απώλειας τηλεπικοινωνιακής σύνδεσης.

## Αποτελέσματα Δοκιμών
- `backend/tests/enopoiisi/test_apostoles_kai_rover.py`:
  - `test_rover_safe_stop_preview_and_execute`: PASSED
  - `test_rover_comm_degraded_leads_to_uncertain_state`: PASSED
- Κάλυψη κώδικα `apostoles.py`: 89%.

## Σημειώσεις για το CHANGELOG
- Υλοποίηση συστήματος επιτήρησης rover: τηλεμετρία, αξιολόγηση ενεργειακής εφικτότητας και ασφάλειας επιστροφής, εντολή safe stop και αναβολή αποστολών σε επικίνδυνες καιρικές συνθήκες.
