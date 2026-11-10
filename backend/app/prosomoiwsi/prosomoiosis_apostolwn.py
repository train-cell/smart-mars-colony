"""Ντετερμινιστική παραλαβή εντολών, κίνηση και κατανάλωση ενέργειας rover."""

from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.montela.apostoles import ApostoliOximatos, OximaExerevnis
from backend.app.montela.koinonika_symvanta import Entoli, IstorikoElegxou, SymvanEntolis
from backend.app.ypiresies.ypiresia_apostolwn import YpiresiaApostolwn


def _utc(xronos: datetime) -> datetime:
    return xronos.replace(tzinfo=timezone.utc) if xronos.tzinfo is None else xronos


def _metavasi(
    synedria: Session, entoli: Entoli, katastasi: str, xronos: datetime, minyma: str
) -> None:
    proigoumeni = entoli.katastasi
    if proigoumeni == katastasi:
        return
    entoli.katastasi = katastasi
    if katastasi in {"oloklirothike", "apetyxe"}:
        entoli.xronos_ektelesis = xronos
    synedria.add(
        SymvanEntolis(
            id_entolis=entoli.id_entolis,
            proigoumeni_katastasi=proigoumeni,
            nea_katastasi=katastasi,
            minyma=minyma,
            xronos_symvantos=xronos,
        )
    )
    synedria.add(
        IstorikoElegxou(
            id_xristi=entoli.id_xristi,
            rolos=entoli.rolos,
            energeia="metavasi_entolis_oximatos",
            ontotita="entoles",
            id_ontotitas=entoli.id_entolis,
            palia_timi={"katastasi": proigoumeni},
            nea_timi={"katastasi": katastasi},
            aitiologia=minyma,
            xronos_katagrafis=xronos,
        )
    )


def _xronos_paralavis(
    entoli: Entoli, oxima: OximaExerevnis, apo: datetime, ews: datetime
) -> datetime | None:
    if oxima.katastasi_epikoinwnias != "statheri":
        return None
    xronos_apostolis = datetime.fromisoformat(
        entoli.dedomena_aitimatos.get("xronos_apostolis", apo.isoformat())
    )
    paralavi = _utc(xronos_apostolis) + timedelta(seconds=oxima.kathysterisi_epikoinwnias_s)
    if paralavi > ews:
        return None
    # Μετά από απώλεια σήματος, το βήμα όπου αποκαθίσταται η επικοινωνία είναι το πρώτο τεκμήριο παραλαβής.
    return max(apo, paralavi)


