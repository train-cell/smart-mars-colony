"""Ακραίες είσοδοι και έλεγχοι αβεβαιότητας των δημόσιων συμβολαίων."""

import math
from datetime import datetime, timedelta, timezone

import pytest

from backend.app.fysika_montela.fysika_montela import (
    ypologise_apothema_kai_autonomia_oxygonou,
    ypologise_energeia_kinisis_oximatos,
)
from backend.app.montela.apostoles import OximaExerevnis
from backend.app.montela.koinonika_symvanta import Entoli
from backend.app.prosomoiwsi.prosomoiosis_apostolwn import proxorise_apostoles
from backend.app.ypiresies.energeiaki_trofodosia import ypologise_katanomi_fortiwn


@pytest.mark.parametrize("timi", ["Infinity", "NaN", -1, 0])
def test_mi_egkyri_isxys_fwtismou_den_apothikevetai(pelatis_dokimwn, timi):
    stoixeio_alfa = pelatis_dokimwn.post(
        "/api/v1/thermokipia/thermokipio_01/fwtismos/proepiskopisi",
        json={"id_zwnis": "zwni_01", "isxys_kw": timi},
    )
    assert stoixeio_alfa.status_code == 422, stoixeio_alfa.text
    assert (
        pelatis_dokimwn.get("/api/v1/thermokipia/thermokipio_01/fwtismos/programmata").json() == []
    )


def test_yperxeilisi_eisodou_dinei_sfalma_epikyrwsis(pelatis_dokimwn):
    stoixeio_alfa = pelatis_dokimwn.post(
        "/api/v1/prosomoiwsi/vima",
        content='{"lepta":1e309}',
        headers={"Content-Type": "application/json"},
    )
    assert stoixeio_alfa.status_code == 422
    assert stoixeio_alfa.json()["sfalma"]["kodikos"] == "AKYRI_TIMI"


def test_oxygono_katw_apo_katwfli_me_paragwgi_paramenei_kindynos():
    apotelesma = ypologise_apothema_kai_autonomia_oxygonou(100, 293, 10000, 16000, 6, 0.04, 0.3)
    assert apotelesma[2] == 0
    assert apotelesma[3] == "katwfli_paraviasmeno"


@pytest.mark.parametrize(
    "klisi", [math.pi, -math.pi, math.pi / 2, -math.pi / 2, math.inf, math.nan]
)
def test_anefikti_klisi_aporriptetai(klisi):
    with pytest.raises(ValueError):
        ypologise_energeia_kinisis_oximatos(1000, 1000, klisi_rad=klisi)


def test_epanafora_akyronei_palies_proepiskopiseis(pelatis_dokimwn):
    stoixeio_pi = pelatis_dokimwn.post(
        "/api/v1/thermokipia/thermokipio_01/ardefsi/proepiskopisi",
        json={"id_zwnis": "zwni_01", "posotita_nerou_l": 100},
    ).json()
    assert (
        pelatis_dokimwn.post(
            "/api/v1/prosomoiwsi/epanafora", json={"epivevaiwsi": True}
        ).status_code
        == 200
    )
    stoixeio_alfa = pelatis_dokimwn.post(
        "/api/v1/thermokipia/thermokipio_01/ardefsi/programmata",
        json={"id_proepiskopisis": stoixeio_pi["id_proepiskopisis"]},
    )
    assert stoixeio_alfa.status_code in {404, 409}


def test_rover_eksantlisi_mpatarias_kata_tin_epistrofi(synedria_dokimwn):
    """Εξάντληση μπαταρίας rover κατά τη διαδρομή επιστροφής οδηγεί σε ανάγκη ενέργειας."""
    oxima = synedria_dokimwn.get(OximaExerevnis, "rover_01")
    oxima.katastasi_oximatos = "epistrofi_se_exelixi"
    oxima.apostasi_apo_vasi_km = 4.0
    oxima.taxytita_kmh = 4.0
    oxima.isxys_kinisis_kw = 0.6
    oxima.energeia_kwh = 0.22
    oxima.efedreia_kwh = 0.20
    oxima.katastasi_epikoinwnias = "statheri"

    entoli = Entoli(
        id_entolis="entoli_anaklisis_test_oria",
        id_xristi="xristis_apostolwn",
        rolos="ypefthynos_apostolwn",
        yposystima="apostoles",
        drasi="anaklisi_oximatos",
        id_ontotitas="rover_01",
        katastasi="se_exelixi",
        apotypwma_aitimatos="apotypwma_test",
        dedomena_aitimatos={},
        apotelesma={},
    )
    synedria_dokimwn.add(entoli)
    synedria_dokimwn.commit()

    apo = datetime(2026, 11, 10, 12, 0, tzinfo=timezone.utc)
    ews = apo + timedelta(hours=1)

    proxorise_apostoles(synedria_dokimwn, apo, ews)
    synedria_dokimwn.commit()

    assert oxima.katastasi_oximatos == "anagki_energeias"
    assert entoli.katastasi == "apetyxe"
    assert "Δεν επαρκεί πλέον η εφεδρεία επιστροφής" in (
        entoli.symvanta[-1].minyma if entoli.symvanta else ""
    )
    assert oxima.energeia_kwh >= 0.0


