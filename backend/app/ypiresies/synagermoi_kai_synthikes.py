"""Κανόνες κρίσεων με επαναχρησιμοποίηση ειδοποιήσεων και διατήρηση αναγνώρισης."""

import uuid

from sqlalchemy import select

from backend.app.montela import (
    Aisthitiras,
    DexameniNerou,
    ExwterikosKindynos,
    KatastasiProsomoiwsis,
    OximaExerevnis,
    Synagermos,
    SyskeviYpostiriksisZwis,
    Syssoreftis,
    XwrosKatoikisis,
)
from backend.app.ypiresies.metriseis_kai_poiotita import (
    provoli_metrisis,
    teleftaia_metrisi,
    xronos_apoikias,
)


def enimerwse_synagermous(synedria):
    """Δεν επιλύει αυτόματα ανεπίλυτο συμβάν ούτε κρύβει acknowledge από τον χρήστη."""
    synthikes = {}

    def prosthese(kleidi, energi, titlos, yposystima, sovarotita, epiptwsi, systasi):
        synthikes[kleidi] = (energi, titlos, yposystima, sovarotita, epiptwsi, systasi)

    roloi = synedria.get(KatastasiProsomoiwsis, 1)
    prosthese(
        "kataigida_skonis",
        roloi.energo_senario == "kataigida_skonis_2026",
        "Καταιγίδα σκόνης σε εξέλιξη",
        "poroi",
        "krisimi",
        "Μείωση παραγωγής και αυξημένη θέρμανση.",
        "Συγκρίνετε περιορισμό φορτίων και ασφαλή χειρισμό rover. Η κρίση απαιτεί συνεχή επανεκτίμηση.",
    )
    for xwros in synedria.scalars(select(XwrosKatoikisis)):
        prosthese(
            "oxygono_" + xwros.id_xwrou,
            xwros.pososto_oxygonou * xwros.piesi_pa <= 16000,
            "Χαμηλή μερική πίεση οξυγόνου",
            "ypostiriksi_zwis",
            "krisimi",
            "Παραβίαση εκπαιδευτικού κατωφλίου 16 kPa.",
            "Ελέγξτε παραγωγή, πίεση και αποθέματα.",
        )
        prosthese(
            "piesi_" + xwros.id_xwrou,
            xwros.piesi_pa < 85000,
            "Πτώση πίεσης κατοίκησης",
            "ypostiriksi_zwis",
            "krisimi",
            "Πιθανή διαρροή ατμόσφαιρας.",
            "Εντοπίστε τη διαρροή και ελέγξτε την επαναφορά πίεσης.",
        )
        prosthese(
            "dioxeidio_" + xwros.id_xwrou,
            xwros.pososto_dioxeidiou_anthraka > 0.005,
            "Αυξημένο διοξείδιο άνθρακα",
            "ypostiriksi_zwis",
            "ypsili",
            "Συσσώρευση CO₂.",
            "Ελέγξτε τον καθαριστή αέρα.",
        )
        prosthese(
            "thermokrasia_" + xwros.id_xwrou,
            not 280 <= xwros.thermokrasia_eswteriki_k <= 305,
            "Θερμοκρασία εκτός σεναριακών ορίων",
            "ypostiriksi_zwis",
            "ypsili",
            "Ανεπαρκής θερμική ρύθμιση.",
            "Ελέγξτε θέρμανση και διαθέσιμη ισχύ.",
        )
    for dexameni in synedria.scalars(select(DexameniNerou)):
        prosthese(
            "nero_" + dexameni.id_dexamenis,
            dexameni.trexwn_ogkos_l <= dexameni.efedreia_asfaleias_l,
            "Εξάντληση διαθέσιμου νερού",
            "poroi",
            "krisimi",
            "Διαθέσιμο απόθεμα στο κατώφλι εφεδρείας.",
            "Αναβάλετε άρδευση και ελέγξτε εισροές.",
        )
        prosthese(
            "diarroi_" + dexameni.id_dexamenis,
            dexameni.rythmos_diarrois_l_h > 0,
            "Διαρροή νερού",
            "poroi",
            "ypsili",
            "Απώλεια υδατικού αποθέματος.",
            "Ελέγξτε το κύκλωμα και επαληθεύστε αποκατάσταση.",
        )
    prosthese(
        "energeia",
        sum(stoixeio_sigma.energeia_kwh for stoixeio_sigma in synedria.scalars(select(Syssoreftis)))
        <= 0,
        "Εξάντληση αξιοποιήσιμης ηλεκτρικής ενέργειας",
        "poroi",
        "krisimi",
        "Η ελάχιστη εφεδρεία δεν επιτρέπεται να αναλωθεί.",
        "Περιορίστε φορτία και αποκαταστήστε παραγωγή.",
    )
    from backend.app.ypiresies.ypiresia_porwn import YpiresiaPorwn

    energeia = YpiresiaPorwn(synedria).pare_katastasi_energeias()
    autonomia = energeia["isozygio"]["autonomia_wres"]
    prosthese(
        "xamili_autonomia",
        autonomia is not None and 0 < autonomia < 1,
        "Ηλεκτρική αυτονομία μικρότερη από μία ώρα",
        "poroi",
        "ypsili",
        "Το εκπαιδευτικό περιθώριο προειδοποίησης εξαντλείται.",
        "Επανεκτιμήστε προτεραιότητες και παύση αναβλητών πριν μηδενιστεί το απόθεμα.",
    )
    prosthese(
        "mideniki_iliaki_paragwgi",
        energeia["paragwgi"]["synoliki_isxys_w"] <= 0,
        "Μηδενική φωτοβολταϊκή παραγωγή",
        "poroi",
        "ypsili",
        "Η ζήτηση καλύπτεται από αποθήκευση όσο αυτή επαρκεί.",
        "Ελέγξτε ηλιακή ακτινοβολία, επικάθιση και διαθέσιμη ενέργεια.",
    )
    for oxima in synedria.scalars(select(OximaExerevnis)):
        prosthese(
            "epikoinwnia_" + oxima.id_oximatos,
            oxima.katastasi_epikoinwnias != "statheri",
            "Υποβάθμιση επικοινωνίας rover",
            "apostoles",
            "ypsili",
            "Οι εντολές μπορεί να μην έχουν επιβεβαιωθεί.",
            "Διατηρήστε αβέβαιη κατάσταση μέχρι παραλαβή.",
        )
    for aisthitiras in synedria.scalars(select(Aisthitiras)):
        metrisi = provoli_metrisis(
            synedria, aisthitiras, teleftaia_metrisi(synedria, aisthitiras.id_aisthitira)
        )
        prosthese(
            "aisthitiras_" + aisthitiras.id_aisthitira,
            metrisi is None or metrisi["poiotita"] not in {"egkyro", "ypovathmismeno"},
            "Μη διαθέσιμη ή παρωχημένη μέτρηση",
            aisthitiras.yposystima,
            "ypsili",
            "Οι προβλέψεις απαιτούν έλεγχο της πηγής.",
            "Αποκαταστήστε τον αισθητήρα ή χρησιμοποιήστε ρητά συντηρητική εκτίμηση.",
        )
    for syskevi in synedria.scalars(select(SyskeviYpostiriksisZwis)):
        prosthese(
            "syskevi_" + syskevi.id_syskevis,
            syskevi.katastasi_leitourgias != "energi",
            "Εξοπλισμός υποστήριξης ζωής εκτός λειτουργίας",
            "ypostiriksi_zwis",
            "ypsili",
            "Μειωμένη διαθεσιμότητα συστήματος.",
            "Ελέγξτε τροφοδοσία και κατάσταση συσκευής.",
        )
    kindynos = synedria.scalars(
        select(ExwterikosKindynos).order_by(
            ExwterikosKindynos.xronos_katagrafis.desc(), ExwterikosKindynos.id_kindynou.desc()
        )
    ).first()
    prosthese(
        "aktinovolia",
        bool(kindynos and kindynos.epipedo_aktinovolias > 0.2),
        "Αυξημένη εξωτερική ακτινοβολία",
        "apostoles",
        "ypsili",
        "Αυξημένη έκθεση στην επιφάνεια.",
        "Αναβάλετε επανδρωμένες αποστολές.",
    )
    prosthese(
        "proskrousi",
        bool(kindynos and kindynos.typos_kindynou == "proskrousi"),
        "Προειδοποίηση πιθανής πρόσκρουσης",
        "apostoles",
        "krisimi",
        "Προσομοιωμένο επικίνδυνο συμβάν.",
        "Ανασχεδιάστε διαδρομή και προφυλάξτε το όχημα.",
    )
    for kleidi, (energi, titlos, yposystima, sovarotita, epiptwsi, systasi) in synthikes.items():
        synagermos = synedria.scalars(
            select(Synagermos)
            .where(Synagermos.kleidi_aitias == kleidi)
            .order_by(Synagermos.xronos_dimiourgias.desc())
        ).first()
        if not synagermos and not energi:
            continue
        if not synagermos:
            synagermos = Synagermos(
                id_synagermou="synag_" + uuid.uuid4().hex,
                kleidi_aitias=kleidi,
                titlos=titlos,
                perigrafi=titlos,
                aitia=kleidi,
                epiptwsi=epiptwsi,
                systasi=systasi,
                yposystima=yposystima,
                sovarotita=sovarotita,
                katastasi="energos",
                xronos_dimiourgias=xronos_apoikias(synedria),
                xronos_enimerwsis=xronos_apoikias(synedria),
            )
            synedria.add(synagermos)
        elif energi and (not synagermos.energi_aitia or synagermos.sovarotita != sovarotita):
            synagermos.katastasi = "energos"
            synagermos.epanalamvanomenos = True
            synagermos.id_xristi_anagnwrisis = None
            synagermos.xronos_anagnwrisis = None
            synagermos.id_xristi_epilysis = None
            synagermos.xronos_epilysis = None
            synagermos.sxolio_epilysis = None
        synagermos.energi_aitia = energi
        synagermos.sovarotita = sovarotita
        synagermos.epiptwsi = epiptwsi
        synagermos.systasi = systasi
    synedria.flush()
