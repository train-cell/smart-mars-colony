"""Ρυθμίσεις fixtures και απομονωμένης βάσης δοκιμών για το pytest."""

import json

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.arxika_dedomena.fortwsi_dedomenwn import arxikopoiisi_dedomenwn_epideiksis
from backend.app.main import efarmogi
from backend.app.montela.vasi_montelwn import VasiMontelwn
from backend.app.vasi.synthesi import pare_synedria_vasis

# Δημιουργία απομονωμένης in-memory SQLite βάσης με StaticPool για διατήρηση συνδέσεων
dokimastiki_mixani = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    json_serializer=lambda dedomena: json.dumps(dedomena, default=str),
)


@event.listens_for(Engine, "connect")
def rythmise_ksenous_desmous(syndesi_dokimwn, eggrafi_syndesis):
    dromeas = syndesi_dokimwn.cursor()
    dromeas.execute("PRAGMA foreign_keys=ON")
    dromeas.close()


DokimastikiSynedria = sessionmaker(autocommit=False, autoflush=False, bind=dokimastiki_mixani)


@pytest.fixture(scope="function")
def synedria_dokimwn():
    """Δημιουργεί καθαρό σχήμα και αρχικά δεδομένα για κάθε δοκιμή."""
    VasiMontelwn.metadata.create_all(bind=dokimastiki_mixani)
    synedria = DokimastikiSynedria()
    arxikopoiisi_dedomenwn_epideiksis(synedria, epanarxikopoiisi=True)

    try:
        yield synedria
    finally:
        synedria.close()
        VasiMontelwn.metadata.drop_all(bind=dokimastiki_mixani)


@pytest.fixture(scope="function")
def pelatis_dokimwn(synedria_dokimwn: Session):
    """Επιστρέφει TestClient με αντικατάσταση του database dependency."""

    def paroxeas_dokimastikis_synedrias():
        try:
            yield synedria_dokimwn
        except Exception:
            synedria_dokimwn.rollback()
            raise

    efarmogi.dependency_overrides[pare_synedria_vasis] = paroxeas_dokimastikis_synedrias
    with TestClient(efarmogi, headers={"X-Id-Xristi": "syntonistis"}) as pelatis:
        yield pelatis
    efarmogi.dependency_overrides.clear()
