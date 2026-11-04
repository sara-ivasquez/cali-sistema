# Cali · sistema de información

Grupo: Sara Isabel Vásquez · Alejandro Rendón · Enlace: https://sara-ivasquez.github.io/cali-sistema/cali-sistema/web/ · Revisado: 2026-11-04

## Cómo se reconstruye
```
python3 ingesta/todo.py            # baja las 4 fuentes integradas y reescribe lago/*.json y territorio/comunas.geojson
python3 verificacion/verificar.py  # revisa catálogo, contrato, datos personales y territorio; con una sola falla no se publica
```
La ingesta usa solo la biblioteca estándar de Python: no hay que instalar nada ni usar llaves.
Última corrida completa: 2026-11-04 · F01, F02 y F04 respondieron y se reescribieron; F03 (portal de Cali) respondió HTTP 403 y se conservó su último dato real (probado 2026-10-06) sin cambiar la fecha ni inventar una corrida; `verificar.py` dio 88 comprobaciones, 0 fallas.

Puerta de salida (reproducibilidad): borrar el lago, reconstruirlo y comparar con Git.
```
rm -f lago/*.json            # en PowerShell: Remove-Item lago\*.json
python3 ingesta/todo.py
python3 verificacion/verificar.py
git diff --stat -- lago/
```
Lo esperado es que solo cambien las fechas de prueba y las cifras que cambian solas (las vistas del último mes).
- Reproducibilidad comprobada en esta sesión (2026-11-04): se corrió `ingesta/todo.py` dos veces seguidas. `lago/escucha.json`, `lago/desempeno.json` y `lago/territorio.json` quedaron idénticos byte a byte entre las dos corridas, y `territorio/comunas.geojson` con las mismas 22 comunas y las mismas propiedades. Es decir, los cambios son solo de datos y fechas de fuente, no de estructura ni de cálculo:
  ```
  cali-sistema/lago/desempeno.json  | 2 +-   (solo la fecha de prueba)
  cali-sistema/lago/escucha.json    | 2 +-   (solo la fecha de prueba)
  cali-sistema/lago/poblacion.json  | 4 ++--  (solo la unidad de densidad; ver abajo)
  cali-sistema/lago/territorio.json | 4 ++--  (fecha de prueba y licencia copiada del catálogo)
  ```
- Nota sobre `poblacion.json`: su cambio no viene de una corrida nueva (la fuente dio 403), sino de corregir la **unidad de la densidad** de «habitantes por km²» a «habitantes por hectárea», que es como la publica la fuente (44,56 por hectárea equivale a ~4.456 por km²; 44,56 por km² sería imposible para una ciudad de 2,5 millones en ~560 km²). El valor (44,56) y la fecha de prueba (2026-10-06) son los reales de la última corrida con éxito.

### Compuerta de publicación
Como el sistema se publica con `git push` a GitHub Pages, la compuerta es un hook de Git `pre-push` que corre la verificación y cancela el push si falla. Se instala una vez por clon:
```
cp verificacion/pre-push ../.git/hooks/pre-push   # la raíz de Git es la carpeta que contiene a cali-sistema/
chmod +x ../.git/hooks/pre-push
```
Probado en esta sesión: con el lago correcto el hook permite el push (0 fallas); rompiéndolo a propósito (una fecha con hora y una cifra fuera de rango) da 2 fallas y exit 1, y el push se cancela.

Exploraciones (requieren `python3 -m pip install duckdb`):
```
python3 explorar/duckdb_remoto.py  # F02 consultada con DuckDB sin bajarla
python3 explorar/duckdb_lago.py    # cruce de población (F03) y MDM (F02) con SQL sobre el lago
```

