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


if __name__ == "__main__":
    unittest.main()
