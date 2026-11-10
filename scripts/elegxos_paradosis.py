"""Ελέγχει την παράδοση μέσω πραγματικού HTTP σε ιδιωτική προσωρινή SQLite.

Δεν δέχεται εξωτερική διεύθυνση API και δεν επαναφέρει προσωπική εγκατάσταση.
Οι επαναφορές αφορούν μόνο τη βάση που δημιουργεί το ίδιο το εργαλείο.
"""

import argparse
import json
import math
import os
import socket
import subprocess
import sys
import tempfile
import time
from contextlib import contextmanager
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

PROELEFSI = "http://localhost:5173"


@contextmanager
def prosorini_egkatastasi():
    """Αναβαθμίζει νέα βάση και τερματίζει αποκλειστικά τη δική της διεργασία."""
    riza = Path(__file__).resolve().parents[1]
    with tempfile.TemporaryDirectory(prefix="mars-paradosi-") as katalogos:
        perivallon = {
            **os.environ,
            "PERIVALLON": "dokimes",
            "DIADROMI_VASIS": "sqlite:///" + str(Path(katalogos) / "paradosi.sqlite"),
            "EPITREPOMENES_PROELEFSEIS": PROELEFSI,
            "PYTHONDONTWRITEBYTECODE": "1",
        }
        with (Path(katalogos) / "ektelesi.log").open("w+") as katagrafi:
            for entoli in (
                [sys.executable, "-m", "alembic", "upgrade", "head"],
                [sys.executable, "-m", "scripts.arxika_dedomena"],
            ):
                subprocess.run(
                    entoli,
                    cwd=riza,
                    env=perivallon,
                    stdout=katagrafi,
                    stderr=subprocess.STDOUT,
                    check=True,
                    timeout=30,
                )
            with socket.socket() as syndesi:
                syndesi.bind(("127.0.0.1", 0))
                thyra = syndesi.getsockname()[1]
            diadikasia = subprocess.Popen(
                [
                    sys.executable,
                    "-m",
                    "uvicorn",
                    "backend.app.main:efarmogi",
                    "--host",
                    "127.0.0.1",
                    "--port",
                    str(thyra),
                ],
                cwd=riza,
                env=perivallon,
                stdout=katagrafi,
                stderr=subprocess.STDOUT,
            )
            diefthynsi = f"http://127.0.0.1:{thyra}"
            try:
                orio = time.monotonic() + 15
                while time.monotonic() < orio:
                    if diadikasia.poll() is not None:
                        break
                    try:
                        with urlopen(diefthynsi + "/api/v1/ygeia", timeout=0.5) as apantisi:
                            if apantisi.status == 200:
                                yield diefthynsi
                                return
                    except (URLError, TimeoutError):
                        time.sleep(0.1)
                katagrafi.flush()
                katagrafi.seek(0)
                raise RuntimeError("Απέτυχε η δοκιμαστική εκκίνηση:\n" + katagrafi.read()[-3000:])
            finally:
                diadikasia.terminate()
                try:
                    diadikasia.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    diadikasia.kill()
                    diadikasia.wait(timeout=5)


