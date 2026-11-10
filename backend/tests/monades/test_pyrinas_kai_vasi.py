"""Δοκιμές μονάδας για τον πυρήνα ασφαλείας, τη βάση και τους γενικούς χειριστές σφαλμάτων."""

import asyncio
from unittest.mock import MagicMock

import pytest

from backend.app.main import xeiristis_genikou_sfalmatos
from backend.app.pyrinas.asfaleia import (
    RolosXristi,
)
from backend.app.pyrinas.sfalmata import SfalmaKanona
from backend.app.vasi.synthesi import pare_synedria_vasis


def test_asfaleia_me_riti_taftotita(synedria_dokimwn):
    from backend.app.pyrinas.asfaleia import pare_xristi_apo_vasi

    xristis = pare_xristi_apo_vasi(synedria_dokimwn, "syntonistis")
    assert xristis.vasikos_rolos == RolosXristi.SYNTONISTIS_APOIKIAS
    for id_xristi in (None, "agnwstos"):
        with pytest.raises(SfalmaKanona) as sfalma:
            pare_xristi_apo_vasi(synedria_dokimwn, id_xristi)
        assert sfalma.value.katastasi_http == 401
    with pytest.raises(SfalmaKanona) as sfalma:
        pare_xristi_apo_vasi(synedria_dokimwn, "xristis_zwis", "syntonistis_apoikias")
    assert sfalma.value.katastasi_http == 403


def test_paroxi_synedrias_vasis():
    """Έλεγχος του generator διαχείρισης συνεδρίας SQLAlchemy στη synthesi.py."""
    genitria = pare_synedria_vasis()
    synedria = next(genitria)
    assert synedria is not None
    # Επιβεβαίωση εκτέλεσης finally μπλοκ (κλείσιμο συνεδρίας)
    with pytest.raises(StopIteration):
        next(genitria)


def test_synedria_vasis_epanafora_meta_sfalma():
    """Έλεγχος του rollback όταν προκύπτει σφάλμα κατά τη χρήση της συνεδρίας (lines 47-49)."""
    genitria = pare_synedria_vasis()
    synedria = next(genitria)
    assert synedria is not None
    with pytest.raises(RuntimeError, match="Σφάλμα συνεδρίας"):
        genitria.throw(RuntimeError("Σφάλμα συνεδρίας"))


def test_rythmiseis_sqlite_se_pragmatiki_syndesi():
    import sqlite3

    from backend.app.vasi.synthesi import rythmise_sqlite

    syndesi = sqlite3.connect(":memory:")
    rythmise_sqlite(syndesi, None)
    assert syndesi.execute("PRAGMA foreign_keys").fetchone()[0] == 1
    assert syndesi.execute("PRAGMA busy_timeout").fetchone()[0] == 5000
    syndesi.close()


def test_kentrikos_xeiristis_genikou_sfalmatos():
    """Έλεγχος γενικού χειριστή σφαλμάτων 500 στο main.py."""
    aitima_dokimwn = MagicMock()
    sfalma = RuntimeError("Απρόβλεπτο σφάλμα προσομοίωσης")
    apantisi_http = asyncio.run(xeiristis_genikou_sfalmatos(aitima_dokimwn, sfalma))
    assert apantisi_http.status_code == 500
    assert b"ESWTERIKO_SFALMA" in apantisi_http.body
