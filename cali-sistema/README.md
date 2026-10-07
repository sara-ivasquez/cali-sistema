# Cali · sistema de información

Grupo: Sara Isabel Vásquez · Alejandro Rendón · Enlace: https://sara-ivasquez.github.io/cali-sistema/cali-sistema/web/ · Revisado: 2026-10-06

## Cómo se reconstruye
```
python3 ingesta/todo.py            # baja las 4 fuentes integradas y reescribe lago/*.json y territorio/comunas.geojson
python3 verificacion/verificar.py  # revisa catálogo, contrato, datos personales y territorio; con una sola falla no se publica
```
La ingesta usa solo la biblioteca estándar de Python: no hay que instalar nada ni usar llaves.
Última corrida completa: 2026-10-06 · 4 de 4 scripts terminaron bien · 88 comprobaciones, 0 fallas.

Puerta de salida (reproducibilidad): borrar el lago, reconstruirlo y comparar con Git.
```
Remove-Item lago\*.json
python3 ingesta/todo.py
python3 verificacion/verificar.py
git diff --stat -- lago/
```
Lo esperado es que solo cambien las fechas de prueba y las cifras que cambian solas (las vistas del último mes).
- Primera corrida (2026-10-06): el lago se reconstruyó y la verificación pasó (88 comprobaciones, 0 fallas), pero `git diff` mostró los 4 archivos cambiados (1.683 líneas agregadas y 929 borradas). No era falta de reproducibilidad: Git comparaba contra el lago anterior, que todavía no tenía la forma del contrato. Hubo que subir primero el lago nuevo y repetir la prueba.
- Segunda corrida, con el contrato ya subido: <pegar resultado de `git diff --stat -- lago/`>

Exploraciones (requieren `python3 -m pip install duckdb`):
```
python3 explorar/duckdb_remoto.py  # F02 consultada con DuckDB sin bajarla
python3 explorar/duckdb_lago.py    # cruce de población (F03) y MDM (F02) con SQL sobre el lago
```

## El contrato
Toda cifra llega con valor, unidad, vigencia y fuente. La forma de cada archivo del lago, sus campos y sus reglas están en [`contrato/CONTRATO.md`](contrato/CONTRATO.md). La fuente de cada archivo se copia del catálogo (no se escribe a mano en cada script) y la unidad de cada cifra se define una sola vez, en `UNIDADES` dentro de `ingesta/comun.py`. `verificar.py` revisa el contrato archivo por archivo.

El contrato lo escribimos después del primer lago, no antes como pide el método: es una vuelta atrás que dejamos anotada (ver Revisión cruzada).

## Cómo se conecta la vista con el lago
La página no tiene ninguna cifra escrita a mano: lee en tiempo de ejecución `lago/*.json`, `territorio/comunas.geojson` y `catalogo/fuentes.json`. Cada cifra que muestra se puede tocar y abre su fuente, entidad, licencia, vigencia y fecha de prueba; las cifras derivadas muestran además su fórmula.

## Para quién y qué pregunta
- Usuario: un concejal de Santiago de Cali.
- Preguntas:
  1. ¿Cuánta gente vive en Cali y cuánta en la zona urbana y en la rural? (F03)
  2. ¿Qué tan bien gestiona el municipio sus recursos? (F02 · MDM del DNP)
  3. ¿Cuántos árboles hay en cada comuna y en qué estado están? (F04). Reemplazó a la pregunta inicial sobre calidad del aire, para la que no integramos fuente.
  4. ¿Cuánto interés despierta Cali afuera y cómo cambia en el año? (F01 · vistas en Wikipedia)
- Escala y comparación: la ciudad contra sí misma en el tiempo (población 1987–2020, MDM 2016–2020, vistas mes a mes); urbana contra rural (F03); y las 22 comunas entre sí (F04).
- Lo que decidimos no mostrar, y por qué: los campos del censo arbóreo cuyo significado no está confirmado en la ficha de la IDESC (`cobarb_ha`, `arb_habita`, `arb_eep` y similares, y `area_m2`: al usarlo, la densidad daba entre 17.030 y 42.980 árboles por km², imposible para una ciudad; el área se calcula desde el polígono).
- Huecos que el sistema dice en pantalla: MDM posterior a 2020, población posterior a 2020, población por comuna, límites oficiales de comunas, calidad del aire.

