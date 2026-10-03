"""F02 · Medición de Desempeño Municipal del DNP para Cali (DIVIPOLA 76001)."""
from urllib.parse import quote
from comun import bajar_json, guardar_crudo, guardar_lago

CODIGO = "76001"
consulta = ("$select=anio,dato&$where=" + quote(f"codigo_entidad='{CODIGO}' AND indicador='MDM'")
            + "&$order=anio")
URL = "https://www.datos.gov.co/resource/nkjx-rsq7.json?" + consulta

datos = bajar_json(URL)
guardar_crudo("desempeno", datos)

# El campo 'dato' llega como texto: aquí se convierte a número
registros = [{"anio": int(d["anio"]), "mdm": round(float(d["dato"]), 2)} for d in datos]
ultimo = registros[-1]
guardar_lago(
    "desempeno", "F02", URL, vigencia=str(ultimo["anio"]), registros=registros,
    cifras={"mdm_ultimo_anio": ultimo["mdm"]},
)
print(f"Cali MDM: {len(registros)} años, último {ultimo['anio']} con {ultimo['mdm']}")
