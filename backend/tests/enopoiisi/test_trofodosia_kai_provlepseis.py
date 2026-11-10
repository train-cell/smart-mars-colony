"""Ανεξάρτητα αριθμητικά αποτελέσματα για τα κενά R1–R3 της τελικής αποτίμησης."""

from datetime import timedelta

import pytest
from sqlalchemy import select

from backend.app.montela import (
    Aisthitiras,
    Fwtovoltaiko,
    KatastasiProsomoiwsis,
    MetrisiAisthitira,
    Syssoreftis,
    XwrosKatoikisis,
)
from backend.app.ypiresies.metriseis_kai_poiotita import ananeose_metriseis


def rythmise_paragwgi(synedria, isxys_kw, energeia_kwh=0):
    """Προετοιμάζει συνεπή φυσική κατάσταση και αντίστοιχες προσομοιωμένες μετρήσεις."""
    pv = synedria.get(Fwtovoltaiko, "pv_01")
    pv.aktinovolia_w_m2 = (
        isxys_kw * 1000 / (pv.apodosi_eta * pv.epifaneia_m2 * pv.syntelestis_epikathisis_f)
    )
    pv.isxys_paragwgis_w = isxys_kw * 1000
    synedria.get(Syssoreftis, "syssoreftis_01").energeia_kwh = energeia_kwh
    ananeose_metriseis(synedria, synedria.get(KatastasiProsomoiwsis, 1).xronos_prosomoiwsis)
    synedria.commit()


def test_mideniki_trofodosia_midenizei_kai_provlepomeni_paragwgi(pelatis_dokimwn, synedria_dokimwn):
    rythmise_paragwgi(synedria_dokimwn, 0)
    provlepsi = pelatis_dokimwn.get("/api/v1/xwroi-katoikisis/xwros_01/provlepsi-oxygonou")
    assert provlepsi.status_code == 200, provlepsi.text
    dedomena = provlepsi.json()
    assert dedomena["rythmos_paragwgis_kg_h"] == 0
    assert dedomena["synoliki_autonomia_me_dexameni_wres"] == pytest.approx(
        (dedomena["maza_xrisimou_oxygonou_kg"] + 500) / 0.16, abs=0.1
    )
    vima = pelatis_dokimwn.post("/api/v1/prosomoiwsi/vima", json={"lepta": 5}).json()
    assert vima["apotelesmata"][0]["ypostiriksi_zwis"][0]["paragwgi_oxygonou_kg"] == 0


def test_krisima_proigountai_anavlitwn_me_eparki_iliaki_isxy(pelatis_dokimwn, synedria_dokimwn):
    rythmise_paragwgi(synedria_dokimwn, 12)
    vima = pelatis_dokimwn.post("/api/v1/prosomoiwsi/vima", json={"lepta": 5})
    assert vima.status_code == 200, vima.text
    assert synedria_dokimwn.get(
        XwrosKatoikisis, "xwros_01"
    ).thermokrasia_eswteriki_k == pytest.approx(293)
    zwi = vima.json()["apotelesmata"][0]["ypostiriksi_zwis"][0]
    assert zwi["paragwgi_oxygonou_kg"] == pytest.approx(0.1 / 12)


def test_peperasmeni_mpataria_den_dinei_aperioristi_paragwgi_o2(pelatis_dokimwn, synedria_dokimwn):
    rythmise_paragwgi(synedria_dokimwn, 0, 1.4)
    dedomena = pelatis_dokimwn.get("/api/v1/xwroi-katoikisis/xwros_01/provlepsi-oxygonou").json()
    # 14 kW ζήτηση: η μπαταρία επαρκεί 0,1 h. Το O₂ αντικαθιστά 0,01 kg κατανάλωσης.
    anamenomeno = (dedomena["maza_xrisimou_oxygonou_kg"] + 500 + 0.01) / 0.16
    assert dedomena["synoliki_autonomia_me_dexameni_wres"] == pytest.approx(anamenomeno, abs=0.1)
    assert dedomena["trofodosia"]["diarkeia_plirous_trofodosias_wres"] == pytest.approx(0.1)


@pytest.mark.parametrize("katastasi", ["ektos_leitourgias", "palio"])
def test_energeiaki_pigi_apaiteitai_gia_thermiki_proepiskopisi(
    pelatis_dokimwn, synedria_dokimwn, katastasi
):
    if katastasi == "palio":
        for metrisi in synedria_dokimwn.scalars(
            select(MetrisiAisthitira).where(MetrisiAisthitira.id_aisthitira == "aisth_aktinovolia")
        ):
            metrisi.xronos_metrisis -= timedelta(hours=1)
    else:
        synedria_dokimwn.get(Aisthitiras, "aisth_aktinovolia").katastasi = katastasi
    synedria_dokimwn.commit()
    apantisi = pelatis_dokimwn.post(
        "/api/v1/xwroi-katoikisis/xwros_01/thermokrasia/proepiskopisi",
        json={"epithymiti_thermokrasia_k": 295, "anamenomeni_ekdosi_katastasis": 1},
    )
    assert apantisi.status_code == 503, apantisi.text


