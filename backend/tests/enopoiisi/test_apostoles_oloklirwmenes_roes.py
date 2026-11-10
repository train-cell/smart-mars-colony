"""Έλεγχοι αποστολών: φυσικός προϋπολογισμός, διαδρομή, παραλαβή και χρόνος."""

from datetime import timedelta

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.api.v1.apostoles import dromologitis
from backend.app.arxika_dedomena.fortwsi_dedomenwn import arxikopoiisi_dedomenwn_epideiksis
from backend.app.montela import VasiMontelwn
from backend.app.montela.apostoles import OximaExerevnis
from backend.app.montela.koinonika_symvanta import Entoli, KatastasiProsomoiwsis
from backend.app.prosomoiwsi.prosomoiosis_apostolwn import proxorise_apostoles
from backend.app.pyrinas.asfaleia import XRISTES_EPIDEIKSIS
from backend.app.pyrinas.sfalmata import SfalmaKanona, xeiristis_sfalmatos_domain
from backend.app.vasi.synthesi import pare_synedria_vasis
from backend.app.ypiresies.ypiresia_apostolwn import YpiresiaApostolwn


@pytest.fixture
def synedria_apostolwn():
    mixani = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    VasiMontelwn.metadata.create_all(mixani)
    paroxeas = sessionmaker(bind=mixani, autoflush=False)
    with paroxeas() as synedria:
        arxikopoiisi_dedomenwn_epideiksis(synedria)
        yield synedria
    mixani.dispose()


@pytest.fixture
def pelatis_apostolwn(synedria_apostolwn):
    efarmogi = FastAPI()
    efarmogi.include_router(dromologitis, prefix="/api/v1")
    efarmogi.add_exception_handler(SfalmaKanona, xeiristis_sfalmatos_domain)

    def pare_dokimastiki():
        try:
            yield synedria_apostolwn
        except Exception:
            synedria_apostolwn.rollback()
            raise

    efarmogi.dependency_overrides[pare_synedria_vasis] = pare_dokimastiki
    with TestClient(efarmogi) as pelatis:
        yield pelatis


def _vima(synedria, lepta):
    katastasi = synedria.get(KatastasiProsomoiwsis, 1)
    apo = katastasi.xronos_prosomoiwsis
    ews = apo + timedelta(minutes=lepta)
    apantisi = proxorise_apostoles(synedria, apo, ews)
    katastasi.xronos_prosomoiwsis = ews
    synedria.commit()
    return apantisi


def _sti_vasi(synedria):
    oxima = synedria.get(OximaExerevnis, "rover_01")
    oxima.apostasi_apo_vasi_km = 0
    oxima.syntetagmeni_x = 0
    oxima.syntetagmeni_y = 0
    synedria.commit()
    return oxima


def _sxedio(**epipleon):
    return {
        "titlos": "Δειγματοληψία",
        "skopos": "Συλλογή εδάφους",
        "apostasi_km": 1.0,
        "ektimwmeni_diarkeia_wres": 1.0,
        "maza_fortiou_kg": 50.0,
        "plithos_plirwmatos": 0,
        **epipleon,
    }


def test_asfalis_stasi_apaitei_proepiskopisi(pelatis_apostolwn):
    apantisi = pelatis_apostolwn.post(
        "/api/v1/oximata/rover_01/asfalis-stasi/entoles",
        headers={"X-Id-Xristi": "xristis_apostolwn"},
    )
    assert apantisi.status_code == 422


def test_stasi_den_allazei_tin_isxy_epistrofis(synedria_apostolwn):
    ypiresia = YpiresiaApostolwn(synedria_apostolwn)
    xeiristis = XRISTES_EPIDEIKSIS["xristis_apostolwn"]
    proep = ypiresia.proepiskopisi_asfalous_stasis("rover_01", xeiristis)
    synedria_apostolwn.commit()
    apantisi = ypiresia.ektelesi_asfalous_stasis("rover_01", xeiristis, proep["id_proepiskopisis"])
    assert apantisi["katastasi_entolis"] == "oloklirothike"
    assert ypiresia.proepiskopisi_anaklisis("rover_01")[
        "apaitoumeni_energeia_kwh"
    ] == pytest.approx(0.3)
    oxima = synedria_apostolwn.get(OximaExerevnis, "rover_01")
    assert oxima.mesi_isxys_kw == pytest.approx(0.1)
    assert oxima.isxys_kinisis_kw == pytest.approx(0.6)


