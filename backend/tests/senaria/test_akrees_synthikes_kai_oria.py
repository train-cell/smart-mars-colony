"""Ακραίες είσοδοι και έλεγχοι αβεβαιότητας των δημόσιων συμβολαίων."""

import math

import pytest

from backend.app.fysika_montela.fysika_montela import (
    ypologise_apothema_kai_autonomia_oxygonou,
    ypologise_energeia_kinisis_oximatos,
)


@pytest.mark.parametrize("timi", ["Infinity", "NaN", -1, 0])
def test_mi_egkyri_isxys_fwtismou_den_apothikevetai(pelatis_dokimwn, timi):
    stoixeio_alfa = pelatis_dokimwn.post(
        "/api/v1/thermokipia/thermokipio_01/fwtismos/proepiskopisi",
        json={"id_zwnis": "zwni_01", "isxys_kw": timi},
    )
    assert stoixeio_alfa.status_code == 422, stoixeio_alfa.text
    assert (
        pelatis_dokimwn.get("/api/v1/thermokipia/thermokipio_01/fwtismos/programmata").json() == []
    )


def test_yperxeilisi_eisodou_dinei_sfalma_epikyrwsis(pelatis_dokimwn):
    stoixeio_alfa = pelatis_dokimwn.post(
        "/api/v1/prosomoiwsi/vima",
        content='{"lepta":1e309}',
        headers={"Content-Type": "application/json"},
    )
    assert stoixeio_alfa.status_code == 422
    assert stoixeio_alfa.json()["sfalma"]["kodikos"] == "AKYRI_TIMI"


def test_oxygono_katw_apo_katwfli_me_paragwgi_paramenei_kindynos():
    apotelesma = ypologise_apothema_kai_autonomia_oxygonou(100, 293, 10000, 16000, 6, 0.04, 0.3)
    assert apotelesma[2] == 0
    assert apotelesma[3] == "katwfli_paraviasmeno"


@pytest.mark.parametrize(
    "klisi", [math.pi, -math.pi, math.pi / 2, -math.pi / 2, math.inf, math.nan]
)
def test_anefikti_klisi_aporriptetai(klisi):
    with pytest.raises(ValueError):
        ypologise_energeia_kinisis_oximatos(1000, 1000, klisi_rad=klisi)


def test_epanafora_akyronei_palies_proepiskopiseis(pelatis_dokimwn):
    stoixeio_pi = pelatis_dokimwn.post(
        "/api/v1/thermokipia/thermokipio_01/ardefsi/proepiskopisi",
        json={"id_zwnis": "zwni_01", "posotita_nerou_l": 100},
    ).json()
    assert (
        pelatis_dokimwn.post(
            "/api/v1/prosomoiwsi/epanafora", json={"epivevaiwsi": True}
        ).status_code
        == 200
    )
    stoixeio_alfa = pelatis_dokimwn.post(
        "/api/v1/thermokipia/thermokipio_01/ardefsi/programmata",
        json={"id_proepiskopisis": stoixeio_pi["id_proepiskopisis"]},
    )
    assert stoixeio_alfa.status_code in {404, 409}
