from datetime import date
from decimal import Decimal

from .modelos import ResultadoVNA, ResultadoAuditoriaVNA, EtapaAuditoriaVNA


def calcular_vna(
    conn,
    id_indice,
    data_inicio_rentabilidade: date,
    data_vna: date,
    vne: Decimal = Decimal("1000"),
    base_pro_rata="DU",
    detalhar=False,
):
    fator_final = Decimal("1")
    vna = vne * fator_final

    if detalhar:
        etapas = [
            EtapaAuditoriaVNA(
                ordem=1,
                ano=data_vna.year,
                mes=data_vna.month,
                dt_divulgacao=data_vna,
                ni=Decimal("0"),
                b_real=True,
                dut_numerador=0,
                dut_denominador=0,
                fator_mensal=Decimal("1"),
                fator_acumulado=Decimal("1"),
            )
        ]

        return ResultadoAuditoriaVNA(
            id_indice=id_indice,
            nome_indice=f"Índice {id_indice}",
            data_inicio_rentabilidade=data_inicio_rentabilidade,
            data_vna=data_vna,
            vne=vne,
            fator_final=fator_final,
            vna=vna,
            etapas=etapas,
        )

    return ResultadoVNA(
        id_indice=id_indice,
        nome_indice=f"Índice {id_indice}",
        data_inicio_rentabilidade=data_inicio_rentabilidade,
        data_vna=data_vna,
        vne=vne,
        fator_final=fator_final,
        vna=vna,
    )