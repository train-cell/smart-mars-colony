"""Συμπλήρωση πυρήνα, μόνιμων εντολών και προσομοίωσης

Revision ID: c551f5a42528
Revises: 1c63bef8cc3e
Create Date: 2026-11-10 12:25:18.108996

"""

import json
from datetime import datetime, timezone
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# Αναγνωριστικά της αλυσίδας μεταναστεύσεων.
revision: str = "c551f5a42528"
down_revision: Union[str, Sequence[str], None] = "1c63bef8cc3e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Προσθέτει λειτουργικά πεδία χωρίς απώλεια υφιστάμενων δεδομένων."""

    # Η παλιά εφαρμογή αφαιρούσε αμέσως τις δεσμεύσεις μελλοντικής άρδευσης.
    # Ελέγχουμε πριν από κάθε DDL ώστε η αναβάθμιση να μη δημιουργήσει υπερχείλιση.
    epistrofes = list(
        op.get_bind()
        .execute(
            sa.text(
                "SELECT d.id_dexamenis, d.trexwn_ogkos_l, d.xwritikotita_l, SUM(p.posotita_nerou_l) AS desmevmeno "
                "FROM dexamenes_nerou d JOIN programmata_ardefsis p ON p.id_dexamenis=d.id_dexamenis "
                "WHERE p.katastasi='programmatismeno' GROUP BY d.id_dexamenis"
            )
        )
        .mappings()
    )
    for epistrofi in epistrofes:
        if (
            epistrofi["trexwn_ogkos_l"] + epistrofi["desmevmeno"]
            > epistrofi["xwritikotita_l"] + 1e-8
        ):
            raise RuntimeError(
                "Οι παλιές δεσμεύσεις άρδευσης υπερβαίνουν τη χωρητικότητα. Απαιτείται συμφωνία αποθέματος πριν την αναβάθμιση."
            )
    # Παλαιές εγκαταστάσεις έχουν την αρχική αγγλική στήλη με το ίδιο revision.
    stiles = {
        stili["name"] for stili in sa.inspect(op.get_bind()).get_columns("katastasi_prosomoiwsis")
    }
    if "active_scenario" in stiles and "energo_senario" not in stiles:
        op.execute(
            "ALTER TABLE katastasi_prosomoiwsis RENAME COLUMN active_scenario TO energo_senario"
        )
    for pinakas, palio, neo in [
        ("xristes", "email", "ilektroniki_dieythynsi"),
        ("roloi_xristwn", "id", "id_rolou"),
        ("katastasi_prosomoiwsis", "seed", "sporos"),
        ("stigmiotypa_senariwn", "dedomena_snapshot", "dedomena_stigmiotypou"),
    ]:
        op.execute(f"ALTER TABLE {pinakas} RENAME COLUMN {palio} TO {neo}")
    op.add_column(
        "oximata_exerevnis",
        sa.Column("xwritikotita_energeias_kwh", sa.Float(), server_default="1", nullable=False),
    )
    op.add_column(
        "oximata_exerevnis",
        sa.Column("isxys_fortisis_kw", sa.Float(), server_default="0.2", nullable=False),
    )
    op.create_table(
        "proepiskopiseis",
        sa.Column("id_proepiskopisis", sa.String(length=50), nullable=False),
        sa.Column("id_xristi", sa.String(length=50), nullable=False),
        sa.Column("drasi", sa.String(length=100), nullable=False),
        sa.Column("id_ontotitas", sa.String(length=100), nullable=False),
        sa.Column("dedomena", sa.JSON(), nullable=False),
        sa.Column("stigmiotypo", sa.JSON(), nullable=False),
        sa.Column("katastasi", sa.String(length=30), server_default="energi", nullable=False),
        sa.Column("epoxi_prosomoiwsis", sa.String(length=36), nullable=False),
        sa.Column("xronos_dimiourgias", sa.DateTime(timezone=True), nullable=False),
        sa.Column("xronos_liksis", sa.DateTime(timezone=True), nullable=False),
        sa.Column("xronos_liksis_prosomoiwsis", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["id_xristi"],
            ["xristes.id_xristi"],
        ),
        sa.PrimaryKeyConstraint("id_proepiskopisis"),
    )
    with op.batch_alter_table("apostoles_oximatwn", schema=None) as metavoli_pinaka:
        metavoli_pinaka.add_column(
            sa.Column("apostasi_km", sa.Float(), server_default="0", nullable=False)
        )
        metavoli_pinaka.add_column(
            sa.Column("ektimwmeni_diarkeia_wres", sa.Float(), server_default="0", nullable=False)
        )
        metavoli_pinaka.add_column(
            sa.Column("apaitoumeni_energeia_kwh", sa.Float(), server_default="0", nullable=False)
        )
        metavoli_pinaka.add_column(
            sa.Column("energeia_katanalwtheisa_kwh", sa.Float(), server_default="0", nullable=False)
        )
        metavoli_pinaka.add_column(
            sa.Column("maza_fortiou_kg", sa.Float(), server_default="0", nullable=False)
        )
        metavoli_pinaka.add_column(
            sa.Column("plithos_plirwmatos", sa.Integer(), server_default="0", nullable=False)
        )
        metavoli_pinaka.add_column(
            sa.Column("sxedio", sa.JSON(), server_default="{}", nullable=False)
        )
        metavoli_pinaka.add_column(sa.Column("id_entolis", sa.String(length=50), nullable=True))

    with op.batch_alter_table("dexamenes_nerou", schema=None) as metavoli_pinaka:
        metavoli_pinaka.add_column(
            sa.Column("diathesimi_anakyklwsi", sa.Boolean(), server_default="1", nullable=False)
        )
        metavoli_pinaka.add_column(
            sa.Column("typos_nerou", sa.String(length=30), server_default="katharo", nullable=False)
        )
        metavoli_pinaka.add_column(
            sa.Column("rythmos_diarrois_l_h", sa.Float(), server_default="0", nullable=False)
        )

    with op.batch_alter_table("entoles", schema=None) as metavoli_pinaka:
        metavoli_pinaka.add_column(sa.Column("id_ontotitas", sa.String(length=100), nullable=True))
        metavoli_pinaka.add_column(
            sa.Column("apotypwma_aitimatos", sa.String(length=64), nullable=True)
        )

    with op.batch_alter_table("exwterikoi_kindynoi", schema=None) as metavoli_pinaka:
        metavoli_pinaka.add_column(
            sa.Column(
                "monada_aktinovolias", sa.String(length=30), server_default="mSv/h", nullable=False
            )
        )
        metavoli_pinaka.add_column(
            sa.Column("pigi", sa.String(length=100), server_default="prosomoiwsi", nullable=False)
        )
        metavoli_pinaka.add_column(sa.Column("apolyti_avevaiotita", sa.Float(), nullable=True))
        metavoli_pinaka.add_column(
            sa.Column("energi", sa.Boolean(), server_default="1", nullable=False)
        )

    with op.batch_alter_table("katastasi_prosomoiwsis", schema=None) as metavoli_pinaka:
        metavoli_pinaka.add_column(
            sa.Column("ekdosi_katastasis", sa.Integer(), server_default="1", nullable=False)
        )
        metavoli_pinaka.add_column(
            sa.Column(
                "epoxi_prosomoiwsis", sa.String(length=36), server_default="arxiki", nullable=False
            )
        )
        metavoli_pinaka.add_column(
            sa.Column("pausi_anavlitwn", sa.Boolean(), server_default="0", nullable=False)
        )

    with op.batch_alter_table("metriseis_aisthitirwn", schema=None) as metavoli_pinaka:
        metavoli_pinaka.add_column(
            sa.Column("xronos_paralavis", sa.DateTime(timezone=True), nullable=True)
        )

    with op.batch_alter_table("oximata_exerevnis", schema=None) as metavoli_pinaka:
        metavoli_pinaka.add_column(
            sa.Column("xronos_teleftaias_tilemetrias", sa.DateTime(timezone=True), nullable=True)
        )
        metavoli_pinaka.add_column(
            sa.Column("isxys_kinisis_kw", sa.Float(), server_default="0.6", nullable=False)
        )
        metavoli_pinaka.add_column(
            sa.Column("voithitiki_isxys_w", sa.Float(), server_default="100", nullable=False)
        )
        metavoli_pinaka.add_column(
            sa.Column("syntetagmeni_x", sa.Float(), server_default="0", nullable=False)
        )
        metavoli_pinaka.add_column(
            sa.Column("syntetagmeni_y", sa.Float(), server_default="0", nullable=False)
        )
        metavoli_pinaka.add_column(
            sa.Column("maza_fortiou_kg", sa.Float(), server_default="0", nullable=False)
        )
        metavoli_pinaka.add_column(
            sa.Column("plithos_plirwmatos", sa.Integer(), server_default="0", nullable=False)
        )
        metavoli_pinaka.add_column(
            sa.Column("kathysterisi_epikoinwnias_s", sa.Float(), server_default="0", nullable=False)
        )

    with op.batch_alter_table("programmata_anakyklwsis", schema=None) as metavoli_pinaka:
        metavoli_pinaka.add_column(
            sa.Column("posotita_eisodou_l", sa.Float(), server_default="0", nullable=False)
        )
        metavoli_pinaka.add_column(
            sa.Column("apwleia_l", sa.Float(), server_default="0", nullable=False)
        )
        metavoli_pinaka.add_column(
            sa.Column("isxys_kw", sa.Float(), server_default="0.2", nullable=False)
        )
        metavoli_pinaka.add_column(
            sa.Column("id_dexamenis_pigis", sa.String(length=50), nullable=True)
        )
        metavoli_pinaka.add_column(sa.Column("id_entolis", sa.String(length=50), nullable=True))
        metavoli_pinaka.add_column(
            sa.Column("ektelestheisa_posotita_l", sa.Float(), server_default="0", nullable=False)
        )
        metavoli_pinaka.create_foreign_key(
            "fk_anakyklwsi_pigi_nerou", "dexamenes_nerou", ["id_dexamenis_pigis"], ["id_dexamenis"]
        )

    with op.batch_alter_table("programmata_ardefsis", schema=None) as metavoli_pinaka:
        metavoli_pinaka.add_column(sa.Column("id_entolis", sa.String(length=50), nullable=True))
        metavoli_pinaka.add_column(
            sa.Column("ektelestheisa_posotita_l", sa.Float(), server_default="0", nullable=False)
        )

    with op.batch_alter_table("programmata_fwtismou", schema=None) as metavoli_pinaka:
        metavoli_pinaka.add_column(sa.Column("id_entolis", sa.String(length=50), nullable=True))
        metavoli_pinaka.add_column(
            sa.Column("ektelestheisa_energeia_kwh", sa.Float(), server_default="0", nullable=False)
        )

    with op.batch_alter_table("roes_nerou", schema=None) as metavoli_pinaka:
        metavoli_pinaka.add_column(
            sa.Column("id_programmatos", sa.String(length=50), nullable=True)
        )
        metavoli_pinaka.add_column(
            sa.Column("xronos_enarksis", sa.DateTime(timezone=True), nullable=True)
        )
        metavoli_pinaka.add_column(
            sa.Column("xronos_liksis", sa.DateTime(timezone=True), nullable=True)
        )
        metavoli_pinaka.add_column(
            sa.Column("energi", sa.Boolean(), server_default="1", nullable=False)
        )

    with op.batch_alter_table("synagermoi", schema=None) as metavoli_pinaka:
        metavoli_pinaka.add_column(sa.Column("kleidi_aitias", sa.String(length=150), nullable=True))
        metavoli_pinaka.add_column(
            sa.Column("energi_aitia", sa.Boolean(), server_default="1", nullable=False)
        )
        metavoli_pinaka.create_index(
            metavoli_pinaka.f("ix_synagermoi_kleidi_aitias"), ["kleidi_aitias"], unique=False
        )

    with op.batch_alter_table("thermokipia", schema=None) as metavoli_pinaka:
        metavoli_pinaka.add_column(
            sa.Column("diathesimi_ardefsi", sa.Boolean(), server_default="1", nullable=False)
        )
        metavoli_pinaka.add_column(
            sa.Column("diathesimos_fwtismos", sa.Boolean(), server_default="1", nullable=False)
        )

    with op.batch_alter_table("xwroi_katoikisis", schema=None) as metavoli_pinaka:
        metavoli_pinaka.add_column(
            sa.Column(
                "thermiki_xwritikotita_j_k", sa.Float(), server_default="10000000", nullable=False
            )
        )
        metavoli_pinaka.add_column(
            sa.Column(
                "rythmos_diarrois_piesis_pa_h", sa.Float(), server_default="0", nullable=False
            )
        )

    for epistrofi in epistrofes:
        op.get_bind().execute(
            sa.text(
                "UPDATE dexamenes_nerou SET trexwn_ogkos_l=trexwn_ogkos_l+:posotita, ekdosi_katastasis=ekdosi_katastasis+1 WHERE id_dexamenis=:anagnwristiko"
            ),
            {"posotita": epistrofi["desmevmeno"], "anagnwristiko": epistrofi["id_dexamenis"]},
        )
    for epistrofi in epistrofes:
        op.get_bind().execute(
            sa.text(
                "INSERT INTO istoriko_elegxou (id_xristi,rolos,energeia,ontotita,id_ontotitas,palia_timi,nea_timi,aitiologia,xronos_katagrafis) "
                "VALUES (:xristis,:rolos,:drasi,:ontotita,:anagnwristiko,:palia,:nea,:aitia,:xronos)"
            ),
            {
                "xristis": "systima_metanastefsis",
                "rolos": "systima",
                "drasi": "epistrofi_palias_desmefsis_ardefsis",
                "ontotita": "dexamenes_nerou",
                "anagnwristiko": epistrofi["id_dexamenis"],
                "palia": json.dumps({"trexwn_ogkos_l": epistrofi["trexwn_ogkos_l"]}),
                "nea": json.dumps(
                    {"trexwn_ogkos_l": epistrofi["trexwn_ogkos_l"] + epistrofi["desmevmeno"]}
                ),
                "aitia": "Αναβάθμιση παλαιών δεσμεύσεων σε χρονικά εκτελούμενη άρδευση, χωρίς διπλή αφαίρεση.",
                "xronos": datetime.now(timezone.utc).replace(tzinfo=None).isoformat(sep=" "),
            },
        )
    op.execute(
        "UPDATE metriseis_aisthitirwn SET xronos_paralavis = xronos_metrisis WHERE xronos_paralavis IS NULL"
    )
    op.execute("UPDATE roes_nerou SET energi = 0 WHERE typos_rois = 'ardefsi'")


