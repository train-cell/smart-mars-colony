"""Επιπλέον δοκιμές ενοποίησης για κάλυψη όλων των διαδρομών και υπηρεσιών (Coverage >= 85%)."""

import pytest
from fastapi.testclient import TestClient

from backend.app.fysika_montela.fysika_montela import ypologise_energeia_kinisis_oximatos


def test_aisthitires_kai_metriseis_endpoints(pelatis_dokimwn: TestClient):
    """Έλεγχος λίστας αισθητήρων με φίλτρα και ιστορικού μετρήσεων."""
    # Όλοι οι αισθητήρες
    apantisi_ola = pelatis_dokimwn.get("/api/v1/aisthitires")
    assert apantisi_ola.status_code == 200
    assert len(apantisi_ola.json()) >= 8

    # Φίλτρο ανά υποσύστημα
    apantisi_zwis = pelatis_dokimwn.get("/api/v1/aisthitires?yposystima=ypostiriksi_zwis")
    assert apantisi_zwis.status_code == 200
    assert all(a["yposystima"] == "ypostiriksi_zwis" for a in apantisi_zwis.json())

    # Ιστορικό μετρήσεων συγκεκριμένου αισθητήρα
    apantisi_metr = pelatis_dokimwn.get(
        "/api/v1/aisthitires/aisth_thermokrasia_esw/metriseis?orio=10"
    )
    assert apantisi_metr.status_code == 200
    assert len(apantisi_metr.json()) >= 1
    assert apantisi_metr.json()[0]["timi"] == 293.0


def test_taftopoiisi_kai_xristes(pelatis_dokimwn: TestClient):
    """Έλεγχος εισόδου και ανάκτησης τρέχοντος χρήστη."""
    # Έγκυρη είσοδος
    apantisi_login = pelatis_dokimwn.post(
        "/api/v1/taftopoiisi/eisodos",
        json={"id_xristi": "xristis_zwis"},
    )
    assert apantisi_login.status_code == 200
    assert apantisi_login.json()["id_xristi"] == "xristis_zwis"

    # Μη έγκυρος χρήστης
    apantisi_fail = pelatis_dokimwn.post(
        "/api/v1/taftopoiisi/eisodos",
        json={"id_xristi": "agnwstos"},
    )
    assert apantisi_fail.status_code == 404

    # Ανάκτηση τρέχοντος χρήστη μέσω headers
    apantisi_trexwn = pelatis_dokimwn.get(
        "/api/v1/taftopoiisi/trexwn-xristis",
        headers={"X-Id-Xristi": "xristis_porwn"},
    )
    assert apantisi_trexwn.status_code == 200
    assert apantisi_trexwn.json()["id_xristi"] == "xristis_porwn"


def test_poroi_anakyklwsi_fwtismos_kai_fortia(pelatis_dokimwn: TestClient):
    """Έλεγχος ανακύκλωσης, φωτισμού, φορτίων, ροών και ισοζυγίου νερού."""
    # 1. Θερμοκήπια και Ζώνες
    apantisi_th = pelatis_dokimwn.get("/api/v1/thermokipia")
    assert apantisi_th.status_code == 200
    assert len(apantisi_th.json()) >= 1

    apantisi_z = pelatis_dokimwn.get("/api/v1/thermokipia/thermokipio_01/zwnes")
    assert apantisi_z.status_code == 200
    assert len(apantisi_z.json()) >= 2

    # 2. Φωτισμός: Προεπισκόπηση -> Δημιουργία -> Λίστα -> Ακύρωση
    proep_fwt = pelatis_dokimwn.post(
        "/api/v1/thermokipia/thermokipio_01/fwtismos/proepiskopisi",
        json={"id_zwnis": "zwni_01", "isxys_kw": 3.0, "diarkeia_wres": 5.0},
    ).json()
    assert proep_fwt["synoliki_energeia_kwh"] == 15.0

    prog_fwt = pelatis_dokimwn.post(
        "/api/v1/thermokipia/thermokipio_01/fwtismos/entoles",
        json={"id_zwnis": "zwni_01", "isxys_kw": 3.0, "diarkeia_wres": 5.0},
        headers={"X-Id-Xristi": "xristis_porwn"},
    ).json()
    id_prog_fwt = prog_fwt["id_programmatos"]

    lista_fwt = pelatis_dokimwn.get(
        "/api/v1/thermokipia/thermokipio_01/fwtismos/programmata"
    ).json()
    assert any(p["id_programmatos"] == id_prog_fwt for p in lista_fwt)

    akyrosi_fwt = pelatis_dokimwn.post(
        f"/api/v1/thermokipia/thermokipio_01/fwtismos/programmata/{id_prog_fwt}/akyrosi",
        headers={"X-Id-Xristi": "xristis_porwn"},
    )
    assert akyrosi_fwt.status_code == 200

    # 3. Ανακύκλωση Νερού: Προεπισκόπηση -> Δημιουργία -> Λίστα -> Ακύρωση
    proep_anak = pelatis_dokimwn.post(
        "/api/v1/nero/anakyklwsi/proepiskopisi",
        json={"posotita_nerou_l": 500.0, "apodosi": 0.85},
    ).json()
    assert proep_anak["epistrefomeno_nero_l"] == 425.0

    prog_anak = pelatis_dokimwn.post(
        "/api/v1/nero/anakyklwsi/programmata",
        json={"posotita_nerou_l": 500.0, "apodosi": 0.85},
        headers={"X-Id-Xristi": "xristis_porwn"},
    ).json()
    id_prog_anak = prog_anak["id_programmatos"]

    lista_anak = pelatis_dokimwn.get("/api/v1/nero/anakyklwsi/programmata").json()
    assert any(p["id_programmatos"] == id_prog_anak for p in lista_anak)

    akyrosi_anak = pelatis_dokimwn.post(
        f"/api/v1/nero/anakyklwsi/programmata/{id_prog_anak}/akyrosi",
        headers={"X-Id-Xristi": "xristis_porwn"},
    )
    assert akyrosi_anak.status_code == 200

    # 4. Ισοζύγιο, Ροές και Τηλεμετρίες Ενέργειας
    assert pelatis_dokimwn.get("/api/v1/nero/isozygio").status_code == 200
    assert pelatis_dokimwn.get("/api/v1/nero/roes").status_code == 200
    assert pelatis_dokimwn.get("/api/v1/energeia/katastasi").status_code == 200
    assert pelatis_dokimwn.get("/api/v1/energeia/fortia").status_code == 200
    assert pelatis_dokimwn.get("/api/v1/energeia/fwtovoltaika").status_code == 200
    assert pelatis_dokimwn.get("/api/v1/energeia/syssoreftes").status_code == 200


