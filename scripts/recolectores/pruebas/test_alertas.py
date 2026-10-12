"""Pruebas del recolector de alertas con muestras guardadas (sin internet).

Uso: python3 -m unittest discover scripts/recolectores/pruebas
"""
import datetime as dt
import os
import sys
import unittest

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(AQUI))
import alertas  # noqa: E402

AHORA = dt.datetime(2026, 10, 7, 12, 0, tzinfo=dt.timezone.utc)


def muestra(nombre):
    with open(os.path.join(AQUI, "muestras", nombre), "rb") as f:
        return f.read()


class Usgs(unittest.TestCase):
    def test_solo_sismos_en_costa_rica(self):
        r = alertas.leer_usgs(muestra("usgs.json"), AHORA)
        self.assertEqual(len(r), 1)
        self.assertEqual(r[0]["titulo"], "Sismo de magnitud 3.5, 2 km al sur de Pocora, Costa Rica")
        self.assertEqual(r[0]["tipo"], "sismo")
        self.assertEqual(r[0]["inicio"], "2026-10-04T08:00:00Z")
        self.assertEqual(r[0]["zona"]["geometria"]["coordinates"], [-83.6, 10.15])

    def test_lugar_sin_formato_conocido_queda_igual(self):
        self.assertEqual(alertas.lugar_en_espanol("Costa Rica"), "Costa Rica")


class Imn(unittest.TestCase):
    def test_enlaces_del_rss(self):
        self.assertEqual(len(alertas.enlaces_rss(muestra("imn-rss.xml"))), 1)

    def test_aviso_cap_vigente(self):
        r = alertas.leer_cap(muestra("imn-cap.xml"), "https://x", AHORA)
        self.assertEqual(len(r), 1)
        a = r[0]
        self.assertEqual(a["titulo"], "Aviso amarillo por lluvias en el Pacífico")
        self.assertEqual(a["severidad"], "moderada")
        self.assertEqual(a["inicio"], "2026-10-07T18:00:00Z")
        self.assertEqual(a["fin"], "2026-10-09T00:00:00Z")
        self.assertIn("Pacífico Central, Pacífico Sur", a["descripcion"])
        self.assertEqual(a["fuente"]["url"], "https://www.imn.ac.cr/avisos")

    def test_aviso_vencido_se_descarta(self):
        despues = AHORA + dt.timedelta(days=5)
        self.assertEqual(alertas.leer_cap(muestra("imn-cap.xml"), "https://x", despues), [])


class Gdacs(unittest.TestCase):
    def test_solo_costa_rica(self):
        r = alertas.leer_gdacs(muestra("gdacs.xml"), AHORA)
        self.assertEqual(len(r), 1)
        self.assertEqual(r[0]["tipo"], "sismo")
        self.assertEqual(r[0]["severidad"], "baja")
        self.assertEqual(r[0]["titulo"], "Sismo que incluye a Costa Rica (alerta verde de GDACS)")


class Jasec(unittest.TestCase):
    def test_solo_cortes_recientes(self):
        r = alertas.leer_jasec(muestra("jasec.xml"), AHORA)
        self.assertEqual([a["titulo"] for a in r], ["Interrupción programada Pacayas 06/10/2026"])
        self.assertEqual(r[0]["descripcion"], "Se interrumpirá el servicio de 8:15 a 16:00.")
        self.assertEqual(r[0]["zona"]["provincia"], "Cartago")


class Rsn(unittest.TestCase):
    def test_sismos_sentidos_recientes(self):
        r = alertas.leer_rsn(muestra("rsn.xml"), AHORA)
        self.assertEqual(len(r), 1)
        self.assertEqual(r[0]["titulo"], "Sismo sentido de magnitud 3,1 Mw, 06 de octubre del 2026, 4:12 pm")
        self.assertIn("Ubicación: 7 km al noreste de Cascajal de Coronado", r[0]["descripcion"])
        self.assertEqual(r[0]["inicio"], "2026-10-06T22:38:00Z")


