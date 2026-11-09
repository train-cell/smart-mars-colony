"""Δοκιμές μονάδας για τον πυρήνα ασφαλείας, τη βάση και τους γενικούς χειριστές σφαλμάτων."""

import asyncio
from unittest.mock import MagicMock

import pytest

from backend.app.main import xeiristis_genikou_sfalmatos
from backend.app.pyrinas.asfaleia import (
    RolosXristi,
    pare_trexonta_xristi,
)
from backend.app.pyrinas.sfalmata import KodikosSfalmatos, SfalmaDomain
from backend.app.vasi.synthesi import pare_synedria_vasis


def test_asfaleia_header_branches():
    """Πλήρης έλεγχος όλων των διακλαδώσεων ανάκτησης χρήστη από headers."""
    # 1. Πλήρης ταυτοποίηση με έγκυρο χρήστη και έγκυρο ρόλο
    u1 = pare_trexonta_xristi(x_id_xristi="syntonistis", x_rolos="syntonistis_apoikias")
    assert u1.id_xristi == "syntonistis"

    # 2. Χρήστης χωρίς δικαίωμα ανάληψης αυθαίρετου ρόλου (403)
    with pytest.raises(SfalmaDomain) as exc_info:
        pare_trexonta_xristi(x_id_xristi="xristis_zwis", x_rolos="syntonistis_apoikias")
    assert exc_info.value.katastasi_http == 403
    assert exc_info.value.kodikos == KodikosSfalmatos.ANARMODIOS_XRISTIS

    # 3. Μη έγκυρος ρόλος όταν έχει δοθεί id χρήστη (400)
    with pytest.raises(SfalmaDomain) as exc_info:
        pare_trexonta_xristi(x_id_xristi="xristis_zwis", x_rolos="aniparxtos_rolos")
    assert exc_info.value.katastasi_http == 400
    assert exc_info.value.kodikos == KodikosSfalmatos.AKYRI_TIMI

    # 4. Χωρίς id χρήστη, αλλά με έγκυρο x_rolos -> εύρεση demo χρήστη
    u2 = pare_trexonta_xristi(x_id_xristi=None, x_rolos="ypefthynos_ypostiriksis_zwis")
    assert u2.vasikos_rolos == RolosXristi.YPEFTHYNOS_YPOSTIRIKSIS_ZWIS

    # 5. Χωρίς id χρήστη, με μη έγκυρο x_rolos (400)
    with pytest.raises(SfalmaDomain) as exc_info:
        pare_trexonta_xristi(x_id_xristi=None, x_rolos="aniparxtos_rolos")
    assert exc_info.value.katastasi_http == 400
    assert exc_info.value.kodikos == KodikosSfalmatos.AKYRI_TIMI

    # 6. Χωρίς κανένα header -> προεπιλογή syntonistis
    u_default = pare_trexonta_xristi(x_id_xristi=None, x_rolos=None)
    assert u_default.id_xristi == "syntonistis"

    # 7. Άγνωστο id χρήστη χωρίς ρόλο -> προεπιλογή syntonistis
    u_unknown = pare_trexonta_xristi(x_id_xristi="agnwstos_xristis", x_rolos=None)
    assert u_unknown.id_xristi == "syntonistis"


def test_vasi_synthesi_pare_synedria_generator():
    """Έλεγχος του generator διαχείρισης συνεδρίας SQLAlchemy στη synthesi.py."""
    gen = pare_synedria_vasis()
    synedria = next(gen)
    assert synedria is not None
    # Επιβεβαίωση εκτέλεσης finally μπλοκ (κλείσιμο συνεδρίας)
    with pytest.raises(StopIteration):
        next(gen)


def test_vasi_synthesi_pare_synedria_generator_exception_rollback():
    """Έλεγχος του rollback όταν προκύπτει σφάλμα κατά τη χρήση της συνεδρίας (lines 47-49)."""
    gen = pare_synedria_vasis()
    sess = next(gen)
    assert sess is not None
    with pytest.raises(RuntimeError, match="Σφάλμα συνεδρίας"):
        gen.throw(RuntimeError("Σφάλμα συνεδρίας"))


def test_vasi_synthesi_set_sqlite_pragma():
    """Έλεγχος κλήσης και εξαίρεσης στο PRAGMA WAL listener (lines 34-35)."""
    from backend.app.vasi.synthesi import set_sqlite_pragma

    mock_cursor = MagicMock()

    def fake_execute(query):
        if "journal_mode=WAL" in query:
            raise RuntimeError("WAL mode not supported on in-memory mock")

    mock_cursor.execute.side_effect = fake_execute

    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    # Δεν πρέπει να εγείρει σφάλμα καθώς υπάρχει try-except pass
    set_sqlite_pragma(mock_conn, None)
    assert mock_cursor.close.called


def test_main_xeiristis_genikou_sfalmatos():
    """Έλεγχος γενικού χειριστή σφαλμάτων 500 στο main.py."""
    request_mock = MagicMock()
    exc = RuntimeError("Απρόβλεπτο σφάλμα προσομοίωσης")
    response = asyncio.run(xeiristis_genikou_sfalmatos(request_mock, exc))
    assert response.status_code == 500
    assert b"ESWTERIKO_SFALMA" in response.body
