---
title: Arquitectura técnica
---

# Arquitectura técnica de Ventanilla Abierta

> Documento de diseño. Versión 1, 2026-10-06. Describe cómo está hecho el proyecto hoy y hacia dónde puede crecer sin pagar servidores ni dominio.

## 1. Principios que mandan sobre todo lo demás

1. **Costo cero para el proyecto.** Nada que necesite tarjeta de crédito para funcionar. Si un servicio gratuito desaparece, el sitio tiene que poder mudarse en una tarde.
2. **El contenido es texto plano.** Markdown y YAML en git. Cualquier persona puede leerlo, editarlo y copiarlo sin herramientas especiales.
3. **Cada dato tiene fuente oficial y fecha.** La arquitectura tiene que hacer fácil cumplir esa regla y difícil saltársela (validación automática).
4. **Funciona en un teléfono barato con mala señal.** Páginas livianas, sin frameworks pesados, legibles sin JavaScript.
5. **Sin rastreo.** No recolectamos datos de quien visita el sitio.

## 2. Cómo está hoy (fase 1)

- **Sitio estático con Jekyll**, publicado por GitHub Pages desde `main` (raíz). Sin tema: layout propio en `_layouts/default.html` y `_layouts/categoria.html`, estilos en `assets/css/style.scss`.
- **Portada con tarjetas**: `_includes/tarjetas.html` recorre `_data/categorias.yml`.
- **Fichas** en `tramites/costa-rica/<carpeta>/<slug>.md`, con el formato de `plantillas/ficha-tramite.md`.
- **Páginas de categoría** en `tramites/costa-rica/categorias/<slug>.md`, que solo apuntan al layout `categoria`.
- **Contribuciones** por issues (plantillas "Corrección" y "Nuevo trámite") y pull requests.
- **Licencias**: MIT para el código, CC BY-SA 4.0 para el contenido.

Esto ya cumple los principios. La recomendación es **no cambiar de stack**, sino agregar estructura y validación alrededor.

### Problemas que vale la pena resolver pronto

| Problema | Por qué importa | Propuesta |
|---|---|---|
| El estado (✅/⚠) de cada ficha está escrito dos veces: en su front matter y en `_data/categorias.yml`. | Se pueden desincronizar y el sitio mostraría ✅ en una guía que es borrador. | Que la página de categoría lea el estado desde la ficha (sección 4.2). |
| El campo `categoria` de las fichas mezcla nombres de carpeta (`contratos`, `general`, `vivienda`) con slugs de categoría (`contratos-y-abogados`). | No sirve para filtrar ni validar. | Separar `carpeta` (implícita en la ruta) de `categorias` (lista de slugs válidos). |
| `CONTRIBUTING.md` dice que se agregue la guía a `tramites/costa-rica/README.md`, pero el índice real es `_data/categorias.yml`. | Confunde a quien llega a ayudar. | Corregir el paso en `CONTRIBUTING.md`. |
| No hay validación automática. | Un PR puede llegar sin fuentes o sin fecha y nadie lo nota. | GitHub Actions con validador de esquema y enlaces (sección 5.3). |
| No hay buscador. | Con 25 guías se navega; con 100 no. | Índice de búsqueda estático (sección 3). |

## 3. Stack recomendado

| Pieza | Elección | Por qué | Alternativa si falla |
|---|---|---|---|
| Generador | **Jekyll** (el que ya usa el repo) | GitHub Pages lo compila sin configurar nada; Liquid alcanza para todo lo de la fase 1. | Eleventy o Astro, si algún día hace falta lógica que Liquid no permite. El contenido no cambia. |
| Hosting | **GitHub Pages** | Gratis para repos públicos, HTTPS incluido, sin servidor. | Cloudflare Pages o Netlify (plan gratis), apuntando al mismo repo. |
| Compilación | Hoy: la compilación automática de Pages. Cuando haga falta: **GitHub Actions** (ver sección 7). | Actions es gratis en repos públicos y permite validar, generar índices y traer datos. | — |
| Estilos | CSS propio con variables y modo oscuro (ya existe). | Cero dependencias, liviano. | — |
| JavaScript | **Solo mejora progresiva**, sin framework. | El sitio se lee sin JS; el JS agrega búsqueda, alertas y asistente. | Preact o Alpine si una pantalla lo necesita de verdad. |
| Búsqueda | **Índice JSON generado por Liquid** (`/buscar.json`) + búsqueda en el navegador con un script pequeño (por ejemplo MiniSearch o Lunr). | No necesita servidor ni compilación extra; funciona en Pages tal cual. | Pagefind, cuando se pase a compilar con Actions (indexa el HTML final y es muy liviano). |
| Lectura sin conexión | **Service worker** que guarda las fichas visitadas (PWA). | Útil en zonas con mala señal. | — |
| Validación | **Python** en Actions: `pyyaml` + `jsonschema` para el front matter, `lychee` para enlaces rotos. | Fácil de leer y de mantener por voluntarios. | — |
| Analítica | **Ninguna** por ahora. | Principio 5. Si un día se necesita, una opción sin cookies y autoalojable. | — |
| Asistente IA (futuro) | **WebLLM** en el navegador, o **API key propia** de quien lo usa, guardada solo en su navegador. | El proyecto no paga tokens ni guarda conversaciones. | — |

