from datetime import date
from decimal import Decimal, ROUND_DOWN, getcontext

from .calendario import (
    contar_dias_uteis,
    proximo_dia_util_ou_mesma_data,
    validar_existencia_calendario,
    aniversario_ajustado,
)
from .indices import obter_indice, obter_ni_mensal_para_data_calculo
from .modelos import ResultadoVNA, ResultadoAuditoriaVNA, EtapaAuditoriaVNA
from .exceptions import ParametroInvalidoError

getcontext().prec = 28


QTD_8 = Decimal("0.00000001")
QTD_16 = Decimal("0.0000000000000001")


def _trunc(valor: Decimal, casas: int) -> Decimal:
    if casas == 8:
        return valor.quantize(QTD_8, rounding=ROUND_DOWN)
    if casas == 16:
        return valor.quantize(QTD_16, rounding=ROUND_DOWN)
    raise ValueError("Quantidade de casas não suportada.")


def _pow_decimal(base: Decimal, expoente: Decimal) -> Decimal:
    """
    Potência com expoente decimal usando ln/exp do Decimal.
    """
    if base <= 0:
        raise ParametroInvalidoError("Base inválida para cálculo do fator.")
    if expoente == 0:
        return Decimal("1")
    if expoente == 1:
        return base
    return (base.ln() * expoente).exp()


def _mes_anterior(ano: int, mes: int) -> tuple[int, int]:
    if mes == 1:
        return ano - 1, 12
    return ano, mes - 1


def _primeiro_dia_mes_anterior(dt: date) -> date:
    ano, mes = _mes_anterior(dt.year, dt.month)
    return date(ano, mes, 1)


def _segundo_mes_anterior(dt: date) -> date:
    ano_1, mes_1 = _mes_anterior(dt.year, dt.month)
    ano_2, mes_2 = _mes_anterior(ano_1, mes_1)
    return date(ano_2, mes_2, 1)


def _proximo_aniversario_apos(conn, dt: date, dia: int = 15) -> date:
    """
    Próximo aniversário após dt, conforme a lógica da planilha.
    """
    ani_mes = aniversario_ajustado(conn, dt.year, dt.month, dia)
    if dt < ani_mes:
        return ani_mes

    ano_next, mes_next = (dt.year + 1, 1) if dt.month == 12 else (dt.year, dt.month + 1)
    return aniversario_ajustado(conn, ano_next, mes_next, dia)


