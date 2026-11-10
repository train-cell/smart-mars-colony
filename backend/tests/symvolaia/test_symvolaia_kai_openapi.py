"""Δοκιμές συμβολαίων API, OpenAPI schema και ελέγχου ονοματοδοσίας Greeklish (TEST-08, TEST-17, TEST-18, TEST-19, TEST-21)."""

from fastapi.testclient import TestClient


def test_ygeia_kai_metadedomena(pelatis_dokimwn: TestClient):
    """TEST-08: Έλεγχος υγείας και μεταδεδομένων του backend."""
    apantisi_ygeias = pelatis_dokimwn.get("/api/v1/ygeia")
    assert apantisi_ygeias.status_code == 200
    dedomena = apantisi_ygeias.json()
    assert dedomena["katastasi"] == "leitourgiko"
    assert dedomena["vasi_dedomenwn"] == "sqlite_energi"

    # Έλεγχος και του framework alias /health
    apantisi_psevdonymou = pelatis_dokimwn.get("/health", follow_redirects=True)
    assert apantisi_psevdonymou.status_code == 200
    assert apantisi_psevdonymou.json()["katastasi"] == "leitourgiko"

    # Μεταδεδομένα
    apantisi_meta = pelatis_dokimwn.get("/api/v1/metadedomena")
    assert apantisi_meta.status_code == 200
    assert "monades_si" in apantisi_meta.json()


def test_roloi_kai_epanafora(pelatis_dokimwn: TestClient):
    """TEST-17: Προώθηση ρολογιού προσομοίωσης και επαναφορά baseline."""
    # Προώθηση κατά 30 λεπτά
    apantisi_vima = pelatis_dokimwn.post(
        "/api/v1/prosomoiwsi/vima",
        json={"lepta": 30},
    )
    assert apantisi_vima.status_code == 200
    assert apantisi_vima.json()["lepta_pou_prostethikan"] == 30
    assert apantisi_vima.json()["simerino_vima"] >= 1

    # Επαναφορά
    apantisi_epanaforas = pelatis_dokimwn.post(
        "/api/v1/prosomoiwsi/epanafora",
        json={"epivevaiwsi": True},
        headers={"X-Id-Xristi": "syntonistis"},
    )
    assert apantisi_epanaforas.status_code == 200
    assert (
        "επαναφορά" in apantisi_epanaforas.json()["minyma"]
        or "επανήλθε" in apantisi_epanaforas.json()["minyma"]
    )


def test_plirotita_symvolaiou(pelatis_dokimwn: TestClient):
    """TEST-19: Επαλήθευση ότι το OpenAPI JSON περιέχει όλα τα απαιτούμενα endpoints."""
    apantisi = pelatis_dokimwn.get("/openapi.json")
    assert apantisi.status_code == 200
    sxhma = apantisi.json()

    assert "openapi" in sxhma
    assert "paths" in sxhma
    diadromes = sxhma["paths"]

    # Έλεγχος ύπαρξης των κύριων διαδρομών
    ypoxrewtikes_diadromes = [
        "/api/v1/ygeia",
        "/api/v1/synopsi",
        "/api/v1/xwroi-katoikisis",
        "/api/v1/xwroi-katoikisis/{id_xwrou}/thermokrasia/proepiskopisi",
        "/api/v1/xwroi-katoikisis/{id_xwrou}/thermokrasia/entoles",
        "/api/v1/thermokipia/{id_thermokipiou}/ardefsi/proepiskopisi",
        "/api/v1/thermokipia/{id_thermokipiou}/ardefsi/programmata",
        "/api/v1/energeia/katastasi",
        "/api/v1/energeia/periorismos-fortiwn/entoles",
        "/api/v1/oximata",
        "/api/v1/oximata/{id_oximatos}/anaklisi/proepiskopisi",
        "/api/v1/oximata/{id_oximatos}/asfalis-stasi/entoles",
        "/api/v1/synagermoi",
        "/api/v1/dikaiwmata/metavivaseis",
        "/api/v1/senaria/kataigida-skonis/proepiskopisi",
        "/api/v1/istoriko-elegxou",
    ]

    for stoixeio_delta in ypoxrewtikes_diadromes:
        assert stoixeio_delta in diadromes, (
            f"Η διαδρομή {stoixeio_delta} λείπει από το OpenAPI schema!"
        )


def test_kanones_onomatodosias(pelatis_dokimwn: TestClient):
    """TEST-21: Έλεγχος ότι τα δικά μας paths και request/response schemas ακολουθούν Greeklish."""
    sxhma = pelatis_dokimwn.get("/openapi.json").json()
    diadromes = sxhma["paths"]

    # Απαγορευμένα αγγλικά domain prefixes/suffixes σε δικά μας endpoints
    apagorevmena_agglika = [
        "temperature",
        "irrigation",
        "greenhouse",
        "battery",
        "power",
        "sensor",
        "rover",
        "storm",
        "water",
        "habitats",
        "missions",
    ]

    for diadromi in diadromes.keys():
        diadromi_peza = diadromi.lower()
        for leksh in apagorevmena_agglika:
            # Ελέγχουμε ότι δεν χρησιμοποιήθηκαν αγγλικές λέξεις domain στις δικές μας διαδρομές
            # (εξαιρείται το /openapi.json)
            if "/api/v1/" in diadromi_peza:
                assert f"/{leksh}" not in diadromi_peza, (
                    f"Βρέθηκε αγγλική λέξη domain στο path: {diadromi}"
                )

    # Έλεγχος ότι και όλοι οι πίνακες και οι στήλες της βάσης είναι Greeklish
    from backend.app.montela import VasiMontelwn

    for onoma_pinaka, pinakas in VasiMontelwn.metadata.tables.items():
        pinakas_peza = onoma_pinaka.lower()
        for leksh in apagorevmena_agglika:
            assert leksh not in pinakas_peza, (
                f"Βρέθηκε αγγλική λέξη domain στον πίνακα: {onoma_pinaka}"
            )
        for stili in pinakas.columns:
            stili_peza = stili.name.lower()
            for leksh in [
                "temperature",
                "battery",
                "sensor",
                "habitats",
                "missions",
                "active_scenario",
            ]:
                assert leksh != stili_peza, (
                    f"Βρέθηκε αγγλική λέξη domain στη στήλη {stili.name} του πίνακα {onoma_pinaka}"
                )


def test_oles_oi_epityxies_exoun_rita_sxhmata_kai_koina_sfalmata(pelatis_dokimwn):
    sxhma = pelatis_dokimwn.get("/openapi.json").json()
    for diadromi, methodoi in sxhma["paths"].items():
        for methodos, leitourgia in methodoi.items():
            if methodos not in {"get", "post", "put", "delete", "patch"}:
                continue
            epityxia = leitourgia["responses"]["200"]["content"]["application/json"]["schema"]
            assert epityxia, (diadromi, methodos)
            if "$ref" in epityxia:
                onoma = epityxia["$ref"].rsplit("/", 1)[1]
                assert sxhma["components"]["schemas"][onoma].get("properties"), onoma
            else:
                assert epityxia.get("type") == "array", (diadromi, epityxia)
                assert epityxia["items"], diadromi
            for kodikos in ["401", "403", "404", "409", "422", "503"]:
                assert leitourgia["responses"][kodikos]["content"]["application/json"]["schema"][
                    "$ref"
                ].endswith("/ApantisiSfalmatosSxhma")


def test_python_vasi_kai_dimosia_pedia_onomatodosias(pelatis_dokimwn):
    from scripts.elegxos_onomatodosias import elegxe_onomatodosia

    assert elegxe_onomatodosia() == []