## 4. Estructura del repositorio

Las URL actuales se mantienen: mover fichas rompe enlaces compartidos en redes. Lo nuevo se agrega alrededor.

```
ventanilla-abierta/
├── _config.yml
├── _data/
│   ├── categorias.yml            # categorías y orden de temas (sin duplicar el estado)
│   ├── instituciones.yml         # nuevo: catálogo de instituciones con sitio oficial
│   └── territorio/               # fase 2: provincias, cantones y distritos
├── _includes/  _layouts/  assets/
├── tramites/
│   └── costa-rica/
│       ├── index.md
│       ├── categorias/<slug>.md
│       └── <carpeta>/<slug>.md   # fichas (rutas actuales sin cambios)
├── alertas/                      # fase 2: páginas que muestran alertas
├── buses/                        # fase 2: páginas de rutas y horarios
├── datos/                        # fase 2: datos abiertos versionados
│   ├── alertas/                  # JSON generado (ver sección 6)
│   └── buses/gtfs/<operador>/    # horarios en formato GTFS
├── esquemas/
│   ├── ficha.schema.json         # reglas del front matter de una ficha
│   ├── alerta.schema.json
│   └── institucion.schema.json
├── scripts/
│   ├── validar_fichas.py
│   ├── revisar_vencidas.py
│   └── recolectores/             # fase 2: un script por fuente oficial
├── plantillas/ficha-tramite.md
├── docs/
│   ├── arquitectura.md           # este documento
│   └── decisiones/               # registros cortos de decisiones (ADR)
├── .github/
│   ├── ISSUE_TEMPLATE/*.yml      # formularios de issues
│   ├── pull_request_template.md
│   ├── CODEOWNERS
│   └── workflows/
│       ├── validar.yml           # en cada PR
│       ├── revisar-vencidas.yml  # una vez al mes
│       └── recolectar-alertas.yml# fase 2
├── CONTRIBUTING.md  README.md  LICENSE  LICENSE-CONTENIDO.md
```

Para que Jekyll no publique lo que no es página, `_config.yml` debe excluir `esquemas/`, `scripts/` y `docs/decisiones/` (y `datos/` solo si se sirve por otro camino).

### 4.1 Varios países

El país ya está en la ruta (`tramites/costa-rica/`). Para Centroamérica se agrega otra carpeta (`tramites/panama/`) y su archivo de categorías (`_data/paises/panama/categorias.yml`). No hace falta decidirlo ahora; solo evitar escribir "Costa Rica" fijo en los layouts.

## 5. Modelo de datos: guías de trámites

### 5.1 Ficha

Una ficha es un archivo Markdown. El **front matter** lleva lo que una máquina necesita (para validar, buscar, filtrar y avisar cuándo revisar); el **cuerpo** lleva la explicación para personas, con las secciones de la plantilla.

```yaml
---
title: "Registro de marca"
resumen: "Cómo proteger el nombre de tu negocio o proyecto ante el Registro Nacional."
pais: CR
categorias: [emprendimiento, artistas]   # slugs de _data/categorias.yml
estado: verificado                       # borrador | verificado
ultima_verificacion: 2026-10-05
revisar_cada_dias: 180                   # opcional; por defecto 180
solo: depende                            # si | no | depende
profesional: abogado                     # ninguno | notario | abogado
instituciones: [registro-nacional]       # ids de _data/instituciones.yml
costos:
  - concepto: Solicitud de marca, por clase
    monto: 50
    moneda: USD
    fuente: https://...                  # URL oficial
    verificado: 2026-10-05
fuentes:
  - nombre: Tabla de aranceles del Registro Nacional
    url: https://...
    consultada: 2026-10-05
palabras_clave: [marca, logo, nombre comercial]
---
```

Reglas que valida el esquema (`esquemas/ficha.schema.json`):

