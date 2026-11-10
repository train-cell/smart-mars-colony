"""Δοκιμές διασύνδεσης: δικαιώματα, ολική επαναφορά αποτυχημένης εντολής και φυσική λογιστική."""

from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import select

from backend.app.montela import (
    Entoli,
    KatastasiProsomoiwsis,
    MetavivasiDikaiwmatos,
    OximaExerevnis,
    Proepiskopisi,
    Syssoreftis,
    Xristis,
)
from backend.app.pyrinas.rythmiseis import rythmiseis


def test_riti_taftotita_kai_eisodos_anenergou(pelatis_dokimwn, synedria_dokimwn):
    pelatis_dokimwn.headers.pop("X-Id-Xristi")
    for kefalides in [{}, {"X-Id-Xristi": "agnwstos"}]:
        apantisi = pelatis_dokimwn.post(
            "/api/v1/prosomoiwsi/vima", json={"lepta": 1}, headers=kefalides
        )
        assert apantisi.status_code == 401
        assert apantisi.json()["sfalma"]["id_aitimatos"] == apantisi.headers["X-Id-Aitimatos"]
    synedria_dokimwn.get(Xristis, "xristis_porwn").energos = False
    synedria_dokimwn.commit()
    assert (
        pelatis_dokimwn.post(
            "/api/v1/taftopoiisi/eisodos", json={"id_xristi": "xristis_porwn"}
        ).status_code
        == 401
    )


def test_metavivasi_pediou_efarmozetai_anakaleitai_kai_ligei(pelatis_dokimwn, synedria_dokimwn):
    pelatis = pelatis_dokimwn
    diadromi = "/api/v1/xwroi-katoikisis/xwros_01/thermokrasia/proepiskopisi"
    aitima = {"epithymiti_thermokrasia_k": 295, "anamenomeni_ekdosi_katastasis": 1}
    kefalides = {"X-Id-Xristi": "xristis_porwn"}
    assert pelatis.post(diadromi, json=aitima, headers=kefalides).status_code == 403
    aitima_metavivasis = {
        "id_paralipti": "xristis_porwn",
        "rolos": "ypefthynos_ypostiriksis_zwis",
        "pedio_efarmogis": "xwros_01",
        "diarkeia_wres": 1,
        "aitiologia": "Κάλυψη συγκεκριμένης βάρδιας",
    }
    egkrisi = pelatis.post("/api/v1/dikaiwmata/metavivaseis", json=aitima_metavivasis)
    assert egkrisi.status_code == 200, egkrisi.text
    assert pelatis.post(diadromi, json=aitima, headers=kefalides).status_code == 200
    assert (
        pelatis.post(
            diadromi.replace("xwros_01", "allo"), json=aitima, headers=kefalides
        ).status_code
        == 403
    )
    anagnwristiko = egkrisi.json()["id_metavivasis"]
    assert (
        pelatis.post(f"/api/v1/dikaiwmata/metavivaseis/{anagnwristiko}/anaklisi").status_code == 200
    )
    assert pelatis.post(diadromi, json=aitima, headers=kefalides).status_code == 403
    egkrisi = pelatis.post("/api/v1/dikaiwmata/metavivaseis", json=aitima_metavivasis)
    metavivasi = synedria_dokimwn.get(MetavivasiDikaiwmatos, egkrisi.json()["id_metavivasis"])
    metavivasi.xronos_liksis = datetime.now(timezone.utc) - timedelta(seconds=1)
    synedria_dokimwn.commit()
    assert pelatis.post(diadromi, json=aitima, headers=kefalides).status_code == 403
    assert (
        pelatis.post(
            "/api/v1/dikaiwmata/metavivaseis",
            json={**aitima_metavivasis, "rolos": "syntonistis_apoikias"},
        ).status_code
        == 403
    )


