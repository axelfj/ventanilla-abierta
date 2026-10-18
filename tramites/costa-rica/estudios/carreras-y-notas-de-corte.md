---
title: "Carreras de las universidades públicas y sus notas de corte"
pais: Costa Rica
ultima_verificacion: 2026-10-18
estado: borrador
---

# Carreras de las universidades públicas y sus notas de corte

> ⚠️ Esta guía es información general, no asesoría legal. Las notas de corte cambian cada año: verificá siempre con la universidad.
> **Última verificación:** 2026-10-18. Los datos vienen de documentos oficiales de cada universidad (enlaces abajo).

## Qué es
Aquí están las carreras que ofrecen la UCR, el TEC, la UNA, la UNED y la UTN, y la **nota de corte** de cada carrera cuando la universidad la publica. La nota de corte es la nota de admisión de la **última persona que entró** a esa carrera en esa sede. No es una nota mínima fija: depende de cuántos cupos hay y de las notas de quienes concursan ese año. Para saber cómo se calcula tu nota y cómo se inscribe el examen, mirá [Cómo entrar a una universidad pública](admision-universidades-publicas.html).

Cómo leer la tabla:
- La nota de corte del año pasado sirve de referencia, no de garantía: si tu nota es menor, podés concursar igual, y conviene tener una segunda opción.
- **UCR:** los cortes son del **Ingreso 2025**, el documento oficial más reciente que pudimos abrir. Los del Ingreso 2026 se consultaban en un sistema de la UCR que ya cerró; la UCR solo publicó los diez más altos en [su sitio de noticias](https://www.ucr.ac.cr/noticias/2025/12/18/la-carrera-de-microbiologia-obtuvo-nuevamente-el-corte-de-admision-mas-alto-para-el-2026.html).
- **TEC:** cortes del **Ingreso 2026** (columna "admitido").
- **UNA:** no publica la nota de corte de cada carrera en un documento; aquí va solo la lista de carreras de la admisión 2026-2027.
- **UNED:** entrada abierta, sin examen ni nota de corte.
- **UTN:** no publica notas de corte; aquí va la lista de carreras.

## ¿Lo podés hacer solo?
- **Sí.** Consultar las carreras y los cortes es gratis y no necesitás a nadie.

## Buscá una carrera

<form class="buscador" role="search">
  <label for="q-carrera" class="oculto">Buscar una carrera o una sede</label>
  <input id="q-carrera" type="search" placeholder="Ej.: medicina, computación, Liberia" autocomplete="off" disabled>
</form>
<p id="carrera-resumen" class="migas" aria-live="polite"><noscript>El buscador necesita JavaScript. Podés abrir cada universidad abajo.</noscript></p>

{% for u in site.data.carreras.universidades %}
<details{% if forloop.first %} open{% endif %}>
<summary><strong>{{ u.nombre }} ({{ u.siglas }})</strong>: {{ u.carreras.size }} carreras{% if u.anio_notas and u.anio_notas != "" %}, notas de corte del {{ u.anio_notas }}{% endif %}</summary>
<p>{{ u.admision }}</p>
{% if u.nota %}<p class="migas">{{ u.nota }}</p>{% endif %}
<table class="carreras">
<thead><tr><th>Carrera</th>{% if u.carreras[0].sede %}<th>Sede</th>{% endif %}<th>Nota de corte</th></tr></thead>
<tbody>
{% for c in u.carreras %}<tr><td>{{ c.nombre }}</td>{% if u.carreras[0].sede %}<td>{{ c.sede }}</td>{% endif %}<td>{% if c.nota %}{{ c.nota }}{% else %}{% if u.id == "uned" %}Entrada abierta{% else %}No publicada{% endif %}{% endif %}</td></tr>
{% endfor %}</tbody>
</table>
<p class="migas">Fuente: <a href="{{ u.fuente_carreras }}" rel="noopener">lista oficial de carreras</a>{% if u.fuente_notas and u.fuente_notas != "" and u.fuente_notas != u.fuente_carreras %} · <a href="{{ u.fuente_notas }}" rel="noopener">notas de corte</a>{% endif %}. Revisado el {{ u.verificado | date: "%d/%m/%Y" }}.</p>
</details>
{% endfor %}

<script src="{{ '/assets/js/carreras.js' | relative_url }}" defer></script>

## Errores comunes
- Tomar la nota de corte como una nota mínima garantizada: cambia cada año.
- Comparar notas entre universidades: cada una calcula la nota de admisión distinto.
- Elegir una sola carrera muy disputada sin una segunda opción.
- Creer que la UNED o la UTN piden examen: no lo piden.

## Preguntas frecuentes
**¿Por qué una misma carrera tiene cortes distintos en cada sede?**
Porque cada sede tiene sus propios cupos y concursa otra gente.

**¿Dónde veo las carreras de las universidades privadas?**
En la consulta oficial del CONESUP. Ver [Cómo buscar una escuela, colegio o universidad](buscar-un-centro-educativo.html).

**Esta lista está vieja o le falta una carrera.**
Avisanos con el enlace oficial y la corregimos ([reportar](https://github.com/axelfj/ventanilla-abierta/issues/new?template=correccion.md)).

## Fuentes
- [UCR, Oficina de Registro e Información, cortes de ingreso a carrera ordinaria, primer ingreso 2025](https://ori.ucr.ac.cr/sites/default/files/2025-11/2025-cortes_ordinaria.pdf), consultado 2026-10-18.
- [UCR, "La carrera de Microbiología obtuvo nuevamente el corte de admisión más alto para el 2026"](https://www.ucr.ac.cr/noticias/2025/12/18/la-carrera-de-microbiologia-obtuvo-nuevamente-el-corte-de-admision-mas-alto-para-el-2026.html) (18-12-2025), consultada 2026-10-18.
- [TEC, notas de corte por carrera 2025-2026](https://www.tec.ac.cr/sites/default/files/media/doc/notas-de-corte-2025-2026-2.pdf), consultado 2026-10-18.
- [TEC, histórico de notas de corte de tres años](https://www.tec.ac.cr/sites/default/files/media/doc/notas-de-corte-2025-2026-historico-3-anos.pdf), consultado 2026-10-18.
- [UNA, oferta académica 2026-2027](https://www.registro.una.ac.cr/index.php/oferta-academica-y-acreditacion-2026-2027-faq/oferta-academica), consultada 2026-10-18.
- [UNA, notas de corte de años anteriores](https://www.registro.una.ac.cr/index.php/notas-de-corte-de-anos-anteriores), consultada 2026-10-18.
- [UNED, carreras](https://uned.ac.cr/oferta-educativa/carreras), consultada 2026-10-18.
- [UTN, carreras](https://www.utn.ac.cr/carreras), consultada 2026-10-18.

---
¿Encontraste un error? [Reportalo aquí](https://github.com/axelfj/ventanilla-abierta/issues/new?template=correccion.md).
