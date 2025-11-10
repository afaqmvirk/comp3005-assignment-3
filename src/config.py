import os
import psycopg2
from psycopg2 import sql

try:
    from dotenv import load_dotenv, find_dotenv 
    dotenv_path = find_dotenv(usecwd=True)
    if dotenv_path:
        load_dotenv(dotenv_path=dotenv_path)
except Exception:
    pass


def ensure_database_exists():
    """self explanatory i hope"""
    target_db = os.getenv("PGDATABASE")
    if not target_db:
        return

    conn_kwargs = dict(
        host=os.getenv("PGHOST"),
        port=os.getenv("PGPORT"),
        user=os.getenv("PGUSER"),
        password=os.getenv("PGPASSWORD"),
    )

    try:
        psycopg2.connect(dbname=target_db, **conn_kwargs).close()
        return
    except psycopg2.OperationalError:
        pass

    con = psycopg2.connect(dbname="postgres", **conn_kwargs)
    con.autocommit = True
    with con.cursor() as cur:
        cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(target_db)))
    con.close()


def get_connection():
    required = ["PGHOST", "PGPORT", "PGDATABASE", "PGUSER", "PGPASSWORD"]
    missing = [k for k in required if not os.getenv(k)]
    if missing:
        raise RuntimeError(
            f"Missing env vars: {', '.join(missing)}. "
            "Set them/create .env file (see README)."
        )

    return psycopg2.connect(
        host=os.getenv("PGHOST"),
        port=os.getenv("PGPORT"),
        dbname=os.getenv("PGDATABASE"),
        user=os.getenv("PGUSER"),
        password=os.getenv("PGPASSWORD"),
    )
