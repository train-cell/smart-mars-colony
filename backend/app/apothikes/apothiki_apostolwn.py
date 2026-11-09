"""Αποθήκη δεδομένων (Repository) για οχήματα εξερεύνησης (rover) και κινδύνους."""

from typing import List, Optional

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from backend.app.montela.apostoles import (
    ApostoliOximatos,
    ExwterikosKindynos,
    OximaExerevnis,
    ShmeioDiadromis,
)


class ApothikiApostolwn:
    """Διαχείριση ερωτημάτων βάσης για rover και αποστολές."""

    def __init__(self, synedria: Session):
        self.synedria = synedria

    def pare_oximata(self) -> List[OximaExerevnis]:
        """Ανάκτηση όλων των οχημάτων εξερεύνησης."""
        return list(self.synedria.scalars(select(OximaExerevnis)).all())

    def pare_oxima_ana_id(self, id_oximatos: str) -> Optional[OximaExerevnis]:
        """Ανάκτηση οχήματος βάσει ID."""
        return self.synedria.get(OximaExerevnis, id_oximatos)

    def pare_apostoles_oximatos(self, id_oximatos: str) -> List[ApostoliOximatos]:
        """Ανάκτηση ιστορικού αποστολών οχήματος."""
        dilwsi = (
            select(ApostoliOximatos)
            .where(ApostoliOximatos.id_oximatos == id_oximatos)
            .order_by(desc(ApostoliOximatos.xronos_enarksis))
        )
        return list(self.synedria.scalars(dilwsi).all())

    def pare_apostoli_ana_id(self, id_apostolis: str) -> Optional[ApostoliOximatos]:
        """Ανάκτηση αποστολής βάσει ID."""
        return self.synedria.get(ApostoliOximatos, id_apostolis)

    def pare_shmeia_diadromis(self, id_apostolis: str) -> List[ShmeioDiadromis]:
        """Ανάκτηση σημείων διαδρομής αποστολής."""
        dilwsi = (
            select(ShmeioDiadromis)
            .where(ShmeioDiadromis.id_apostolis == id_apostolis)
            .order_by(ShmeioDiadromis.seira)
        )
        return list(self.synedria.scalars(dilwsi).all())

    def pare_kindynous(self, orio: int = 20) -> List[ExwterikosKindynos]:
        """Ανάκτηση εξωτερικών περιβαλλοντικών κινδύνων."""
        dilwsi = (
            select(ExwterikosKindynos)
            .order_by(desc(ExwterikosKindynos.xronos_katagrafis))
            .limit(orio)
        )
        return list(self.synedria.scalars(dilwsi).all())
