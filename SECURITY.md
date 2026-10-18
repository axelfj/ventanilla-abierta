# Seguridad

Ventanilla Abierta es un sitio estático: no tiene cuentas, contraseñas, formularios ni base de datos.
Aun así, si encontrás un problema de seguridad (por ejemplo, una forma de meter código en la página de
alertas o de cambiar los datos publicados), **no abras un issue público**.

Reportalo en privado desde la pestaña **Security → Report a vulnerability** del repositorio.
Te respondemos ahí.

## Qué hace el sitio para protegerse

- Las páginas de alertas y buses muestran lo que viene de sitios externos siempre como texto, nunca como HTML,
  y solo enlazan a direcciones `https://` o `http://`.
- Cada página trae una política de contenido (CSP) que solo deja correr los scripts del propio sitio.
- Cada aviso solo puede enlazar a los dominios de su fuente (por ejemplo, `cnfl.go.cr` para la CNFL). Si una
  fuente cambia o la comprometen y empieza a enlazar a otro sitio, el aviso enlaza a la página oficial de esa fuente.
- Los recolectores limitan el tamaño de lo que bajan y la cantidad de alertas por fuente, y no publican
  si una fuente devuelve datos incompletos.
- Los workflows corren con permisos de solo lectura. Solo el paso que publica en la rama `datos`, y solo
  desde `main`, puede escribir. Las acciones de GitHub están fijas a un commit exacto.
- El texto de las páginas que va a los datos estructurados para Google (JSON-LD) no puede cerrar la etiqueta
  `<script>`, aunque una guía traiga `</script>` en el título.

## Si nadie mantiene el sitio

El proyecto puede quedar años sin que nadie lo revise. Está pensado para fallar sin hacer daño:

- **Si los datos dejan de actualizarse** (GitHub atrasa los workflows programados, y los apaga en repos sin
  actividad por 60 días), la página de alertas esconde las alertas que ya terminaron y avisa que la lista
  puede estar vieja. La de buses avisa si las tarifas tienen más de un mes.
- **Si una fuente cambia de formato o se cae**, su recolector falla, se conservan las alertas anteriores
  (que se esconden solas al vencer) y la lista de fuentes la marca con ❌.
- **Si nadie revisa los PRs de Dependabot**, las acciones siguen fijas al commit que ya se revisó: nada cambia
  solo. Antes de mergear uno, mirá que venga de `dependabot[bot]` y que solo cambie el SHA y el comentario de versión.
- **GitHub Pages no deja poner encabezados HTTP**, así que la protección contra que otro sitio meta estas
  páginas en un marco (`frame-ancestors`) no se puede activar. El sitio no tiene botones que hagan acciones
  ni datos de nadie, así que el riesgo es bajo.

Si retomás el proyecto, revisá primero que los workflows de **Actions** estén encendidos y en verde.
