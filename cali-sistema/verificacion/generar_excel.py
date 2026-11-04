"""Genera el Excel de la segunda entrega (diccionario reconstruido) a partir del lago REAL.
Reconstruido con asistencia de Kiro: no es el archivo original de la entrega (no se encontró
en el repositorio), sino un equivalente generado desde los datos y el catálogo actuales.

    ../.venv/bin/python verificacion/generar_excel.py   # escribe entrega/diccionario_cali.xlsx

Requiere openpyxl. El contenido (ejemplos, fechas, fuentes) sale de archivos reales:
catalogo/fuentes.json, lago/*.json y territorio/comunas.geojson.
"""
import json
from datetime import date
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

RAIZ = Path(__file__).resolve().parent.parent
SALIDA = RAIZ / "entrega" / "diccionario_cali.xlsx"

catalogo = json.loads((RAIZ / "catalogo" / "fuentes.json").read_text(encoding="utf-8"))
lago = {p.stem: json.loads(p.read_text(encoding="utf-8")) for p in sorted((RAIZ / "lago").glob("*.json"))}
geo = json.loads((RAIZ / "territorio" / "comunas.geojson").read_text(encoding="utf-8"))

# ---- estilo ----
AZUL = PatternFill("solid", fgColor="1F6B54")
GRIS = PatternFill("solid", fgColor="E8EEEC")
BLANCO = Font(color="FFFFFF", bold=True)
NEGRITA = Font(bold=True)
BORDE = Border(*(Side(style="thin", color="C8D2CE") for _ in range(4)))
WRAP = Alignment(wrap_text=True, vertical="top")
WRAP_TOP = Alignment(wrap_text=True, vertical="top", horizontal="left")


def hoja(wb, titulo, encabezados, filas, anchos):
    ws = wb.create_sheet(titulo)
    for j, h in enumerate(encabezados, 1):
        c = ws.cell(1, j, h)
        c.fill = AZUL; c.font = BLANCO; c.alignment = WRAP; c.border = BORDE
    for i, fila in enumerate(filas, 2):
        for j, v in enumerate(fila, 1):
            c = ws.cell(i, j, v)
            c.alignment = WRAP_TOP; c.border = BORDE
            if i % 2 == 0:
                c.fill = GRIS
    for j, a in enumerate(anchos, 1):
        ws.column_dimensions[get_column_letter(j)].width = a
    ws.freeze_panes = "A2"
    return ws


wb = Workbook()
wb.remove(wb.active)

# ===================== 1. INSTRUCCIONES =====================
ws = wb.create_sheet("Instrucciones")
ws.column_dimensions["A"].width = 110
texto = [
    ("Diccionario de datos · Sistema de información de Santiago de Cali (segunda entrega)", NEGRITA),
    ("Grupo: Sara Isabel Vásquez · Alejandro Rendón — Tópicos de Sistemas de Información, Universidad EAFIT", None),
    ("", None),
    ("ARCHIVO RECONSTRUIDO. No se encontró el Excel original de la entrega en el repositorio.", NEGRITA),
    ("Este archivo se reconstruyó con asistencia de Kiro a partir de los datos reales del proyecto:", None),
    ("catalogo/fuentes.json, lago/*.json y territorio/comunas.geojson. Se regenera con:", None),
    ("    ../.venv/bin/python verificacion/generar_excel.py", None),
    ("", None),
    ("Hojas:", NEGRITA),
    ("• Fuentes — catálogo completo (integradas, candidata, descartadas y las que no existen/responden), con licencia, estado y fecha de prueba real.", None),
    ("• Diccionario — todos y solo los campos que el lago guarda de verdad, con su unidad, un ejemplo real y si el sistema lo muestra.", None),
    ("• Bitácora IA — qué se le encargó a cada herramienta de IA y qué se le corrigió, incluida esta sesión con Kiro.", None),
    ("• Resumen — cifras principales del sistema, con su fuente y vigencia.", None),
    ("", None),
    (f"Fecha de generación de este archivo: {date.today().isoformat()}", None),
    ("Enlace del sistema publicado: https://sara-ivasquez.github.io/cali-sistema/cali-sistema/web/", None),
    ("Repositorio: https://github.com/sara-ivasquez/cali-sistema", None),
    ("", None),
    ("Nota sobre PROXY / datos simulados: el sistema NO usa datos simulados ni aproximados.", NEGRITA),
    ("Todas las cifras salen de las fuentes integradas; las calculadas (porcentajes, árboles por km²) muestran su fórmula.", None),
    ("Nota sobre datos personales: ninguna fuente contiene datos de personas; todo está agregado por ciudad o por comuna.", None),
]
for i, (t, f) in enumerate(texto, 1):
    c = ws.cell(i, 1, t)
    c.alignment = WRAP_TOP
    if f:
        c.font = f

# ===================== 2. FUENTES =====================
filas_f = []
for f in catalogo:
    filas_f.append([
        f["id"], f["nombre"], f["entidad"], f.get("formato", ""), f.get("acceso", ""),
        f["licencia"], f["estado"], f.get("probado") or "—", f.get("url", ""),
        f.get("observaciones", ""),
    ])
