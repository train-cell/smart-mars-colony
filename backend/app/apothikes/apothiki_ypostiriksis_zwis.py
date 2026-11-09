"""Αποθήκη δεδομένων (Repository) για το υποσύστημα υποστήριξης ζωής και αισθητήρες."""

from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from backend.app.montela.ypostiriksi_zwis import (
    Aisthitiras,
    Apoikia,
    ApothemaOxygonou,
    MetrisiAisthitira,
    SyskeviYpostiriksisZwis,
    XwrosKatoikisis,
)


class ApothikiYpostiriksisZwis:
    """Διαχείριση ερωτημάτων βάσης για χώρους κατοίκησης και αισθητήρες."""

    def __init__(self, synedria: Session):
        self.synedria = synedria

    def pare_apoikies(self) -> List[Apoikia]:
        """Ανάκτηση όλων των αποικιών."""
        return list(self.synedria.scalars(select(Apoikia)).all())

    def pare_xwrous(self) -> List[XwrosKatoikisis]:
        """Ανάκτηση όλων των χώρων κατοίκησης."""
        return list(self.synedria.scalars(select(XwrosKatoikisis)).all())

    def pare_xwro_ana_id(self, id_xwrou: str) -> Optional[XwrosKatoikisis]:
        """Ανάκτηση χώρου κατοίκησης βάσει ID."""
        return self.synedria.get(XwrosKatoikisis, id_xwrou)

    def pare_syskeves_xwrou(self, id_xwrou: str) -> List[SyskeviYpostiriksisZwis]:
        """Ανάκτηση συσκευών υποστήριξης ζωής του χώρου."""
        dilwsi = select(SyskeviYpostiriksisZwis).where(SyskeviYpostiriksisZwis.id_xwrou == id_xwrou)
        return list(self.synedria.scalars(dilwsi).all())

    def pare_apothema_oxygonou(self, id_xwrou: str) -> Optional[ApothemaOxygonou]:
        """Ανάκτηση αποθέματος οξυγόνου του χώρου."""
        dilwsi = select(ApothemaOxygonou).where(ApothemaOxygonou.id_xwrou == id_xwrou)
        return self.synedria.scalars(dilwsi).first()

    def pare_aisthitires(
        self,
        yposystima: Optional[str] = None,
        typos_megethous: Optional[str] = None,
        id_xwrou: Optional[str] = None,
    ) -> List[Aisthitiras]:
        """Ανάκτηση αισθητήρων με προαιρετικά φίλτρα."""
        dilwsi = select(Aisthitiras)
        if yposystima:
            dilwsi = dilwsi.where(Aisthitiras.yposystima == yposystima)
        if typos_megethous:
            dilwsi = dilwsi.where(Aisthitiras.typos_megethous == typos_megethous)
        if id_xwrou:
            dilwsi = dilwsi.where(Aisthitiras.id_xwrou == id_xwrou)
        return list(self.synedria.scalars(dilwsi).all())

    def pare_aisthitira_ana_id(self, id_aisthitira: str) -> Optional[Aisthitiras]:
        """Ανάκτηση αισθητήρα βάσει ID."""
        return self.synedria.get(Aisthitiras, id_aisthitira)

    def pare_teleftaia_metrisi(self, id_aisthitira: str) -> Optional[MetrisiAisthitira]:
        """Ανάκτηση της πιο πρόσφατης μέτρησης ενός αισθητήρα."""
        dilwsi = (
            select(MetrisiAisthitira)
            .where(MetrisiAisthitira.id_aisthitira == id_aisthitira)
            .order_by(desc(MetrisiAisthitira.xronos_metrisis))
            .limit(1)
        )
        return self.synedria.scalars(dilwsi).first()

    def pare_istoriko_metrisewn(
        self, id_aisthitira: str, orio: int = 50
    ) -> List[MetrisiAisthitira]:
        """Ανάκτηση ιστορικού μετρήσεων."""
        dilwsi = (
            select(MetrisiAisthitira)
            .where(MetrisiAisthitira.id_aisthitira == id_aisthitira)
            .order_by(desc(MetrisiAisthitira.xronos_metrisis))
            .limit(orio)
        )
        return list(self.synedria.scalars(dilwsi).all())

    def kataxwrise_metrisi(
        self,
        id_aisthitira: str,
        timi: float,
        monada: str,
        eidos: str = "metrimeno",
        pigi: str = "prosomoiwmenos_aisthitiras",
        poiotita: str = "egkyro",
        tasi: str = "statheri",
        apolyti_avevaiotita: float = 0.1,
        einai_palio: bool = False,
        xronos_metrisis: Optional[datetime] = None,
    ) -> MetrisiAisthitira:
        """Προσθήκη νέας μέτρησης αισθητήρα."""
        metrisi = MetrisiAisthitira(
            id_aisthitira=id_aisthitira,
            timi=timi,
            monada=monada,
            eidos=eidos,
            pigi=pigi,
            poiotita=poiotita,
            tasi=tasi,
            apolyti_avevaiotita=apolyti_avevaiotita,
            einai_palio=einai_palio,
            xronos_metrisis=xronos_metrisis or datetime.now(timezone.utc),
        )
        self.synedria.add(metrisi)
        self.synedria.flush()
        return metrisi
