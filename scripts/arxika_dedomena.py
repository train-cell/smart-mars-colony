#!/usr/bin/env python3
"""Σενάριο φόρτωσης αρχικών δεδομένων επίδειξης (Seed Data).

Εκτελείται από το τερματικό:
python scripts/arxika_dedomena.py [--reset]
"""

import sys

from backend.app.arxika_dedomena.fortwsi_dedomenwn import arxikopoiisi_dedomenwn_epideiksis
from backend.app.vasi.synthesi import SynedriaVasis


def main():
    epanarxikopoiisi = "--reset" in sys.argv
    synedria = SynedriaVasis()
    try:
        print("Έναρξη αρχικοποίησης δεδομένων επίδειξης...")
        arxikopoiisi_dedomenwn_epideiksis(synedria, epanarxikopoiisi=epanarxikopoiisi)
        print("Η αρχικοποίηση ολοκληρώθηκε επιτυχώς!")
    finally:
        synedria.close()


if __name__ == "__main__":
    main()
