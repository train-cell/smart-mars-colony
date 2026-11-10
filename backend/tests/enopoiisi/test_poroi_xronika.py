"""Δοκιμές πραγματικού προγραμματισμού, ισοζυγίων και μοναδικότητας πόρων."""

import json
from datetime import timedelta

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.arxika_dedomena.fortwsi_dedomenwn import arxikopoiisi_dedomenwn_epideiksis
from backend.app.montela import VasiMontelwn
from backend.app.montela.koinonika_symvanta import KatastasiProsomoiwsis
from backend.app.montela.poroi import (
    DexameniNerou,
    EnergeiakoFortio,
    ProgrammaAnakyklwsis,
    ProgrammaArdefsis,
    ProgrammaFwtismou,
    Syssoreftis,
)
from backend.app.prosomoiwsi.prosomoiosis_porwn import efarmose_pausi_anavlitwn, proxorise_porous
from backend.app.pyrinas.asfaleia import XRISTES_EPIDEIKSIS
from backend.app.pyrinas.sfalmata import SfalmaKanona
from backend.app.ypiresies.metriseis_kai_poiotita import ananeose_metriseis
from backend.app.ypiresies.ypiresia_porwn import YpiresiaPorwn


@pytest.fixture
def poroi_synedria():
    """Η βάση πόρων είναι ιδιωτική και δεν εκκινεί lifespan ή προσωπική βάση."""
    mixani = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        json_serializer=lambda dedomena: json.dumps(dedomena, default=str),
    )
    VasiMontelwn.metadata.create_all(mixani)
    with sessionmaker(bind=mixani, autoflush=False)() as synedria:
        arxikopoiisi_dedomenwn_epideiksis(synedria)
        yield synedria
    mixani.dispose()


def _proxorise(synedria, lepta):
    roloi = synedria.get(KatastasiProsomoiwsis, 1)
    apo = roloi.xronos_prosomoiwsis
    ews = apo + timedelta(minutes=lepta)
    apotelesma = proxorise_porous(synedria, apo, ews)
    roloi.xronos_prosomoiwsis = ews
    ananeose_metriseis(synedria, ews)
    synedria.commit()
    return apotelesma


def test_ardefsi_mellontiki_ektelesi_mia_fora(poroi_synedria):
    synedria = poroi_synedria
    ypiresia = YpiresiaPorwn(synedria)
    xristis = XRISTES_EPIDEIKSIS["xristis_porwn"]
    # Η αρχική πρόβλεψη δεν δεσμεύει φυσική μάζα και το confirm κρατά reservation.
    twra = synedria.get(KatastasiProsomoiwsis, 1).xronos_prosomoiwsis
    proep = ypiresia.proepiskopisi_ardefsis(
        "thermokipio_01", "zwni_01", 100, 30, twra + timedelta(minutes=30), xristis
    )
    apantisi = ypiresia.dimiourgia_programmatos_ardefsis(
        proep["id_proepiskopisis"], xristis, "kleidi_ardefsis", "thermokipio_01"
    )
    assert synedria.get(DexameniNerou, "dexameni_01").trexwn_ogkos_l == 7500
    assert ypiresia.pare_katastasi_nerou()["synolika"]["desmevmeno_l"] == 100
    epanalipsi = ypiresia.dimiourgia_programmatos_ardefsis(
        proep["id_proepiskopisis"], xristis, "kleidi_ardefsis", "thermokipio_01"
    )
    assert epanalipsi == apantisi
    with pytest.raises(SfalmaKanona):
        ypiresia.dimiourgia_programmatos_ardefsis(
            proep["id_proepiskopisis"], xristis, None, "thermokipio_01"
        )
    synedria.rollback()
    logistiki = _proxorise(synedria, 30)
    assert logistiki["ardefsi_l"] == 0
    # Ο βασικός καθαρός ρυθμός +5 L/h είναι χωριστός από την προγραμματισμένη άρδευση.
    assert synedria.get(DexameniNerou, "dexameni_01").trexwn_ogkos_l == pytest.approx(7502.5)
    logistiki = _proxorise(synedria, 30)
    assert logistiki["ardefsi_l"] == pytest.approx(100)
    assert synedria.get(DexameniNerou, "dexameni_01").trexwn_ogkos_l == pytest.approx(7405)
    assert synedria.get(ProgrammaArdefsis, apantisi["id_programmatos"]).katastasi == "oloklirothike"
    assert _proxorise(synedria, 15)["ardefsi_l"] == 0


def test_akyrwsi_apodesmevei_xwris_eikoniki_epistrofi(poroi_synedria):
    ypiresia = YpiresiaPorwn(poroi_synedria)
    xristis = XRISTES_EPIDEIKSIS["xristis_porwn"]
    proep = ypiresia.proepiskopisi_ardefsis("thermokipio_01", "zwni_01", 100, xristis=xristis)
    stoixeio_pi = ypiresia.dimiourgia_programmatos_ardefsis(
        proep["id_proepiskopisis"], xristis, id_thermokipiou="thermokipio_01"
    )
    stoixeio_ro = ypiresia.akyrosi_programmatos_ardefsis(stoixeio_pi["id_programmatos"], xristis)
    assert stoixeio_ro["epistrafen_nero_l"] == 0
    assert ypiresia.pare_katastasi_nerou()["synolika"]["trexwn_ogkos_l"] == 7500
    assert ypiresia.pare_katastasi_nerou()["synolika"]["desmevmeno_l"] == 0
    assert ypiresia.pare_isozygio_nerou()["roes_l_h"]["katharos_rythmos"] == 5


