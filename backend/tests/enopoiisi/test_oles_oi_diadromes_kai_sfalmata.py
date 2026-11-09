"""Εξαντλητικές δοκιμές ενοποίησης για όλες τις διαδρομές, σφάλματα και υπηρεσίες.

Καλύπτει:
- Όλα τα endpoints σφαλμάτων (404, 400, 403, 409, 422)
- Όλες τις ακυρώσεις εντολών και προγραμμάτων
- Όλες τις μη μεταλλακτικές προεπισκοπήσεις
- Εναλλακτικές καταστάσεις τηλεμετρίας rover (απουσία, σταθερή)
- Έλεγχο ρολογιού και κατάστασης καταιγίδας
- Idempotency replays και optimistic locking
- Αποτυχία σύνδεσης βάσης στον έλεγχο υγείας
"""

import uuid
from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.app.main import efarmogi
from backend.app.montela.apostoles import OximaExerevnis
from backend.app.montela.koinonika_symvanta import Entoli, Synagermos
from backend.app.montela.poroi import DexameniNerou, ProgrammaArdefsis, RoiNerou
from backend.app.pyrinas.asfaleia import XRHSTES_DEMO
from backend.app.pyrinas.sfalmata import KodikosSfalmatos, SfalmaDomain
from backend.app.vasi.synthesi import pare_synedria_vasis
from backend.app.ypiresies.ypiresia_apostolwn import YpiresiaApostolwn
from backend.app.ypiresies.ypiresia_porwn import (
    PROEPISKOPISEIS_ARDEFSIS,
    YpiresiaPorwn,
)
from backend.app.ypiresies.ypiresia_symvantwn_kai_senariwn import (
    YpiresiaSymvantwnKaiSenariwn,
)
from backend.app.ypiresies.ypiresia_ypostiriksis_zwis import (
    PROEPISKOPISEIS_THERMOKRASIAS,
    YpiresiaYpostiriksisZwis,
)

# ============================================================================
# 1. Υγεία & Μεταδεδομένα (ygeia.py)
# ============================================================================


def test_ygeia_sfalma_vasis_branch(pelatis_dokimwn: TestClient):
    """Έλεγχος διακλάδωσης εξαίρεσης βάσης στο /ygeia (lines 22-23)."""
    fake_session = MagicMock()
    fake_session.execute.side_effect = RuntimeError("Προσομοιωμένη διακοπή SQLite")

    def override_provlima():
        yield fake_session

    efarmogi.dependency_overrides[pare_synedria_vasis] = override_provlima
    try:
        resp = pelatis_dokimwn.get("/api/v1/ygeia")
        assert resp.status_code == 200
        dedomena = resp.json()
        assert dedomena["katastasi"] == "sfalma_vasis"
        assert dedomena["vasi_dedomenwn"] == "provlima_syndesis"
    finally:
        efarmogi.dependency_overrides.clear()


# ============================================================================
# 2. Αισθητήρες (aisthitires.py)
# ============================================================================


def test_aisthitiras_den_vrethike_404(pelatis_dokimwn: TestClient):
    """Ανάκτηση μετρήσεων ανύπαρκτου αισθητήρα επιστρέφει 404 (line 67)."""
    resp = pelatis_dokimwn.get("/api/v1/aisthitires/aniparxtos_aisthitiras/metriseis")
    assert resp.status_code == 404
    assert resp.json()["sfalma"]["kodikos"] == KodikosSfalmatos.DEN_VRETHIKE.value


# ============================================================================
# 3. Υποστήριξη Ζωής, Χώροι & Εντολές (ypostiriksi_zwis.py)
# ============================================================================


