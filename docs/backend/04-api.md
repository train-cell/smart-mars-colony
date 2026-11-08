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

### POST `/api/v1/ypostiriksi-zwis/thermokrasia/proepiskopisi`
Υπολογίζει τις επιπτώσεις αλλαγής επιθυμητής θερμοκρασίας θαλάμου (απαιτούμενη θερμική ισχύς, διαφορικό, νέες απώλειες).
```bash
curl -s -X POST http://localhost:8000/api/v1/ypostiriksi-zwis/thermokrasia/proepiskopisi \
  -H "Content-Type: application/json" \
  -H "X-ID-Xristi: xristis_01" \
  -H "X-Rolos: ypefthynos_ypostiriksis_zwis" \
  -d '{
    "id_thalamou": "thalamos_diamonis_01",
    "epithymiti_thermokrasia_k": 294.15
  }'
```
**Απόκριση (200 OK):**
```json
{
  "id_proepiskopisis": "proep_temp_...",
  "id_thalamou": "thalamos_diamonis_01",
  "trexousa_thermokrasia_k": 293.15,
  "epithymiti_thermokrasia_k": 294.15,
  "apaitoumeni_isxys_kw": 8.1,
  "diafora_isxyos_kw": 0.1,
  "oristiki_katastasi": "egkyro",
  "minyma": "Η προεπισκόπηση ρύθμισης θερμοκρασίας ολοκληρώθηκε επιτυχώς."
}
```

### POST `/api/v1/ypostiriksi-zwis/thermokrasia/epivevaiwsi`
Επιβεβαιώνει και εφαρμόζει την αλλαγή στόχου θερμοκρασίας με υποστήριξη Idempotency Key.
```bash
curl -s -X POST http://localhost:8000/api/v1/ypostiriksi-zwis/thermokrasia/epivevaiwsi \
  -H "Content-Type: application/json" \
  -H "X-ID-Xristi: xristis_01" \
  -H "X-Rolos: ypefthynos_ypostiriksis_zwis" \
  -H "Idempotency-Key: idem-temp-1001" \
  -d '{
    "id_proepiskopisis": "proep_temp_..."
  }'
```

---

## 3. Πόροι & Ενέργεια (Υποσύστημα Β)

### POST `/api/v1/poroi/ardefsi/proepiskopisi`
Ελέγχει τη διαθεσιμότητα νερού και υπολογίζει τις επιπτώσεις προγράμματος άρδευσης.
```bash
curl -s -X POST http://localhost:8000/api/v1/poroi/ardefsi/proepiskopisi \
  -H "Content-Type: application/json" \
  -H "X-ID-Xristi: xristis_02" \
  -H "X-Rolos: ypefthynos_porwn" \
  -d '{
    "id_zwnis": "zwni_thermokipiou_a",
    "posotita_nerou_l": 50.0,
    "diarkeia_lepta": 30
  }'
```
**Απόκριση (200 OK):**
```json
{
  "id_proepiskopisis": "proep_ard_...",
  "id_zwnis": "zwni_thermokipiou_a",
  "posotita_nerou_l": 50.0,
  "diathesimo_apothema_l": 5000.0,
  "ypoloipo_meta_ardefsi_l": 4950.0,
  "eparkeia": true,
  "minyma": "Επαρκές απόθεμα νερού για την εκτέλεση της άρδευσης."
}
```

### POST `/api/v1/poroi/ardefsi/epivevaiwsi`
Οριστικοποιεί το πότισμα, αφαιρεί το νερό από τη δεξαμενή και καταγράφει την εντολή.
```bash
curl -s -X POST http://localhost:8000/api/v1/poroi/ardefsi/epivevaiwsi \
  -H "Content-Type: application/json" \
  -H "X-ID-Xristi: xristis_02" \
  -H "X-Rolos: ypefthynos_porwn" \
  -H "Idempotency-Key: idem-ard-2002" \
  -d '{
    "id_proepiskopisis": "proep_ard_..."
  }'
```

### POST `/api/v1/poroi/fortia/periorismos`
Περιορίζει αναβλητά φορτία (π.χ. θέρμανση θερμοκηπίου) για εξοικονόμηση ισχύος.
```bash
curl -s -X POST http://localhost:8000/api/v1/poroi/fortia/periorismos \
  -H "Content-Type: application/json" \
  -H "X-ID-Xristi: xristis_02" \
  -H "X-Rolos: ypefthynos_porwn" \
  -d '{
    "id_fortiou": "fortio_thermansis_thermokipiou",
    "katastasi_leitourgias": "anastoli",
    "pososto_isxyos": 0.0
  }'
```

---

## 4. Αποστολές & Rover (Υποσύστημα Γ)

### POST `/api/v1/apostoles/rover/epistrofi/proepiskopisi`
Αξιολογεί την εφικτότητα και ασφάλεια επιστροφής του rover στη βάση.
```bash
curl -s -X POST http://localhost:8000/api/v1/apostoles/rover/epistrofi/proepiskopisi \
  -H "Content-Type: application/json" \
  -H "X-ID-Xristi: xristis_03" \
  -H "X-Rolos: xeiristis_oximatos" \
  -d '{
    "id_oximatos": "rover_erevnas_01",
    "taxytita_km_h": 4.0
  }'
```
**Απόκριση σε κανονικές συνθήκες:** `energeiaka_efikto: true`, `asfales: true`.
**Απόκριση σε καταιγίδα σκόνης:** `energeiaka_efikto: true`, `asfales: false` (λόγω ορατότητας < 300 m και υποβάθμισης επικοινωνίας).

### POST `/api/v1/apostoles/rover/asfalis-stathmefsi`
Εντολή άμεσης ασφαλούς στάθμευσης (Safe Stop) σε κατάσταση υψηλού κινδύνου.

---

## 5. Σενάρια & Προσομοίωση (Scenarios & Simulation)

### POST `/api/v1/senaria/kataigida-skonis/proepiskopisi`
Υπολογίζει τις συνδυασμένες επιπτώσεις καταιγίδας σκόνης (πτώση ηλιακής ισχύος, αύξηση θερμικών απωλειών, νέα αυτονομία μπαταριών).
```bash
curl -s -X POST http://localhost:8000/api/v1/senaria/kataigida-skonis/proepiskopisi \
  -H "Content-Type: application/json" \
  -H "X-ID-Xristi: xristis_04" \
  -H "X-Rolos: syntonistis_apoikias" \
  -d '{
    "optiko_vathos_tau": 2.5,
    "diarkeia_wres": 48.0,
    "anavoli_fortiwn": true
  }'
```

### POST `/api/v1/senaria/tick`
Προχωρά το εικονικό ρολόι της αποικίας κατά $N$ δευτερόλεπτα.
```bash
curl -s -X POST http://localhost:8000/api/v1/senaria/tick \
  -H "Content-Type: application/json" \
  -H "X-ID-Xristi: xristis_04" \
  -H "X-Rolos: syntonistis_apoikias" \
  -d '{"vimata_deyterolepta": 3600}'
```

### POST `/api/v1/senaria/epanapofora`
Επαναφέρει την αποικία στην αρχική κατάσταση βάσης δεδομένων (reset to initial state).
