"""Funciones compartidas por todos los scripts de ingesta. Solo biblioteca estándar."""
import json
import urllib.request
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
LAGO = RAIZ / "lago"
RAW = LAGO / "raw"
UA = {"User-Agent": "taller-sistemas-de-informacion/1.0 (curso universitario EAFIT)"}


def bajar_json(url):
    """Baja un JSON de una URL (sin llaves)."""
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def guardar_crudo(nombre, datos):
    """Copia cruda en lago/raw/ (no se sube al repo)."""
    RAW.mkdir(parents=True, exist_ok=True)
    (RAW / f"{nombre}.json").write_text(json.dumps(datos, ensure_ascii=False, indent=2), encoding="utf-8")


def guardar_lago(nombre, fuente, url, vigencia, registros, cifras):
    """Escribe lago/<nombre>.json con la procedencia pegada a los datos."""
    salida = {
        "fuente": fuente,                     # ID del catálogo: F01, F02...
        "url": url,
        "vigencia": vigencia,                 # qué periodo cubre el dato
        "probado": date.today().isoformat(),  # día en que la fuente respondió de verdad
        "cifras": cifras,                     # las cifras que mostrará el sistema
        "registros": registros,               # la serie limpia completa
    }
    (LAGO / f"{nombre}.json").write_text(json.dumps(salida, ensure_ascii=False, indent=2), encoding="utf-8")
    return salida
