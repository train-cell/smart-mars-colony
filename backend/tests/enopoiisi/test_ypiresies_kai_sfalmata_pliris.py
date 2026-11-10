"""Προστασία μόνιμων προεπισκοπήσεων, στόχων και ολοκληρωμένων εντολών."""

import pytest

from backend.app.montela import Aisthitiras, MetrisiAisthitira


def _proepiskopisi(pelatis, timi=295, ekdosi=1):
    return pelatis.post(
        "/api/v1/xwroi-katoikisis/xwros_01/thermokrasia/proepiskopisi",
        json={"epithymiti_thermokrasia_k": timi, "anamenomeni_ekdosi_katastasis": ekdosi},
    )


def test_palia_proepiskopisi_meta_kataigida_aporriptetai(pelatis_dokimwn):
    stoixeio_pi = _proepiskopisi(pelatis_dokimwn).json()
    assert pelatis_dokimwn.post("/api/v1/senaria/kataigida-skonis/energopoiisi").status_code == 200
    ekdosi = pelatis_dokimwn.get("/api/v1/xwroi-katoikisis").json()[0]["ekdosi_katastasis"]
    stoixeio_alfa = pelatis_dokimwn.post(
        "/api/v1/xwroi-katoikisis/xwros_01/thermokrasia/entoles",
        json={
            "id_proepiskopisis": stoixeio_pi["id_proepiskopisis"],
            "anamenomeni_ekdosi_katastasis": ekdosi,
        },
    )
    assert stoixeio_alfa.status_code == 409
    assert pelatis_dokimwn.get("/api/v1/energeia/fortia").json()[0] is not None


def test_oloklirwmeni_entoli_den_akyronetai(pelatis_dokimwn):
    stoixeio_pi = _proepiskopisi(pelatis_dokimwn).json()
    stoixeio_alfa = pelatis_dokimwn.post(
        "/api/v1/xwroi-katoikisis/xwros_01/thermokrasia/entoles",
        json={
            "id_proepiskopisis": stoixeio_pi["id_proepiskopisis"],
            "anamenomeni_ekdosi_katastasis": 1,
        },
    )
    assert stoixeio_alfa.status_code == 200, stoixeio_alfa.text
    assert (
        pelatis_dokimwn.post(
            "/api/v1/entoles/" + stoixeio_alfa.json()["id_entolis"] + "/akyrosi"
        ).status_code
        == 409
    )
    x = pelatis_dokimwn.get("/api/v1/xwroi-katoikisis/xwros_01/katastasi").json()
    assert x["thermokrasia"]["epithymiti_k"] == 295
    assert x["thermokrasia"]["eswteriki_k"] == 293
    assert pelatis_dokimwn.post("/api/v1/prosomoiwsi/vima", json={"lepta": 15}).status_code == 200
    x = pelatis_dokimwn.get("/api/v1/xwroi-katoikisis/xwros_01/katastasi").json()
    assert 293 < x["thermokrasia"]["eswteriki_k"] < 295


@pytest.mark.parametrize("eidos", ["apousia", "palia", "ektos_leitourgias"])
def test_mi_egkyri_pigi_apokleiei_proepiskopisi(pelatis_dokimwn, synedria_dokimwn, eidos):
    if eidos == "apousia":
        synedria_dokimwn.query(MetrisiAisthitira).delete()
    elif eidos == "palia":
        synedria_dokimwn.query(MetrisiAisthitira).update({"einai_palio": True})
    else:
        synedria_dokimwn.get(Aisthitiras, "aisth_thermokrasia_exw").katastasi = "ektos_leitourgias"
    synedria_dokimwn.commit()
    assert _proepiskopisi(pelatis_dokimwn).status_code == 503


def test_mia_proepiskopisi_den_ekteleitai_dyo_fores(pelatis_dokimwn):
    stoixeio_pi = _proepiskopisi(pelatis_dokimwn).json()
    stoixeio_alfa = pelatis_dokimwn.post(
        "/api/v1/xwroi-katoikisis/xwros_01/thermokrasia/entoles",
        json={
            "id_proepiskopisis": stoixeio_pi["id_proepiskopisis"],
            "anamenomeni_ekdosi_katastasis": 1,
        },
    )
    assert stoixeio_alfa.status_code == 200
    stoixeio_vita = pelatis_dokimwn.post(
        "/api/v1/xwroi-katoikisis/xwros_01/thermokrasia/entoles",
        json={
            "id_proepiskopisis": stoixeio_pi["id_proepiskopisis"],
            "anamenomeni_ekdosi_katastasis": 2,
        },
    )
    assert stoixeio_vita.status_code == 409
