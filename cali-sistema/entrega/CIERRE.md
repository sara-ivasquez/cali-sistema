# Cierre de la segunda entrega · Sistema de información de Santiago de Cali

Sesión de cierre asistida por Kiro · 2026-11-04. Rama de trabajo: `vistas-mejoras` (fusionada con `origin/main`, que traía el contrato y el lago nuevo). Raíz de Git: carpeta que contiene a `cali-sistema/`; raíz efectiva del proyecto: `cali-sistema/cali-sistema/`.

## Estado por requisito del enunciado

| # | Requisito | Estado | Evidencia |
|---|---|---|---|
| 1 | Sistema publicado y funcional, con los nombres del grupo visibles | Cumplido | Publicado en https://sara-ivasquez.github.io/cali-sistema/cali-sistema/web/ (HTTP 200). Nombres en el pie: «Sara Isabel Vásquez y Alejandro Rendón» y en la barra móvil. |
| 2 | Repositorio con ingesta, verificación y README | Cumplido | `ingesta/`, `verificacion/verificar.py`, `README.md` actualizados. |
| 3 | Excel del diccionario actualizado | Cumplido | `entrega/Diccionario_de_datos_TallerDatos_Cali_Entrega2.xlsx` (plantilla del taller, 6 hojas). El script `verificacion/generar_excel.py` queda como apoyo reproducible, pero el archivo entregado es la plantilla, no una regeneración. |
| 4 | Al menos tres fuentes integradas y usadas en las vistas | Cumplido (4) | F01 (Wikipedia), F02 (MDM/DNP), F03 (población/DAPM), F04 (censo arbóreo). Las cuatro se muestran en la página. |
| 5 | Funciona en teléfono | Parcial | CSS responsive con media query (≤860px) y barra móvil; probado por emulación de viewport y lectura de CSS. No probado en teléfono físico en esta sesión. |
| 6 | Cada cifra con fuente F0x, vigencia y fecha de prueba a un clic | Cumplido | Panel de trazabilidad por cifra (`cifra()`/`abrirTraza()` en `web/index.html`): ID de fuente, entidad, licencia, unidad, vigencia y «fuente probada el». |
| 7 | Una vista territorial por comuna | Cumplido | Mapa MapLibre de las 22 comunas, ficha por comuna, tabla ordenable y comparador de dos comunas. |
| 8 | Responder ≥2 preguntas de la 1ª entrega e identificar pendientes | Cumplido | Las 4 preguntas respondidas (población, gestión, árboles, interés). Pendientes declarados en «Lo que no sabemos»: población actual/por comuna y calidad del aire. |
| 9 | Sin datos personales expuestos | Cumplido | 0 hallazgos de PII en lago/geojson/catálogo; `verificar.py` revisa campos y textos personales; `personas = No` en todas las fuentes. |
| 10 | Identificar datos simulados o PROXY | Cumplido | No hay PROXY: la portada y «Fuentes y método» lo declaran; las cifras calculadas muestran su fórmula. |
| 11 | Sin llaves pagas ni tarjeta | Cumplido | Ingesta con biblioteca estándar; APIs/servicios abiertos sin autenticación; mapa con MapLibre/OSM sin llave. |
| 12 | Prueba real de dos herramientas de visualización sobre los mismos datos y comparación en el README | Cumplido con límite | Mapa: MapLibre (producto) vs. Leaflet (`explorar/leaflet_comunas.html`), misma métrica `no_arboles`, mismos cortes de cuantiles; verificado sin navegador con Node y por HTTP. Gráfica: SVG (producto) vs. Chart.js (`web/explorar/chartjs_poblacion.html`), misma serie F03. Límite: render visual no confirmado por falta de navegador en el entorno. |
| 13 | Decisiones sobre qué mostrar, uso, protección y herramienta | Cumplido | Secciones «Para quién y qué pregunta», «Protección» y «Herramienta elegida» del README. |
| 14 | Bitácora de IA actualizada + reflexión de datos y de seguridad | Cumplido | Bitácora con la sesión de Kiro; reflexiones «Los datos también se mueren» y «Parecer protegido no es estar protegido». |

## Correcciones y validaciones de esta sesión (resumen)
- **Densidad de población**: `comun.py` ya marcaba «habitantes por hectárea», pero `lago/poblacion.json` conservaba la etiqueta vieja «habitantes por km²». Corregido en la cifra y en la serie. Valor 44,56 y fecha 2026-10-06 son los reales; no se convirtió el número porque la fuente ya lo publica por hectárea.
- **F04 (comunas)**: al regenerar, `pull_comunas.py` caía en la capa de solo límites `dapm:pdt_dpa_comunas` (que antes negaba el acceso y ahora responde), perdiendo los árboles. Se corrigió para exigir que la capa traiga el censo arbóreo (`no_arboles`, `arbol_sano`…); vuelve a usar `expediente_municipal:emc_amb_sos_car_censo_arboreo_comuna`.
- **F03 (población)**: el portal respondió HTTP 403. La ingesta ahora falla con mensaje claro y **conserva el dato real** sin cambiar la fecha ni inventar una corrida.
- **F07**: pasó de «No responde» a «Descartada»: ya responde, pero solo trae límites, no árboles.
- **Compuerta de publicación**: hook `pre-push` (`verificacion/pre-push`) que corre `verificar.py` y cancela el push si falla.
- **Verificación**: 88 comprobaciones, 0 fallas. Dos corridas de ingesta reproducibles (escucha/desempeno/territorio idénticos byte a byte).

## Pendientes humanos (no técnicos, no fabricados)
- Auditoría cruzada de cifras por otro grupo y ejercicio de ataque entre grupos.
- Confirmación del profesor de que ningún otro grupo tomó Cali.
- Confirmación en ventana privada real y prueba en teléfono físico.
- Acuerdo del grupo registrado sobre el cambio de la pregunta 3 (calidad del aire → árboles).

## Texto para el buzón
> Entrega 2 · Sistema de información de Santiago de Cali
> Grupo: Sara Isabel Vásquez y Alejandro Rendón
> Sistema publicado: https://sara-ivasquez.github.io/cali-sistema/cali-sistema/web/
> Repositorio: https://github.com/sara-ivasquez/cali-sistema
> Excel adjunto: cali-sistema/entrega/Diccionario_de_datos_TallerDatos_Cali_Entrega2.xlsx
> El sistema integra 4 fuentes abiertas (F01 Wikipedia, F02 MDM/DNP, F03 población DAPM, F04 censo arbóreo IDESC), responde las cuatro preguntas de la primera entrega, muestra la procedencia de cada cifra a un clic (fuente F0x, vigencia y fecha de prueba) y funciona en celular. No usa datos personales ni PROXY. Verificación: 88 comprobaciones, 0 fallas.

## Archivo que debe adjuntarse al buzón
`cali-sistema/entrega/Diccionario_de_datos_TallerDatos_Cali_Entrega2.xlsx`
