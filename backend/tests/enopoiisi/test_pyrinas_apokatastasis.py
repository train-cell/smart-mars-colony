"""Δοκιμές πραγματικής εξουσιοδότησης, μόνιμων previews και συναλλαγών."""

from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import StaleDataError
from sqlalchemy.pool import StaticPool

from backend.app.arxika_dedomena.fortwsi_dedomenwn import arxikopoiisi_dedomenwn_epideiksis
from backend.app.montela import (
    KatastasiProsomoiwsis,
    MetavivasiDikaiwmatos,
    Proepiskopisi,
    VasiMontelwn,
    Xristis,
    XwrosKatoikisis,
)
from backend.app.pyrinas.asfaleia import XRISTES_EPIDEIKSIS, RolosXristi, pare_xristi_apo_vasi
from backend.app.pyrinas.sfalmata import SfalmaKanona
from backend.app.ypiresies.entoles_kai_proepiskopiseis import (
    dimiourgise_proepiskopisi,
    katanalwse_proepiskopisi,
    kataxwrise_entoli,
    kleidwse_synallagi,
    pare_epanalipsi,
    pare_proepiskopisi,
)


@pytest.fixture
def apomonomenes_synedries():
    """Ανεξάρτητη SQLite, χωρίς lifespan ή προσωπική βάση."""
    mixani = create_engine(
        "sqlite://", poolclass=StaticPool, connect_args={"check_same_thread": False}
    )
    VasiMontelwn.metadata.create_all(mixani)
    ergostasio = sessionmaker(bind=mixani, autoflush=False)
    with ergostasio() as synedria:
        arxikopoiisi_dedomenwn_epideiksis(synedria)
    yield ergostasio
    mixani.dispose()


def test_agnwstos_kai_anenergos_xristis_aporriptontai(apomonomenes_synedries):
    with apomonomenes_synedries() as synedria:
        for anagnwristiko in [None, "agnwstos"]:
            with pytest.raises(SfalmaKanona) as sfalma:
                pare_xristi_apo_vasi(synedria, anagnwristiko)
            assert sfalma.value.katastasi_http == 401
        synedria.get(Xristis, "xristis_porwn").energos = False
        synedria.commit()
        with pytest.raises(SfalmaKanona):
            pare_xristi_apo_vasi(synedria, "xristis_porwn")


def test_metavivasi_efarmozetai_mono_se_pedio_kai_prin_liksi(apomonomenes_synedries):
    with apomonomenes_synedries() as synedria:
        twra = datetime.now(timezone.utc)
        metavivasi = MetavivasiDikaiwmatos(
            id_metavivasis="metav_dokimi",
            id_syntonisti="syntonistis",
            id_paralipti="xristis_porwn",
            rolos="ypefthynos_ypostiriksis_zwis",
            pedio_efarmogis="xwros_01",
            xronos_enarksis=twra - timedelta(minutes=1),
            xronos_liksis=twra + timedelta(hours=1),
            aitiologia="Κάλυψη βάρδιας",
            energo=True,
        )
        synedria.add(metavivasi)
        synedria.commit()
        swstos = pare_xristi_apo_vasi(synedria, "xristis_porwn", pedia={"xwros_01"})
        lathos = pare_xristi_apo_vasi(synedria, "xristis_porwn", pedia={"xwros_02"})
        assert RolosXristi.YPEFTHYNOS_YPOSTIRIKSIS_ZWIS in swstos.energoi_roloi
        assert RolosXristi.YPEFTHYNOS_YPOSTIRIKSIS_ZWIS not in lathos.energoi_roloi
        metavivasi.xronos_liksis = twra - timedelta(seconds=1)
        synedria.commit()
        assert (
            RolosXristi.YPEFTHYNOS_YPOSTIRIKSIS_ZWIS
            not in pare_xristi_apo_vasi(synedria, "xristis_porwn", pedia={"xwros_01"}).energoi_roloi
        )
        metavivasi.xronos_liksis = twra + timedelta(hours=1)
        metavivasi.xronos_anaklisis = twra
        synedria.commit()
        assert (
            RolosXristi.YPEFTHYNOS_YPOSTIRIKSIS_ZWIS
            not in pare_xristi_apo_vasi(synedria, "xristis_porwn", pedia={"xwros_01"}).energoi_roloi
        )


