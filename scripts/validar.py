#!/usr/bin/env python3
"""Valida las guías y el índice de categorías de Ventanilla Abierta.

Uso: python3 scripts/validar.py   (desde la raíz del repo; necesita pyyaml)

Revisa que cada guía tenga los datos mínimos (título, país, estado, fecha de
verificación y fuentes) y que _data/categorias.yml apunte a guías que existen.
Sale con código 1 si encuentra errores. En GitHub Actions, los errores aparecen
como anotaciones en el pull request.
"""
import datetime
import os
import re
import sys

import yaml

RAIZ = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
TRAMITES = os.path.join("tramites", "costa-rica")
CATEGORIAS = os.path.join("_data", "categorias.yml")
ESTADOS = {"borrador", "verificado"}
OBLIGATORIOS = ["title", "pais", "ultima_verificacion", "estado"]
EN_ACTIONS = os.environ.get("GITHUB_ACTIONS") == "true"

errores = 0


def error(archivo, mensaje):
    global errores
    errores += 1
    if EN_ACTIONS:
        print(f"::error file={archivo}::{mensaje}")
    else:
        print(f"ERROR  {archivo}: {mensaje}")


def leer_ficha(ruta):
    """Devuelve (front matter, cuerpo) o (None, None) si no tiene front matter."""
    with open(os.path.join(RAIZ, ruta), encoding="utf-8") as f:
        texto = f.read()
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", texto, re.S)
    if not m:
        return None, None
    return yaml.safe_load(m.group(1)) or {}, m.group(2)


def fichas():
    for carpeta, _, archivos in os.walk(os.path.join(RAIZ, TRAMITES)):
        rel = os.path.relpath(carpeta, RAIZ)
        if os.path.basename(rel) == "categorias":
            continue
        for nombre in sorted(archivos):
            if nombre.endswith(".md") and nombre != "index.md":
                yield os.path.join(rel, nombre)


def validar_ficha(ruta, hoy):
    try:
        datos, cuerpo = leer_ficha(ruta)
    except yaml.YAMLError as e:
        error(ruta, f"el front matter no es YAML válido: {e}")
        return
    if datos is None:
        error(ruta, "falta el front matter (el bloque entre --- al inicio del archivo)")
        return

    for campo in OBLIGATORIOS:
        if not datos.get(campo):
            error(ruta, f"falta el campo '{campo}' en el front matter")

    estado = datos.get("estado")
    if estado and estado not in ESTADOS:
        error(ruta, f"'estado' debe ser 'borrador' o 'verificado', no '{estado}'")

    fecha = datos.get("ultima_verificacion")
    if fecha:
        if isinstance(fecha, str):
            try:
                fecha = datetime.date.fromisoformat(fecha)
            except ValueError:
                error(ruta, f"'ultima_verificacion' debe tener formato AAAA-MM-DD, no '{fecha}'")
                fecha = None
        if isinstance(fecha, datetime.date) and fecha > hoy:
            error(ruta, f"'ultima_verificacion' ({fecha}) está en el futuro")

    if "categoria" in datos:
        error(ruta, "quitá el campo 'categoria': las categorías de una guía se definen en _data/categorias.yml")

    fuentes = re.search(r"^## Fuentes\s*$(.*?)(?=^## |\Z)", cuerpo, re.S | re.M)
    if not fuentes:
        error(ruta, "falta la sección '## Fuentes'")
    elif not re.search(r"\]\(https?://", fuentes.group(1)):
        error(ruta, "la sección '## Fuentes' no tiene ningún enlace")


def validar_categorias(rutas_fichas):
    try:
        with open(os.path.join(RAIZ, CATEGORIAS), encoding="utf-8") as f:
            categorias = yaml.safe_load(f) or []
    except yaml.YAMLError as e:
        error(CATEGORIAS, f"no es YAML válido: {e}")
        return

    listadas = set()
    slugs = set()
    for c in categorias:
        slug = c.get("slug")
        if not slug:
            error(CATEGORIAS, f"una categoría no tiene 'slug': {c.get('nombre')}")
            continue
        if slug in slugs:
            error(CATEGORIAS, f"la categoría '{slug}' está repetida")
        slugs.add(slug)
        for campo in ("icono", "nombre", "desc"):
            if not c.get(campo):
                error(CATEGORIAS, f"la categoría '{slug}' no tiene '{campo}'")
        pagina = os.path.join(TRAMITES, "categorias", f"{slug}.md")
        if not os.path.exists(os.path.join(RAIZ, pagina)):
            error(CATEGORIAS, f"la categoría '{slug}' no tiene su página {pagina}")

        for t in c.get("temas") or []:
            if not t.get("titulo"):
                error(CATEGORIAS, f"un tema de '{slug}' no tiene 'titulo'")
            if "estado" in t:
                error(CATEGORIAS, f"quitá 'estado' de '{t.get('titulo')}': el sitio lo toma del front matter de la guía")
            url = t.get("url")
            if not url:
                continue  # tema planeado, todavía sin guía
            if not url.endswith(".html"):
                error(CATEGORIAS, f"la url '{url}' debe terminar en .html")
                continue
            ruta = os.path.join(TRAMITES, url[: -len(".html")] + ".md")
            if not os.path.exists(os.path.join(RAIZ, ruta)):
                error(CATEGORIAS, f"'{t.get('titulo')}' apunta a {ruta}, que no existe")
            listadas.add(ruta)

    for ruta in rutas_fichas:
        if ruta not in listadas:
            error(ruta, "la guía no está en ninguna categoría de _data/categorias.yml, así que nadie la encuentra en el sitio")


def main():
    hoy = datetime.date.today()
    rutas = list(fichas())
    for ruta in rutas:
        validar_ficha(ruta, hoy)
    validar_categorias(rutas)
    if errores:
        print(f"\n{errores} error(es) en {len(rutas)} guías.")
        sys.exit(1)
    print(f"Todo bien: {len(rutas)} guías revisadas.")


if __name__ == "__main__":
    main()
