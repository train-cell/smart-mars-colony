"""Δοκιμές ενοποίησης για το υποσύστημα υποστήριξης ζωής και θερμοκρασίας (TEST-09, TEST-11, TEST-28)."""

import pytest
from fastapi.testclient import TestClient


def test_thermokrasia_proepiskopisi_epivevaiwsi_katastasi(pelatis_dokimwn: TestClient):
    """TEST-09: Πλήρης ροή αλλαγής θερμοκρασίας: Επιλογή -> Snapshot -> Preview -> Confirm -> Status."""
    id_xwrou = "xwros_01"

    # 1. Ανάγνωση τρέχουσας κατάστασης
    apantisi_katastasis = pelatis_dokimwn.get(f"/api/v1/xwroi-katoikisis/{id_xwrou}/katastasi")
    assert apantisi_katastasis.status_code == 200
    dedomena_prin = apantisi_katastasis.json()
    assert dedomena_prin["thermokrasia"]["epithymiti_k"] == 293.0
    ekdosi_prin = dedomena_prin["ekdosi_katastasis"]

    # 2. Αίτημα προεπισκόπησης (295 K)
    apantisi_proep = pelatis_dokimwn.post(
        f"/api/v1/xwroi-katoikisis/{id_xwrou}/thermokrasia/proepiskopisi",
        json={"epithymiti_thermokrasia_k": 295.0, "anamenomeni_ekdosi_katastasis": ekdosi_prin},
        headers={"X-Id-Xristi": "xristis_zwis", "X-Rolos": "ypefthynos_ypostiriksis_zwis"},
    )
    assert apantisi_proep.status_code == 200
    proep = apantisi_proep.json()
    assert proep["id_proepiskopisis"] is not None
    assert proep["zitoumeni"]["epithymiti_thermokrasia_k"] == 295.0
    # Q_meta - Q_prin = 0.2 * 500 * (295 - 213) - 0.2 * 500 * (293 - 213) = 8200 - 8000 = 200 W
    assert proep["epiptwsi"]["metavoli_w"] == pytest.approx(200.0, rel=1e-4)

    # 3. Επιβεβαίωση εντολής
    apantisi_entolis = pelatis_dokimwn.post(
        f"/api/v1/xwroi-katoikisis/{id_xwrou}/thermokrasia/entoles",
        json={
            "id_proepiskopisis": proep["id_proepiskopisis"],
            "anamenomeni_ekdosi_katastasis": ekdosi_prin,
        },
        headers={"X-Id-Xristi": "xristis_zwis", "X-Rolos": "ypefthynos_ypostiriksis_zwis"},
    )
    assert apantisi_entolis.status_code == 200
    entoli = apantisi_entolis.json()
    assert entoli["katastasi"] == "oloklirothike"
    assert entoli["epithymiti_thermokrasia_k"] == 295.0

    # 4. Επαλήθευση νέας κατάστασης (read-after-write)
    apantisi_meta = pelatis_dokimwn.get(f"/api/v1/xwroi-katoikisis/{id_xwrou}/katastasi")
    dedomena_meta = apantisi_meta.json()
    assert dedomena_meta["thermokrasia"]["epithymiti_k"] == 295.0
    assert dedomena_meta["ekdosi_katastasis"] == ekdosi_prin + 1


def test_thermokrasia_periptwseis_apotyxias(pelatis_dokimwn: TestClient):
    """TEST-11: Σενάρια σφαλμάτων θερμοκρασίας (άκυρο εύρος, stale preview, μη εξουσιοδοτημένος ρόλος)."""
    id_xwrou = "xwros_01"

    # 1. Θερμοκρασία εκτός ορίων (< 280 K)
    apantisi_xamilis = pelatis_dokimwn.post(
        f"/api/v1/xwroi-katoikisis/{id_xwrou}/thermokrasia/proepiskopisi",
        json={"epithymiti_thermokrasia_k": 250.0, "anamenomeni_ekdosi_katastasis": 1},
        headers={"X-Id-Xristi": "xristis_zwis"},
    )
    assert apantisi_xamilis.status_code == 422
    sfalma = apantisi_xamilis.json()["sfalma"]
    assert sfalma["kodikos"] == "AKYRI_THERMOKRATIA"

    # 2. Μη εξουσιοδοτημένος ρόλος (ο χειριστής πόρων δεν έχει δικαίωμα στη θερμοκρασία)
    apantisi_anarmodios = pelatis_dokimwn.post(
        f"/api/v1/xwroi-katoikisis/{id_xwrou}/thermokrasia/proepiskopisi",
        json={"epithymiti_thermokrasia_k": 294.0, "anamenomeni_ekdosi_katastasis": 1},
        headers={"X-Id-Xristi": "xristis_porwn", "X-Rolos": "ypefthynos_porwn"},
    )
    assert apantisi_anarmodios.status_code == 403
    assert apantisi_anarmodios.json()["sfalma"]["kodikos"] == "ANARMODIOS_XRISTIS"

    # 3. Stale version (ανυπόστατη έκδοση κατάστασης -> 409 conflict)
    apantisi_palias_proepiskopisis = pelatis_dokimwn.post(
        f"/api/v1/xwroi-katoikisis/{id_xwrou}/thermokrasia/proepiskopisi",
        json={"epithymiti_thermokrasia_k": 294.0, "anamenomeni_ekdosi_katastasis": 999},
        headers={"X-Id-Xristi": "xristis_zwis"},
    )
    assert apantisi_palias_proepiskopisis.status_code == 409
    assert apantisi_palias_proepiskopisis.json()["sfalma"]["kodikos"] == "PALIA_PROEPISKOPISI"