def _montar_primeira_linha(
    conn,
    data_inicio_ajustada: date,
    data_vna: date,
    dia: int = 15,
):
    aniversario_mes_inicio = aniversario_ajustado(conn, data_inicio_ajustada.year, data_inicio_ajustada.month, dia)
    ano_ant, mes_ant = _mes_anterior(data_inicio_ajustada.year, data_inicio_ajustada.month)
    aniversario_mes_anterior_inicio = aniversario_ajustado(conn, ano_ant, mes_ant, dia)

    aniversario_anterior_inicio = (
        aniversario_mes_anterior_inicio if data_inicio_ajustada < aniversario_mes_inicio else aniversario_mes_inicio
    )
    proximo_aniversario_inicio = _proximo_aniversario_apos(conn, data_inicio_ajustada, dia)

    aniversario_mes_calculo = aniversario_ajustado(conn, data_vna.year, data_vna.month, dia)
    ano_ant_calc, mes_ant_calc = _mes_anterior(data_vna.year, data_vna.month)
    aniversario_mes_anterior_calculo = aniversario_ajustado(conn, ano_ant_calc, mes_ant_calc, dia)

    ultimo_aniversario_calculo = (
        aniversario_mes_anterior_calculo if data_vna < aniversario_mes_calculo else aniversario_mes_calculo
    )
    proximo_aniversario_calculo = _proximo_aniversario_apos(conn, data_vna, dia)

    dup_final = contar_dias_uteis(conn, ultimo_aniversario_calculo, data_vna)
    dut_final = contar_dias_uteis(conn, ultimo_aniversario_calculo, proximo_aniversario_calculo)

    dup_inicial = contar_dias_uteis(conn, data_inicio_ajustada, proximo_aniversario_inicio)
    dut_inicial = contar_dias_uteis(conn, aniversario_anterior_inicio, proximo_aniversario_inicio)

    calculo_ate_primeiro_aniversario = data_vna <= proximo_aniversario_inicio
    expoente_inicial = Decimal("1") if data_inicio_ajustada == aniversario_anterior_inicio else (
        Decimal(dup_inicial) / Decimal(dut_inicial)
    )

    dup_periodo_unico = contar_dias_uteis(conn, data_inicio_ajustada, data_vna)

    if calculo_ate_primeiro_aniversario:
        if data_vna == proximo_aniversario_inicio:
            tipo_primeira = "Integral" if expoente_inicial == Decimal("1") else "Parcial inicial"
        else:
            tipo_primeira = "Parcial único"
    else:
        if data_vna == ultimo_aniversario_calculo:
            if data_vna == proximo_aniversario_inicio:
                tipo_primeira = "Integral" if expoente_inicial == Decimal("1") else "Parcial inicial"
            else:
                tipo_primeira = "Integral"
        else:
            tipo_primeira = "Parcial final"

    if calculo_ate_primeiro_aniversario:
        if data_vna == proximo_aniversario_inicio:
            expoente_primeira = expoente_inicial
        else:
            expoente_primeira = Decimal(dup_periodo_unico) / Decimal(dut_inicial)
    else:
        if data_vna == ultimo_aniversario_calculo:
            if data_vna == proximo_aniversario_inicio:
                expoente_primeira = expoente_inicial
            else:
                expoente_primeira = Decimal("1")
        else:
            expoente_primeira = Decimal(dup_final) / Decimal(dut_final)

    return {
        "data_inicio_ajustada": data_inicio_ajustada,
        "aniversario_anterior_inicio": aniversario_anterior_inicio,
        "proximo_aniversario_inicio": proximo_aniversario_inicio,
        "ultimo_aniversario_calculo": ultimo_aniversario_calculo,
        "proximo_aniversario_calculo": proximo_aniversario_calculo,
        "dup_final": dup_final,
        "dut_final": dut_final,
        "dup_inicial": dup_inicial,
        "dut_inicial": dut_inicial,
        "dup_periodo_unico": dup_periodo_unico,
        "expoente_inicial": expoente_inicial,
        "calculo_ate_primeiro_aniversario": calculo_ate_primeiro_aniversario,
        "tipo_primeira": tipo_primeira,
        "expoente_primeira": expoente_primeira,
    }