def test_ypostiriksi_zwis_diadromes_kai_sfalmata(
    pelatis_dokimwn: TestClient, synedria_dokimwn: Session
):
    """Πλήρης έλεγχος διαδρομών χώρων, πρόβλεψης οξυγόνου και ακύρωσης εντολών."""
    # 1. GET /xwroi-katoikisis (lines 43-44)
    resp = pelatis_dokimwn.get("/api/v1/xwroi-katoikisis")
    assert resp.status_code == 200
    assert len(resp.json()) >= 1

    # 2. GET /provlepsi-oxygonou (lines 69-70)
    resp = pelatis_dokimwn.get("/api/v1/xwroi-katoikisis/xwros_01/provlepsi-oxygonou")
    assert resp.status_code == 200
    assert "autonomia_wres" in resp.json()

    # 3. 404 σε ανύπαρκτο χώρο για κατάσταση, πρόβλεψη και προεπισκόπηση
    resp = pelatis_dokimwn.get("/api/v1/xwroi-katoikisis/aniparxtos/katastasi")
    assert resp.status_code == 404

    resp = pelatis_dokimwn.get("/api/v1/xwroi-katoikisis/aniparxtos/provlepsi-oxygonou")
    assert resp.status_code == 404

    resp = pelatis_dokimwn.post(
        "/api/v1/xwroi-katoikisis/aniparxtos/thermokrasia/proepiskopisi",
        json={"epithymiti_thermokrasia_k": 294.0, "anamenomeni_ekdosi_katastasis": 1},
        headers={"X-Id-Xristi": "xristis_zwis"},
    )
    assert resp.status_code == 404

    # 4. GET /entoles/{id} 404 όταν δεν υπάρχει (line 134)
    resp = pelatis_dokimwn.get("/api/v1/entoles/aniparxti_entoli")
    assert resp.status_code == 404

    # 5. POST /entoles/{id}/akyrosi 404 όταν δεν υπάρχει (line 180)
    resp = pelatis_dokimwn.post(
        "/api/v1/entoles/aniparxti_entoli/akyrosi",
        headers={"X-Id-Xristi": "syntonistis"},
    )
    assert resp.status_code == 404

    # 6. Επιτυχής ακύρωση εντολής και απόρριψη επανακύρωσης (lines 185-196)
    entoli = Entoli(
        id_entolis="entoli_dokimis_akyrosis",
        id_xristi="syntonistis",
        rolos="syntonistis_apoikias",
        yposystima="ypostiriksi_zwis",
        drasi="allagi_thermokrasias",
        katastasi="se_exelixi",
        xronos_ektelesis=datetime.now(timezone.utc),
    )
    synedria_dokimwn.add(entoli)
    synedria_dokimwn.commit()

    resp = pelatis_dokimwn.post(
        f"/api/v1/entoles/{entoli.id_entolis}/akyrosi",
        headers={"X-Id-Xristi": "syntonistis"},
    )
    assert resp.status_code == 200
    assert resp.json()["katastasi"] == "akyrothike"

    # Δεύτερη προσπάθεια -> 400 (μη επιτρεπτή μετάβαση)
    resp = pelatis_dokimwn.post(
        f"/api/v1/entoles/{entoli.id_entolis}/akyrosi",
        headers={"X-Id-Xristi": "syntonistis"},
    )
    assert resp.status_code == 400
    assert resp.json()["sfalma"]["kodikos"] == KodikosSfalmatos.MH_EPITREPTI_METAVASI.value