- `title`, `pais`, `categorias`, `estado`, `ultima_verificacion` y al menos una `fuentes` son obligatorios.
- Si `estado: verificado`, **cada costo** tiene `fuente` y `verificado`, y ninguna fuente es de un despacho o empresa privada (lista de dominios permitidos en `_data/instituciones.yml`).
- Las fechas tienen formato `AAAA-MM-DD` y no están en el futuro.
- Cada slug de `categorias` existe en `_data/categorias.yml`.

Los costos y fuentes también se siguen mostrando en el cuerpo (tabla y lista), como hoy. Tenerlos en el front matter permite, además, que el asistente IA y el buscador los citen con su fuente, y que un script avise cuando una tarifa lleva mucho sin revisarse. La migración puede ser gradual: el validador solo exige los campos nuevos a las fichas que se marquen `verificado` después de cierta fecha.

### 5.2 Categoría

`_data/categorias.yml` queda como **el orden y la agrupación**, no como fuente del estado:

```yaml
- slug: emprendimiento
  icono: "💼"
  nombre: Emprendimiento y negocios
  desc: Montar tu negocio, Hacienda, reportes y marcas.
  temas:
    - ficha: emprendimiento/como-montar-un-negocio   # ruta sin .md
    - ficha: propiedad-intelectual/registro-de-marca
    - planeado: Facturación electrónica               # aún no existe
```

El layout busca cada `ficha` en `site.pages` y toma de ahí el título y el estado. Así ✅/⚠ viene siempre de la ficha.

### 5.3 Institución

```yaml
# _data/instituciones.yml
- id: registro-nacional
  nombre: Registro Nacional
  sitio: https://www.rnpdigital.com
  dominios_oficiales: [rnpdigital.com, registronacional.go.cr]
```

Sirve para mostrar "Dónde se hace", para validar que las fuentes sean oficiales y, en la fase 2, para enlazar alertas con la institución que las emite.

### 5.4 Ciclo de vida de una ficha

```
planeado ──► borrador (⚠) ──► verificado (✅) ──► vencida ──► verificado
                   ▲                                  │
                   └──────── corrección con fuente ◄──┘
```

"Vencida" no es un estado escrito a mano: se calcula con `ultima_verificacion + revisar_cada_dias`. El sitio puede mostrar "Revisada hace más de 6 meses" y un workflow mensual abre un issue por cada ficha vencida (sección 7.3).

## 6. Modelo de datos: alertas locales y buses (fase 2)

### 6.1 Advertencia de diseño

Ventanilla Abierta **no es un sistema de emergencias**. Los workflows programados de GitHub pueden atrasarse y no hay garantía de tiempo real. Cada pantalla de alertas debe decir: "Para emergencias, llamá al 911. Información oficial: la institución que emite el aviso." Las alertas resumen y enlazan; no reemplazan el aviso oficial.

Todavía **no está verificado** qué instituciones publican sus avisos en un formato que se pueda leer automáticamente (AyA para agua, ICE y las distribuidoras para luz, MOPT/CONAVI para carreteras, ARESEP y el CTP para buses). Lo primero de la fase 2 es una investigación por fuente, documentada en `docs/decisiones/`, antes de escribir recolectores.

### 6.2 Alerta

Formato propio, simple, inspirado en el estándar CAP (Common Alerting Protocol) para poder convertir si una institución lo publica así.

```json
{
  "id": "aya-2026-10-06-0001",
  "tipo": "agua",                         // agua | luz | carretera | otro
  "titulo": "Suspensión del servicio de agua en San Pedro",
  "descripcion": "Trabajos en tubería principal.",
  "inicio": "2026-10-07T08:00:00-06:00",
  "fin": "2026-10-07T17:00:00-06:00",     // null si no se sabe
  "zona": {
    "provincia": "San José",
    "canton": "Montes de Oca",
    "distritos": ["San Pedro"],
    "codigos": ["1-15-01"],               // División Territorial Administrativa
    "geometria": null                      // GeoJSON opcional
  },
  "fuente": {
    "institucion": "aya",                  // id de _data/instituciones.yml
    "url": "https://...",                  // el aviso oficial
    "recuperado": "2026-10-06T05:00:00Z"
  },
  "origen": "oficial",                     // oficial | comunidad
  "actualizado": "2026-10-06T05:00:00Z"
}
```

- `zona.codigos` permite filtrar "mi distrito" sin geolocalización. La persona elige su distrito una vez y se guarda solo en su navegador.
- `origen: comunidad` se reserva para un posible futuro con reportes de personas; si se usa, se muestra distinto y nunca se mezcla con lo oficial. No está en el alcance inicial.
- Los recolectores escriben `datos/alertas/activas.json` (lo vigente) y un archivo por día en `datos/alertas/historico/AAAA-MM-DD.json`.