hoja(wb, "Fuentes",
     ["ID", "Nombre", "Entidad", "Formato", "Acceso", "Licencia", "Estado", "Probado", "URL", "Observaciones"],
     filas_f,
     [6, 34, 26, 20, 18, 22, 16, 12, 44, 60])

# ===================== 3. DICCIONARIO =====================
# Campos que la página muestra (para marcar "Lo muestra el sistema")
MOSTRADOS = {
    "poblacion": {"anio", "poblacion", "poblacion_urbana", "poblacion_rural", "densidad",
                  "poblacion_ultimo_anio", "poblacion_urbana_ultimo_anio", "poblacion_rural_ultimo_anio", "densidad_ultimo_anio"},
    "desempeno": {"anio", "mdm", "mdm_ultimo_anio"},
    "escucha": {"periodo", "vistas", "vistas_ultimo_mes"},
    "territorio": {"id_comuna", "nombre", "no_arboles", "arbol_sano", "arb_regula", "arbol_seco", "arb_muerto", "numero_comunas"},
}
DESCR = {
    # poblacion
    "anio": "Año del registro",
    "poblacion": "Población total del distrito ese año (habitantes)",
    "poblacion_urbana": "Población de la zona urbana / comunas (habitantes)",
    "poblacion_rural": "Población de la zona rural / corregimientos (habitantes)",
    "densidad": "Densidad bruta del total del distrito (habitantes por hectárea)",
    # desempeno
    "mdm": "Medición de Desempeño Municipal, puntaje de 0 a 100",
    # escucha
    "periodo": "Mes del registro (AAAA-MM)",
    "vistas": "Vistas del artículo de Cali en Wikipedia ese mes",
    # territorio / censo arbóreo
    "gid": "Identificador interno de la capa WFS (no se usa)",
    "id_comuna": "Número de la comuna (1 a 22)",
    "nombre": "Nombre de la comuna",
    "no_arboles": "Total de árboles censados en la comuna",
    "arbol_sano": "Árboles en estado sano",
    "arbol_seco": "Árboles secos",
    "arb_muerto": "Árboles muertos",
    "arb_regula": "Árboles en estado regular",
    "area_m2": "INFERIDO (no definición oficial de la fuente): no parece ser el área de la comuna sino la cobertura arbórea en m², porque coincide con cobarb_ha × 10.000 salvo redondeo (diferencias de 1 a 5 m²). El sistema NO lo usa; el área se calcula desde el polígono.",
    "cobarb_ha": "Cobertura arbórea en hectáreas (significado parcial; el sistema no lo muestra)",
    "arb_habita": "Árboles por habitante (significado sin confirmar; no se muestra)",
    "arb_eep": "Árboles en Estructura Ecológica Principal (sigla EEP sin descripción en la fuente; no se muestra)",
    "m2_eep": "m² de EEP (sin descripción; no se muestra)",
    "ha_eep": "ha de EEP (sin descripción; no se muestra)",
    "arb_eep_ro": "Árboles EEP (variante; sin descripción; no se muestra)",
    "m2_eep_ron": "m² EEP (variante; sin descripción; no se muestra)",
    "ha_eep_ron": "ha EEP (variante; sin descripción; no se muestra)",
    "arb_eec_ep": "Árboles EEC-EP (siglas sin descripción; no se muestra)",
    "m2_eec_ep": "m² EEC-EP (sin descripción; no se muestra)",
    "ha_eec_ep": "ha EEC-EP (sin descripción; no se muestra)",
    "arb_eec_eq": "Árboles EEC-EQ (siglas sin descripción; no se muestra)",
    "m2_eec_eq": "m² EEC-EQ (sin descripción; no se muestra)",
    "ha_eec_eq": "ha EEC-EQ (sin descripción; no se muestra)",
}
UNIDAD_SERIE = {}
for tema, d in lago.items():
    for k, s in (d.get("series") or {}).items():
        UNIDAD_SERIE[(tema, k)] = s.get("unidad", "")
    for k, c in (d.get("cifras") or {}).items():
        UNIDAD_SERIE[(tema, k)] = c.get("unidad", "")

filas_d = []
for tema, d in lago.items():
    # registros (la tabla limpia)
    reg = d.get("registros", [])
    ejemplo = reg[-1] if reg and isinstance(reg[0], dict) else {}
    campos = list(ejemplo.keys()) if ejemplo else []
    # para territorio, los registros vienen de las properties del geojson
    if tema == "territorio" and geo.get("features"):
        ejemplo = geo["features"][0]["properties"]
        campos = list(ejemplo.keys())
    for campo in campos:
        unidad = UNIDAD_SERIE.get((tema, campo), "")
        muestra = "Sí" if campo in MOSTRADOS.get(tema, set()) else "No"
        filas_d.append([
            f"{tema} · registros", campo, DESCR.get(campo, ""), unidad,
            str(ejemplo.get(campo, "")), muestra,
        ])
    # cifras resumidas
    for k, c in (d.get("cifras") or {}).items():
        base = k.replace("_ultimo_anio", "").replace("_ultimo_mes", "")
        muestra = "Sí" if k in MOSTRADOS.get(tema, set()) or base in MOSTRADOS.get(tema, set()) else "No"
        filas_d.append([
            f"{tema} · cifras", k, f"Cifra destacada: {DESCR.get(base, base)}",
            c.get("unidad", ""), str(c.get("valor", "")), muestra,
        ])