def test_apousia_simatos_den_vevaiwnei_stasi(synedria_apostolwn):
    ypiresia = YpiresiaApostolwn(synedria_apostolwn)
    oxima = synedria_apostolwn.get(OximaExerevnis, "rover_01")
    oxima.katastasi_epikoinwnias = "apousia"
    synedria_apostolwn.commit()
    xeiristis = XRISTES_EPIDEIKSIS["xristis_apostolwn"]
    proep = ypiresia.proepiskopisi_asfalous_stasis("rover_01", xeiristis)
    synedria_apostolwn.commit()
    apantisi = ypiresia.ektelesi_asfalous_stasis("rover_01", xeiristis, proep["id_proepiskopisis"])
    assert apantisi["katastasi_entolis"] == "avevaio"
    assert oxima.katastasi_oximatos == "stasi"
    _vima(synedria_apostolwn, 1)
    assert synedria_apostolwn.get(Entoli, apantisi["id_entolis"]).katastasi == "avevaio"
    oxima.katastasi_epikoinwnias = "statheri"
    synedria_apostolwn.commit()
    _vima(synedria_apostolwn, 1)
    assert oxima.katastasi_oximatos == "asfalis_stasi"
    assert synedria_apostolwn.get(Entoli, apantisi["id_entolis"]).katastasi == "oloklirothike"


def test_kathysterisi_paralavis_tireitai(synedria_apostolwn):
    oxima = synedria_apostolwn.get(OximaExerevnis, "rover_01")
    oxima.kathysterisi_epikoinwnias_s = 60
    synedria_apostolwn.commit()
    ypiresia = YpiresiaApostolwn(synedria_apostolwn)
    xeiristis = XRISTES_EPIDEIKSIS["xristis_apostolwn"]
    proep = ypiresia.proepiskopisi_asfalous_stasis("rover_01", xeiristis)
    synedria_apostolwn.commit()
    apantisi = ypiresia.ektelesi_asfalous_stasis("rover_01", xeiristis, proep["id_proepiskopisis"])
    assert apantisi["katastasi_entolis"] == "se_anamoni"
    _vima(synedria_apostolwn, 0.5)
    assert oxima.katastasi_oximatos == "stasi"
    _vima(synedria_apostolwn, 0.5)
    assert oxima.katastasi_oximatos == "asfalis_stasi"


def test_epistrofi_xronos_apostasi_energeia(synedria_apostolwn):
    ypiresia = YpiresiaApostolwn(synedria_apostolwn)
    xeiristis = XRISTES_EPIDEIKSIS["xristis_apostolwn"]
    proep = ypiresia.proepiskopisi_anaklisis("rover_01", xeiristis)
    apantisi = ypiresia.ektelesi_anaklisis("rover_01", xeiristis, proep["id_proepiskopisis"])
    oxima = synedria_apostolwn.get(OximaExerevnis, "rover_01")
    _vima(synedria_apostolwn, 15)
    assert oxima.apostasi_apo_vasi_km == pytest.approx(1)
    assert oxima.energeia_kwh == pytest.approx(0.65)
    _vima(synedria_apostolwn, 15)
    assert oxima.apostasi_apo_vasi_km == pytest.approx(0)
    assert oxima.energeia_kwh == pytest.approx(0.5)
    assert synedria_apostolwn.get(Entoli, apantisi["id_entolis"]).katastasi == "oloklirothike"
    _vima(synedria_apostolwn, 15)
    assert oxima.energeia_kwh == pytest.approx(0.475)


def test_apotelesma_epanalipsis_idio(synedria_apostolwn):
    ypiresia = YpiresiaApostolwn(synedria_apostolwn)
    xeiristis = XRISTES_EPIDEIKSIS["xristis_apostolwn"]
    proep = ypiresia.proepiskopisi_asfalous_stasis("rover_01", xeiristis)
    synedria_apostolwn.commit()
    prwti = ypiresia.ektelesi_asfalous_stasis(
        "rover_01", xeiristis, proep["id_proepiskopisis"], "kleidi"
    )
    defteri = ypiresia.ektelesi_asfalous_stasis(
        "rover_01", xeiristis, proep["id_proepiskopisis"], "kleidi"
    )
    assert defteri == prwti
    with pytest.raises(SfalmaKanona) as sfalma:
        ypiresia.ektelesi_asfalous_stasis(
            "rover_01", xeiristis, proep["id_proepiskopisis"], "allo_kleidi"
        )
    assert sfalma.value.katastasi_http == 409


