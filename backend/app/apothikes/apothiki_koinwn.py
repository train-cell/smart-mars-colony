"""Αποθήκη δεδομένων (Repository) για συναγερμούς, εντολές, audit log, σενάρια και μεταβιβάσεις."""

from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from backend.app.montela.koinonika_symvanta import (
    Entoli,
    IstorikoElegxou,
    KatastasiProsomoiwsis,
    Synagermos,
)
from backend.app.montela.xristes import MetavivasiDikaiwmatos
from backend.app.pyrinas.katagrafi import id_trexontos_aitimatos


class ApothikiKoinwn:
    """Διαχείριση οριζόντιων ερωτημάτων βάσης για όλη την αποικία."""

    def __init__(self, synedria: Session):
        self.synedria = synedria

    # --- Συναγερμοί ---
    def pare_synagermous(
        self, katastasi: Optional[str] = None, yposystima: Optional[str] = None
    ) -> List[Synagermos]:
        """Ανάκτηση συναγερμών με φίλτρα."""
        dilwsi = select(Synagermos)
        if katastasi:
            dilwsi = dilwsi.where(Synagermos.katastasi == katastasi)
        if yposystima:
            dilwsi = dilwsi.where(Synagermos.yposystima == yposystima)
        dilwsi = dilwsi.order_by(desc(Synagermos.xronos_dimiourgias))
        return list(self.synedria.scalars(dilwsi).all())

    def pare_synagermo_ana_id(self, id_synagermou: str) -> Optional[Synagermos]:
        """Ανάκτηση συναγερμού βάσει ID."""
        return self.synedria.get(Synagermos, id_synagermou)

    def kataxwrise_synagermo(
        self,
        id_synagermou: str,
        titlos: str,
        perigrafi: str,
        aitia: str,
        epiptwsi: str,
        systasi: str,
        yposystima: str,
        sovarotita: str = "mesaia",
    ) -> Synagermos:
        """Δημιουργία νέου συναγερμού."""
        synagermos = Synagermos(
            id_synagermou=id_synagermou,
            titlos=titlos,
            perigrafi=perigrafi,
            aitia=aitia,
            epiptwsi=epiptwsi,
            systasi=systasi,
            yposystima=yposystima,
            sovarotita=sovarotita,
            katastasi="energos",
        )
        self.synedria.add(synagermos)
        self.synedria.flush()
        return synagermos

    # --- Εντολές & Audit ---
    def pare_entoles(self, id_xristi: Optional[str] = None, orio: int = 50) -> List[Entoli]:
        """Ανάκτηση εντολών."""
        dilwsi = select(Entoli)
        if id_xristi:
            dilwsi = dilwsi.where(Entoli.id_xristi == id_xristi)
        dilwsi = dilwsi.order_by(desc(Entoli.xronos_dimiourgias)).limit(orio)
        return list(self.synedria.scalars(dilwsi).all())

    def pare_entoli_ana_id(self, id_entolis: str) -> Optional[Entoli]:
        """Ανάκτηση εντολής βάσει ID."""
        return self.synedria.get(Entoli, id_entolis)

    def pare_entoli_ana_id_aitimatos(self, id_aitimatos: str) -> Optional[Entoli]:
        """Έλεγχος μοναδικότητας idempotency key."""
        dilwsi = select(Entoli).where(Entoli.id_aitimatos_monadikotitas == id_aitimatos)
        return self.synedria.scalars(dilwsi).first()

    def kataxwrise_istoriko_elegxou(
        self,
        id_xristi: str,
        rolos: str,
        energeia: str,
        ontotita: str,
        id_ontotitas: str,
        palia_timi: Optional[dict] = None,
        nea_timi: Optional[dict] = None,
        aitiologia: Optional[str] = None,
        id_aitimatos: Optional[str] = None,
    ) -> IstorikoElegxou:
        """Εγγραφή στο αμετάβλητο audit log."""
        grammi = IstorikoElegxou(
            id_xristi=id_xristi,
            rolos=rolos,
            energeia=energeia,
            ontotita=ontotita,
            id_ontotitas=id_ontotitas,
            palia_timi=palia_timi,
            nea_timi=nea_timi,
            aitiologia=aitiologia,
            id_aitimatos=id_aitimatos or id_trexontos_aitimatos.get(),
            xronos_katagrafis=datetime.now(timezone.utc),
        )
        self.synedria.add(grammi)
        self.synedria.flush()
        return grammi

    def pare_istoriko_elegxou(self, orio: int = 100) -> List[IstorikoElegxou]:
        """Ανάκτηση ιστορικού ελέγχου."""
        dilwsi = (
            select(IstorikoElegxou).order_by(desc(IstorikoElegxou.xronos_katagrafis)).limit(orio)
        )
        return list(self.synedria.scalars(dilwsi).all())

    # --- Μεταβιβάσεις Δικαιωμάτων ---
    def pare_metavivaseis(self, mono_energes: bool = False) -> List[MetavivasiDikaiwmatos]:
        """Ανάκτηση μεταβιβάσεων δικαιωμάτων."""
        dilwsi = select(MetavivasiDikaiwmatos)
        if mono_energes:
            twrinos = datetime.now(timezone.utc)
            dilwsi = dilwsi.where(
                MetavivasiDikaiwmatos.energo.is_(True),
                MetavivasiDikaiwmatos.xronos_liksis > twrinos,
            )
        dilwsi = dilwsi.order_by(desc(MetavivasiDikaiwmatos.xronos_dimiourgias))
        return list(self.synedria.scalars(dilwsi).all())

    def pare_metavivasi_ana_id(self, id_metavivasis: str) -> Optional[MetavivasiDikaiwmatos]:
        """Ανάκτηση μεταβίβασης βάσει ID."""
        return self.synedria.get(MetavivasiDikaiwmatos, id_metavivasis)

    # --- Κατάσταση Προσομοίωσης ---
    def pare_katastasi_prosomoiwsis(self) -> KatastasiProsomoiwsis:
        """Ανάκτηση της μοναδικής κατάστασης ρολογιού προσομοίωσης."""
        katastasi = self.synedria.get(KatastasiProsomoiwsis, 1)
        if not katastasi:
            katastasi = KatastasiProsomoiwsis(
                id_katastasis=1,
                simerino_vima=0,
                xronos_prosomoiwsis=datetime.now(timezone.utc),
                sporos=42,
            )
            self.synedria.add(katastasi)
            self.synedria.flush()
        return katastasi
