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
- Los recolectores limitan el tamaño de lo que bajan y la cantidad de alertas por fuente, y no publican
  si una fuente devuelve datos incompletos.
- Los workflows corren con permisos de solo lectura. Solo el paso que publica en la rama `datos`, y solo
  desde `main`, puede escribir. Las acciones de GitHub están fijas a un commit exacto.
