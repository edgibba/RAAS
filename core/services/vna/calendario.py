from datetime import date
from .exceptions import ParametroInvalidoError


def contar_dias_uteis(conn, data_inicio: date, data_fim: date) -> int:

    if data_fim < data_inicio:
        raise ParametroInvalidoError("Data final menor que data inicial")

    sql = """
        SELECT COUNT(*)
        FROM Calendario
        WHERE dtBase > %s
        AND dtBase <= %s
        AND bUtil = TRUE
    """

    with conn.cursor() as cur:
        cur.execute(sql, (data_inicio, data_fim))
        row = cur.fetchone()

    return int(row[0])