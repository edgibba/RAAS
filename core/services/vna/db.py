from contextlib import contextmanager
import psycopg


@contextmanager
def get_connection(conn_string: str):
    conn = psycopg.connect(conn_string)
    try:
        yield conn
    finally:
        conn.close()