def test_apostoles_dimiourgia_kai_anavoli(pelatis_dokimwn: TestClient):
    """Έλεγχος δημιουργίας αποστολής rover, προεπισκόπησης και αναβολής."""
    id_oximatos = "rover_01"

    # 1. Προεπισκόπηση αποστολής
    proep = pelatis_dokimwn.post(
        f"/api/v1/oximata/{id_oximatos}/apostoles/proepiskopisi",
        json={
            "titlos": "Εξερεύνηση Κρατήρα",
            "skopos": "Συλλογή δειγμάτων πετρωμάτων",
            "apostasi_km": 1.5,
            "ektimwmeni_diarkeia_wres": 1.0,
        },
    ).json()
    assert proep["energeiaka_efikto"] is True

    # 2. Δημιουργία αποστολής
    apost = pelatis_dokimwn.post(
        f"/api/v1/oximata/{id_oximatos}/apostoles",
        json={
            "titlos": "Εξερεύνηση Κρατήρα",
            "skopos": "Συλλογή δειγμάτων πετρωμάτων",
            "apostasi_km": 1.5,
            "ektimwmeni_diarkeia_wres": 1.0,
        },
        headers={"X-Id-Xristi": "xristis_apostolwn"},
    ).json()
    id_ap = apost["id_apostolis"]

    # 3. Αναβολή αποστολής
    anavoli = pelatis_dokimwn.post(
        f"/api/v1/oximata/{id_oximatos}/apostoles/{id_ap}/anavoli",
        headers={"X-Id-Xristi": "xristis_apostolwn"},
    )
    assert anavoli.status_code == 200
    assert anavoli.json()["katastasi"] == "anavolh"


def test_entoles_lifecycle_kai_audit_log(pelatis_dokimwn: TestClient):
    """Έλεγχος ανάκτησης κύκλου ζωής εντολής, ακύρωσης και ιστορικού ελέγχου."""
    # 1. Δημιουργία εντολής μέσω αλλαγής θερμοκρασίας
    proep = pelatis_dokimwn.post(
        "/api/v1/xwroi-katoikisis/xwros_01/thermokrasia/proepiskopisi",
        json={"epithymiti_thermokrasia_k": 294.0, "anamenomeni_ekdosi_katastasis": 1},
        headers={"X-Id-Xristi": "xristis_zwis"},
    ).json()

    entoli = pelatis_dokimwn.post(
        "/api/v1/xwroi-katoikisis/xwros_01/thermokrasia/entoles",
        json={"id_proepiskopisis": proep["id_proepiskopisis"], "anamenomeni_ekdosi_katastasis": 1},
        headers={"X-Id-Xristi": "xristis_zwis"},
    ).json()
    id_entolis = entoli["id_entolis"]

    # 2. Ανάκτηση στοιχείων εντολής
    apantisi_entoli = pelatis_dokimwn.get(f"/api/v1/entoles/{id_entolis}")
    assert apantisi_entoli.status_code == 200
    assert apantisi_entoli.json()["id_entolis"] == id_entolis
    assert len(apantisi_entoli.json()["symvanta"]) >= 1

    # 3. Ανάκτηση Audit Log
    audit = pelatis_dokimwn.get("/api/v1/istoriko-elegxou?orio=20")
    assert audit.status_code == 200
    assert len(audit.json()) >= 1


def test_phy06_energeia_kinisis_oximatos():
    """Έλεγχος φυσικού μοντέλου κίνησης rover PHY-06 με κλίση και απόσταση."""
    # 800 kg, 2000 m, κλίση 0.0 rad, τριβή 0.05, απόδοση 0.8, voithitiki 100 W, taxytita 1.11 m/s (~4 km/h)
    kinisi_j, voith_j, kwh = ypologise_energeia_kinisis_oximatos(
        maza_kg=800.0,
        apostasi_m=2000.0,
        klisi_rad=0.0,
        syntelestis_kylisis=0.05,
        apodosi_kinisis=0.8,
        voithitiki_isxys_w=100.0,
        taxytita_m_s=1.11111,
    )
    # W_kinisi = (800 * 3.72076 * 0.05 * 2000) / 0.8 = 372076 J
    # Xronos = 2000 / 1.11111 = 1800 s (0.5 h). Voithitiki = 100 * 1800 = 180000 J
    # Synoliki = 552076 J ≈ 0.1533 kWh
    assert kinisi_j == pytest.approx(372076.0, rel=1e-3)
    assert voith_j == pytest.approx(180000.0, rel=1e-3)
    assert kwh == pytest.approx(0.15335, rel=1e-3)
