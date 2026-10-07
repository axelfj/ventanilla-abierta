---
title: "Decisión 0001: fuentes de alertas"
---

# Decisión 0001: de dónde salen las alertas

Fecha: 2026-10-07. Estado: aceptada para la primera versión.

## Contexto

Queremos avisar de cortes de agua y luz, cierres de carretera y emergencias. La regla del proyecto es que todo dato tenga fuente oficial y fecha, y que no paguemos servidores. Por eso las alertas las junta un workflow de GitHub Actions cada hora y la página `/alertas/` las lee en el navegador.

Revisamos el 2026-10-07 qué publica cada institución y en qué formato. Lo probamos abriendo cada enlace con un lector automático desde la nube; algunos sitios del gobierno bloquean ese tipo de visitas, así que "no se pudo abrir" no siempre quiere decir que el sitio no exista.

## Qué encontramos

| Fuente | Qué publica | Formato | ¿Se pudo abrir? | Decisión |
|---|---|---|---|---|
| IMN, avisos CAP (`cap-sources.s3.amazonaws.com/cr-imn-es/rss.xml`) | Avisos meteorológicos oficiales | RSS con avisos en el estándar CAP 1.2 | Sí, con avisos reales del 06/10/2026 | **Se usa** |
| Red Sismológica Nacional, UCR (`rsn.ucr.ac.cr/...?format=feed&type=rss`) | Sismos sentidos y revisados | RSS | Sí, con sismos del 03 y 06/10/2026 | **Se usa** |
| USGS (`earthquake.usgs.gov/fdsnws/event/1/query`) | Sismos en todo el mundo | GeoJSON, dominio público | Sí | **Se usa** solo para magnitud 4.5 o más, como respaldo |
| GDACS (`gdacs.org/xml/rss.xml`) | Desastres grandes (ONU y Unión Europea) | RSS | Sí (ese día no había nada de Costa Rica) | **Se usa**, filtrado a Costa Rica |
| CNFL, suspensiones (`cnfl.go.cr/servicios/autogestion/suspensiones`) | Cortes de luz programados en la GAM | Tabla HTML | Sí, con cortes reales del 06 y 07/10/2026 | **Se usa** (se lee la tabla) |
| JASEC (`jasec.go.cr/index.php/noticias?format=feed&type=rss`) | Noticias, entre ellas interrupciones | RSS | Una de dos pruebas respondió | **Se usa**, filtrando por "interrupción", "suspensión" o "corte" |
| ICE, mantenimiento programado | Cortes de luz programados | Página que carga los datos con JavaScript | Abre, pero sin datos | Solo enlace |
| Coopeguanacaste, Coopelesca | Cortes y averías | Páginas con JavaScript | Abren, pero sin datos | Solo enlace |
| Coopesantos | Cronograma semanal | HTML | Sí | Solo enlace por ahora; se puede leer después |
| Coopealfaroruiz | Suspensiones | Imágenes y Google Drive | Sí | Solo enlace |
| AyA | Cortes de agua | Página con JavaScript y redes sociales | Abre, pero vacía | Solo enlace |
| ESPH | Agua y luz en Heredia | — | No (bloqueo 403) | Solo enlace |
| CNE | Alertas por cantón | — | No (bloqueo 403) | Solo enlace |
| MOPT, CONAVI | Noticias de obras y cierres | HTML sin RSS; los cierres salen sobre todo en redes | Sí | Solo enlace |
| Waze for Cities | Cierres e incidentes | API | — | No aplica: solo se da a gobiernos y operadores viales con convenio |
| Facebook, X | Avisos de casi todas las instituciones | — | — | **No se usa**: sus términos prohíben leerlos automáticamente |
| datos.go.cr | Catálogo nacional de datos abiertos (CKAN) | — | La portada sí | No encontramos datos de cortes ni cierres |

No encontramos ningún proyecto comunitario previo que junte cortes de agua o luz de Costa Rica en datos abiertos.

## Decisión

1. El recolector (`scripts/recolectores/alertas.py`) lee solo las fuentes marcadas "Se usa". Usa únicamente la biblioteca estándar de Python.
2. Cada alerta enlaza al aviso oficial y guarda cuándo se recuperó. No reescribimos el contenido del aviso, solo lo resumimos.
3. Si una fuente falla, se conservan sus alertas de la hora anterior y la página dice qué fuente no respondió.
4. Para agua y carreteras, la página muestra dónde publica cada institución. No leemos Facebook ni X.
5. Los datos se guardan en la rama `datos`, reescrita en cada corrida con un solo commit, para no llenar el historial de `main`.

## Qué falta y cómo seguir

- **Agua y carreteras**: pedir a AyA, ESPH, MOPT, CONAVI y CNE que publiquen sus avisos en un formato abierto (RSS o CAP). El IMN ya lo hace, así que es posible.
- **ICE y cooperativas con JavaScript**: se podrían leer con un navegador automático (Playwright) dentro de Actions. Es más frágil; se evalúa después.
- **Reportes de la comunidad**: fuera del alcance por ahora (ver `docs/arquitectura.md`, sección 12).
- Confirmar desde los servidores de GitHub qué fuentes responden: el workflow "Recolectar alertas" lo muestra en su resumen en cada corrida.
