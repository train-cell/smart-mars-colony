"""Εξαντλητικές δοκιμές για όλα τα Edge Cases και ακραίες αρειανές συνθήκες προσομοίωσης.

Καλύπτει:
1. Μηδενική ακτινοβολία (νύχτα στον Άρη: G = 0 W/m²).
2. Εξάντληση μπαταριών (0 kWh, έλλειμμα χωρίς αποθήκευση).
3. Κρίσιμη πτώση οξυγόνου κάτω από το όριο πίεσης (O2 starvation).
4. Πλήρης εξάντληση νερού στη δεξαμενή και απόρριψη νέας εντολής άρδευσης (RES-05, RES-06).
5. Αισθητήρας offline / stale / μηδενική ποιότητα (τηλεμετρία και απορρίψεις).
6. Πλήρης απώλεια επικοινωνίας rover (comm loss -> avevaio state, αδυναμία επιβεβαίωσης).
7. Ταυτόχρονες συγκρουόμενες εντολές άρδευσης ή ενέργειας (optimistic lock conflict 409).
8. Διπλή αποστολή με το ίδιο Idempotency-Key (idempotent replay χωρίς διπλή αφαίρεση πόρων).
9. Ακραίες αρειανές θερμοκρασίες (T_exw = 140 K, T_esw = 310 K και έλεγχοι ορίων).
10. Ακύρωση προγραμμάτων άρδευσης, φωτισμού και ανακύκλωσης σε επιτρεπτή και μη-επιτρεπτή φάση.
"""

import uuid
from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.app.fysika_montela.fysika_montela import (
    ypologise_apaitisi_thermansis,
    ypologise_apothema_kai_autonomia_oxygonou,
    ypologise_ilektriko_isozygio_kai_autonomia,
    ypologise_isxy_fwtovoltaikou,
    ypologise_thermikes_apwleies,
)
from backend.app.montela.apostoles import OximaExerevnis
from backend.app.montela.poroi import DexameniNerou, ProgrammaFwtismou
from backend.app.montela.ypostiriksi_zwis import Aisthitiras, MetrisiAisthitira, XwrosKatoikisis
from backend.app.pyrinas.asfaleia import XRHSTES_DEMO
from backend.app.pyrinas.sfalmata import KodikosSfalmatos, SfalmaDomain
from backend.app.ypiresies.ypiresia_porwn import (
    PROEPISKOPISEIS_ARDEFSIS,
    YpiresiaPorwn,
)
from backend.app.ypiresies.ypiresia_symvantwn_kai_senariwn import (
    YpiresiaSymvantwnKaiSenariwn,
)

# ============================================================================
# EDGE-CASE 1: Μηδενική ακτινοβολία (Νύχτα στον Άρη: G = 0 W/m²)
# ============================================================================


def test_edge_case_01_nyxta_mhdeniki_aktinovolia():
    """Πλήρης απουσία φωτός (G=0): Μηδενική φωτοβολταϊκή ισχύς και άμεση εκκένωση μπαταρίας."""
    p_pv = ypologise_isxy_fwtovoltaikou(
        apodosi_fwtovoltaikou=0.20,
        epifaneia_m2=100.0,
        aktinovolia_w_m2=0.0,
        syntelestis_epikathisis=0.8,
    )
    assert p_pv == 0.0

    # Κατανάλωση νύχτας: θέρμανση 8 kW, κρίσιμα 2 kW = 10 kW. Παραγωγή 0 kW.
    fortia, elleimma, diathesimi, auto, katastasi = ypologise_ilektriko_isozygio_kai_autonomia(
        paragwgi_kw=p_pv,
        krisima_fortia_kw=10.0,
        anavlita_fortia_kw=0.0,
        apwleies_kw=0.0,
        energeia_syssorefti_kwh=30.0,
        efedreia_idi_afairemeni=True,
    )
    assert fortia == 10.0
    assert elleimma == 10.0
    assert auto == pytest.approx(30.0 / 10.0)  # 3 ώρες
    assert katastasi == "ekkenwsi_se_exelixi"