Segunda herramienta de visualización y Excel del diccionario:
```
# Mapa de comunas con Leaflet (misma métrica no_arboles que el producto), fuera del sistema:
#   abrir explorar/leaflet_comunas.html en un navegador (o servir estático y abrir /explorar/leaflet_comunas.html)
```
El Excel final del diccionario es `entrega/Diccionario_de_datos_TallerDatos_Cali_Entrega2.xlsx`. El script `verificacion/generar_excel.py` existe como apoyo reproducible (genera una versión del diccionario desde el lago y el catálogo), pero el archivo que se entrega es el Excel de la plantilla del taller, no una regeneración.

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
  4. ¿Cuánta atención recibe el artículo de Cali en Wikipedia y cómo cambia en el año? (F01 · vistas del artículo). Son consultas al artículo con acceso «user» (sin bots), no personas únicas ni evidencia de interés de fuera de Cali: la API no dice de dónde vienen las vistas.
- Escala y comparación: la ciudad contra sí misma en el tiempo (población 1987–2020, MDM 2016–2020, vistas mes a mes); urbana contra rural (F03); y las 22 comunas entre sí (F04).
- Respondidas en el sistema: las cuatro preguntas de la primera entrega; ninguna queda pendiente. Lo que todavía no se puede responder (la población actual y por comuna, porque la del DANE, F05, solo está en Excel, y la calidad del aire, que reemplazamos en la primera entrega por los árboles por comuna) se declara como hueco en la sección «Lo que no sabemos» de la página.
- Lo que decidimos no mostrar, y por qué: los campos del censo arbóreo que la fuente no describe (siglas EEP y EEC, `arb_habita`) y `area_m2`, que resultó ser la cobertura arbórea y no el área de la comuna (con él la densidad daba entre 17.030 y 42.980 árboles por km², imposible para una ciudad; el área se calcula desde el polígono). Tampoco integramos fuentes con registros individuales, como los de seguridad.
- Datos simulados o aproximados (PROXY): ninguno. Todas las cifras salen de las fuentes integradas; las calculadas (porcentajes, árboles por km²) muestran su fórmula a un clic. La portada lo dice.
- Huecos que el sistema dice en pantalla: MDM posterior a 2020, población posterior a 2020, población por comuna, límites oficiales de comunas, calidad del aire.

## La réplica
- Qué replicamos tal cual del ejemplo: la anatomía de carpetas (`catalogo/`, `contrato/`, `ingesta/`, `lago/` con `raw/` fuera del repositorio, `territorio/`, `verificacion/`, `web/`), la ingesta en Python con biblioteca estándar, el lago en JSON con la forma del contrato, los límites en GeoJSON WGS84 y una verificación que bloquea la publicación con un solo fallo, incluida la búsqueda de correos y celulares.
- Qué tuvimos que cambiar para nuestra ciudad: el artículo de Wikipedia (`Cali`) y el código DIVIPOLA (`76001` en lugar de `05001`). Siguiendo la advertencia sobre el catálogo de Lima, normalizamos entidad, licencia y estado con listas cerradas (`catalogo/listas.json`) desde la primera fuente. Además, `verificar.py` exige que todo lo que está en el lago figure como «Integrada» en el catálogo, que cada cifra esté en un rango con sentido para Cali y que todos los puntos del mapa caigan dentro de la ciudad.
- Fuentes catalogadas · integradas · candidata · descartada · no existe: 7 · 4 (F01–F04) · 1 (F05) · 1 (F07, trae solo límites) · 1 (F06). Ver `catalogo/fuentes.json`.
- Huecos: lo que buscamos y no existe abierto para esta ciudad:
  - MDM posterior a 2020: la ficha en datos.gov.co declara frecuencia anual, pero los datos no se actualizan desde el 2022-02-21.
  - Población posterior a 2020 con API: el portal de Cali la tiene solo hasta 2020 (sin actualizar desde 2018-10-29); la proyección vigente del DANE (F05) existe, pero solo en Excel.
  - Límites oficiales de comunas con árboles: la capa de Planeación (F07) en octubre negaba el acceso y el 2026-11-04 ya respondía, pero solo trae los límites, sin el censo arbóreo. Por eso seguimos con la capa del censo arbóreo por comuna (F04), que es la que tiene los árboles.

