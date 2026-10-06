"""Exploración · Tramo INGESTA: la misma fuente F02, consultada con DuckDB sin bajarla.
pip install duckdb      ·      python3 explorar/duckdb_remoto.py
Compárenlo con: python3 ingesta/pull_desempeno.py  (deben dar los mismos 5 años y 86.45 en 2020)"""
from urllib.parse import quote
import duckdb

consulta = ("$select=anio,dato&$where="
            + quote("codigo_entidad='76001' AND indicador='MDM'")
            + "&$order=anio")
url = "https://www.datos.gov.co/resource/nkjx-rsq7.json?" + consulta
print("DuckDB", duckdb.__version__)
print(duckdb.sql(f"SELECT anio, ROUND(CAST(dato AS DOUBLE), 2) AS mdm FROM read_json_auto('{url}') ORDER BY anio"))