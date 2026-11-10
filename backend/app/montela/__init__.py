"""Συγκεντρωτική εισαγωγή όλων των ORM μοντέλων για το Alembic και την εφαρμογή."""

from backend.app.montela.apostoles import (
    ApostoliOximatos,
    ExwterikosKindynos,
    OximaExerevnis,
    ShmeioDiadromis,
)
from backend.app.montela.koinonika_symvanta import (
    Apofasi,
    EktelesiSenariou,
    Entoli,
    IstorikoElegxou,
    KatastasiProsomoiwsis,
    Proepiskopisi,
    StigmiotypoSenariou,
    SymvanEntolis,
    Synagermos,
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
    Thermokipio,
    ZwniThermokipiou,
)
from backend.app.montela.vasi_montelwn import VasiMontelwn, XronikaPedia
from backend.app.montela.xristes import AnathesiRolouXristi, MetavivasiDikaiwmatos, Xristis
from backend.app.montela.ypostiriksi_zwis import (
    Aisthitiras,
    Apoikia,
    ApothemaOxygonou,
    MetrisiAisthitira,
    SyskeviYpostiriksisZwis,
    XwrosKatoikisis,
)

__all__ = [
    "VasiMontelwn",
    "XronikaPedia",
    "Xristis",
    "AnathesiRolouXristi",
    "MetavivasiDikaiwmatos",
    "Apoikia",
    "XwrosKatoikisis",
    "SyskeviYpostiriksisZwis",
    "ApothemaOxygonou",
    "Aisthitiras",
    "MetrisiAisthitira",
    "Thermokipio",
    "ZwniThermokipiou",
    "DexameniNerou",
    "RoiNerou",
    "ProgrammaArdefsis",
    "ProgrammaAnakyklwsis",
    "ProgrammaFwtismou",
    "Fwtovoltaiko",
    "Syssoreftis",
    "EnergeiakoFortio",
    "OximaExerevnis",
    "ApostoliOximatos",
    "ShmeioDiadromis",
    "ExwterikosKindynos",
    "Synagermos",
    "Entoli",
    "SymvanEntolis",
    "EktelesiSenariou",
    "StigmiotypoSenariou",
    "Apofasi",
    "IstorikoElegxou",
    "KatastasiProsomoiwsis",
    "Proepiskopisi",
]
