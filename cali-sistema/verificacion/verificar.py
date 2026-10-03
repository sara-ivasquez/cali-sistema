"""Si una sola comprobación falla, no se publica.  python3 verificacion/verificar.py"""
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
catalogo = {f["id"]: f for f in json.loads((RAIZ / "catalogo/fuentes.json").read_text(encoding="utf-8"))}
listas = json.loads((RAIZ / "catalogo/listas.json").read_text(encoding="utf-8"))

fallas, pruebas = [], 0


def comprobar(cond, msg):
    global pruebas
    pruebas += 1
    if not cond:
        fallas.append(msg)


# 1. El catálogo usa solo valores de las listas cerradas
for f in catalogo.values():
    comprobar(f["entidad"] in listas["entidades"], f"{f['id']}: entidad fuera de la lista")
    comprobar(f["licencia"] in listas["licencias"], f"{f['id']}: licencia fuera de la lista")
    comprobar(f["estado"] in listas["estados"], f"{f['id']}: estado fuera de la lista")

# 2. Cada archivo del lago tiene procedencia completa y cifras válidas
archivos = sorted((RAIZ / "lago").glob("*.json"))
comprobar(len(archivos) > 0, "el lago está vacío: corran python3 ingesta/todo.py")
for a in archivos:
    d = json.loads(a.read_text(encoding="utf-8"))
    for campo in ("fuente", "url", "vigencia", "probado", "cifras", "registros"):
        comprobar(d.get(campo) not in (None, "", [], {}), f"{a.name}: falta '{campo}'")
    comprobar(d.get("fuente") in catalogo, f"{a.name}: la fuente {d.get('fuente')} no está en el catálogo")
    for k, v in d.get("cifras", {}).items():
        comprobar(isinstance(v, (int, float)) and v >= 0, f"{a.name}: cifra '{k}' inválida ({v})")

print(f"{pruebas} comprobaciones, {len(fallas)} fallas")
for f in fallas:
    print("  ✗", f)
sys.exit(1 if fallas else 0)