## ¿Se puede usar?
| Fuente | Licencia | Personas | Estado | Condición |
|---|---|---|---|---|
| F01 · Vistas del artículo «Cali» en Wikipedia | CC0 | No | Integrada | Ninguna |
| F02 · Medición de Desempeño Municipal (DNP) | CC BY-SA 4.0 | No | Integrada | Citar al DNP; lo derivado se publica con la misma licencia. Serie solo hasta 2020 |
| F03 · Población y densidad de Cali (DAPM) | CC BY-SA (sin versión declarada) | No | Integrada | Citar a la Alcaldía; misma licencia. Serie hasta 2020 |
| F04 · Comunas con censo arbóreo (IDESC) | no declara | No | Integrada | No encontramos la ficha de licencia de esta capa (en el diccionario: «no declara»); citamos a la Alcaldía |
| F05 · Proyecciones de población DANE 2018–2042 | por verificar | No | Candidata | Pendiente: solo en Excel |
| F06 · Capa `idesc:mc_comunas` | CC BY-SA (sin versión declarada) | No | No existe | La capa documentada en 2020 ya no está en el servidor |
| F07 · Capa oficial `dapm:pdt_dpa_comunas` | no declara | No | Descartada | En octubre negaba el acceso; el 2026-11-04 ya respondía, pero solo trae límites, sin censo arbóreo. No integrada |

## Bitácora de exploración
| Tramo | Herramienta | Qué pidió para empezar | Licencia | Dónde quedan los datos | ¿Se rehace con un comando? | Estado del proyecto | Qué resolvió | Qué no pudo | ¿Quedó? ¿Por qué? |
|---|---|---|---|---|---|---|---|---|---|
| Ingesta | Python estándar (urllib) | Nada | PSF (OSI) | `lago/*.json` y `territorio/comunas.geojson`, en el repositorio | Sí: `python3 ingesta/todo.py` | Activo (Python 3.14) | Bajó las 4 fuentes; convirtió texto a número; corrigió la codificación de F03; descubrió la capa de comunas preguntándole al servidor | No consulta sin bajar; cruzar fuentes exige escribir código | Sí: cero dependencias y escribe el lago con la forma del contrato |
| Ingesta | DuckDB 1.5.6 (`read_json_auto` remoto) | `pip install duckdb` | MIT (OSI) | En memoria, nada en disco | Sí: `python3 explorar/duckdb_remoto.py` | Activo (1.5.6) | Consultó F02 sin bajarla y dio exactamente los mismos 5 valores que el script base (77.2 · 63.82 · 81.38 · 83.74 · 86.45) | Infirió `anio` como texto (varchar), no como número; no guarda procedencia ni fecha de prueba | No para la ingesta: el resultado no queda en el lago. Sí como control: confirmó los valores del script base |
| Lago | Archivos JSON con la forma del contrato | Nada | — | `lago/*.json` en el repositorio | Sí: `python3 ingesta/todo.py` | — | Cada cifra con valor, unidad, vigencia y fuente; la página los lee directo | Cruzar dos fuentes exige código | Sí: es lo que puede leer la página sin servidor |
| Lago | DuckDB 1.5.6 sobre los mismos JSON | `pip install duckdb` | MIT (OSI) | En memoria; lee los JSON del lago | Sí: `python3 explorar/duckdb_lago.py` | Activo (1.5.6) | Cruzó población (F03) y MDM (F02) por año con una consulta SQL: 5 años en común (2016–2020) | La página no puede leerlo directamente; necesita instalación | No como lago, sí como herramienta de análisis sobre el lago |
| Verificación | `verificar.py` propio | Nada | — | — | Sí: `python3 verificacion/verificar.py` | Propio | Catálogo con listas cerradas; contrato de cada archivo; rangos de cada cifra; ningún campo ni texto con datos personales; coordenadas dentro de Cali. Probado rompiendo el lago a propósito: detectó una fecha con hora y una cifra fuera de rango (2 fallas, exit 1) | No compara contra la corrida anterior | Sí. Segunda herramienta de contraste: `explorar/duckdb_verificacion.py` (SQL en DuckDB sobre los mismos JSON), fila de abajo |
| Vistas | Página HTML + MapLibre GL (hecha con Claude) | Nada: un archivo HTML; MapLibre y OpenStreetMap sin llave | MapLibre: BSD-3 (OSI); mapa base: ODbL | Lee el lago del repositorio; no guarda nada | Sí: se publica sola con cada `git push` | Activo | Las 7 secciones, trazabilidad a un clic en cada cifra, mapa de las 22 comunas, funciona en celular | El mapa depende de servicios externos (MapLibre por CDN y teselas de OpenStreetMap); sin servidor no podría tener compuerta | Sí: es la única que cumple a la vez trazabilidad a un clic con el ID de la fuente, celular y datos leídos del repositorio sin pasos a mano |
| Verificación (exploración) | DuckDB 1.5.6 (SQL) | `pip install duckdb` | MIT (OSI) | En memoria; solo lee | Sí: `python3 explorar/duckdb_verificacion.py` | Exploración, no reemplaza al oficial | Replica con SQL una parte de los controles del oficial (rangos, estados, licencias, coordenadas dentro de una caja que contiene a Cali) | No cubre todos los controles ni bloquea la publicación; requiere instalar DuckDB | Sí como segunda herramienta de contraste sobre los mismos datos |
| Vistas (mapa) | Leaflet 1.9.4 (exploración) | Nada: Leaflet por CDN, teselas OSM sin llave | BSD-2 (Leaflet); ODbL (teselas) | En el navegador; el GeoJSON sale de `territorio/comunas.geojson`, igual que el producto | Sí: abrir `explorar/leaflet_comunas.html` (acepta `?base=`) | Exploración, segunda herramienta de mapa | Mapa de las 22 comunas coloreado por `no_arboles` con los mismos cortes que el producto; clic → detalle de la comuna; panel con fuente, licencia, vigencia y fecha de prueba. Verificado sin navegador con Node sobre el GeoJSON real y por HTTP (carga y CDN) | No se confirmó el render visual ni la interacción con ratón/tacto (el entorno no tiene navegador). kepler.gl se dejó de lado por exigir navegador | Como contraste: confirma que el mismo GeoJSON se pinta por `no_arboles` con otra librería y da el mismo mapa temático. El producto sigue con MapLibre |
| Publicación | GitHub Pages | Repositorio público | — | El repositorio | Sí: cada `git push` a `main` | Activo | Enlace público gratis, sin servidor | No ejecuta código de servidor; la compuerta real se hace con un hook `pre-push` de Git que corre la verificación antes de publicar | Sí: el sistema es abierto; el hook `pre-push` (`verificacion/pre-push`) bloquea el push si la verificación falla |

