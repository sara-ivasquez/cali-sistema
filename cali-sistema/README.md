# Cali · sistema de información

Grupo: Sara Isabel Vásquez (datos: catálogo, ingesta, lago y verificación) · Alejandro Rendón (vistas) · Enlace: <url de la página> · Revisado: 2026-10-05

## Cómo se reconstruye
```
python3 ingesta/todo.py            # baja las 4 fuentes integradas y reescribe lago/*.json y territorio/comunas.geojson
python3 verificacion/verificar.py  # 68 comprobaciones; con una sola falla no se publica
```
La ingesta usa solo la biblioteca estándar de Python: no hay que instalar nada ni usar llaves.
Última corrida completa: 2026-10-05 · 4 de 4 scripts terminaron bien · 68 comprobaciones, 0 fallas.

Exploraciones (requieren `python3 -m pip install duckdb`):
```
python3 explorar/duckdb_remoto.py  # F02 consultada con DuckDB sin bajarla
python3 explorar/duckdb_lago.py    # cruce de población (F03) y MDM (F02) con SQL sobre el lago
```

## Cómo se conecta la vista con el lago
La página no tiene ninguna cifra escrita a mano: lee en tiempo de ejecución `lago/*.json`, `territorio/comunas.geojson` y `catalogo/fuentes.json` desde este repositorio. Cada archivo del lago trae pegada su procedencia: `fuente` (ID del catálogo), `url`, `vigencia` y `probado`.

## Para quién y qué pregunta
- Usuario: un concejal de Santiago de Cali.
- Preguntas:
  1. ¿Cuánta gente vive en Cali y cuánta en la zona urbana y en la rural? (F03)
  2. ¿Qué tan bien gestiona el municipio sus recursos? (F02 · MDM del DNP)
  3. <confirmar: ¿Cuántos árboles hay en cada comuna y en qué estado están? (F04)>
  4. ¿Cuánto interés despierta Cali afuera y cómo cambia en el año? (F01 · vistas en Wikipedia)
- Escala y comparación: la ciudad contra sí misma en el tiempo (población 1987–2020, MDM 2016–2020, vistas mes a mes); urbana contra rural (F03); y las 22 comunas entre sí (F04).
- Lo que decidimos no mostrar, y por qué: <decisión del grupo. Candidatos: los campos del censo arbóreo cuyo significado no confirmamos en la ficha de la IDESC; población por comuna, que no encontramos abierta>
- Huecos que el sistema dice en pantalla: MDM posterior a 2020, población posterior a 2020, población por comuna.

## La réplica
- Qué replicamos tal cual del ejemplo: la anatomía de carpetas (`catalogo/`, `ingesta/`, `lago/` con `raw/` fuera del repositorio, `territorio/`, `verificacion/`, `web/`), la ingesta en Python con biblioteca estándar, el lago en JSON, los límites en GeoJSON y un script propio de verificación que bloquea la publicación con un solo fallo.
- Qué tuvimos que cambiar para nuestra ciudad: el artículo de Wikipedia (`Cali`) y el código DIVIPOLA (`76001` en lugar de `05001`). Siguiendo la advertencia sobre el catálogo de Lima, normalizamos entidad, licencia y estado con listas cerradas (`catalogo/listas.json`) desde la primera fuente, y `verificar.py` rechaza cualquier valor fuera de ellas. Además, `verificar.py` exige que todo lo que está en el lago figure como «Integrada» en el catálogo con su fecha de prueba, que cada cifra esté en un rango con sentido y que todos los puntos del mapa caigan dentro de Cali.
- Fuentes catalogadas · integradas · caídas · descartadas: 5 · 4 · 0 · 0 (F05 sigue como candidata; ver `catalogo/fuentes.json`).
- Huecos: lo que buscamos y no existe abierto para esta ciudad:
  - MDM posterior a 2020: la ficha en datos.gov.co declara frecuencia anual, pero los datos no se actualizan desde el 2022-02-21.
  - Población posterior a 2020 en formato abierto con API: el portal de Cali la tiene solo hasta 2020 (sin actualizar desde 2018-10-29); la proyección vigente del DANE (F05) existe, pero solo en Excel.
  - Límites oficiales de comunas: la capa de Planeación (`dapm:pdt_dpa_comunas`) está publicada en el WFS de la IDESC, pero responde «permission denied». Usamos los límites de la capa del censo arbóreo por comuna.

