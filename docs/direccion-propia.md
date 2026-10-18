---
title: Una dirección propia sin comprar dominio
---

# Una dirección propia sin comprar dominio

Hoy el sitio vive en `axelfj.github.io/ventanilla-abierta`. Se puede dejar en una dirección más corta y con
nombre propio **sin pagar nada**. Lo tiene que hacer la persona dueña del repositorio, porque son ajustes de
la cuenta de GitHub.

## Opción recomendada: `ventanilla-abierta.github.io`

GitHub da gratis una dirección `NOMBRE.github.io` a cada cuenta y a cada organización. Si el sitio se pasa a
una organización gratuita llamada, por ejemplo, `ventanilla-abierta`, queda en
**`https://ventanilla-abierta.github.io/`**, sin la subcarpeta. Además, el proyecto deja de depender de una
cuenta personal, y se pueden sumar más personas a la organización.

1. **Crear la organización.** En GitHub: tu foto → *Your organizations* → *New organization* → plan **Free**.
   Nombre: `ventanilla-abierta` (o el que esté libre; ese nombre es la dirección).
2. **Pasar el repositorio.** En `axelfj/ventanilla-abierta` → *Settings* → *General* → al final,
   *Transfer ownership* → a la organización nueva. GitHub redirige los enlaces viejos del repositorio
   (issues, clones) automáticamente.
3. **Renombrarlo.** Ya en la organización, *Settings* → *General* → *Repository name* →
   `ventanilla-abierta.github.io` (tiene que ser exactamente `NOMBRE-DE-LA-ORGANIZACIÓN.github.io`).
4. **Revisar Pages.** *Settings* → *Pages*: fuente *Deploy from a branch*, rama `main`, carpeta `/ (root)`.
   Marcá *Enforce HTTPS*. En unos minutos el sitio sale en la dirección nueva.
5. **Revisar Actions.** En la pestaña *Actions*, si aparece un aviso, activá los workflows. Las alertas y las
   tarifas de bus siguen funcionando solas: las páginas leen la rama `datos` del repositorio donde estén
   publicadas (`site.github.repository_nwo`), así que no hay que cambiar código.
6. **Actualizar dónde aparece la dirección:** el campo *Website* del repositorio, la bio de Instagram y
   Search Console (agregá la propiedad nueva; ver [indexacion.md](indexacion.md)). Con la dirección en la raíz,
   ahora sí se puede agregar un `robots.txt`.

Todos los enlaces internos del sitio usan `relative_url`, así que funcionan igual sin la subcarpeta.

**Lo que se pierde:** la dirección vieja `axelfj.github.io/ventanilla-abierta/...` deja de abrir (GitHub no
redirige las páginas de Pages al pasar un repositorio). Si ya se compartieron enlaces, se puede crear de nuevo
un repositorio `axelfj/ventanilla-abierta` con Pages activo y solo un `404.html` que mande a la dirección nueva:

```html
<!DOCTYPE html>
<meta charset="utf-8">
<title>Ventanilla Abierta se mudó</title>
<script>
  location.replace("https://ventanilla-abierta.github.io" + location.pathname.replace(/^\/ventanilla-abierta/, "") + location.search + location.hash);
</script>
<p>Nos mudamos a <a href="https://ventanilla-abierta.github.io/">ventanilla-abierta.github.io</a>.</p>
```

(Hacelo después del paso 2, porque crear un repositorio con el nombre viejo apaga la redirección de GitHub
para clones e issues. Quien tenga el repositorio clonado solo tiene que cambiar el `remote`.)

## Otras opciones gratis (más lentas o con condiciones)

| Opción | Dirección | Costo | Lo malo |
|---|---|---|---|
| Organización de GitHub (arriba) | `ventanilla-abierta.github.io` | ₡0 | Sigue diciendo "github.io" |
| Dominio gratuito de [EU.org](https://nic.eu.org/) | `ventanilla-abierta.eu.org` | ₡0 | La aprobación puede tardar semanas o meses, y hay que manejar el DNS en otro servicio gratuito |
| Dominio `.cr` o `.com` | `ventanillaabierta.cr` | Pago anual | No cumple con "costo cero" |

Si un día se usa un dominio propio, se pone en *Settings* → *Pages* → *Custom domain*; GitHub da el HTTPS gratis.

No se recomiendan subdominios "gratis" de servicios pensados para otra cosa (por ejemplo, los de proyectos de
JavaScript o de portafolios personales): sus reglas no cubren un sitio como este y pueden quitarlo.
