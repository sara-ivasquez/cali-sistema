"""F01 · Vistas mensuales del artículo de la ciudad en Wikipedia (es)."""
from urllib.parse import quote
from comun import bajar_json, guardar_crudo, guardar_lago

CIUDAD = "Cali"
ARTICULO = "Cali"  # Revisen en es.wikipedia.org el título exacto y que no sea desambiguación
URL = ("https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/"
       f"es.wikipedia/all-access/user/{quote(ARTICULO)}/monthly/20250101/20260930")

datos = bajar_json(URL)
guardar_crudo("escucha", datos)

registros = [
    {"periodo": f"{i['timestamp'][:4]}-{i['timestamp'][4:6]}", "vistas": i["views"]}
    for i in datos["items"]
]
ultimo = registros[-1]
guardar_lago(
    "escucha", "F01", URL, vigencia=ultimo["periodo"], registros=registros,
    cifras={"vistas_ultimo_mes": ultimo["vistas"]},
)
print(f"{CIUDAD}: {len(registros)} meses, último {ultimo['periodo']} con {ultimo['vistas']} vistas")