## ¿Se puede usar?
| Fuente | Licencia | Personas | Estado | Condición |
|---|---|---|---|---|
| F01 · Vistas del artículo «Cali» en Wikipedia | CC0 | No | Integrada | Ninguna |
| F02 · Medición de Desempeño Municipal (DNP) | CC BY-SA 4.0 | No | Integrada | Citar al DNP; lo que se derive se publica con la misma licencia. Serie solo hasta 2020 |
| F03 · Población y densidad de Cali (DAPM) | CC BY-SA (sin versión declarada) | No | Integrada | Citar a la Alcaldía; misma licencia. Serie hasta 2020 |
| F04 · Comunas con censo arbóreo (IDESC) | CC BY-SA (sin versión declarada) | No | Integrada | Citar a la Alcaldía; misma licencia. <pendiente: confirmar la licencia de esta capa en la IDESC> |
| F05 · Proyecciones de población DANE 2018–2042 | por verificar | No | Candidata | Pendiente: solo en Excel |

## Bitácora de exploración
| Tramo | Herramienta | Qué pidió para empezar | Licencia | Dónde quedan los datos | ¿Se rehace con un comando? | Estado del proyecto | Qué resolvió | Qué no pudo | ¿Quedó? ¿Por qué? |
|---|---|---|---|---|---|---|---|---|---|
| Ingesta | Python estándar (urllib) | Nada | PSF (OSI) | `lago/*.json` y `territorio/comunas.geojson`, en el repositorio | Sí: `python3 ingesta/todo.py` | Activo (Python 3.14) | Bajó las 4 fuentes; convirtió texto a número; corrigió la codificación de F03; descubrió la capa de comunas preguntándole al servidor | No consulta sin bajar; cruzar fuentes exige escribir código | Sí: cero dependencias y deja la procedencia pegada a cada cifra, que es lo que lee la web |
| Ingesta | DuckDB 1.5.6 (`read_json_auto` remoto) | `pip install duckdb` | MIT (OSI) | En memoria, nada en disco | Sí: `python3 explorar/duckdb_remoto.py` | Activo (1.5.6) | Consultó F02 sin bajarla y dio exactamente los mismos 5 valores que el script base (77.2 · 63.82 · 81.38 · 83.74 · 86.45) | Infirió `anio` como texto (varchar), no como número; no guarda procedencia ni fecha de prueba | No para la ingesta: el resultado no queda en el lago. Sí como control: confirmó los valores del script base |
| Lago | Archivos JSON | Nada | — | `lago/*.json` en el repositorio | Sí: `python3 ingesta/todo.py` | — | Cada cifra con su fuente, vigencia y fecha; la web los lee directo desde GitHub | Cruzar dos fuentes exige código | Sí: es lo que puede leer la página sin servidor |
| Lago | DuckDB 1.5.6 sobre los mismos JSON | `pip install duckdb` | MIT (OSI) | En memoria; lee los JSON del lago | Sí: `python3 explorar/duckdb_lago.py` | Activo (1.5.6) | Cruzó población (F03) y MDM (F02) por año con una consulta SQL: 5 años en común (2016–2020) | La página no puede leerlo directamente; necesita instalación | No como lago, sí como herramienta de análisis sobre el lago |
| Verificación | `verificar.py` propio | Nada | — | — | Sí: `python3 verificacion/verificar.py` | Propio | 68 comprobaciones: listas cerradas, procedencia completa, coherencia lago–catálogo, rangos de cada cifra y coordenadas dentro de Cali | No compara contra la corrida anterior | Sí <pendiente: segunda herramienta> |
| Vistas | <Alejandro> | | | | | | | | |
| Vistas | <Alejandro> | | | | | | | | |

## Protección
- Nivel: <confirmar: abierto. Todas las fuentes son públicas, agregadas por ciudad o comuna y sin datos de personas>
- Qué protegemos, y de quién: los crudos (`lago/raw/`) y cualquier secreto (`.env`) no llegan al repositorio (ver `.gitignore`). El sistema no usa llaves: todas las fuentes son APIs o servicios abiertos sin autenticación.
- Pruebas de terminal o de ventana privada: <pendiente: abrir la página en ventana privada y desde un teléfono>
- Revisión de secretos en el historial (2026-10-05):
  - `git log -p | Select-String -Pattern "api_key|apikey|access_token|password\s*=|secret\s*=|PRIVATE KEY"` → sin resultados.
  - `git ls-files lago/raw` → solo `lago/raw/.gitkeep`: los crudos no llegan al repositorio.
  - `git log --all --oneline -- .env` → sin resultados: nunca se subió un archivo de secretos.

