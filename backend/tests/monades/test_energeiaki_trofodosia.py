"""Αριθμητικά όρια κοινής κατανομής, αδιαίρετων προγραμμάτων και αυτονομίας δύο φάσεων."""

import pytest

from backend.app.ypiresies.energeiaki_trofodosia import (
    ypologise_autonomia_dyo_fasewn,
    ypologise_katanomi_fortiwn,
)


def fortio(onoma, isxys, krisimo, proteraiotita, plires=False):
    return dict(
        id_fortiou=onoma,
        isxys_kw=isxys,
        energo=True,
        einai_krisimo=krisimo,
        proteraiotita=proteraiotita,
        apaitei_pliri_trofodosia=plires,
    )


def test_idia_proteraiotita_analogika_kai_krisima_prwta():
    fortia = [fortio("a", 8, True, 1), fortio("b", 4, True, 1), fortio("c", 2, False, 0)]
    katanomi = ypologise_katanomi_fortiwn(fortia, 6)
    assert katanomi["ana_fortio"]["a"]["paradidomeni_kw"] == 4
    assert katanomi["ana_fortio"]["b"]["paradidomeni_kw"] == 2
    assert katanomi["ana_fortio"]["c"]["paradidomeni_kw"] == 0
    assert katanomi["paradidomeni_kw"] == 6
    assert fortia[0]["isxys_kw"] == 8


def test_adiaireto_programma_den_katanalwnei_meriki_isxy():
    fortia = [
        fortio("a", 3, False, 1, True),
        fortio("b", 1, False, 2, True),
        fortio("c", 2, False, 3),
    ]
    katanomi = ypologise_katanomi_fortiwn(fortia, 2)
    assert [katanomi["ana_fortio"][onoma]["paradidomeni_kw"] for onoma in ("a", "b", "c")] == [
        0,
        1,
        1,
    ]
    assert katanomi["mi_kalyptomeni_kw"] == 4


@pytest.mark.parametrize(
    "maza,katanalwsi,tora,meta,diarkeia,anamenomeno",
    [
        (1, 0.2, 0.1, 0, 1, 5.5),
        (1, 0.2, 0.1, 0, 100, 10),
        (1, 0.2, 0.3, 0, 1, 6),
        (1, 0.2, 0.3, 0.3, 1, None),
        (1, 0, 0, 0, 0, None),
        (1, 0.2, 0.1, 0, None, 10),
        (0, 0.2, 0.3, 0.3, 1, 0),
    ],
)
def test_autonomia_dyo_fasewn_arithmitika_oria(maza, katanalwsi, tora, meta, diarkeia, anamenomeno):
    apotelesma = ypologise_autonomia_dyo_fasewn(maza, katanalwsi, tora, meta, diarkeia)
    assert apotelesma == (pytest.approx(anamenomeno) if anamenomeno is not None else None)


@pytest.mark.parametrize("timi", [-1, float("nan"), float("inf")])
def test_aporripsi_akyron_fysikwn_eisodwn(timi):
    with pytest.raises(ValueError):
        ypologise_katanomi_fortiwn([], timi)
    with pytest.raises(ValueError):
        ypologise_katanomi_fortiwn([fortio("a", timi, True, 1)], 10)
    with pytest.raises(ValueError):
        ypologise_autonomia_dyo_fasewn(1, 0.2, 0.1, 0, timi)
    with pytest.raises(ValueError):
        ypologise_autonomia_dyo_fasewn(timi, 0.2, 0.1, 0, 1)
