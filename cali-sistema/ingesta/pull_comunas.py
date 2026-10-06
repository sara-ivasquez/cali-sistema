"""F04 · Límites de las comunas de Cali desde el WFS de la IDESC, en GeoJSON (EPSG:4326).
En lugar de adivinar el nombre de la capa, se lo pregunta al servidor (GetCapabilities)."""
import json
import re
import sys
import urllib.request
from datetime import date
from urllib.parse import urlencode
from comun import RAIZ, RAW, UA, guardar_lago

SERVIDORES = [
    "https://ws-idesc.cali.gov.co/geoserver/wfs",
    "https://ws-idesc.cali.gov.co/geoserver/idesc/wfs",
]
intentos = []


def pedir(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read().decode("utf-8", errors="replace")


def error_del_servidor(texto):
    """Saca el mensaje de un ServiceExceptionReport de GeoServer."""
    m = re.search(r"<ServiceException(\s[^>]*)?>(.*?)</ServiceException>", texto, re.S)
    if not m:
        return " ".join(texto[:300].split())
    return f"{(m.group(1) or '').strip()} {' '.join(m.group(2).split())}"


def anotar(msg):
    intentos.append(msg)
    print(msg)


# 1. Preguntarle al servidor qué capas tiene y quedarse con las que hablan de comunas
base, capas = None, []
for b in SERVIDORES:
    try:
        caps = pedir(f"{b}?service=WFS&request=GetCapabilities&version=1.0.0")
    except Exception as e:
        anotar(f"  ✗ {b}: GetCapabilities sin respuesta: {e}")
        continue
    nombres = re.findall(r"<Name>([^<]+)</Name>", caps)
    capas = [n for n in nombres if "comuna" in n.lower()]
    anotar(f"  · {b}: {len(nombres)} capas en total, {len(capas)} mencionan 'comuna': {capas}")
    if capas:
        base = b
        break

if not capas:
    RAW.mkdir(parents=True, exist_ok=True)
    (RAW / "comunas_intentos.txt").write_text("\n".join(intentos), encoding="utf-8")
    sys.exit("✗ El servidor no publica ninguna capa de comunas. Detalle en lago/raw/comunas_intentos.txt")

# Primero las que parecen límites puros; las de observatorios (obs_, x_comuna) al final
capas.sort(key=lambda n: (0 if n.lower().endswith("comunas") else 1, "obs" in n.lower()))

# 2. Probar cada capa: sirve si trae polígonos y entre 15 y 30 elementos (Cali tiene 22 comunas)
geo, url_usada, capa_usada = None, None, None
for capa in capas:
    url = f"{base}?" + urlencode({"service": "WFS", "version": "1.0.0", "request": "GetFeature",
                                  "typeName": capa, "outputFormat": "application/json", "srsName": "EPSG:4326"})
    try:
        texto = pedir(url)
    except Exception as e:
        anotar(f"  ✗ {capa}: sin respuesta: {e}")
        continue
    try:
        candidato = json.loads(texto)
    except json.JSONDecodeError:
        anotar(f"  ✗ {capa}: error del servidor: {error_del_servidor(texto)}")
        continue
    feats = candidato.get("features", [])
    tipos = {(f.get("geometry") or {}).get("type") for f in feats}
    if not feats or not tipos <= {"Polygon", "MultiPolygon"}:
        anotar(f"  ✗ {capa}: {len(feats)} elementos de tipo {tipos}: no son polígonos de comunas")
        continue
    if not 15 <= len(feats) <= 30:
        anotar(f"  ✗ {capa}: {len(feats)} polígonos; se esperaban unos 22")
        continue
    anotar(f"  ✓ {capa}: {len(feats)} polígonos")
    geo, url_usada, capa_usada = candidato, url, capa
    break

RAW.mkdir(parents=True, exist_ok=True)
(RAW / "comunas_intentos.txt").write_text("\n".join(intentos), encoding="utf-8")
if geo is None:
    sys.exit("✗ Ninguna capa sirvió como límites de comunas. Detalle en lago/raw/comunas_intentos.txt")
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

geo.update({"fuente": "F04", "url": url_usada, "capa": capa_usada,
            "vigencia": "capa vigente IDESC", "probado": date.today().isoformat()})
(RAIZ / "territorio").mkdir(exist_ok=True)
(RAIZ / "territorio" / "comunas.geojson").write_text(json.dumps(geo, ensure_ascii=False), encoding="utf-8")

registros = [ft["properties"] for ft in geo["features"]]
guardar_lago("territorio", "F04", url_usada, vigencia="capa vigente IDESC", registros=registros,
             cifras={"numero_comunas": len(registros)})
print(f"Cali comunas: {len(registros)} polígonos de la capa {capa_usada} guardados en territorio/comunas.geojson")