def test_mi_efikti_apostoli_den_kataxwrietai(synedria_apostolwn):
    _sti_vasi(synedria_apostolwn)
    ypiresia = YpiresiaApostolwn(synedria_apostolwn)
    xeiristis = XRISTES_EPIDEIKSIS["xristis_apostolwn"]
    proep = ypiresia.proepiskopisi_apostolis(
        "rover_01", _sxedio(apostasi_km=100, ektimwmeni_diarkeia_wres=72), xeiristis
    )
    assert not proep["energeiaka_efikto"]
    with pytest.raises(SfalmaKanona) as sfalma:
        ypiresia.dimiourgia_apostolis("rover_01", proep["id_proepiskopisis"], xeiristis)
    assert sfalma.value.kodikos.value == "ANEPARKIS_ENERGEIA"


def test_sxedio_diatirei_parametrous_kai_ekteleitai(synedria_apostolwn):
    oxima = _sti_vasi(synedria_apostolwn)
    ypiresia = YpiresiaApostolwn(synedria_apostolwn)
    xeiristis = XRISTES_EPIDEIKSIS["xristis_apostolwn"]
    sxedio = _sxedio(
        maza_fortiou_kg=150,
        plithos_plirwmatos=1,
        shmeia_diadromis=[
            {
                "syntetagmeni_x": 600,
                "syntetagmeni_y": 800,
                "apostasi_apo_proigoumeno_m": 1000,
                "klisi_rad": 0.1,
            }
        ],
    )
    proep = ypiresia.proepiskopisi_apostolis("rover_01", sxedio, xeiristis)
    apantisi = ypiresia.dimiourgia_apostolis("rover_01", proep["id_proepiskopisis"], xeiristis)
    meta = ypiresia.pare_katastasi_oximatos("rover_01")["apostoles"][0]
    assert meta["maza_fortiou_kg"] == 150
    assert meta["plithos_plirwmatos"] == 1
    assert meta["shmeia_diadromis"][0]["klisi_rad"] == pytest.approx(0.1)
    _vima(synedria_apostolwn, 30)
    assert oxima.apostasi_apo_vasi_km == pytest.approx(1)
    assert oxima.syntetagmeni_x == pytest.approx(600)
    _vima(synedria_apostolwn, 30)
    assert oxima.katastasi_oximatos == "sti_vasi"
    assert oxima.energeia_kwh == pytest.approx(0.8 - proep["ektimwmeni_energeia_kwh"])
    assert oxima.energeia_kwh >= oxima.efedreia_kwh
    assert synedria_apostolwn.get(Entoli, apantisi["id_entolis"]).katastasi == "oloklirothike"


def test_anavoli_elegxei_goniko_kai_katastasi(synedria_apostolwn):
    _sti_vasi(synedria_apostolwn)
    ypiresia = YpiresiaApostolwn(synedria_apostolwn)
    xeiristis = XRISTES_EPIDEIKSIS["xristis_apostolwn"]
    proep = ypiresia.proepiskopisi_apostolis("rover_01", _sxedio(), xeiristis)
    apantisi = ypiresia.dimiourgia_apostolis("rover_01", proep["id_proepiskopisis"], xeiristis)
    with pytest.raises(SfalmaKanona) as sfalma:
        ypiresia.anavoli_apostolis("anyparkto", apantisi["id_apostolis"], xeiristis)
    assert sfalma.value.katastasi_http == 404
    akyrosi = ypiresia.anavoli_apostolis("rover_01", apantisi["id_apostolis"], xeiristis)
    assert akyrosi["katastasi"] == "anavoli"
    with pytest.raises(SfalmaKanona):
        ypiresia.anavoli_apostolis("rover_01", apantisi["id_apostolis"], xeiristis)


def test_api_palia_proepiskopisi_kai_apousia_rolou(pelatis_apostolwn, synedria_apostolwn):
    diadromi = "/api/v1/oximata/rover_01/asfalis-stasi"
    assert pelatis_apostolwn.post(diadromi + "/proepiskopisi").status_code == 401
    kefalides = {"X-Id-Xristi": "xristis_apostolwn"}
    proep = pelatis_apostolwn.post(diadromi + "/proepiskopisi", headers=kefalides)
    assert proep.status_code == 200
    oxima = synedria_apostolwn.get(OximaExerevnis, "rover_01")
    oxima.energeia_kwh -= 0.01
    synedria_apostolwn.commit()
    epivevaiwsi = pelatis_apostolwn.post(
        diadromi + "/entoles",
        headers=kefalides,
        json={"id_proepiskopisis": proep.json()["id_proepiskopisis"]},
    )
    assert epivevaiwsi.status_code == 409


