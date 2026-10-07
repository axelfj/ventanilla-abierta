#!/usr/bin/env python3
"""Recolector de tarifas de autobús de Ventanilla Abierta (fase 2).

Uso: python3 scripts/recolectores/tarifas_bus.py SALIDA_DIR

Baja el pliego tarifario de autobús que la ARESEP publica como dato abierto
(ver docs/decisiones/0002-fuentes-de-buses.md) y escribe SALIDA_DIR/tarifas.json,
más compacto, para el buscador de /buses/. Solo usa la biblioteca estándar.
"""
import datetime as dt
import json
import os
import sys
import urllib.request

FUENTE = "https://datos.aresep.go.cr/ws.datosabiertos/Services/IT/PliegoTarifario.svc/ObtenerPliegoTarifarioAutobus/0"
FICHA = "https://aresep.go.cr/datos-abiertos/tarifas-autobus/"
AGENTE = "VentanillaAbierta/1.0 (+https://github.com/axelfj/ventanilla-abierta)"


def bajar(url, tiempo=120):
    pedido = urllib.request.Request(url, headers={"User-Agent": AGENTE, "Accept": "application/json"})
    with urllib.request.urlopen(pedido, timeout=tiempo) as r:
        return r.read()


def texto(valor):
    return " ".join((valor or "").split())


def numero(valor):
    try:
        return round(float(valor), 2)
    except (TypeError, ValueError):
        return None


def fecha(valor):
    return (valor or "")[:10] or None


def operadores(valor):
    """"3-101-065720:AUTOTRANSPORTES CESMAG, S.A./3-101-...:OTRA" -> ["AUTOTRANSPORTES CESMAG, S.A.", "OTRA"]."""
    nombres = []
    for parte in (valor or "").split("/"):
        nombre = texto(parte.split(":", 1)[-1])
        if nombre and nombre not in nombres:
            nombres.append(nombre)
    return nombres


def normalizar(datos):
    """Convierte la respuesta de la ARESEP en una lista de tramos con su tarifa y su resolución."""
    respuesta = json.loads(datos)
    if not respuesta.get("metadata", {}).get("success", True):
        raise ValueError(f"la ARESEP respondió sin éxito: {respuesta.get('metadata')}")
    tramos = []
    for r in respuesta.get("value") or []:
        if not r.get("codigoRuta"):
            continue
        tramos.append({
            "ruta": texto(r.get("codigoRuta")),
            "nombre": texto(r.get("nombreRuta")),
            "ramal": texto(r.get("nombreRamal")),
            "tramo": texto(r.get("nombreFraccionamiento")),
            "km": numero(r.get("promedioKmViaje")),
            "tarifa": numero(r.get("tarifaRegular")),
            "adulto_mayor": numero(r.get("tarifaAdultoMayor")),
            "resolucion": texto(r.get("resolucion")),
            "gaceta": texto(r.get("gaceta")),
            "fecha_gaceta": fecha(r.get("fechaGaceta")),
            "vigente_desde": fecha(r.get("fechaVigencia")),
            "operadores": operadores(r.get("operadores")),
        })
    if not tramos:
        raise ValueError("la respuesta de la ARESEP no trajo tarifas")
    tramos.sort(key=lambda t: (t["ruta"], t["ramal"], t["tramo"]))
    return tramos


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    salida = sys.argv[1]
    ahora = dt.datetime.now(dt.timezone.utc).replace(microsecond=0)
    tramos = normalizar(bajar(FUENTE))
    os.makedirs(salida, exist_ok=True)
    with open(os.path.join(salida, "tarifas.json"), "w", encoding="utf-8") as f:
        json.dump({
            "fuente": {"institucion": "ARESEP", "url": FICHA, "datos": FUENTE,
                       "recuperado": ahora.strftime("%Y-%m-%dT%H:%M:%SZ")},
            "tramos": tramos,
        }, f, ensure_ascii=False, separators=(",", ":"))
    rutas = len({t["ruta"] for t in tramos})
    resumen = f"ARESEP: {len(tramos)} tramos de {rutas} rutas. Ejemplo: {tramos[0]['ruta']} {tramos[0]['nombre']}, ₡{tramos[0]['tarifa']}"
    print(resumen)
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as f:
            f.write(f"### Tarifas de autobús\n\n{resumen}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
