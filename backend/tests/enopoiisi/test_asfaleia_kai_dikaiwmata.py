"""Δοκιμές ενοποίησης για ασφάλεια, ρόλους, μεταβίβαση και idempotency (TEST-12, TEST-13, TEST-23)."""

from fastapi.testclient import TestClient


def test_roloi_apagorevsi_kai_egkrisi_syntonisti(pelatis_dokimwn: TestClient):
    """TEST-12: Έλεγχος δικαιωμάτων ρόλων: απόρριψη μη εξουσιοδοτημένων ενεργειών και coordinator approval."""
    # 1. Ο χειριστής υποστήριξης ζωής ΔΕΝ μπορεί να προγραμματίσει άρδευση (μόνο ο χειριστής πόρων ή ο coordinator)
    apantisi_ardefsi = pelatis_dokimwn.post(
        "/api/v1/thermokipia/thermokipio_01/ardefsi/proepiskopisi",
        json={"id_zwnis": "zwni_01", "posotita_nerou_l": 50.0, "diarkeia_lepta": 30},
        headers={"X-Id-Xristi": "xristis_zwis", "X-Rolos": "ypefthynos_ypostiriksis_zwis"},
    )
    assert apantisi_ardefsi.status_code == 403
    assert apantisi_ardefsi.json()["sfalma"]["kodikos"] == "ANARMODIOS_XRISTIS"

    # 2. Ο χειριστής πόρων ΔΕΝ μπορεί να διατάξει διασταυρούμενο load shedding (μόνο coordinator)
    apantisi_periorismou = pelatis_dokimwn.post(
        "/api/v1/energeia/periorismos-fortiwn/entoles",
        json={"pausi_anavlhtwn": True, "aitiologia": "Δοκιμή παύσης"},
        headers={"X-Id-Xristi": "xristis_porwn", "X-Rolos": "ypefthynos_porwn"},
    )
    assert apantisi_periorismou.status_code == 403
    assert apantisi_periorismou.json()["sfalma"]["kodikos"] == "ANARMODIOS_XRISTIS"

    # 3. Ο συντονιστής αποικίας ΜΠΟΡΕΙ να εκτελέσει load shedding
    proepiskopisi_periorismou = pelatis_dokimwn.post(
        "/api/v1/energeia/periorismos-fortiwn/proepiskopisi",
        json={"pausi_anavlhtwn": True, "aitiologia": "Επίσημη έγκριση συντονιστή για δοκιμή"},
    ).json()
    apantisi_periorismou_syntonisti = pelatis_dokimwn.post(
        "/api/v1/energeia/periorismos-fortiwn/entoles",
        json={"id_proepiskopisis": proepiskopisi_periorismou["id_proepiskopisis"]},
        headers={"X-Id-Xristi": "syntonistis", "X-Rolos": "syntonistis_apoikias"},
    )
    assert apantisi_periorismou_syntonisti.status_code == 200
    assert apantisi_periorismou_syntonisti.json()["pausi_anavlhtwn"] is True


def test_kleidi_monadikotitas_apotrepei_dipli_ektelesi(pelatis_dokimwn: TestClient):
    """TEST-13: Το κλειδί idempotency αποτρέπει διπλή εκτέλεση εντολής."""
    id_xwrou = "xwros_01"

    # Προεπισκόπηση
    proep = pelatis_dokimwn.post(
        f"/api/v1/xwroi-katoikisis/{id_xwrou}/thermokrasia/proepiskopisi",
        json={"epithymiti_thermokrasia_k": 294.0, "anamenomeni_ekdosi_katastasis": 1},
        headers={"X-Id-Xristi": "xristis_zwis"},
    ).json()

    # Πρώτη εκτέλεση με μοναδικό κλειδί
    kleidi = "monadiko_aitima_abc_123"
    apantisi_1 = pelatis_dokimwn.post(
        f"/api/v1/xwroi-katoikisis/{id_xwrou}/thermokrasia/entoles",
        json={"id_proepiskopisis": proep["id_proepiskopisis"], "anamenomeni_ekdosi_katastasis": 1},
        headers={"X-Id-Xristi": "xristis_zwis", "Idempotency-Key": kleidi},
    )
    assert apantisi_1.status_code == 200
    id_entolis_1 = apantisi_1.json()["id_entolis"]

    # Δεύτερη εκτέλεση με το ίδιο ακριβώς κλειδί (replay)
    apantisi_2 = pelatis_dokimwn.post(
        f"/api/v1/xwroi-katoikisis/{id_xwrou}/thermokrasia/entoles",
        json={"id_proepiskopisis": proep["id_proepiskopisis"], "anamenomeni_ekdosi_katastasis": 1},
        headers={"X-Id-Xristi": "xristis_zwis", "Idempotency-Key": kleidi},
    )
    assert apantisi_2.status_code == 200
    # Επιστρέφεται η ίδια εντολή χωρίς διπλή τροποποίηση της κατάστασης
    assert apantisi_2.json()["id_entolis"] == id_entolis_1
    assert apantisi_2.json() == apantisi_1.json()


def test_metavivasi_egkrisi_kai_anaklisi(pelatis_dokimwn: TestClient):
    """TEST-23: Μεταβίβαση ελέγχου από coordinator, διάρκεια, λήξη και ανάκληση (CORE-18)."""
    # 1. Έγκριση μεταβίβασης από συντονιστή
    apantisi_metavivasis = pelatis_dokimwn.post(
        "/api/v1/dikaiwmata/metavivaseis",
        json={
            "id_paralipti": "xristis_zwis",
            "rolos": "ypefthynos_porwn",
            "diarkeia_wres": 4.0,
            "aitiologia": "Κάλυψη βάρδιας διαχείρισης πόρων",
        },
        headers={"X-Id-Xristi": "syntonistis"},
    )
    assert apantisi_metavivasis.status_code == 200
    metav = apantisi_metavivasis.json()
    id_metavivasis = metav["id_metavivasis"]

    # 2. Έλεγχος ότι εμφανίζεται στις ενεργές μεταβιβάσεις
    apantisi_listas = pelatis_dokimwn.get("/api/v1/dikaiwmata/metavivaseis?mono_energes=true")
    assert any(
        stoixeio_mi["id_metavivasis"] == id_metavivasis for stoixeio_mi in apantisi_listas.json()
    )

    # 3. Ανάκληση μεταβίβασης
    apantisi_anaklisi = pelatis_dokimwn.post(
        f"/api/v1/dikaiwmata/metavivaseis/{id_metavivasis}/anaklisi",
        headers={"X-Id-Xristi": "syntonistis"},
    )
    assert apantisi_anaklisi.status_code == 200
    assert apantisi_anaklisi.json()["energo"] is False

    # 4. Επαλήθευση ότι δεν είναι πλέον ενεργή
    apantisi_listas_meta = pelatis_dokimwn.get("/api/v1/dikaiwmata/metavivaseis?mono_energes=true")
    assert not any(
        stoixeio_mi["id_metavivasis"] == id_metavivasis
        for stoixeio_mi in apantisi_listas_meta.json()
    )


def test_psevdonymo_xeiristi_oximatos(pelatis_dokimwn: TestClient):
    """Έλεγχος υποστήριξης των headers alias 'xeiristis_oximatos'."""
    apantisi = pelatis_dokimwn.get(
        "/api/v1/taftopoiisi/trexwn-xristis",
        headers={"X-Id-Xristi": "xeiristis_oximatos", "X-Rolos": "xeiristis_oximatos"},
    )
    assert apantisi.status_code == 200
    assert apantisi.json()["vasikos_rolos"] == "ypefthynos_apostolwn"