def test_proepiskopisi_diatiroitai_kai_katanalwnetai_mia_fora(apomonomenes_synedries):
    xristis = XRISTES_EPIDEIKSIS["xristis_zwis"]
    with apomonomenes_synedries() as synedria:
        proep = dimiourgise_proepiskopisi(
            synedria, "thermokrasia", "xwros_01", xristis, {"epiptwsi": 200}, {"ekdosi": 1}
        )
        synedria.commit()
    with apomonomenes_synedries() as nea:
        kleidwse_synallagi(nea)
        dedomena = pare_proepiskopisi(
            nea, proep["id_proepiskopisis"], "thermokrasia", "xwros_01", xristis, {"ekdosi": 1}
        )
        assert dedomena["epiptwsi"] == 200
        katanalwse_proepiskopisi(nea, proep["id_proepiskopisis"])
        nea.commit()
        with pytest.raises(SfalmaKanona) as sfalma:
            katanalwse_proepiskopisi(nea, proep["id_proepiskopisis"])
        assert sfalma.value.katastasi_http == 409


def test_proepiskopisi_elegxei_katoxo_ekdosi_liksi_kai_epoxi(apomonomenes_synedries):
    xristis = XRISTES_EPIDEIKSIS["xristis_zwis"]
    with apomonomenes_synedries() as synedria:
        proep = dimiourgise_proepiskopisi(
            synedria, "thermokrasia", "xwros_01", xristis, {}, {"ekdosi": 1}
        )
        synedria.commit()
        anagnwristiko = proep["id_proepiskopisis"]
        with pytest.raises(SfalmaKanona) as sfalma:
            pare_proepiskopisi(
                synedria,
                anagnwristiko,
                "thermokrasia",
                "xwros_01",
                XRISTES_EPIDEIKSIS["syntonistis"],
            )
        assert sfalma.value.katastasi_http == 403
        with pytest.raises(SfalmaKanona):
            pare_proepiskopisi(
                synedria, anagnwristiko, "thermokrasia", "xwros_01", xristis, {"ekdosi": 2}
            )
        synedria.get(KatastasiProsomoiwsis, 1).epoxi_prosomoiwsis = "epanafora"
        synedria.commit()
        with pytest.raises(SfalmaKanona):
            pare_proepiskopisi(synedria, anagnwristiko, "thermokrasia", "xwros_01", xristis)
        synedria.get(KatastasiProsomoiwsis, 1).epoxi_prosomoiwsis = synedria.get(
            Proepiskopisi, anagnwristiko
        ).epoxi_prosomoiwsis
        synedria.get(Proepiskopisi, anagnwristiko).xronos_liksis = datetime.now(
            timezone.utc
        ) - timedelta(seconds=1)
        synedria.commit()
        with pytest.raises(SfalmaKanona):
            pare_proepiskopisi(synedria, anagnwristiko, "thermokrasia", "xwros_01", xristis)


def test_monadikotita_ana_xristi_drasi_kai_soma(apomonomenes_synedries):
    with apomonomenes_synedries() as synedria:
        xristis = XRISTES_EPIDEIKSIS["xristis_zwis"]
        apantisi = {"katastasi": "oloklirothike", "epithymiti_thermokrasia_k": 295}
        kataxwrise_entoli(
            synedria,
            xristis,
            "ypostiriksi_zwis",
            "thermokrasia",
            "xwros_01",
            {"timi": 295},
            apantisi,
            kleidi="idio",
        )
        synedria.commit()
        assert (
            pare_epanalipsi(synedria, xristis, "thermokrasia", "xwros_01", "idio", {"timi": 295})
            == apantisi
        )
        assert (
            pare_epanalipsi(
                synedria,
                XRISTES_EPIDEIKSIS["xristis_porwn"],
                "ardefsi",
                "thermokipio_01",
                "idio",
                {"timi": 295},
            )
            is None
        )
        with pytest.raises(SfalmaKanona) as sfalma:
            pare_epanalipsi(synedria, xristis, "thermokrasia", "xwros_01", "idio", {"timi": 296})
        assert sfalma.value.katastasi_http == 409


