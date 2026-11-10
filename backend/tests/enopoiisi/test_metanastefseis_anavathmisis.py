"""Μεταναστεύσεις από καθαρή και παλαιά εγκατάσταση με διατήρηση δεδομένων."""

from datetime import datetime, timezone
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import Session

from backend.app.arxika_dedomena.fortwsi_dedomenwn import arxikopoiisi_dedomenwn_epideiksis
from backend.app.montela import DexameniNerou, ProgrammaArdefsis
from backend.app.pyrinas.rythmiseis import rythmiseis


def rythmise_metanastefsi(monkeypatch, diadromi):
    """Κατευθύνει το Alembic αποκλειστικά σε προσωρινή βάση της δοκιμής."""
    riza = Path(__file__).resolve().parents[3]
    monkeypatch.setattr(rythmiseis, "DIADROMI_VASIS", "sqlite:///" + str(diadromi))
    rythmisi = Config(str(riza / "alembic.ini"))
    rythmisi.set_main_option("script_location", str(riza / "migrations"))
    return rythmisi


@pytest.mark.parametrize("palia_onomasia", [False, True])
def test_anavathmisi_palias_vasis_diatiroi_dedomena_kai_epistrefei_desmevseis(
    tmp_path, monkeypatch, palia_onomasia
):
    diadromi = tmp_path / "anavathmisi.db"
    rythmisi = rythmise_metanastefsi(monkeypatch, diadromi)
    command.upgrade(rythmisi, "head")
    mixani = create_engine("sqlite:///" + str(diadromi))
    with Session(mixani) as synedria:
        arxikopoiisi_dedomenwn_epideiksis(synedria)
        dexameni = synedria.get(DexameniNerou, "dexameni_01")
        dexameni.trexwn_ogkos_l = 7400
        synedria.add(
            ProgrammaArdefsis(
                id_programmatos="palia_desmefsi",
                id_thermokipiou="thermokipio_01",
                id_zwnis="zwni_01",
                id_dexamenis="dexameni_01",
                posotita_nerou_l=100,
                xronos_enarksis=datetime.now(timezone.utc),
                diarkeia_lepta=30,
                katastasi="programmatismeno",
            )
        )
        synedria.commit()
    command.downgrade(rythmisi, "1c63bef8cc3e")
    if palia_onomasia:
        with mixani.begin() as syndesi:
            syndesi.execute(
                text(
                    "ALTER TABLE katastasi_prosomoiwsis RENAME COLUMN energo_senario TO active_scenario"
                )
            )
    command.upgrade(rythmisi, "head")
    with mixani.connect() as syndesi:
        stiles = {stili["name"] for stili in inspect(syndesi).get_columns("katastasi_prosomoiwsis")}
        assert "energo_senario" in stiles and "active_scenario" not in stiles
        assert (
            syndesi.execute(
                text("SELECT trexwn_ogkos_l FROM dexamenes_nerou WHERE id_dexamenis='dexameni_01'")
            ).scalar()
            == 7500
        )
        assert (
            syndesi.execute(
                text(
                    "SELECT COUNT(*) FROM programmata_ardefsis WHERE id_programmatos='palia_desmefsi'"
                )
            ).scalar()
            == 1
        )
        assert syndesi.execute(text("PRAGMA foreign_key_check")).all() == []
    command.check(rythmisi)
    mixani.dispose()


def test_anavathmisi_aporriptei_asymfwni_desmefsi_prin_allaksei_sxhma(tmp_path, monkeypatch):
    diadromi = tmp_path / "yperxeilisi.db"
    rythmisi = rythmise_metanastefsi(monkeypatch, diadromi)
    command.upgrade(rythmisi, "head")
    mixani = create_engine("sqlite:///" + str(diadromi))
    with Session(mixani) as synedria:
        arxikopoiisi_dedomenwn_epideiksis(synedria)
        synedria.get(DexameniNerou, "dexameni_01").trexwn_ogkos_l = 10000
        synedria.add(
            ProgrammaArdefsis(
                id_programmatos="asymfwni_desmefsi",
                id_thermokipiou="thermokipio_01",
                id_zwnis="zwni_01",
                id_dexamenis="dexameni_01",
                posotita_nerou_l=100,
                xronos_enarksis=datetime.now(timezone.utc),
                diarkeia_lepta=30,
                katastasi="programmatismeno",
            )
        )
        synedria.commit()
    command.downgrade(rythmisi, "1c63bef8cc3e")
    with pytest.raises(RuntimeError, match="χωρητικότητα"):
        command.upgrade(rythmisi, "head")
    with mixani.connect() as syndesi:
        assert "proepiskopiseis" not in inspect(syndesi).get_table_names()
        assert (
            syndesi.execute(text("SELECT version_num FROM alembic_version")).scalar()
            == "1c63bef8cc3e"
        )
    mixani.dispose()
