from datetime import date
from decimal import Decimal

from django.test import TestCase
from django.db import connection

from core.services.vna.vna import calcular_vna


class VNATestCase(TestCase):
    databases = {"default"}

    def test_vna_2026_03_09(self):
        resultado = calcular_vna(
            connection,
            id_indice=5,
            data_inicio_rentabilidade=date(2023, 11, 6),
            data_vna=date(2026, 3, 9),
            vne=Decimal("1000"),
            detalhar=True,
        )
        self.assertEqual(str(resultado.vna), "1111.84703223")

    def test_vna_2026_02_18(self):
        resultado = calcular_vna(
            connection,
            id_indice=5,
            data_inicio_rentabilidade=date(2023, 11, 6),
            data_vna=date(2026, 2, 18),
            vne=Decimal("1000"),
            detalhar=True,
        )
        self.assertEqual(str(resultado.vna), "1106.73571719")