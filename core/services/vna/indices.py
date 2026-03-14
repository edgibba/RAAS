from .modelos import IndiceCadastro
from .exceptions import IndiceNaoEncontradoError


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
            id_indice=row[0],
            nome=row[1],
            periodicidade=row[2],
        )
        for row in rows
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