## Protección
- Nivel: abierto. Las cuatro fuentes integradas son públicas, con licencias que permiten reutilizar (CC0 y CC BY-SA), y todos los datos están agregados por ciudad o por comuna: ninguno apunta a una persona (columna «Personas» del catálogo, y `verificar.py` busca campos y textos con datos personales). Una clave sería teatro: en GitHub Pages no hay servidor, así que solo podría estar escrita en el JavaScript, donde cualquiera la lee.
- Qué protegemos, y de quién: los secretos del código y los crudos. No usamos llaves (todas las fuentes son abiertas y sin autenticación); `lago/raw/` y `.env` están en `.gitignore`.
- Pruebas de terminal contra el sitio publicado (repetidas el 2026-11-04 con `curl`):
  - `GET …/cali-sistema/cali-sistema/web/` → **200**: la página abre.
  - `GET …/cali-sistema/` (raíz del sitio) → **200**: la redirección desde la raíz funciona.
  - `GET …/cali-sistema/cali-sistema/lago/poblacion.json` → **200**: los datos agregados son públicos a propósito.
  - `GET …/cali-sistema/cali-sistema/lago/raw/poblacion.json` → **404**: los crudos no están publicados.
  - `curl … web/ | grep -iE "password|api_key|apikey|token|secret"` → **sin resultados**: la página no tiene claves.
