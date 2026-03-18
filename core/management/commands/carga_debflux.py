import csv
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction

from core.models import DebentureFluxo

BATCH_SIZE = 500
HEADER_SKIP = 2  # linhas antes do header no debflux.csv


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


def _limpar_tipo(valor: str) -> str:
    """
    O arquivo ANBIMA exporta o campo Tipo com o valor duplicado
    (ex: 'IPCAIPCA', 'DOLARDOLAR'). Retorna apenas a primeira metade
    quando o valor for uma repetição exata.
    """
    v = valor.strip()
    if not v:
        return v
    meio = len(v) // 2
    if len(v) % 2 == 0 and v[:meio] == v[meio:]:
        return v[:meio]
    return v


class Command(BaseCommand):
    help = "Carrega a agenda de fluxos de debentures ANBIMA (debflux.csv)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--arquivo",
            default=str(Path(settings.BASE_DIR) / "data" / "debflux.csv"),
            help="Caminho do CSV de fluxos",
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
                self.stdout.write("Limpando tabela DebentureFluxo...")
                DebentureFluxo.objects.all().delete()

            total, ignorados = self._carregar(arquivo)

        self.stdout.write(self.style.SUCCESS(
            f"Carga concluida: {total} registros carregados, {ignorados} ignorados (cod_deb ausente no cadastro)."
        ))

    def _contar_linhas(self, arquivo: Path) -> int:
        with arquivo.open("r", encoding="latin-1", newline="") as f:
            for _ in range(HEADER_SKIP):
                next(f)
            reader = csv.reader(f, delimiter="\t")
            next(reader)
            return sum(1 for row in reader if len(row) > 4 and row[3].strip())

    def _carregar(self, arquivo: Path):
        from core.models import DebentureCadastro
        codigos_validos = set(
            DebentureCadastro.objects.values_list("codigo_ativo", flat=True)
        )

        self.stdout.write(f"Carregando: {arquivo}")
        lote = []
        total = 0
        ignorados = 0

        with arquivo.open("r", encoding="latin-1", newline="") as f:
            for _ in range(HEADER_SKIP):
                next(f)
            reader = csv.reader(f, delimiter="\t")
            next(reader)  # header

            for row in reader:
                if len(row) < 5:
                    continue

                cod_deb = row[3].strip()
                if not cod_deb:
                    continue

                if cod_deb not in codigos_validos:
                    ignorados += 1
                    continue

                dt_evento = _parse_date(row[0])
                if dt_evento is None:
                    continue

                evento = row[4].strip()
                if not evento:
                    continue

                obj = DebentureFluxo(
                    cod_deb_id=cod_deb,
                    dt_evento=dt_evento,
                    evento=evento,
                    dt_pagamento=_parse_date(row[1]),
                    tipo=_limpar_tipo(row[5]) if len(row) > 5 else "",
                    taxa_percentual=_parse_decimal(row[6]) if len(row) > 6 else None,
                    liquidacao=row[7].strip() if len(row) > 7 else "",
                )
                lote.append(obj)

                if len(lote) >= BATCH_SIZE:
                    DebentureFluxo.objects.bulk_create(
                        lote,
                        update_conflicts=True,
                        update_fields=["dt_pagamento", "tipo", "taxa_percentual", "liquidacao"],
                        unique_fields=["cod_deb_id", "dt_evento", "evento"],
                    )
                    total += len(lote)
                    lote = []

            if lote:
                DebentureFluxo.objects.bulk_create(
                    lote,
                    update_conflicts=True,
                    update_fields=["dt_pagamento", "tipo", "taxa_percentual", "liquidacao"],
                    unique_fields=["cod_deb_id", "dt_evento", "evento"],
                )
                total += len(lote)

        return total, ignorados
