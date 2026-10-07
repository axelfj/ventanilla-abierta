#!/usr/bin/env python3
"""Recolector de alertas de Ventanilla Abierta (fase 2).

Uso: python3 scripts/recolectores/alertas.py SALIDA_DIR [--anterior ARCHIVO]

Lee solo fuentes oficiales o abiertas que publican en un formato que una máquina
puede leer (ver docs/decisiones/0001-fuentes-de-alertas.md) y escribe:

  SALIDA_DIR/activas.json   las alertas vigentes, en el formato de docs/arquitectura.md §6.2
  SALIDA_DIR/estado.json    cómo le fue a cada fuente en esta corrida

Si una fuente falla, se conservan sus alertas de la corrida anterior (--anterior)
y estado.json lo dice. Solo usa la biblioteca estándar de Python.
"""
import argparse
import datetime as dt
import email.utils
import html
import html.parser
import json
import os
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET

AGENTE = "VentanillaAbierta/1.0 (+https://github.com/axelfj/ventanilla-abierta)"
UTC = dt.timezone.utc
CR = dt.timezone(dt.timedelta(hours=-6))  # Costa Rica no usa horario de verano

# Caja que contiene a Costa Rica (incluye un poco de Nicaragua y Panamá; se filtra por nombre).
CAJA_CR = {"minlatitude": 8.0, "maxlatitude": 11.3, "minlongitude": -86.0, "maxlongitude": -82.5}


def bajar(url, tiempo=30):
    pedido = urllib.request.Request(url, headers={"User-Agent": AGENTE})
    with urllib.request.urlopen(pedido, timeout=tiempo) as r:
        return r.read()


def iso(fecha):
    return fecha.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ") if fecha else None


def fecha_rss(texto):
    try:
        return email.utils.parsedate_to_datetime(texto.strip())
    except (TypeError, ValueError, AttributeError):
        return None


def fecha_iso(texto):
    try:
        return dt.datetime.fromisoformat(texto.strip().replace("Z", "+00:00"))
    except (AttributeError, ValueError):
        return None


def limpiar(texto_html, largo=400):
    texto = html.unescape(re.sub(r"<[^>]+>", " ", texto_html or ""))
    texto = re.sub(r"\s+", " ", texto).strip()
    return texto if len(texto) <= largo else texto[: largo - 1].rstrip() + "…"


def alerta(fuente, ident, tipo, titulo, url, ahora, descripcion="", inicio=None, fin=None,
           zona=None, severidad=None):
    return {
        "id": f"{fuente}-{ident}",
        "tipo": tipo,
        "titulo": titulo,
        "descripcion": descripcion,
        "inicio": iso(inicio),
        "fin": iso(fin),
        "severidad": severidad,
        "zona": zona or {"provincia": None, "canton": None, "distritos": [], "codigos": [], "geometria": None},
        "fuente": {"institucion": fuente, "url": url, "recuperado": iso(ahora)},
        "origen": "oficial",
        "actualizado": iso(ahora),
    }


# ---------------------------------------------------------------- Sismos: USGS

def url_usgs(ahora, dias=7):
    # Solo sismos fuertes: los sentidos de menor magnitud ya vienen de la RSN, que es la fuente oficial.
    desde = (ahora - dt.timedelta(days=dias)).strftime("%Y-%m-%d")
    q = "&".join(f"{k}={v}" for k, v in CAJA_CR.items())
    return f"https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&minmagnitude=4.5&starttime={desde}&{q}"


RUMBOS = {"N": "norte", "S": "sur", "E": "este", "W": "oeste", "NE": "noreste", "NW": "noroeste",
          "SE": "sureste", "SW": "suroeste", "NNE": "nornoreste", "ENE": "estenoreste", "ESE": "estesureste",
          "SSE": "sursureste", "SSW": "sursuroeste", "WSW": "oestesuroeste", "WNW": "oestenoroeste", "NNW": "nornoroeste"}