def test_metavivasi_dexamenis_kai_akyrosi_xwris_genika_pronomia(pelatis_dokimwn):
    pelatis = pelatis_dokimwn
    egkrisi = pelatis.post(
        "/api/v1/dikaiwmata/metavivaseis",
        json={
            "id_paralipti": "xristis_zwis",
            "rolos": "ypefthynos_porwn",
            "pedio_efarmogis": "dexameni_01",
            "diarkeia_wres": 1,
            "aitiologia": "Ελεγχόμενος κύκλος ανακύκλωσης",
        },
    )
    assert egkrisi.status_code == 200, egkrisi.text
    kefalides = {"X-Id-Xristi": "xristis_zwis"}
    proep = pelatis.post(
        "/api/v1/nero/anakyklwsi/proepiskopisi", headers=kefalides, json={"posotita_nerou_l": 100}
    )
    assert proep.status_code == 200, proep.text
    programma = pelatis.post(
        "/api/v1/nero/anakyklwsi/programmata",
        headers=kefalides,
        json={"id_proepiskopisis": proep.json()["id_proepiskopisis"]},
    )
    assert programma.status_code == 200, programma.text
    assert (
        pelatis.post(
            f"/api/v1/nero/anakyklwsi/programmata/{programma.json()['id_programmatos']}/akyrosi",
            headers=kefalides,
        ).status_code
        == 200
    )
    assert (
        pelatis.post(
            "/api/v1/thermokipia/thermokipio_01/ardefsi/proepiskopisi",
            headers=kefalides,
            json={"id_zwnis": "zwni_01", "posotita_nerou_l": 100},
        ).status_code
        == 403
    )


def test_apotyxia_apofasis_epanaferei_proepiskopisi_kai_istoriko(pelatis_dokimwn, synedria_dokimwn):
    pelatis = pelatis_dokimwn
    assert pelatis.post("/api/v1/senaria/kataigida-skonis/energopoiisi").status_code == 200
    proep = pelatis.post("/api/v1/senaria/kataigida-skonis/proepiskopisi").json()
    prin = len(synedria_dokimwn.scalars(select(Entoli)).all())
    apotyxia = pelatis.post(
        "/api/v1/senaria/kataigida_skonis_2026/apofaseis",
        json={
            "id_proepiskopisis": proep["id_proepiskopisis"],
            "epilogi": "anaklisi_oximatos",
            "aitiologia": "Δοκιμή επικίνδυνης ανάκλησης",
        },
    )
    assert apotyxia.status_code == 409, apotyxia.text
    assert synedria_dokimwn.get(Proepiskopisi, proep["id_proepiskopisis"]).katastasi == "energi"
    assert len(synedria_dokimwn.scalars(select(Entoli)).all()) == prin
    assert not synedria_dokimwn.get(KatastasiProsomoiwsis, 1).pausi_anavlitwn
    epityxia = pelatis.post(
        "/api/v1/senaria/kataigida_skonis_2026/apofaseis",
        json={
            "id_proepiskopisis": proep["id_proepiskopisis"],
            "epilogi": "pausi_anavlhtwn",
            "aitiologia": "Προστασία κρίσιμων φορτίων",
        },
    )
    assert epityxia.status_code == 200, epityxia.text


def test_fortisi_oximatos_logistiki_kai_pausi(pelatis_dokimwn, synedria_dokimwn):
    oxima = synedria_dokimwn.get(OximaExerevnis, "rover_01")
    oxima.apostasi_apo_vasi_km = 0
    oxima.katastasi_oximatos = "stasi"
    synedria_dokimwn.commit()
    apantisi = pelatis_dokimwn.post("/api/v1/prosomoiwsi/vima", json={"lepta": 30})
    assert apantisi.status_code == 200, apantisi.text
    synedria_dokimwn.refresh(oxima)
    assert oxima.energeia_kwh == pytest.approx(
        0.84
    )  # 0,8 + 0,2 × 0,5 × 90% − 0,1 × 0,5 kWh βοηθητικών.
    # Η φόρτιση αφαιρεί 0,1 kWh από την κοινή μπαταρία, επιπλέον του βασικού ελλείμματος 4,6 kWh.
    assert synedria_dokimwn.get(Syssoreftis, "syssoreftis_01").energeia_kwh == pytest.approx(25.3)
    istoriko = pelatis_dokimwn.get("/api/v1/energeia/istoriko")
    assert istoriko.status_code == 200, istoriko.text
    assert istoriko.json()[0]["logistiki"]["fortisi_oximatwn_kwh"] == pytest.approx(0.09)
    assert any(
        f["id_fortiou"] == "fortio_fortisis_rover_01"
        for f in istoriko.json()[0]["fortia_egkatastasewn"]
    )
    proep = pelatis_dokimwn.post(
        "/api/v1/energeia/periorismos-fortiwn/proepiskopisi",
        json={"pausi_anavlhtwn": True, "aitiologia": "Διατήρηση αποθέματος"},
    ).json()
    assert (
        pelatis_dokimwn.post(
            "/api/v1/energeia/periorismos-fortiwn/entoles",
            json={"id_proepiskopisis": proep["id_proepiskopisis"]},
        ).status_code
        == 200
    )
    assert pelatis_dokimwn.post("/api/v1/prosomoiwsi/vima", json={"lepta": 30}).status_code == 200
    synedria_dokimwn.refresh(oxima)
    assert oxima.energeia_kwh == pytest.approx(
        0.79
    )  # Η παύση φόρτισης δεν καταργεί το βοηθητικό φορτίο.