- Revisión de secretos y crudos en el repositorio (2026-11-04, con los comandos de Git disponibles aquí):
  - `git grep -nIE "api_key|apikey|access_token|password=|secret=|BEGIN (RSA|PRIVATE) KEY"` sobre los archivos rastreados → sin coincidencias (salvo esta misma documentación de los patrones).
  - Barrido de `lago/*.json`, `territorio/comunas.geojson` y `catalogo/fuentes.json` con los mismos patrones de `verificar.py` (correos, celulares colombianos, nombres de campo personales) → **0 hallazgos**.
  - `git ls-files | grep lago/raw` → solo `lago/raw/.gitkeep`: los crudos no llegan al repositorio (y `.gitignore` ignora `lago/raw/*`). Se revisó lo **ya rastreado**, no solo el `.gitignore`.
  - `git ls-files | grep -iE "\.env|secret|credential|\.key|token"` → sin resultados: nunca se subió un archivo de secretos.

## Herramienta elegida para las vistas
- Qué necesitábamos mostrar: cifras con su fuente a un clic, series en el tiempo y un mapa de las 22 comunas, que se viera bien en celular.
- Qué teníamos que proteger: nada sensible (nivel abierto); solo evitar cifras escritas a mano y datos que no estén en el lago.
- Herramienta elegida: una página HTML/CSS/JavaScript estática en GitHub Pages, que muestra todo leyendo el lago, sin servidor ni cifras escritas a mano. El mapa usa **MapLibre GL** (BSD-3) con teselas de OpenStreetMap, sin llave; las gráficas de serie se dibujan en SVG propio. Como el nivel es abierto, no necesita compuerta en el navegador.

### Prueba real de dos herramientas sobre los mismos datos
La entrega pide probar dos herramientas de visualización sobre los mismos datos y comparar. Lo hicimos en dos frentes, los dos sobre datos del lago, y dejamos las pruebas en `explorar/` y `web/explorar/`, separadas del producto.

**1. Mapa de comunas: MapLibre (producto) vs. Leaflet (exploración), misma métrica `no_arboles`.**
- Archivos: producto en `web/index.html` (sección «Árboles por comuna»); exploración en [`explorar/leaflet_comunas.html`](explorar/leaflet_comunas.html). Las dos leen el mismo `territorio/comunas.geojson` y aceptan `?base=` para forzar la misma copia.
- Prueba (asistida por Kiro, 2026-11-04): se sirvió el repo en `http://localhost:8777/` y se comprobó por HTTP que la página de Leaflet (200), el GeoJSON y el catálogo cargan desde la misma base, y que las CDN de Leaflet 1.9.4 responden 200. La lógica de datos de la exploración se verificó **sin navegador**, con Node sobre el GeoJSON real: 22 comunas, color por `no_arboles` con los **mismos cortes de cuantiles** que usa el mapa del producto (`[6206, 8746, 12371, 15759]`, min 1.004, máx 51.195), ningún campo nulo rompe el detalle, y la «consulta de una comuna» devuelve valores reales (Comuna 17: 51.195 árboles). Es decir, las dos herramientas colorean las mismas comunas por la misma métrica con los mismos cortes.
  - Carga de comunas: sí (22 polígonos). Color por `no_arboles`: sí. Consulta de una comuna: sí (clic → panel con no_arboles, sanos, regulares, secos, muertos). Campos y tooltip: configurables (Leaflet `bindTooltip`). Fuente/vigencia/fecha: sí, en el panel lateral (lee el catálogo). Exportación/compartir: Leaflet no exporta imagen por sí solo; compartir es publicar el HTML, que lee el GeoJSON del repositorio (los datos quedan en el repo, no incrustados en la página). Ubicación de los datos: el repositorio, igual que el producto.
  - Qué **no** se pudo verificar aquí: el render visual y la interacción con ratón/tacto, porque el entorno no tiene navegador. Lo implementado está probado a nivel de datos; la vista queda lista para abrir en un navegador.
- Sobre kepler.gl: no lo probamos porque exige un navegador (demo web o Jupyter) que este entorno no tiene; en vez de dejar el requisito sin resolver por depender de esa herramienta, implementamos y corrimos la alternativa local con Leaflet sobre exactamente los mismos datos y la misma métrica. Las supuestas limitaciones de kepler.gl no se dan por ciertas: no se comprobaron.
- Decisión: se conserva **MapLibre** como mapa del producto (ya integra la trazabilidad a un clic con el ID de la fuente, el comparador de comunas y la tabla; no hay que sumar nada). Leaflet queda como segunda herramienta de contraste en `explorar/`, que confirma que el mismo GeoJSON se puede pintar por `no_arboles` con otra librería y da el mismo mapa temático.