### 6.3 Buses

Usar el estándar **GTFS** (General Transit Feed Specification): archivos CSV (`agency.txt`, `routes.txt`, `stops.txt`, `trips.txt`, `stop_times.txt`, `calendar.txt`). Ventajas: es abierto, hay validadores gratuitos y los datos sirven también para otras apps.

- Un directorio por operador: `datos/buses/gtfs/<operador>/`.
- Cada operador lleva un `fuente.yml` con de dónde salió cada dato (permiso de ARESEP, publicación del operador, levantamiento comunitario) y su fecha.
- Las tarifas se toman solo de la fuente oficial que las fija, con fecha, igual que los costos de las fichas.
- El sitio genera páginas estáticas por ruta (horarios en tabla) y, opcionalmente, un buscador "de A a B" en el navegador que lee los CSV.

## 7. Cómo aceptar contribuciones

### 7.1 Caminos de entrada, de menos a más técnico

1. **Formulario de issue** (Corrección / Nuevo trámite / Alerta incorrecta). Pasar las plantillas actuales a **formularios YAML** de GitHub, con campos obligatorios ("Fuente oficial", "Fecha en que lo verificaste").
2. **Botón "Editar esta página"** en cada ficha, que abre el editor web de GitHub. GitHub hace el fork y el PR solo; quien contribuye no necesita instalar nada.
3. **Pull request** normal para quien ya usa git.
4. **Fuente pegada**: para sitios que no se pueden leer automáticamente, quien contribuye pega el texto oficial en el issue, con enlace y fecha.

### 7.2 Revisión

- **Plantilla de PR** con casillas: "Cada dato nuevo tiene fuente oficial y fecha", "No recomiendo despachos ni servicios pagos", "Usé voseo y lenguaje claro".
- **CODEOWNERS**: Axel como dueño de todo al inicio; luego, personas de confianza por categoría (por ejemplo, alguien de música para `artistas/`).
- **Etiquetas**: `correccion`, `nuevo-tramite`, `necesita-fuente`, `vencida`, `fase-2`, `buen-primer-aporte`.
- **Regla de verificación**: una ficha pasa a `verificado` solo si alguien distinto de quien la escribió revisó las fuentes. Mientras el proyecto tenga una sola persona mantenedora, basta con que la revise Axel.
- **Protección de `main`** (Axel la activa en Settings → Branches): PR obligatorio y el workflow `validar` en verde.

### 7.3 Automatización con GitHub Actions

| Workflow | Cuándo corre | Qué hace |
|---|---|---|
| `validar.yml` | En cada PR | Valida el front matter contra `esquemas/ficha.schema.json`, revisa que las categorías existan, compila el sitio con Jekyll y busca enlaces rotos con lychee. Comenta en el PR qué falta. |
| `revisar-vencidas.yml` | Una vez al mes | Busca fichas con `ultima_verificacion` más vieja que `revisar_cada_dias` y abre un issue `vencida` por cada una (sin duplicar). |
| `recolectar-alertas.yml` | Fase 2, cada 30 a 60 min | Corre los recolectores, valida contra `alerta.schema.json` y publica los JSON. |

Nota: GitHub desactiva los workflows programados de repos públicos que pasan 60 días sin actividad. El workflow mensual de fichas vencidas mantiene el repo activo, pero conviene saberlo.

### 7.4 Comunidad

- **Código de conducta** (Contributor Covenant en español).
- **GitHub Discussions** para preguntas que no son errores ("¿cómo hago tal cosa?"). Lo activa Axel en Settings.
- Una **guía de estilo** corta dentro de `CONTRIBUTING.md` con ejemplos de frases buenas y malas.

## 8. Licencias

| Qué | Licencia | Comentario |
|---|---|---|
| Código (layouts, CSS, JS, scripts) | **MIT** (ya elegida) | Permite reutilizar el código en cualquier proyecto. |
| Contenido (fichas, textos) | **CC BY-SA 4.0** (ya elegida) | Quien copie las guías debe dar crédito y compartir igual. Evita que alguien las encierre detrás de un muro de pago. |
| Datos que produce el proyecto (alertas normalizadas, GTFS levantado por la comunidad) | **CC BY-SA 4.0** también, salvo que la fuente imponga otra cosa | Mantiene una sola licencia de contenido. Si más adelante se busca que apps de transporte los usen, evaluar ODbL, que es la habitual en datos geográficos abiertos. |
| Datos tomados de instituciones | Los de la institución | Se citan y enlazan. Antes de redistribuir datos crudos de una institución, revisar sus términos y anotarlo en `fuente.yml`. |
| Textos de leyes y decretos | Se citan con enlace a la fuente oficial | No se copian completos; se explican. |