@pytest.mark.parametrize(
    "diadromi,soma",
    [
        ("/prosomoiwsi/vima", {"lepta": 1}),
        ("/prosomoiwsi/epanafora", {"epivevaiwsi": True}),
        ("/senaria/prokathorismena/diarroi_nerou/energopoiisi", None),
        ("/senaria/kataigida-skonis/energopoiisi", None),
    ],
)
def test_paragogi_apokleiei_ergaleia_epideiksis(pelatis_dokimwn, monkeypatch, diadromi, soma):
    monkeypatch.setattr(rythmiseis, "PERIVALLON", "paragogi")
    assert pelatis_dokimwn.post("/api/v1" + diadromi, json=soma).status_code == 403


def test_apokatastasi_aitias_kai_epanemfanisi_synagermou(pelatis_dokimwn):
    pelatis = pelatis_dokimwn

    def senergo(kodikos):
        apantisi = pelatis.post(f"/api/v1/senaria/prokathorismena/{kodikos}/energopoiisi")
        assert apantisi.status_code == 200, apantisi.text

    senergo("diarroi_nerou")
    synagermos = next(
        s for s in pelatis.get("/api/v1/synagermoi").json() if "διαρρο" in s["titlos"].lower()
    )
    diadromi = f"/api/v1/synagermoi/{synagermos['id_synagermou']}"
    assert pelatis.post(diadromi + "/anagnwrisi").status_code == 200
    assert (
        pelatis.post(
            diadromi + "/epilysi", json={"sxolio_epilysis": "Χωρίς αποκατάσταση"}
        ).status_code
        == 409
    )
    senergo("apokatastasi")
    assert (
        pelatis.post(
            diadromi + "/epilysi", json={"sxolio_epilysis": "Επαληθεύτηκε η στεγανότητα"}
        ).status_code
        == 200
    )
    senergo("diarroi_nerou")
    idio = next(
        s
        for s in pelatis.get("/api/v1/synagermoi").json()
        if s["id_synagermou"] == synagermos["id_synagermou"]
    )
    assert idio["katastasi"] == "energos" and idio["energi_aitia"]


def test_mideniki_energeia_den_oloklirwnei_fwtismo(pelatis_dokimwn, synedria_dokimwn):
    pelatis = pelatis_dokimwn
    proep = pelatis.post(
        "/api/v1/thermokipia/thermokipio_01/fwtismos/proepiskopisi",
        json={"id_zwnis": "zwni_01", "isxys_kw": 2, "diarkeia_wres": 1},
    ).json()
    programma = pelatis.post(
        "/api/v1/thermokipia/thermokipio_01/fwtismos/entoles",
        json={"id_proepiskopisis": proep["id_proepiskopisis"]},
    ).json()
    synedria_dokimwn.get(Syssoreftis, "syssoreftis_01").energeia_kwh = 0
    synedria_dokimwn.commit()
    assert pelatis.post("/api/v1/prosomoiwsi/vima", json={"lepta": 60}).status_code == 200
    apotelesma = next(
        p
        for p in pelatis.get("/api/v1/thermokipia/thermokipio_01/fwtismos/programmata").json()
        if p["id_programmatos"] == programma["id_programmatos"]
    )
    assert apotelesma["katastasi"] == "apetyxe"
    assert apotelesma["ektelestheisa_energeia_kwh"] == 0


