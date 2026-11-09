"""Δοκιμές ενοποίησης για συναγερμούς: αναγνώριση vs επίλυση και deduplication (TEST-14, TEST-24)."""

from fastapi.testclient import TestClient


def test_alert_acknowledge_vs_resolve(pelatis_dokimwn: TestClient):
    """TEST-14 & TEST-24: Η αναγνώριση ΔΕΝ επιλύει τον συναγερμό. Η επίλυση απαιτεί αιτιολόγηση."""
    # 1. Ενεργοποίηση καταιγίδας που παράγει συναγερμό
    pelatis_dokimwn.post(
        "/api/v1/senaria/kataigida-skonis/energopoiisi",
        headers={"X-Id-Xristi": "syntonistis"},
    )

    # 2. Ανάκτηση ενεργών συναγερμών
    apantisi = pelatis_dokimwn.get("/api/v1/synagermoi?katastasi=energos")
    assert apantisi.status_code == 200
    synagermoi = apantisi.json()
    assert len(synagermoi) >= 1
    id_synagermou = synagermoi[0]["id_synagermou"]

    # 3. Αναγνώριση συναγερμού (Acknowledge)
    apantisi_ack = pelatis_dokimwn.post(
        f"/api/v1/synagermoi/{id_synagermou}/anagnwrisi",
        headers={"X-Id-Xristi": "xristis_porwn"},
    )
    assert apantisi_ack.status_code == 200
    assert apantisi_ack.json()["katastasi"] == "anagnwrismenos"

    # Επαλήθευση ότι ΔΕΝ έχει επιλυθεί
    apantisi_check = pelatis_dokimwn.get("/api/v1/synagermoi?katastasi=epilymenos")
    assert not any(s["id_synagermou"] == id_synagermou for s in apantisi_check.json())

    # 4. Απόπειρα επίλυσης χωρίς αιτιολόγηση (απορρίπτεται)
    apantisi_fail = pelatis_dokimwn.post(
        f"/api/v1/synagermoi/{id_synagermou}/epilysi",
        json={"sxolio_epilysis": ""},
        headers={"X-Id-Xristi": "xristis_porwn"},
    )
    assert apantisi_fail.status_code == 422  # validation failure

    # 5. Έγκυρη επίλυση με τεκμηριωμένο σχόλιο
    apantisi_resolve = pelatis_dokimwn.post(
        f"/api/v1/synagermoi/{id_synagermou}/epilysi",
        json={"sxolio_epilysis": "Εφαρμόστηκε παύση αναβλητών φορτίων και η καταιγίδα εξασθένησε."},
        headers={"X-Id-Xristi": "xristis_porwn"},
    )
    assert apantisi_resolve.status_code == 200
    assert apantisi_resolve.json()["katastasi"] == "epilymenos"
