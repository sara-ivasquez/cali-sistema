# Contrato de datos del lago

El contrato es la promesa que el sistema le hace a quien pregunta: **toda cifra llega con valor, unidad, vigencia y fuente**. Cada archivo de `lago/` tiene esta forma, y `verificacion/verificar.py` no deja publicar si un archivo no la cumple.

```json
{
 "tema": "poblacion",
 "probado": "2026-10-05",
 "fuentes": [
  { "id": "F03", "nombre": "Estimaciones y proyecciones de población y densidad. Cali, 1987-2020",
    "url": "https://datos.cali.gov.co/api/3/action/datastore_search?resource_id=…",
    "estado": "Integrada al lago", "licencia": "CC BY-SA (sin versión declarada)" }
 ],
 "cifras": {
  "poblacion_ultimo_anio": { "valor": 2496442, "unidad": "habitantes", "vigencia": "2020", "fuente": "F03" }
 },
 "series": {
  "poblacion": { "unidad": "habitantes", "fuente": "F03", "puntos": [[1987, 1523000], [2020, 2496442]] }
 },
 "registros": [ { "anio": 2020, "poblacion": 2496442, "poblacion_urbana": 2456432, "poblacion_rural": 40010, "densidad": 4426.31 } ]
}
```

| Campo | Qué es | Regla |
|---|---|---|
| `tema` | Nombre del tema | Igual al nombre del archivo (`poblacion` → `lago/poblacion.json`) |
| `probado` | Día en que la fuente respondió de verdad | `AAAA-MM-DD`, sin hora |
| `fuentes` | Fuentes del archivo, copiadas del catálogo | Cada una con `id`, `url` y `licencia`; el `id` existe en `catalogo/fuentes.json` y está «Integrada al lago» |
| `cifras` | Las cifras que muestra el sistema | Cada una con `valor` numérico, `unidad`, `vigencia` y `fuente` (un `id` de `fuentes`); dentro de su rango con sentido |
| `series` | Series en el tiempo | `unidad`, `fuente` y `puntos` como pares `[eje, valor]` con valor numérico |
| `registros` | Extensión nuestra: la tabla limpia completa | La usan la página y las exploraciones con DuckDB |

## Reglas

1. **Ninguna cifra sin fuente, URL y vigencia.** La fuente se copia del catálogo; no se escribe a mano en cada script.
2. **Las fechas de prueba van por día**, nunca con hora: dicen cuándo se comprobó, no cuándo corrió el script.
3. **Los crudos van a `lago/raw/`**, que está en `.gitignore` y nunca se publica.
4. **Los números se normalizan en el script**: separadores de miles, coma decimal y texto se convierten antes de guardar. Nunca se suma texto.
5. **Las geometrías van en GeoJSON con coordenadas WGS84** (`territorio/comunas.geojson`), con su fuente y fecha de prueba como miembros de la colección.
6. **Ningún dato personal**: ningún campo con nombre de dato personal (cédula, teléfono, correo…) y ningún texto con un correo o un celular.
7. **La unidad de cada cifra se define una sola vez**, en `UNIDADES` dentro de `ingesta/comun.py`. Una cifra sin unidad no entra al lago.

## Puerta de salida

Borrar el lago y reconstruirlo. Si después Git muestra cambios que nadie esperaba (más allá de las fechas de prueba y las cifras que cambian solas, como las vistas del último mes), la ingesta no es reproducible.

```
Remove-Item lago\*.json
python3 ingesta/todo.py
python3 verificacion/verificar.py
git diff --stat -- lago/
```