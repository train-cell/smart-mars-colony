# 12 - Πίνακας Ιχνηλασιμότητας (Traceability Matrix)

Ο παρακάτω πίνακας αποτυπώνει την πλήρη αντιστοίχιση των λειτουργικών και φυσικών απαιτήσεων με τα αρχεία υλοποίησης, τα endpoints του API και τις αντίστοιχες αυτοματοποιημένες δοκιμές.

| Κωδικός Απαίτησης | Περιγραφή | Αρχεία Υλοποίησης | Endpoints API | Αυτοματοποιημένη Δοκιμή |
| :--- | :--- | :--- | :--- | :--- |
| **PHY-01** | Θερμικές Απώλειες Κελύφους | `fysika_montela.py` | `POST /ypostiriksi-zwis/thermokrasia/proepiskopisi` | `test_fysika_montela.py::test_golden_thermikes_apwleies_kanonikes_kai_kataigida` |
| **PHY-02** | Φωτοβολταϊκή Παραγωγή | `fysika_montela.py` | `POST /senaria/kataigida-skonis/proepiskopisi` | `test_fysika_montela.py::test_golden_fwtovoltaika_kanonika_kai_kataigida` |
| **PHY-03** | Ηλεκτρικό Ισοζύγιο & Αυτονομία | `fysika_montela.py` | `GET /poroi/ilektriki-energeia/isozigio` | `test_fysika_montela.py::test_golden_ilektriko_isozygio_kai_autonomia_pliris_alysida` |
| **PHY-04** | Ισοζύγιο Οξυγόνου & Ατμόσφαιρας | `fysika_montela.py` | `GET /ypostiriksi-zwis/atmosfaira` | `test_fysika_montela.py::test_oxygono_ypologismoi_kai_autonomia` |
| **PHY-05** | Ισοζύγιο Υδατικών Πόρων | `fysika_montela.py` | `POST /poroi/ardefsi/proepiskopisi` | `test_fysika_montela.py::test_isozygio_nerou_apothiki_kai_aneparkeia` |
| **PHY-06** | Κινηματική & Ενέργεια Rover | `fysika_montela.py` | `POST /apostoles/rover/epistrofi/proepiskopisi` | `test_epipleon_kalipsi.py::test_phy06_energeia_kinisis_oximatos` |
| **PHY-07** | Εκτίμηση Κινδύνου Επιστροφής | `fysika_montela.py` | `POST /apostoles/rover/epistrofi/proepiskopisi` | `test_fysika_montela.py::test_golden_rover_epistrofi_kai_asfaleia` |
| **CORE-01…06** | Σχήματα, Φάκελος Σφαλμάτων, Μονάδες | `sfalmata.py`, `monades.py`, `koina.py` | Όλα τα endpoints | `test_monades.py`, `test_sxhmata.py` |
| **CORE-07…08** | Έλεγχος Πρόσβασης (RBAC) | `asfaleia.py` | Όλα τα προστατευμένα endpoints | `test_asfaleia_kai_dikaiwmata.py::test_rbac_forbidden_and_coordinator_approval` |
| **CORE-09…10** | Μοτίβο 2 Βημάτων (Preview / Confirm) | `ypostiriksi_zwis.py`, `poroi.py` | `POST .../proepiskopisi`, `POST .../epivevaiwsi` | `test_ypostiriksi_zwis.py`, `test_poroi_kai_ardefsi.py` |
| **CORE-11…12** | Αποτροπή Διπλής Εκτέλεσης (Idempotency) | `asfaleia.py`, `apothiki_koinwn.py` | `POST .../epivevaiwsi` | `test_asfaleia_kai_dikaiwmata.py::test_idempotency_key_prevents_duplicate_execution` |
| **CORE-13…14** | Αρχείο Καταγραφής Ελέγχου (Audit Log) | `ypiresia_symvantwn_kai_senariwn.py` | `GET /istoriko/audit-log` | `test_epipleon_kalipsi.py::test_entoles_lifecycle_kai_audit_log` |
| **CORE-15…16** | Εικονικό Ρολόι & Επαναφορά | `senaria.py` | `POST /senaria/tick`, `POST /senaria/epanapofora` | `test_symvolaia_kai_openapi.py::test_simulation_clock_and_reset` |
| **CORE-17…18** | Συναγερμοί (Αναγνώριση & Επίλυση) | `synagermoi.py` | `POST /synagermoi/{id}/anagnwrisi`, `POST /synagermoi/{id}/epilysi` | `test_synagermoi.py::test_alert_acknowledge_vs_resolve` |
| **CORE-19…20** | Μεταβίβαση Δικαιωμάτων (Delegation) | `dikaiwmata.py`, `asfaleia.py` | `POST /dikaiwmata/metavivasi`, `POST /dikaiwmata/anaklisi` | `test_asfaleia_kai_dikaiwmata.py::test_delegation_grant_and_revoke` |
| **LIFE-01…06** | Θερμοκρασία Θαλάμων | `ypostiriksi_zwis.py` | `/ypostiriksi-zwis/thermokrasia/*` | `test_ypostiriksi_zwis.py` |
| **RES-01…08** | Νερό, Δεξαμενές, Άρδευση | `poroi.py` | `/poroi/ardefsi/*`, `/poroi/dexamenes` | `test_poroi_kai_ardefsi.py` |
| **RES-09…10** | Περιορισμός Αναβλητών Φορτίων | `poroi.py` | `POST /poroi/fortia/periorismos` | `test_kataigida_skonis.py` |
| **MISSION-01…08** | Rover, Αποστολές, Safe Stop | `apostoles.py` | `/apostoles/rover/*` | `test_apostoles_kai_rover.py` |
| **STORM-01…08** | Χρυσό Σενάριο Καταιγίδας Σκόνης | `senaria.py` | `/senaria/kataigida-skonis/*` | `test_kataigida_skonis.py::test_storm_scenario_full_end_to_end_chain` |
| **TEST-01…21** | Greeklish & Συμβόλαια OpenAPI | `main.py` | `/openapi.json`, `/health` | `test_symvolaia_kai_openapi.py` |
