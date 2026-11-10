"""Διαδρομές αισθητήρων και καταγεγραμμένων μετρήσεων."""

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.app.apothikes.apothiki_ypostiriksis_zwis import ApothikiYpostiriksisZwis
from backend.app.pyrinas.sfalmata import KodikosSfalmatos, SfalmaKanona
from backend.app.sxhmata.apantiseis import AisthitirasApantisi, MetrisiApantisi
from backend.app.vasi.synthesi import pare_synedria_vasis
from backend.app.ypiresies.metriseis_kai_poiotita import provoli_metrisis

dromologitis = APIRouter(prefix="/aisthitires", tags=["Αισθητήρες & Μετρήσεις"])


@dromologitis.get("", summary="Λίστα αισθητήρων με προαιρετικό φιλτράρισμα asset/metric")
def pare_aisthitires(
    yposystima: Optional[str] = Query(default=None),
    typos_megethous: Optional[str] = Query(default=None),
    id_xwrou: Optional[str] = Query(default=None),
    synedria: Session = Depends(pare_synedria_vasis),
) -> list[AisthitirasApantisi]:
    """Επιστρέφει τους αισθητήρες της αποικίας και την πιο πρόσφατη μέτρησή τους."""
    apothiki = ApothikiYpostiriksisZwis(synedria)
    aisthitires = apothiki.pare_aisthitires(
        yposystima=yposystima, typos_megethous=typos_megethous, id_xwrou=id_xwrou
    )
    apotelesmata = []
    for stoixeio_alfa in aisthitires:
        teleftaia = apothiki.pare_teleftaia_metrisi(stoixeio_alfa.id_aisthitira)
        apotelesmata.append(
            {
                "id_aisthitira": stoixeio_alfa.id_aisthitira,
                "kodikos": stoixeio_alfa.kodikos_aisthitira,
                "typos_megethous": stoixeio_alfa.typos_megethous,
                "yposystima": stoixeio_alfa.yposystima,
                "id_xwrou": stoixeio_alfa.id_xwrou,
                "monada": stoixeio_alfa.monada,
                "katastasi": stoixeio_alfa.katastasi,
                "teleftaia_metrisi": provoli_metrisis(synedria, stoixeio_alfa, teleftaia),
            }
        )
    return apotelesmata


@dromologitis.get("/{id_aisthitira}/metriseis", summary="Ιστορικό και ποιότητα μετρήσεων αισθητήρα")
def pare_metriseis_aisthitira(
    id_aisthitira: str,
    orio: int = Query(default=50, ge=1, le=500),
    synedria: Session = Depends(pare_synedria_vasis),
) -> list[MetrisiApantisi]:
    """Επιστρέφει χρονοσειρά μετρήσεων αισθητήρα με αξιολόγηση ποιότητας."""
    apothiki = ApothikiYpostiriksisZwis(synedria)
    aisth = apothiki.pare_aisthitira_ana_id(id_aisthitira)
    if not aisth:
        raise SfalmaKanona(
            kodikos=KodikosSfalmatos.DEN_VRETHIKE,
            minyma=f"Ο αισθητήρας '{id_aisthitira}' δεν βρέθηκε.",
            katastasi_http=404,
        )

    metriseis = apothiki.pare_istoriko_metrisewn(id_aisthitira, orio=orio)
    return [
        {"id_metrisis": metrisi.id_metrisis, **provoli_metrisis(synedria, aisth, metrisi)}
        for metrisi in metriseis
    ]
