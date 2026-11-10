"""Περιβάλλον μεταναστεύσεων του Smart Mars Colony."""

from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from backend.app.montela import VasiMontelwn
from backend.app.pyrinas.rythmiseis import rythmiseis

rythmisi = context.config

if rythmisi.config_file_name is not None:
    fileConfig(rythmisi.config_file_name)

# Ορισμός του metadata όλων των ORM μοντέλων
metadedomena_stoxou = VasiMontelwn.metadata

# Δυναμική ρύθμιση της διεύθυνσης βάσης από τις ρυθμίσεις της εφαρμογής
rythmisi.set_main_option("sqlalchemy.url", rythmiseis.DIADROMI_VASIS)


def ektelesi_xwris_syndesi() -> None:
    """Παραγωγή SQL μεταναστεύσεων χωρίς εκτέλεση."""
    dieythynsi = rythmisi.get_main_option("sqlalchemy.url")
    context.configure(
        url=dieythynsi,
        target_metadata=metadedomena_stoxou,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        render_as_batch=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def ektelesi_me_syndesi() -> None:
    """Εκτέλεση μεταναστεύσεων με έλεγχο ακεραιότητας SQLite."""
    diamorfwsi = rythmisi.get_section(rythmisi.config_ini_section, {})
    diamorfwsi["sqlalchemy.url"] = rythmiseis.DIADROMI_VASIS

    mixani = engine_from_config(
        diamorfwsi,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with mixani.connect() as syndesi:
        # Το batch SQLite αναδημιουργεί πίνακες με διατήρηση ξένων κλειδιών.
        einai_sqlite = syndesi.dialect.name == "sqlite"
        if einai_sqlite:
            syndesi.exec_driver_sql("PRAGMA foreign_keys=OFF")
            syndesi.commit()
        context.configure(
            connection=syndesi,
            target_metadata=metadedomena_stoxou,
            render_as_batch=True,
        )

        with context.begin_transaction():
            context.run_migrations()
        if einai_sqlite:
            paraviaseis = syndesi.exec_driver_sql("PRAGMA foreign_key_check").fetchall()
            if paraviaseis:
                raise RuntimeError("Η μετανάστευση εντόπισε παραβίαση ξένων κλειδιών.")
            syndesi.exec_driver_sql("PRAGMA foreign_keys=ON")


if context.is_offline_mode():
    ektelesi_xwris_syndesi()
else:
    ektelesi_me_syndesi()