**2. Gráfica de población: SVG propio (producto) vs. Chart.js (exploración), misma serie F03.**
- Archivos: producto en `web/index.html` (sección «Gente», gráfica SVG); exploración en [`web/explorar/chartjs_poblacion.html`](web/explorar/chartjs_poblacion.html), accesible desde la propia sección «Gente» con el enlace «Ver la misma serie con Chart.js». Las dos leen `lago/poblacion.json` y aceptan `?base=`.
- Prueba (HTTP, con servidor estático local): con la misma `?base=` las dos responden 200 y resuelven la misma copia de `lago/poblacion.json` (34 registros de 1987 a 2020, último año 2.496.442). El SVG no usa librería; Chart.js se carga por CDN. Diferencias observadas en el código: el SVG calcula su escala a mano y filtra nulos; Chart.js trae tooltip, hover y leyenda por defecto. Las dos usan `Intl.NumberFormat('es-CO')` y marcan el gráfico con `role="img"`.
- Qué **no** se pudo verificar aquí: la comparación visual lado a lado en celular y la interacción (tooltips, teclado, lector de pantalla), por no tener navegador en el entorno.
- Decisión: se conserva **SVG** para las gráficas del producto (no agrega dependencia de CDN y conserva el estilo); Chart.js queda como exploración accesible, para comparar.

## Nuestra posición

### Datos · «Los datos también se mueren» (ciclo de vida)
Nuestro propio catálogo es la evidencia. De las siete fuentes que rastreamos, solo una se actualiza sola (F01, las vistas de Wikipedia). El MDM del DNP (F02) declara frecuencia anual, pero sus datos no cambian desde el 2022-02-21. La población del portal de Cali (F03) no se toca desde el 2018-10-29, llega solo a 2020 y el 2026-11-04 además respondió HTTP 403 a la API (seguimos con el último dato real, de 2026-10-06). La capa de comunas documentada en el portal en 2020 ya no existe en el servidor (F06). La capa oficial de Planeación (F07), que en octubre negaba el acceso con «permission denied», el 2026-11-04 ya devolvía sus 22 polígonos: el acceso cambió sin aviso, otra muestra de que un metadato o un estado no son permanentes. Aun así no la integramos, porque solo trae límites y no el censo arbóreo que necesita el sistema. Ninguno de esos portales avisa que algo cambió: lo descubrimos porque cada fuente lleva una fecha de prueba.

- **¿Quién mantiene el sistema cuando termine el curso, o quién decide apagarlo?** Sara Isabel Vásquez responde por el lago y el catálogo. Al terminar el curso el sistema queda publicado tal como está y no se actualiza más; ella es quien decide apagarlo, desactivando GitHub Pages. Volver a ponerlo al día cuesta un comando (`python3 ingesta/todo.py`) más la verificación, porque las fuentes que dejen de responder hacen fallar la ingesta en vez de publicar datos viejos en silencio.
- **¿Qué debe decir la portada el día en que la prueba más reciente tenga más de un año?** Lo dice sola. La página calcula la fecha de prueba más reciente del lago y, si tiene más de un año, muestra antes de cualquier cifra: «Este sistema no se ha actualizado en más de un año… Úsalo como registro histórico, no para decidir hoy». Además, cada cifra lleva su vigencia en la misma línea (por ejemplo, «86,45 de 100 · 2020»), y la sección «Lo que el sistema no sabe» lista las series detenidas y las fuentes caídas.

### Seguridad · «Parecer protegido no es estar protegido» (apariencia)
Decidimos no parecer protegidos. El sistema es abierto: no pide clave, así que no da una sensación de seguridad que no tenga. Una clave en GitHub Pages solo podría estar en el JavaScript, que es exactamente la compuerta de mentira que cualquiera lee con «ver código».