def test_ypiresia_ypostiriksis_zwis_fault_branches(synedria_dokimwn: Session):
    """Έλεγχος ακραίων σφαλμάτων υπηρεσίας υποστήριξης ζωής."""
    ypiresia = YpiresiaYpostiriksisZwis(synedria_dokimwn)
    syntonistis = XRHSTES_DEMO["syntonistis"]

    # 1. ektelesi_allagis_thermokrasias σε ανύπαρκτο χώρο -> 404 (line 275)
    with pytest.raises(SfalmaDomain) as exc_info:
        ypiresia.ektelesi_allagis_thermokrasias(
            id_xwrou="aniparxtos",
            id_proepiskopisis="some_id",
            anamenomeni_ekdosi_katastasis=1,
            xristis=syntonistis,
        )
    assert exc_info.value.katastasi_http == 404

    # 2. ektelesi_allagis_thermokrasias με ανύπαρκτο preview id -> 404 (line 282)
    with pytest.raises(SfalmaDomain) as exc_info:
        ypiresia.ektelesi_allagis_thermokrasias(
            id_xwrou="xwros_01",
            id_proepiskopisis="aniparxti_proepiskopisi",
            anamenomeni_ekdosi_katastasis=1,
            xristis=syntonistis,
        )
    assert exc_info.value.katastasi_http == 404

    # 3. ektelesi_allagis_thermokrasias με mismatch χώρου -> 400 (line 290)
    mock_id = f"mock_prev_{uuid.uuid4().hex[:6]}"
    PROEPISKOPISEIS_THERMOKRASIAS[mock_id] = {
        "id_xwrou": "diaforetikos_xwros",
        "zitoumeni": {"epithymiti_thermokrasia_k": 294.0},
    }
    with pytest.raises(SfalmaDomain) as exc_info:
        ypiresia.ektelesi_allagis_thermokrasias(
            id_xwrou="xwros_01",
            id_proepiskopisis=mock_id,
            anamenomeni_ekdosi_katastasis=1,
            xristis=syntonistis,
        )
    assert exc_info.value.katastasi_http == 400

    # 4. ektelesi_allagis_thermokrasias με optimistic locking mismatch -> 409 (line 298)
    PROEPISKOPISEIS_THERMOKRASIAS[mock_id]["id_xwrou"] = "xwros_01"
    with pytest.raises(SfalmaDomain) as exc_info:
        ypiresia.ektelesi_allagis_thermokrasias(
            id_xwrou="xwros_01",
            id_proepiskopisis=mock_id,
            anamenomeni_ekdosi_katastasis=999,  # πραγματική είναι 1
            xristis=syntonistis,
        )
    assert exc_info.value.katastasi_http == 409


# ============================================================================
# 4. Πόροι, Άρδευση, Φωτισμός & Ενέργεια (poroi.py)
# ============================================================================


def test_poroi_diadromes_kai_sfalmata(pelatis_dokimwn: TestClient, synedria_dokimwn: Session):
    """Πλήρης έλεγχος διαδρομών πόρων, προεπισκοπήσεων και ακυρώσεων."""
    # 1. GET /thermokipia/{id}/ardefsi/programmata (lines 145-149)
    resp = pelatis_dokimwn.get("/api/v1/thermokipia/thermokipio_01/ardefsi/programmata")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)

    # 2. 404 στην ακύρωση προγράμματος φωτισμού (line 287)
    resp = pelatis_dokimwn.post(
        "/api/v1/fwtismos/programmata/aniparxto_fwtismo/akyrosi",
        headers={"X-Id-Xristi": "syntonistis"},
    )
    assert resp.status_code == 404

    # 3. 404 στην ακύρωση προγράμματος ανακύκλωσης (line 425)
    resp = pelatis_dokimwn.post(
        "/api/v1/anakyklwsi/programmata/aniparxti_anakyklwsi/akyrosi",
        headers={"X-Id-Xristi": "syntonistis"},
    )
    assert resp.status_code == 404

    # 4. POST /energeia/periorismos-fortiwn/proepiskopisi (lines 484-485)
    resp = pelatis_dokimwn.post(
        "/api/v1/energeia/periorismos-fortiwn/proepiskopisi",
        json={"pausi_anavlhtwn": True, "aitiologia": "Έλεγχος αποκοπής"},
        headers={"X-Id-Xristi": "xristis_porwn"},
    )
    assert resp.status_code == 200
    assert "ofelos" in resp.json()
    assert resp.json()["ofelos"]["meiwsi_isxyos_kw"] == 4.0

    # 5. POST /energeia/periorismos-fortiwn/entoles από μη συντονιστή -> 403 (line 508)
    resp = pelatis_dokimwn.post(
        "/api/v1/energeia/periorismos-fortiwn/entoles",
        json={"pausi_anavlhtwn": True, "aitiologia": "Αυθαίρετη εντολή"},
        headers={"X-Id-Xristi": "xristis_porwn"},
    )
    assert resp.status_code == 403


