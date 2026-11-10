"""Πραγματικές ροές rover με προεπισκόπηση και ειλικρινή επιβεβαίωση."""

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.app.montela.apostoles import OximaExerevnis


def test_asfalis_stasi_proepiskopisi_kai_ektelesi(pelatis_dokimwn: TestClient):
    kefalides = {"X-Id-Xristi": "xristis_apostolwn"}
    diadromi = "/api/v1/oximata/rover_01/asfalis-stasi"
    proep = pelatis_dokimwn.post(diadromi + "/proepiskopisi", headers=kefalides)
    assert proep.status_code == 200
    assert proep.json()["protinomeni_drasi"] == "asfalis_stasi"
    apantisi = pelatis_dokimwn.post(
        diadromi + "/entoles",
        headers=kefalides,
        json={"id_proepiskopisis": proep.json()["id_proepiskopisis"]},
    )
    assert apantisi.status_code == 200
    assert apantisi.json()["katastasi_entolis"] == "oloklirothike"
    assert (
        pelatis_dokimwn.get("/api/v1/oximata/rover_01/apostoles").json()["kinisi"]["katastasi"]
        == "asfalis_stasi"
    )


def test_ypovathmismeni_epikoinwnia_afinei_avevaio(
    pelatis_dokimwn: TestClient, synedria_dokimwn: Session
):
    oxima = synedria_dokimwn.get(OximaExerevnis, "rover_01")
    oxima.katastasi_epikoinwnias = "ypovathmismeni"
    synedria_dokimwn.commit()
    kefalides = {"X-Id-Xristi": "xristis_apostolwn"}
    diadromi = "/api/v1/oximata/rover_01/anaklisi"
    proep = pelatis_dokimwn.post(diadromi + "/proepiskopisi", headers=kefalides)
    assert proep.status_code == 200
    apantisi = pelatis_dokimwn.post(
        diadromi + "/entoles",
        headers=kefalides,
        json={"id_proepiskopisis": proep.json()["id_proepiskopisis"]},
    )
    assert apantisi.status_code == 200
    assert apantisi.json()["katastasi_entolis"] == "avevaio"
    assert oxima.katastasi_oximatos == "stasi"
