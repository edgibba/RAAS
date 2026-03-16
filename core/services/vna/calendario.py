from datetime import date

from .exceptions import ParametroInvalidoError, CalendarioIncompletoError


def contar_dias_uteis(conn, data_inicio_inclusiva: date, data_fim_exclusiva: date) -> int:
    """
    Conta dias úteis no intervalo [data_inicio_inclusiva, data_fim_exclusiva).
    Equivale ao padrão da planilha:
        COUNTIFS(dtBase, ">=" & inicio, dtBase, "<" & fim)
    """
    if data_fim_exclusiva < data_inicio_inclusiva:
        raise ParametroInvalidoError("Data final menor que data inicial.")

    sql = """
        SELECT COUNT(*)
        FROM Calendario
        WHERE bUtil = TRUE
          AND dtBase >= %s
          AND dtBase < %s
    """

    with conn.cursor() as cur:
        cur.execute(sql, (data_inicio_inclusiva, data_fim_exclusiva))
        row = cur.fetchone()

    return int(row[0] or 0)


def proximo_dia_util_ou_mesma_data(conn, dt: date) -> date:
    """
    Retorna o primeiro dia útil >= dt.
    """
    sql = """
        SELECT dtBase
        FROM Calendario
        WHERE bUtil = TRUE
          AND dtBase >= %s
        ORDER BY dtBase
        LIMIT 1
    """

    with conn.cursor() as cur:
        cur.execute(sql, (dt,))
        row = cur.fetchone()

    if row is None:
        raise CalendarioIncompletoError(f"Não há dia útil a partir de {dt}.")

    return row[0]


def validar_existencia_calendario(conn, data_inicio: date, data_fim: date) -> None:
    if data_fim < data_inicio:
        raise ParametroInvalidoError("Data final menor que data inicial.")

    sql = """
        SELECT COUNT(*)
        FROM Calendario
        WHERE dtBase >= %s
          AND dtBase <= %s
    """

    with conn.cursor() as cur:
        cur.execute(sql, (data_inicio, data_fim))
        row = cur.fetchone()

    if row is None or int(row[0]) == 0:
        raise CalendarioIncompletoError(
            f"Calendário não encontrado no intervalo {data_inicio} a {data_fim}."
        )


def aniversario_ajustado(conn, ano: int, mes: int, dia: int = 15) -> date:
    """
    Retorna o aniversário do mês, ajustado para o próximo dia útil
    quando o dia-base não for útil.
    """
    return proximo_dia_util_ou_mesma_data(conn, date(ano, mes, dia))