# 04 - Τεκμηρίωση Διεπαφών API (Endpoints Reference)

Όλα τα endpoints έχουν πρόθεμα `/api/v1` και επιστρέφουν JSON. Η ταυτοποίηση γίνεται μέσω των HTTP headers `X-ID-Xristi` και `X-Rolos`.

---

## 1. Υγεία και Μεταδεδομένα (Health & Meta)

### GET `/health` & GET `/api/v1/ygeia`
Επιστρέφει την κατάσταση λειτουργίας του backend, έκδοση και πληροφορίες περιβάλλοντος.
```bash
curl -s http://localhost:8000/health
```
**Απόκριση (200 OK):**
```json
{
  "katastasi": "leitourgiko",
  "ekdosi": "0.1.0",
  "perivallon": "anaptyxi",
  "xronos": "2026-11-10T00:00:00Z"
}
```

---

## 2. Υποστήριξη Ζωής (ECLSS - Υποσύστημα Α)

### POST `/api/v1/xwroi-katoikisis/xwros_01/thermokrasia/proepiskopisi`
Υπολογίζει τις επιπτώσεις αλλαγής επιθυμητής θερμοκρασίας θαλάμου (απαιτούμενη θερμική ισχύς, διαφορικό, νέες απώλειες).
```bash
curl -s -X POST http://localhost:8000/api/v1/xwroi-katoikisis/xwros_01/thermokrasia/proepiskopisi \
  -H "Content-Type: application/json" \
  -H "X-ID-Xristi: xristis_01" \
  -H "X-Rolos: ypefthynos_ypostiriksis_zwis" \
  -d '{
    "epithymiti_thermokrasia_k": 294.15,
    "anamenomeni_ekdosi_katastasis": 1
  }'
```
**Απόκριση (200 OK):**
```json
{
  "id_proepiskopisis": "proep_therm_...",
  "id_xwrou": "xwros_01",
  "ekdosi_senariou": 1,
  "trexousa": {
    "thermokrasia_k": 293.0,
    "epithymiti_thermokrasia_k": 293.0
  },
  "zitoumeni": {
    "epithymiti_thermokrasia_k": 294.15
  },
  "epiptwsi": {
    "thermansi_prin_w": 8000.0,
    "thermansi_meta_w": 8115.0,
    "metavoli_w": 115.0
  },
  "apaiteitai_epivevaiwsi": true
}
```

### POST `/api/v1/xwroi-katoikisis/xwros_01/thermokrasia/entoles`
Επιβεβαιώνει και εφαρμόζει την αλλαγή στόχου θερμοκρασίας με υποστήριξη Idempotency Key.
```bash
curl -s -X POST http://localhost:8000/api/v1/xwroi-katoikisis/xwros_01/thermokrasia/entoles \
  -H "Content-Type: application/json" \
  -H "X-ID-Xristi: xristis_01" \
  -H "X-Rolos: ypefthynos_ypostiriksis_zwis" \
  -H "Idempotency-Key: idem-temp-1001" \
  -d '{
    "id_proepiskopisis": "proep_therm_...",
    "anamenomeni_ekdosi_katastasis": 1
  }'
```

---

## 3. Πόροι & Ενέργεια (Υποσύστημα Β)

### POST `/api/v1/thermokipia/thermokipio_01/ardefsi/proepiskopisi`
Ελέγχει τη διαθεσιμότητα νερού και υπολογίζει τις επιπτώσεις προγράμματος άρδευσης.
```bash
curl -s -X POST http://localhost:8000/api/v1/thermokipia/thermokipio_01/ardefsi/proepiskopisi \
  -H "Content-Type: application/json" \
  -H "X-ID-Xristi: xristis_02" \
  -H "X-Rolos: ypefthynos_porwn" \
  -d '{
    "id_zwnis": "zwni_01",
    "posotita_nerou_l": 50.0,
    "diarkeia_lepta": 30
  }'
```
**Απόκριση (200 OK):**
```json
{
  "id_proepiskopisis": "proep_ardefsi_...",
  "id_thermokipiou": "thermokipio_01",
  "id_zwnis": "zwni_01",
  "id_dexamenis": "dexameni_01",
  "posotita_nerou_l": 50.0,
  "stathmi_prin_l": 7500.0,
  "stathmi_meta_l": 7450.0,
  "ygrasia_prin": 0.55,
  "ygrasia_meta_ektimwmeni": 0.60,
  "eparkis_stathmi": true
}
```