class Cnfl(unittest.TestCase):
    def test_suspensiones_que_no_terminaron(self):
        r = alertas.leer_cnfl(muestra("cnfl.html"), AHORA)
        # Pavas terminó el 6 de octubre y Escazú en setiembre; queda Barva (7 oct, 8 a. m. a 4 p. m.).
        self.assertEqual(len(r), 1)
        a = r[0]
        self.assertEqual(a["id"], "cnfl-6226-136-2026")
        self.assertEqual(a["titulo"], "Corte de luz programado: Residencial El Cipresal (parcial), San José de la Montaña, Barva, Heredia")
        self.assertEqual(a["inicio"], "2026-10-07T14:00:00Z")
        self.assertEqual(a["fin"], "2026-10-07T22:00:00Z")
        self.assertEqual(a["zona"]["provincia"], "Heredia")
        self.assertEqual(a["zona"]["canton"], "Barva")
        self.assertEqual(a["descripcion"], "Mantenimiento de obras eléctricas. Número de suspensión: 6226-136-2026.")

    def test_mes_setiembre(self):
        self.assertEqual(alertas.hora_cnfl("9", "Setiembre", "2026", "08:00 AM").month, 9)


class Corrida(unittest.TestCase):
    def test_fuente_caida_conserva_lo_anterior(self):
        vieja = alertas.alerta("jasec", "1", "luz", "Corte viejo", "https://x", AHORA)

        def falla(ahora):
            raise TimeoutError("sin respuesta")

        fuentes = {"jasec": falla, "usgs": lambda ahora: alertas.leer_usgs(muestra("usgs.json"), ahora)}
        r, estado = alertas.correr([vieja], AHORA, fuentes)
        self.assertEqual(len(r), 2)
        self.assertFalse(estado["jasec"]["ok"])
        self.assertIn("sin respuesta", estado["jasec"]["error"])
        self.assertTrue(estado["usgs"]["ok"])

    def test_fuente_con_demasiadas_alertas_se_recorta(self):
        muchas = [alertas.alerta("rsn", str(n), "sismo", "Sismo", "https://x", AHORA) for n in range(500)]
        r, estado = alertas.correr([], AHORA, {"rsn": lambda ahora: muchas})
        self.assertEqual(len(r), alertas.MAX_POR_FUENTE)


class Seguridad(unittest.TestCase):
    """Lo que viene de afuera se guarda como texto y solo con enlaces web normales."""

    def test_enlace_peligroso_se_cambia_por_la_pagina_de_la_fuente(self):
        for url in ["javascript:alert(1)", " JavaScript:alert(1)", "data:text/html,hola", "file:///etc/passwd", "", None]:
            a = alertas.alerta("jasec", "1", "luz", "Corte", url, AHORA)
            self.assertEqual(a["fuente"]["url"], alertas.PAGINAS["jasec"])

    def test_enlace_web_se_conserva(self):
        a = alertas.alerta("jasec", "1", "luz", "Corte", " https://www.jasec.go.cr/aviso ", AHORA)
        self.assertEqual(a["fuente"]["url"], "https://www.jasec.go.cr/aviso")

    def test_titulo_sin_etiquetas_y_con_largo_maximo(self):
        a = alertas.alerta("rsn", "1", "sismo", "<img src=x onerror=alert(1)>Sismo " + "x" * 500, "https://x", AHORA)
        self.assertNotIn("<img", a["titulo"])
        self.assertLessEqual(len(a["titulo"]), 200)

    def test_no_baja_direcciones_que_no_son_web(self):
        with self.assertRaises(ValueError):
            alertas.bajar("file:///etc/passwd")

    def test_rss_con_enlaces_raros(self):
        rss = (b'<rss><channel><item><title>Interrupcion del servicio</title>'
               b'<link>javascript:alert(1)</link><pubDate>Tue, 06 Oct 2026 10:00:00 GMT</pubDate></item></channel></rss>')
        r = alertas.leer_jasec(rss, AHORA)
        self.assertEqual(r[0]["fuente"]["url"], alertas.PAGINAS["jasec"])


if __name__ == "__main__":
    unittest.main()
