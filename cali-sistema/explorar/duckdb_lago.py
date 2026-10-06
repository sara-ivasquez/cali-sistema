"""Exploración · Tramo LAGO: los mismos JSON del lago, consultados con SQL en DuckDB.
pip install duckdb      ·      python3 explorar/duckdb_lago.py   (antes: python3 ingesta/todo.py)"""
from pathlib import Path
import duckdb

LAGO = (Path(__file__).resolve().parent.parent / "lago").as_posix()

# Cruce de dos fuentes por año: población (F03) y desempeño municipal (F02)
print(duckdb.sql(f"""
    WITH pob AS (SELECT r.anio, r.poblacion FROM (SELECT unnest(registros) AS r FROM read_json_auto('{LAGO}/poblacion.json'))),
         mdm AS (SELECT r.anio, r.mdm       FROM (SELECT unnest(registros) AS r FROM read_json_auto('{LAGO}/desempeno.json')))
    SELECT pob.anio, pob.poblacion, mdm.mdm
    FROM pob JOIN mdm USING (anio)
    ORDER BY anio
"""))