### POST `/api/v1/thermokipia/thermokipio_01/ardefsi/programmata`
Οριστικοποιεί το πότισμα, δεσμεύει το νερό από τη δεξαμενή και καταγράφει το πρόγραμμα άρδευσης.
```bash
curl -s -X POST http://localhost:8000/api/v1/thermokipia/thermokipio_01/ardefsi/programmata \
  -H "Content-Type: application/json" \
  -H "X-ID-Xristi: xristis_02" \
  -H "X-Rolos: ypefthynos_porwn" \
  -H "Idempotency-Key: idem-ard-2002" \
  -d '{
    "id_proepiskopisis": "proep_ardefsi_..."
  }'
```

### POST `/api/v1/energeia/periorismos-fortiwn/proepiskopisi`
Υπολογίζει τις επιπτώσεις παύσης αναβλητών φορτίων (θέρμανση θερμοκηπίου) για εξοικονόμηση ισχύος κατά τη διάρκεια καταιγίδας.
```bash
curl -s -X POST http://localhost:8000/api/v1/energeia/periorismos-fortiwn/proepiskopisi \
  -H "Content-Type: application/json" \
  -H "X-ID-Xristi: xristis_02" \
  -H "X-Rolos: ypefthynos_porwn" \
  -d '{
    "pausi_anavlhtwn": true,
    "aitiologia": "Εξοικονόμηση ισχύος λόγω επικείμενης καταιγίδας"
  }'
```
**Απόκριση (200 OK):**
```json
{
  "pausi_anavlhtwn": true,
  "katastasi_prin": {
    "fortia_kw": 14.0,
    "elleimma_kw": 9.2,
    "autonomia_wres": 3.261
  },
  "katastasi_meta": {
    "fortia_kw": 10.0,
    "elleimma_kw": 5.2,
    "autonomia_wres": 5.769
  },
  "ofelos": {
    "meiwsi_isxyos_kw": 4.0,
    "kerdos_autonomias_wres": 2.508,
    "kerdos_autonomias_lepta": 150.5
  },
  "apaiteitai_egkrisi_syntonisti": true
}
```

### POST `/api/v1/energeia/periorismos-fortiwn/entoles`
Εκτελεί τον περιορισμό/αναστολή φορτίων με έγκριση συντονιστή και καταγραφή στο audit log.
```bash
curl -s -X POST http://localhost:8000/api/v1/energeia/periorismos-fortiwn/entoles \
  -H "Content-Type: application/json" \
  -H "X-ID-Xristi: syntonistis" \
  -H "X-Rolos: syntonistis_apoikias" \
  -H "Idempotency-Key: idem-per-01" \
  -d '{
    "pausi_anavlhtwn": true,
    "aitiologia": "Εξοικονόμηση ισχύος λόγω επικείμενης καταιγίδας"
  }'
```

---

## 4. Αποστολές & Rover (Υποσύστημα Γ)

### POST `/api/v1/oximata/rover_01/anaklisi/proepiskopisi`
Αξιολογεί την πολυδιάστατη εφικτότητα και ασφάλεια επιστροφής του rover στη βάση (ενέργεια, ορατότητα, επικοινωνία).
```bash
curl -s -X POST http://localhost:8000/api/v1/oximata/rover_01/anaklisi/proepiskopisi \
  -H "X-ID-Xristi: xristis_03" \
  -H "X-Rolos: xeiristis_oximatos"
```
**Απόκριση σε κανονικές συνθήκες (200 OK):**
```json
{
  "apostasi_km": 2.0,
  "taxytita_kmh": 4.0,
  "xronos_epistrofis_wres": 0.5,
  "xronos_epistrofis_lepta": 30.0,
  "apaitoumeni_energeia_kwh": 0.3,
  "energeia_meta_epistrofi_kwh": 0.5,
  "energeiaka_efikto": true,
  "oratotita_asfalis": true,
  "epikoinwnia_asfalis": true,
  "synolika_asfalis_epistrofi": true,
  "proeidopoiiseis": [],
  "id_oximatos": "rover_01",
  "onoma_oximatos": "Εξερευνητικό Όχημα Αίολος (Rover-1)",
  "ekdosi_katastasis": 1
}
```
*Σημείωση:* Σε συνθήκες καταιγίδας σκόνης, η ορατότητα πέφτει στα 100 m (< 300 m όριο ασφαλείας) και το `synolika_asfalis_epistrofi` γίνεται `false`.