# ============================================================================
# EDGE-CASE 2: Εξάντληση μπαταριών (0 kWh, έλλειμμα χωρίς αποθήκευση)
# ============================================================================


def test_edge_case_02_eksantlisi_mpatariwn():
    """Μηδενική ενέργεια συσσωρευτή: Άμεση κατάρρευση αυτονομίας (0 h, εκκένωση εφεδρείας)."""
    fortia, elleimma, diathesimi, auto, katastasi = ypologise_ilektriko_isozygio_kai_autonomia(
        paragwgi_kw=0.0,
        krisima_fortia_kw=10.0,
        anavlita_fortia_kw=0.0,
        apwleies_kw=0.0,
        energeia_syssorefti_kwh=0.0,
        efedreia_idi_afairemeni=True,
    )
    assert fortia == 10.0
    assert elleimma == 10.0
    assert diathesimi == 0.0
    assert auto == 0.0
    assert katastasi == "ekkenwsi_efedreias"


# ============================================================================
# EDGE-CASE 3: Κρίσιμη πτώση οξυγόνου κάτω από το όριο πίεσης (O2 starvation)
# ============================================================================


def test_edge_case_03_katwfli_o2_paraviasmeno():
    """Μερική πίεση O2 κάτω από το όριο των 16 kPa: Μηδενικό αξιοποιήσιμο απόθεμα και συναγερμός."""
    moles, maza_kg, auto_h, katastasi = ypologise_apothema_kai_autonomia_oxygonou(
        ogkos_m3=1000.0,
        thermokrasia_k=293.0,
        meriki_piesi_oxygonou_pa=14500.0,  # κάτω από 16.000 Pa
        katwfli_asfaleias_piesis_pa=16000.0,
        arithmos_katoikwn=4,
        katanalwsi_ana_atomo_kg_h=0.04,
        rythmos_paragwgis_kg_h=0.0,
    )
    assert moles == 0.0
    assert maza_kg == 0.0
    assert auto_h == 0.0
    assert katastasi == "katwfli_paraviasmeno"


# ============================================================================
# EDGE-CASE 4: Πλήρης εξάντληση νερού και απόρριψη νέας εντολής άρδευσης
# ============================================================================


def test_edge_case_04_pliris_eksantlisi_nerou(synedria_dokimwn: Session):
    """Εξάντληση νερού δεξαμενής στο επίπεδο εφεδρείας: Απόρριψη προεπισκόπησης και επιβεβαίωσης."""
    ypiresia = YpiresiaPorwn(synedria_dokimwn)
    syntonistis = XRHSTES_DEMO["syntonistis"]

    # 1. Κατέβασμα στάθμης ακριβώς στην εφεδρεία ασφαλείας (1500 L)
    dex = synedria_dokimwn.get(DexameniNerou, "dexameni_01")
    dex.trexwn_ogkos_l = 1500.0
    synedria_dokimwn.commit()

    # Προσπάθεια προεπισκόπησης 50 L -> 400 ANEPARKES_NERO
    with pytest.raises(SfalmaDomain) as exc:
        ypiresia.proepiskopisi_ardefsis(
            id_thermokipiou="thermokipio_01",
            id_zwnis="zwni_01",
            posotita_nerou_l=50.0,
        )
    assert exc.value.katastasi_http == 400
    assert exc.value.kodikos == KodikosSfalmatos.ANEPARKES_NERO

    # 2. Κάλυψη γραμμής 228 (ypiresia_porwn.py): Έγκυρη προεπισκόπηση, αλλά το νερό εξαντλείται πριν την επιβεβαίωση
    fake_prev_id = f"prev_drain_{uuid.uuid4().hex[:6]}"
    PROEPISKOPISEIS_ARDEFSIS[fake_prev_id] = {
        "id_dexamenis": "dexameni_01",
        "id_zwnis": "zwni_01",
        "posotita_nerou_l": 100.0,
        "diarkeia_lepta": 30,
        "xronos_enarksis": datetime.now(timezone.utc),
    }

    with pytest.raises(SfalmaDomain) as exc2:
        ypiresia.dimiourgia_programmatos_ardefsis(fake_prev_id, syntonistis)
    assert exc2.value.katastasi_http == 409
    assert exc2.value.kodikos == KodikosSfalmatos.ANEPARKES_NERO


