# Cómo contribuir

¡Gracias por querer ayudar! Ventanilla Abierta solo funciona si la información es correcta y está al día.

## Reglas editoriales (no negociables)

1. **Nunca inventés.** Si no encontrás una fuente oficial, marcá el dato como `⚠️ Por verificar` en lugar de adivinar.
2. **Fuente y fecha en cada dato.** Usá fuentes oficiales: leyes (SCIJ), sitios de instituciones públicas, La Gaceta, tablas de tarifas oficiales. Indicá la fecha en que lo verificaste (AAAA-MM-DD).
3. **Información, no asesoría legal.** Explicá cómo funciona el trámite; no le digás a nadie qué decisión legal tomar.
4. **Español claro con voseo.** Frases cortas. Si usás un término técnico, explicalo.
5. **No recomendés** despachos, notarías, empresas ni servicios pagos. Sí podés decir cuándo hace falta un profesional.
6. **Costos oficiales**, no honorarios. Si mencionás que un servicio privado suele cobrar más, no des nombres.

## Formas de ayudar

### Reportar un error
Abrí un issue con la plantilla **Corrección**. Incluí la guía, el dato incorrecto, el dato correcto y la fuente oficial.

### Pedir un trámite nuevo
Abrí un issue con la plantilla **Nuevo trámite**.

### Escribir o mejorar una guía
1. Hacé un fork del repositorio.
2. Copiá `plantillas/ficha-tramite.md` a la carpeta de la categoría correspondiente en `tramites/costa-rica/`.
3. Llená todas las secciones. Las que no sepás, marcalas `⚠️ Por verificar`.
4. Agregá la guía a una o más categorías en `_data/categorias.yml`, con su `titulo` y su `url` (la ruta de la guía desde `tramites/costa-rica/`, terminada en `.html`). Por ejemplo:
   `- { titulo: Registro de marca, url: propiedad-intelectual/registro-de-marca.html }`
   El estado ✅/⚠️ no se escribe ahí: el sitio lo toma del campo `estado` de la guía.
5. Revisá tu guía con `python3 scripts/validar.py` (necesita `pip install pyyaml`). El mismo chequeo corre automáticamente en cada pull request.
6. Abrí un pull request explicando qué fuentes consultaste.

## Nombres de archivos

- Minúsculas, sin tildes, con guiones: `registro-de-marca.md`, `traspaso-de-vehiculo.md`.
- Carpetas: usá la carpeta existente que mejor calce (`trabajo`, `emprendimiento`, `artistas`, `eventos`, etc.). La carpeta define la dirección de la guía; las categorías de la portada salen de `_data/categorias.yml`, y una guía puede estar en varias.

## Licencia de tus aportes

Al contribuir, aceptás que tu contenido se publique bajo [CC BY-SA 4.0](LICENSE-CONTENIDO.md) y tu código bajo [MIT](LICENSE).
