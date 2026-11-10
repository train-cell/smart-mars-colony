"""Δοκιμές μονάδας για πλήρη κάλυψη των αποθηκών δεδομένων (Repositories).

Καλύπτει όλες τις μεθόδους ανάκτησης, τα φίλτρα παραμέτρων και την αρχικοποίηση
καταστάσεων σε:
- ApothikiApostolwn
- ApothikiKoinwn
- ApothikiPorwn
- ApothikiYpostiriksisZwis
"""

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from backend.app.apothikes.apothiki_apostolwn import ApothikiApostolwn
from backend.app.apothikes.apothiki_koinwn import ApothikiKoinwn
from backend.app.apothikes.apothiki_porwn import ApothikiPorwn
from backend.app.apothikes.apothiki_ypostiriksis_zwis import ApothikiYpostiriksisZwis
from backend.app.montela.apostoles import ApostoliOximatos, ShmeioDiadromis
from backend.app.montela.koinonika_symvanta import KatastasiProsomoiwsis


def test_apothiki_apostolwn_pliris(synedria_dokimwn: Session):
    """Έλεγχος μεθόδων και φίλτρων στην αποθήκη αποστολών."""
    apothiki = ApothikiApostolwn(synedria_dokimwn)

    # Δημιουργία δοκιμαστικής αποστολής και σημείων
    apostoli = ApostoliOximatos(
        id_apostolis="apost_dokimi_01",
        id_oximatos="rover_01",
        titlos="Δειγματοληψία Εδάφους",
        skopos="Γεωλογική ανάλυση",
        katastasi_apostolis="se_exelixi",
        xronos_enarksis=datetime.now(timezone.utc),
    )
    synedria_dokimwn.add(apostoli)
    synedria_dokimwn.flush()

    shmeio = ShmeioDiadromis(
        id_apostolis="apost_dokimi_01",
        seira=1,
        syntetagmeni_x=100.0,
        syntetagmeni_y=200.0,
        apostasi_apo_proigoumeno_m=500.0,
        klisi_rad=0.05,
    )
    synedria_dokimwn.add(shmeio)
    synedria_dokimwn.commit()

    # 1. pare_apostoli_ana_id
    ap = apothiki.pare_apostoli_ana_id("apost_dokimi_01")
    assert ap is not None
    assert ap.id_apostolis == "apost_dokimi_01"

    ap_null = apothiki.pare_apostoli_ana_id("aniparxti_apostoli")
    assert ap_null is None

    # 2. pare_shmeia_diadromis
    shmeia = apothiki.pare_shmeia_diadromis("apost_dokimi_01")
    assert isinstance(shmeia, list)
    assert len(shmeia) == 1
    assert shmeia[0].seira == 1

    # 3. pare_kindynous με όριο
    kindynoi = apothiki.pare_kindynous(orio=1)
    assert isinstance(kindynoi, list)
    assert len(kindynoi) <= 1


def test_apothiki_koinwn_pliris(synedria_dokimwn: Session):
    """Έλεγχος μεθόδων και φίλτρων στην αποθήκη κοινών δεδομένων."""
    apothiki = ApothikiKoinwn(synedria_dokimwn)

    # 1. pare_synagermous με φίλτρο yposystima
    synagermoi = apothiki.pare_synagermous(yposystima="poroi")
    assert isinstance(synagermoi, list)

    # 2. pare_entoles με φίλτρο id_xristi
    entoles = apothiki.pare_entoles(id_xristi="syntonistis", orio=10)
    assert isinstance(entoles, list)

    # 3. pare_katastasi_prosomoiwsis όταν δεν υπάρχει γραμμή στη βάση
    synedria_dokimwn.query(KatastasiProsomoiwsis).delete()
    synedria_dokimwn.commit()

    katastasi = apothiki.pare_katastasi_prosomoiwsis()
    assert katastasi is not None
    assert katastasi.id_katastasis == 1
    assert katastasi.simerino_vima == 0


def test_apothiki_porwn_pliris(synedria_dokimwn: Session):
    """Έλεγχος μεθόδων και φίλτρων στην αποθήκη πόρων."""
    apothiki = ApothikiPorwn(synedria_dokimwn)

    # 1. pare_thermokipio_ana_id
    thm = apothiki.pare_thermokipio_ana_id("thermokipio_01")
    assert thm is not None
    assert thm.id_thermokipiou == "thermokipio_01"

    # 2. pare_roes_nerou με φίλτρο δεξαμενής
    roes = apothiki.pare_roes_nerou(id_dexamenis="dexameni_01")
    assert isinstance(roes, list)
    assert len(roes) >= 1

    # 3. pare_programmata_ardefsis με φίλτρο θερμοκηπίου
    programmata = apothiki.pare_programmata_ardefsis(id_thermokipiou="thermokipio_01")
    assert isinstance(programmata, list)


def test_apothiki_ypostiriksis_zwis_pliris(synedria_dokimwn: Session):
    """Έλεγχος μεθόδων και φίλτρων στην αποθήκη υποστήριξης ζωής."""
    apothiki = ApothikiYpostiriksisZwis(synedria_dokimwn)

    # 1. pare_apoikies
    apoikies = apothiki.pare_apoikies()
    assert len(apoikies) >= 1
    assert apoikies[0].id_apoikias == "apoikia_olympus"

    # 2. pare_aisthitires με φίλτρο typos_megethous
    aisth_t = apothiki.pare_aisthitires(typos_megethous="thermokrasia")
    assert len(aisth_t) >= 1
    assert all(stoixeio_alfa.typos_megethous == "thermokrasia" for stoixeio_alfa in aisth_t)

    # 3. pare_aisthitires με φίλτρο id_xwrou
    aisth_x = apothiki.pare_aisthitires(id_xwrou="xwros_01")
    assert len(aisth_x) >= 1
    assert all(stoixeio_alfa.id_xwrou == "xwros_01" for stoixeio_alfa in aisth_x)

    # 4. kataxwrise_metrisi
    metrisi = apothiki.kataxwrise_metrisi(
        id_aisthitira="aisth_thermokrasia_esw",
        timi=294.5,
        monada="K",
        eidos="metrimeno",
        pigi="dokimastikos_aisthitiras",
    )
    assert metrisi.id_metrisis is not None
    assert metrisi.timi == 294.5
