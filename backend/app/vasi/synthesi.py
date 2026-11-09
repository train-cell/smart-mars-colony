"""Σύνδεση SQLite και διαχείριση συνεδριών SQLAlchemy 2.0.

Ενεργοποιεί ρητά τα Foreign Keys στη SQLite μέσω event listener
και παρέχει context-managed session dependency.
"""

import json
from typing import Generator

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from backend.app.pyrinas.rythmiseis import rythmiseis

# Δημιουργία SQLite Engine με check_same_thread=False για FastAPI concurrency
mixani_vasis = create_engine(
    rythmiseis.DIADROMI_VASIS,
    connect_args={"check_same_thread": False} if "sqlite" in rythmiseis.DIADROMI_VASIS else {},
    json_serializer=lambda obj: json.dumps(obj, default=str),
    echo=False,
)


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Επιβολή ξένων κλειδιών (foreign keys) στη SQLite."""
    # Εφαρμόζεται μόνο σε συνδέσεις SQLite
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


SynedriaVasis = sessionmaker(autocommit=False, autoflush=False, bind=mixani_vasis)


def pare_synedria_vasis() -> Generator[Session, None, None]:
    """FastAPI Dependency για παροχή συνεδρίας βάσης δεδομένων με αυτόματο κλείσιμο."""
    synedria = SynedriaVasis()
    try:
        yield synedria
    finally:
        synedria.close()
