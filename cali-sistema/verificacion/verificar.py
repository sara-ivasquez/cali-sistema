"""Si una sola comprobación falla, no se publica.  python3 verificacion/verificar.py"""
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
catalogo = {f["id"]: f for f in json.loads((RAIZ / "catalogo/fuentes.json").read_text(encoding="utf-8"))}
listas = json.loads((RAIZ / "catalogo/listas.json").read_text(encoding="utf-8"))

# Rangos con sentido para cada cifra: una cifra fuera de rango es un error de ingesta, no un hallazgo
RANGOS = {
    "vistas_ultimo_mes": (0, 10_000_000),
    "mdm_ultimo_anio": (0, 100),
    "poblacion_ultimo_anio": (1_000_000, 4_000_000),
    "densidad_ultimo_anio": (0, 100_000),
    "numero_comunas": (20, 25),
}
# Caja que contiene a Cali (lon, lat): cualquier coordenada fuera es una geometría mal proyectada
CALI = {"lon": (-76.9, -76.3), "lat": (3.2, 3.7)}

fallas, pruebas = [], 0


def comprobar(cond, msg):
    global pruebas
    pruebas += 1
    if not cond:
        fallas.append(msg)


# 1. El catálogo usa solo valores de las listas cerradas, y lo integrado tiene fecha de prueba
for f in catalogo.values():
    comprobar(f["entidad"] in listas["entidades"], f"{f['id']}: entidad fuera de la lista")
    comprobar(f["licencia"] in listas["licencias"], f"{f['id']}: licencia fuera de la lista")
    comprobar(f["estado"] in listas["estados"], f"{f['id']}: estado fuera de la lista")
    if f["estado"] == "Integrada al lago":
        comprobar(bool(f.get("probado")), f"{f['id']}: está integrada pero no tiene fecha de prueba")

# 2. Cada archivo del lago tiene procedencia completa y cifras dentro de rango
archivos = sorted((RAIZ / "lago").glob("*.json"))
comprobar(len(archivos) > 0, "el lago está vacío: corran python3 ingesta/todo.py")
for a in archivos:
    d = json.loads(a.read_text(encoding="utf-8"))
    for campo in ("fuente", "url", "vigencia", "probado", "cifras", "registros"):
        comprobar(d.get(campo) not in (None, "", [], {}), f"{a.name}: falta '{campo}'")
    fuente = d.get("fuente")
    comprobar(fuente in catalogo, f"{a.name}: la fuente {fuente} no está en el catálogo")
    if fuente in catalogo:
        comprobar(catalogo[fuente]["estado"] == "Integrada al lago",
                  f"{a.name}: {fuente} está en el lago pero el catálogo dice '{catalogo[fuente]['estado']}'")
    for k, v in d.get("cifras", {}).items():
        comprobar(isinstance(v, (int, float)), f"{a.name}: cifra '{k}' no es número ({v})")
        if k in RANGOS and isinstance(v, (int, float)):
            lo, hi = RANGOS[k]
            comprobar(lo <= v <= hi, f"{a.name}: '{k}' = {v} fuera del rango esperado [{lo}, {hi}]")

# 3. El territorio está en grados y dentro de Cali
geo_path = RAIZ / "territorio" / "comunas.geojson"
if geo_path.exists():
    geo = json.loads(geo_path.read_text(encoding="utf-8"))
    comprobar(geo.get("type") == "FeatureCollection", "comunas.geojson no es una FeatureCollection")
    comprobar(len(geo.get("features", [])) > 0, "comunas.geojson no tiene polígonos")
    comprobar(geo.get("fuente") in catalogo, "comunas.geojson no dice de qué fuente sale")

    def puntos(c):
        if isinstance(c[0], (int, float)):
            yield c
        else:
            for x in c:
                yield from puntos(x)

    fuera = 0
    for ft in geo.get("features", []):
        for lon, lat, *_ in puntos(ft["geometry"]["coordinates"]):
            if not (CALI["lon"][0] <= lon <= CALI["lon"][1] and CALI["lat"][0] <= lat <= CALI["lat"][1]):
                fuera += 1
    comprobar(fuera == 0, f"comunas.geojson: {fuera} puntos fuera de Cali (¿coordenadas invertidas o en metros?)")

print(f"{pruebas} comprobaciones, {len(fallas)} fallas")
for f in fallas:
    print("  ✗", f)
sys.exit(1 if fallas else 0)