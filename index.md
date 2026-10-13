---
title: Ventanilla Abierta
layout: default
description: Guías claras y gratuitas para hacer trámites en Costa Rica, con fuentes oficiales. Sin fila.
---
# Trámites de Costa Rica, explicados claro

Guías gratis, sin anuncios y con fuentes oficiales. Sin fila.

> 🚨 **¿Estás en peligro ahora?** Llamá al **9-1-1**.

{% include buscador.html %}

## Lo que más busca la gente

<ul class="situaciones">
{%- for s in site.data.portada.situaciones %}
  <li><a href="{{ '/tramites/costa-rica/' | append: s.url | relative_url }}"><span aria-hidden="true">{{ s.icono }}</span> {{ s.texto }}</a></li>
{%- endfor %}
</ul>

## Todos los temas

{% include tarjetas.html %}

## También

- **[Alertas](alertas/)**: cortes de luz programados, avisos del clima y sismos, con enlace al aviso oficial.
- **[Buses](buses/)**: cuánto cuesta cada ruta según la ARESEP, y dónde ver los horarios.
- **[Qué es Ventanilla Abierta](acerca.html)**: quién lo hace, cómo verificamos los datos y cómo ayudar.
