"""Εξαντλητικές δοκιμές ενοποίησης για πλήρη κάλυψη όλων των υπηρεσιών και διαδρομών σφάλματος."""

from datetime import datetime, timezone

import pytest
from sqlalchemy.orm import Session

from backend.app.pyrinas.asfaleia import DedomenaXristi, RolosXristi
from backend.app.pyrinas.sfalmata import SfalmaDomain
from backend.app.ypiresies.ypiresia_apostolwn import YpiresiaApostolwn
from backend.app.ypiresies.ypiresia_porwn import (
    YpiresiaPorwn,
)
from backend.app.ypiresies.ypiresia_ypostiriksis_zwis import (
    PROEPISKOPISEIS_THERMOKRASIAS,
    YpiresiaYpostiriksisZwis,
)


def test_ypiresia_ypostiriksis_zwis_sfalmata(synedria_dokimwn: Session):
    """Ελέγχει σφάλματα και ακραίες περιπτώσεις στην υπηρεσία υποστήριξης ζωής."""
    ypiresia = YpiresiaYpostiriksisZwis(synedria_dokimwn)
    xristis = DedomenaXristi(
        id_xristi="xristis_01",
        onoma="Life Officer",
        vasikos_rolos=RolosXristi.YPEFTHYNOS_YPOSTIRIKSIS_ZWIS,
        energoi_roloi=[RolosXristi.YPEFTHYNOS_YPOSTIRIKSIS_ZWIS],
    )

    # 1. Χώρος δεν βρέθηκε (404)
    with pytest.raises(SfalmaDomain) as exc:
        ypiresia.pare_katastasi_xwrou("mh_yparktos_xwros")
    assert exc.value.katastasi_http == 404

    with pytest.raises(SfalmaDomain) as exc:
        ypiresia.provlepsi_oxygonou("mh_yparktos_xwros")
    assert exc.value.katastasi_http == 404

    with pytest.raises(SfalmaDomain) as exc:
        ypiresia.proepiskopisi_allagis_thermokrasias("mh_yparktos_xwros", 295.0, 1)
    assert exc.value.katastasi_http == 404

    # 2. Θερμοκρασία εκτός ορίων (400)
    with pytest.raises(SfalmaDomain) as exc:
        ypiresia.proepiskopisi_allagis_thermokrasias("xwros_01", 200.0, 1)
    assert exc.value.katastasi_http == 400

    # 3. Stale version (409)
    with pytest.raises(SfalmaDomain) as exc:
        ypiresia.proepiskopisi_allagis_thermokrasias("xwros_01", 295.0, 999)
    assert exc.value.katastasi_http == 409

    # 4. Μη έγκυρη προεπισκόπηση κατά την εκτέλεση (404)
    with pytest.raises(SfalmaDomain) as exc:
        ypiresia.ektelesi_allagis_thermokrasias("xwros_01", "mh_yparrkti_proep", 1, xristis)
    assert exc.value.katastasi_http == 404

    # 5. Stale version κατά την εκτέλεση (409)
    PROEPISKOPISEIS_THERMOKRASIAS["fake_proep"] = {
        "id_xwrou": "xwros_01",
        "epithymiti_thermokrasia_k": 294.0,
        "xronos_dimiourgias": datetime.now(timezone.utc),
    }
    with pytest.raises(SfalmaDomain) as exc:
        ypiresia.ektelesi_allagis_thermokrasias("xwros_01", "fake_proep", 999, xristis)
    assert exc.value.katastasi_http == 409


