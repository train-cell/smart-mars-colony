"""Πραγματικές κοινές ροές πόρων, εξοπλισμού και ιστορικού."""

from datetime import datetime, timedelta

import pytest


def test_ardefsi_api_xronos_kai_mi_dipli_katanalwsi(pelatis_dokimwn):
    stoixeio_pi = pelatis_dokimwn.post(
        "/api/v1/thermokipia/thermokipio_01/ardefsi/proepiskopisi",
        json={
            "id_zwnis": "zwni_01",
            "posotita_nerou_l": 100,
            "diarkeia_lepta": 30,
            "xronos_enarksis": "2026-11-10T12:30:00Z",
        },
    )
    assert stoixeio_pi.status_code == 200, stoixeio_pi.text
    stoixeio_alfa = pelatis_dokimwn.post(
        "/api/v1/thermokipia/thermokipio_01/ardefsi/programmata",
        json={"id_proepiskopisis": stoixeio_pi.json()["id_proepiskopisis"]},
    )
    assert stoixeio_alfa.status_code == 200, stoixeio_alfa.text
    prin = pelatis_dokimwn.get("/api/v1/nero/dexamenes").json()

    def ogkos_dexamenis(dedomena):
        return next(
            dexameni
            for dexameni in dedomena["dexamenes"]
            if dexameni["id_dexamenis"] == "dexameni_01"
        )["trexwn_ogkos_l"]

    assert ogkos_dexamenis(prin) == 7500
    assert pelatis_dokimwn.post("/api/v1/prosomoiwsi/vima", json={"lepta": 30}).status_code == 200
    assert ogkos_dexamenis(pelatis_dokimwn.get("/api/v1/nero/dexamenes").json()) == pytest.approx(
        7502.5
    )
    stoixeio_alfa = pelatis_dokimwn.post("/api/v1/prosomoiwsi/vima", json={"lepta": 30})
    assert stoixeio_alfa.status_code == 200, stoixeio_alfa.text
    assert ogkos_dexamenis(pelatis_dokimwn.get("/api/v1/nero/dexamenes").json()) == pytest.approx(
        7405
    )
    assert (
        pelatis_dokimwn.get("/api/v1/thermokipia/thermokipio_01/ardefsi/programmata").json()[0][
            "katastasi"
        ]
        == "oloklirothike"
    )


def test_anakyklwsi_api_diatirei_maza(pelatis_dokimwn):
    stoixeio_pi = pelatis_dokimwn.post(
        "/api/v1/nero/anakyklwsi/proepiskopisi", json={"posotita_nerou_l": 100, "apodosi": 0.85}
    )
    assert stoixeio_pi.status_code == 200, stoixeio_pi.text
    stoixeio_alfa = pelatis_dokimwn.post(
        "/api/v1/nero/anakyklwsi/programmata",
        json={"id_proepiskopisis": stoixeio_pi.json()["id_proepiskopisis"]},
    )
    assert stoixeio_alfa.status_code == 200, stoixeio_alfa.text
    assert pelatis_dokimwn.post("/api/v1/prosomoiwsi/vima", json={"lepta": 60}).status_code == 200
    dexamenes = {
        x["id_dexamenis"]: x["trexwn_ogkos_l"]
        for x in pelatis_dokimwn.get("/api/v1/nero/dexamenes").json()["dexamenes"]
    }
    assert dexamenes["dexameni_gkrizou"] == pytest.approx(900)
    assert dexamenes["dexameni_01"] == pytest.approx(7590)


def test_syskevi_ypostiriksis_zwis_proepiskopisi_epivevaiwsi(pelatis_dokimwn):
    diadromi = "/api/v1/xwroi-katoikisis/xwros_01/syskeves/sysk_scrubber"
    stoixeio_pi = pelatis_dokimwn.post(
        diadromi + "/proepiskopisi",
        json={"energopoiisi": False, "aitiologia": "Ελεγχόμενη συντήρηση"},
    )
    assert stoixeio_pi.status_code == 200, stoixeio_pi.text
    stoixeio_alfa = pelatis_dokimwn.post(
        diadromi + "/entoles", json={"id_proepiskopisis": stoixeio_pi.json()["id_proepiskopisis"]}
    )
    assert stoixeio_alfa.status_code == 200, stoixeio_alfa.text
    assert stoixeio_alfa.json()["katastasi_syskevis"] == "anenergi"
    assert any(x["energi_aitia"] for x in pelatis_dokimwn.get("/api/v1/synagermoi").json())
    assert any(
        x["energeia"] == "rythmisi_syskevis"
        for x in pelatis_dokimwn.get("/api/v1/istoriko-elegxou").json()
    )


def test_xronos_metrisewn_me_metatopisi_kai_poiotita(pelatis_dokimwn):
    stoixeio_alfa = pelatis_dokimwn.get("/api/v1/aisthitires/aisth_o2/metriseis").json()[0]
    assert datetime.fromisoformat(
        stoixeio_alfa["xronos_metrisis"].replace("Z", "+00:00")
    ).utcoffset() == timedelta(0)
    assert stoixeio_alfa["pigi"] == "prosomoiwmenos_aisthitiras"
    assert stoixeio_alfa["poiotita"] == "egkyro"
    assert "avevaiotita" in stoixeio_alfa
