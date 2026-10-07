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
        self.assertEqual(r[0]["titulo"], "Sismo sentido en Coronado")
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


if __name__ == "__main__":
    unittest.main()
