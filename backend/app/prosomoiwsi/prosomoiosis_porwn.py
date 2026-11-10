"""Χρονική εκτέλεση πόρων με διατήρηση νερού και ρητή ηλεκτρική λογιστική."""

from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.montela.apostoles import OximaExerevnis
from backend.app.montela.koinonika_symvanta import (
    Entoli,
    IstorikoElegxou,
    KatastasiProsomoiwsis,
    SymvanEntolis,
)
from backend.app.montela.poroi import (
    DexameniNerou,
    EnergeiakoFortio,
    Fwtovoltaiko,
    ProgrammaAnakyklwsis,
    ProgrammaArdefsis,
    ProgrammaFwtismou,
    RoiNerou,
    Syssoreftis,
    ZwniThermokipiou,
)

ENERGES_KATASTASEIS = {"programmatismeno", "se_exelixi", "anastoli"}


def se_utc(xronos: datetime) -> datetime:
    """Κανονικοποιεί και παλιές SQLite χρονοσφραγίδες σε UTC."""
    return (
        xronos.replace(tzinfo=timezone.utc)
        if xronos.tzinfo is None
        else xronos.astimezone(timezone.utc)
    )


def liksi_programmatos(programma) -> datetime:
    """Επιστρέφει το τέλος του δηλωμένου παραθύρου εκτέλεσης."""
    if isinstance(programma, ProgrammaFwtismou):
        return se_utc(programma.xronos_liksis)
    return se_utc(programma.xronos_enarksis) + timedelta(minutes=programma.diarkeia_lepta)


def efarmose_pausi_anavlitwn(synedria: Session, pausi: bool) -> int:
    """Μεταβάλλει την κοινή πολιτική και τα αναβλητά φορτία, χωρίς commit."""
    katastasi = synedria.get(KatastasiProsomoiwsis, 1)
    katastasi.pausi_anavlitwn = pausi
    plithos = 0
    for fortio in synedria.scalars(select(EnergeiakoFortio)):
        if fortio.einai_anavlito:
            fortio.energo = not pausi
            plithos += 1
    enimerwse_fortia_programmatwn(synedria, se_utc(katastasi.xronos_prosomoiwsis))
    return plithos


def _allakse_entoli(
    synedria: Session, programma, katastasi: str, xronos: datetime, minyma: str
) -> None:
    """Καταγράφει πραγματική μετάβαση προγράμματος και σχετικής εντολής."""
    proigoumeni = programma.katastasi
    programma.katastasi = katastasi
    if proigoumeni == katastasi:
        return
    entoli = synedria.get(Entoli, programma.id_entolis) if programma.id_entolis else None
    if entoli:
        proig_entolis = entoli.katastasi
        entoli.katastasi = katastasi
        entoli.xronos_enimerwsis = xronos
        if katastasi in {"oloklirothike", "apetyxe", "akyrothike"}:
            entoli.xronos_ektelesis = xronos
        synedria.add(
            SymvanEntolis(
                id_entolis=entoli.id_entolis,
                proigoumeni_katastasi=proig_entolis,
                nea_katastasi=katastasi,
                minyma=minyma,
                xronos_symvantos=xronos,
            )
        )
    synedria.add(
        IstorikoElegxou(
            id_xristi="prosomoiwsi",
            rolos="systima",
            energeia="metavasi_programmatos",
            ontotita="programma_porwn",
            id_ontotitas=programma.id_programmatos,
            palia_timi={"katastasi": proigoumeni},
            nea_timi={"katastasi": katastasi},
            aitiologia=minyma,
            xronos_katagrafis=xronos,
        )
    )


def _ola_programmata(synedria: Session) -> list:
    """Ανακτά τα εκκρεμή προγράμματα των τριών τύπων."""
    return [
        programma
        for typos in (ProgrammaArdefsis, ProgrammaAnakyklwsis, ProgrammaFwtismou)
        for programma in synedria.scalars(select(typos)).all()
        if programma.katastasi in ENERGES_KATASTASEIS
    ]


