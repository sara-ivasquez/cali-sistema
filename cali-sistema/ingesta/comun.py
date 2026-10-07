"""Funciones compartidas por todos los scripts de ingesta. Solo biblioteca estándar.
Cada archivo del lago se escribe con la forma del contrato: ver contrato/CONTRATO.md."""
import json
import urllib.request
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
LAGO = RAIZ / "lago"
RAW = LAGO / "raw"
UA = {"User-Agent": "taller-sistemas-de-informacion/1.0 (curso universitario EAFIT)"}

# Unidad de cada cifra y de cada serie. Se define UNA vez, aquí; una cifra sin unidad no entra al lago.
UNIDADES = {
    "vistas_ultimo_mes": "vistas de personas",
    "vistas": "vistas de personas",
    "mdm_ultimo_anio": "puntos de 0 a 100",
    "mdm": "puntos de 0 a 100",
    "poblacion_ultimo_anio": "habitantes",
    "poblacion": "habitantes",
    "poblacion_urbana_ultimo_anio": "habitantes",
    "poblacion_urbana": "habitantes",
    "poblacion_rural_ultimo_anio": "habitantes",
    "poblacion_rural": "habitantes",
    "densidad_ultimo_anio": "habitantes por km²",
    "densidad": "habitantes por km²",
    "numero_comunas": "comunas",
}
EJES = ("anio", "periodo")  # columnas que sirven de eje x para las series


def bajar_json(url):
    """Baja un JSON de una URL (sin llaves)."""
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def guardar_crudo(nombre, datos):
    """Copia cruda en lago/raw/ (no se sube al repo)."""
    RAW.mkdir(parents=True, exist_ok=True)
    (RAW / f"{nombre}.json").write_text(json.dumps(datos, ensure_ascii=False, indent=2), encoding="utf-8")


def fuente_del_catalogo(fid):
    """La fuente se copia del catálogo: el catálogo es la única verdad sobre nombre, estado y licencia."""
    catalogo = json.loads((RAIZ / "catalogo" / "fuentes.json").read_text(encoding="utf-8"))
    f = next((x for x in catalogo if x["id"] == fid), None)
    if f is None:
        raise SystemExit(f"✗ {fid} no está en catalogo/fuentes.json: catalóguela antes de ingerirla")
    return {k: f.get(k) for k in ("id", "nombre", "url", "estado", "licencia")}


def series_de(registros, fuente):
    """Arma las series del contrato a partir de los registros que tienen año o periodo."""
    if not registros or not isinstance(registros[0], dict):
        return {}
    eje = next((e for e in EJES if e in registros[0]), None)
    if eje is None:
        return {}
    series = {}
    for campo in registros[0]:
        if campo == eje or campo not in UNIDADES:
            continue
        puntos = [[r[eje], r[campo]] for r in registros if isinstance(r.get(campo), (int, float))]
        if puntos:
            series[campo] = {"unidad": UNIDADES[campo], "fuente": fuente, "puntos": puntos}
    return series


def guardar_lago(nombre, fuente, url, vigencia, registros, cifras):
    """Escribe lago/<nombre>.json con la forma del contrato."""
    sin_unidad = [k for k in cifras if k not in UNIDADES]
    if sin_unidad:
        raise SystemExit(f"✗ Cifras sin unidad (agréguenlas a UNIDADES en comun.py): {sin_unidad}")
    f = fuente_del_catalogo(fuente)
    f["url"] = url  # la URL exacta que se consultó, con sus filtros
    salida = {
        "tema": nombre,
        "probado": date.today().isoformat(),  # el día en que la fuente respondió de verdad
        "fuentes": [f],
        "cifras": {k: {"valor": v, "unidad": UNIDADES[k], "vigencia": vigencia, "fuente": fuente}
                   for k, v in cifras.items()},
        "series": series_de(registros, fuente),
        "registros": registros,  # extensión del contrato: la tabla limpia completa
    }
    (LAGO / f"{nombre}.json").write_text(json.dumps(salida, ensure_ascii=False, indent=1), encoding="utf-8")
    return salida