def lugar_en_espanol(lugar):
    """"12 km SSW of Jacó, Costa Rica" -> "12 km al sursuroeste de Jacó, Costa Rica"."""
    m = re.match(r"(\d+(?:\.\d+)? km) ([NSEW]{1,3}) of (.+)", lugar)
    if not m or m.group(2) not in RUMBOS:
        return lugar
    return f"{m.group(1)} al {RUMBOS[m.group(2)]} de {m.group(3)}"


def leer_usgs(datos, ahora):
    """Sismos de magnitud 4.5 o más con epicentro descrito en Costa Rica, últimos 7 días."""
    salida = []
    for f in json.loads(datos).get("features", []):
        p = f.get("properties", {})
        lugar = p.get("place") or ""
        if "Costa Rica" not in lugar:
            continue
        cuando = dt.datetime.fromtimestamp(p["time"] / 1000, UTC)
        lon, lat, prof = (f.get("geometry") or {}).get("coordinates", [None, None, None])[:3]
        salida.append(alerta(
            "usgs", f.get("id"), "sismo",
            f"Sismo de magnitud {p.get('mag'):.1f}, {lugar_en_espanol(lugar)}",
            p.get("url"), ahora,
            descripcion=f"Profundidad: {prof:.0f} km. Dato preliminar del USGS; en Costa Rica el dato oficial lo da la RSN o el OVSICORI." if prof is not None else "",
            inicio=cuando,
            zona={"provincia": None, "canton": None, "distritos": [], "codigos": [],
                  "geometria": {"type": "Point", "coordinates": [lon, lat]}},
        ))
    return salida


# --------------------------------------- Sismos sentidos: RSN (UCR e ICE)

RSS_RSN = "https://rsn.ucr.ac.cr/actividad-sismica/ultimos-sismos?format=feed&type=rss"


def leer_rsn(datos, ahora, dias=7):
    """Sismos sentidos que la Red Sismológica Nacional ya revisó, publicados en los últimos días."""
    salida = []
    for i in ET.fromstring(datos).iter("item"):
        publicado = fecha_rss(i.findtext("pubDate") or "")
        if publicado and publicado < ahora - dt.timedelta(days=dias):
            continue
        url = (i.findtext("link") or "").strip()
        titulo = (i.findtext("title") or "Sismo sentido").strip()
        # "SISMO, 06 de octubre del 2026, 4:12 pm., Mag: 3,1 Mw, SENTIDO" -> "Sismo sentido de magnitud 3,1 Mw, 06 de octubre del 2026, 4:12 pm"
        m = re.match(r"SISMO,\s*(?P<cuando>.+?)\.?,\s*Mag:\s*(?P<mag>[\d,.]+\s*\w*)", titulo, re.I)
        if m:
            sentido = "sentido " if "SENTIDO" in titulo.upper() else ""
            titulo = f"Sismo {sentido}de magnitud {m['mag']}, {m['cuando']}"
        salida.append(alerta(
            "rsn", re.sub(r"\W+", "-", (i.findtext("guid") or url).rsplit("/", 1)[-1])[:80], "sismo",
            titulo, url, ahora, descripcion=limpiar(i.findtext("description")), inicio=publicado,
        ))
    return salida


# ---------------------------------------------- Clima: avisos CAP del IMN (WMO)

# El IMN publica sus avisos en CAP 1.2; la OMM los aloja en este feed (el sitio del IMN no tiene RSS que sirva).
RSS_IMN = "https://cap-sources.s3.amazonaws.com/cr-imn-es/rss.xml"
CAP = "{urn:oasis:names:tc:emergency:cap:1.2}"
SEVERIDAD = {"Extreme": "extrema", "Severe": "alta", "Moderate": "moderada", "Minor": "baja"}


def enlaces_rss(datos):
    raiz = ET.fromstring(datos)
    return [(i.findtext("link") or "").strip() for i in raiz.iter("item") if i.findtext("link")]


