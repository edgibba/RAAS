from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass(frozen=True)
class IndiceCadastro:
    id_indice: int
    nome: str
    periodicidade: str


@dataclass(frozen=True)
class ResultadoVNA:
    id_indice: int
    nome_indice: str
    data_inicio_rentabilidade: date
    data_vna: date
    vne: Decimal
    fator_final: Decimal
    vna: Decimal


@dataclass(frozen=True)
class EtapaAuditoriaVNA:
    ordem: int
    tipo: str
    data_fim_periodo: date
    ref_ni_atual: date
    ref_ni_anterior: date
    dt_divulgacao: date | None
    ni_atual: Decimal
    ni_anterior: Decimal
    fonte: str
    dup: int
    dut: int
    expoente: Decimal
    fator_mensal: Decimal
    fator_acumulado: Decimal


@dataclass(frozen=True)
class ResultadoAuditoriaVNA:
    id_indice: int
    nome_indice: str
    data_inicio_rentabilidade: date
    data_vna: date
    vne: Decimal
    fator_final: Decimal
    vna: Decimal
    etapas: list[EtapaAuditoriaVNA]