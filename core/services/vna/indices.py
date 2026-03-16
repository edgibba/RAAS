from datetime import date
from decimal import Decimal

from .modelos import IndiceCadastro
from .exceptions import IndiceNaoEncontradoError, SerieMensalNaoEncontradaError


def listar_indices_mensais(conn):
    sql = """
    SELECT idIndice, nome, Periodicidade
    FROM Indices
    WHERE Periodicidade = 'MENSAL'
    ORDER BY nome
    """

    with conn.cursor() as cur:
        cur.execute(sql)
        rows = cur.fetchall()

    return [
        IndiceCadastro(
            id_indice=r[0],
            nome=r[1],
            periodicidade=r[2],
        )
        for r in rows
    ]


def obter_indice(conn, id_indice):
    sql = """
    SELECT idIndice, nome, Periodicidade
    FROM Indices
    WHERE idIndice = %s
    """

    with conn.cursor() as cur:
        cur.execute(sql, (id_indice,))
        row = cur.fetchone()

    if row is None:
        raise IndiceNaoEncontradoError(f"Índice {id_indice} não encontrado.")

    return IndiceCadastro(
        id_indice=row[0],
        nome=row[1],
        periodicidade=row[2],
    )


def obter_ni_mensal_para_data_calculo(conn, id_indice: int, ano: int, mes: int, data_vna: date):
    """
    Retorna o NI aplicável para a data de cálculo:
    - usa o valor real quando dtDivulgacao <= data_vna
    - caso contrário, usa o projetado
    """

    sql = """
    SELECT
        dtDivulgacao,
        NI,
        bReal
    FROM IndicesMensaisTempo
    WHERE idIndice = %s
      AND nAno = %s
      AND nMes = %s
    ORDER BY bReal DESC, dtDivulgacao DESC
    """

    with conn.cursor() as cur:
        cur.execute(sql, (id_indice, ano, mes))
        rows = cur.fetchall()

    if not rows:
        raise SerieMensalNaoEncontradaError(
            f"Série não encontrada para idIndice={id_indice}, ano={ano}, mes={mes}."
        )

    real_row = None
    proj_row = None

    for row in rows:
        dt_div, ni, b_real = row
        if b_real:
            real_row = row
        else:
            proj_row = row

    if real_row is not None:
        dt_div, ni, _ = real_row
        if dt_div is not None and dt_div <= data_vna and ni is not None and Decimal(ni) > 0:
            return {
                "dt_divulgacao": dt_div,
                "ni": Decimal(ni),
                "b_real": True,
                "fonte": "Real divulgado",
            }

    if proj_row is not None:
        dt_div, ni, _ = proj_row
        if ni is not None and Decimal(ni) > 0:
            return {
                "dt_divulgacao": dt_div,
                "ni": Decimal(ni),
                "b_real": False,
                "fonte": "Projetado vigente",
            }

    raise SerieMensalNaoEncontradaError(
        f"Sem NI válido para idIndice={id_indice}, ano={ano}, mes={mes}."
    )