## La réplica
- Qué replicamos tal cual del ejemplo: la anatomía de carpetas (`catalogo/`, `contrato/`, `ingesta/`, `lago/` con `raw/` fuera del repositorio, `territorio/`, `verificacion/`, `web/`), la ingesta en Python con biblioteca estándar, el lago en JSON con la forma del contrato, los límites en GeoJSON WGS84 y una verificación que bloquea la publicación con un solo fallo, incluida la búsqueda de correos y celulares.
- Qué tuvimos que cambiar para nuestra ciudad: el artículo de Wikipedia (`Cali`) y el código DIVIPOLA (`76001` en lugar de `05001`). Siguiendo la advertencia sobre el catálogo de Lima, normalizamos entidad, licencia y estado con listas cerradas (`catalogo/listas.json`) desde la primera fuente. Además, `verificar.py` exige que todo lo que está en el lago figure como «Integrada» en el catálogo, que cada cifra esté en un rango con sentido para Cali y que todos los puntos del mapa caigan dentro de la ciudad.
- Fuentes catalogadas · integradas · caídas · descartadas: 7 · 4 · 1 · 0, más 1 que ya no existe (F06) y 1 candidata (F05). Ver `catalogo/fuentes.json`.
- Huecos: lo que buscamos y no existe abierto para esta ciudad:
  - MDM posterior a 2020: la ficha en datos.gov.co declara frecuencia anual, pero los datos no se actualizan desde el 2022-02-21.
  - Población posterior a 2020 con API: el portal de Cali la tiene solo hasta 2020 (sin actualizar desde 2018-10-29); la proyección vigente del DANE (F05) existe, pero solo en Excel.
  - Límites oficiales de comunas: la capa de Planeación (F07) está publicada, pero responde «permission denied». Usamos los límites de la capa del censo arbóreo por comuna (F04).

## ¿Se puede usar?
| Fuente | Licencia | Personas | Estado | Condición |
|---|---|---|---|---|
| F01 · Vistas del artículo «Cali» en Wikipedia | CC0 | No | Integrada | Ninguna |
| F02 · Medición de Desempeño Municipal (DNP) | CC BY-SA 4.0 | No | Integrada | Citar al DNP; lo derivado se publica con la misma licencia. Serie solo hasta 2020 |
| F03 · Población y densidad de Cali (DAPM) | CC BY-SA (sin versión declarada) | No | Integrada | Citar a la Alcaldía; misma licencia. Serie hasta 2020 |
| F04 · Comunas con censo arbóreo (IDESC) | CC BY-SA (sin versión declarada) | No | Integrada | Citar a la Alcaldía; misma licencia. <confirmar la licencia de esta capa> |
| F05 · Proyecciones de población DANE 2018–2042 | por verificar | No | Candidata | Pendiente: solo en Excel |
| F06 · Capa `idesc:mc_comunas` | CC BY-SA (sin versión declarada) | No | No existe | La capa documentada en 2020 ya no está en el servidor |
| F07 · Capa oficial `dapm:pdt_dpa_comunas` | no declara | No | No responde | Publicada, pero el servidor niega el acceso |