- **¿Qué parte parece protegida sin estarlo, y cómo lo demostramos con una terminal?** Ninguna, y lo comprobamos (2026-10-06). La página responde 200 y los datos del lago también responden 200: son públicos a propósito, porque son agregados y abiertos. Los crudos responden 404, y no porque estén escondidos: nunca llegaron al repositorio (`git ls-files lago/raw` solo muestra `.gitkeep`). La página no contiene claves (`Select-String` sin resultados), y el historial de Git tampoco. Lo que no es dato personal no necesita control técnico; para asegurarnos de que no lo es, `verificar.py` rechaza cualquier campo con nombre de dato personal y cualquier texto con un correo o un celular.
- **¿Qué ve alguien que abre el enlace en una ventana privada?** Lo mismo que cualquier visitante, porque el sitio no tiene sesión ni cookies: es HTML estático que lee archivos públicos. No hace falta una ventana privada para comprobarlo; se ve en el código (no hay login ni `document.cookie`). <pendiente humano: abrirlo en una ventana privada real como confirmación extra; no se hizo en esta sesión por no tener navegador>. En celular, la verificación de esta sesión fue por emulación de viewport y lectura del CSS responsive, no en un teléfono físico.

## Bitácora de IA
| Tramo | Herramienta | Qué le encargamos | Qué entregó | Qué le corregimos |
|---|---|---|---|---|
| Rastreo | Claude | Elegir una ciudad con datos abiertos suficientes | Cali, por su portal propio (datos.cali.gov.co) y su escala por comunas | Pendiente humano: confirmar con el profesor que ningún otro grupo tomó Cali (sin evidencia aún) |
| Ingesta | Claude | Esqueleto del repositorio y scripts de F01 y F02 | Estructura de carpetas, `comun.py`, dos scripts, `todo.py` y `verificar.py` | El zip traía una carpeta anidada: el primer comando falló y el repositorio quedó con la carpeta doble (por eso la página está en `/cali-sistema/cali-sistema/web/`). Propuso el MDM para la gestión actual sin advertir que la serie termina en 2020 |
| Catálogo | Claude | Revisar si el artículo de Wikipedia era el correcto | Indicó cómo comprobar redirección y desambiguación | Lo comprobamos a mano: «Cali» es el artículo principal |
| Ingesta | Claude | Fuente y script de población (F03) | Script que busca la fila de población en la API CKAN del portal de Cali | La primera versión mostraba el texto con la codificación rota («Poblaci贸n»): el portal guardó el archivo en UTF-8 y lo leyó como GBK. Se agregó población urbana y rural con un control de que sumen el total |
| Territorio | Claude | Límites de las comunas (F04) | Script contra el WFS de la IDESC con la capa `idesc:mc_comunas`, tomada de una ficha de 2020 | La capa ya no existía (F06) y el primer script cortaba el mensaje de error. Se cambió para que pregunte al servidor sus capas y valide que traiga polígonos y unos 22 elementos. La oficial (F07) respondió «permission denied»; quedó la del censo arbóreo |
| Exploración | Claude | Scripts de DuckDB para comparar herramientas | `duckdb_remoto.py` y `duckdb_lago.py` | Corrieron bien; DuckDB infirió el año como texto, a diferencia del script base |
| Vistas | Claude | Página con las 7 secciones leyendo el lago | Un HTML que lee los JSON del repositorio, sin cifras escritas a mano | En la vista previa de Claude no cargaban los datos (bloquea conexiones externas); en GitHub la ruta daba 404 por la carpeta doble; calculó árboles por km² con el campo `area_m2` sin confirmar su significado y dio valores imposibles (17.030–42.980 por km²): se corrigió calculando el área desde el polígono |
| Contrato | Claude | Adaptar el lago al contrato del método | Lago con `tema`, `fuentes`, `cifras` con valor/unidad/vigencia/fuente y `series`; verificación del contrato y de datos personales; `contrato/CONTRATO.md` | Corrió sin fallas (88 comprobaciones). La puerta de salida mostró los 4 archivos cambiados porque Git comparaba contra el formato anterior: hubo que subir el lago nuevo y repetir la prueba |
| Vistas | Claude | Mostrar el estado de los árboles por comuna | Sanos, secos y muertos, sin los regulares | En la Comuna 1 los regulares eran 4.246 de 5.782: el estado se veía incompleto. Se agregaron, con el % de sanos |
| Contrato | Claude | Unidad de cada cifra en el contrato | Puso «habitantes por km²» para la densidad de F03 | El valor era 44,56: imposible por km² para una ciudad de 2,5 millones en unos 560 km² (serían unos 4.456). La fuente mide habitantes por hectárea; se corrigió la unidad en `comun.py`, pero el `lago/poblacion.json` quedó sin regenerar con la etiqueta vieja (lo cerró Kiro, ver abajo) |
| Cierre de la 2ª entrega | Kiro | Regenerar el lago, corregir la densidad y dejar la entrega lista | Lago regenerado desde el directorio correcto; unidad de densidad corregida a «habitantes por hectárea» en `lago/poblacion.json` (cifra y serie); `verificar.py` 88 comprobaciones, 0 fallas; dos corridas reproducibles; Excel del diccionario final en `entrega/Diccionario_de_datos_TallerDatos_Cali_Entrega2.xlsx`; hook `pre-push` como compuerta | `pull_comunas.py` ahora caía en la capa de **solo límites** (`dapm:pdt_dpa_comunas`, sin árboles), que antes negaba el acceso y ya responde: se corrigió para exigir que la capa traiga el censo arbóreo (`no_arboles`, `arbol_sano`…), restaurando F04. F03 respondió HTTP 403: se hizo que la ingesta falle con mensaje claro y conserve el dato real sin cambiar la fecha |
| Visualización | Kiro | Segunda herramienta sobre los mismos datos (ver «Prueba real de dos herramientas») | Exploración Leaflet (`explorar/leaflet_comunas.html`): mismas 22 comunas, color por `no_arboles` con los mismos cortes del producto, consulta por comuna; verificada sin navegador con Node sobre el GeoJSON real; prueba HTTP de carga y de CDN | No se verificó el render visual ni la interacción con ratón/tacto: el entorno no tiene navegador. kepler.gl quedó fuera por depender de navegador; se resolvió con la alternativa local Leaflet |