def test_orm_aporriptei_palia_anagnwsi_kai_diatiroi_utc(tmp_path):
    mixani = create_engine("sqlite:///" + str(tmp_path / "taftoxronismos.db"))
    VasiMontelwn.metadata.create_all(mixani)
    ergostasio = sessionmaker(bind=mixani)
    with ergostasio() as synedria:
        arxikopoiisi_dedomenwn_epideiksis(synedria)
    with ergostasio() as prwti, ergostasio() as deuteri:
        xwros_prwtos = prwti.get(XwrosKatoikisis, "xwros_01")
        xwros_deuteros = deuteri.get(XwrosKatoikisis, "xwros_01")
        assert xwros_prwtos.xronos_dimiourgias.tzinfo is not None
        xwros_prwtos.epithymiti_thermokrasia_k = 294
        prwti.commit()
        xwros_deuteros.epithymiti_thermokrasia_k = 295
        with pytest.raises(StaleDataError):
            deuteri.commit()
    mixani.dispose()


def test_dyo_taftoxrones_desmevseis_den_xrisimopoioun_to_idio_nero(tmp_path):
    """Δύο πραγματικές συνδέσεις διεκδικούν4000 L από το ίδιο διαθέσιμο6500 L."""
    from concurrent.futures import ThreadPoolExecutor
    from threading import Barrier

    from sqlalchemy import select

    from backend.app.montela import ProgrammaArdefsis
    from backend.app.ypiresies.ypiresia_porwn import YpiresiaPorwn

    mixani = create_engine(
        "sqlite:///" + str(tmp_path / "desmevseis.db"), connect_args={"check_same_thread": False}
    )
    VasiMontelwn.metadata.create_all(mixani)
    ergostasio = sessionmaker(bind=mixani, autoflush=False)
    xristis = XRISTES_EPIDEIKSIS["xristis_porwn"]
    with ergostasio() as synedria:
        arxikopoiisi_dedomenwn_epideiksis(synedria)
        ypiresia = YpiresiaPorwn(synedria)
        prwti = ypiresia.proepiskopisi_ardefsis("thermokipio_01", "zwni_01", 4000, xristis=xristis)
        deuteri = ypiresia.proepiskopisi_ardefsis(
            "thermokipio_01", "zwni_02", 4000, xristis=xristis
        )
    empodio = Barrier(2)

    def desmevse(protasi):
        with ergostasio() as synedria:
            empodio.wait(timeout=5)
            try:
                YpiresiaPorwn(synedria).dimiourgia_programmatos_ardefsis(
                    protasi["id_proepiskopisis"], xristis, id_thermokipiou="thermokipio_01"
                )
                return 200
            except SfalmaKanona as sfalma:
                synedria.rollback()
                return sfalma.katastasi_http

    with ThreadPoolExecutor(max_workers=2) as ektelestis:
        apotelesmata = list(ektelestis.map(desmevse, [prwti, deuteri]))
    assert sorted(apotelesmata) == [200, 409]
    with ergostasio() as synedria:
        assert len(synedria.scalars(select(ProgrammaArdefsis)).all()) == 1
        assert YpiresiaPorwn(synedria).pare_katastasi_nerou()["synolika"]["desmevmeno_l"] == 4000
    mixani.dispose()


def test_anaklisi_metavivasis_aporriptei_kai_palio_antikeimeno_xristi(apomonomenes_synedries):
    """Ο έλεγχος μέσα στη συναλλαγή δεν εμπιστεύεται DTO που διαβάστηκε πριν την ανάκληση."""
    with apomonomenes_synedries() as synedria:
        twra = datetime.now(timezone.utc)
        metavivasi = MetavivasiDikaiwmatos(
            id_metavivasis="metav_palia",
            id_syntonisti="syntonistis",
            id_paralipti="xristis_porwn",
            rolos="ypefthynos_ypostiriksis_zwis",
            pedio_efarmogis="xwros_01",
            xronos_enarksis=twra - timedelta(minutes=1),
            xronos_liksis=twra + timedelta(hours=1),
            aitiologia="Ελεγχόμενη βάρδια",
            energo=True,
        )
        synedria.add(metavivasi)
        synedria.commit()
        xristis = pare_xristi_apo_vasi(synedria, "xristis_porwn", pedia={"xwros_01"})
        proep = dimiourgise_proepiskopisi(synedria, "thermokrasia", "xwros_01", xristis, {}, {})
        synedria.commit()
        metavivasi.energo = False
        synedria.commit()
        kleidwse_synallagi(synedria)
        with pytest.raises(SfalmaKanona) as sfalma:
            pare_proepiskopisi(
                synedria, proep["id_proepiskopisis"], "thermokrasia", "xwros_01", xristis, {}
            )
        assert sfalma.value.katastasi_http == 403
