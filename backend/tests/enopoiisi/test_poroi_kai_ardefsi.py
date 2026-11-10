"""Δοκιμές ενοποίησης για πόρους, άρδευση, νερό και ενέργεια (TEST-10, TEST-11, TEST-25, TEST-26)."""

from fastapi.testclient import TestClient


def test_ardefsi_proepiskopisi_epivevaiwsi_akyrosi(pelatis_dokimwn: TestClient):
    """TEST-10: Πλήρης ροή άρδευσης: Ζώνη -> Επιθεώρηση -> Preview -> Confirm -> Μείωση στάθμης -> Ακύρωση."""
    id_thermokipiou = "thermokipio_01"
    id_zwnis = "zwni_01"

    # 1. Έλεγχος αρχικής στάθμης δεξαμενής
    apantisi_nerou_prin = pelatis_dokimwn.get("/api/v1/nero/dexamenes")
    assert apantisi_nerou_prin.status_code == 200
    dexameni_prin = apantisi_nerou_prin.json()["dexamenes"][0]
    stathmi_prin = dexameni_prin["trexwn_ogkos_l"]

    # 2. Προεπισκόπηση άρδευσης 100 L
    apantisi_proep = pelatis_dokimwn.post(
        f"/api/v1/thermokipia/{id_thermokipiou}/ardefsi/proepiskopisi",
        json={"id_zwnis": id_zwnis, "posotita_nerou_l": 100.0, "diarkeia_lepta": 30},
        headers={"X-Id-Xristi": "xristis_porwn"},
    )
    assert apantisi_proep.status_code == 200
    proep = apantisi_proep.json()
    assert proep["id_proepiskopisis"] is not None
    assert proep["stathmi_meta_l"] == stathmi_prin - 100.0

    # 3. Επιβεβαίωση δημιουργίας προγράμματος
    apantisi_prog = pelatis_dokimwn.post(
        f"/api/v1/thermokipia/{id_thermokipiou}/ardefsi/programmata",
        json={"id_proepiskopisis": proep["id_proepiskopisis"]},
        headers={"X-Id-Xristi": "xristis_porwn"},
    )
    assert apantisi_prog.status_code == 200
    programma = apantisi_prog.json()
    id_programmatos = programma["id_programmatos"]
    assert programma["katastasi"] == "programmatismeno"
    assert programma["nea_stathmi_dexamenis_l"] == stathmi_prin
    assert programma["desmevmeno_nero_l"] == 100

    # 4. Επαλήθευση ότι η δεξαμενή μειώθηκε ακριβώς μία φορά κατά 100 L
    apantisi_nerou_meta = pelatis_dokimwn.get("/api/v1/nero/dexamenes")
    stathmi_meta = apantisi_nerou_meta.json()["dexamenes"][0]["trexwn_ogkos_l"]
    assert stathmi_meta == stathmi_prin

    # 5. Ακύρωση προγράμματος και επιστροφή ποσότητας (TEST-25)
    apantisi_akyrosis = pelatis_dokimwn.post(
        f"/api/v1/ardefsi/programmata/{id_programmatos}/akyrosi",
        headers={"X-Id-Xristi": "xristis_porwn"},
    )
    assert apantisi_akyrosis.status_code == 200
    assert apantisi_akyrosis.json()["katastasi"] == "akyrothike"

    # Επαλήθευση επιστροφής νερού
    apantisi_nerou_teliko = pelatis_dokimwn.get("/api/v1/nero/dexamenes")
    stathmi_teliki = apantisi_nerou_teliko.json()["dexamenes"][0]["trexwn_ogkos_l"]
    assert stathmi_teliki == stathmi_prin


def test_ardefsi_me_aneparkes_nero(pelatis_dokimwn: TestClient):
    """TEST-11 & TEST-26: Απόρριψη άρδευσης όταν ζητείται νερό πάνω από το διαθέσιμο (όχι silent clamp)."""
    id_thermokipiou = "thermokipio_01"
    id_zwnis = "zwni_01"

    # Ζήτηση 50,000 L όταν η δεξαμενή έχει 7,500 L
    apantisi = pelatis_dokimwn.post(
        f"/api/v1/thermokipia/{id_thermokipiou}/ardefsi/proepiskopisi",
        json={"id_zwnis": id_zwnis, "posotita_nerou_l": 50000.0, "diarkeia_lepta": 30},
        headers={"X-Id-Xristi": "xristis_porwn"},
    )
    assert apantisi.status_code == 409
    sfalma = apantisi.json()["sfalma"]
    assert sfalma["kodikos"] == "ANEPARKES_NERO"
    assert "diathesimo_l" in sfalma["leptomereies"]