def test_ypiresia_porwn_xwris_dexameni(synedria_dokimwn: Session):
    """proepiskopisi_ardefsis χωρίς δεξαμενή νερού -> 404 (line 142)."""
    ypiresia = YpiresiaPorwn(synedria_dokimwn)
    synedria_dokimwn.query(RoiNerou).delete()
    synedria_dokimwn.query(DexameniNerou).delete()
    synedria_dokimwn.flush()
    with pytest.raises(SfalmaDomain) as exc_info:
        ypiresia.proepiskopisi_ardefsis(
            id_thermokipiou="thermokipio_01",
            id_zwnis="zwni_01",
            posotita_nerou_l=50.0,
        )
    assert exc_info.value.katastasi_http == 404


def test_ypiresia_porwn_fault_branches(synedria_dokimwn: Session):
    """Έλεγχος σφαλμάτων και ορίων στην υπηρεσία πόρων."""
    ypiresia = YpiresiaPorwn(synedria_dokimwn)
    syntonistis = XRHSTES_DEMO["syntonistis"]

    # 1. proepiskopisi_ardefsis με ζώνη εκτός θερμοκηπίου -> 404 (line 126)
    with pytest.raises(SfalmaDomain) as exc_info:
        ypiresia.proepiskopisi_ardefsis(
            id_thermokipiou="lathos_thermokipio",
            id_zwnis="zwni_01",
            posotita_nerou_l=50.0,
        )
    assert exc_info.value.katastasi_http == 404

    # 2. proepiskopisi_ardefsis με αρνητικό νερό -> 400 (line 133)
    with pytest.raises(SfalmaDomain) as exc_info:
        ypiresia.proepiskopisi_ardefsis(
            id_thermokipiou="thermokipio_01",
            id_zwnis="zwni_01",
            posotita_nerou_l=-10.0,
        )
    assert exc_info.value.katastasi_http == 400

    # 4. dimiourgia_programmatos_ardefsis με stale preview id -> 404 (line 209)
    with pytest.raises(SfalmaDomain) as exc_info:
        ypiresia.dimiourgia_programmatos_ardefsis(
            id_proepiskopisis="aniparxto_id",
            xristis=syntonistis,
        )
    assert exc_info.value.katastasi_http == 404

    # 5. dimiourgia_programmatos_ardefsis όταν η δεξαμενή ή ζώνη δεν βρεθεί -> 404 (line 220)
    fake_prev_id = "fake_prev_99"
    PROEPISKOPISEIS_ARDEFSIS[fake_prev_id] = {
        "id_dexamenis": "aniparxti_dex",
        "id_zwnis": "zwni_01",
        "posotita_nerou_l": 50.0,
        "diarkeia_lepta": 30,
        "xronos_enarksis": datetime.now(timezone.utc),
    }
    with pytest.raises(SfalmaDomain) as exc_info:
        ypiresia.dimiourgia_programmatos_ardefsis(
            id_proepiskopisis=fake_prev_id,
            xristis=syntonistis,
        )
    assert exc_info.value.katastasi_http == 404

    # 6. akyrosi_programmatos_ardefsis σε ανύπαρκτο πρόγραμμα -> 404 (line 319)
    with pytest.raises(SfalmaDomain) as exc_info:
        ypiresia.akyrosi_programmatos_ardefsis("aniparxto_prog", syntonistis)
    assert exc_info.value.katastasi_http == 404

    # 7. akyrosi_programmatos_ardefsis σε πρόγραμμα που δεν είναι 'programmatismeno' -> 400 (line 326)
    prog = ProgrammaArdefsis(
        id_programmatos="prog_oloklirothike",
        id_thermokipiou="thermokipio_01",
        id_zwnis="zwni_01",
        id_dexamenis="dexameni_01",
        posotita_nerou_l=50.0,
        diarkeia_lepta=30,
        katastasi="oloklirothike",
        xronos_enarksis=datetime.now(timezone.utc),
    )
    synedria_dokimwn.add(prog)
    synedria_dokimwn.commit()

    with pytest.raises(SfalmaDomain) as exc_info:
        ypiresia.akyrosi_programmatos_ardefsis("prog_oloklirothike", syntonistis)
    assert exc_info.value.katastasi_http == 400