def test_epikalypsi_kai_palia_proepiskopisi_aporriptontai(poroi_synedria):
    ypiresia = YpiresiaPorwn(poroi_synedria)
    xristis = XRISTES_EPIDEIKSIS["xristis_porwn"]
    stoixeio_alfa = ypiresia.proepiskopisi_ardefsis(
        "thermokipio_01", "zwni_01", 100, xristis=xristis
    )
    stoixeio_vita = ypiresia.proepiskopisi_ardefsis(
        "thermokipio_01", "zwni_02", 100, xristis=xristis
    )
    ypiresia.dimiourgia_programmatos_ardefsis(
        stoixeio_alfa["id_proepiskopisis"], xristis, id_thermokipiou="thermokipio_01"
    )
    with pytest.raises(SfalmaKanona):
        ypiresia.dimiourgia_programmatos_ardefsis(
            stoixeio_vita["id_proepiskopisis"], xristis, id_thermokipiou="thermokipio_01"
        )
    poroi_synedria.rollback()
    with pytest.raises(SfalmaKanona):
        ypiresia.proepiskopisi_ardefsis("thermokipio_01", "zwni_01", 50, xristis=xristis)


def test_anakyklwsi_diathrei_maza_nero_me_apwleia(poroi_synedria):
    synedria = poroi_synedria
    ypiresia = YpiresiaPorwn(synedria)
    xristis = XRISTES_EPIDEIKSIS["xristis_porwn"]
    for stoixeio_ro in synedria.scalars(select(EnergeiakoFortio)):
        stoixeio_ro.energo = False
    synedria.commit()
    proep = ypiresia.proepiskopisi_anakyklwsis(100, 0.85, xristis)
    stoixeio_pi = ypiresia.dimiourgia_programmatos_anakyklwsis(proep["id_proepiskopisis"], xristis)
    assert synedria.get(DexameniNerou, "dexameni_gkrizou").trexwn_ogkos_l == 1000
    logistiki = _proxorise(synedria, 60)
    assert logistiki["anakyklwsi_eisodos_l"] == 100
    assert logistiki["anakyklwsi_epistrofi_l"] == 85
    assert logistiki["apwleia_anakyklwsis_l"] == 15
    assert synedria.get(DexameniNerou, "dexameni_gkrizou").trexwn_ogkos_l == 900
    assert synedria.get(DexameniNerou, "dexameni_01").trexwn_ogkos_l == 7590
    assert (
        synedria.get(ProgrammaAnakyklwsis, stoixeio_pi["id_programmatos"]).katastasi
        == "oloklirothike"
    )
    assert _proxorise(synedria, 15)["anakyklwsi_eisodos_l"] == 0


def test_fwtismos_xronika_oria_kai_ilektriki_energeia(poroi_synedria):
    synedria = poroi_synedria
    ypiresia = YpiresiaPorwn(synedria)
    xristis = XRISTES_EPIDEIKSIS["xristis_porwn"]
    twra = synedria.get(KatastasiProsomoiwsis, 1).xronos_prosomoiwsis
    proep = ypiresia.proepiskopisi_fwtismou(
        "thermokipio_01", "zwni_01", 2, 1, xristis, twra + timedelta(minutes=30)
    )
    stoixeio_pi = ypiresia.dimiourgia_programmatos_fwtismou(
        "thermokipio_01", proep["id_proepiskopisis"], xristis
    )
    logistiki = _proxorise(synedria, 90)
    # Βασικό έλλειμμα 9.2 kW επί 1.5 h + 2 kW επί 1 h = 15.8 kWh.
    assert synedria.get(Syssoreftis, "syssoreftis_01").energeia_kwh == pytest.approx(14.2)
    programma = synedria.get(ProgrammaFwtismou, stoixeio_pi["id_programmatos"])
    assert programma.ektelestheisa_energeia_kwh == 2
    assert programma.katastasi == "oloklirothike"
    assert not any(
        stoixeio_zita.energo
        for stoixeio_zita in synedria.scalars(select(EnergeiakoFortio))
        if stoixeio_zita.id_fortiou.startswith("fortio_programmatos_")
    )
    assert logistiki["mi_kalyptomeni_energeia_kwh"] == 0


def test_periorismos_energeias_aposkopisi_kai_mideniki_autonomia(poroi_synedria):
    synedria = poroi_synedria
    ypiresia = YpiresiaPorwn(synedria)
    efarmose_pausi_anavlitwn(synedria, True)
    synedria.commit()
    proep = ypiresia.proepiskopisi_periorismou_fortiwn(False)
    assert proep["katastasi_meta"]["fortia_kw"] == 14
    assert proep["katastasi_meta"]["autonomia_wres"] == pytest.approx(30 / 9.2, abs=1e-6)
    synedria.get(Syssoreftis, "syssoreftis_01").energeia_kwh = 0
    synedria.commit()
    assert ypiresia.proepiskopisi_periorismou_fortiwn(True)["katastasi_meta"]["autonomia_wres"] == 0


