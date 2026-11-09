"""Δοκιμές ενοποίησης για rover, αποστολές, ανάκληση και ασφαλή στάση (TEST-16, TEST-27)."""

from fastapi.testclient import TestClient


def test_rover_safe_stop_preview_and_execute(pelatis_dokimwn: TestClient):
    """TEST-27: Προεπισκόπηση και εκτέλεση ασφαλούς στάσης rover (MISSION-08)."""
    id_oximatos = "rover_01"

    # 1. Προεπισκόπηση ασφαλούς στάσης
    apantisi_proep = pelatis_dokimwn.post(
        f"/api/v1/oximata/{id_oximatos}/asfalis-stasi/proepiskopisi"
    )
    assert apantisi_proep.status_code == 200
    proep = apantisi_proep.json()
    assert proep["protinomeni_drasi"] == "asfalis_stasi"
    assert "energeia" in proep["epiptwseis"]

    # 2. Εκτέλεση εντολής ασφαλούς στάσης
    apantisi_stasis = pelatis_dokimwn.post(
        f"/api/v1/oximata/{id_oximatos}/asfalis-stasi/entoles",
        headers={"X-Id-Xristi": "xristis_apostolwn"},
    )
    assert apantisi_stasis.status_code == 200
    assert apantisi_stasis.json()["katastasi_oximatos"] == "asfalis_stasi"

    # 3. Επαλήθευση νέας κατάστασης
    apantisi_meta = pelatis_dokimwn.get(f"/api/v1/oximata/{id_oximatos}/apostoles")
    assert apantisi_meta.json()["kinisi"]["katastasi"] == "asfalis_stasi"


def test_rover_comm_degraded_leads_to_uncertain_state(pelatis_dokimwn: TestClient):
    """TEST-16: Υποβαθμισμένη επικοινωνία rover προκαλεί κατάσταση 'avevaio' και όχι ψευδή 'oloklirothike'."""
    id_oximatos = "rover_01"

    # 1. Ενεργοποίηση καταιγίδας που υποβαθμίζει την επικοινωνία του rover
    pelatis_dokimwn.post(
        "/api/v1/senaria/kataigida-skonis/energopoiisi",
        headers={"X-Id-Xristi": "syntonistis"},
    )

    # 2. Αίτημα ανάκλησης εν μέσω καταιγίδας με υποβαθμισμένη τηλεμετρία
    apantisi = pelatis_dokimwn.post(
        f"/api/v1/oximata/{id_oximatos}/anaklisi/entoles",
        headers={"X-Id-Xristi": "xristis_apostolwn"},
    )
    assert apantisi.status_code == 200
    dedomena = apantisi.json()
    # Η κατάσταση της εντολής πρέπει να είναι 'avevaio' λόγω μη επιβεβαίωσης επικοινωνίας
    assert dedomena["katastasi_entolis"] == "avevaio"
    assert "Υποβαθμισμένη επικοινωνία" in dedomena["minyma"]