def leer_cap(datos, url, ahora):
    """Un aviso CAP 1.2. Devuelve [] si ya venció o es una cancelación."""
    raiz = ET.fromstring(datos)
    if raiz.findtext(f"{CAP}msgType") == "Cancel":
        return []
    infos = raiz.findall(f"{CAP}info")
    info = next((i for i in infos if (i.findtext(f"{CAP}language") or "").startswith("es")), infos[0] if infos else None)
    if info is None:
        return []
    fin = fecha_iso(info.findtext(f"{CAP}expires") or "")
    if fin and fin < ahora:
        return []
    zonas = [a.findtext(f"{CAP}areaDesc") for a in info.findall(f"{CAP}area")]
    titulo = info.findtext(f"{CAP}headline") or info.findtext(f"{CAP}event") or "Aviso meteorológico"
    descripcion = " ".join(t for t in [info.findtext(f"{CAP}description"), info.findtext(f"{CAP}instruction")] if t)
    if zonas:
        descripcion = f"Zonas: {', '.join(z for z in zonas if z)}. {descripcion}"
    return [alerta(
        "imn", raiz.findtext(f"{CAP}identifier") or url, "clima", titulo.strip(),
        info.findtext(f"{CAP}web") or url, ahora,
        descripcion=limpiar(descripcion, 600),
        inicio=fecha_iso(info.findtext(f"{CAP}onset") or info.findtext(f"{CAP}effective") or raiz.findtext(f"{CAP}sent") or ""),
        fin=fin,
        severidad=SEVERIDAD.get(info.findtext(f"{CAP}severity")),
    )]


def recolectar_imn(ahora):
    salida = []
    for url in enlaces_rss(bajar(RSS_IMN)):
        salida += leer_cap(bajar(url), url, ahora)
    return salida


# ---------------------------------------------------- Desastres: GDACS (ONU/UE)

RSS_GDACS = "https://www.gdacs.org/xml/rss.xml"
GDACS = "{http://www.gdacs.org}"
TIPO_GDACS = {"EQ": "sismo", "TC": "clima", "FL": "clima", "DR": "clima", "VO": "volcan", "WF": "otro"}
EVENTO_GDACS = {"EQ": "Sismo", "TC": "Ciclón tropical", "FL": "Inundación", "DR": "Sequía", "VO": "Erupción volcánica",
                "WF": "Incendio forestal"}
NIVEL_GDACS = {"Red": "alta", "Orange": "moderada", "Green": "baja"}
COLOR_GDACS = {"Red": "roja", "Orange": "naranja", "Green": "verde"}


def leer_gdacs(datos, ahora):
    salida = []
    for i in ET.fromstring(datos).iter("item"):
        paises = (i.findtext(f"{GDACS}iso3") or "") + " " + (i.findtext(f"{GDACS}country") or "")
        if "CRI" not in paises and "Costa Rica" not in paises:
            continue
        hasta = fecha_rss(i.findtext(f"{GDACS}todate") or "")
        if hasta and hasta < ahora - dt.timedelta(days=3):
            continue
        tipo, nivel = i.findtext(f"{GDACS}eventtype"), i.findtext(f"{GDACS}alertlevel")
        # GDACS publica en inglés; el título se arma en español y el detalle queda en su sitio.
        titulo = f"{EVENTO_GDACS.get(tipo, 'Desastre')} que incluye a Costa Rica"
        if nivel in COLOR_GDACS:
            titulo += f" (alerta {COLOR_GDACS[nivel]} de GDACS)"
        salida.append(alerta(
            "gdacs", (tipo or "") + (i.findtext(f"{GDACS}eventid") or i.findtext("guid") or ""),
            TIPO_GDACS.get(tipo, "otro"), titulo, (i.findtext("link") or "").strip(), ahora,
            descripcion="Resumen internacional de la ONU y la Unión Europea, en inglés: " + limpiar(i.findtext("title"), 200),
            inicio=fecha_rss(i.findtext(f"{GDACS}fromdate") or ""), fin=hasta,
            severidad=NIVEL_GDACS.get(i.findtext(f"{GDACS}alertlevel")),
        ))
    return salida