def test_dipli_akyrosi_programmatos_dinei_409(pelatis_dokimwn):
    """Δεύτερη απόπειρα ακύρωσης ήδη ακυρωμένου προγράμματος επιστρέφει 409 Conflict."""
    apantisi_proep = pelatis_dokimwn.post(
        "/api/v1/thermokipia/thermokipio_01/ardefsi/proepiskopisi",
        json={"id_zwnis": "zwni_01", "posotita_nerou_l": 50.0, "diarkeia_lepta": 30},
        headers={"X-Id-Xristi": "xristis_porwn"},
    )
    assert apantisi_proep.status_code == 200
    id_proep = apantisi_proep.json()["id_proepiskopisis"]

    apantisi_dim = pelatis_dokimwn.post(
        "/api/v1/thermokipia/thermokipio_01/ardefsi/programmata",
        json={"id_proepiskopisis": id_proep},
        headers={"X-Id-Xristi": "xristis_porwn"},
    )
    assert apantisi_dim.status_code == 200
    id_prog = apantisi_dim.json()["id_programmatos"]

    apantisi_ak1 = pelatis_dokimwn.post(
        f"/api/v1/ardefsi/programmata/{id_prog}/akyrosi",
        headers={"X-Id-Xristi": "xristis_porwn"},
    )
    assert apantisi_ak1.status_code == 200
    assert apantisi_ak1.json()["katastasi"] == "akyrothike"

    apantisi_ak2 = pelatis_dokimwn.post(
        f"/api/v1/ardefsi/programmata/{id_prog}/akyrosi",
        headers={"X-Id-Xristi": "xristis_porwn"},
    )
    assert apantisi_ak2.status_code == 409
    assert apantisi_ak2.json()["sfalma"]["kodikos"] == "MH_EPITREPTI_METAVASI"


def test_ardefsi_akrivws_iso_me_diathesimo_apothema(pelatis_dokimwn):
    """Αίτηση για το 100% του διαθέσιμου νερού άνω εφεδρείας επιτυγχάνει και μηδενίζει το υπόλοιπο."""
    apantisi_dexamenes = pelatis_dokimwn.get("/api/v1/nero/dexamenes")
    assert apantisi_dexamenes.status_code == 200
    dexameni = apantisi_dexamenes.json()["dexamenes"][0]
    diathesimo = dexameni["trexwn_ogkos_l"] - dexameni["efedreia_asfaleias_l"]
    assert diathesimo > 0

    apantisi_proep = pelatis_dokimwn.post(
        "/api/v1/thermokipia/thermokipio_01/ardefsi/proepiskopisi",
        json={"id_zwnis": "zwni_01", "posotita_nerou_l": diathesimo, "diarkeia_lepta": 30},
        headers={"X-Id-Xristi": "xristis_porwn"},
    )
    assert apantisi_proep.status_code == 200
    id_proep = apantisi_proep.json()["id_proepiskopisis"]

    apantisi_dim = pelatis_dokimwn.post(
        "/api/v1/thermokipia/thermokipio_01/ardefsi/programmata",
        json={"id_proepiskopisis": id_proep},
        headers={"X-Id-Xristi": "xristis_porwn"},
    )
    assert apantisi_dim.status_code == 200

    apantisi_aporripsi = pelatis_dokimwn.post(
        "/api/v1/thermokipia/thermokipio_01/ardefsi/proepiskopisi",
        json={"id_zwnis": "zwni_02", "posotita_nerou_l": 1.0, "diarkeia_lepta": 30},
        headers={"X-Id-Xristi": "xristis_porwn"},
    )
    assert apantisi_aporripsi.status_code == 409
    assert apantisi_aporripsi.json()["sfalma"]["kodikos"] == "ANEPARKES_NERO"


