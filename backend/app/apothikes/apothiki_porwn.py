"""Αποθήκη δεδομένων (Repository) για πόρους: θερμοκήπια, νερό, φωτοβολταϊκά και ενέργεια."""

from typing import List, Optional

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from backend.app.montela.poroi import (
    DexameniNerou,
    EnergeiakoFortio,
    Fwtovoltaiko,
    ProgrammaAnakyklwsis,
    ProgrammaArdefsis,
    ProgrammaFwtismou,
    RoiNerou,
    Syssoreftis,
    Thermokipio,
    ZwniThermokipiou,
)


class ApothikiPorwn:
    """Διαχείριση ερωτημάτων βάσης για το υποσύστημα πόρων."""

    def __init__(self, synedria: Session):
        self.synedria = synedria

    def pare_thermokipia(self) -> List[Thermokipio]:
        """Ανάκτηση όλων των θερμοκηπίων."""
        return list(self.synedria.scalars(select(Thermokipio)).all())

    def pare_thermokipio_ana_id(self, id_thermokipiou: str) -> Optional[Thermokipio]:
        """Ανάκτηση θερμοκηπίου βάσει ID."""
        return self.synedria.get(Thermokipio, id_thermokipiou)

    def pare_zwnes_thermokipiou(self, id_thermokipiou: str) -> List[ZwniThermokipiou]:
        """Ανάκτηση των ζωνών ενός θερμοκηπίου."""
        dilwsi = select(ZwniThermokipiou).where(ZwniThermokipiou.id_thermokipiou == id_thermokipiou)
        return list(self.synedria.scalars(dilwsi).all())

    def pare_zwni_ana_id(self, id_zwnis: str) -> Optional[ZwniThermokipiou]:
        """Ανάκτηση ζώνης βάσει ID."""
        return self.synedria.get(ZwniThermokipiou, id_zwnis)

    def pare_dexamenes_nerou(self) -> List[DexameniNerou]:
        """Ανάκτηση όλων των δεξαμενών νερού."""
        return list(self.synedria.scalars(select(DexameniNerou)).all())

    def pare_dexameni_ana_id(self, id_dexamenis: str) -> Optional[DexameniNerou]:
        """Ανάκτηση δεξαμενής βάσει ID."""
        return self.synedria.get(DexameniNerou, id_dexamenis)

    def pare_roes_nerou(self, id_dexamenis: Optional[str] = None) -> List[RoiNerou]:
        """Ανάκτηση ροών νερού."""
        dilwsi = select(RoiNerou)
        if id_dexamenis:
            dilwsi = dilwsi.where(RoiNerou.id_dexamenis == id_dexamenis)
        dilwsi = dilwsi.order_by(desc(RoiNerou.xronos_katagrafis)).limit(100)
        return list(self.synedria.scalars(dilwsi).all())

    def pare_programmata_ardefsis(
        self, id_thermokipiou: Optional[str] = None
    ) -> List[ProgrammaArdefsis]:
        """Ανάκτηση προγραμμάτων άρδευσης."""
        dilwsi = select(ProgrammaArdefsis)
        if id_thermokipiou:
            dilwsi = dilwsi.where(ProgrammaArdefsis.id_thermokipiou == id_thermokipiou)
        dilwsi = dilwsi.order_by(desc(ProgrammaArdefsis.xronos_enarksis))
        return list(self.synedria.scalars(dilwsi).all())

    def pare_programma_ardefsis_ana_id(self, id_programmatos: str) -> Optional[ProgrammaArdefsis]:
        """Ανάκτηση προγράμματος άρδευσης βάσει ID."""
        return self.synedria.get(ProgrammaArdefsis, id_programmatos)

    def pare_programmata_anakyklwsis(self) -> List[ProgrammaAnakyklwsis]:
        """Ανάκτηση προγραμμάτων ανακύκλωσης νερού."""
        dilwsi = select(ProgrammaAnakyklwsis).order_by(desc(ProgrammaAnakyklwsis.xronos_enarksis))
        return list(self.synedria.scalars(dilwsi).all())

    def pare_programma_anakyklwsis_ana_id(
        self, id_programmatos: str
    ) -> Optional[ProgrammaAnakyklwsis]:
        """Ανάκτηση προγράμματος ανακύκλωσης βάσει ID."""
        return self.synedria.get(ProgrammaAnakyklwsis, id_programmatos)

    def pare_programmata_fwtismou(
        self, id_thermokipiou: Optional[str] = None
    ) -> List[ProgrammaFwtismou]:
        """Ανάκτηση προγραμμάτων φωτισμού θερμοκηπίου."""
        dilwsi = select(ProgrammaFwtismou)
        if id_thermokipiou:
            dilwsi = dilwsi.where(ProgrammaFwtismou.id_thermokipiou == id_thermokipiou)
        dilwsi = dilwsi.order_by(desc(ProgrammaFwtismou.xronos_enarksis))
        return list(self.synedria.scalars(dilwsi).all())

    def pare_programma_fwtismou_ana_id(self, id_programmatos: str) -> Optional[ProgrammaFwtismou]:
        """Ανάκτηση προγράμματος φωτισμού βάσει ID."""
        return self.synedria.get(ProgrammaFwtismou, id_programmatos)

    def pare_fwtovoltaika(self) -> List[Fwtovoltaiko]:
        """Ανάκτηση όλων των φωτοβολταϊκών συστοιχιών."""
        return list(self.synedria.scalars(select(Fwtovoltaiko)).all())

    def pare_syssoreftes(self) -> List[Syssoreftis]:
        """Ανάκτηση όλων των συσσωρευτών."""
        return list(self.synedria.scalars(select(Syssoreftis)).all())

    def pare_energeiaka_fortia(self) -> List[EnergeiakoFortio]:
        """Ανάκτηση όλων των ηλεκτρικών φορτίων."""
        return list(
            self.synedria.scalars(
                select(EnergeiakoFortio).order_by(EnergeiakoFortio.proteraiotita)
            ).all()
        )
