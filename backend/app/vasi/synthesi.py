"""Σύνδεση SQLite και διαχείριση συνεδριών SQLAlchemy 2.0.

Ενεργοποιεί ρητά τα Foreign Keys στη SQLite μέσω event listener
και παρέχει context-managed session dependency.
"""

import json
import sqlite3
from typing import Generator

from fastapi.encoders import jsonable_encoder
from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from backend.app.pyrinas.rythmiseis import rythmiseis

# Δημιουργία SQLite Engine με check_same_thread=False για FastAPI concurrency
mixani_vasis = create_engine(
    rythmiseis.DIADROMI_VASIS,
    connect_args={"check_same_thread": False} if "sqlite" in rythmiseis.DIADROMI_VASIS else {},
    json_serializer=lambda timi: json.dumps(jsonable_encoder(timi), allow_nan=False),
    echo=False,
)


@event.listens_for(Engine, "connect")
def rythmise_sqlite(syndesi_vasis, eggrafi_syndesis):
    """Επιβολή ξένων κλειδιών και βελτιστοποίηση ταυτοχρονισμού στη SQLite."""
    if not isinstance(syndesi_vasis, sqlite3.Connection):
        return
    dromeas = syndesi_vasis.cursor()
    dromeas.execute("PRAGMA foreign_keys=ON")
    dromeas.execute("PRAGMA busy_timeout=5000")
    try:
        dromeas.execute("PRAGMA journal_mode=WAL")
    except sqlite3.OperationalError:
        # Προσωρινές βάσεις δεν υποστηρίζουν πάντοτε WAL.
        dromeas.execute("PRAGMA journal_mode")
    dromeas.close()


SynedriaVasis = sessionmaker(autocommit=False, autoflush=False, bind=mixani_vasis)


def pare_synedria_vasis() -> Generator[Session, None, None]:
    """FastAPI Dependency για παροχή συνεδρίας βάσης δεδομένων με αυτόματο κλείσιμο."""
    synedria = SynedriaVasis()
    try:
        yield synedria
    except Exception:
        synedria.rollback()
        raise
    finally:
        synedria.close()
