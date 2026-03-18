import csv
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction

from core.models import DebentureCadastro

BATCH_SIZE = 500

# Mapeamento: índice da coluna no CSV → campo do model
COL_MAP = {
    0:  "codigo_ativo",
    1:  "empresa",
    2:  "serie",
    3:  "emissao",
    4:  "ipo",
    5:  "situacao",
    6:  "isin",
    7:  "registro_cvm_emissao",
    8:  "dt_registro_cvm_emissao",
    9:  "registro_cvm_programa",
    10: "dt_registro_cvm_programa",
    11: "dt_emissao",
    12: "dt_vencimento",
    13: "motivo_saida",
    14: "dt_saida_novo_vencimento",
    15: "dt_inicio_rentabilidade",
    16: "dt_inicio_distribuicao",
    17: "dt_proxima_repactuacao",
    18: "ato_societario_1",
    19: "dt_ato_1",
    20: "ato_societario_2",
    21: "dt_ato_2",
    22: "forma",
    23: "garantia_especie",
    24: "classe",
    25: "qtd_emitida",
    26: "artigo_14",
    27: "artigo_24",
    28: "qtd_mercado",
    29: "qtd_tesouraria",
    30: "qtd_resgatada",
    31: "qtd_cancelada",
    32: "qtd_convertida_snd",
    33: "qtd_convertida_fora_snd",
    34: "qtd_permutada_snd",
    35: "qtd_permutada_fora_snd",
    36: "unidade_monetaria_emissao",
    37: "vn_emissao",
    38: "unidade_monetaria_atual",
    39: "vn_atual",
    40: "dt_ult_vna",
    41: "indice",
    42: "tipo_indice",
    43: "criterio_calculo",
    44: "dia_ref_indice_precos",
    45: "criterio_indice",
    46: "corrige_a_cada",
    47: "pct_multiplicador",
    48: "limite_tjlp",
    49: "tipo_limite_tjlp",
    50: "juros_criterio_antigo",
    51: "premios_criterio_antigo",
    52: "amort_taxa",
    53: "amort_cada",
    54: "amort_unidade",
    55: "amort_carencia",
    56: "amort_criterio",
    57: "tipo_amortizacao",
    58: "juros_taxa",
    59: "juros_prazo",
    60: "juros_cada",
    61: "juros_unidade",
    62: "juros_carencia",
    63: "juros_criterio",
    64: "juros_tipo",
    65: "premio_taxa",
    66: "premio_prazo",
    67: "premio_cada",
    68: "premio_unidade",
    69: "premio_carencia",
    70: "premio_criterio",
    71: "premio_tipo",
    72: "participacao_taxa",
    73: "participacao_cada",
    74: "participacao_unidade",
    75: "participacao_carencia",
    76: "participacao_descricao",
    77: "banco_mandatario",
    78: "agente_fiduciario",
    79: "instituicao_depositaria",
    80: "coordenador_lider",
    81: "cnpj",
    82: "deb_incentivada",
    83: "escritura_padronizada",
    84: "resgate_antecipado",
}

DATE_FIELDS = {
    "dt_registro_cvm_emissao", "dt_registro_cvm_programa", "dt_emissao",
    "dt_vencimento", "dt_saida_novo_vencimento", "dt_inicio_rentabilidade",
    "dt_inicio_distribuicao", "dt_proxima_repactuacao", "dt_ult_vna",
    "dt_ato_1", "dt_ato_2",
}

DECIMAL_FIELDS = {
    "qtd_emitida", "qtd_mercado", "qtd_tesouraria", "qtd_resgatada",
    "qtd_cancelada", "qtd_convertida_snd", "qtd_convertida_fora_snd",
    "qtd_permutada_snd", "qtd_permutada_fora_snd",
    "vn_emissao", "vn_atual",
}


def _parse_date(valor: str):
    v = valor.strip()
    if not v or v == "-":
        return None
    try:
        d, m, a = v.split("/")
        return date(int(a), int(m), int(d))
    except (ValueError, AttributeError):
        return None


def _parse_decimal(valor: str):
    v = valor.strip().replace(".", "").replace(",", ".")
    if not v or v == "-":
        return None
    try:
        return Decimal(v)
    except InvalidOperation:
        return None


class Command(BaseCommand):
    help = "Carrega o cadastro de debentures ANBIMA (debcad.csv)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--arquivo",
            default=str(Path(settings.BASE_DIR) / "data" / "debcad.csv"),
            help="Caminho do CSV de cadastro de debentures",
        )
        parser.add_argument(
            "--limpar",
            action="store_true",
            help="Apaga todos os registros antes da carga",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Valida o arquivo sem gravar no banco",
        )

    def handle(self, *args, **options):
        arquivo = Path(options["arquivo"])
        limpar = options["limpar"]
        dry_run = options["dry_run"]

        if not arquivo.exists():
            self.stderr.write(f"Arquivo nao encontrado: {arquivo}")
            return

        if dry_run:
            self.stdout.write(self.style.WARNING("[DRY-RUN] Validando sem gravar..."))
            total = self._contar_linhas(arquivo)
            self.stdout.write(self.style.SUCCESS(f"[DRY-RUN] {total} registros encontrados. Arquivo valido."))
            return

        with transaction.atomic():
            if limpar:
                self.stdout.write("Limpando tabela DebentureCadastro...")
                DebentureCadastro.objects.all().delete()

            total = self._carregar(arquivo)

        self.stdout.write(self.style.SUCCESS(f"Carga concluida: {total} registros processados."))

    def _contar_linhas(self, arquivo: Path) -> int:
        with arquivo.open("r", encoding="latin-1", newline="") as f:
            # pula 4 linhas de cabeçalho
            for _ in range(4):
                next(f)
            reader = csv.reader(f, delimiter="\t")
            next(reader)  # linha de header das colunas
            return sum(1 for _ in reader)

    def _carregar(self, arquivo: Path) -> int:
        self.stdout.write(f"Carregando: {arquivo}")
        lote = []
        total = 0

        with arquivo.open("r", encoding="latin-1", newline="") as f:
            for _ in range(4):
                next(f)
            reader = csv.reader(f, delimiter="\t")
            next(reader)  # header

            for row in reader:
                obj = self._parse_row(row)
                if obj is None:
                    continue
                lote.append(obj)

                if len(lote) >= BATCH_SIZE:
                    DebentureCadastro.objects.bulk_create(
                        lote,
                        update_conflicts=True,
                        update_fields=[f for f in COL_MAP.values() if f != "codigo_ativo"],
                        unique_fields=["codigo_ativo"],
                    )
                    total += len(lote)
                    lote = []

            if lote:
                DebentureCadastro.objects.bulk_create(
                    lote,
                    update_conflicts=True,
                    update_fields=[f for f in COL_MAP.values() if f != "codigo_ativo"],
                    unique_fields=["codigo_ativo"],
                )
                total += len(lote)

        self.stdout.write(f"Debentures carregadas: {total}")
        return total

    def _parse_row(self, row: list) -> DebentureCadastro | None:
        if not row or not row[0].strip():
            return None

        kwargs = {}
        for idx, campo in COL_MAP.items():
            valor = row[idx].strip() if idx < len(row) else ""

            if campo in DATE_FIELDS:
                kwargs[campo] = _parse_date(valor)
            elif campo in DECIMAL_FIELDS:
                kwargs[campo] = _parse_decimal(valor)
            else:
                kwargs[campo] = valor

        return DebentureCadastro(**kwargs)