@pytest.mark.parametrize(
    "pedio,timi", [("apostasi_km", "Infinity"), ("maza_fortiou_kg", -1), ("plithos_plirwmatos", 10)]
)
def test_api_aporriptei_akyres_posotites(pelatis_apostolwn, pedio, timi):
    apantisi = pelatis_apostolwn.post(
        "/api/v1/oximata/rover_01/apostoles/proepiskopisi",
        headers={"X-Id-Xristi": "xristis_apostolwn"},
        json=_sxedio(**{pedio: timi}),
    )
    assert apantisi.status_code == 422


def test_api_elegxei_klisi_kai_mikos_diadromis(pelatis_apostolwn):
    kefalides = {"X-Id-Xristi": "xristis_apostolwn"}
    aitima = _sxedio(shmeia_diadromis=[{"apostasi_apo_proigoumeno_m": 1000, "klisi_rad": 3.14}])
    assert (
        pelatis_apostolwn.post(
            "/api/v1/oximata/rover_01/apostoles/proepiskopisi", headers=kefalides, json=aitima
        ).status_code
        == 422
    )
    aitima = _sxedio(shmeia_diadromis=[{"apostasi_apo_proigoumeno_m": 1200, "klisi_rad": 0}])
    assert (
        pelatis_apostolwn.post(
            "/api/v1/oximata/rover_01/apostoles/proepiskopisi", headers=kefalides, json=aitima
        ).status_code
        == 422
    )


def test_aktinovolia_einai_aneksartitos_kindynos(synedria_apostolwn):
    from backend.app.montela.apostoles import ExwterikosKindynos

    kindynos = synedria_apostolwn.get(ExwterikosKindynos, "kindynos_baseline")
    kindynos.epipedo_aktinovolias = 0.6
    synedria_apostolwn.commit()
    ypiresia = YpiresiaApostolwn(synedria_apostolwn)
    xeiristis = XRISTES_EPIDEIKSIS["xristis_apostolwn"]
    proep = ypiresia.proepiskopisi_anaklisis("rover_01", xeiristis)
    assert proep["energeiaka_efikto"]
    assert proep["oratotita_asfalis"]
    assert not proep["aktinovolia_asfalis"]
    assert not proep["synolika_asfalis_epistrofi"]
    with pytest.raises(SfalmaKanona) as sfalma:
        ypiresia.ektelesi_anaklisis("rover_01", xeiristis, proep["id_proepiskopisis"])
    assert sfalma.value.katastasi_http == 409


def test_api_proepiskopisi_apostolis_kai_epanalipsi(pelatis_apostolwn, synedria_apostolwn):
    _sti_vasi(synedria_apostolwn)
    kefalides = {"X-Id-Xristi": "xristis_apostolwn", "Idempotency-Key": "apostoli-monadiki"}
    proep = pelatis_apostolwn.post(
        "/api/v1/oximata/rover_01/apostoles/proepiskopisi", headers=kefalides, json=_sxedio()
    )
    assert proep.status_code == 200
    aitima = {"id_proepiskopisis": proep.json()["id_proepiskopisis"]}
    prwti = pelatis_apostolwn.post(
        "/api/v1/oximata/rover_01/apostoles", headers=kefalides, json=aitima
    )
    assert prwti.status_code == 200
    defteri = pelatis_apostolwn.post(
        "/api/v1/oximata/rover_01/apostoles", headers=kefalides, json=aitima
    )
    assert defteri.status_code == 200
    assert prwti.json() == defteri.json()
    assert len(pelatis_apostolwn.get("/api/v1/oximata/rover_01/apostoles").json()["apostoles"]) == 1


def test_apousia_simatos_diatirei_teleftaia_epivevaiwmeni_ora(synedria_apostolwn):
    oxima = synedria_apostolwn.get(OximaExerevnis, "rover_01")
    roloi = synedria_apostolwn.get(KatastasiProsomoiwsis, 1)
    oxima.xronos_teleftaias_tilemetrias = roloi.xronos_prosomoiwsis
    oxima.katastasi_epikoinwnias = "apousia"
    synedria_apostolwn.commit()
    _vima(synedria_apostolwn, 5)
    katastasi = YpiresiaApostolwn(synedria_apostolwn).pare_oximata()[0]
    assert katastasi["xronos_metrisis"] == roloi.xronos_prosomoiwsis - timedelta(minutes=5)
    assert katastasi["poiotita"] == "apousia"
    assert katastasi["avevaiotita"]
