"""Δοκιμές μονάδας για κοινά Pydantic DTOs και Enums (koina.py)."""

from datetime import datetime, timezone

from backend.app.sxhmata.koina import (
    ApantisiSfalmatosSxhma,
    AvevaiotitaSxhma,
    EidosMetrisis,
    EntoliApantisiSxhma,
    KatastasiEntolis,
    KatastasiSynagermou,
    MetrisiAisthitiraSxhma,
    PoiotitaMetrisis,
    SfalmaPerigrafiSxhma,
    SovarotitaSynagermou,
    TasiMetrisis,
)


def test_aparithmiseis_kai_sxhmata():
    """Ελέγχει την ορθότητα τιμών enum και σειριοποίησης σχημάτων."""
    assert EidosMetrisis.METRIMENO.value == "metrimeno"
    assert PoiotitaMetrisis.EGKYRO.value == "egkyro"
    assert TasiMetrisis.STATHERI.value == "statheri"
    assert KatastasiEntolis.OLOKLIROTHIKE.value == "oloklirothike"
    assert SovarotitaSynagermou.KRISIMI.value == "krisimi"
    assert KatastasiSynagermou.EPILYMENOS.value == "epilymenos"

    avev = AvevaiotitaSxhma(apolyti_timi=0.5, monada="K", pososto=0.17)
    assert avev.apolyti_timi == 0.5
    assert avev.monada == "K"

    twrinos = datetime.now(timezone.utc)
    metrisi = MetrisiAisthitiraSxhma(
        megethos="thermokrasia_thalamou",
        timi=293.15,
        monada="K",
        eidos=EidosMetrisis.METRIMENO,
        pigi="aisthitiras_th_01",
        xronos_metrisis=twrinos,
        poiotita=PoiotitaMetrisis.EGKYRO,
        avevaiotita=avev,
        tasi=TasiMetrisis.STATHERI,
        einai_palio=False,
    )
    assert metrisi.timi == 293.15
    assert metrisi.avevaiotita is not None
    assert metrisi.avevaiotita.apolyti_timi == 0.5

    plirofories_sfalmatos = SfalmaPerigrafiSxhma(
        kodikos="aneparki_apothema_nerou",
        minyma="Δεν επαρκεί το νερό",
        leptomereies={"diathesimo": 10.0},
        id_aitimatos="aitima_123",
        epanalipsimo=False,
    )
    fakelos = ApantisiSfalmatosSxhma(sfalma=plirofories_sfalmatos)
    assert fakelos.sfalma.kodikos == "aneparki_apothema_nerou"

    entoli_dto = EntoliApantisiSxhma(
        id_entolis="entoli_1",
        yposystima="ardefsi",
        drasi="enarksi",
        katastasi=KatastasiEntolis.EPIVEVAIWTHIKE,
        id_xristi="xristis_01",
        rolos="ypefthynos_porwn",
        xronos_dimiourgias=twrinos,
        xronos_enimerwsis=twrinos,
        minyma="Εντολή επιβεβαιώθηκε",
        leptomereies={"id_zwnis": "zwni_a"},
    )
    assert entoli_dto.katastasi == KatastasiEntolis.EPIVEVAIWTHIKE
