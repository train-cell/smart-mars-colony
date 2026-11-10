"""Ρυθμίσεις εφαρμογής Smart Mars Colony Backend.

Διαβάζει μεταβλητές περιβάλλοντος με ασφαλείς προεπιλεγμένες τιμές
για τοπική εκπαιδευτική εκτέλεση.
"""

from typing import List

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class RythmiseisEfarmogis(BaseSettings):
    """Ρυθμίσεις συστήματος."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    ONOMA_EFARMOGIS: str = "Smart Mars Colony Backend"
    EKDOSI: str = "1.1.3"
    PERIVALLON: str = "anaptyxi"
    DIADROMI_VASIS: str = "sqlite:///./smart_mars_colony.db"
    EPIPEDO_KATAGRAFIS: str = "INFO"
    DIASTIMA_LIKSIS_PROEPISKOPISIS_LEPTA: int = 15
    MEGISTI_ILIKIA_METRISIS_LEPTA: int = 30
    EPITREPOMENES_PROELEFSEIS: str = Field(
        default="http://localhost:3000,http://localhost:5173,http://127.0.0.1:3000,http://127.0.0.1:5173",
        validation_alias=AliasChoices("EPITREPOMENES_PROELEFSEIS", "EPITREPOMENA_ORIGINS"),
    )

    @property
    def lista_epitrepomenwn_proelefsewn(self) -> List[str]:
        """Επιστρέφει τη λίστα των επιτρεπόμενων origins για CORS."""
        return [
            proelefsi.strip()
            for proelefsi in self.EPITREPOMENES_PROELEFSEIS.split(",")
            if proelefsi.strip()
        ]


rythmiseis = RythmiseisEfarmogis()
