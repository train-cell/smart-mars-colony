# Συμβόλαιο Επικοινωνίας Frontend - Backend

Το παρόν έγγραφο ορίζει το επίσημο τεχνικό συμβόλαιο διεπαφής μεταξύ του Frontend Dashboard και του Backend API του **Smart Mars Colony**. Έχει γραφτεί αναλυτικά με διαγράμματα και επεξηγήσεις ώστε να καθοδηγήσει πλήρως τη συνάδελφο του Frontend στην υλοποίηση του UI.

---

## 1. Βασικές Αρχές Διεπαφής & Αρχιτεκτονική Επικοινωνίας

```mermaid
flowchart LR
    subgraph Frontend["Frontend Dashboard (UI)"]
        UI_Widgets["Οθόνες & Widgets"]
        UI_Modals["Διάλογοι Επιβεβαίωσης"]
        UI_Store["Client State (Zustand/Redux)"]
    end

    subgraph HTTP["HTTP / REST Interface (Greeklish)"]
        Headers["Headers: X-ID-Xristi, X-Rolos, Idempotency-Key"]
        Endpoints["Base URL: /api/v1/..."]
    end

    subgraph Backend["Smart Mars Colony Backend"]
        FastAPI["FastAPI Routing & Auth Guard"]
        Services["Domain Services (ECLSS, Poroi, Rover)"]
        Physics["Αμιγή Φυσικά Μοντέλα (PHY-01..07)"]
        DB[("SQLite 3 Database")]
    end

    UI_Widgets -->|1. GET /synopsi, /aisthitires| Endpoints
    UI_Modals -->|2. POST /proepiskopisi| Endpoints
    UI_Modals -->|3. POST /epivevaiwsi + Idempotency-Key| Endpoints
    Endpoints --> Headers
    Headers --> FastAPI
    FastAPI --> Services
    Services --> Physics
    Services --> DB
```

- **Πρωτόκολλο:** HTTP/1.1 μέσω REST & JSON.
- **Κοινή Ρίζα Endpoints:** `/api/v1`
- **Κανόνας Greeklish (§0A):** Όλα τα JSON κλειδιά, παράμετροι διαδρομών (path parameters) και τιμές enums ακολουθούν αυστηρά λατινική μεταγραφή ελληνικών λέξεων (ASCII).
- **Μονάδες Μέτρησης:**
  - Θερμοκρασία: Kelvin ($K$) ως εσωτερική τιμή, με υποστήριξη βαθμών Κελσίου ($^\circ C$) στις αποκρίσεις.
  - Ενέργεια / Ισχύς: $kW$ για ισχύ, $kWh$ για αποθηκευμένη ενέργεια.
  - Όγκος: Λίτρα ($L$) ή κυβικά μέτρα ($m^3$).
  - Πίεση: Pascals ($Pa$) ή $kPa$.

---

## 2. Επικεφαλίδες Αιτημάτων (Request Headers)

| Επικεφαλίδα | Υποχρεωτική | Περιγραφή | Παράδειγμα |
| :--- | :---: | :--- | :--- |
| `Content-Type` | Ναι (στα POST) | Μορφή σώματος αιτήματος | `application/json` |
| `X-ID-Xristi` | Ναι (στα προστατευμένα) | Αναγνωριστικό συνδεδεμένου χρήστη | `xristis_01` |
| `X-Rolos` | Ναι (στα προστατευμένα) | Ενεργός ρόλος για το αίτημα | `ypefthynos_ypostiriksis_zwis` |
| `Idempotency-Key` | Προαιρετική (Συνιστάται στα Confirm) | Μοναδικό UUID κλειδί αποτροπής διπλής εκτέλεσης | `c2a688b1-36f1-4db8-bcae-ec15e0e01234` |

---

## 3. Κύκλος Ζωής Εντολών Δύο Βημάτων (Preview / Confirm / Cancel Pattern)

Για λόγους ασφάλειας στον Άρη, καμία κρίσιμη ενέργεια (αλλαγή θερμοκρασίας, άρδευση, διακοπή φορτίου, κίνηση rover) δεν εκτελείται άμεσα με ένα κλικ. Αντίθετα, ακολουθείται η παρακάτω ροή:

```mermaid
sequenceDiagram
    autonumber
    actor User as Χειριστής (UI)
    participant UI as Frontend Dashboard
    participant API as Backend API (/api/v1)
    participant Phys as Φυσικό Μοντέλο & Βάση

    User->>UI: Εισαγωγή επιθυμητής τιμής (π.χ. T = 294.15 K)
    UI->>API: POST /.../proepiskopisi (AitimaProepiskopisis)
    API->>Phys: Υπολογισμός επιπτώσεων (ισχύς, υπόλοιπο, ρίσκο)
    Phys-->>API: Προβλεπόμενες τιμές
    API-->>UI: 200 OK (id_proepiskopisis, epiptwsi, proeidopoiiseis)
    UI->>User: Εμφάνιση Modal Επιβεβαίωσης με τις επιπτώσεις
    
    alt Ο Χρήστης Πατάει "Επιβεβαίωση"
        User->>UI: Κλικ "Επιβεβαίωση"
        UI->>API: POST /.../entoles (id_proepiskopisis) + Idempotency-Key
        API->>Phys: Εφαρμογή εντολής & καταγραφή audit log
        Phys-->>API: Οριστική ενημέρωση
        API-->>UI: 200 OK (Κατάσταση: oloklirothike / se_exelixi)
        UI->>User: Toast ειδοποίηση επιτυχίας & ανανέωση dashboard
    else Ο Χρήστης Πατάει "Ακύρωση"
        User->>UI: Κλικ "Ακύρωση"
        UI->>API: POST /.../akyrosi (ή απλή απόρριψη modal)
        API-->>UI: 200 OK (Ακυρώθηκε χωρίς καμία επίπτωση)
        UI->>User: Επιστροφή στην προηγούμενη κατάσταση
    end
```