## Bitácora de exploración
| Tramo | Herramienta | Qué pidió para empezar | Licencia | Dónde quedan los datos | ¿Se rehace con un comando? | Estado del proyecto | Qué resolvió | Qué no pudo | ¿Quedó? ¿Por qué? |
|---|---|---|---|---|---|---|---|---|---|
| Ingesta | Python estándar (urllib) | Nada | PSF (OSI) | `lago/*.json` y `territorio/comunas.geojson`, en el repositorio | Sí: `python3 ingesta/todo.py` | Activo (Python 3.14) | Bajó las 4 fuentes; convirtió texto a número; corrigió la codificación de F03; descubrió la capa de comunas preguntándole al servidor | No consulta sin bajar; cruzar fuentes exige escribir código | Sí: cero dependencias y escribe el lago con la forma del contrato |
| Ingesta | DuckDB 1.5.6 (`read_json_auto` remoto) | `pip install duckdb` | MIT (OSI) | En memoria, nada en disco | Sí: `python3 explorar/duckdb_remoto.py` | Activo (1.5.6) | Consultó F02 sin bajarla y dio exactamente los mismos 5 valores que el script base (77.2 · 63.82 · 81.38 · 83.74 · 86.45) | Infirió `anio` como texto (varchar), no como número; no guarda procedencia ni fecha de prueba | No para la ingesta: el resultado no queda en el lago. Sí como control: confirmó los valores del script base |
| Lago | Archivos JSON con la forma del contrato | Nada | — | `lago/*.json` en el repositorio | Sí: `python3 ingesta/todo.py` | — | Cada cifra con valor, unidad, vigencia y fuente; la página los lee directo | Cruzar dos fuentes exige código | Sí: es lo que puede leer la página sin servidor |
| Lago | DuckDB 1.5.6 sobre los mismos JSON | `pip install duckdb` | MIT (OSI) | En memoria; lee los JSON del lago | Sí: `python3 explorar/duckdb_lago.py` | Activo (1.5.6) | Cruzó población (F03) y MDM (F02) por año con una consulta SQL: 5 años en común (2016–2020) | La página no puede leerlo directamente; necesita instalación | No como lago, sí como herramienta de análisis sobre el lago |
| Verificación | `verificar.py` propio | Nada | — | — | Sí: `python3 verificacion/verificar.py` | Propio | Catálogo con listas cerradas; contrato de cada archivo; rangos de cada cifra; ningún campo ni texto con datos personales; coordenadas dentro de Cali. Probado rompiendo el lago a propósito: detectó una fecha con hora, una cifra sin fuente y un texto con correo y celular | No compara contra la corrida anterior | Sí <pendiente: segunda herramienta, por ejemplo Frictionless> |
| Vistas | Página HTML + MapLibre GL (hecha con Claude) | Nada: un archivo HTML; MapLibre y OpenStreetMap sin llave | MapLibre: BSD-3 (OSI); mapa base: ODbL | Lee el lago del repositorio; no guarda nada | Sí: se publica sola con cada `git push` | Activo | Las 7 secciones, trazabilidad a un clic en cada cifra, mapa de las 22 comunas, funciona en celular | El mapa depende de servicios externos (MapLibre por CDN y teselas de OpenStreetMap); sin servidor no podría tener compuerta | Sí <pendiente: segunda herramienta> |
| Publicación | GitHub Pages | Repositorio público | — | El repositorio | Sí: cada `git push` a `main` | Activo | Enlace público gratis, sin servidor | No puede ejecutar código de servidor: una compuerta de verdad sería imposible aquí | Sí: el sistema es abierto y no necesita compuerta <pendiente: segunda herramienta, por ejemplo Vercel> |

## Protección
- Nivel: abierto. Las cuatro fuentes integradas son públicas, con licencias que permiten reutilizar (CC0 y CC BY-SA), y todos los datos están agregados por ciudad o por comuna: ninguno apunta a una persona (columna «Personas» del catálogo, y `verificar.py` busca campos y textos con datos personales). Una clave sería teatro: en GitHub Pages no hay servidor, así que solo podría estar escrita en el JavaScript, donde cualquiera la lee.
- Qué protegemos, y de quién: los secretos del código y los crudos. No usamos llaves (todas las fuentes son abiertas y sin autenticación); `lago/raw/` y `.env` están en `.gitignore`.
- Pruebas de terminal (2026-10-06):
  - `curl.exe -s -o NUL -w "%{http_code}\n" https://sara-ivasquez.github.io/cali-sistema/cali-sistema/web/` → 200: la página abre.
  - `curl.exe -s -o NUL -w "%{http_code}\n" https://sara-ivasquez.github.io/cali-sistema/cali-sistema/lago/poblacion.json` → 200: los datos agregados son públicos a propósito.
  - `curl.exe -s -o NUL -w "%{http_code}\n" https://sara-ivasquez.github.io/cali-sistema/cali-sistema/lago/raw/poblacion.json` → 404: los crudos no están publicados.
  - `curl.exe -s https://sara-ivasquez.github.io/cali-sistema/cali-sistema/web/ | Select-String -Pattern "password|api_key|apikey|token|secret"` → sin resultados: la página no tiene claves.
  - Abierta en celular: carga y funciona. Ventana privada: <confirmar>.