## Revisión cruzada
- Tres cifras auditadas por otro grupo: **pendiente humano**. Es un ejercicio entre grupos del curso; no se ha realizado y no lo inventamos. Qué registrar cuando se haga: qué grupo audita, qué tres cifras revisó, el resultado y las correcciones.
- Ataque de otro grupo: **pendiente humano**. Tampoco se ha realizado. Qué registrar: qué grupo atacó, qué intentó, qué consiguió y qué cambiamos.
- Retroalimentación del profesor y confirmación de que ningún otro grupo tomó Cali: **pendiente humano**, no hay evidencia todavía.
- Vueltas atrás en la ruta (estas sí ocurrieron y están documentadas):
  - De Ingesta a Catálogo: al correr F02 descubrimos que la serie termina en 2020 y lo registramos como hueco.
  - De Ingesta a Catálogo y de vuelta: la capa de comunas documentada no existía (F06); la oficial (F07) negaba el acceso en octubre y en noviembre ya respondía, pero sin el censo arbóreo. F04 pasó de «Candidata» a «No responde» y después a «Integrada» con la capa del censo arbóreo, que es la que trae los árboles.
  - De Lago a Contrato: escribimos el contrato después del primer lago y tuvimos que reescribir el formato de todos los archivos.
  - De Vistas a Qué mostrar: la densidad de árboles con `area_m2` daba valores imposibles; dejamos de usar ese campo y lo sumamos a lo que no mostramos.
  - De Para quién: la pregunta 3 cambió de calidad del aire (sin fuente abierta integrable) a árboles por comuna (F04). El cambio está reflejado en la portada y en «Lo que no sabemos», donde la calidad del aire aparece como hueco. <pendiente humano: confirmar que este cambio de pregunta fue acuerdo del grupo>
  - De Ingesta a cálculo (esta sesión): al regenerar el lago, `pull_comunas.py` tomó la capa de solo límites porque ya respondía; se corrigió para exigir el censo arbóreo. Y la densidad de F03 quedó con la unidad vieja en el JSON aunque `comun.py` ya estaba corregido: se cerró regenerando la unidad.