def test_pv_apantisi_periexei_pigi_xrono_kai_poiotita(pelatis_dokimwn):
    dedomena = pelatis_dokimwn.get("/api/v1/energeia/fwtovoltaika").json()[0]
    assert dedomena["poiotita"] == "egkyro"
    assert dedomena["xronos_metrisis"].endswith(("Z", "+00:00"))
    assert dedomena["metriseis"]["aktinovolia"]["pigi"] == "prosomoiwmenos_aisthitiras"
    assert dedomena["metriseis"]["skoni"]["monada"] == "syntelestis"


def test_mpataria_eksantleitai_mesa_sto_vima_me_idia_paragwgi_provlepsis(
    pelatis_dokimwn, synedria_dokimwn
):
    # 0,14 kWh / 14 kW = 0,01 h = 36 s πλήρους τροφοδοσίας.
    rythmise_paragwgi(synedria_dokimwn, 0, 0.14)
    dedomena = pelatis_dokimwn.post("/api/v1/prosomoiwsi/vima", json={"lepta": 5}).json()
    poroi = dedomena["apotelesmata"][0]["poroi"]
    zwi = dedomena["apotelesmata"][0]["ypostiriksi_zwis"]
    assert sum(x["paragwgi_oxygonou_kg"] for x in zwi) == pytest.approx(0.001, abs=1e-8)
    assert len(poroi["katanomes"]) == 2
    assert poroi["katanalwsi_kwh"] == pytest.approx(0.14)
    assert synedria_dokimwn.get(Syssoreftis, "syssoreftis_01").energeia_kwh == pytest.approx(
        0, abs=1e-8
    )


@pytest.mark.parametrize("isxys_kw,energeia_kwh", [(0, 0.14), (12, 0), (30, 30)])
def test_energeiako_isozygio_den_dimiourgei_energeia(
    pelatis_dokimwn, synedria_dokimwn, isxys_kw, energeia_kwh
):
    rythmise_paragwgi(synedria_dokimwn, isxys_kw, energeia_kwh)
    poroi = pelatis_dokimwn.post("/api/v1/prosomoiwsi/vima", json={"lepta": 5}).json()[
        "apotelesmata"
    ][0]["poroi"]
    assert poroi["paragwgi_kwh"] + poroi["ekfortisi_syssoreftwn_kwh"] == pytest.approx(
        poroi["katanalwsi_kwh"]
        + poroi["fortisi_syssoreftwn_kwh"]
        + poroi["perissevma_mi_apothikevmeno_kwh"],
        abs=3e-8,
    )
    assert poroi["zitisi_energeias_kwh"] == pytest.approx(
        poroi["katanalwsi_kwh"] + poroi["mi_kalyptomeni_energeia_kwh"], abs=3e-8
    )


def test_ypovathmismeni_iliaki_pigi_dinei_syntiritiki_provlepsi(pelatis_dokimwn, synedria_dokimwn):
    rythmise_paragwgi(synedria_dokimwn, 30)
    synedria_dokimwn.get(Aisthitiras, "aisth_aktinovolia").katastasi = "ektos_leitourgias"
    synedria_dokimwn.commit()
    dedomena = pelatis_dokimwn.get("/api/v1/xwroi-katoikisis/xwros_01/provlepsi-oxygonou").json()
    assert dedomena["rythmos_paragwgis_kg_h"] == 0
    assert dedomena["trofodosia"]["poiotita_iliakis_pigis"] == "apousia"
    assert any("μηδενική ηλιακή" in x for x in dedomena["proeidopoiiseis"])
    assert pelatis_dokimwn.get("/api/v1/energeia/fwtovoltaika").json()[0]["poiotita"] == "apousia"


@pytest.mark.parametrize("allagi,anamenomenos_kwdikos", [("pv", 409), ("aisthitiras", 503)])
def test_energeiaki_allagi_apokleiei_palia_thermiki_epivevaiwsi(
    pelatis_dokimwn, synedria_dokimwn, allagi, anamenomenos_kwdikos
):
    proep = pelatis_dokimwn.post(
        "/api/v1/xwroi-katoikisis/xwros_01/thermokrasia/proepiskopisi",
        json={"epithymiti_thermokrasia_k": 295, "anamenomeni_ekdosi_katastasis": 1},
    ).json()
    if allagi == "pv":
        synedria_dokimwn.get(Fwtovoltaiko, "pv_01").aktinovolia_w_m2 = 100
    else:
        synedria_dokimwn.get(Aisthitiras, "aisth_skoni").katastasi = "ektos_leitourgias"
    synedria_dokimwn.commit()
    apantisi = pelatis_dokimwn.post(
        "/api/v1/xwroi-katoikisis/xwros_01/thermokrasia/entoles",
        json={"id_proepiskopisis": proep["id_proepiskopisis"], "anamenomeni_ekdosi_katastasis": 1},
    )
    assert apantisi.status_code == anamenomenos_kwdikos, apantisi.text
    assert synedria_dokimwn.get(XwrosKatoikisis, "xwros_01").epithymiti_thermokrasia_k == 293


