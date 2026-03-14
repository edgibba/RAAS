from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass(frozen=True)
class IndiceCadastro:
    id_indice: int
    nome: str
    periodicidade: str


@dataclass(frozen=True)
class IndiceMensal:
    id_indice: int
    ano: int
    mes: int
    dt_divulgacao: date
    ni: Decimal
    b_real: bool


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
    ano: int
    mes: int
    dt_divulgacao: date
    ni: Decimal
    b_real: bool
    dut_numerador: int
    dut_denominador: int
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