import csv
from decimal import Decimal
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import connection, transaction

BATCH_SIZE = 500


class Command(BaseCommand):
    help = "Carrega calendario de dias uteis e/ou serie historica de indices mensais"

    def add_arguments(self, parser):
        parser.add_argument(
            "--arquivo-calendario",
            default=str(Path(settings.BASE_DIR) / "data" / "calendario.csv"),
            help="Caminho do CSV do calendario",
        )
        parser.add_argument(
            "--arquivo-indices",
            default=str(Path(settings.BASE_DIR) / "data" / "indices_mensais.csv"),
            help="Caminho do CSV dos indices mensais",
        )
        parser.add_argument(
            "--apenas-calendario",
            action="store_true",
            help="Carrega apenas o calendario, ignorando indices",
        )
        parser.add_argument(
            "--apenas-indices",
            action="store_true",
            help="Carrega apenas os indices, ignorando calendario",
        )
        parser.add_argument(
            "--limpar",
            action="store_true",
            help="Apaga os dados das tabelas sendo carregadas antes da carga",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Valida os arquivos sem gravar no banco de dados",
        )

    def handle(self, *args, **options):
        apenas_cal = options["apenas_calendario"]
        apenas_idx = options["apenas_indices"]
        limpar = options["limpar"]
        dry_run = options["dry_run"]

        # Se nenhum filtro for passado, carrega tudo
        carregar_cal = not apenas_idx
        carregar_idx = not apenas_cal

        arq_cal = Path(options["arquivo_calendario"])
        arq_idx = Path(options["arquivo_indices"])

        if carregar_cal and not arq_cal.exists():
            self.stderr.write(f"Arquivo de calendario nao encontrado: {arq_cal}")
            return

        if carregar_idx and not arq_idx.exists():
            self.stderr.write(f"Arquivo de indices nao encontrado: {arq_idx}")
            return

        if dry_run:
            self.stdout.write(self.style.WARNING("[DRY-RUN] Validando arquivos sem gravar no banco..."))
            if carregar_cal:
                self._validar_csv_calendario(arq_cal)
            if carregar_idx:
                self._validar_csv_indices(arq_idx)
            self.stdout.write(self.style.SUCCESS("[DRY-RUN] Arquivos validos. Nenhuma alteracao foi feita."))
            return

        with transaction.atomic():
            with connection.cursor() as cursor:
                if limpar:
                    if carregar_cal:
                        self.stdout.write("Limpando tabela Calendario...")
                        cursor.execute("DELETE FROM Calendario")
                    if carregar_idx:
                        self.stdout.write("Limpando tabelas de Indices...")
                        cursor.execute("DELETE FROM IndicesMensaisTempo")
                        cursor.execute("DELETE FROM Indices")

                if carregar_idx:
                    self._garantir_indice_ipca(cursor)

                if carregar_cal:
                    self._cargar_calendario(cursor, arq_cal)

                if carregar_idx:
                    self._cargar_indices(cursor, arq_idx)

        self.stdout.write(self.style.SUCCESS("Carga concluida com sucesso."))

    def _garantir_indice_ipca(self, cursor):
        cursor.execute("""
            INSERT INTO Indices (nome, Periodicidade)
            VALUES ('IPCA', 'MENSAL')
            ON CONFLICT (nome) DO NOTHING
        """)

    def _obter_id_indice(self, cursor, nome_indice: str) -> int:
        cursor.execute("""
            SELECT idIndice
            FROM Indices
            WHERE nome = %s
        """, [nome_indice])
        row = cursor.fetchone()
        if not row:
            raise ValueError(f"Indice nao cadastrado: {nome_indice}")
        return row[0]

    def _cargar_calendario(self, cursor, caminho: Path):
        self.stdout.write(f"Carregando calendario: {caminho}")

        with caminho.open("r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            lote = []
            total = 0

            for row in reader:
                lote.append((row["dtBase"].strip(), self._to_bool(row["bUtil"])))
                if len(lote) >= BATCH_SIZE:
                    self._inserir_lote_calendario(cursor, lote)
                    total += len(lote)
                    lote = []

            if lote:
                self._inserir_lote_calendario(cursor, lote)
                total += len(lote)

        self.stdout.write(f"Calendario carregado: {total} linhas")

    def _inserir_lote_calendario(self, cursor, lote):
        cursor.executemany("""
            INSERT INTO Calendario (dtBase, bUtil)
            VALUES (%s, %s)
            ON CONFLICT (dtBase)
            DO UPDATE SET bUtil = EXCLUDED.bUtil
        """, lote)

    def _cargar_indices(self, cursor, caminho: Path):
        self.stdout.write(f"Carregando indices mensais: {caminho}")

        # Agrupa por índice para minimizar consultas de id
        cache_ids = {}
        lote = []
        total = 0

        with caminho.open("r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)

            for row in reader:
                nome_indice = row["nome_indice"].strip()
                if nome_indice not in cache_ids:
                    cache_ids[nome_indice] = self._obter_id_indice(cursor, nome_indice)

                lote.append((
                    cache_ids[nome_indice],
                    int(row["nAno"]),
                    int(row["nMes"]),
                    row["dtDivulgacao"].strip(),
                    Decimal(row["NI"]),
                    self._to_bool(row["bReal"]),
                ))

                if len(lote) >= BATCH_SIZE:
                    self._inserir_lote_indices(cursor, lote)
                    total += len(lote)
                    lote = []

            if lote:
                self._inserir_lote_indices(cursor, lote)
                total += len(lote)

        self.stdout.write(f"Indices mensais carregados: {total} linhas")

    def _inserir_lote_indices(self, cursor, lote):
        cursor.executemany("""
            INSERT INTO IndicesMensaisTempo
                (idIndice, nAno, nMes, dtDivulgacao, NI, bReal)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (idIndice, nAno, nMes, bReal)
            DO UPDATE SET
                dtDivulgacao = EXCLUDED.dtDivulgacao,
                NI = EXCLUDED.NI,
                bReal = EXCLUDED.bReal
        """, lote)

    def _validar_csv_calendario(self, caminho: Path):
        self.stdout.write(f"Validando calendario: {caminho}")
        with caminho.open("r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            colunas_esperadas = {"dtBase", "bUtil"}
            if not colunas_esperadas.issubset(set(reader.fieldnames or [])):
                raise ValueError(f"Colunas esperadas no calendario: {colunas_esperadas}")
            total = sum(1 for _ in reader)
        self.stdout.write(f"  {total} linhas encontradas no calendario")

    def _validar_csv_indices(self, caminho: Path):
        self.stdout.write(f"Validando indices: {caminho}")
        with caminho.open("r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            colunas_esperadas = {"nome_indice", "nAno", "nMes", "dtDivulgacao", "NI", "bReal"}
            if not colunas_esperadas.issubset(set(reader.fieldnames or [])):
                raise ValueError(f"Colunas esperadas nos indices: {colunas_esperadas}")
            total = sum(1 for _ in reader)
        self.stdout.write(f"  {total} linhas encontradas nos indices")

    @staticmethod
    def _to_bool(valor: str) -> bool:
        valor = str(valor).strip().lower()
        return valor in {"1", "true", "t", "sim", "s", "y", "yes"}