hoja(wb, "Diccionario",
     ["Archivo · sección", "Campo", "Qué es", "Unidad", "Ejemplo real", "¿Lo muestra el sistema?"],
     filas_d,
     [22, 24, 62, 26, 18, 18])

# ===================== 4. BITÁCORA IA =====================
bitacora = [
    ["Rastreo", "Claude", "Elegir una ciudad con datos abiertos suficientes",
     "Propuso Cali por su portal propio y su escala por comunas", "Confirmar con el profesor que ningún otro grupo tomó Cali (pendiente humano)"],
    ["Ingesta", "Claude", "Esqueleto del repositorio y scripts F01/F02",
     "Estructura de carpetas, comun.py, scripts, todo.py y verificar.py", "El zip traía carpeta anidada; propuso el MDM sin avisar que la serie termina en 2020"],
    ["Ingesta", "Claude", "Fuente y script de población (F03)",
     "Script contra la API CKAN del portal de Cali", "Codificación rota (GBK/UTF-8) corregida; se añadió control urbana+rural=total"],
    ["Territorio", "Claude", "Límites de las comunas (F04)",
     "Script WFS que pregunta sus capas al servidor", "La capa documentada ya no existía; se cambió a preguntar GetCapabilities"],
    ["Contrato / lago", "Claude", "Dar forma de contrato al lago (valor, unidad, vigencia, fuente)",
     "comun.py reescribe el lago con el contrato; verificar.py lo exige", "La densidad quedó con unidad equivocada (km²) en comun.py y sin regenerar el lago"],
    ["Corrección y cierre", "Kiro", "Regenerar el lago, corregir la densidad y cerrar la entrega",
     "Unidad de densidad corregida a habitantes por hectárea (44,56); lago regenerado y verificado (88 comprobaciones, 0 fallas); dos corridas reproducibles",
     "pull_comunas.py elegía la capa de solo límites (sin árboles) ahora que responde: se corrigió para exigir el censo arbóreo. F03 respondió 403: se conservó el dato real sin cambiar la fecha"],
    ["Visualización", "Kiro", "Segunda herramienta sobre los mismos datos",
     "Exploración Leaflet (explorar/leaflet_comunas.html): mismas 22 comunas, color por no_arboles, consulta por comuna; verificada sin navegador con Node sobre el GeoJSON real",
     "Render visual no confirmado aquí (sin navegador en el entorno); la lógica de datos sí se probó"],
]
hoja(wb, "Bitácora IA",
     ["Tramo", "Herramienta", "Qué le encargamos", "Qué entregó", "Qué le corregimos / limitación"],
     bitacora,
     [20, 14, 34, 54, 54])

# ===================== 5. RESUMEN =====================
def cifra(tema, clave):
    c = lago[tema]["cifras"][clave]
    return c["valor"], c.get("unidad", ""), c.get("vigencia", ""), c.get("fuente", "")

resumen = []
for tema, clave, etq in [
    ("poblacion", "poblacion_ultimo_anio", "Población total de Cali"),
    ("poblacion", "poblacion_urbana_ultimo_anio", "Población urbana (comunas)"),
    ("poblacion", "poblacion_rural_ultimo_anio", "Población rural (corregimientos)"),
    ("poblacion", "densidad_ultimo_anio", "Densidad bruta"),
    ("desempeno", "mdm_ultimo_anio", "Medición de Desempeño Municipal (MDM)"),
    ("escucha", "vistas_ultimo_mes", "Vistas del artículo de Cali en Wikipedia (último mes)"),
    ("territorio", "numero_comunas", "Comunas en el mapa"),
]:
    v, u, vig, fid = cifra(tema, clave)
    resumen.append([etq, v, u, vig, fid])

# árboles totales del geojson (dato derivado real)
tot = sum((ft["properties"].get("no_arboles") or 0) for ft in geo["features"])
sanos = sum((ft["properties"].get("arbol_sano") or 0) for ft in geo["features"])
resumen.append(["Árboles censados en total (suma de no_arboles)", tot, "árboles", "capa vigente IDESC", "F04"])
resumen.append(["% de árboles sanos en el total",
                round(sanos / tot * 100, 1) if tot else "sin dato", "%", "capa vigente IDESC", "F04"])

hoja(wb, "Resumen",
     ["Indicador", "Valor", "Unidad", "Vigencia", "Fuente"],
     resumen,
     [48, 16, 26, 20, 10])

SALIDA.parent.mkdir(parents=True, exist_ok=True)
wb.save(SALIDA)
print(f"Excel generado: {SALIDA.relative_to(RAIZ)}  ({SALIDA.stat().st_size} bytes)")
