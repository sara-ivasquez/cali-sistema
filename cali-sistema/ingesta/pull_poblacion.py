"""F03 · Población y densidad de Cali 1987-2020 (datos.cali.gov.co, API CKAN)."""
import sys
from comun import bajar_json, guardar_crudo, guardar_lago

RECURSO = "fb8150d6-2af0-4d75-b741-33aaf871b19c"
URL = f"https://datos.cali.gov.co/api/3/action/datastore_search?resource_id={RECURSO}&limit=100"


def arreglar(texto):
    """El portal guardó el CSV en UTF-8 pero lo leyó como GBK: 'Poblaci贸n' -> 'Población'."""
    try:
        return texto.encode("gbk").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return texto


def numero(v):
    """Convierte '2.408.654', '2408654' o 2408654.0 en número."""
    if isinstance(v, (int, float)):
        return v
    s = str(v).strip().replace(" ", "")
    try:
        return float(s)
    except ValueError:
        return float(s.replace(".", "").replace(",", "."))


datos = bajar_json(URL)
guardar_crudo("poblacion", datos)
filas = datos["result"]["records"]

col_desc = next(k for k in filas[0] if k != "_id" and not k.isdigit())
print(f"Columna de descripción: {col_desc!r} -> corregida: {arreglar(col_desc)!r}")
for f in filas:
    f["_desc"] = arreglar(str(f[col_desc])).strip()


def fila_despues_de(i):
    """La fila 'Densidad bruta' que sigue a la fila i (cada bloque trae su propia densidad)."""
    for f in filas[i + 1:]:
        if f["_desc"].lower().startswith("densidad"):
            return f
        if f["_desc"].lower().startswith("población"):
            return None
    return None


def buscar(inicio):
    for i, f in enumerate(filas):
        if f["_desc"].lower().startswith(inicio):
            return i, f
    return None, None


i_tot, total = buscar("población total")
i_com, comunas = buscar("población comunas")
i_cor, correg = buscar("población corregimientos")
if total is None:
    sys.exit("✗ No se encontró la fila 'Población total'. Filas: " + ", ".join(f["_desc"] for f in filas))
densidad = fila_despues_de(i_tot)

registros = []
for a in sorted(k for k in total if k.isdigit()):
    r = {"anio": int(a), "poblacion": int(round(numero(total[a])))}
    if comunas is not None and comunas.get(a) not in (None, ""):
        r["poblacion_urbana"] = int(round(numero(comunas[a])))
    if correg is not None and correg.get(a) not in (None, ""):
        r["poblacion_rural"] = int(round(numero(correg[a])))
    if densidad is not None and densidad.get(a) not in (None, ""):
        r["densidad"] = round(numero(densidad[a]), 2)
    registros.append(r)

ultimo = registros[-1]
cifras = {"poblacion_ultimo_anio": ultimo["poblacion"]}
for campo in ("poblacion_urbana", "poblacion_rural", "densidad"):
    if campo in ultimo:
        cifras[f"{campo}_ultimo_anio"] = ultimo[campo]

# Control de coherencia: urbana + rural debe dar el total
if "poblacion_urbana" in ultimo and "poblacion_rural" in ultimo:
    suma = ultimo["poblacion_urbana"] + ultimo["poblacion_rural"]
    print(f"Control: urbana + rural = {suma} · total = {ultimo['poblacion']} · diferencia = {suma - ultimo['poblacion']}")

guardar_lago("poblacion", "F03", URL, vigencia=str(ultimo["anio"]), registros=registros, cifras=cifras)
print(f"Cali población: {len(registros)} años, último {ultimo['anio']} con {ultimo['poblacion']} habitantes")