def test_anastoli_anakyklwsis_den_dimiourgei_nero(poroi_synedria):
    synedria = poroi_synedria
    ypiresia = YpiresiaPorwn(synedria)
    xristis = XRISTES_EPIDEIKSIS["xristis_porwn"]
    proep = ypiresia.proepiskopisi_anakyklwsis(100, 0.85, xristis)
    stoixeio_pi = ypiresia.dimiourgia_programmatos_anakyklwsis(proep["id_proepiskopisis"], xristis)
    efarmose_pausi_anavlitwn(synedria, True)
    synedria.commit()
    assert _proxorise(synedria, 60)["anakyklwsi_eisodos_l"] == 0
    assert synedria.get(DexameniNerou, "dexameni_gkrizou").trexwn_ogkos_l == 1000
    assert synedria.get(ProgrammaAnakyklwsis, stoixeio_pi["id_programmatos"]).katastasi == "apetyxe"


def test_api_porwn_sxhmata_kai_xronos_enarksis(pelatis_dokimwn):
    """Το πραγματικό HTTP συμβόλαιο διατηρεί χρόνο έναρξης και σαφή απόκριση."""
    pelatis = pelatis_dokimwn
    kefalides = {"X-Id-Xristi": "xristis_porwn"}
    # Το seed αρχίζει την 10/11/2026 12:00 UTC.
    aitima = {
        "id_zwnis": "zwni_01",
        "posotita_nerou_l": 100,
        "diarkeia_lepta": 30,
        "xronos_enarksis": "2026-11-10T13:00:00Z",
    }
    apantisi = pelatis.post(
        "/api/v1/thermokipia/thermokipio_01/ardefsi/proepiskopisi", headers=kefalides, json=aitima
    )
    assert apantisi.status_code == 200, apantisi.text
    proep = apantisi.json()
    assert proep["xronos_enarksis"] == "2026-11-10T13:00:00Z"
    assert proep["xronos_liksis"] == "2026-11-10T13:30:00Z"
    assert proep["xronos_liksis_proepiskopisis"] != proep["xronos_liksis"]
    lathos = pelatis.post(
        "/api/v1/thermokipia/allo/ardefsi/programmata",
        headers=kefalides,
        json={"id_proepiskopisis": proep["id_proepiskopisis"]},
    )
    assert lathos.status_code in {404, 409}
    epivevaiwsi = pelatis.post(
        "/api/v1/thermokipia/thermokipio_01/ardefsi/programmata",
        headers={**kefalides, "Idempotency-Key": "monadiko-api"},
        json={"id_proepiskopisis": proep["id_proepiskopisis"]},
    )
    assert epivevaiwsi.status_code == 200, epivevaiwsi.text
    assert epivevaiwsi.json()["nea_stathmi_dexamenis_l"] == 7500
    epanalipsi = pelatis.post(
        "/api/v1/thermokipia/thermokipio_01/ardefsi/programmata",
        headers={**kefalides, "Idempotency-Key": "monadiko-api"},
        json={"id_proepiskopisis": proep["id_proepiskopisis"]},
    )
    assert epanalipsi.json() == epivevaiwsi.json()
    sxhma = pelatis.get("/openapi.json").json()
    apantisi_sxhma = sxhma["paths"]["/api/v1/energeia/katastasi"]["get"]["responses"]["200"][
        "content"
    ]["application/json"]["schema"]
    assert "$ref" in apantisi_sxhma
    anakyklwsi = pelatis.post(
        "/api/v1/nero/anakyklwsi/proepiskopisi", headers=kefalides, json={"posotita_nerou_l": 100}
    )
    assert anakyklwsi.status_code == 200, anakyklwsi.text
    epivevaiwsi = pelatis.post(
        "/api/v1/nero/anakyklwsi/programmata",
        headers=kefalides,
        json={"id_proepiskopisis": anakyklwsi.json()["id_proepiskopisis"]},
    )
    assert epivevaiwsi.status_code == 200, epivevaiwsi.text


def test_api_porwn_aporriptei_agnwsta_kai_apeira(pelatis_dokimwn):
    """Καμία σιωπηλή αγνόηση ώρας ή αποθήκευση άπειρης ισχύος."""
    for somatidio in [
        {"id_zwnis": "zwni_01", "isxys_kw": "Infinity"},
        {"id_zwnis": "zwni_01", "allo_pedio": 2},
        {"id_zwnis": "zwni_01", "xronos_enarksis": "2026-11-10T13:00:00"},
    ]:
        apantisi = pelatis_dokimwn.post(
            "/api/v1/thermokipia/thermokipio_01/fwtismos/proepiskopisi",
            headers={"X-Id-Xristi": "xristis_porwn"},
            json=somatidio,
        )
        assert apantisi.status_code == 422, apantisi.text