def test_energeiakes_anagnwseis_xwris_parenergeies(pelatis_dokimwn, synedria_dokimwn):
    from sqlalchemy import func

    from backend.app.montela import EnergeiakoFortio

    prin = (
        synedria_dokimwn.scalar(select(func.count()).select_from(MetrisiAisthitira)),
        synedria_dokimwn.scalar(select(func.count()).select_from(EnergeiakoFortio)),
    )
    for diadromi in (
        "/api/v1/energeia/katastasi",
        "/api/v1/energeia/fortia",
        "/api/v1/xwroi-katoikisis/xwros_01/provlepsi-oxygonou",
    ):
        apantisi = pelatis_dokimwn.get(diadromi)
        assert apantisi.status_code == 200, apantisi.text
    meta = (
        synedria_dokimwn.scalar(select(func.count()).select_from(MetrisiAisthitira)),
        synedria_dokimwn.scalar(select(func.count()).select_from(EnergeiakoFortio)),
    )
    assert prin == meta
    assert synedria_dokimwn.get(Syssoreftis, "syssoreftis_01").energeia_kwh == 30


@pytest.mark.parametrize("diarkeia,iliaki_kw,anamenomeni", [(30, 0, False), (0, 12, True)])
def test_ikanopoiimeni_katanalwsi_o2_elegxei_kai_teliki_pigi(
    pelatis_dokimwn, synedria_dokimwn, diarkeia, iliaki_kw, anamenomeni
):
    from backend.app.montela import ApothemaOxygonou

    synedria_dokimwn.scalar(select(ApothemaOxygonou)).rythmos_paragwgis_kg_h = 0.2
    rythmise_paragwgi(synedria_dokimwn, iliaki_kw, diarkeia)
    dedomena = pelatis_dokimwn.get("/api/v1/xwroi-katoikisis/xwros_01/provlepsi-oxygonou").json()
    assert (dedomena["synoliki_autonomia_me_dexameni_wres"] is None) is anamenomeni


def test_midenikoi_katoikoi_kai_apenergopoiimeni_ilektrolysi(pelatis_dokimwn, synedria_dokimwn):
    from backend.app.montela import SyskeviYpostiriksisZwis

    for syskevi in synedria_dokimwn.scalars(select(SyskeviYpostiriksisZwis)):
        if syskevi.typos_syskevis == "ilektrolysi":
            syskevi.katastasi_leitourgias = "anenergi"
    synedria_dokimwn.commit()
    dedomena = pelatis_dokimwn.get("/api/v1/xwroi-katoikisis/xwros_01/provlepsi-oxygonou").json()
    assert dedomena["rythmos_paragwgis_kg_h"] == 0
    assert dedomena["synoliki_autonomia_me_dexameni_wres"] > 0
    synedria_dokimwn.get(XwrosKatoikisis, "xwros_01").plithysmos = 0
    synedria_dokimwn.commit()
    assert (
        pelatis_dokimwn.get("/api/v1/xwroi-katoikisis/xwros_01/provlepsi-oxygonou").json()[
            "synoliki_autonomia_me_dexameni_wres"
        ]
        is None
    )


def test_palio_pv_istoriko_diavazetai_me_agnwsti_poiotita():
    from backend.app.api.v1.poroi import FwtovoltaikoApantisi

    palio = FwtovoltaikoApantisi(
        id_fwtovoltaikou="pv_01",
        onoma="PV",
        epifaneia_m2=200,
        apodosi_eta=0.2,
        syntelestis_skonis=0.8,
        aktinovolia_w_m2=150,
        isxys_w=4800,
    )
    assert palio.poiotita == "agnwsti"
    assert palio.xronos_metrisis is None


