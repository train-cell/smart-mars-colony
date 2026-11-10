"""Χρονικά έγκυρη τηλεμετρία και ενιαία προβολή μετρήσεων της προσομοίωσης."""

from datetime import datetime, timezone

from sqlalchemy import select

from backend.app.montela import (
    Aisthitiras,
    DexameniNerou,
    Fwtovoltaiko,
    KatastasiProsomoiwsis,
    MetrisiAisthitira,
    XwrosKatoikisis,
    ZwniThermokipiou,
)
from backend.app.pyrinas.rythmiseis import rythmiseis
from backend.app.pyrinas.sfalmata import KodikosSfalmatos, SfalmaKanona


def se_utc(xronos: datetime) -> datetime:
    """Ανακτά το UTC και για ιστορικές εγγραφές SQLite χωρίς offset."""
    return (
        xronos.replace(tzinfo=timezone.utc)
        if xronos.tzinfo is None
        else xronos.astimezone(timezone.utc)
    )


def xronos_apoikias(synedria) -> datetime:
    """Επιστρέφει αποκλειστικά το κοινό προσομοιωμένο ρολόι."""
    katastasi = synedria.get(KatastasiProsomoiwsis, 1)
    return se_utc(katastasi.xronos_prosomoiwsis)


def teleftaia_metrisi(synedria, id_aisthitira):
    return synedria.scalars(
        select(MetrisiAisthitira)
        .where(MetrisiAisthitira.id_aisthitira == id_aisthitira)
        .order_by(MetrisiAisthitira.xronos_metrisis.desc(), MetrisiAisthitira.id_metrisis.desc())
        .limit(1)
    ).first()


def provoli_metrisis(synedria, aisthitiras, metrisi):
    """Η απουσία ή παλαιότητα δεν μετατρέπεται σιωπηρά σε έγκυρη ένδειξη."""
    if metrisi is None:
        return None
    ilikia_s = (xronos_apoikias(synedria) - se_utc(metrisi.xronos_metrisis)).total_seconds()
    palia = (
        metrisi.einai_palio
        or ilikia_s > rythmiseis.MEGISTI_ILIKIA_METRISIS_LEPTA * 60
        or ilikia_s < -1
    )
    poiotita = metrisi.poiotita
    if aisthitiras.katastasi != "leitourgikos":
        poiotita = "apousia"
    elif palia:
        poiotita = "palio"
    return {
        "megethos": aisthitiras.typos_megethous,
        "timi": metrisi.timi,
        "monada": metrisi.monada,
        "eidos": metrisi.eidos,
        "pigi": metrisi.pigi,
        "xronos_metrisis": se_utc(metrisi.xronos_metrisis),
        "xronos_paralavis": se_utc(metrisi.xronos_paralavis or metrisi.xronos_metrisis),
        "poiotita": poiotita,
        "avevaiotita": {"apolyti_timi": metrisi.apolyti_avevaiotita, "monada": metrisi.monada},
        "tasi": metrisi.tasi,
        "einai_palio": palia,
    }


def pare_egkyri_metrisi(synedria, id_aisthitira):
    """Απορρίπτει κρίσιμη πρόβλεψη χωρίς πρόσφατη, έγκυρη πηγή."""
    aisthitiras = synedria.get(Aisthitiras, id_aisthitira)
    metrisi = teleftaia_metrisi(synedria, id_aisthitira)
    provoli = provoli_metrisis(synedria, aisthitiras, metrisi) if aisthitiras else None
    if provoli is None or provoli["poiotita"] not in {"egkyro", "ypovathmismeno"}:
        raise SfalmaKanona(
            KodikosSfalmatos.PALIA_METRISI
            if provoli and provoli["einai_palio"]
            else KodikosSfalmatos.APOUSIA_METRISIS,
            "Η απαιτούμενη μέτρηση απουσιάζει, είναι παρωχημένη ή ο αισθητήρας δεν λειτουργεί.",
            503,
            {
                "id_aisthitira": id_aisthitira,
                "poiotita": provoli["poiotita"] if provoli else "apousia",
            },
        )
    return metrisi


def ananeose_metriseis(synedria, xronos):
    """Παράγει νέες μετρήσεις μόνο από λειτουργικούς προσομοιωμένους αισθητήρες."""
    xwros = synedria.get(XwrosKatoikisis, "xwros_01")
    pv = synedria.get(Fwtovoltaiko, "pv_01")
    dexameni = synedria.get(DexameniNerou, "dexameni_01")
    times = {}
    if xwros:
        times.update(
            {
                "aisth_thermokrasia_esw": xwros.thermokrasia_eswteriki_k,
                "aisth_thermokrasia_exw": xwros.thermokrasia_exwteriki_k,
                "aisth_piesi": xwros.piesi_pa,
                "aisth_o2": xwros.pososto_oxygonou,
                "aisth_co2": xwros.pososto_dioxeidiou_anthraka,
                "aisth_ygrasia": xwros.sxetiki_ygrasia,
            }
        )
    if pv:
        times.update(
            {"aisth_aktinovolia": pv.aktinovolia_w_m2, "aisth_skoni": pv.syntelestis_epikathisis_f}
        )
    if dexameni:
        times["aisth_nero"] = dexameni.trexwn_ogkos_l
    times["aisth_piesi_exw"] = 600.0
    for zwni in synedria.scalars(select(ZwniThermokipiou)):
        times["aisth_ygrasia_" + zwni.id_zwnis] = zwni.ygrasia_ypostrwmatos
    for id_aisthitira, timi in times.items():
        aisthitiras = synedria.get(Aisthitiras, id_aisthitira)
        if not aisthitiras or aisthitiras.katastasi != "leitourgikos":
            continue
        palia = teleftaia_metrisi(synedria, id_aisthitira)
        tasi = (
            "statheri"
            if not palia or abs(palia.timi - timi) < 1e-8
            else ("afksousa" if timi > palia.timi else "fthinousa")
        )
        synedria.add(
            MetrisiAisthitira(
                id_aisthitira=id_aisthitira,
                timi=timi,
                monada=aisthitiras.monada,
                eidos="metrimeno",
                pigi="prosomoiwmenos_aisthitiras",
                poiotita="egkyro",
                tasi=tasi,
                apolyti_avevaiotita=palia.apolyti_avevaiotita if palia else 0.01,
                einai_palio=False,
                xronos_metrisis=xronos,
                xronos_paralavis=xronos,
            )
        )
    synedria.flush()
