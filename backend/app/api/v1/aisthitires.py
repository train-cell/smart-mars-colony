"""Διαδρομές αισθητήρων και καταγεγραμμένων μετρήσεων."""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.app.apothikes.apothiki_ypostiriksis_zwis import ApothikiYpostiriksisZwis
from backend.app.pyrinas.sfalmata import KodikosSfalmatos, SfalmaDomain
from backend.app.vasi.synthesi import pare_synedria_vasis

router = APIRouter(prefix="/aisthitires", tags=["Αισθητήρες & Μετρήσεις"])


@router.get("", summary="Λίστα αισθητήρων με προαιρετικό φιλτράρισμα asset/metric")
def pare_aisthitires(
    yposystima: Optional[str] = Query(default=None),
    typos_megethous: Optional[str] = Query(default=None),
    id_xwrou: Optional[str] = Query(default=None),
    synedria: Session = Depends(pare_synedria_vasis),
) -> List[Dict[str, Any]]:
    """Επιστρέφει τους αισθητήρες της αποικίας και την πιο πρόσφατη μέτρησή τους."""
    apothiki = ApothikiYpostiriksisZwis(synedria)
    aisthitires = apothiki.pare_aisthitires(
        yposystima=yposystima, typos_megethous=typos_megethous, id_xwrou=id_xwrou
    )
    apotelesmata = []
    for a in aisthitires:
        teleftaia = apothiki.pare_teleftaia_metrisi(a.id_aisthitira)
        apotelesmata.append(
            {
                "id_aisthitira": a.id_aisthitira,
                "kodikos": a.kodikos_aisthitira,
                "typos_megethous": a.typos_megethous,
                "yposystima": a.yposystima,
                "id_xwrou": a.id_xwrou,
                "monada": a.monada,
                "katastasi": a.katastasi,
                "teleftaia_metrisi": (
                    {
                        "timi": teleftaia.timi,
                        "monada": teleftaia.monada,
                        "eidos": teleftaia.eidos,
                        "poiotita": teleftaia.poiotita,
                        "tasi": teleftaia.tasi,
                        "einai_palio": teleftaia.einai_palio,
                        "xronos_metrisis": teleftaia.xronos_metrisis,
                    }
                    if teleftaia
                    else None
                ),
            }
        )
    return apotelesmata


@router.get("/{id_aisthitira}/metriseis", summary="Ιστορικό και ποιότητα μετρήσεων αισθητήρα")
def pare_metriseis_aisthitira(
    id_aisthitira: str,
    orio: int = Query(default=50, ge=1, le=500),
    synedria: Session = Depends(pare_synedria_vasis),
) -> List[Dict[str, Any]]:
    """Επιστρέφει χρονοσειρά μετρήσεων αισθητήρα με αξιολόγηση ποιότητας."""
    apothiki = ApothikiYpostiriksisZwis(synedria)
    aisth = apothiki.pare_aisthitira_ana_id(id_aisthitira)
    if not aisth:
        raise SfalmaDomain(
            kodikos=KodikosSfalmatos.DEN_VRETHIKE,
            minyma=f"Ο αισθητήρας '{id_aisthitira}' δεν βρέθηκε.",
            katastasi_http=404,
        )

    metriseis = apothiki.pare_istoriko_metrisewn(id_aisthitira, orio=orio)
    return [
        {
            "id_metrisis": m.id_metrisis,
            "timi": m.timi,
            "monada": m.monada,
            "eidos": m.eidos,
            "pigi": m.pigi,
            "poiotita": m.poiotita,
            "tasi": m.tasi,
            "apolyti_avevaiotita": m.apolyti_avevaiotita,
            "einai_palio": m.einai_palio,
            "xronos_metrisis": m.xronos_metrisis,
        }
        for m in metriseis
    ]