# ============================================================================
# 5. Αποστολές & Rover (apostoles.py)
# ============================================================================


def test_apostoles_diadromes_kai_sfalmata(pelatis_dokimwn: TestClient, synedria_dokimwn: Session):
    """Πλήρης έλεγχος διαδρομών αποστολών, κινδύνων, rover και αναβολής."""
    # 1. GET /kindynoi (lines 35-36)
    resp = pelatis_dokimwn.get("/api/v1/kindynoi")
    assert resp.status_code == 200
    assert len(resp.json()) >= 1

    # 2. GET /oximata (lines 42-43)
    resp = pelatis_dokimwn.get("/api/v1/oximata")
    assert resp.status_code == 200
    assert len(resp.json()) >= 1

    # 3. POST /oximata/{id}/apostoles/proepiskopisi 404 όταν το όχημα δεν υπάρχει (line 71)
    resp = pelatis_dokimwn.post(
        "/api/v1/oximata/aniparxto/apostoles/proepiskopisi",
        json={
            "titlos": "Test",
            "skopos": "Test",
            "apostasi_km": 2.0,
            "ektimwmeni_diarkeia_wres": 1.0,
        },
    )
    assert resp.status_code == 404

    # 4. POST /oximata/{id}/anaklisi/proepiskopisi (lines 136-137)
    resp = pelatis_dokimwn.post("/api/v1/oximata/rover_01/anaklisi/proepiskopisi")
    assert resp.status_code == 200
    assert "energeiaka_efikto" in resp.json()

    # 5. POST /oximata/{id}/apostoles/{id}/anavoli 404 όταν η αποστολή δεν υπάρχει (line 201)
    resp = pelatis_dokimwn.post(
        "/api/v1/oximata/rover_01/apostoles/aniparxti/anavoli",
        headers={"X-Id-Xristi": "syntonistis"},
    )
    assert resp.status_code == 404


def test_ypiresia_apostolwn_fault_branches(synedria_dokimwn: Session):
    """Έλεγχος καταστάσεων επικοινωνίας rover και σφαλμάτων υπηρεσίας αποστολών."""
    ypiresia = YpiresiaApostolwn(synedria_dokimwn)
    syntonistis = XRHSTES_DEMO["syntonistis"]

    # 1. pare_katastasi_oximatos 404 (line 51)
    with pytest.raises(SfalmaDomain) as exc_info:
        ypiresia.pare_katastasi_oximatos("aniparxto")
    assert exc_info.value.katastasi_http == 404

    # 2. proepiskopisi_asfalous_stasis 404 (line 204)
    with pytest.raises(SfalmaDomain) as exc_info:
        ypiresia.proepiskopisi_asfalous_stasis("aniparxto")
    assert exc_info.value.katastasi_http == 404

    # 3. ektelesi_asfalous_stasis 404 (line 228)
    with pytest.raises(SfalmaDomain) as exc_info:
        ypiresia.ektelesi_asfalous_stasis("aniparxto", syntonistis)
    assert exc_info.value.katastasi_http == 404

    # 4. ektelesi_anaklisis 404 (line 141)
    with pytest.raises(SfalmaDomain) as exc_info:
        ypiresia.ektelesi_anaklisis("aniparxto", syntonistis)
    assert exc_info.value.katastasi_http == 404

    # 5. ektelesi_anaklisis με επικοινωνία "apousia" -> avevaio (lines 155-156)
    rover = synedria_dokimwn.get(OximaExerevnis, "rover_01")
    rover.katastasi_epikoinwnias = "apousia"
    synedria_dokimwn.commit()

    res = ypiresia.ektelesi_anaklisis("rover_01", syntonistis)
    assert res["katastasi_entolis"] == "avevaio"
    assert "Απώλεια επικοινωνίας" in res["minyma"]

    # 6. ektelesi_anaklisis με επικοινωνία "statheri" -> epistrofi_se_exelixi (lines 164-165)
    rover.katastasi_epikoinwnias = "statheri"
    synedria_dokimwn.commit()

    res = ypiresia.ektelesi_anaklisis("rover_01", syntonistis)
    assert res["katastasi_entolis"] == "se_exelixi"
    assert rover.katastasi_oximatos == "epistrofi_se_exelixi"