def anavlito_fortio_diathesimo(synedria: Session, fortio: EnergeiakoFortio) -> bool:
    """Ελέγχει αν η άρση παύσης θα ενεργοποιούσε πραγματικά το συγκεκριμένο φορτίο."""
    if fortio.id_fortiou.startswith("fortio_fortisis_"):
        oxima = synedria.get(OximaExerevnis, fortio.id_fortiou.removeprefix("fortio_fortisis_"))
        return bool(
            oxima
            and oxima.apostasi_apo_vasi_km <= 1e-6
            and oxima.katastasi_oximatos in {"stasi", "asfalis_stasi", "sti_vasi"}
            and oxima.energeia_kwh < oxima.xwritikotita_energeias_kwh - 1e-9
        )
    if fortio.id_fortiou.startswith("fortio_programmatos_"):
        twra = se_utc(synedria.get(KatastasiProsomoiwsis, 1).xronos_prosomoiwsis)
        return any(
            fortio.id_fortiou == "fortio_programmatos_" + programma.id_programmatos
            and se_utc(programma.xronos_enarksis) <= twra < liksi_programmatos(programma)
            for programma in _ola_programmata(synedria)
        )
    return True


def enimerwse_fortia_programmatwn(synedria: Session, xronos: datetime) -> None:
    """Υπολογίζει ενεργά προγράμματα/φορτία του συγκεκριμένου προσομοιωμένου χρόνου."""
    katastasi = synedria.get(KatastasiProsomoiwsis, 1)
    pausi = bool(katastasi.pausi_anavlitwn)
    for fortio in synedria.scalars(select(EnergeiakoFortio)):
        if fortio.id_fortiou.startswith("fortio_programmatos_"):
            fortio.energo = False
    for zwni in synedria.scalars(select(ZwniThermokipiou)):
        zwni.katastasi_fwtismou = "fysiko"
    for programma in _ola_programmata(synedria):
        enarksi = se_utc(programma.xronos_enarksis)
        liksi = liksi_programmatos(programma)
        if not (enarksi <= xronos < liksi):
            continue
        anavlito = not isinstance(programma, ProgrammaArdefsis)
        if pausi and anavlito:
            _allakse_entoli(
                synedria,
                programma,
                "anastoli",
                xronos,
                "Αναστολή αναβλητού προγράμματος με κοινή απόφαση πόρων.",
            )
            continue
        _allakse_entoli(
            synedria,
            programma,
            "se_exelixi",
            xronos,
            "Έναρξη ή συνέχιση στο προσομοιωμένο χρονικό παράθυρο.",
        )
        isxys_kw = programma.isxys_kw if anavlito else 0.2
        id_fortiou = "fortio_programmatos_" + programma.id_programmatos
        fortio = synedria.get(EnergeiakoFortio, id_fortiou)
        if fortio is None:
            fortio = EnergeiakoFortio(
                id_fortiou=id_fortiou,
                onoma="Πρόγραμμα " + programma.id_programmatos,
                egkatastasi="thermokipio"
                if not isinstance(programma, ProgrammaAnakyklwsis)
                else "anakyklwsi_nerou",
                isxys_kw=isxys_kw,
                einai_krisimo=not anavlito,
                einai_anavlito=anavlito,
                energo=True,
                proteraiotita=2 if anavlito else 1,
            )
            synedria.add(fortio)
        else:
            fortio.isxys_kw = isxys_kw
            fortio.energo = True
        if isinstance(programma, ProgrammaFwtismou):
            zwni = synedria.get(ZwniThermokipiou, programma.id_zwnis)
            if zwni:
                zwni.katastasi_fwtismou = "texnito_energo"
    for oxima in synedria.scalars(select(OximaExerevnis)):
        id_fortiou = "fortio_fortisis_" + oxima.id_oximatos
        fortio = synedria.get(EnergeiakoFortio, id_fortiou)
        if not fortio:
            fortio = EnergeiakoFortio(
                id_fortiou=id_fortiou,
                onoma="Φόρτιση οχήματος",
                egkatastasi="vasi_oximatwn",
                isxys_kw=oxima.isxys_fortisis_kw,
                einai_krisimo=False,
                einai_anavlito=True,
                energo=False,
                proteraiotita=4,
            )
            synedria.add(fortio)
        fortio.energo = (
            not pausi
            and oxima.apostasi_apo_vasi_km <= 1e-6
            and oxima.katastasi_oximatos in {"stasi", "asfalis_stasi", "sti_vasi"}
            and oxima.energeia_kwh < oxima.xwritikotita_energeias_kwh - 1e-9
        )
    synedria.flush()


