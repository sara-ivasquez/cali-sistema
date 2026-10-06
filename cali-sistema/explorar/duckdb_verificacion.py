"""Exploración · Tramo VERIFICACIÓN: segunda herramienta sobre los MISMOS datos y controles.

No reemplaza a verificacion/verificar.py (ese es el oficial y el que bloquea la publicación).
Aquí se repiten algunos de sus controles con SQL en DuckDB, para contrastar que una herramienta
distinta llega a las mismas conclusiones sobre los mismos archivos del lago y el catálogo.
No modifica datos ni el verificador oficial: solo lee.

    pip install duckdb        (no se instala aquí; si falta, el script lo avisa y sale)
    python3 explorar/duckdb_verificacion.py
    # comparar con: python3 verificacion/verificar.py

Controles replicados (equivalentes a los del oficial):
  A. Rangos con sentido de las cifras del lago (mismos límites que RANGOS en verificar.py).
  B. Coherencia lago -> catálogo: la fuente de cada archivo del lago está 'Integrada al lago'.
  C. Listas cerradas: licencia y estado de cada fuente dentro de catalogo/listas.json.
  D. Coordenadas del GeoJSON dentro de la caja que contiene a Cali.

Lo que NO cubre (y por qué): el oficial además revisa que cada cifra sea numérica y la
presencia de todos los campos de procedencia; aquí el foco es contrastar rangos, coherencia,
listas y geografía con SQL. El resultado de esta exploración no se publica ni queda en el lago.
"""
import json
import sys
from pathlib import Path

try:
    import duckdb
except ModuleNotFoundError:
    sys.exit("Falta DuckDB. Instálalo con 'pip install duckdb' para correr esta exploración "
             "(no se instala automáticamente). El verificador oficial no necesita DuckDB.")

RAIZ = Path(__file__).resolve().parent.parent
LAGO = (RAIZ / "lago").as_posix()
CAT = (RAIZ / "catalogo" / "fuentes.json").as_posix()
LISTAS = (RAIZ / "catalogo" / "listas.json").as_posix()
GEO = (RAIZ / "territorio" / "comunas.geojson").as_posix()

# Mismos límites que RANGOS en verificacion/verificar.py (copiados tal cual para el contraste).
RANGOS = {
    "vistas_ultimo_mes": (0, 10_000_000),
    "mdm_ultimo_anio": (0, 100),
    "poblacion_ultimo_anio": (1_000_000, 4_000_000),
    "densidad_ultimo_anio": (0, 100_000),
    "numero_comunas": (20, 25),
}
# Misma caja que CALI en verificar.py (lon, lat).
CALI = {"lon": (-76.9, -76.3), "lat": (3.2, 3.7)}

con = duckdb.connect()
fallas = []


def chequear(cond, msg):
    if not cond:
        fallas.append(msg)


print("DuckDB", duckdb.__version__)

# ----- A. Rangos de las cifras del lago (una fila por cifra, leyendo cada JSON del lago) -----
# Se leen las cifras de cada archivo del lago y se contrastan con los mismos rangos del oficial.
for archivo in sorted(Path(LAGO).glob("*.json")):
    d = json.loads(archivo.read_text(encoding="utf-8"))
    for k, v in (d.get("cifras") or {}).items():
        if k in RANGOS and isinstance(v, (int, float)):
            lo, hi = RANGOS[k]
            # el contraste del rango se hace en SQL para que sea DuckDB quien evalúe
            dentro = con.execute("SELECT ? BETWEEN ? AND ?", [v, lo, hi]).fetchone()[0]
            chequear(dentro, f"A · {archivo.name}: '{k}' = {v} fuera de [{lo}, {hi}]")
            print(f"  A · {archivo.name}: {k} = {v}  rango [{lo}, {hi}]  -> {'ok' if dentro else 'FUERA'}")

# ----- B y C. Catálogo: coherencia y listas cerradas, con SQL sobre fuentes.json y listas.json -----
listas = json.loads(Path(LISTAS).read_text(encoding="utf-8"))

# B. Toda fuente que aparece en algún archivo del lago debe estar 'Integrada al lago' en el catálogo.
fuentes_lago = sorted({json.loads(a.read_text(encoding="utf-8")).get("fuente")
                       for a in Path(LAGO).glob("*.json")})
# añadir la fuente declarada por el GeoJSON
geo_raw = json.loads(Path(GEO).read_text(encoding="utf-8"))
if geo_raw.get("fuente"):
    fuentes_lago = sorted(set(fuentes_lago) | {geo_raw["fuente"]})

estados = con.execute(f"""
    SELECT id, estado, licencia
    FROM read_json_auto('{CAT}')
    WHERE id IN ({','.join('?' for _ in fuentes_lago)})
""", fuentes_lago).fetchall()
estado_por_id = {r[0]: (r[1], r[2]) for r in estados}

for fid in fuentes_lago:
    if fid not in estado_por_id:
        chequear(False, f"B · la fuente {fid} usada por el lago no está en el catálogo")
        continue
    estado, licencia = estado_por_id[fid]
    chequear(estado == "Integrada al lago", f"B · {fid}: el lago la usa pero el catálogo dice '{estado}'")
    chequear(licencia in listas["licencias"], f"C · {fid}: licencia '{licencia}' fuera de la lista cerrada")
    print(f"  B/C · {fid}: estado '{estado}' · licencia '{licencia}' -> "
          f"{'ok' if estado == 'Integrada al lago' and licencia in listas['licencias'] else 'REVISAR'}")

# C (continuación). Todos los estados del catálogo dentro de la lista cerrada.
estados_fuera = con.execute(f"""
    SELECT id, estado FROM read_json_auto('{CAT}')
    WHERE estado NOT IN ({','.join('?' for _ in listas['estados'])})
""", listas["estados"]).fetchall()
for fid, estado in estados_fuera:
    chequear(False, f"C · {fid}: estado '{estado}' fuera de la lista cerrada")

# ----- D. Coordenadas del GeoJSON dentro de Cali -----
# DuckDB lee el GeoJSON como JSON y se extraen los puntos; se cuenta cuántos caen fuera de la caja.
coords = []
def recolectar(c):
    if isinstance(c, list) and c and isinstance(c[0], (int, float)):
        coords.append((c[0], c[1]))
    elif isinstance(c, list):
        for x in c:
            recolectar(x)
for ft in geo_raw.get("features", []):
    recolectar(ft["geometry"]["coordinates"])

con.execute("CREATE TEMP TABLE puntos(lon DOUBLE, lat DOUBLE)")
con.executemany("INSERT INTO puntos VALUES (?, ?)", coords)
fuera = con.execute("""
    SELECT count(*) FROM puntos
    WHERE lon NOT BETWEEN ? AND ? OR lat NOT BETWEEN ? AND ?
""", [CALI["lon"][0], CALI["lon"][1], CALI["lat"][0], CALI["lat"][1]]).fetchone()[0]
total = con.execute("SELECT count(*) FROM puntos").fetchone()[0]
chequear(fuera == 0, f"D · {fuera} de {total} puntos del GeoJSON caen fuera de Cali")
print(f"  D · puntos del GeoJSON: {total} total, {fuera} fuera de la caja de Cali -> {'ok' if fuera == 0 else 'REVISAR'}")

print(f"\nExploración DuckDB: {len(fallas)} hallazgo(s).")
for f in fallas:
    print("  ✗", f)
print("\nEsto es una exploración de contraste; la publicación la decide verificacion/verificar.py.")
sys.exit(1 if fallas else 0)