def test_allagi_iliakwn_synthikwn_akyrwnei_proepiskopisi(pelatis_dokimwn):
    pelatis = pelatis_dokimwn
    proep = pelatis.post(
        "/api/v1/thermokipia/thermokipio_01/fwtismos/proepiskopisi",
        json={"id_zwnis": "zwni_01", "isxys_kw": 2, "diarkeia_wres": 1},
    ).json()
    assert (
        pelatis.post("/api/v1/senaria/prokathorismena/xamili_aktinovolia/energopoiisi").status_code
        == 200
    )
    assert (
        pelatis.post(
            "/api/v1/thermokipia/thermokipio_01/fwtismos/entoles",
            json={"id_proepiskopisis": proep["id_proepiskopisis"]},
        ).status_code
        == 409
    )


def test_nero_provlepsi_sevetai_mellontiko_xroniko_orizonta(pelatis_dokimwn):
    pelatis = pelatis_dokimwn
    proep = pelatis.post(
        "/api/v1/thermokipia/thermokipio_01/ardefsi/proepiskopisi",
        json={
            "id_zwnis": "zwni_01",
            "posotita_nerou_l": 100,
            "xronos_enarksis": "2026-11-12T12:00:00Z",
        },
    ).json()
    assert (
        pelatis.post(
            "/api/v1/thermokipia/thermokipio_01/ardefsi/programmata",
            json={"id_proepiskopisis": proep["id_proepiskopisis"]},
        ).status_code
        == 200
    )
    # Η δέσμευση παραμένει, η φυσική κατανάλωση της μεθεπόμενης ημέρας δεν ανήκει στο 24ωρο.
    isozygio = pelatis.get("/api/v1/nero/isozygio").json()
    assert isozygio["apothema"]["desmevmeno_l"] == 100
    assert isozygio["provlepsi_24h_l"] == pytest.approx(7620)


def test_paliotita_kindynwn_apokleiei_vevaiosi_asfaleias(pelatis_dokimwn, synedria_dokimwn):
    from backend.app.montela import ExwterikosKindynos

    kindynos = synedria_dokimwn.scalar(select(ExwterikosKindynos))
    kindynos.xronos_katagrafis -= timedelta(hours=1)
    synedria_dokimwn.commit()
    proep = pelatis_dokimwn.post("/api/v1/oximata/rover_01/anaklisi/proepiskopisi")
    assert proep.status_code == 200, proep.text
    assert proep.json()["perivallon"]["poiotita"] == "palio"
    assert not proep.json()["synolika_asfalis_epistrofi"]


def test_id_aitimatos_kai_istoriko_sysxetizontai(pelatis_dokimwn):
    pelatis = pelatis_dokimwn
    proep = pelatis.post(
        "/api/v1/xwroi-katoikisis/xwros_01/thermokrasia/proepiskopisi",
        json={"epithymiti_thermokrasia_k": 295, "anamenomeni_ekdosi_katastasis": 1},
    ).json()
    apantisi = pelatis.post(
        "/api/v1/xwroi-katoikisis/xwros_01/thermokrasia/entoles",
        headers={"X-Id-Aitimatos": "aitima-elegxou-1"},
        json={"id_proepiskopisis": proep["id_proepiskopisis"], "anamenomeni_ekdosi_katastasis": 1},
    )
    assert apantisi.status_code == 200, apantisi.text
    assert apantisi.headers["X-Id-Aitimatos"] == "aitima-elegxou-1"
    assert any(
        eggrafi["id_aitimatos"] == "aitima-elegxou-1"
        for eggrafi in pelatis.get("/api/v1/istoriko-elegxou").json()
    )


def test_aprovlepto_sfalma_diatirei_anagnwristiko_xwris_dedomena(pelatis_dokimwn, monkeypatch):
    from backend.app.ypiresies.ypiresia_porwn import YpiresiaPorwn

    def apotyxia(self):
        raise RuntimeError("mi_dimosio_soma_aitimatos")

    monkeypatch.setattr(YpiresiaPorwn, "pare_katastasi_energeias", apotyxia)
    apantisi = pelatis_dokimwn.get(
        "/api/v1/energeia/katastasi", headers={"X-Id-Aitimatos": "aitima-sfalmatos"}
    )
    assert apantisi.status_code == 500
    assert apantisi.headers["X-Id-Aitimatos"] == "aitima-sfalmatos"
    assert apantisi.json()["sfalma"]["id_aitimatos"] == "aitima-sfalmatos"
    assert "mi_dimosio_soma" not in apantisi.text
