from .modelos import EtapaAuditoriaVNA


def registrar_etapa(
    etapas,
    ordem,
    indice_mensal,
    dut_num,
    dut_den,
    fator_mensal,
    fator_acumulado,
):

    etapa = EtapaAuditoriaVNA(
        ordem=ordem,
        ano=indice_mensal.ano,
        mes=indice_mensal.mes,
        dt_divulgacao=indice_mensal.dt_divulgacao,
        ni=indice_mensal.ni,
        b_real=indice_mensal.b_real,
        dut_numerador=dut_num,
        dut_denominador=dut_den,
        fator_mensal=fator_mensal,
        fator_acumulado=fator_acumulado,
    )

    etapas.append(etapa)