---

## 4. Μηχανή Καταστάσεων Εντολών (Command State Machine)

```mermaid
stateDiagram-v2
    [*] --> protathike: Δημιουργία πρότασης
    protathike --> proepiskopithike: Κλήση POST /proepiskopisi
    proepiskopithike --> epivevaiwthike: Κλήση POST /entoles (Confirm)
    proepiskopithike --> akyrothike: Κλικ Ακύρωση / Timeout
    epivevaiwthike --> se_exelixi: Ανάληψη από υποσύστημα
    se_exelixi --> oloklirothike: Επιτυχής εκτέλεση
    se_exelixi --> apetyxe: Αποτυχία υλικού/ορίου
    se_exelixi --> avevaio: Απώλεια τηλεμετρίας / comm loss
    avevaio --> oloklirothike: Επανασύνδεση & επιβεβαίωση
    avevaio --> apetyxe: Χρονικό όριο αναμονής (Timeout)
    oloklirothike --> [*]
    apetyxe --> [*]
    akyrothike --> [*]
```

---

## 5. Τυποποιημένη Δομή Απόκρισης Μέτρησης Αισθητήρα

Όλες οι αποκρίσεις που αφορούν τιμές αισθητήρων ακολουθούν ενιαία δομή:

```json
{
  "megethos": "thermokrasia_thalamou",
  "timi": 293.15,
  "monada": "K",
  "eidos": "metrimeno",
  "pigi": "aisthitiras_th_01",
  "xronos_metrisis": "2026-11-10T00:00:00Z",
  "poiotita": "egkyro",
  "avevaiotita": {
    "apolyti_timi": 0.5,
    "monada": "K",
    "pososto": 0.17
  },
  "tasi": "statheri",
  "einai_palio": false
}
```

### Επεξήγηση Πεδίων για το Frontend
- `megethos`: Το αναγνωριστικό του μεγέθους σε Greeklish (π.χ. `thermokrasia_eswteriki`, `piesi_pa`, `pososto_oxygonou`).
- `timi`: Η αριθμητική τιμή της μέτρησης.
- `monada`: Η μονάδα μέτρησης (`K`, `Pa`, `kg`, `kW`, `kWh`, `L`, `pososto`).
- `eidos`: `metrimeno` (πραγματική μέτρηση), `ektimimeno` (εκτίμηση μέσω μοντέλου), `provlepsi` (μελλοντική πρόβλεψη), `setpoint` (επιθυμητός στόχος ρύθμισης).
- `poiotita`: `egkyro` (πράσινο badge στο UI), `ypovathmismeno` (κίτρινο badge), `palio` (πορτοκαλί ένδειξη stale data), `apousia` (κόκκινη ένδειξη offline αισθητήρα).
- `avevaiotita`: Προαιρετικό αντικείμενο στατιστικής αβεβαιότητας ($\pm \Delta$).
- `tasi`: `afksousa` ($\uparrow$), `fthinousa` ($\downarrow$), `statheri` ($\rightarrow$), `agnwsti`.

---

## 6. Τυποποιημένος Φάκελος Σφάλματος (Unified Error Envelope)

Όλες οι αποκρίσεις αποτυχίας (HTTP 400, 403, 404, 409, 422, 500) επιστρέφουν JSON με ρίζα `sfalma`:

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

### Πίνακας Κωδικών Σφαλμάτων Domain

| Κωδικός (`kodikos`) | HTTP Status | Σημασία & Οδηγία για το UI |
| :--- | :---: | :--- |
| `ANEPARKES_NERO` | 400 | Το αιτούμενο νερό υπερβαίνει το διαθέσιμο. Εμφάνιση κόκκινου banner στο modal άρδευσης. |
| `EKTOS_ORIWN` | 400 | Η αιτούμενη τιμή (π.χ. θερμοκρασία) είναι εκτός επιτρεπτών ορίων. |
| `ANARMODIOS_ROLOS` | 403 | Ο χρήστης δεν έχει δικαίωμα για την ενέργεια. Εμφάνιση απαγορευτικού μηνύματος ή πρόταση μεταβίβασης ρόλου. |
| `DEN_VRETHIKE` | 404 | Ο πόρος (θάλαμος, όχημα, δεξαμενή) δεν βρέθηκε. |
| `STALE_PREVIEW` / `DIENEXI` | 409 | Η προεπισκόπηση έληξε ή άλλαξαν τα δεδομένα ενδιάμεσα. Απαιτείται ανανέωση προεπισκόπησης. |
| `AKYRI_TIMI` | 422 | Σφάλμα validation πεδίων εισόδου από το Pydantic. |
| `ESWTERIKO_SFALMA` | 500 | Απρόβλεπτο σφάλμα εξυπηρετητή. Εμφάνιση γενικού μηνύματος αποτυχίας. |