def test_proepiskopisi_lhgei_meta_apo_vima_xronou_prosomoiwsis(pelatis_dokimwn):
    """Προεπισκόπηση καθίσταται άκυρη μετά από προώθηση του χρόνου προσομοίωσης πέραν του TTL."""
    apantisi_proep = pelatis_dokimwn.post(
        "/api/v1/thermokipia/thermokipio_01/ardefsi/proepiskopisi",
        json={"id_zwnis": "zwni_01", "posotita_nerou_l": 20.0, "diarkeia_lepta": 15},
        headers={"X-Id-Xristi": "xristis_porwn"},
    )
    assert apantisi_proep.status_code == 200
    id_proep = apantisi_proep.json()["id_proepiskopisis"]

    apantisi_vima = pelatis_dokimwn.post(
        "/api/v1/prosomoiwsi/vima",
        json={"lepta": 16.0},
    )
    assert apantisi_vima.status_code == 200

    apantisi_epiv = pelatis_dokimwn.post(
        "/api/v1/thermokipia/thermokipio_01/ardefsi/programmata",
        json={"id_proepiskopisis": id_proep},
        headers={"X-Id-Xristi": "xristis_porwn"},
    )
    assert apantisi_epiv.status_code == 409
    assert apantisi_epiv.json()["sfalma"]["kodikos"] == "PALIA_PROEPISKOPISI"


def test_idempotency_key_mismatch_payload_dinei_409(pelatis_dokimwn):
    """Αποστολή του ίδιου Idempotency-Key με διαφορετικά δεδομένα επιστρέφει 409 SYNTHIKI_SYGGROUSIS."""
    p1 = pelatis_dokimwn.post(
        "/api/v1/thermokipia/thermokipio_01/ardefsi/proepiskopisi",
        json={"id_zwnis": "zwni_01", "posotita_nerou_l": 15.0, "diarkeia_lepta": 15},
        headers={"X-Id-Xristi": "xristis_porwn"},
    ).json()["id_proepiskopisis"]

    p2 = pelatis_dokimwn.post(
        "/api/v1/thermokipia/thermokipio_01/ardefsi/proepiskopisi",
        json={"id_zwnis": "zwni_01", "posotita_nerou_l": 25.0, "diarkeia_lepta": 15},
        headers={"X-Id-Xristi": "xristis_porwn"},
    ).json()["id_proepiskopisis"]

    kleidi = "dokimi_idempotency_mismatch_999"
    kefalides = {"X-Id-Xristi": "xristis_porwn", "Idempotency-Key": kleidi}

    r1 = pelatis_dokimwn.post(
        "/api/v1/thermokipia/thermokipio_01/ardefsi/programmata",
        json={"id_proepiskopisis": p1},
        headers=kefalides,
    )
    assert r1.status_code == 200

    r2 = pelatis_dokimwn.post(
        "/api/v1/thermokipia/thermokipio_01/ardefsi/programmata",
        json={"id_proepiskopisis": p1},
        headers=kefalides,
    )
    assert r2.status_code == 200
    assert r2.json()["id_programmatos"] == r1.json()["id_programmatos"]

    r3 = pelatis_dokimwn.post(
        "/api/v1/thermokipia/thermokipio_01/ardefsi/programmata",
        json={"id_proepiskopisis": p2},
        headers=kefalides,
    )
    assert r3.status_code == 409
    assert r3.json()["sfalma"]["kodikos"] == "SYNTHIKI_SYGGROUSIS"


def test_apokopi_fortiwn_kai_antagwnismos_proteraiotitas():
    """Κατανομή ισχύος υπό περιορισμό: κρίσιμα πρώτα, μετά κατά προτεραιότητα και απόρριψη αδιαίρετων."""
    fortia = [
        {
            "id_fortiou": "f1_krisimo",
            "isxys_kw": 5.0,
            "energo": True,
            "einai_krisimo": True,
            "proteraiotita": 1,
            "apaitei_pliri_trofodosia": False,
        },
        {
            "id_fortiou": "f2_ypsilis",
            "isxys_kw": 3.0,
            "energo": True,
            "einai_krisimo": False,
            "proteraiotita": 1,
            "apaitei_pliri_trofodosia": False,
        },
        {
            "id_fortiou": "f3_xamilis",
            "isxys_kw": 4.0,
            "energo": True,
            "einai_krisimo": False,
            "proteraiotita": 2,
            "apaitei_pliri_trofodosia": False,
        },
        {
            "id_fortiou": "f4_adiaireto",
            "isxys_kw": 2.0,
            "energo": True,
            "einai_krisimo": False,
            "proteraiotita": 3,
            "apaitei_pliri_trofodosia": True,
        },
    ]
    apotelesma = ypologise_katanomi_fortiwn(fortia, 7.0)
    assert apotelesma["ana_fortio"]["f1_krisimo"]["paradidomeni_kw"] == pytest.approx(5.0)
    assert apotelesma["ana_fortio"]["f2_ypsilis"]["paradidomeni_kw"] == pytest.approx(2.0)
    assert apotelesma["ana_fortio"]["f3_xamilis"]["paradidomeni_kw"] == pytest.approx(0.0)
    assert apotelesma["ana_fortio"]["f4_adiaireto"]["paradidomeni_kw"] == pytest.approx(0.0)
    assert apotelesma["paradidomeni_kw"] == pytest.approx(7.0)
    assert apotelesma["mi_kalyptomeni_kw"] == pytest.approx(7.0)