# ============================================================================
# EDGE-CASE 5: Αισθητήρας offline / stale / μηδενική ποιότητα
# ============================================================================


def test_edge_case_05_aisthitiras_offline_kai_stale(
    pelatis_dokimwn: TestClient, synedria_dokimwn: Session
):
    """Αισθητήρας σε κατάσταση βλάβης ή με παλιές μετρήσεις."""
    aisth = synedria_dokimwn.get(Aisthitiras, "aisth_thermokrasia_esw")
    aisth.katastasi = "ektos_leitourgias"

    metrisi_palaia = MetrisiAisthitira(
        id_aisthitira="aisth_thermokrasia_esw",
        timi=293.0,
        monada="K",
        eidos="metrimeno",
        pigi="sfalma_epiasfalisis",
        poiotita="sfalma",
        tasi="statheri",
        apolyti_avevaiotita=5.0,
        einai_palio=True,
        xronos_metrisis=datetime.now(timezone.utc) - timedelta(hours=24),
    )
    synedria_dokimwn.add(metrisi_palaia)
    synedria_dokimwn.commit()

    resp = pelatis_dokimwn.get("/api/v1/aisthitires/aisth_thermokrasia_esw/metriseis")
    assert resp.status_code == 200
    metriseis = resp.json()
    assert any(m["poiotita"] == "sfalma" for m in metriseis)


# ============================================================================
# EDGE-CASE 6: Πλήρης απώλεια επικοινωνίας rover (comm loss -> avevaio state)
# ============================================================================


def test_edge_case_06_rover_comm_loss_avevaio(
    pelatis_dokimwn: TestClient, synedria_dokimwn: Session
):
    """Rover χωρίς επικοινωνία (απουσία): Η εντολή ανάκλησης μπαίνει σε κατάσταση 'avevaio'."""
    rover = synedria_dokimwn.get(OximaExerevnis, "rover_01")
    rover.katastasi_epikoinwnias = "apousia"
    synedria_dokimwn.commit()

    resp = pelatis_dokimwn.post(
        "/api/v1/oximata/rover_01/anaklisi/entoles",
        headers={"X-Id-Xristi": "syntonistis"},
    )
    assert resp.status_code == 200
    dedomena = resp.json()
    assert dedomena["katastasi_entolis"] == "avevaio"
    assert "Απώλεια επικοινωνίας" in dedomena["minyma"]


# ============================================================================
# EDGE-CASE 7: Ταυτόχρονες συγκρουόμενες εντολές (optimistic lock conflict 409)
# ============================================================================


def test_edge_case_07_optimistic_locking_conflict(
    pelatis_dokimwn: TestClient, synedria_dokimwn: Session
):
    """Σύγκρουση ταυτόχρονης τροποποίησης (409 Conflict): Η αναμενόμενη έκδοση διαφέρει."""
    # 1. Δημιουργία προεπισκόπησης με βάση έκδοση 1
    resp_prev = pelatis_dokimwn.post(
        "/api/v1/xwroi-katoikisis/xwros_01/thermokrasia/proepiskopisi",
        json={"epithymiti_thermokrasia_k": 294.0, "anamenomeni_ekdosi_katastasis": 1},
        headers={"X-Id-Xristi": "xristis_zwis"},
    )
    assert resp_prev.status_code == 200
    id_prev = resp_prev.json()["id_proepiskopisis"]

    # 2. Ταυτόχρονη αλλαγή κατάστασης από άλλο χρήστη (έκδοση γίνεται 2)
    xwros = synedria_dokimwn.get(XwrosKatoikisis, "xwros_01")
    xwros.ekdosi_katastasis = 2
    synedria_dokimwn.commit()

    # 3. Προσπάθεια επιβεβαίωσης με την παλιά έκδοση 1 -> 409 STALE_PROEPISKOPISI
    resp_conf = pelatis_dokimwn.post(
        "/api/v1/xwroi-katoikisis/xwros_01/thermokrasia/entoles",
        json={"id_proepiskopisis": id_prev, "anamenomeni_ekdosi_katastasis": 1},
        headers={"X-Id-Xristi": "xristis_zwis"},
    )
    assert resp_conf.status_code == 409
    assert resp_conf.json()["sfalma"]["kodikos"] == KodikosSfalmatos.STALE_PROEPISKOPISI.value


