# Ροές Επίδειξης και Σεναρίων (Demonstration Flows)

Το έγγραφο αυτό καθοδηγεί τον χειριστή ή το frontend στην εκτέλεση δύο θεμελιωδών ροών επίδειξης: τη ρύθμιση θερμοκρασίας και τον προγραμματισμό άρδευσης.

---

## 1. Ροή Επίδειξης 1: Ρύθμιση Θερμοκρασίας Θαλάμου

### Στόχος
Ο Υπεύθυνος Υποστήριξης Ζωής επιθυμεί να αυξήσει τη θερμοκρασία του θαλάμου διαμονής κατά 1 Kelvin (από 293.15 K σε 294.15 K) και να επιθεωρήσει τη μεταβολή της απαιτούμενης ισχύος πριν από την οριστική εφαρμογή.

### Βήμα 1: Αίτημα Προεπισκόπησης
```bash
curl -X POST http://localhost:8000/api/v1/xwroi-katoikisis/xwros_01/thermokrasia/proepiskopisi \
  -H "Content-Type: application/json" \
  -H "X-ID-Xristi: xristis_01" \
  -H "X-Rolos: ypefthynos_ypostiriksis_zwis" \
  -d '{
    "epithymiti_thermokrasia_k": 294.15,
    "anamenomeni_ekdosi_katastasis": 1
  }'
```
**Απάντηση Backend:**
- Επιστρέφεται `id_proepiskopisis` (π.χ. `proep_therm_0bb9898a`).
- `thermansi_prin_w`: $8000.0 \, W$.
- `thermansi_meta_w`: $8115.0 \, W$ (μεταβολή $+115.0 \, W$).
- `apaiteitai_epivevaiwsi`: `true`.

### Βήμα 2: Προβολή στο UI
Ο χρήστης βλέπει την πρόβλεψη στην οθόνη: *"Η νέα ρύθμιση θα αυξήσει την κατανάλωση θέρμανσης κατά 115 W. Επιθυμείτε εφαρμογή;"*.

### Βήμα 3: Επιβεβαίωση Εντολής
```bash
curl -X POST http://localhost:8000/api/v1/xwroi-katoikisis/xwros_01/thermokrasia/entoles \
  -H "Content-Type: application/json" \
  -H "X-ID-Xristi: xristis_01" \
  -H "X-Rolos: ypefthynos_ypostiriksis_zwis" \
  -H "Idempotency-Key: idem-temp-step-3" \
  -d '{
    "id_proepiskopisis": "proep_therm_0bb9898a",
    "anamenomeni_ekdosi_katastasis": 1
  }'
```
**Αποτέλεσμα:** Ο στόχος ενημερώνεται, καταχωρείται εγγραφή στο audit log, και η νέα θερμοκρασία είναι ενεργή.

---

## 2. Ροή Επίδειξης 2: Άρδευση Θερμοκηπίου

### Στόχος
Ο Υπεύθυνος Πόρων επιθυμεί να ποτίσει τη Ζώνη Α Θερμοκηπίου με 50 λίτρα νερού.

### Βήμα 1: Αίτημα Προεπισκόπησης
```bash
curl -X POST http://localhost:8000/api/v1/thermokipia/thermokipio_01/ardefsi/proepiskopisi \
  -H "Content-Type: application/json" \
  -H "X-ID-Xristi: xristis_02" \
  -H "X-Rolos: ypefthynos_porwn" \
  -d '{
    "id_zwnis": "zwni_01",
    "posotita_nerou_l": 50.0,
    "diarkeia_lepta": 30
  }'
```
**Απάντηση Backend:**
- Επιστρέφεται `id_proepiskopisis` (π.χ. `proep_ardefsi_61e6164e`).
- `stathmi_prin_l`: $7500.0 \, L$.
- `stathmi_meta_l`: $7450.0 \, L$.
- `eparkis_stathmi`: `true`.

### Βήμα 2: Επιβεβαίωση Εντολής
```bash
curl -X POST http://localhost:8000/api/v1/thermokipia/thermokipio_01/ardefsi/programmata \
  -H "Content-Type: application/json" \
  -H "X-ID-Xristi: xristis_02" \
  -H "X-Rolos: ypefthynos_porwn" \
  -H "Idempotency-Key: idem-ard-step-2" \
  -d '{
    "id_proepiskopisis": "proep_ardefsi_61e6164e"
  }'
```
**Αποτέλεσμα:** Το απόθεμα νερού της δεξαμενής μειώνεται στα 7.450 L, δημιουργείται εγγραφή στο πρόγραμμα άρδευσης με κατάσταση `programmatismeno`, και η ενέργεια καταγράφεται στο audit log.

### Βήμα 3: Δοκιμή Σφάλματος Ανεπάρκειας Νερού (Fault Injection)
Εάν σταλεί αίτημα άρδευσης με $10.000 \, L$ (ενώ το διαθέσιμο νερό πάνω από την εφεδρεία είναι 6.000 L):
```bash
curl -X POST http://localhost:8000/api/v1/thermokipia/thermokipio_01/ardefsi/proepiskopisi \
  -H "Content-Type: application/json" \
  -H "X-ID-Xristi: xristis_02" \
  -H "X-Rolos: ypefthynos_porwn" \
  -d '{
    "id_zwnis": "zwni_01",
    "posotita_nerou_l": 10000.0,
    "diarkeia_lepta": 60
  }'
```
**Απόκριση (400 Bad Request):**
```json
{
  "sfalma": {
    "kodikos": "ANEPARKES_NERO",
    "minyma": "Το διαθέσιμο νερό πάνω από την εφεδρεία δεν επαρκεί για την άρδευση.",
    "leptomereies": {
      "diathesimo_l": 6000.0,
      "zitoumeno_l": 10000.0,
      "efedreia_asfaleias_l": 1500.0
    },
    "id_aitimatos": null,
    "epanalipsimo": false
  }
}
```