### POST `/api/v1/oximata/rover_01/asfalis-stasi/entoles`
Εντολή άμεσης ασφαλούς στάσης (Safe Stop) σε κατάσταση υψηλού κινδύνου.
```bash
curl -s -X POST http://localhost:8000/api/v1/oximata/rover_01/asfalis-stasi/entoles \
  -H "Content-Type: application/json" \
  -H "X-ID-Xristi: syntonistis" \
  -H "X-Rolos: syntonistis_apoikias" \
  -H "Idempotency-Key: idem-safe-01" \
  -d '{
    "anamenomeni_ekdosi_katastasis": 1,
    "aitiologia": "Ορατότητα κάτω των 300m λόγω αμμοθύελλας"
  }'
```
**Απόκριση (200 OK):**
```json
{
  "id_entolis": "entoli_stasis_...",
  "id_oximatos": "rover_01",
  "katastasi_oximatos": "asfalis_stasi",
  "minyma": "Το όχημα τέθηκε επιτυχώς σε κατάσταση ασφαλούς στάσης."
}
```

---

## 5. Σενάρια & Προσομοίωση (Scenarios & Simulation)

### POST `/api/v1/senaria/kataigida-skonis/proepiskopisi`
Υπολογίζει συγκριτικά όλες τις επιλογές καταιγίδας βάσει των στατιστικών του Golden Fixture (§6).
```bash
curl -s -X POST http://localhost:8000/api/v1/senaria/kataigida-skonis/proepiskopisi \
  -H "X-ID-Xristi: xristis_04" \
  -H "X-Rolos: syntonistis_apoikias"
```
**Απόκριση (200 OK):**
```json
{
  "senario": "kataigida_skonis_2026",
  "statistika_golden_fixture": {
    "pv_kanoniko_kw": 4.8,
    "pv_kataigida_kw": 0.8,
    "thermansi_kanoniki_kw": 8.0,
    "thermansi_kataigida_kw": 10.0,
    "autonomia_kanoniki_wres": 3.261,
    "autonomia_xwris_pausi_wres": 1.974,
    "autonomia_me_pausi_wres": 2.679,
    "kerdos_autonomias_lepta": 42.29
  },
  "epiloges_apofasis": {
    "kamia_allagi": {
      "autonomia_wres": 1.974,
      "kindynos": "ypsilos"
    },
    "pausi_anavlhtwn": {
      "autonomia_wres": 2.679,
      "kerdos_lepta": 42.29,
      "kindynos": "metrios"
    }
  },
  "apaiteitai_egkrisi_syntonisti": true
}
```

### POST `/api/v1/prosomoiwsi/vima`
Προχωρά το εικονικό ρολόι της αποικίας κατά καθορισμένο αριθμό λεπτών (CORE-13).
```bash
curl -s -X POST http://localhost:8000/api/v1/prosomoiwsi/vima \
  -H "Content-Type: application/json" \
  -H "X-ID-Xristi: xristis_04" \
  -H "X-Rolos: syntonistis_apoikias" \
  -d '{"lepta": 15}'
```
**Απόκριση (200 OK):**
```json
{
  "simerino_vima": 1,
  "neos_xronos": "2026-11-10T12:15:00",
  "lepta_pou_prostethikan": 15
}
```

### POST `/api/v1/prosomoiwsi/epanafora`
Επαναφέρει την προσομοίωση και τις παραμέτρους στις κανονικές συνθήκες baseline.
```bash
curl -s -X POST http://localhost:8000/api/v1/prosomoiwsi/epanafora \
  -H "X-ID-Xristi: syntonistis" \
  -H "X-Rolos: syntonistis_apoikias"
```
