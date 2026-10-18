# Que el sitio salga en Google y Bing

El sitio ya trae lo técnico: `sitemap.xml`, título con "Costa Rica" en cada guía, descripción, enlace canónico,
idioma `es-CR`, Open Graph y datos estructurados (artículo con fecha de verificación y migas). Lo que falta lo
tiene que hacer la persona dueña del repositorio, una sola vez y gratis.

## 1. Google Search Console

1. Entrá a <https://search.google.com/search-console> con tu cuenta de Google.
2. "Agregar propiedad" → **Prefijo de URL** → `https://axelfj.github.io/ventanilla-abierta/`.
3. Método de verificación: **Etiqueta HTML**. Te da algo como
   `<meta name="google-site-verification" content="AbC123..." />`.
4. Copiá solo lo que está entre las comillas de `content` y pegalo en `_config.yml`:
   `google_site_verification: AbC123...`. Hacé commit en `main` y esperá a que GitHub Pages publique (un par de minutos).
5. Volvé a Search Console y tocá **Verificar**. No borres la línea después: Google la revisa de vez en cuando.
6. En el menú, **Sitemaps** → escribí `sitemap.xml` → Enviar.
7. En **Inspección de URLs**, pegá la portada y unas cuantas guías importantes y tocá "Solicitar indexación".

## 2. Bing (también alimenta a DuckDuckGo, Yahoo y a varios buscadores con IA)

1. Entrá a <https://www.bing.com/webmasters>.
2. Lo más fácil: **Importar desde Google Search Console** (trae el sitio y el sitemap ya verificados).
3. Si preferís verificar aparte: método **Meta tag**, copiá el código de `content` y pegalo en
   `_config.yml` como `bing_site_verification: ...`.

## Por qué no hay `robots.txt`

Los buscadores solo leen el `robots.txt` de la raíz del dominio (`axelfj.github.io/robots.txt`), no el de una
subcarpeta. Como el sitio vive en `/ventanilla-abierta/`, uno propio no serviría de nada. Por eso el sitemap se
envía a mano en el paso 1.6.

## Qué más ayuda (gratis)

- **Enlaces desde otros sitios.** Es lo que más pesa para un sitio nuevo: el campo "Website" del repositorio
  en GitHub, la bio de Instagram, y pedir a bibliotecas, consultorios jurídicos de universidades y asociaciones
  de desarrollo que enlacen las guías que les sirvan.
- **Compartir guías concretas** (no solo la portada) por WhatsApp e Instagram.
- **Revisar Search Console cada mes:** el informe "Rendimiento" dice qué busca la gente que llega. Si una
  búsqueda común no tiene guía, es candidata para la siguiente tanda.
