"""Συμβόλαια αναγνώσεων, parent IDs και πραγματικά σφάλματα HTTP."""

import pytest


@pytest.mark.parametrize(
    "diadromi",
    [
        "/ygeia",
        "/metadedomena",
        "/synopsi",
        "/xwroi-katoikisis",
        "/xwroi-katoikisis/xwros_01/katastasi",
        "/xwroi-katoikisis/xwros_01/provlepsi-oxygonou",
        "/aisthitires",
        "/aisthitires/aisth_o2/metriseis",
        "/thermokipia",
        "/thermokipia/thermokipio_01/zwnes",
        "/energeia/katastasi",
        "/energeia/fortia",
        "/energeia/fwtovoltaika",
        "/energeia/syssoreftes",
        "/nero/dexamenes",
        "/nero/isozygio",
        "/nero/roes",
        "/oximata",
        "/oximata/rover_01/apostoles",
        "/kindynoi",
        "/synagermoi",
        "/dikaiwmata/metavivaseis",
        "/istoriko-elegxou",
        "/senaria/kataigida-skonis",
        "/senaria/kataigida_skonis_2026/xronologio",
    ],
)
def test_anagnwseis_exoun_egkyro_symvolaio(pelatis_dokimwn, diadromi):
    apantisi = pelatis_dokimwn.get("/api/v1" + diadromi)
    assert apantisi.status_code == 200, apantisi.text
    assert isinstance(apantisi.json(), (dict, list))


@pytest.mark.parametrize(
    "diadromi",
    [
        "/xwroi-katoikisis/agnwstos/katastasi",
        "/xwroi-katoikisis/agnwstos/provlepsi-oxygonou",
        "/aisthitires/agnwstos/metriseis",
        "/entoles/agnwsti",
        "/oximata/agnwsto/apostoles",
        "/senaria/agnwsto/xronologio",
        "/den-yparxei",
    ],
)
def test_anagnwseis_aniparktwn_ontotitwn(pelatis_dokimwn, diadromi):
    apantisi = pelatis_dokimwn.get("/api/v1" + diadromi)
    assert apantisi.status_code == 404
    assert "sfalma" in apantisi.json()


def test_aniparkto_goniko_den_ektelei_ardefsi(pelatis_dokimwn):
    stoixeio_pi = pelatis_dokimwn.post(
        "/api/v1/thermokipia/thermokipio_01/ardefsi/proepiskopisi",
        json={"id_zwnis": "zwni_01", "posotita_nerou_l": 100},
    ).json()
    stoixeio_alfa = pelatis_dokimwn.post(
        "/api/v1/thermokipia/agnwsto/ardefsi/programmata",
        json={"id_proepiskopisis": stoixeio_pi["id_proepiskopisis"]},
    )
    assert stoixeio_alfa.status_code in {404, 409}
    assert (
        pelatis_dokimwn.get("/api/v1/thermokipia/thermokipio_01/ardefsi/programmata").json() == []
    )


def test_epilogi_senariou_agnwstou_den_metavallei_fortia(pelatis_dokimwn):
    stoixeio_alfa = pelatis_dokimwn.post("/api/v1/senaria/agnwsto/apofaseis/proepiskopisi")
    assert stoixeio_alfa.status_code == 404
    assert pelatis_dokimwn.get("/api/v1/energeia/katastasi").json()["fortia"]["anavlita_kw"] == 4