- Revisión de secretos en el historial (2026-10-05):
  - `git log -p | Select-String -Pattern "api_key|apikey|access_token|password\s*=|secret\s*=|PRIVATE KEY"` → sin resultados.
  - `git ls-files lago/raw` → solo `lago/raw/.gitkeep`: los crudos no llegan al repositorio.
  - `git log --all --oneline -- .env` → sin resultados: nunca se subió un archivo de secretos.

## Herramienta elegida para las vistas
- Qué necesitábamos mostrar: cifras con su fuente a un clic, series en el tiempo y un mapa de las 22 comunas, que se viera bien en celular.
- Qué teníamos que proteger: nada sensible (nivel abierto); solo evitar cifras escritas a mano y datos que no estén en el lago.
- Por qué esta herramienta cumple las dos cosas, y cuál descartamos por poco: una página HTML estática en GitHub Pages muestra todo leyendo el lago, sin servidor ni cifras escritas a mano, y como el nivel es abierto no necesita compuerta. <pendiente: la segunda herramienta probada y por qué no quedó>

## Nuestra posición

### Datos · «Los datos también se mueren» (ciclo de vida)
Nuestro propio catálogo es la evidencia. De las siete fuentes que rastreamos, solo una se actualiza sola (F01, las vistas de Wikipedia). El MDM del DNP (F02) declara frecuencia anual, pero sus datos no cambian desde el 2022-02-21. La población del portal de Cali (F03) no se toca desde el 2018-10-29 y llega solo a 2020. La capa de comunas documentada en el portal en 2020 ya no existe en el servidor (F06), y la capa oficial está publicada, pero no deja leerse (F07). Ninguno de esos portales avisa que algo cambió: lo descubrimos porque cada fuente lleva una fecha de prueba.

- **¿Quién mantiene el sistema cuando termine el curso, o quién decide apagarlo?** Sara Isabel Vásquez responde por el lago y el catálogo. Al terminar el curso el sistema queda publicado tal como está y no se actualiza más; ella es quien decide apagarlo, desactivando GitHub Pages. Volver a ponerlo al día cuesta un comando (`python3 ingesta/todo.py`) más la verificación, porque las fuentes que dejen de responder hacen fallar la ingesta en vez de publicar datos viejos en silencio.
- **¿Qué debe decir la portada el día en que la prueba más reciente tenga más de un año?** Lo dice sola. La página calcula la fecha de prueba más reciente del lago y, si tiene más de un año, muestra antes de cualquier cifra: «Este sistema no se ha actualizado en más de un año… Úsalo como registro histórico, no para decidir hoy». Además, cada cifra lleva su vigencia en la misma línea (por ejemplo, «86,45 de 100 · 2020»), y la sección «Lo que el sistema no sabe» lista las series detenidas y las fuentes caídas.

### Seguridad · «Parecer protegido no es estar protegido» (apariencia)
Decidimos no parecer protegidos. El sistema es abierto: no pide clave, así que no da una sensación de seguridad que no tenga. Una clave en GitHub Pages solo podría estar en el JavaScript, que es exactamente la compuerta de mentira que cualquiera lee con «ver código».

- **¿Qué parte parece protegida sin estarlo, y cómo lo demostramos con una terminal?** Ninguna, y lo comprobamos (2026-10-06). La página responde 200 y los datos del lago también responden 200: son públicos a propósito, porque son agregados y abiertos. Los crudos responden 404, y no porque estén escondidos: nunca llegaron al repositorio (`git ls-files lago/raw` solo muestra `.gitkeep`). La página no contiene claves (`Select-String` sin resultados), y el historial de Git tampoco. Lo que no es dato personal no necesita control técnico; para asegurarnos de que no lo es, `verificar.py` rechaza cualquier campo con nombre de dato personal y cualquier texto con un correo o un celular.
- **¿Qué ve alguien que abre el enlace en una ventana privada?** Lo mismo que cualquier visitante, porque no hay sesión: <confirmar en ventana privada>. En celular abre y funciona.

