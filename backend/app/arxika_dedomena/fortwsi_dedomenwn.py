"""Επαναλήψιμη φόρτωση αρχικών δεδομένων επίδειξης (Seed Data - CORE-05).

Διασφαλίζει πλήρη συμβατότητα με τα golden inputs της παραγράφου §6
χωρίς διπλότυπες εγγραφές.
"""

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from backend.app.montela import (
    Aisthitiras,
    Apoikia,
    ApothemaOxygonou,
    DexameniNerou,
    EnergeiakoFortio,
    ExwterikosKindynos,
    Fwtovoltaiko,
    KatastasiProsomoiwsis,
    MetrisiAisthitira,
    OximaExerevnis,
    RoiNerou,
    RolosXristiModel,
    SyskeviYpostiriksisZwis,
    Syssoreftis,
    Thermokipio,
    Xristis,
    XwrosKatoikisis,
    ZwniThermokipiou,
)
from backend.app.pyrinas.asfaleia import XRHSTES_DEMO


def arxikopoiisi_dedomenwn_epideiksis(synedria: Session, epanarxikopoiisi: bool = False) -> None:
    """Εισάγει τα δεδομένα εκκίνησης της αποικίας αν δεν υπάρχουν ήδη."""
    if epanarxikopoiisi:
        # Διαγραφή υφιστάμενων εγγραφών με σεβασμό στα foreign keys
        for pinakas in [
            MetrisiAisthitira,
            Aisthitiras,
            SyskeviYpostiriksisZwis,
            ApothemaOxygonou,
            RoiNerou,
            ZwniThermokipiou,
            Thermokipio,
            DexameniNerou,
            Fwtovoltaiko,
            Syssoreftis,
            EnergeiakoFortio,
            OximaExerevnis,
            ExwterikosKindynos,
            KatastasiProsomoiwsis,
            XwrosKatoikisis,
            Apoikia,
            RolosXristiModel,
            Xristis,
        ]:
            synedria.query(pinakas).delete()
        synedria.commit()

    # Έλεγχος αν υπάρχουν ήδη δεδομένα
    if synedria.query(Xristis).first():
        return

    twrinos_xronos = datetime(2026, 11, 10, 12, 0, 0, tzinfo=timezone.utc)

    # 1. Χρήστες και Ρόλοι
    for demo_x in XRHSTES_DEMO.values():
        xristis = Xristis(
            id_xristi=demo_x.id_xristi,
            onoma=demo_x.onoma,
            vasikos_rolos=demo_x.vasikos_rolos.value,
            energos=True,
        )
        synedria.add(xristis)
        for rolos in demo_x.energoi_roloi:
            synedria.add(
                RolosXristiModel(
                    id_xristi=demo_x.id_xristi,
                    rolos=rolos.value,
                )
            )
    synedria.flush()

    # 2. Αποικία και Χώρος Κατοίκησης
    apoikia = Apoikia(
        id_apoikias="apoikia_olympus",
        onoma="Αποικία Όλυμπος (Olympus Mons Colony)",
        perigrafi="Πρότυπος ερευνητικός σταθμός και κατοικία στον Άρη",
    )
    synedria.add(apoikia)
    synedria.flush()

    xwros = XwrosKatoikisis(
        id_xwrou="xwros_01",
        id_apoikias="apoikia_olympus",
        onoma="Κύριος Θάλαμος Διαβίωσης (Hab-1)",
        plithysmos=4,
        ogkos_m3=1000.0,
        epifaneia_m2=500.0,
        syntelestis_thermoperatotitas_u=0.2,
        epithymiti_thermokrasia_k=293.0,
        thermokrasia_eswteriki_k=293.0,
        thermokrasia_exwteriki_k=213.0,
        piesi_pa=101325.0,
        pososto_oxygonou=0.21,
        pososto_dioxeidiou_anthraka=0.0004,
        sxetiki_ygrasia=0.45,
        ekdosi_katastasis=1,
    )
    synedria.add(xwros)
    synedria.flush()

    # 3. Εξοπλισμός Υποστήριξης Ζωής και Οξυγόνο
    synedria.add(
        SyskeviYpostiriksisZwis(
            id_syskevis="sysk_thermansis",
            id_xwrou="xwros_01",
            onoma="Κεντρικός Ηλεκτρικός Θερμαντήρας (COP=1)",
            typos_syskevis="thermantiras",
            katastasi_leitourgias="energi",
            katanalwsi_isxyos_w=8000.0,
        )
    )
    synedria.add(
        ApothemaOxygonou(
            id_apothematos="apoth_o2_01",
            id_xwrou="xwros_01",
            diathesimo_kg=500.0,
            xwritikotita_kg=1000.0,
            rythmos_paragwgis_kg_h=0.1,
        )
    )

    # 4. Αισθητήρες και Αρχικές Μετρήσεις
    metriseis_arxikes = [
        (
            "aisth_thermokrasia_esw",
            "thermokrasia_eswteriki",
            "thermokrasia",
            "ypostiriksi_zwis",
            "xwros_01",
            293.0,
            "K",
        ),
        (
            "aisth_thermokrasia_exw",
            "thermokrasia_exwteriki",
            "thermokrasia",
            "ypostiriksi_zwis",
            "xwros_01",
            213.0,
            "K",
        ),
        (
            "aisth_piesi",
            "piesi_atmofairas",
            "piesi",
            "ypostiriksi_zwis",
            "xwros_01",
            101325.0,
            "Pa",
        ),
        (
            "aisth_o2",
            "pososto_oxygonou",
            "oxygono",
            "ypostiriksi_zwis",
            "xwros_01",
            0.21,
            "pososto",
        ),
        (
            "aisth_co2",
            "pososto_co2",
            "dioxeidio_anthraka",
            "ypostiriksi_zwis",
            "xwros_01",
            0.0004,
            "pososto",
        ),
        (
            "aisth_ygrasia",
            "sxetiki_ygrasia",
            "ygrasia",
            "ypostiriksi_zwis",
            "xwros_01",
            0.45,
            "pososto",
        ),
        ("aisth_aktinovolia", "aktinovolia_iliou", "aktinovolia", "poroi", None, 300.0, "W/m2"),
        ("aisth_skoni", "syntelestis_skonis_f", "skoni", "poroi", None, 0.8, "syntelestis"),
    ]

    for id_a, kod, typ, yposyst, xw, tim, mon in metriseis_arxikes:
        aisth = Aisthitiras(
            id_aisthitira=id_a,
            kodikos_aisthitira=kod,
            typos_megethous=typ,
            yposystima=yposyst,
            id_xwrou=xw,
            monada=mon,
            katastasi="leitourgikos",
        )
        synedria.add(aisth)
        synedria.add(
            MetrisiAisthitira(
                id_aisthitira=id_a,
                timi=tim,
                monada=mon,
                eidos="metrimeno",
                pigi="prosomoiwmenos_aisthitiras",
                poiotita="egkyro",
                tasi="statheri",
                apolyti_avevaiotita=0.01 if "pososto" in mon else 0.5,
                einai_palio=False,
                xronos_metrisis=twrinos_xronos,
            )
        )

    # 5. Θερμοκήπιο και Ζώνες
    thermokipio = Thermokipio(
        id_thermokipiou="thermokipio_01",
        onoma="Βιολογικό Θερμοκήπιο 1 (Greenhouse Alpha)",
        thermokrasia_k=295.0,
        ygrasia_aera=0.65,
        ekdosi_katastasis=1,
    )
    synedria.add(thermokipio)
    synedria.flush()

    synedria.add(
        ZwniThermokipiou(
            id_zwnis="zwni_01",
            id_thermokipiou="thermokipio_01",
            onoma_zwnis="Ζώνη Πατάτας",
            fyto="patates",
            ygrasia_ypostrwmatos=0.55,
            epithymiti_ygrasia=0.60,
            katastasi_fwtismou="fysiko_kai_texnito",
        )
    )
    synedria.add(
        ZwniThermokipiou(
            id_zwnis="zwni_02",
            id_thermokipiou="thermokipio_01",
            onoma_zwnis="Ζώνη Φυλλωδών Λαχανικών",
            fyto="maroulia_spanaki",
            ygrasia_ypostrwmatos=0.58,
            epithymiti_ygrasia=0.65,
            katastasi_fwtismou="fysiko_kai_texnito",
        )
    )

    # 6. Δεξαμενή Νερού και Ροές
    dexameni = DexameniNerou(
        id_dexamenis="dexameni_01",
        onoma="Κύρια Δεξαμενή Νερού Αποικίας",
        xwritikotita_l=10000.0,
        trexwn_ogkos_l=7500.0,
        efedreia_asfaleias_l=1500.0,
        ekdosi_katastasis=1,
    )
    synedria.add(dexameni)
    synedria.flush()

    synedria.add(
        RoiNerou(
            id_dexamenis="dexameni_01",
            typos_rois="anakyklwsi",
            rythmos_l_h=15.0,
            perigrafi="Επιστροφή από κλειστό κύκλωμα ανακύκλωσης",
            xronos_katagrafis=twrinos_xronos,
        )
    )
    synedria.add(
        RoiNerou(
            id_dexamenis="dexameni_01",
            typos_rois="analwsi",
            rythmos_l_h=10.0,
            perigrafi="Βασική κατανάλωση πληθυσμού και υποστήριξης ζωής",
            xronos_katagrafis=twrinos_xronos,
        )
    )

    # 7. Φωτοβολταϊκά, Συσσωρευτές και Ενεργειακά Φορτία (§6 Golden Baseline)
    synedria.add(
        Fwtovoltaiko(
            id_fwtovoltaikou="pv_01",
            onoma="Κύρια Συστοιχία Φωτοβολταϊκών Πλαισίων",
            epifaneia_m2=100.0,
            apodosi_eta=0.20,
            syntelestis_epikathisis_f=0.8,
            aktinovolia_w_m2=300.0,
            isxys_paragwgis_w=4800.0,  # 0.2 * 100 * 300 * 0.8 = 4800 W = 4.8 kW
        )
    )
    synedria.add(
        Syssoreftis(
            id_syssorefti="syssoreftis_01",
            onoma="Κεντρική Μπαταρία Αποικίας",
            xwritikotita_kwh=50.0,
            energeia_kwh=30.0,  # 30 kWh αξιοποιήσιμη ενέργεια
            efedreia_kwh=10.0,
            katastasi="kanoniki_leitourgia",
        )
    )

    # Φορτία: Θέρμανση 8 kW, άλλα κρίσιμα 2 kW, αναβλητά 4 kW
    synedria.add(
        EnergeiakoFortio(
            id_fortiou="fortio_thermansis",
            onoma="Ηλεκτρική Θέρμανση Χώρου Hab-1",
            egkatastasi="xwros_katoikisis",
            isxys_kw=8.0,
            einai_krisimo=True,
            einai_anavlito=False,
            energo=True,
            proteraiotita=1,
        )
    )
    synedria.add(
        EnergeiakoFortio(
            id_fortiou="fortio_krisimo_loipo",
            onoma="Συστήματα Υποστήριξης Ζωής & Αερισμού",
            egkatastasi="xwros_katoikisis",
            isxys_kw=2.0,
            einai_krisimo=True,
            einai_anavlito=False,
            energo=True,
            proteraiotita=2,
        )
    )
    synedria.add(
        EnergeiakoFortio(
            id_fortiou="fortio_anavlito_thermokipiou",
            onoma="Τεχνητός Φωτισμός & Βοηθητικές Αντλίες Θερμοκηπίου",
            egkatastasi="thermokipio",
            isxys_kw=4.0,
            einai_krisimo=False,
            einai_anavlito=True,
            energo=True,
            proteraiotita=3,
        )
    )

    # 8. Όχημα Εξερεύνησης (Rover - §6 Golden Baseline)
    synedria.add(
        OximaExerevnis(
            id_oximatos="rover_01",
            onoma="Εξερευνητικό Όχημα Αίολος (Rover-1)",
            maza_kg=800.0,
            apostasi_apo_vasi_km=2.0,
            taxytita_kmh=4.0,
            energeia_kwh=0.8,
            efedreia_kwh=0.2,
            mesi_isxys_kw=0.6,
            katastasi_oximatos="stasi",
            katastasi_epikoinwnias="statheri",
            ekdosi_katastasis=1,
        )
    )

    # 9. Εξωτερικός Κίνδυνος
    synedria.add(
        ExwterikosKindynos(
            id_kindynou="kindynos_baseline",
            typos_kindynou="orizontia_diaygeia",
            oratotita_m=5000.0,
            epipedo_aktinovolias=0.05,
            sovarotita="xamili",
            eidos_dedomenwn="metrimeno",
            perigrafi="Κανονικές ατμοσφαιρικές συνθήκες χωρίς ενεργή καταιγίδα σκόνης.",
            xronos_katagrafis=twrinos_xronos,
        )
    )

    # 10. Ρολόι Προσομοίωσης
    synedria.add(
        KatastasiProsomoiwsis(
            id_katastasis=1,
            simerino_vima=0,
            xronos_prosomoiwsis=twrinos_xronos,
            active_scenario=None,
            seed=42,
            einai_se_pausi=False,
        )
    )

    synedria.commit()