def downgrade() -> None:
    """Επαναφέρει το αρχικό σχήμα· τα νέα δεδομένα απαιτούν αντίγραφο ασφαλείας."""
    for pinakas, palio, neo in [
        ("xristes", "email", "ilektroniki_dieythynsi"),
        ("roloi_xristwn", "id", "id_rolou"),
        ("katastasi_prosomoiwsis", "seed", "sporos"),
        ("stigmiotypa_senariwn", "dedomena_snapshot", "dedomena_stigmiotypou"),
    ]:
        op.execute(f"ALTER TABLE {pinakas} RENAME COLUMN {neo} TO {palio}")
    op.drop_column("oximata_exerevnis", "isxys_fortisis_kw")
    op.drop_column("oximata_exerevnis", "xwritikotita_energeias_kwh")

    with op.batch_alter_table("xwroi_katoikisis", schema=None) as metavoli_pinaka:
        metavoli_pinaka.drop_column("rythmos_diarrois_piesis_pa_h")
        metavoli_pinaka.drop_column("thermiki_xwritikotita_j_k")

    with op.batch_alter_table("thermokipia", schema=None) as metavoli_pinaka:
        metavoli_pinaka.drop_column("diathesimos_fwtismos")
        metavoli_pinaka.drop_column("diathesimi_ardefsi")

    with op.batch_alter_table("synagermoi", schema=None) as metavoli_pinaka:
        metavoli_pinaka.drop_index(metavoli_pinaka.f("ix_synagermoi_kleidi_aitias"))
        metavoli_pinaka.drop_column("energi_aitia")
        metavoli_pinaka.drop_column("kleidi_aitias")

    with op.batch_alter_table("roes_nerou", schema=None) as metavoli_pinaka:
        metavoli_pinaka.drop_column("energi")
        metavoli_pinaka.drop_column("xronos_liksis")
        metavoli_pinaka.drop_column("xronos_enarksis")
        metavoli_pinaka.drop_column("id_programmatos")

    with op.batch_alter_table("programmata_fwtismou", schema=None) as metavoli_pinaka:
        metavoli_pinaka.drop_column("ektelestheisa_energeia_kwh")
        metavoli_pinaka.drop_column("id_entolis")

    with op.batch_alter_table("programmata_ardefsis", schema=None) as metavoli_pinaka:
        metavoli_pinaka.drop_column("ektelestheisa_posotita_l")
        metavoli_pinaka.drop_column("id_entolis")

    with op.batch_alter_table("programmata_anakyklwsis", schema=None) as metavoli_pinaka:
        metavoli_pinaka.drop_constraint("fk_anakyklwsi_pigi_nerou", type_="foreignkey")
        metavoli_pinaka.drop_column("ektelestheisa_posotita_l")
        metavoli_pinaka.drop_column("id_entolis")
        metavoli_pinaka.drop_column("id_dexamenis_pigis")
        metavoli_pinaka.drop_column("isxys_kw")
        metavoli_pinaka.drop_column("apwleia_l")
        metavoli_pinaka.drop_column("posotita_eisodou_l")

    with op.batch_alter_table("oximata_exerevnis", schema=None) as metavoli_pinaka:
        metavoli_pinaka.drop_column("xronos_teleftaias_tilemetrias")
        metavoli_pinaka.drop_column("kathysterisi_epikoinwnias_s")
        metavoli_pinaka.drop_column("plithos_plirwmatos")
        metavoli_pinaka.drop_column("maza_fortiou_kg")
        metavoli_pinaka.drop_column("syntetagmeni_y")
        metavoli_pinaka.drop_column("syntetagmeni_x")
        metavoli_pinaka.drop_column("voithitiki_isxys_w")
        metavoli_pinaka.drop_column("isxys_kinisis_kw")

    with op.batch_alter_table("metriseis_aisthitirwn", schema=None) as metavoli_pinaka:
        metavoli_pinaka.drop_column("xronos_paralavis")

    with op.batch_alter_table("katastasi_prosomoiwsis", schema=None) as metavoli_pinaka:
        metavoli_pinaka.drop_column("pausi_anavlitwn")
        metavoli_pinaka.drop_column("epoxi_prosomoiwsis")
        metavoli_pinaka.drop_column("ekdosi_katastasis")

    with op.batch_alter_table("exwterikoi_kindynoi", schema=None) as metavoli_pinaka:
        metavoli_pinaka.drop_column("energi")
        metavoli_pinaka.drop_column("apolyti_avevaiotita")
        metavoli_pinaka.drop_column("pigi")
        metavoli_pinaka.drop_column("monada_aktinovolias")

    with op.batch_alter_table("entoles", schema=None) as metavoli_pinaka:
        metavoli_pinaka.drop_column("apotypwma_aitimatos")
        metavoli_pinaka.drop_column("id_ontotitas")

    with op.batch_alter_table("dexamenes_nerou", schema=None) as metavoli_pinaka:
        metavoli_pinaka.drop_column("rythmos_diarrois_l_h")
        metavoli_pinaka.drop_column("typos_nerou")
        metavoli_pinaka.drop_column("diathesimi_anakyklwsi")

    with op.batch_alter_table("apostoles_oximatwn", schema=None) as metavoli_pinaka:
        metavoli_pinaka.drop_column("id_entolis")
        metavoli_pinaka.drop_column("sxedio")
        metavoli_pinaka.drop_column("plithos_plirwmatos")
        metavoli_pinaka.drop_column("maza_fortiou_kg")
        metavoli_pinaka.drop_column("energeia_katanalwtheisa_kwh")
        metavoli_pinaka.drop_column("apaitoumeni_energeia_kwh")
        metavoli_pinaka.drop_column("ektimwmeni_diarkeia_wres")
        metavoli_pinaka.drop_column("apostasi_km")

    op.drop_table("proepiskopiseis")