# ============================================================================
# EDGE-CASE 8: Διπλή αποστολή με το ίδιο Idempotency-Key
# ============================================================================


def test_edge_case_08_idempotency_key_replay(
    pelatis_dokimwn: TestClient, synedria_dokimwn: Session
):
    """Επανάληψη εντολής άρδευσης με το ίδιο κλειδί μοναδικότητας: Επιστροφή προηγούμενου αποτελέσματος χωρίς διπλή αφαίρεση νερού."""
    # 1. Προεπισκόπηση άρδευσης
    resp_prev = pelatis_dokimwn.post(
        "/api/v1/thermokipia/thermokipio_01/ardefsi/proepiskopisi",
        json={"id_zwnis": "zwni_01", "posotita_nerou_l": 50.0, "diarkeia_lepta": 30},
        headers={"X-Id-Xristi": "xristis_porwn"},
    )
    assert resp_prev.status_code == 200
    id_prev = resp_prev.json()["id_proepiskopisis"]

    idemp_key = f"idemp_ardefsi_{uuid.uuid4().hex[:8]}"

    # 2. Πρώτη εκτέλεση
    resp1 = pelatis_dokimwn.post(
        "/api/v1/thermokipia/thermokipio_01/ardefsi/programmata",
        json={"id_proepiskopisis": id_prev},
        headers={"X-Id-Xristi": "xristis_porwn", "Idempotency-Key": idemp_key},
    )
    assert resp1.status_code == 200
    id_entolis_1 = resp1.json()["id_entolis"]

    # 3. Δεύτερη εκτέλεση με το ίδιο κλειδί -> Idempotent Replay (γραμμές 197-201 στο ypiresia_porwn.py)
    resp2 = pelatis_dokimwn.post(
        "/api/v1/thermokipia/thermokipio_01/ardefsi/programmata",
        json={"id_proepiskopisis": id_prev},
        headers={"X-Id-Xristi": "xristis_porwn", "Idempotency-Key": idemp_key},
    )
    assert resp2.status_code == 200
    assert resp2.json()["id_entolis"] == id_entolis_1
    assert "idempotent replay" in resp2.json()["minyma"]


# ============================================================================
# EDGE-CASE 9: Ακραίες Αρειανές Θερμοκρασίες (T_exw = 140 K, T_esw = 310 K)
# ============================================================================


def test_edge_case_09_akrees_thermokrasies(pelatis_dokimwn: TestClient):
    """Ακραίες θερμοκρασίες χειμώνα (140 K) και υπέρβαση μέγιστης επιτρεπτής εσωτερικής θερμοκρασίας."""
    # 1. Θερμικές απώλειες με deltaT = 170 K (310 K - 140 K): Q = 0.2 * 500 * 170 = 17.000 W = 17 kW
    apwleies = ypologise_thermikes_apwleies(
        syntelestis_thermoperatotitas_w_m2k=0.2,
        epifaneia_m2=500.0,
        thermokrasia_eswteriki_k=310.0,
        thermokrasia_exwteriki_k=140.0,
    )
    assert apwleies == pytest.approx(17000.0)

    # 2. Απαίτηση θέρμανσης
    apaitisi = ypologise_apaitisi_thermansis(
        syntelestis_thermoperatotitas_w_m2k=0.2,
        epifaneia_m2=500.0,
        thermokrasia_eswteriki_k=310.0,
        thermokrasia_exwteriki_k=140.0,
        syntelestis_apodosis_cop=1.0,
    )
    assert apaitisi == pytest.approx(17000.0)

    # 3. Αίτημα θερμοκρασίας > 305 K απορρίπτεται με 400 AKYRI_THERMOKRATIA
    resp = pelatis_dokimwn.post(
        "/api/v1/xwroi-katoikisis/xwros_01/thermokrasia/proepiskopisi",
        json={"epithymiti_thermokrasia_k": 310.0, "anamenomeni_ekdosi_katastasis": 1},
        headers={"X-Id-Xristi": "xristis_zwis"},
    )
    assert resp.status_code == 400
    assert resp.json()["sfalma"]["kodikos"] == KodikosSfalmatos.AKYRI_THERMOKRATIA.value


