# Ροές Επίδειξης και Σεναρίων (Demonstration Flows)

Το έγγραφο αυτό καθοδηγεί τον χειριστή ή το frontend στην εκτέλεση δύο θεμελιωδών ροών επίδειξης: τη ρύθμιση θερμοκρασίας και τον προγραμματισμό άρδευσης.

---

## 1. Ροή Επίδειξης 1: Ρύθμιση Θερμοκρασίας Θαλάμου

### Στόχος
Ο Υπεύθυνος Υποστήριξης Ζωής επιθυμεί να αυξήσει τη θερμοκρασία του θαλάμου διαμονής κατά 1 Kelvin (από 293.15 K σε 294.15 K) και να επιθεωρήσει τη μεταβολή της απαιτούμενης ισχύος πριν από την οριστική εφαρμογή.

### Βήμα 1: Αίτημα Προεπισκόπησης
```bash
curl -X POST http://localhost:8000/api/v1/ypostiriksi-zwis/thermokrasia/proepiskopisi \
  -H "Content-Type: application/json" \
  -H "X-ID-Xristi: xristis_01" \
  -H "X-Rolos: ypefthynos_ypostiriksis_zwis" \
  -d '{
    "id_thalamou": "thalamos_diamonis_01",
    "epithymiti_thermokrasia_k": 294.15
  }'
```
**Απάντηση Backend:**
- Επιστρέφεται `id_proepiskopisis` (π.χ. `proep_temp_ab12cd34`).
- Απαιτούμενη ισχύς: $8.1 \, kW$ (διαφορά $+0.1 \, kW$).
- Κατάσταση: `egkyro`.

### Βήμα 2: Προβολή στο UI
Ο χρήστης βλέπει την πρόβλεψη στην οθόνη: *"Η νέα ρύθμιση θα αυξήσει την κατανάλωση κατά 0.1 kW. Επιθυμείτε εφαρμογή;"*.

### Βήμα 3: Επιβεβαίωση Εντολής
```bash
curl -X POST http://localhost:8000/api/v1/ypostiriksi-zwis/thermokrasia/epivevaiwsi \
  -H "Content-Type: application/json" \
  -H "X-ID-Xristi: xristis_01" \
  -H "X-Rolos: ypefthynos_ypostiriksis_zwis" \
  -H "Idempotency-Key: idem-temp-step-3" \
  -d '{
    "id_proepiskopisis": "proep_temp_ab12cd34"
  }'
```
**Αποτέλεσμα:** Ο στόχος ενημερώνεται, καταχωρείται εγγραφή στο audit log, και η νέα θερμοκρασία είναι ενεργή.

---

## 2. Ροή Επίδειξης 2: Άρδευση Θερμοκηπίου

### Στόχος
Ο Υπεύθυνος Πόρων επιθυμεί να ποτίσει τη Ζώνη Α Θερμοκηπίου με 50 λίτρα νερού.

### Βήμα 1: Αίτημα Προεπισκόπησης
```bash
curl -X POST http://localhost:8000/api/v1/poroi/ardefsi/proepiskopisi \
  -H "Content-Type: application/json" \
  -H "X-ID-Xristi: xristis_02" \
  -H "X-Rolos: ypefthynos_porwn" \
  -d '{
    "id_zwnis": "zwni_thermokipiou_a",
    "posotita_nerou_l": 50.0,
    "diarkeia_lepta": 30
  }'
```
**Απάντηση Backend:**
- Επιστρέφεται `id_proepiskopisis` (π.χ. `proep_ard_ef56gh78`).
- Διαθέσιμο απόθεμα: $5.000,0 \, L$.
- Υπόλοιπο μετά την άρδευση: $4.950,0 \, L$.
- Επάρκεια: `true`.

### Βήμα 2: Επιβεβαίωση Εντολής
```bash
curl -X POST http://localhost:8000/api/v1/poroi/ardefsi/epivevaiwsi \
  -H "Content-Type: application/json" \
  -H "X-ID-Xristi: xristis_02" \
  -H "X-Rolos: ypefthynos_porwn" \
  -H "Idempotency-Key: idem-ard-step-2" \
  -d '{
    "id_proepiskopisis": "proep_ard_ef56gh78"
  }'
```
**Αποτέλεσμα:** Το απόθεμα νερού της δεξαμενής μειώνεται στα 4.950 L, δημιουργείται εγγραφή στο πρόγραμμα άρδευσης με κατάσταση `oloklirothike`, και η ενέργεια καταγράφεται στο audit log.

### Βήμα 3: Δοκιμή Σφάλματος Ανεπάρκειας Νερού (Fault Injection)
Εάν σταλεί αίτημα άρδευσης με $10.000 \, L$ (ενώ το απόθεμα είναι 5.000 L):
```bash
curl -X POST http://localhost:8000/api/v1/poroi/ardefsi/proepiskopisi \
  -H "Content-Type: application/json" \
  -H "X-ID-Xristi: xristis_02" \
  -H "X-Rolos: ypefthynos_porwn" \
  -d '{
    "id_zwnis": "zwni_thermokipiou_a",
    "posotita_nerou_l": 10000.0,
    "diarkeia_lepta": 60
  }'
```
**Απόκριση (400 Bad Request):**
```json
{
  "sfalma": {
    "kodikos": "aneparki_apothema_nerou",
    "minyma": "Το διαθέσιμο νερό (5000.0 L) δεν επαρκεί για την αιτούμενη ποσότητα (10000.0 L).",
    "leptomereies": {
      "diathesimo_apothema_l": 5000.0,
      "aitoumeni_posotita_l": 10000.0
    },
    "epanalipsimo": false
  }
}
```