Además: cada archivo de contenido indica su licencia en el pie del sitio (ya existe), y `CONTRIBUTING.md` ya dice que los aportes entran bajo estas licencias.

## 9. Despliegue de bajo costo

### Etapa A (hoy): Pages compila solo

- Fuente: rama `main`, raíz. Costo: ₡0.
- Suficiente mientras no se necesiten plugins de Jekyll fuera de la lista que Pages permite ni pasos de compilación propios.

### Etapa B: compilar con GitHub Actions

Cuándo: al agregar Pagefind, validaciones que deban bloquear la publicación, o datos de la fase 2.

1. Agregar `.github/workflows/publicar.yml` con las acciones oficiales de Pages (`actions/configure-pages`, `actions/upload-pages-artifact`, `actions/deploy-pages`).
2. Axel cambia en Settings → Pages la fuente de "Deploy from a branch" a "GitHub Actions".
3. El workflow compila Jekyll, genera el índice de búsqueda, copia `datos/` y publica.

Costo: ₡0 (los minutos de Actions son gratis en repos públicos).

### Etapa C: datos de la fase 2

- Los recolectores guardan los JSON en una rama aparte, `datos`, para no llenar el historial de `main` con commits automáticos.
- El workflow de publicación toma la última versión de esa rama al compilar. Si hace falta refrescar alertas sin recompilar todo, el navegador puede leerlas directamente desde la rama `datos` (GitHub sirve esos archivos con CORS abierto).
- Límites a respetar: un sitio de Pages tiene un tope de 1 GB y un ancho de banda mensual recomendado de 100 GB. El histórico de alertas debe comprimirse o recortarse a un período razonable.

### Dominio

`axelfj.github.io/ventanilla-abierta` es gratis y suficiente. Si un día se compra un dominio, Pages lo soporta con HTTPS sin costo adicional; el `baseurl` de `_config.yml` es lo único que cambia.

### Plan de salida

Si GitHub Pages dejara de servir, el mismo repo se conecta a Cloudflare Pages o Netlify (planes gratuitos) con el comando `jekyll build` y la carpeta `_site`. No hay base de datos ni servidor que migrar.

## 10. Asistente IA (más adelante)

- **Nunca en un servidor del proyecto.** Dos modos, ambos en el navegador:
  1. **Modelo local con WebLLM**: se descarga una vez, corre en la GPU del dispositivo. Gratis y privado, pero pesado para teléfonos de gama baja.
  2. **API key propia**: la persona pega su key; se guarda solo en su navegador y las llamadas salen directo del navegador al proveedor.
- **Respuestas ancladas a las fichas**: el asistente busca primero en el índice de búsqueda, recibe solo las fichas relevantes y debe citar la ficha y su fuente oficial. Si la respuesta no está en las fichas, lo dice.
- El aviso "información, no asesoría legal" aparece siempre en el chat.

## 11. Hoja de ruta técnica

| Paso | Qué | Necesita a Axel en Settings |
|---|---|---|
| 1 | Corregir `CONTRIBUTING.md` (índice real) y excluir carpetas nuevas en `_config.yml`. | No |
| 2 | Esquema de ficha + `validar.yml` en modo aviso (comenta, no bloquea). | No |
| 3 | Estado leído desde la ficha en la página de categoría. | No |
| 4 | Formularios de issue en YAML, plantilla de PR, botón "Editar esta página". | No |
| 5 | Buscador con índice JSON. | No |
| 6 | `revisar-vencidas.yml` mensual. | No |
| 7 | Protección de `main`, Discussions. | Sí |
| 8 | Pasar Pages a GitHub Actions (etapa B). | Sí |
| 9 | Fase 2: investigar fuentes de alertas y buses, una por una. | No |
| 10 | Fase 2: recolectores, rama `datos`, páginas de alertas y buses. | No |
| 11 | Asistente IA en el navegador. | No |

## 12. Decisiones abiertas

- **Licencia de los datos de buses**: CC BY-SA 4.0 (una sola licencia) u ODbL (más usada en datos de transporte). Se decide cuando haya datos.
- **Alertas de la comunidad**: si se aceptan o no, y cómo se moderan. Fuera del alcance inicial.
- **Idiomas**: si algún día se traducen guías (por ejemplo, al inglés para personas extranjeras residentes), Jekyll lo permite con una carpeta por idioma; no se diseña ahora.
