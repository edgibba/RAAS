import csv
from datetime import date
from decimal import Decimal
from pathlib import Path

from django.test import TestCase
from django.db import connection

from core.services.vna.vna import calcular_vna

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"


class VNATestCase(TestCase):
    databases = {"default"}

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._criar_tabelas()
        cls._carregar_dados()

    @classmethod
    def tearDownClass(cls):
        cls._remover_tabelas()
        super().tearDownClass()

    @classmethod
    def _criar_tabelas(cls):
        with connection.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS Indices (
                    idIndice SERIAL PRIMARY KEY,
                    nome VARCHAR(100) NOT NULL UNIQUE,
                    Periodicidade VARCHAR(20) NOT NULL
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS IndicesMensaisTempo (
                    id SERIAL PRIMARY KEY,
                    idIndice INTEGER NOT NULL REFERENCES Indices(idIndice),
                    nAno INTEGER NOT NULL,
                    nMes INTEGER NOT NULL,
                    dtDivulgacao DATE,
                    NI NUMERIC(30, 15),
                    bReal BOOLEAN NOT NULL,
                    UNIQUE (idIndice, nAno, nMes, bReal)
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS Calendario (
                    dtBase DATE PRIMARY KEY,
                    bUtil BOOLEAN NOT NULL
                )
            """)

    @classmethod
    def _carregar_dados(cls):
        arq_cal = DATA_DIR / "calendario.csv"
        arq_idx = DATA_DIR / "indices_mensais.csv"

        with connection.cursor() as cur:
            # Insere IPCA com idIndice=5 explícito para corresponder aos testes
            cur.execute("""
                INSERT INTO Indices (idIndice, nome, Periodicidade)
                VALUES (5, 'IPCA', 'MENSAL')
                ON CONFLICT DO NOTHING
            """)

            with arq_cal.open("r", encoding="utf-8-sig", newline="") as f:
                reader = csv.DictReader(f)
                cal_rows = [
                    (row["dtBase"].strip(), row["bUtil"].strip() in ("1", "true", "t", "sim"))
                    for row in reader
                ]
            cur.executemany(
                "INSERT INTO Calendario (dtBase, bUtil) VALUES (%s, %s) ON CONFLICT DO NOTHING",
                cal_rows,
            )

            with arq_idx.open("r", encoding="utf-8-sig", newline="") as f:
                reader = csv.DictReader(f)
                idx_rows = [
                    (
                        int(row["nAno"]),
                        int(row["nMes"]),
                        row["dtDivulgacao"].strip(),
                        Decimal(row["NI"]),
                        row["bReal"].strip() in ("1", "true", "t", "sim"),
                    )
                    for row in reader
                    if row["nome_indice"].strip() == "IPCA"
                ]
            cur.executemany("""
                INSERT INTO IndicesMensaisTempo
                    (idIndice, nAno, nMes, dtDivulgacao, NI, bReal)
                VALUES (5, %s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING
            """, idx_rows)

    @classmethod
    def _remover_tabelas(cls):
        with connection.cursor() as cur:
            cur.execute("DROP TABLE IF EXISTS IndicesMensaisTempo")
            cur.execute("DROP TABLE IF EXISTS Indices CASCADE")
            cur.execute("DROP TABLE IF EXISTS Calendario")

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