def calcular_vna(
    conn,
    id_indice,
    data_inicio_rentabilidade: date,
    data_vna: date,
    vne: Decimal = Decimal("1000"),
    base_pro_rata: str = "DU",
    dia_referencia: int = 15,
    detalhar: bool = False,
):
    if data_vna < data_inicio_rentabilidade:
        raise ParametroInvalidoError(
            "A data do VNA não pode ser anterior à data de início da rentabilidade."
        )

    if base_pro_rata != "DU":
        raise ParametroInvalidoError("Nesta etapa, somente DU está implementado.")

    if dia_referencia not in range(1, 29):
        raise ParametroInvalidoError("Dia de referência deve ser entre 1 e 28.")

    indice = obter_indice(conn, id_indice)

    data_inicio_ajustada = proximo_dia_util_ou_mesma_data(conn, data_inicio_rentabilidade)
    validar_existencia_calendario(conn, data_inicio_ajustada, data_vna)

    info = _montar_primeira_linha(conn, data_inicio_ajustada, data_vna, dia_referencia)

    datas_fim = [data_vna]

    if not info["calculo_ate_primeiro_aniversario"]:
        data_anterior = info["ultimo_aniversario_calculo"]
        if data_vna != info["ultimo_aniversario_calculo"]:
            datas_fim.append(data_anterior)
        while True:
            ano_ant, mes_ant = _mes_anterior(data_anterior.year, data_anterior.month)
            dt_retro = aniversario_ajustado(conn, ano_ant, mes_ant, dia_referencia)

            if dt_retro <= info["proximo_aniversario_inicio"]:
                if data_anterior != info["proximo_aniversario_inicio"]:
                    datas_fim.append(info["proximo_aniversario_inicio"])
                break

            datas_fim.append(dt_retro)
            data_anterior = dt_retro

    etapas = []
    fator_acumulado = Decimal("0")
    ordem = 1

    for i, data_fim_periodo in enumerate(datas_fim):
        if i == 0 and info["tipo_primeira"] == "Parcial final":
            ref_ni_atual = _primeiro_dia_mes_anterior(info["proximo_aniversario_calculo"])
            ref_ni_anterior = _segundo_mes_anterior(info["proximo_aniversario_calculo"])
        else:
            ref_ni_atual = _primeiro_dia_mes_anterior(data_fim_periodo)
            ref_ni_anterior = _segundo_mes_anterior(data_fim_periodo)

        ni_atual_info = obter_ni_mensal_para_data_calculo(
            conn, id_indice, ref_ni_atual.year, ref_ni_atual.month, data_vna
        )
        ni_anterior_info = obter_ni_mensal_para_data_calculo(
            conn, id_indice, ref_ni_anterior.year, ref_ni_anterior.month, data_vna
        )

        ni_atual = Decimal(ni_atual_info["ni"])
        ni_anterior = Decimal(ni_anterior_info["ni"])

        if i == 0:
            tipo = info["tipo_primeira"]
            if tipo == "Integral":
                dup = 0
                dut = 0
            elif tipo == "Parcial final":
                dup = info["dup_final"]
                dut = info["dut_final"]
            elif tipo == "Parcial inicial":
                dup = info["dup_inicial"]
                dut = info["dut_inicial"]
            else:  # Parcial único
                dup = info["dup_periodo_unico"]
                dut = info["dut_inicial"]

            expoente = info["expoente_primeira"]
        else:
            if data_fim_periodo == info["proximo_aniversario_inicio"]:
                tipo = "Integral" if info["expoente_inicial"] == Decimal("1") else "Parcial inicial"
            else:
                tipo = "Integral"

            if tipo == "Integral":
                dup = 0
                dut = 0
                expoente = Decimal("1")
            else:
                dup = info["dup_inicial"]
                dut = info["dut_inicial"]
                expoente = info["expoente_inicial"]

        fator_bruto = _pow_decimal(ni_atual / ni_anterior, expoente)
        fator_mensal = _trunc(fator_bruto, 8)

        if ordem == 1:
            fator_acumulado = _trunc(fator_mensal, 16)
        else:
            fator_acumulado = _trunc(fator_acumulado * fator_mensal, 16)

        etapas.append(
            EtapaAuditoriaVNA(
                ordem=ordem,
                tipo=tipo,
                data_fim_periodo=data_fim_periodo,
                ref_ni_atual=ref_ni_atual,
                ref_ni_anterior=ref_ni_anterior,
                dt_divulgacao=ni_atual_info["dt_divulgacao"],
                ni_atual=ni_atual,
                ni_anterior=ni_anterior,
                fonte=ni_atual_info["fonte"],
                dup=dup,
                dut=dut,
                expoente=expoente,
                fator_mensal=fator_mensal,
                fator_acumulado=fator_acumulado,
            )
        )
        ordem += 1

    vna = _trunc(vne * fator_acumulado, 8)

    if detalhar:
        return ResultadoAuditoriaVNA(
            id_indice=id_indice,
            nome_indice=indice.nome,
            data_inicio_rentabilidade=data_inicio_rentabilidade,
            data_vna=data_vna,
            vne=vne,
            fator_final=fator_acumulado,
            vna=vna,
            etapas=etapas,
        )

    return ResultadoVNA(
        id_indice=id_indice,
        nome_indice=indice.nome,
        data_inicio_rentabilidade=data_inicio_rentabilidade,
        data_vna=data_vna,
        vne=vne,
        fator_final=fator_acumulado,
        vna=vna,
    )