## Herramienta elegida para las vistas
- Qué necesitábamos mostrar: <Alejandro>
- Qué teníamos que proteger: <Alejandro>
- Por qué esta herramienta cumple las dos cosas, y cuál descartamos por poco: <Alejandro>

## Nuestra posición
- Gestión y gobierno de datos: un metadato no es una garantía. La ficha del MDM en datos.gov.co dice «frecuencia anual» y se editó en septiembre de 2026, pero los datos no cambian desde febrero de 2022; la población del portal de Cali no se toca desde 2018; y la capa de comunas documentada en el portal en 2020 ya no existe en el servidor. Nuestra respuesta: el catálogo registra la fecha en que cada fuente respondió de verdad (`probado`), el sistema muestra la vigencia del dato en la misma línea de la cifra (2020) y no la fecha de actualización del portal, y `verificar.py` impide publicar una cifra cuya fuente no esté integrada y fechada en el catálogo.
- Ciberseguridad: un servicio público mal configurado también es un riesgo. Al pedir la capa oficial de comunas, el servidor de la IDESC no solo negó el acceso: respondió con el error interno de Java y el nombre de la tabla de su base de datos («permission denied for table pdt_dpa_comunas»), información que a un atacante le sirve para conocer la infraestructura. Nuestra respuesta: nuestro sistema no tiene servidor propio ni base de datos que exponer, no usa llaves, deja los crudos fuera del repositorio y revisamos el historial completo de Git en busca de secretos (ver Protección). <ampliar con la decisión de nivel de protección>

## Bitácora de IA
| Tramo | Herramienta | Qué le encargamos | Qué entregó | Qué le corregimos |
|---|---|---|---|---|
| Rastreo | Claude | Elegir una ciudad con datos abiertos suficientes | Cali, por su portal propio (datos.cali.gov.co) y su escala por comunas | <confirmar con el profesor que nadie más la tenía> |
| Ingesta | Claude | Esqueleto del repositorio y scripts de F01 y F02 | Estructura de carpetas, `comun.py`, dos scripts, `todo.py` y `verificar.py` | El zip traía una carpeta anidada y el primer comando falló («No such file or directory»). Propuso el MDM para la gestión actual sin advertir que la serie termina en 2020; lo descubrimos al correrlo |
| Catálogo | Claude | Revisar si el artículo de Wikipedia era el correcto | Indicó cómo comprobar redirección y desambiguación | Lo comprobamos a mano: «Cali» es el artículo principal |
| Ingesta | Claude | Fuente y script de población (F03) | Script que busca la fila de población en la API CKAN del portal de Cali | La primera versión mostraba el texto con la codificación rota («Poblaci贸n»). Se corrigió: el portal guardó el archivo en UTF-8 y lo leyó como GBK. También se agregó población urbana y rural con un control de que sumen el total (diferencia 0) |
| Territorio | Claude | Límites de las comunas (F04) | Script contra el WFS de la IDESC con la capa `idesc:mc_comunas`, tomada de una ficha de 2020 | La capa ya no existía y el primer script cortaba el mensaje de error a la mitad. Se cambió para que pregunte al servidor sus capas (357, 4 con «comuna») y valide que traiga polígonos y unos 22 elementos. La oficial (`dapm:pdt_dpa_comunas`) respondió «permission denied»; quedó la del censo arbóreo |
| Exploración | Claude | Scripts de DuckDB para comparar herramientas | `duckdb_remoto.py` y `duckdb_lago.py` | Corrieron bien; DuckDB infirió el año como texto, a diferencia del script base |

## Revisión cruzada
- Tres cifras auditadas por el grupo <X>: resultado y correcciones
- Ataque del grupo <Y>: qué intentó, qué consiguió, qué cambiamos
- Vueltas atrás en la ruta:
  - De Ingesta a Catálogo: al correr F02 descubrimos que la serie termina en 2020 y lo registramos como hueco.
  - De Ingesta a Catálogo y de vuelta: la capa de comunas documentada no existía; el catálogo cambió de «Candidata» a «No responde» y después a «Integrada» con otra capa.
  - <confirmar: de Ingesta a Para quién, si la pregunta 3 cambia de calidad del aire a árboles por comuna>