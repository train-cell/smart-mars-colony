"""Διαδρομή συγκεντρωτικής εικόνας αποικίας (SHARED-01)."""

from typing import Any, Dict

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.vasi.synthesi import pare_synedria_vasis
from backend.app.ypiresies.ypiresia_symvantwn_kai_senariwn import YpiresiaSymvantwnKaiSenariwn

router = APIRouter(tags=["Σύνοψη Αποικίας"])


@router.get("/synopsi", summary="Συνοπτική κοινή κατάσταση αποικίας και ενεργοί συναγερμοί")
def pare_synopsi(synedria: Session = Depends(pare_synedria_vasis)) -> Dict[str, Any]:
    """Επιστρέφει ενοποιημένη εικόνα των 3 υποσυστημάτων, πόρων και συναγερμών."""
    ypiresia = YpiresiaSymvantwnKaiSenariwn(synedria)
    return ypiresia.pare_synopsi_apoikias()
