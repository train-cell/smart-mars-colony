"""Ρυθμίσεις εφαρμογής Smart Mars Colony Backend.

Διαβάζει μεταβλητές περιβάλλοντος με ασφαλείς προεπιλεγμένες τιμές
για τοπική εκπαιδευτική εκτέλεση.
"""

from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class RythmiseisEfarmogis(BaseSettings):
    """Ρυθμίσεις συστήματος."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    ONOMA_EFARMOGIS: str = "Smart Mars Colony Backend"
    EKDOSI: str = "1.0.0"
    PERIVALLON: str = "anaptyxi"
    DIADROMI_VASIS: str = "sqlite:///./smart_mars_colony.db"
    EPIPEDO_KATAGRAFIS: str = "INFO"
    MYSTIKO_KLEIDI: str = "ekpaideftiko-kleidi-mono-gia-topiki-xrisi-demo"
    EPITREPOMENA_ORIGINS: str = (
        "http://localhost:3000,http://localhost:5173,http://127.0.0.1:3000,http://127.0.0.1:5173"
    )

    @property
    def lista_epitrepomenwn_origins(self) -> List[str]:
        """Επιστρέφει τη λίστα των επιτρεπόμενων origins για CORS."""
        return [origin.strip() for origin in self.EPITREPOMENA_ORIGINS.split(",") if origin.strip()]


rythmiseis = RythmiseisEfarmogis()