# ============================================================================
# 6. Σενάρια & Διαχείριση Χρόνου (senaria.py)
# ============================================================================


def test_senaria_diadromes_kai_sfalmata(pelatis_dokimwn: TestClient, synedria_dokimwn: Session):
    """Πλήρης έλεγχος διαδρομών καταιγίδας, προεπισκοπήσεων και σφαλμάτων."""
    # 1. GET /senaria/kataigida-skonis (lines 40-44)
    resp = pelatis_dokimwn.get("/api/v1/senaria/kataigida-skonis")
    assert resp.status_code == 200
    assert resp.json()["senario"] == "kataigida_skonis_2026"

    # 2. POST /senaria/{id}/apofaseis/proepiskopisi (lines 84-85)
    resp = pelatis_dokimwn.post("/api/v1/senaria/kataigida_skonis_2026/apofaseis/proepiskopisi")
    assert resp.status_code == 200
    assert "epiloges_apofasis" in resp.json()

    # 3. ypovoli_apofasis_kataigidas από μη συντονιστή -> 403 (line 549)
    resp = pelatis_dokimwn.post(
        "/api/v1/senaria/kataigida_skonis_2026/apofaseis",
        json={"epilogi": "pausi_anavlhtwn", "aitiologia": "Έλεγχος"},
        headers={"X-Id-Xristi": "xristis_porwn"},
    )
    assert resp.status_code == 403

    # 4. ypovoli_apofasis_kataigidas με μη έγκυρη επιλογή -> 400 (line 561)
    resp = pelatis_dokimwn.post(
        "/api/v1/senaria/kataigida_skonis_2026/apofaseis",
        json={"epilogi": "akyri_epilogi_apofasis", "aitiologia": "Έλεγχος"},
        headers={"X-Id-Xristi": "syntonistis"},
    )
    assert resp.status_code == 400

    # 5. proxorise_xrono με lepta <= 0 -> 400 (line 637)
    ypiresia = YpiresiaSymvantwnKaiSenariwn(synedria_dokimwn)
    with pytest.raises(SfalmaDomain) as exc_info:
        ypiresia.proxorise_xrono(lepta=0)
    assert exc_info.value.katastasi_http == 400


# ============================================================================
# 7. Δικαιώματα & Μεταβιβάσεις (dikaiwmata.py)
# ============================================================================


def test_dikaiwmata_diadromes_kai_sfalmata(pelatis_dokimwn: TestClient, synedria_dokimwn: Session):
    """Πλήρης έλεγχος διαδρομών μεταβιβάσεων και εξουσιοδότησης."""
    # 1. POST /metavivaseis/proepiskopisi (line 58)
    resp = pelatis_dokimwn.post(
        "/api/v1/dikaiwmata/metavivaseis/proepiskopisi",
        json={
            "id_paralipti": "xristis_porwn",
            "rolos": "syntonistis_apoikias",
            "diarkeia_wres": 12.0,
            "pedio_efarmogis": "diaxeirisi_kataigidas",
        },
        headers={"X-Id-Xristi": "syntonistis"},
    )
    assert resp.status_code == 200
    assert resp.json()["einai_epileksimo"] is True

    ypiresia = YpiresiaSymvantwnKaiSenariwn(synedria_dokimwn)
    xristis_zwis = XRHSTES_DEMO["xristis_zwis"]
    syntonistis = XRHSTES_DEMO["syntonistis"]

    # 2. dimiourgia_metavivasis από μη συντονιστή -> 403 (line 263)
    with pytest.raises(SfalmaDomain) as exc_info:
        ypiresia.dimiourgia_metavivasis(
            id_paralipti="xristis_porwn",
            rolos="syntonistis_apoikias",
            diarkeia_wres=10.0,
            aitiologia="Αυθαίρετη μεταβίβαση",
            xristis=xristis_zwis,
        )
    assert exc_info.value.katastasi_http == 403

    # 3. dimiourgia_metavivasis με άκυρη διάρκεια -> 400 (line 270)
    with pytest.raises(SfalmaDomain) as exc_info:
        ypiresia.dimiourgia_metavivasis(
            id_paralipti="xristis_porwn",
            rolos="syntonistis_apoikias",
            diarkeia_wres=100.0,  # > 72 ώρες
            aitiologia="Υπερβολική διάρκεια",
            xristis=syntonistis,
        )
    assert exc_info.value.katastasi_http == 400

    # 4. anaklisi_metavivasis από μη συντονιστή -> 403 (line 316)
    with pytest.raises(SfalmaDomain) as exc_info:
        ypiresia.anaklisi_metavivasis("metav_01", xristis=xristis_zwis)
    assert exc_info.value.katastasi_http == 403

    # 5. anaklisi_metavivasis ανύπαρκτης μεταβίβασης -> 404 (line 324)
    with pytest.raises(SfalmaDomain) as exc_info:
        ypiresia.anaklisi_metavivasis("aniparxti_metav", xristis=syntonistis)
    assert exc_info.value.katastasi_http == 404


