"""Δοκιμές συμβολαίων API, OpenAPI schema και ελέγχου ονοματοδοσίας Greeklish (TEST-08, TEST-17, TEST-18, TEST-19, TEST-21)."""

from fastapi.testclient import TestClient


def test_health_and_metadata_endpoints(pelatis_dokimwn: TestClient):
    """TEST-08: Έλεγχος υγείας και μεταδεδομένων του backend."""
    apantisi_ygeias = pelatis_dokimwn.get("/api/v1/ygeia")
    assert apantisi_ygeias.status_code == 200
    dedomena = apantisi_ygeias.json()
    assert dedomena["katastasi"] == "leitourgiko"
    assert dedomena["vasi_dedomenwn"] == "sqlite_energi"

    # Έλεγχος και του framework alias /health
    apantisi_alias = pelatis_dokimwn.get("/health", follow_redirects=True)
    assert apantisi_alias.status_code == 200
    assert apantisi_alias.json()["katastasi"] == "leitourgiko"

    # Μεταδεδομένα
    apantisi_meta = pelatis_dokimwn.get("/api/v1/metadedomena")
    assert apantisi_meta.status_code == 200
    assert "monades_si" in apantisi_meta.json()


def test_simulation_clock_and_reset(pelatis_dokimwn: TestClient):
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
    apantisi_reset = pelatis_dokimwn.post(
        "/api/v1/prosomoiwsi/epanafora",
        headers={"X-Id-Xristi": "syntonistis"},
    )
    assert apantisi_reset.status_code == 200
    assert (
        "επαναφορά" in apantisi_reset.json()["minyma"]
        or "επανήλθε" in apantisi_reset.json()["minyma"]
    )


def test_openapi_schema_completeness(pelatis_dokimwn: TestClient):
    """TEST-19: Επαλήθευση ότι το OpenAPI JSON περιέχει όλα τα απαιτούμενα endpoints."""
    apantisi = pelatis_dokimwn.get("/openapi.json")
    assert apantisi.status_code == 200
    schema = apantisi.json()

    assert "openapi" in schema
    assert "paths" in schema
    paths = schema["paths"]

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

    for d in ypoxrewtikes_diadromes:
        assert d in paths, f"Η διαδρομή {d} λείπει από το OpenAPI schema!"


def test_greeklish_naming_standards(pelatis_dokimwn: TestClient):
    """TEST-21: Έλεγχος ότι τα δικά μας paths και request/response schemas ακολουθούν Greeklish."""
    schema = pelatis_dokimwn.get("/openapi.json").json()
    paths = schema["paths"]

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

    for path in paths.keys():
        path_lower = path.lower()
        for leksh in apagorevmena_agglika:
            # Ελέγχουμε ότι δεν χρησιμοποιήθηκαν αγγλικές λέξεις domain στις δικές μας διαδρομές
            # (εξαιρείται το /openapi.json)
            if "/api/v1/" in path_lower:
                assert f"/{leksh}" not in path_lower, (
                    f"Βρέθηκε αγγλική λέξη domain στο path: {path}"
                )

    # Έλεγχος ότι και όλοι οι πίνακες και οι στήλες της βάσης είναι Greeklish
    from backend.app.montela import VasiMontelwn

    for onoma_pinaka, pinakas in VasiMontelwn.metadata.tables.items():
        pinakas_lower = onoma_pinaka.lower()
        for leksh in apagorevmena_agglika:
            assert leksh not in pinakas_lower, (
                f"Βρέθηκε αγγλική λέξη domain στον πίνακα: {onoma_pinaka}"
            )
        for stili in pinakas.columns:
            stili_lower = stili.name.lower()
            for leksh in [
                "temperature",
                "battery",
                "sensor",
                "habitats",
                "missions",
                "active_scenario",
            ]:
                assert leksh != stili_lower, (
                    f"Βρέθηκε αγγλική λέξη domain στη στήλη {stili.name} του πίνακα {onoma_pinaka}"
                )