# ----------------------------------------- Luz: CNFL (Gran Área Metropolitana)

URL_CNFL = "https://www.cnfl.go.cr/servicios/autogestion/suspensiones"
MESES = {m: n for n, m in enumerate(["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto",
                                     "septiembre", "octubre", "noviembre", "diciembre"], 1)}
MESES["setiembre"] = 9
FECHA_CNFL = re.compile(r"^(?P<lugar>.*?)\s+(?P<dia>\d{1,2}) de (?P<mes>\w+) del (?P<anio>\d{4})\s+"
                        r"(?P<desde>\d{1,2}:\d{2}\s*[AP]M)\s*-\s*(?P<hasta>\d{1,2}:\d{2}\s*[AP]M)", re.I)


class Celdas(html.parser.HTMLParser):
    """Junta el texto de cada celda de cada fila de las tablas de una página."""

    def __init__(self):
        super().__init__()
        self.filas, self.celda = [], None

    def handle_starttag(self, tag, attrs):
        if tag == "tr":
            self.filas.append([])
        elif tag in ("td", "th") and self.filas:
            self.celda = []

    def handle_endtag(self, tag):
        if tag in ("td", "th") and self.celda is not None:
            self.filas[-1].append(re.sub(r"\s+", " ", "".join(self.celda)).strip())
            self.celda = None

    def handle_data(self, data):
        if self.celda is not None:
            self.celda.append(data)


def hora_cnfl(dia, mes, anio, hora):
    h = dt.datetime.strptime(re.sub(r"\s+", " ", hora.upper()), "%I:%M %p")
    return dt.datetime(int(anio), MESES[mes.lower()], int(dia), h.hour, h.minute, tzinfo=CR)


def nombre_propio(texto):
    return " ".join(p if p in ("de", "del", "la", "las", "los", "y") else p.capitalize() for p in texto.lower().split())


def leer_cnfl(datos, ahora):
    """Suspensiones programadas de la tabla de la CNFL que todavía no terminaron."""
    lector = Celdas()
    lector.feed(datos.decode("utf-8", "replace"))
    salida = []
    for fila in lector.filas:
        m = FECHA_CNFL.match(fila[0]) if fila else None
        if not m or m.group("mes").lower() not in MESES or "cancelad" in " ".join(fila).lower():
            continue
        inicio = hora_cnfl(m["dia"], m["mes"], m["anio"], m["desde"])
        fin = hora_cnfl(m["dia"], m["mes"], m["anio"], m["hasta"])
        if fin < ahora:
            continue
        partes = [nombre_propio(re.sub(r"\s*\(", " (", p).strip()) for p in m["lugar"].split(",")]
        detalle = fila[1] if len(fila) > 1 else ""
        numero = re.search(r"N[úu]mero de Suspensi[óo]n:\s*([\w-]+)", detalle)
        trabajo = detalle.replace(m["lugar"], "").split("Número de")[0].strip(" .")
        salida.append(alerta(
            "cnfl", numero.group(1) if numero else f"{inicio:%Y%m%d%H%M}-{partes[-1]}", "luz",
            "Corte de luz programado: " + ", ".join(reversed(partes)), URL_CNFL, ahora,
            descripcion=(trabajo.capitalize() + "." if trabajo else "") +
                        (f" Número de suspensión: {numero.group(1)}." if numero else ""),
            inicio=inicio, fin=fin,
            zona={"provincia": partes[0], "canton": partes[1] if len(partes) > 1 else None,
                  "distritos": partes[2:3], "codigos": [], "geometria": None},
        ))
    return salida


# ------------------------------------------------------- Luz: JASEC (Cartago)

RSS_JASEC = "https://www.jasec.go.cr/index.php/noticias?format=feed&type=rss"
PALABRAS_CORTE = re.compile(r"interrupci|suspensi|corte", re.I)