## Bitácora de IA
| Tramo | Herramienta | Qué le encargamos | Qué entregó | Qué le corregimos |
|---|---|---|---|---|
| Rastreo | Claude | Elegir una ciudad con datos abiertos suficientes | Cali, por su portal propio (datos.cali.gov.co) y su escala por comunas | <confirmar con el profesor que nadie más la tenía> |
| Ingesta | Claude | Esqueleto del repositorio y scripts de F01 y F02 | Estructura de carpetas, `comun.py`, dos scripts, `todo.py` y `verificar.py` | El zip traía una carpeta anidada: el primer comando falló y el repositorio quedó con la carpeta doble (por eso la página está en `/cali-sistema/cali-sistema/web/`). Propuso el MDM para la gestión actual sin advertir que la serie termina en 2020 |
| Catálogo | Claude | Revisar si el artículo de Wikipedia era el correcto | Indicó cómo comprobar redirección y desambiguación | Lo comprobamos a mano: «Cali» es el artículo principal |
| Ingesta | Claude | Fuente y script de población (F03) | Script que busca la fila de población en la API CKAN del portal de Cali | La primera versión mostraba el texto con la codificación rota («Poblaci贸n»): el portal guardó el archivo en UTF-8 y lo leyó como GBK. Se agregó población urbana y rural con un control de que sumen el total |
| Territorio | Claude | Límites de las comunas (F04) | Script contra el WFS de la IDESC con la capa `idesc:mc_comunas`, tomada de una ficha de 2020 | La capa ya no existía (F06) y el primer script cortaba el mensaje de error. Se cambió para que pregunte al servidor sus capas y valide que traiga polígonos y unos 22 elementos. La oficial (F07) respondió «permission denied»; quedó la del censo arbóreo |
| Exploración | Claude | Scripts de DuckDB para comparar herramientas | `duckdb_remoto.py` y `duckdb_lago.py` | Corrieron bien; DuckDB infirió el año como texto, a diferencia del script base |
| Vistas | Claude | Página con las 7 secciones leyendo el lago | Un HTML que lee los JSON del repositorio, sin cifras escritas a mano | En la vista previa de Claude no cargaban los datos (bloquea conexiones externas); en GitHub la ruta daba 404 por la carpeta doble; calculó árboles por km² con el campo `area_m2` sin confirmar su significado y dio valores imposibles (17.030–42.980 por km²): se corrigió calculando el área desde el polígono |
| Contrato | Claude | Adaptar el lago al contrato del método | Lago con `tema`, `fuentes`, `cifras` con valor/unidad/vigencia/fuente y `series`; verificación del contrato y de datos personales; `contrato/CONTRATO.md` | Corrió sin fallas (88 comprobaciones). La puerta de salida mostró los 4 archivos cambiados porque Git comparaba contra el formato anterior: hubo que subir el lago nuevo y repetir la prueba |

## Revisión cruzada
- Tres cifras auditadas por el grupo <X>: resultado y correcciones
- Ataque del grupo <Y>: qué intentó, qué consiguió, qué cambiamos
- Vueltas atrás en la ruta:
  - De Ingesta a Catálogo: al correr F02 descubrimos que la serie termina en 2020 y lo registramos como hueco.
  - De Ingesta a Catálogo y de vuelta: la capa de comunas documentada no existía (F06) y la oficial no deja leerse (F07); F04 pasó de «Candidata» a «No responde» y después a «Integrada» con otra capa.
  - De Lago a Contrato: escribimos el contrato después del primer lago y tuvimos que reescribir el formato de todos los archivos.
  - De Vistas a Qué mostrar: la densidad de árboles con `area_m2` daba valores imposibles; dejamos de usar ese campo y lo sumamos a lo que no mostramos.
  - <confirmar: de Ingesta a Para quién, si la pregunta 3 cambió de calidad del aire a árboles por comuna>