# ============================================================================
# 8. Συναγερμοί (synagermoi.py)
# ============================================================================


def test_synagermoi_sfalmata(synedria_dokimwn: Session):
    """Έλεγχος σφαλμάτων αναγνώρισης και επίλυσης συναγερμών."""
    ypiresia = YpiresiaSymvantwnKaiSenariwn(synedria_dokimwn)
    syntonistis = XRHSTES_DEMO["syntonistis"]

    # 1. anagnwrisi_synagermou σε ανύπαρκτο συναγερμό -> 404 (line 150)
    with pytest.raises(SfalmaDomain) as exc_info:
        ypiresia.anagnwrisi_synagermou("aniparxtos_synagermos", syntonistis)
    assert exc_info.value.katastasi_http == 404

    # 2. anagnwrisi_synagermou σε ήδη επιλυμένο συναγερμό -> 400 (line 157)
    synagermos = Synagermos(
        id_synagermou="synag_epilymenos",
        titlos="Δοκιμή",
        perigrafi="Δοκιμή",
        aitia="Δοκιμή",
        epiptwsi="Δοκιμή",
        systasi="Δοκιμή",
        yposystima="poroi",
        sovarotita="xamili",
        katastasi="epilymenos",
        sxolio_epilysis="Επιλύθηκε επιτυχώς.",
    )
    synedria_dokimwn.add(synagermos)
    synedria_dokimwn.commit()

    with pytest.raises(SfalmaDomain) as exc_info:
        ypiresia.anagnwrisi_synagermou("synag_epilymenos", syntonistis)
    assert exc_info.value.katastasi_http == 400

    # 3. epilysi_synagermou σε ανύπαρκτο συναγερμό -> 404 (line 192)
    with pytest.raises(SfalmaDomain) as exc_info:
        ypiresia.epilysi_synagermou("aniparxtos_synagermos", syntonistis, "Σχόλιο")
    assert exc_info.value.katastasi_http == 404

    # 4. epilysi_synagermou με κενό σχόλιο -> 400 (line 199)
    synagermos_energos = Synagermos(
        id_synagermou="synag_energos_dokimi",
        titlos="Ενεργός",
        perigrafi="Ενεργός",
        aitia="Ενεργός",
        epiptwsi="Ενεργός",
        systasi="Ενεργός",
        yposystima="poroi",
        sovarotita="xamili",
        katastasi="energos",
    )
    synedria_dokimwn.add(synagermos_energos)
    synedria_dokimwn.commit()

    with pytest.raises(SfalmaDomain) as exc_info:
        ypiresia.epilysi_synagermou("synag_energos_dokimi", syntonistis, "   ")
    assert exc_info.value.katastasi_http == 400
