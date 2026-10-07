"""Verificación antes de publicar: con una sola falla no se publica.
Revisa el catálogo, el contrato de cada archivo del lago (contrato/CONTRATO.md),
que no haya datos personales y que el mapa caiga dentro de Cali.
    python3 verificacion/verificar.py        # muestra solo las fallas
    python3 verificacion/verificar.py -v     # muestra también lo que pasa"""
import json
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
VERBOSO = "-v" in sys.argv
catalogo = {f["id"]: f for f in json.loads((RAIZ / "catalogo/fuentes.json").read_text(encoding="utf-8"))}
listas = json.loads((RAIZ / "catalogo/listas.json").read_text(encoding="utf-8"))

# Rangos con sentido para cada cifra: una cifra fuera de rango es un error de ingesta, no un hallazgo
RANGOS = {
    "vistas_ultimo_mes": (0, 10_000_000),
    "mdm_ultimo_anio": (0, 100),
    "poblacion_ultimo_anio": (1_000_000, 4_000_000),
    "poblacion_urbana_ultimo_anio": (1_000_000, 4_000_000),
    "poblacion_rural_ultimo_anio": (0, 500_000),
    "densidad_ultimo_anio": (0, 100_000),
    "numero_comunas": (20, 25),
}
CALI = {"lon": (-76.9, -76.3), "lat": (3.2, 3.7)}  # caja que contiene a Cali
DIA = re.compile(r"\d{4}-\d{2}-\d{2}")
PII = re.compile(r"[\w.+-]+@[\w-]+\.[a-z]{2,}|(?<!\d)3\d{9}(?!\d)")  # correos y celulares colombianos
CAMPOS_PERSONALES = re.compile(r"cedula|documento_identidad|telefono|celular|correo|email", re.I)

fallas, pruebas = [], 0


def comprobar(cond, msg):
    global pruebas
    pruebas += 1
    if not cond:
        fallas.append(msg)
    elif VERBOSO:
        print("  PASS", msg)


def recorrer(x, clave=""):
    if isinstance(x, dict):
        for k, v in x.items():
            yield k, None
            yield from recorrer(v, k)
    elif isinstance(x, list):
        for v in x:
            yield from recorrer(v, clave)
    else:
        yield clave, x


# 1. Catálogo: listas cerradas, y lo integrado o probado tiene fecha de un día
for f in catalogo.values():
    comprobar(f["entidad"] in listas["entidades"], f"{f['id']}: entidad dentro de la lista cerrada")
    comprobar(f["licencia"] in listas["licencias"], f"{f['id']}: licencia dentro de la lista cerrada")
    comprobar(f["estado"] in listas["estados"], f"{f['id']}: estado dentro de la lista cerrada")
    if f["estado"] != "Candidata":
        comprobar(bool(f.get("probado")) and DIA.fullmatch(str(f.get("probado"))) is not None,
                  f"{f['id']}: tiene fecha de prueba (un día)")

# 2. Contrato de cada archivo del lago
archivos = sorted((RAIZ / "lago").glob("*.json"))
comprobar(len(archivos) > 0, "el lago no está vacío (si falla: python3 ingesta/todo.py)")
for a in archivos:
    d = json.loads(a.read_text(encoding="utf-8"))
    n = a.name
    comprobar(d.get("tema") == a.stem, f"{n}: el tema coincide con el nombre del archivo")
    comprobar(DIA.fullmatch(str(d.get("probado"))) is not None, f"{n}: probado es un día")
    fuentes = d.get("fuentes") or []
    ids = {f.get("id") for f in fuentes}
    comprobar(len(fuentes) > 0, f"{n}: declara al menos una fuente")
    for f in fuentes:
        comprobar(bool(f.get("url")) and bool(f.get("licencia")), f"{n}: {f.get('id')} con url y licencia")
        comprobar(f.get("id") in catalogo, f"{n}: {f.get('id')} existe en el catálogo")
        if f.get("id") in catalogo:
            comprobar(catalogo[f["id"]]["estado"] == "Integrada al lago",
                      f"{n}: {f['id']} figura como 'Integrada al lago' en el catálogo")
    cifras = d.get("cifras") or {}
    comprobar(len(cifras) > 0, f"{n}: tiene al menos una cifra")
    for k, c in cifras.items():
        completa = (isinstance(c, dict) and isinstance(c.get("valor"), (int, float))
                    and bool(c.get("unidad")) and bool(c.get("vigencia")) and c.get("fuente") in ids)
        comprobar(completa, f"{n}: {k} con valor, unidad, vigencia y fuente conocida")
        if completa and k in RANGOS:
            lo, hi = RANGOS[k]
            comprobar(lo <= c["valor"] <= hi, f"{n}: {k} = {c['valor']} dentro de [{lo}, {hi}]")
    for k, s in (d.get("series") or {}).items():
        ok = (bool(s.get("unidad")) and s.get("fuente") in ids and len(s.get("puntos", [])) > 0
              and all(isinstance(p, list) and len(p) == 2 and isinstance(p[1], (int, float)) for p in s["puntos"]))
        comprobar(ok, f"{n}: serie {k} con unidad, fuente conocida y puntos numéricos")
    pares = list(recorrer(d))
    sospechosos = sorted({k for k, _ in pares if k and CAMPOS_PERSONALES.search(str(k))})
    comprobar(not sospechosos, f"{n}: ningún campo con nombre de dato personal {sospechosos or ''}".rstrip())
    hallado = next((v for _, v in pares if isinstance(v, str) and PII.search(v)), None)
    comprobar(hallado is None, f"{n}: ningún texto con correo o celular {hallado or ''}".rstrip())

# 3. Territorio: en grados (WGS84) y dentro de Cali
geo_path = RAIZ / "territorio" / "comunas.geojson"
if geo_path.exists():
    geo = json.loads(geo_path.read_text(encoding="utf-8"))
    comprobar(geo.get("type") == "FeatureCollection", "comunas.geojson es una FeatureCollection")
    comprobar(len(geo.get("features", [])) > 0, "comunas.geojson tiene polígonos")
    comprobar(geo.get("fuente") in catalogo, "comunas.geojson dice de qué fuente sale")

    def puntos(c):
        if isinstance(c[0], (int, float)):
            yield c
        else:
            for x in c:
                yield from puntos(x)

    fuera = sum(1 for ft in geo.get("features", []) for lon, lat, *_ in puntos(ft["geometry"]["coordinates"])
                if not (CALI["lon"][0] <= lon <= CALI["lon"][1] and CALI["lat"][0] <= lat <= CALI["lat"][1]))
    comprobar(fuera == 0, f"comunas.geojson: todos los puntos dentro de Cali ({fuera} fuera)")

print(f"{pruebas} comprobaciones, {len(fallas)} fallas")
for f in fallas:
    print("  FAIL", f)
sys.exit(1 if fallas else 0)