"""Δοκιμές ολοκληρωμένου σεναρίου καταιγίδας σκόνης (STORM-01…10, TEST-02, TEST-15, TEST-20)."""

import pytest
from fastapi.testclient import TestClient


def test_kataigida_pliris_diadromi(pelatis_dokimwn: TestClient):
    """STORM-01 έως STORM-10: Πλήρης αλυσίδα σεναρίου καταιγίδας σκόνης με τα αριθμητικά golden αποτελέσματα (§6)."""
    # ------------------------------------------------------------------------
    # 1. Έλεγχος Baseline Συνθηκών (§6 Golden Fixture)
    # ------------------------------------------------------------------------
    apantisi_synopsis = pelatis_dokimwn.get("/api/v1/synopsi")
    assert apantisi_synopsis.status_code == 200
    dedomena_arxika = apantisi_synopsis.json()

    # PV baseline = 4.8 kW, Θέρμανση = 8.0 kW, Έλλειμμα = 9.2 kW, Αυτονομία = 30 / 9.2 ≈ 3.26 h
    assert dedomena_arxika["energeia"]["paragwgi_kw"] == pytest.approx(4.8, rel=1e-3)
    assert dedomena_arxika["energeia"]["elleimma_kw"] == pytest.approx(9.2, rel=1e-3)
    assert dedomena_arxika["energeia"]["autonomia_wres"] == pytest.approx(30.0 / 9.2, rel=1e-3)

    # ------------------------------------------------------------------------
    # 2. Προεπισκόπηση Σεναρίου Καταιγίδας (§6 Υπολογισμοί)
    # ------------------------------------------------------------------------
    apantisi_proep = pelatis_dokimwn.post("/api/v1/senaria/kataigida-skonis/proepiskopisi")
    assert apantisi_proep.status_code == 200
    proep = apantisi_proep.json()
    statistika = proep["statistika_senariou"]

    # Επαλήθευση ακριβών τιμών παραγράφου §6:
    assert statistika["fwtovoltaika"]["arxiki_kw"] == pytest.approx(4.8, rel=1e-3)
    assert statistika["fwtovoltaika"]["kataigida_kw"] == pytest.approx(0.8, rel=1e-3)
    assert statistika["fwtovoltaika"]["ptwsi_kw"] == pytest.approx(4.0, rel=1e-3)

    assert statistika["thermansi"]["arxiki_kw"] == pytest.approx(8.0, rel=1e-3)
    assert statistika["thermansi"]["kataigida_kw"] == pytest.approx(10.0, rel=1e-3)
    assert statistika["thermansi"]["afksisi_kw"] == pytest.approx(2.0, rel=1e-3)

    assert statistika["fortia_kai_autonomia"]["arxiki_katastasi"]["elleimma_kw"] == pytest.approx(
        9.2, rel=1e-3
    )
    assert statistika["fortia_kai_autonomia"]["arxiki_katastasi"][
        "autonomia_wres"
    ] == pytest.approx(3.26087, rel=1e-3)

    assert statistika["fortia_kai_autonomia"]["kataigida_me_anavlita"][
        "elleimma_kw"
    ] == pytest.approx(15.2, rel=1e-3)
    assert statistika["fortia_kai_autonomia"]["kataigida_me_anavlita"][
        "autonomia_wres"
    ] == pytest.approx(1.97368, rel=1e-3)

    assert statistika["fortia_kai_autonomia"]["kataigida_me_pausi_anavlhtwn"][
        "elleimma_kw"
    ] == pytest.approx(11.2, rel=1e-3)
    assert statistika["fortia_kai_autonomia"]["kataigida_me_pausi_anavlhtwn"][
        "autonomia_wres"
    ] == pytest.approx(2.67857, rel=1e-3)
    assert statistika["fortia_kai_autonomia"]["kataigida_me_pausi_anavlhtwn"][
        "kerdos_lepta"
    ] == pytest.approx(42.29, rel=1e-2)

    # Έλεγχος rover επιστροφής
    assert statistika["oxima"]["xronos_epistrofis_wres"] == 0.5
    assert statistika["oxima"]["apaitoumeni_energeia_kwh"] == 0.3
    assert statistika["oxima"]["energeiaka_efikto"] is True
    assert statistika["oxima"]["oratotita_asfalis"] is False
    assert statistika["oxima"]["synolika_asfalis_epistrofi"] is False

    # ------------------------------------------------------------------------
    # 3. Ενεργοποίηση Καταιγίδας (STORM-02)
    # ------------------------------------------------------------------------
    apantisi_energ = pelatis_dokimwn.post(
        "/api/v1/senaria/kataigida-skonis/energopoiisi",
        headers={"X-Id-Xristi": "syntonistis"},
    )
    assert apantisi_energ.status_code == 200
    assert apantisi_energ.json()["katastasi"] == "energi"

    # Έλεγχος ότι η παραγωγή PV έπεσε στα 0.8 kW και η θέρμανση ανέβηκε στα 10 kW
    synopsi_kataigidas = pelatis_dokimwn.get("/api/v1/synopsi").json()
    assert synopsi_kataigidas["energeia"]["paragwgi_kw"] == pytest.approx(0.8, rel=1e-3)
    assert synopsi_kataigidas["energeia"]["elleimma_kw"] == pytest.approx(15.2, rel=1e-3)
    assert synopsi_kataigidas["energeia"]["autonomia_wres"] == pytest.approx(1.97368, rel=1e-3)

    # ------------------------------------------------------------------------
    # 4. Έγκριση και Εκτέλεση Απόφασης Συντονιστή (STORM-06, STORM-08)
    # ------------------------------------------------------------------------
    nea_proep = pelatis_dokimwn.post("/api/v1/senaria/kataigida-skonis/proepiskopisi").json()
    apantisi_apofasis = pelatis_dokimwn.post(
        "/api/v1/senaria/kataigida_skonis_2026/apofaseis",
        json={
            "id_proepiskopisis": nea_proep["id_proepiskopisis"],
            "epilogi": "syndyasmos_pliroys_asfaleias",
            "aitiologia": "Έγκριση συντονιστή: παύση αναβλητών φορτίων και ασφαλής στάση rover",
        },
        headers={"X-Id-Xristi": "syntonistis"},
    )
    assert apantisi_apofasis.status_code == 200
    assert apantisi_apofasis.json()["egkekrimeni"] is True

    # ------------------------------------------------------------------------
    # 5. Επαλήθευση Νέας Κατάστασης (STORM-09, TEST-20)
    # ------------------------------------------------------------------------
    synopsi_meta = pelatis_dokimwn.get("/api/v1/synopsi").json()
    # Μετά την παύση αναβλητών (4 kW), το έλλειμμα μειώνεται από 15.2 kW σε 11.2 kW
    assert synopsi_meta["energeia"]["elleimma_kw"] == pytest.approx(11.2, rel=1e-3)
    # Η αυτονομία αυξάνεται σε 2.68 ώρες (~2.67857 h)
    assert synopsi_meta["energeia"]["autonomia_wres"] == pytest.approx(2.67857, rel=1e-3)
    # Η υποβαθμισμένη επικοινωνία δεν επιτρέπει ψευδή βεβαίωση εκτέλεσης.
    assert synopsi_meta["oxima_exerevnis"]["katastasi"] == "stasi"
    assert apantisi_apofasis.json()["entoli_oximatos"]["katastasi_entolis"] == "avevaio"
    assert (
        pelatis_dokimwn.post(
            "/api/v1/senaria/prokathorismena/apokatastasi/energopoiisi"
        ).status_code
        == 200
    )
    assert pelatis_dokimwn.post("/api/v1/prosomoiwsi/vima", json={"lepta": 1}).status_code == 200
    assert pelatis_dokimwn.get("/api/v1/oximata").json()[0]["katastasi_oximatos"] == "asfalis_stasi"

    # ------------------------------------------------------------------------
    # 6. Έλεγχος Χρονολογίου Αποφάσεων (STORM-08)
    # ------------------------------------------------------------------------
    xronologio = pelatis_dokimwn.get("/api/v1/senaria/kataigida_skonis_2026/xronologio").json()
    assert len(xronologio) >= 1
    assert xronologio[0]["epilogi"] == "syndyasmos_pliroys_asfaleias"
    assert xronologio[0]["egkekrimeni"] is True