def _katagrapse_roh(
    synedria: Session,
    programma,
    id_dexamenis: str,
    typos: str,
    posotita_l: float,
    apo: datetime,
    ews: datetime,
) -> None:
    """Ιστορική ροή ορισμένου διαστήματος, χωρίς διπλή χρήση ως μόνιμου ρυθμού."""
    if posotita_l <= 0 or ews <= apo:
        return
    synedria.add(
        RoiNerou(
            id_dexamenis=id_dexamenis,
            typos_rois=typos,
            rythmos_l_h=posotita_l / ((ews - apo).total_seconds() / 3600),
            perigrafi="Προσομοιωμένη εκτέλεση " + programma.id_programmatos,
            xronos_katagrafis=ews,
            id_programmatos=programma.id_programmatos,
            xronos_enarksis=apo,
            xronos_liksis=ews,
            energi=False,
        )
    )


def proxorise_porous(synedria: Session, apo: datetime, ews: datetime) -> dict:
    """Εκτελεί κάθε χρονικό τμήμα μία φορά· ο καλών ορίζει ρολόι και συναλλαγή."""
    apo, ews = se_utc(apo), se_utc(ews)
    if ews <= apo:
        raise ValueError("Το χρονικό διάστημα πρέπει να είναι θετικό.")
    programmata = _ola_programmata(synedria)
    oria = {apo, ews}
    for programma in programmata:
        for orio in (se_utc(programma.xronos_enarksis), liksi_programmatos(programma)):
            if apo < orio < ews:
                oria.add(orio)
    for roi in synedria.scalars(select(RoiNerou)):
        if roi.energi and not roi.id_programmatos:
            for orio in (roi.xronos_enarksis, roi.xronos_liksis):
                if orio and apo < se_utc(orio) < ews:
                    oria.add(se_utc(orio))
    oria = sorted(oria)
    apotelesma = {
        "ardefsi_l": 0.0,
        "anakyklwsi_eisodos_l": 0.0,
        "anakyklwsi_epistrofi_l": 0.0,
        "apwleia_anakyklwsis_l": 0.0,
        "yperxeilisi_l": 0.0,
        "diarros_l": 0.0,
        "elleimma_nerou_l": 0.0,
        "katanalwsi_kwh": 0.0,
        "paragwgi_kwh": 0.0,
        "mi_kalyptomeni_energeia_kwh": 0.0,
        "tmimata": len(oria) - 1,
        "fortisi_oximatwn_kwh": 0.0,
        "perissevma_mi_apothikevmeno_kwh": 0.0,
    }
    for arxi, telos in zip(oria, oria[1:]):
        enimerwse_fortia_programmatwn(synedria, arxi)
        wres = (telos - arxi).total_seconds() / 3600.0
        fortia = list(synedria.scalars(select(EnergeiakoFortio)))
        katanalwsi_kw = sum(
            stoixeio_zita.isxys_kw for stoixeio_zita in fortia if stoixeio_zita.energo
        )
        paragwgi_kw = (
            sum(
                stoixeio_zita.isxys_paragwgis_w
                for stoixeio_zita in synedria.scalars(select(Fwtovoltaiko))
            )
            / 1000.0
        )
        kathari_zitisi_kwh = (katanalwsi_kw - paragwgi_kw) * wres
        syssoreftes = list(synedria.scalars(select(Syssoreftis)))
        diathesimi_kwh = sum(stoixeio_sigma.energeia_kwh for stoixeio_sigma in syssoreftes)
        pliris_trofodosia = kathari_zitisi_kwh <= diathesimi_kwh + 1e-9
        apotelesma["katanalwsi_kwh"] += katanalwsi_kw * wres
        apotelesma["paragwgi_kwh"] += paragwgi_kw * wres
        ypoloipo_kwh = abs(kathari_zitisi_kwh)
        for syssoreftis in syssoreftes:
            if kathari_zitisi_kwh >= 0:
                poso = min(syssoreftis.energeia_kwh, ypoloipo_kwh)
                syssoreftis.energeia_kwh -= poso
            else:
                poso = min(
                    max(
                        0.0,
                        syssoreftis.xwritikotita_kwh
                        - syssoreftis.efedreia_kwh
                        - syssoreftis.energeia_kwh,
                    ),
                    ypoloipo_kwh,
                )
                syssoreftis.energeia_kwh += poso
            ypoloipo_kwh -= poso
            syssoreftis.katastasi = (
                "ekkenwsi_efedreias"
                if syssoreftis.energeia_kwh <= 1e-9
                else "ekkenwsi_se_exelixi"
                if kathari_zitisi_kwh > 0
                else "fortisi"
            )
        if kathari_zitisi_kwh > 0:
            apotelesma["mi_kalyptomeni_energeia_kwh"] += max(0.0, ypoloipo_kwh)
        if kathari_zitisi_kwh < 0:
            apotelesma["perissevma_mi_apothikevmeno_kwh"] += max(0, ypoloipo_kwh)
        if pliris_trofodosia:
            for oxima in synedria.scalars(select(OximaExerevnis)):
                fortio = synedria.get(EnergeiakoFortio, "fortio_fortisis_" + oxima.id_oximatos)
                if fortio and fortio.energo:
                    fortisi = min(
                        oxima.xwritikotita_energeias_kwh - oxima.energeia_kwh,
                        oxima.isxys_fortisis_kw * wres * 0.9,
                    )
                    oxima.energeia_kwh += max(0, fortisi)
                    apotelesma["fortisi_oximatwn_kwh"] += max(0, fortisi)
        for dexameni in synedria.scalars(select(DexameniNerou)):
            eisroi = ekroi = 0.0
            for roi in synedria.scalars(
                select(RoiNerou).where(
                    RoiNerou.id_dexamenis == dexameni.id_dexamenis,
                    RoiNerou.energi.is_(True),
                    RoiNerou.id_programmatos.is_(None),
                )
            ):
                if roi.xronos_enarksis and se_utc(roi.xronos_enarksis) > arxi:
                    continue
                if roi.xronos_liksis and se_utc(roi.xronos_liksis) <= arxi:
                    continue
                if roi.typos_rois == "eisroi":
                    eisroi += roi.rythmos_l_h * wres
                elif roi.typos_rois in {"analwsi", "diarros"}:
                    ekroi += roi.rythmos_l_h * wres
            diarros = dexameni.rythmos_diarrois_l_h * wres
            apotelesma["diarros_l"] += diarros
            nea_stathmi = dexameni.trexwn_ogkos_l + eisroi - ekroi - diarros
            apotelesma["elleimma_nerou_l"] += max(0.0, -nea_stathmi)
            apotelesma["yperxeilisi_l"] += max(0.0, nea_stathmi - dexameni.xwritikotita_l)
            if nea_stathmi < 0 or nea_stathmi > dexameni.xwritikotita_l:
                synedria.add(
                    IstorikoElegxou(
                        id_xristi="prosomoiwsi",
                        rolos="systima",
                        energeia="oria_isozygiou_nerou",
                        ontotita="dexameni_nerou",
                        id_ontotitas=dexameni.id_dexamenis,
                        palia_timi={"trexwn_ogkos_l": dexameni.trexwn_ogkos_l},
                        nea_timi={
                            "yperxeilisi_l": max(0, nea_stathmi - dexameni.xwritikotita_l),
                            "elleimma_l": max(0, -nea_stathmi),
                        },
                        aitiologia="Ρητή καταγραφή φυσικής υπερχείλισης ή μη καλυπτόμενης υδατικής ζήτησης.",
                        xronos_katagrafis=telos,
                    )
                )
            dexameni.trexwn_ogkos_l = min(dexameni.xwritikotita_l, max(0.0, nea_stathmi))
        for programma in programmata:
            if programma.katastasi not in ENERGES_KATASTASEIS or not (
                se_utc(programma.xronos_enarksis) <= arxi < liksi_programmatos(programma)
            ):
                continue
            if programma.katastasi == "anastoli":
                continue
            if not pliris_trofodosia:
                _allakse_entoli(
                    synedria,
                    programma,
                    "apetyxe",
                    arxi,
                    "Ανεπαρκής ενέργεια για πλήρη εκτέλεση του χρονικού τμήματος.",
                )
                continue
            if isinstance(programma, ProgrammaFwtismou):
                programma.ektelestheisa_energeia_kwh += programma.isxys_kw * wres
                continue
            synoliki_eisodos = (
                programma.posotita_nerou_l
                if isinstance(programma, ProgrammaArdefsis)
                else programma.posotita_eisodou_l
            )
            klasma = min(
                1.0,
                (telos - se_utc(programma.xronos_enarksis)).total_seconds()
                / (programma.diarkeia_lepta * 60),
            )
            posotita_l = max(0.0, synoliki_eisodos * klasma - programma.ektelestheisa_posotita_l)
            id_pigis = (
                programma.id_dexamenis
                if isinstance(programma, ProgrammaArdefsis)
                else programma.id_dexamenis_pigis
            )
            pigi = synedria.get(DexameniNerou, id_pigis)
            if not pigi or pigi.trexwn_ogkos_l - pigi.efedreia_asfaleias_l + 1e-8 < posotita_l:
                _allakse_entoli(
                    synedria,
                    programma,
                    "apetyxe",
                    arxi,
                    "Το πραγματικό απόθεμα δεν επαρκεί πλέον για το προγραμματισμένο νερό.",
                )
                continue
            pigi.trexwn_ogkos_l -= posotita_l
            programma.ektelestheisa_posotita_l += posotita_l
            if isinstance(programma, ProgrammaArdefsis):
                apotelesma["ardefsi_l"] += posotita_l
                zwni = synedria.get(ZwniThermokipiou, programma.id_zwnis)
                zwni.ygrasia_ypostrwmatos = min(1.0, zwni.ygrasia_ypostrwmatos + posotita_l / 1000)
                _katagrapse_roh(
                    synedria, programma, pigi.id_dexamenis, "ardefsi", posotita_l, arxi, telos
                )
            else:
                proorismos = synedria.get(DexameniNerou, programma.id_dexamenis)
                epistrofi = posotita_l * programma.apodosi_anakyklwsis
                apwleia = posotita_l - epistrofi
                yperxeilisi = max(
                    0.0, proorismos.trexwn_ogkos_l + epistrofi - proorismos.xwritikotita_l
                )
                proorismos.trexwn_ogkos_l = min(
                    proorismos.xwritikotita_l, proorismos.trexwn_ogkos_l + epistrofi
                )
                apotelesma["anakyklwsi_eisodos_l"] += posotita_l
                apotelesma["anakyklwsi_epistrofi_l"] += epistrofi - yperxeilisi
                apotelesma["apwleia_anakyklwsis_l"] += apwleia
                apotelesma["yperxeilisi_l"] += yperxeilisi
                _katagrapse_roh(
                    synedria,
                    programma,
                    pigi.id_dexamenis,
                    "trofodosia_anakyklwsis",
                    posotita_l,
                    arxi,
                    telos,
                )
                _katagrapse_roh(
                    synedria,
                    programma,
                    proorismos.id_dexamenis,
                    "anakyklwsi",
                    epistrofi - yperxeilisi,
                    arxi,
                    telos,
                )
        synedria.flush()
        for programma in programmata:
            if (
                programma.katastasi in ENERGES_KATASTASEIS
                and liksi_programmatos(programma) <= telos
            ):
                anamenomeno = (
                    programma.isxys_kw
                    * (
                        (
                            liksi_programmatos(programma) - se_utc(programma.xronos_enarksis)
                        ).total_seconds()
                        / 3600
                    )
                    if isinstance(programma, ProgrammaFwtismou)
                    else programma.posotita_nerou_l
                    if isinstance(programma, ProgrammaArdefsis)
                    else programma.posotita_eisodou_l
                )
                ektelesthike = (
                    programma.ektelestheisa_energeia_kwh
                    if isinstance(programma, ProgrammaFwtismou)
                    else programma.ektelestheisa_posotita_l
                )
                nea_katastasi = "oloklirothike" if ektelesthike + 1e-6 >= anamenomeno else "apetyxe"
                _allakse_entoli(
                    synedria,
                    programma,
                    nea_katastasi,
                    telos,
                    "Ολοκλήρωση χρονικού παραθύρου και επαλήθευση πραγματικής παροχής.",
                )
    enimerwse_fortia_programmatwn(synedria, ews)
    synedria.flush()
    return {
        kleidi: round(timi, 8) if isinstance(timi, float) else timi
        for kleidi, timi in apotelesma.items()
    }
