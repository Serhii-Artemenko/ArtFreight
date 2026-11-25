import os

import psycopg


def get_connection():
    """Open a connection to our local development database."""
    password = os.environ.get("DB_PASSWORD")

    if not password:
        raise RuntimeError("DB_PASSWORD is not set in this terminal.")

    return psycopg.connect(
        host="localhost",
        port=5432,
        dbname="artfreight",
        user="artfreight_app",
        password=password,
        connect_timeout=5,
    )