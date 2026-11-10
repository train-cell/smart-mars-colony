"""Δοκιμές ενοποίησης για συναγερμούς: αναγνώριση vs επίλυση και deduplication (TEST-14, TEST-24)."""

from fastapi.testclient import TestClient


def test_synagermos_anagnwrisi_kai_epilysi(pelatis_dokimwn: TestClient):
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
    id_synagermou = next(
        stoixeio_sigma["id_synagermou"]
        for stoixeio_sigma in synagermoi
        if stoixeio_sigma["yposystima"] == "poroi"
    )

    # 3. Αναγνώριση συναγερμού (Acknowledge)
    apantisi_anagnwrisis = pelatis_dokimwn.post(
        f"/api/v1/synagermoi/{id_synagermou}/anagnwrisi",
        headers={"X-Id-Xristi": "xristis_porwn"},
    )
    assert apantisi_anagnwrisis.status_code == 200
    assert apantisi_anagnwrisis.json()["katastasi"] == "anagnwrismenos"

    # Επαλήθευση ότι ΔΕΝ έχει επιλυθεί
    apantisi_elegxou = pelatis_dokimwn.get("/api/v1/synagermoi?katastasi=epilymenos")
    assert not any(
        stoixeio_sigma["id_synagermou"] == id_synagermou
        for stoixeio_sigma in apantisi_elegxou.json()
    )

    # 4. Απόπειρα επίλυσης χωρίς αιτιολόγηση (απορρίπτεται)
    apantisi_apotyxias = pelatis_dokimwn.post(
        f"/api/v1/synagermoi/{id_synagermou}/epilysi",
        json={"sxolio_epilysis": ""},
        headers={"X-Id-Xristi": "xristis_porwn"},
    )
    assert apantisi_apotyxias.status_code == 422  # validation failure

    # Η αιτία παραμένει ορατή μετά την αναγνώριση.
    assert any(
        stoixeio_sigma["id_synagermou"] == id_synagermou
        for stoixeio_sigma in pelatis_dokimwn.get("/api/v1/synopsi").json()["energoi_synagermoi"]
    )
    assert (
        pelatis_dokimwn.post(
            f"/api/v1/synagermoi/{id_synagermou}/epilysi",
            json={"sxolio_epilysis": "Απλό σχόλιο χωρίς αποκατάσταση"},
            headers={"X-Id-Xristi": "xristis_porwn"},
        ).status_code
        == 409
    )
    assert (
        pelatis_dokimwn.post(
            "/api/v1/senaria/prokathorismena/apokatastasi/energopoiisi"
        ).status_code
        == 200
    )
    # 5. Έγκυρη επίλυση μετά την πραγματική αποκατάσταση
    apantisi_epilysis = pelatis_dokimwn.post(
        f"/api/v1/synagermoi/{id_synagermou}/epilysi",
        json={"sxolio_epilysis": "Εφαρμόστηκε παύση αναβλητών φορτίων και η καταιγίδα εξασθένησε."},
        headers={"X-Id-Xristi": "xristis_porwn"},
    )
    assert apantisi_epilysis.status_code == 200
    assert apantisi_epilysis.json()["katastasi"] == "epilymenos"
