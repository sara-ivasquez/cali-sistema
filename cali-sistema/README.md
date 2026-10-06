# Cali · sistema de información



## Cómo se reconstruye
```
python3 ingesta/todo.py           # baja las fuentes y reescribe lago/*.json
python3 verificacion/verificar.py # si una comprobación falla, no se publica
```
Solo usa la biblioteca estándar de Python: no hay que instalar nada ni usar llaves.
Última corrida: 2026-10-03 · 23 comprobaciones, 0 fallas.

## Cómo se conecta la vista con el lago
La página no tiene ninguna cifra escrita a mano: lee en tiempo de ejecución los JSON del lago y el catálogo desde este repositorio (`lago/*.json` y `catalogo/fuentes.json`). Cada archivo del lago trae pegada su procedencia: `fuente` (ID del catálogo), `url`, `vigencia` y `probado`.

## Para quién y qué pregunta
- Usuario: un concejal de Santiago de Cali.
- Preguntas:
  1. ¿Cuánta gente vive en Cali y en cada comuna? <pendiente: fuente de población>
  2. ¿Qué tan bien gestiona el municipio sus recursos? (F02 · MDM del DNP)
  3. ¿Cómo está la calidad del aire y en qué zonas es peor? <pendiente: fuente de aire>
  4. ¿Cuánto interés despierta Cali afuera y cómo cambia en el año? (F01 · vistas en Wikipedia)
- Escala y comparación: la ciudad contra sí misma en el tiempo (MDM 2016–2020, vistas mes a mes) y, dentro de la ciudad, por comunas <pendiente: límites de comunas en territorio/>.
- Lo que decidimos no mostrar, y por qué: <pendiente de decidir en grupo>

## La réplica
- Qué replicamos tal cual del ejemplo: la anatomía de carpetas (`catalogo/`, `ingesta/`, `lago/` con `raw/` fuera del repositorio, `territorio/`, `verificacion/`, `web/`), la ingesta en Python con biblioteca estándar, el lago en JSON y un script propio de verificación que bloquea la publicación con un solo fallo.
- Qué tuvimos que cambiar para nuestra ciudad: el artículo de Wikipedia (`Cali`) y el código DIVIPOLA (`76001` en lugar de `05001`). Además, siguiendo la advertencia sobre el catálogo de Lima, normalizamos entidad, licencia y estado con listas cerradas (`catalogo/listas.json`) desde la primera fuente, y `verificar.py` rechaza cualquier valor fuera de esas listas.
- Fuentes catalogadas · integradas · caídas · descartadas: 2 · 2 · 0 · 0 (ver `catalogo/fuentes.json`).
- Huecos: el MDM publicado en datos.gov.co llega solo hasta 2020; la ficha declara frecuencia anual, pero los datos no se actualizan desde el 2022-02-21. <pendiente: confirmar si el Portal Territorial del DNP tiene años posteriores>

## ¿Se puede usar?
| Fuente | Licencia | Personas | Estado | Condición |
|---|---|---|---|---|
| F01 · Vistas del artículo «Cali» en Wikipedia | CC0 | No | Integrada | Ninguna |
| F02 · Medición de Desempeño Municipal (DNP) | CC BY-SA 4.0 | No | Integrada | Citar al DNP; lo que se derive se publica con la misma licencia. Serie solo hasta 2020 |

## Bitácora de exploración
| Tramo | Herramienta | Qué pidió para empezar | Licencia | Dónde quedan los datos | ¿Se rehace con un comando? | Estado del proyecto | Qué resolvió | Qué no pudo | ¿Quedó? ¿Por qué? |
|---|---|---|---|---|---|---|---|---|---|
| Ingesta | Python estándar (urllib) | Nada | PSF (OSI) | `lago/*.json` en el repositorio | Sí: `python3 ingesta/todo.py` | Activo (Python 3.14) | Bajó F01 (21 meses) y F02 (5 años) y convirtió `dato` de texto a número | No consulta sin bajar; no detecta solo si el artículo es una desambiguación | Sí: cero dependencias, igual que la réplica |
| Ingesta | DuckDB (`read_json_auto` remoto) | `pip install duckdb` <y lo que haya pedido> | MIT (OSI) | En memoria, nada en disco | Sí, corriendo el script | <versión y fecha> | <pendiente> | No guarda la procedencia | <pendiente> |
| Verificación | `verificar.py` propio | Nada | — | — | Sí: `python3 verificacion/verificar.py` | Propio | 23 comprobaciones: listas cerradas del catálogo, procedencia completa, fuente existente y cifras válidas | No compara contra la corrida anterior | <pendiente: segunda herramienta> |
| Vistas | <v0> | <cuenta…> | | | | | | | |
| Vistas | <HTML plano u otra> | | | | | | | | |

## Protección
- Nivel: <propuesta: abierto. Todas las fuentes son públicas, agregadas y sin datos de personas>
- Qué protegemos, y de quién: los crudos (`lago/raw/`) y cualquier secreto (`.env`) no llegan al repositorio (ver `.gitignore`).
- Pruebas de terminal o de ventana privada: <pendiente>
- Revisión de secretos en el historial: <pendiente: `git log -p | Select-String -Pattern "key|token|password|secret"` y resultado>

## Herramienta elegida para las vistas
- Qué necesitábamos mostrar: <compañero de vistas>
- Qué teníamos que proteger: <compañero de vistas>
- Por qué esta herramienta cumple las dos cosas, y cuál descartamos por poco: <compañero de vistas>

## Nuestra posición
- Gestión y gobierno de datos: un metadato no es una garantía. La ficha del MDM en datos.gov.co dice «frecuencia anual» y se editó en septiembre de 2026, pero los datos no cambian desde febrero de 2022. Por eso nuestro sistema muestra la vigencia (2020) en la misma línea de la cifra, y no la fecha de actualización del portal. <ampliar>
- Ciberseguridad: <pendiente>

## Bitácora de IA
| Tramo | Herramienta | Qué le encargamos | Qué entregó | Qué le corregimos |
|---|---|---|---|---|
| Rastreo | Claude | Elegir una ciudad con datos abiertos suficientes | Cali, por su portal propio (datos.cali.gov.co) y su escala por comunas | <confirmar con el profesor que nadie más la tenía> |
| Ingesta | Claude | Esqueleto del repositorio y scripts de F01 y F02 | Estructura de carpetas, `comun.py`, dos scripts, `todo.py` y `verificar.py` | El zip traía una carpeta anidada y el primer comando falló («No such file or directory»). Propuso el MDM para la gestión actual sin advertir que la serie termina en 2020; lo descubrimos al correrlo |
| Catálogo | Claude | Revisar si el artículo de Wikipedia era el correcto | Indicó cómo comprobar redirección y desambiguación | Lo comprobamos a mano: «Cali» es el artículo principal |

## Revisión cruzada
- Tres cifras auditadas por el grupo <X>: resultado y correcciones
- Ataque del grupo <Y>: qué intentó, qué consiguió, qué cambiamos
- Vueltas atrás en la ruta: de qué tramo a cuál, y por qué