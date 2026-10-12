"""Pruebas del recolector de tarifas de autobús con una muestra guardada (sin internet)."""
import os
import sys
import unittest

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(AQUI))
import tarifas_bus  # noqa: E402


class Tarifas(unittest.TestCase):
    def test_normaliza_un_tramo(self):
        with open(os.path.join(AQUI, "muestras", "aresep.json"), "rb") as f:
            tramos = tarifas_bus.normalizar(f.read())
        self.assertEqual(len(tramos), 1)
        t = tramos[0]
        self.assertEqual(t["ruta"], "I-1")
        self.assertEqual(t["tarifa"], 350.0)
        self.assertEqual(t["km"], 13.15)
        self.assertEqual(t["vigente_desde"], "2026-09-04")
        self.assertEqual(t["fecha_gaceta"], "2026-09-02")
        self.assertEqual(t["operadores"], ["AUTOTRANSPORTES CESMAG, S.A.", "OTRA EMPRESA S.A."])

    def test_respuesta_vacia_es_error(self):
        with self.assertRaises(ValueError):
            tarifas_bus.normalizar(b'{"metadata":{"success":true},"value":[]}')

    def test_respuesta_incompleta_no_se_publica(self):
        with open(os.path.join(AQUI, "muestras", "aresep.json"), "rb") as f:
            tramos = tarifas_bus.normalizar(f.read())
        with self.assertRaises(ValueError):
            tarifas_bus.revisar(tramos)
        tarifas_bus.revisar(tramos * 2000)

    def test_tarifas_imposibles_quedan_sin_dato(self):
        for valor in ["-5", "nan", "inf", "1e12", "abc", None]:
            self.assertIsNone(tarifas_bus.numero(valor))
        self.assertEqual(tarifas_bus.numero("350"), 350.0)


if __name__ == "__main__":
    unittest.main()