def leer_jasec(datos, ahora, dias=10):
    """Noticias de JASEC que anuncian interrupciones, publicadas en los últimos días."""
    salida = []
    for i in ET.fromstring(datos).iter("item"):
        titulo = (i.findtext("title") or "").strip()
        if not PALABRAS_CORTE.search(titulo):
            continue
        publicado = fecha_rss(i.findtext("pubDate") or "")
        if publicado and publicado < ahora - dt.timedelta(days=dias):
            continue
        url = (i.findtext("link") or "").strip()
        salida.append(alerta(
            "jasec", re.sub(r"\W+", "-", url.rsplit("/", 1)[-1])[:80] or titulo, "luz", titulo, url, ahora,
            descripcion=limpiar(i.findtext("description")),
            inicio=publicado,
            zona={"provincia": "Cartago", "canton": None, "distritos": [], "codigos": [], "geometria": None},
        ))
    return salida


# --------------------------------------------------------------------- Corrida

FUENTES = {
    "imn": recolectar_imn,
    "rsn": lambda ahora: leer_rsn(bajar(RSS_RSN), ahora),
    "usgs": lambda ahora: leer_usgs(bajar(url_usgs(ahora)), ahora),
    "gdacs": lambda ahora: leer_gdacs(bajar(RSS_GDACS), ahora),
    "cnfl": lambda ahora: leer_cnfl(bajar(URL_CNFL), ahora),
    # Desde los servidores de GitHub no siempre responde; se intenta igual, sin esperar mucho.
    "jasec": lambda ahora: leer_jasec(bajar(RSS_JASEC, tiempo=15), ahora),
}


def correr(anteriores, ahora, fuentes=FUENTES):
    alertas, estado = [], {}
    for nombre, recolectar in fuentes.items():
        try:
            nuevas = recolectar(ahora)
            estado[nombre] = {"ok": True, "alertas": len(nuevas), "revisado": iso(ahora)}
        except Exception as e:  # una fuente caída no tumba a las demás
            nuevas = [a for a in anteriores if a["fuente"]["institucion"] == nombre
                      and not (a.get("fin") and a["fin"] < iso(ahora))]
            estado[nombre] = {"ok": False, "alertas": len(nuevas), "revisado": iso(ahora),
                              "error": f"{type(e).__name__}: {e}"[:200]}
            print(f"::warning::{nombre}: {e}", file=sys.stderr)
        alertas += nuevas
    alertas.sort(key=lambda a: a["inicio"] or "", reverse=True)
    return alertas, estado


def main():
    p = argparse.ArgumentParser()
    p.add_argument("salida")
    p.add_argument("--anterior")
    args = p.parse_args()
    anteriores = []
    if args.anterior and os.path.exists(args.anterior):
        try:
            with open(args.anterior, encoding="utf-8") as f:
                anteriores = json.load(f).get("alertas", [])
        except ValueError:
            print("::warning::no se pudo leer el archivo de alertas anteriores", file=sys.stderr)
    ahora = dt.datetime.now(UTC).replace(microsecond=0)
    alertas, estado = correr(anteriores, ahora)
    os.makedirs(args.salida, exist_ok=True)
    with open(os.path.join(args.salida, "activas.json"), "w", encoding="utf-8") as f:
        json.dump({"generado": iso(ahora), "alertas": alertas}, f, ensure_ascii=False, indent=1)
    with open(os.path.join(args.salida, "estado.json"), "w", encoding="utf-8") as f:
        json.dump({"generado": iso(ahora), "fuentes": estado}, f, ensure_ascii=False, indent=1)
    resumen = [f"- {n}: {'ok' if e['ok'] else 'falló'}, {e['alertas']} alertas {e.get('error', '')}" for n, e in estado.items()]
    resumen += [f"  - {a['tipo']}: {a['titulo']}" for a in alertas]
    print("\n".join(resumen))
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as f:
            f.write("### Alertas recolectadas\n\n" + "\n".join(resumen) + "\n")
    # Falla solo si no funcionó ninguna fuente, para enterarse por correo de GitHub.
    return 0 if any(e["ok"] for e in estado.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