# ============================================================================
# EDGE-CASE 10: Ακυρώσεις Προγραμμάτων (Φωτισμός, Ανακύκλωση, Απόφαση Καταιγίδας)
# ============================================================================


def test_edge_case_10_akyroseis_kai_apofaseis_faults(
    pelatis_dokimwn: TestClient, synedria_dokimwn: Session
):
    """Ακυρώσεις ανύπαρκτων προγραμμάτων (γραμμές 287, 425 στο poroi.py) και απόφαση καταιγίδας από μη συντονιστή (γραμμή 549)."""
    # 1. Ακύρωση ανύπαρκτου προγράμματος φωτισμού -> 404 (line 287 στο poroi.py)
    resp_light = pelatis_dokimwn.post(
        "/api/v1/thermokipia/thermokipio_01/fwtismos/programmata/aniparxto_fwtismo/akyrosi",
        headers={"X-Id-Xristi": "syntonistis"},
    )
    assert resp_light.status_code == 404
    assert resp_light.json()["sfalma"]["kodikos"] == KodikosSfalmatos.DEN_VRETHIKE.value

    # 2. Ακύρωση ανύπαρκτου προγράμματος ανακύκλωσης -> 404 (line 425 στο poroi.py)
    resp_recyc = pelatis_dokimwn.post(
        "/api/v1/nero/anakyklwsi/programmata/aniparxti_anakyklwsi/akyrosi",
        headers={"X-Id-Xristi": "syntonistis"},
    )
    assert resp_recyc.status_code == 404
    assert resp_recyc.json()["sfalma"]["kodikos"] == KodikosSfalmatos.DEN_VRETHIKE.value

    # 3. Επιτυχής ακύρωση υπάρχοντος προγράμματος φωτισμού
    twrinos = datetime.now(timezone.utc)
    prog_fwt = ProgrammaFwtismou(
        id_programmatos="prog_fwt_dokimi",
        id_thermokipiou="thermokipio_01",
        id_zwnis="zwni_01",
        isxys_kw=2.0,
        xronos_enarksis=twrinos,
        xronos_liksis=twrinos + timedelta(hours=6),
        katastasi="programmatismeno",
    )
    synedria_dokimwn.add(prog_fwt)
    synedria_dokimwn.commit()

    resp_cancel = pelatis_dokimwn.post(
        "/api/v1/thermokipia/thermokipio_01/fwtismos/programmata/prog_fwt_dokimi/akyrosi",
        headers={"X-Id-Xristi": "syntonistis"},
    )
    assert resp_cancel.status_code == 200
    assert resp_cancel.json()["katastasi"] == "akyrothike"

    # 4. ypovoli_apofasis_kataigidas απευθείας στην υπηρεσία από μη συντονιστή -> 403 (line 549 ypiresia_symvantwn_kai_senariwn.py)
    ypiresia_sen = YpiresiaSymvantwnKaiSenariwn(synedria_dokimwn)
    xristis_porwn = XRHSTES_DEMO["xristis_porwn"]
    with pytest.raises(SfalmaDomain) as exc_info:
        ypiresia_sen.ypovoli_apofasis_kataigidas(
            epilogi="pausi_anavlhtwn",
            aitiologia="Μη εξουσιοδοτημένη ενέργεια",
            xristis=xristis_porwn,
        )
    assert exc_info.value.katastasi_http == 403
    assert exc_info.value.kodikos == KodikosSfalmatos.ANARMODIOS_XRISTIS
