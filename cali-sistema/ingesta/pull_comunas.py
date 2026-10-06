"""F04 · Límites de las comunas de Cali desde el WFS de la IDESC, en GeoJSON (EPSG:4326)."""
import json
import sys
import urllib.request
from datetime import date
from urllib.parse import urlencode
from comun import RAIZ, RAW, UA, guardar_lago

CAPA = "idesc:mc_comunas"
SERVIDORES = [
    "https://ws-idesc.cali.gov.co/geoserver/wfs",
    "https://ws-idesc.cali.gov.co/geoserver/idesc/wfs",
    "http://ws-idesc.cali.gov.co:8081/geoserver/idesc/wfs",
]
VARIANTES = [  # GeoServer acepta pedir GeoJSON de varias formas según la versión
    {"version": "1.0.0", "typeName": CAPA, "outputFormat": "application/json"},
    {"version": "1.0.0", "typeName": CAPA, "outputFormat": "json"},
    {"version": "2.0.0", "typeNames": CAPA, "outputFormat": "application/json"},
]


def pedir(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", errors="replace")


geo, url_usada, intentos = None, None, []
for base in SERVIDORES:
    for v in VARIANTES:
        url = f"{base}?" + urlencode({"service": "WFS", "request": "GetFeature", "srsName": "EPSG:4326", **v})
        try:
            texto = pedir(url)
        except Exception as e:
            intentos.append(f"{url}\n    -> sin respuesta: {e}")
            print(f"  ✗ {base} ({v['version']}, {v['outputFormat']}): sin respuesta: {e}")
            break  # si el servidor no responde, no tiene sentido probar más variantes en él
        try:
            geo = json.loads(texto)
            url_usada = url
            break
        except json.JSONDecodeError:
            muestra = " ".join(texto[:300].split())
            intentos.append(f"{url}\n    -> respondió pero no es JSON: {muestra}")
            print(f"  ✗ {base} ({v['version']}, {v['outputFormat']}): respondió, pero no es JSON: {muestra[:150]}…")
    if geo is not None:
        break

RAW.mkdir(parents=True, exist_ok=True)
(RAW / "comunas_intentos.txt").write_text("\n\n".join(intentos), encoding="utf-8")
if geo is None or geo.get("type") != "FeatureCollection":
    sys.exit("✗ Ningún servidor WFS devolvió GeoJSON. Detalle completo en lago/raw/comunas_intentos.txt")
(RAW / "comunas.json").write_text(json.dumps(geo, ensure_ascii=False), encoding="utf-8")


def recorrer(coords, f):
    if isinstance(coords[0], (int, float)):
        return f(coords)
    return [recorrer(c, f) for c in coords]


# Si el servidor devolvió (lat, lon) en vez de (lon, lat), se invierte. Cali: lon ≈ -76.5, lat ≈ 3.4
primero = geo["features"][0]["geometry"]["coordinates"]
while not isinstance(primero[0], (int, float)):
    primero = primero[0]
if abs(primero[0]) > 180:
    sys.exit("✗ Las coordenadas siguen en metros (EPSG:6249): el servidor no reproyectó.")
invertir = abs(primero[0]) < 10 and abs(primero[1]) > 50
if invertir:
    print("  ! Coordenadas en orden (lat, lon): se invierten.")

for ft in geo["features"]:
    g = ft["geometry"]
    g["coordinates"] = recorrer(
        g["coordinates"],
        lambda p: [round(p[1], 6), round(p[0], 6)] if invertir else [round(p[0], 6), round(p[1], 6)],
    )

print("Propiedades de cada comuna:", list(geo["features"][0]["properties"].keys()))

geo.update({"fuente": "F04", "url": url_usada, "vigencia": "capa vigente IDESC", "probado": date.today().isoformat()})
(RAIZ / "territorio").mkdir(exist_ok=True)
(RAIZ / "territorio" / "comunas.geojson").write_text(json.dumps(geo, ensure_ascii=False), encoding="utf-8")

registros = [ft["properties"] for ft in geo["features"]]
guardar_lago("territorio", "F04", url_usada, vigencia="capa vigente IDESC", registros=registros,
             cifras={"numero_comunas": len(registros)})
print(f"Cali comunas: {len(registros)} polígonos guardados en territorio/comunas.geojson")