def test_ypiresia_porwn_sfalmata_kai_akyroseis(synedria_dokimwn: Session):
    """Ελέγχει σφάλματα, ακυρώσεις και ακραίες τιμές στην υπηρεσία πόρων."""
    ypiresia = YpiresiaPorwn(synedria_dokimwn)
    xristis = DedomenaXristi(
        id_xristi="xristis_02",
        onoma="Resource Officer",
        vasikos_rolos=RolosXristi.YPEFTHYNOS_PORWN,
        energoi_roloi=[RolosXristi.YPEFTHYNOS_PORWN],
    )
    syntonistis = DedomenaXristi(
        id_xristi="syntonistis",
        onoma="Coordinator",
        vasikos_rolos=RolosXristi.SYNTONISTIS_APOIKIAS,
        energoi_roloi=[RolosXristi.SYNTONISTIS_APOIKIAS],
    )

    # 1. Θερμοκήπιο ή ζώνη δεν βρέθηκε (404)
    with pytest.raises(SfalmaDomain) as exc:
        ypiresia.proepiskopisi_ardefsis("mh_yparrktos", "zwni_01", 50.0, 30)
    assert exc.value.katastasi_http == 404

    with pytest.raises(SfalmaDomain) as exc:
        ypiresia.proepiskopisi_ardefsis("thermokipio_01", "mh_yparrkti_zwni", 50.0, 30)
    assert exc.value.katastasi_http == 404

    # 2. Προεπισκόπηση δεν βρέθηκε κατά την επιβεβαίωση (404)
    with pytest.raises(SfalmaDomain) as exc:
        ypiresia.dimiourgia_programmatos_ardefsis("mh_yparrkti_proep", xristis)
    assert exc.value.katastasi_http == 404

    # 3. Ακύρωση προγράμματος που δεν υπάρχει (404)
    with pytest.raises(SfalmaDomain) as exc:
        ypiresia.akyrosi_programmatos_ardefsis("mh_yparrkto_prog", xristis)
    assert exc.value.katastasi_http == 404

    # 4. Περιορισμός φορτίων: μη εξουσιοδοτημένος χρήστης (403)
    with pytest.raises(SfalmaDomain) as exc:
        ypiresia.ektelesi_periorismou_fortiwn(
            pausi_anavlhtwn=True, xristis=xristis, aitiologia="Dokimi"
        )
    assert exc.value.katastasi_http == 403

    # 5. Περιορισμός φορτίων: επιτυχής εκτέλεση από συντονιστή
    res_shed = ypiresia.ektelesi_periorismou_fortiwn(
        pausi_anavlhtwn=True, xristis=syntonistis, aitiologia="Test Curtailment"
    )
    assert res_shed["pausi_anavlhtwn"] is True
    assert res_shed["arithmos_fortiwn_pou_allaksan"] >= 0


def test_ypiresia_apostolwn_sfalmata_kai_safe_stop(synedria_dokimwn: Session):
    """Ελέγχει σφάλματα, rover safe stop και αναβολές στην υπηρεσία αποστολών."""
    ypiresia = YpiresiaApostolwn(synedria_dokimwn)
    xeiristis = DedomenaXristi(
        id_xristi="xristis_03",
        onoma="Rover Operator",
        vasikos_rolos=RolosXristi.YPEFTHYNOS_APOSTOLWN,
        energoi_roloi=[RolosXristi.YPEFTHYNOS_APOSTOLWN],
    )

    # 1. Rover δεν βρέθηκε (404)
    with pytest.raises(SfalmaDomain) as exc:
        ypiresia.pare_katastasi_oximatos("mh_yparrkto_rover")
    assert exc.value.katastasi_http == 404

    with pytest.raises(SfalmaDomain) as exc:
        ypiresia.proepiskopisi_anaklisis("mh_yparrkto_rover")
    assert exc.value.katastasi_http == 404

    with pytest.raises(SfalmaDomain) as exc:
        ypiresia.ektelesi_asfalous_stasis("mh_yparrkto_rover", xeiristis)
    assert exc.value.katastasi_http == 404

    # 2. Προεπισκόπηση ασφαλούς στάσης
    preview_stop = ypiresia.proepiskopisi_asfalous_stasis("rover_01")
    assert preview_stop["protinomeni_drasi"] == "asfalis_stasi"
    assert preview_stop["apaiteitai_epivevaiwsi"] is True