class ElegxosParadosis:
    """Πελάτης της τεκμηριωμένης σύμβασης, χωρίς άμεση πρόσβαση σε ORM ή services."""

    def __init__(self, diefthynsi):
        self.diefthynsi = diefthynsi
        self.elegxoi = []

    def apaitise(self, synthiki, perigrafi):
        if not synthiki:
            raise RuntimeError("Αποτυχία ελέγχου: " + perigrafi)
        self.elegxoi.append(perigrafi)

    def konta(self, timi, anamenomeni, perigrafi, anoxi=1e-6):
        self.apaitise(math.isclose(timi, anamenomeni, rel_tol=0, abs_tol=anoxi), perigrafi)

    def klisi(
        self,
        methodos,
        diadromi,
        dedomena=None,
        xristis="syntonistis",
        anamenomeni=200,
        kefalides=None,
    ):
        olikes = {"Origin": PROELEFSI, **(kefalides or {})}
        if xristis:
            olikes["X-Id-Xristi"] = xristis
        if dedomena is not None:
            olikes["Content-Type"] = "application/json"
        aitima = Request(
            self.diefthynsi + diadromi,
            data=json.dumps(dedomena).encode() if dedomena is not None else None,
            headers=olikes,
            method=methodos,
        )
        try:
            apantisi = urlopen(aitima, timeout=10)
        except HTTPError as sfalma:
            apantisi = sfalma
        with apantisi:
            soma = apantisi.read().decode()
            katastasi, kefalides_apantisis = apantisi.status, apantisi.headers
        if katastasi != anamenomeni:
            raise RuntimeError(
                f"{methodos} {diadromi}: αναμενόταν {anamenomeni}, λήφθηκε {katastasi}: {soma}"
            )
        self.apaitise(
            kefalides_apantisis.get("Access-Control-Allow-Origin") == PROELEFSI,
            "CORS στην " + diadromi,
        )
        apotelesma = json.loads(soma)
        if anamenomeni >= 400:
            self.apaitise(
                apotelesma["sfalma"]["id_aitimatos"] == kefalides_apantisis["X-Id-Aitimatos"],
                "Κοινό σφάλμα με συσχέτιση αιτήματος",
            )
        return apotelesma

    def epanafora(self):
        self.klisi("POST", "/api/v1/prosomoiwsi/epanafora", {"epivevaiwsi": True})

    def katastasi_xwrou(self):
        return self.klisi("GET", "/api/v1/xwroi-katoikisis/xwros_01/katastasi")

    def stathmi_nerou(self):
        dexamenes = self.klisi("GET", "/api/v1/nero/dexamenes")["dexamenes"]
        return next(d for d in dexamenes if d["id_dexamenis"] == "dexameni_01")["trexwn_ogkos_l"]

    def thermokrasia(self):
        self.epanafora()
        diadromi = "/api/v1/xwroi-katoikisis/xwros_01/thermokrasia/"
        ekdosi = self.katastasi_xwrou()["ekdosi_katastasis"]
        dedomena = {"epithymiti_thermokrasia_k": 295, "anamenomeni_ekdosi_katastasis": ekdosi}
        self.klisi("POST", diadromi + "proepiskopisi", dedomena, xristis=None, anamenomeni=401)
        self.klisi(
            "POST", diadromi + "proepiskopisi", dedomena, xristis="xristis_porwn", anamenomeni=403
        )
        self.klisi(
            "POST",
            diadromi + "proepiskopisi",
            {**dedomena, "epithymiti_thermokrasia_k": 310},
            xristis="xristis_zwis",
            anamenomeni=422,
        )
        proep = self.klisi("POST", diadromi + "proepiskopisi", dedomena, xristis="xristis_zwis")
        self.konta(proep["epiptwsi"]["metavoli_w"], 200, "Θερμική μεταβολή 200 W")
        self.konta(
            self.katastasi_xwrou()["thermokrasia"]["epithymiti_k"],
            293,
            "Το preview δεν αλλάζει στόχο",
        )
        soma = {
            "id_proepiskopisis": proep["id_proepiskopisis"],
            "anamenomeni_ekdosi_katastasis": ekdosi,
        }
        kefalides = {
            "Idempotency-Key": "paradosi_thermokrasias",
            "X-Id-Aitimatos": "paradosi_thermokrasias",
        }
        entoli = self.klisi(
            "POST", diadromi + "entoles", soma, xristis="xristis_zwis", kefalides=kefalides
        )
        epanalipsi = self.klisi(
            "POST", diadromi + "entoles", soma, xristis="xristis_zwis", kefalides=kefalides
        )
        self.apaitise(entoli == epanalipsi, "Ακριβής idempotent επανάληψη επιβεβαίωσης")
        self.klisi("GET", "/api/v1/entoles/" + entoli["id_entolis"])
        self.konta(
            self.katastasi_xwrou()["thermokrasia"]["eswteriki_k"],
            293,
            "Η επιβεβαίωση δεν αλλάζει ακαριαία μέτρηση",
        )
        self.klisi(
            "POST", diadromi + "proepiskopisi", dedomena, xristis="xristis_zwis", anamenomeni=409
        )
        self.klisi("POST", "/api/v1/prosomoiwsi/vima", {"lepta": 30})
        teliki = self.katastasi_xwrou()["thermokrasia"]["eswteriki_k"]
        self.konta(teliki, 293.0356779352834, "Αναλυτική θερμοκρασία μετά 30 min")
        istoriko = self.klisi("GET", "/api/v1/istoriko-elegxou")
        self.apaitise(
            any(s["id_aitimatos"] == "paradosi_thermokrasias" for s in istoriko),
            "Η επιβεβαίωση διατηρεί ίχνος ελέγχου",
        )
        return {"metavoli_w": 200, "thermokrasia_meta_30min_k": teliki}

    def ardefsi(self):
        self.epanafora()
        diadromi = "/api/v1/thermokipia/thermokipio_01/ardefsi/"
        proep = self.klisi(
            "POST",
            diadromi + "proepiskopisi",
            {
                "id_zwnis": "zwni_01",
                "posotita_nerou_l": 100,
                "diarkeia_lepta": 30,
                "xronos_enarksis": "2026-11-10T12:30:00Z",
            },
            xristis="xristis_porwn",
        )
        self.konta(self.stathmi_nerou(), 7500, "Η προεπισκόπηση δεν αφαιρεί νερό")
        programma = self.klisi(
            "POST",
            diadromi + "programmata",
            {"id_proepiskopisis": proep["id_proepiskopisis"]},
            xristis="xristis_porwn",
        )
        self.konta(self.stathmi_nerou(), 7500, "Η δέσμευση δεν αφαιρεί φυσικό νερό")
        self.konta(programma["desmevmeno_nero_l"], 100, "Η επιβεβαίωση δεσμεύει 100 L")
        self.klisi("POST", "/api/v1/prosomoiwsi/vima", {"lepta": 30})
        self.konta(self.stathmi_nerou(), 7502.5, "Καμία άρδευση πριν την έναρξη")
        self.klisi("POST", "/api/v1/prosomoiwsi/vima", {"lepta": 30})
        self.konta(self.stathmi_nerou(), 7405, "Μία πραγματική παράδοση 100 L")
        programmata = self.klisi("GET", diadromi + "programmata")
        self.apaitise(
            next(p for p in programmata if p["id_programmatos"] == programma["id_programmatos"])[
                "katastasi"
            ]
            == "oloklirothike",
            "Η ολοκλήρωση ακολουθεί τη φυσική εκτέλεση",
        )
        self.klisi("POST", "/api/v1/prosomoiwsi/vima", {"lepta": 5})
        self.konta(
            self.stathmi_nerou(), 7405 + 5 / 12, "Δεν επανακαταναλώνεται το ολοκληρωμένο πρόγραμμα"
        )
        self.epanafora()
        proep = self.klisi(
            "POST",
            diadromi + "proepiskopisi",
            {"id_zwnis": "zwni_01", "posotita_nerou_l": 100},
            xristis="xristis_porwn",
        )
        programma = self.klisi(
            "POST",
            diadromi + "programmata",
            {"id_proepiskopisis": proep["id_proepiskopisis"]},
            xristis="xristis_porwn",
        )
        self.klisi(
            "POST",
            "/api/v1/ardefsi/programmata/" + programma["id_programmatos"] + "/akyrosi",
            xristis="xristis_porwn",
        )
        self.konta(self.stathmi_nerou(), 7500, "Η ακύρωση αποδεσμεύει χωρίς εικονική επιστροφή")
        return {"posotita_l": 100, "stathmi_meta_60min_l": 7405, "akyrosi_prin_ektelesi": True}

    def kataigida(self):
        self.epanafora()
        proep = self.klisi("POST", "/api/v1/senaria/kataigida-skonis/proepiskopisi")
        statistika = proep["statistika_senariou"]
        self.konta(statistika["fwtovoltaika"]["arxiki_kw"], 4.8, "Αρχική ηλιακή παραγωγή 4,8 kW")
        self.konta(
            statistika["fwtovoltaika"]["kataigida_kw"], 0.8, "Ηλιακή παραγωγή καταιγίδας 0,8 kW"
        )
        self.konta(
            statistika["fortia_kai_autonomia"]["kataigida_me_anavlita"]["autonomia_wres"],
            30 / 15.2,
            "Αυτονομία καταιγίδας χωρίς παύση",
            1e-4,
        )
        self.klisi("POST", "/api/v1/senaria/kataigida-skonis/energopoiisi")
        proep = self.klisi("POST", "/api/v1/senaria/kataigida-skonis/proepiskopisi")
        apofasi = self.klisi(
            "POST",
            "/api/v1/senaria/kataigida_skonis_2026/apofaseis",
            {
                "id_proepiskopisis": proep["id_proepiskopisis"],
                "epilogi": "syndyasmos_pliroys_asfaleias",
                "aitiologia": "Επαλήθευση ελεγχόμενης παράδοσης",
            },
        )
        self.apaitise(
            apofasi["egkekrimeni"] is True, "Η κοινή απόφαση χρειάζεται πραγματική έγκριση"
        )
        self.apaitise(
            apofasi["entoli_oximatos"]["katastasi_entolis"] == "avevaio",
            "Η απουσία σήματος δεν βεβαιώνει στάση",
        )
        synopsi = self.klisi("GET", "/api/v1/synopsi")
        self.konta(synopsi["energeia"]["elleimma_kw"], 11.2, "Έλλειμμα μετά παύση 11,2 kW")
        self.konta(synopsi["energeia"]["autonomia_wres"], 30 / 11.2, "Αυτονομία μετά παύση", 0.001)
        self.klisi("POST", "/api/v1/senaria/prokathorismena/apokatastasi/energopoiisi")
        self.klisi("POST", "/api/v1/prosomoiwsi/vima", {"lepta": 1})
        self.apaitise(
            self.klisi("GET", "/api/v1/oximata")[0]["katastasi_oximatos"] == "asfalis_stasi",
            "Η αποκατάσταση και νέο βήμα επιβεβαιώνουν στάση",
        )
        return {
            "autonomia_prin_wres": 30 / 15.2,
            "autonomia_meta_wres": 30 / 11.2,
            "epivevaiwsi_meta_apokatastasi": True,
        }

    def ektelese(self):
        aitima = Request(
            self.diefthynsi + "/api/v1/prosomoiwsi/vima",
            method="OPTIONS",
            headers={
                "Origin": PROELEFSI,
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "content-type,x-id-xristi,idempotency-key,x-id-aitimatos",
            },
        )
        with urlopen(aitima, timeout=5) as apantisi:
            self.apaitise(
                apantisi.headers.get("Access-Control-Allow-Origin") == PROELEFSI,
                "CORS preflight επιτρέπει τις κεφαλίδες διεπαφής",
            )
        sxhma = self.klisi("GET", "/openapi.json")
        apothikevmeno = json.loads(
            (Path(__file__).resolve().parents[1] / "docs/koino/openapi.json").read_text()
        )
        self.apaitise(sxhma == apothikevmeno, "Το δημοσιευμένο OpenAPI συμφωνεί με την εφαρμογή")
        pv = self.klisi("GET", "/api/v1/energeia/fwtovoltaika")[0]
        self.apaitise(
            pv["poiotita"] == "egkyro" and pv["xronos_metrisis"].endswith(("Z", "+00:00")),
            "PV με πρόσφατη ποιότητα και χρόνο UTC",
        )
        roes = {
            "thermokrasia": self.thermokrasia(),
            "ardefsi": self.ardefsi(),
            "kataigida": self.kataigida(),
        }
        self.epanafora()
        self.klisi("POST", "/api/v1/senaria/prokathorismena/vlavi_aisthitira_oxygonou/energopoiisi")
        self.klisi("GET", "/api/v1/xwroi-katoikisis/xwros_01/provlepsi-oxygonou", anamenomeni=503)
        return {
            "katastasi": "epityxia",
            "ekdosi": sxhma["info"]["version"],
            "arithmos_elegxwn": len(self.elegxoi),
            "elegxoi": self.elegxoi,
            "roes": roes,
            "prosopiki_vasi_xrisimopoiithike": False,
            "pragmatiko_frontend_elegxthike": False,
        }


def kyrio():
    parsertis = argparse.ArgumentParser(description=__doc__)
    parsertis.add_argument("--anafora", type=Path, help="Προαιρετικό αρχείο αποτελεσμάτων JSON")
    orismata = parsertis.parse_args()
    with prosorini_egkatastasi() as diefthynsi:
        apotelesma = ElegxosParadosis(diefthynsi).ektelese()
    keimeno = json.dumps(apotelesma, ensure_ascii=False, indent=2) + "\n"
    if orismata.anafora:
        orismata.anafora.parent.mkdir(parents=True, exist_ok=True)
        orismata.anafora.write_text(keimeno, encoding="utf-8")
    print(keimeno)


if __name__ == "__main__":
    kyrio()