def proxorise_apostoles(synedria: Session, apo: datetime, ews: datetime) -> dict:
    """Προχωρά επιβεβαιωμένες ενέργειες χωρίς commit ή αλλαγή του κοινού ρολογιού.

    Η επιστημονική αποστολή ακολουθεί δηλωμένη διαδρομή μετάβασης και επιστροφής.
    Η κατανάλωση ολοκληρώνεται ανά τμήμα διαδρομής και στη διάρκεια επιστημονικής
    αναμονής, με διακριτό κόστος μάζας/κλίσης/βοηθητικών φορτίων.
    """
    apo, ews = _utc(apo), _utc(ews)
    if ews <= apo:
        return {"katanalwsi_kwh": 0.0, "metavaseis": 0}
    ypiresia = YpiresiaApostolwn(synedria)
    synoliki_energeia = 0.0
    metavaseis = 0
    for oxima in synedria.scalars(select(OximaExerevnis)).all():
        arxiki_energeia = oxima.energeia_kwh
        entoles = list(
            synedria.scalars(
                select(Entoli).where(
                    Entoli.yposystima == "apostoles",
                    Entoli.id_ontotitas == oxima.id_oximatos,
                    Entoli.katastasi.in_(["avevaio", "se_anamoni", "egkrithike", "se_exelixi"]),
                )
            ).all()
        )
        enarksi_kinisis = apo
        for entoli in entoles:
            if entoli.katastasi == "se_exelixi":
                continue
            paralavi = _xronos_paralavis(entoli, oxima, apo, ews)
            if paralavi is None:
                if oxima.katastasi_epikoinwnias != "statheri":
                    _metavasi(
                        synedria,
                        entoli,
                        "avevaio",
                        apo,
                        "Δεν επιβεβαιώθηκε επικοινωνία με το όχημα.",
                    )
                continue
            if entoli.drasi == "asfalis_stasi":
                # Κατανάλωση μέχρι την ακινητοποίηση και μετά μόνο βοηθητικά φορτία.
                wres_prin = (paralavi - apo).total_seconds() / 3600
                wres_meta = (ews - paralavi).total_seconds() / 3600
                zitisi = (
                    oxima.mesi_isxys_kw * wres_prin + oxima.voithitiki_isxys_w / 1000 * wres_meta
                )
                oxima.energeia_kwh = max(0, oxima.energeia_kwh - zitisi)
                if oxima.katastasi_oximatos == "epistrofi_se_exelixi":
                    proigoumeni_apostasi = oxima.apostasi_apo_vasi_km
                    oxima.apostasi_apo_vasi_km = max(
                        0, proigoumeni_apostasi - oxima.taxytita_kmh * wres_prin
                    )
                    logos = (
                        oxima.apostasi_apo_vasi_km / proigoumeni_apostasi
                        if proigoumeni_apostasi
                        else 0
                    )
                    oxima.syntetagmeni_x *= logos
                    oxima.syntetagmeni_y *= logos
                ypiresia._efarmose_xeirismo(oxima, "asfalis_stasi")
                _metavasi(
                    synedria,
                    entoli,
                    "oloklirothike",
                    paralavi,
                    "Επιβεβαιώθηκε η ασφαλής στάση από το όχημα.",
                )
                enarksi_kinisis = ews
                metavaseis += 1
            elif entoli.drasi == "anaklisi_oximatos":
                axiologisi = ypiresia._axiologisi_epistrofis(oxima)
                if not axiologisi["energeiaka_efikto"] or not axiologisi["diadromi_asfalis"]:
                    _metavasi(
                        synedria,
                        entoli,
                        "apetyxe",
                        paralavi,
                        "Οι συνθήκες δεν επιτρέπουν ασφαλή ανάκληση· απαιτείται νέα απόφαση.",
                    )
                else:
                    ypiresia._efarmose_xeirismo(oxima, "anaklisi_oximatos")
                    _metavasi(
                        synedria,
                        entoli,
                        "se_exelixi",
                        paralavi,
                        "Επιβεβαιώθηκε η έναρξη επιστροφής.",
                    )
                    enarksi_kinisis = paralavi
                metavaseis += 1
            elif entoli.drasi == "dimiourgia_apostolis":
                apostoli = synedria.get(
                    ApostoliOximatos, entoli.dedomena_aitimatos.get("id_apostolis")
                )
                if apostoli is None or apostoli.katastasi_apostolis != "se_anamoni":
                    continue
                axiologisi = ypiresia._axiologisi_epistrofis(oxima)
                if (
                    not axiologisi["diadromi_asfalis"]
                    or oxima.energeia_kwh - apostoli.apaitoumeni_energeia_kwh < oxima.efedreia_kwh
                ):
                    apostoli.katastasi_apostolis = "apetyxe"
                    _metavasi(
                        synedria,
                        entoli,
                        "apetyxe",
                        paralavi,
                        "Η επανεκτίμηση πριν την αναχώρηση απέτυχε.",
                    )
                else:
                    apostoli.katastasi_apostolis = "se_exelixi"
                    apostoli.xronos_enarksis = paralavi
                    oxima.katastasi_oximatos = "apostoli_se_exelixi"
                    oxima.maza_fortiou_kg = apostoli.maza_fortiou_kg
                    oxima.plithos_plirwmatos = apostoli.plithos_plirwmatos
                    _metavasi(
                        synedria,
                        entoli,
                        "se_exelixi",
                        paralavi,
                        "Το όχημα επιβεβαίωσε την αναχώρηση.",
                    )
                    enarksi_kinisis = paralavi
                metavaseis += 1
        if oxima.katastasi_oximatos == "epistrofi_se_exelixi" and enarksi_kinisis < ews:
            axiologisi = ypiresia._axiologisi_epistrofis(oxima)
            if not axiologisi["diadromi_asfalis"] or oxima.katastasi_epikoinwnias != "statheri":
                # Δεν επινοείται επιβεβαίωση κίνησης από την απουσία τηλεμετρίας.
                for entoli in entoles:
                    if entoli.drasi == "anaklisi_oximatos" and entoli.katastasi == "se_exelixi":
                        _metavasi(
                            synedria,
                            entoli,
                            "avevaio",
                            apo,
                            "Η εξέλιξη επιστροφής δεν μπορεί να επιβεβαιωθεί.",
                        )
            else:
                wres = min(
                    (ews - enarksi_kinisis).total_seconds() / 3600,
                    oxima.apostasi_apo_vasi_km / oxima.taxytita_kmh,
                )
                kostos = wres * oxima.isxys_kinisis_kw
                if kostos > max(0, oxima.energeia_kwh - oxima.efedreia_kwh) + 1e-9:
                    oxima.katastasi_oximatos = "anagki_energeias"
                    for entoli in entoles:
                        if entoli.drasi == "anaklisi_oximatos":
                            _metavasi(
                                synedria,
                                entoli,
                                "apetyxe",
                                apo,
                                "Δεν επαρκεί πλέον η εφεδρεία επιστροφής.",
                            )
                else:
                    oxima.energeia_kwh -= kostos
                    proigoumeni_apostasi = oxima.apostasi_apo_vasi_km
                    oxima.apostasi_apo_vasi_km = max(
                        0, proigoumeni_apostasi - wres * oxima.taxytita_kmh
                    )
                    logos = (
                        oxima.apostasi_apo_vasi_km / proigoumeni_apostasi
                        if proigoumeni_apostasi
                        else 0
                    )
                    oxima.syntetagmeni_x *= logos
                    oxima.syntetagmeni_y *= logos
                    if oxima.apostasi_apo_vasi_km <= 1e-9:
                        oxima.katastasi_oximatos = "sti_vasi"
                        oxima.mesi_isxys_kw = oxima.voithitiki_isxys_w / 1000
                        for entoli in entoles:
                            if (
                                entoli.drasi == "anaklisi_oximatos"
                                and entoli.katastasi == "se_exelixi"
                            ):
                                _metavasi(
                                    synedria,
                                    entoli,
                                    "oloklirothike",
                                    enarksi_kinisis + timedelta(hours=wres),
                                    "Επιβεβαιώθηκε άφιξη στη βάση.",
                                )
                        enarksi_kinisis += timedelta(hours=wres)
        synedria.flush()
        apostoles = synedria.scalars(
            select(ApostoliOximatos).where(
                ApostoliOximatos.id_oximatos == oxima.id_oximatos,
                ApostoliOximatos.katastasi_apostolis == "se_exelixi",
            )
        ).all()
        for apostoli in apostoles:
            if oxima.katastasi_oximatos != "apostoli_se_exelixi":
                continue
            entoli = synedria.get(Entoli, apostoli.id_entolis) if apostoli.id_entolis else None
            if (
                oxima.katastasi_epikoinwnias != "statheri"
                or not ypiresia._axiologisi_epistrofis(oxima)["diadromi_asfalis"]
            ):
                apostoli.katastasi_apostolis = "anastoli"
                if entoli:
                    _metavasi(
                        synedria,
                        entoli,
                        "avevaio",
                        apo,
                        "Η ασφαλής εξέλιξη αποστολής απαιτεί νέα αξιολόγηση.",
                    )
                continue
            telos = _utc(apostoli.xronos_enarksis) + timedelta(
                hours=apostoli.ektimwmeni_diarkeia_wres
            )
            enarksi = max(apo, _utc(apostoli.xronos_enarksis))
            telos_tmimatos = min(ews, telos)
            arxi_wres = max(0, (enarksi - _utc(apostoli.xronos_enarksis)).total_seconds() / 3600)
            telos_wres = max(
                0, (telos_tmimatos - _utc(apostoli.xronos_enarksis)).total_seconds() / 3600
            )
            tmimata = apostoli.sxedio.get("tmimata_prosomoiwsis", [])
            kostos = 0.0
            for tmima in tmimata:
                diarkeia = tmima["liksi_wres"] - tmima["enarksi_wres"]
                koino_diastima = max(
                    0, min(telos_wres, tmima["liksi_wres"]) - max(arxi_wres, tmima["enarksi_wres"])
                )
                if diarkeia > 1e-9:
                    kostos += tmima["energeia_kwh"] * koino_diastima / diarkeia
            kostos = min(
                kostos,
                max(0, apostoli.apaitoumeni_energeia_kwh - apostoli.energeia_katanalwtheisa_kwh),
            )
            if kostos > max(0, oxima.energeia_kwh - oxima.efedreia_kwh) + 1e-9:
                apostoli.katastasi_apostolis = "apetyxe"
                oxima.katastasi_oximatos = "anagki_energeias"
                if entoli:
                    _metavasi(
                        synedria,
                        entoli,
                        "apetyxe",
                        enarksi,
                        "Ανεπαρκής ενέργεια για συνέχεια χωρίς παραβίαση εφεδρείας.",
                    )
                continue
            oxima.energeia_kwh -= kostos
            apostoli.energeia_katanalwtheisa_kwh += kostos
            for tmima in tmimata:
                if tmima["enarksi_wres"] <= telos_wres <= tmima["liksi_wres"] + 1e-9:
                    diarkeia_tmimatos = tmima["liksi_wres"] - tmima["enarksi_wres"]
                    logos = (
                        min(
                            1.0,
                            max(
                                0.0,
                                (telos_wres - tmima["enarksi_wres"]) / diarkeia_tmimatos,
                            ),
                        )
                        if diarkeia_tmimatos > 1e-9
                        else 1.0
                    )
                    oxima.syntetagmeni_x = tmima["x_arxi_m"] + logos * (
                        tmima["x_telos_m"] - tmima["x_arxi_m"]
                    )
                    oxima.syntetagmeni_y = tmima["y_arxi_m"] + logos * (
                        tmima["y_telos_m"] - tmima["y_arxi_m"]
                    )
                    oxima.apostasi_apo_vasi_km = (
                        tmima["apostasi_arxi_m"]
                        + logos * (tmima["apostasi_telos_m"] - tmima["apostasi_arxi_m"])
                    ) / 1000
                    oxima.mesi_isxys_kw = (
                        tmima["energeia_kwh"] / diarkeia_tmimatos
                        if diarkeia_tmimatos > 1e-9
                        else 0.0
                    )
                    break
            if telos_tmimatos >= telos:
                apostoli.katastasi_apostolis = "oloklirothike"
                apostoli.xronos_oloklirwsis = telos
                oxima.katastasi_oximatos = "sti_vasi"
                oxima.maza_fortiou_kg = 0
                oxima.plithos_plirwmatos = 0
                enarksi_kinisis = telos
                if entoli:
                    _metavasi(
                        synedria,
                        entoli,
                        "oloklirothike",
                        telos,
                        "Η αποστολή ολοκληρώθηκε με διατήρηση εφεδρείας.",
                    )
        if (
            oxima.katastasi_oximatos in {"stasi", "asfalis_stasi", "sti_vasi"}
            and enarksi_kinisis < ews
            and not any(
                stoixeio_epsilon.drasi == "asfalis_stasi"
                and stoixeio_epsilon.katastasi == "oloklirothike"
                for stoixeio_epsilon in entoles
            )
        ):
            oxima.energeia_kwh = max(
                0,
                oxima.energeia_kwh
                - oxima.voithitiki_isxys_w / 1000 * (ews - enarksi_kinisis).total_seconds() / 3600,
            )
        if oxima.katastasi_epikoinwnias == "statheri":
            oxima.xronos_teleftaias_tilemetrias = ews
        if not abs(oxima.energeia_kwh - arxiki_energeia) < 1e-12:
            oxima.ekdosi_katastasis += 1
        synoliki_energeia += arxiki_energeia - oxima.energeia_kwh
    synedria.flush()
    return {"katanalwsi_kwh": round(synoliki_energeia, 9), "metavaseis": metavaseis}