def test_programma_trofodoteitai_prin_xamiloteris_proteraiotitas_fortio(
    pelatis_dokimwn, synedria_dokimwn
):
    from backend.app.montela import ProgrammaFwtismou
    from backend.app.pyrinas.asfaleia import XRISTES_EPIDEIKSIS
    from backend.app.ypiresies.ypiresia_porwn import YpiresiaPorwn

    ypiresia = YpiresiaPorwn(synedria_dokimwn)
    xristis = XRISTES_EPIDEIKSIS["syntonistis"]
    proep = ypiresia.proepiskopisi_fwtismou("thermokipio_01", "zwni_01", 1, 1 / 12, xristis)
    programma = ypiresia.dimiourgia_programmatos_fwtismou(
        "thermokipio_01", proep["id_proepiskopisis"], xristis
    )
    rythmise_paragwgi(synedria_dokimwn, 12)
    vima = pelatis_dokimwn.post("/api/v1/prosomoiwsi/vima", json={"lepta": 5})
    assert vima.status_code == 200, vima.text
    teliko = synedria_dokimwn.get(ProgrammaFwtismou, programma["id_programmatos"])
    assert teliko.katastasi == "oloklirothike"
    assert teliko.ektelestheisa_energeia_kwh == pytest.approx(1 / 12)
    poroi = vima.json()["apotelesmata"][0]["poroi"]
    assert poroi["mi_kalyptomeni_energeia_kwh"] == pytest.approx(3 / 12)


def test_offline_iliaki_tilemetria_den_stamata_ti_fysiki(pelatis_dokimwn, synedria_dokimwn):
    rythmise_paragwgi(synedria_dokimwn, 30)
    synedria_dokimwn.get(Aisthitiras, "aisth_aktinovolia").katastasi = "ektos_leitourgias"
    synedria_dokimwn.commit()
    apantisi = pelatis_dokimwn.post("/api/v1/prosomoiwsi/vima", json={"lepta": 5})
    assert apantisi.status_code == 200, apantisi.text
    assert apantisi.json()["apotelesmata"][0]["ypostiriksi_zwis"][0][
        "paragwgi_oxygonou_kg"
    ] == pytest.approx(0.1 / 12)
    assert pelatis_dokimwn.get("/api/v1/energeia/fwtovoltaika").json()[0]["poiotita"] == "apousia"


@pytest.mark.parametrize(
    "diadromi,dedomena",
    [
        (
            "/api/v1/thermokipia/thermokipio_01/fwtismos/proepiskopisi",
            {"id_zwnis": "zwni_01", "isxys_kw": 1, "diarkeia_wres": 1},
        ),
        (
            "/api/v1/energeia/periorismos-fortiwn/proepiskopisi",
            {"pausi_anavlhtwn": True, "aitiologia": "Ασφαλής προεπισκόπηση"},
        ),
    ],
)
def test_krisimes_proepiskopiseis_porwn_xreiazontai_pigi(
    pelatis_dokimwn, synedria_dokimwn, diadromi, dedomena
):
    synedria_dokimwn.get(Aisthitiras, "aisth_skoni").katastasi = "ektos_leitourgias"
    synedria_dokimwn.commit()
    apantisi = pelatis_dokimwn.post(diadromi, json=dedomena)
    assert apantisi.status_code == 503, apantisi.text


def test_kataigida_epivevaiwsi_epanelegxei_iliaki_pigi(pelatis_dokimwn, synedria_dokimwn):
    assert pelatis_dokimwn.post("/api/v1/senaria/kataigida-skonis/energopoiisi").status_code == 200
    proep = pelatis_dokimwn.post("/api/v1/senaria/kataigida-skonis/proepiskopisi").json()
    synedria_dokimwn.get(Aisthitiras, "aisth_skoni").katastasi = "ektos_leitourgias"
    synedria_dokimwn.commit()
    apantisi = pelatis_dokimwn.post(
        "/api/v1/senaria/kataigida_skonis_2026/apofaseis",
        json={
            "id_proepiskopisis": proep["id_proepiskopisis"],
            "epilogi": "pausi_anavlhtwn",
            "aitiologia": "Δοκιμή πηγής πριν την επιβεβαίωση",
        },
    )
    assert apantisi.status_code == 503, apantisi.text
    assert synedria_dokimwn.get(KatastasiProsomoiwsis, 1).pausi_anavlitwn is False


def test_poly_mikri_mpataria_den_dimiourgei_mideniko_xroniko_tmima(synedria_dokimwn):
    from backend.app.prosomoiwsi.prosomoiosis_porwn import proxorise_porous
    from backend.app.ypiresies.metriseis_kai_poiotita import se_utc

    rythmise_paragwgi(synedria_dokimwn, 0, 1.001e-9)
    arxi = se_utc(synedria_dokimwn.get(KatastasiProsomoiwsis, 1).xronos_prosomoiwsis)
    poroi = proxorise_porous(synedria_dokimwn, arxi, arxi + timedelta(microseconds=1))
    assert poroi["tmimata"] == 1
    assert synedria_dokimwn.get(Syssoreftis, "syssoreftis_01").energeia_kwh >= 0
    assert len(poroi["katanomes"]) == 1
