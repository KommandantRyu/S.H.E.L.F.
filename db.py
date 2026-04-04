import os
from contextlib import contextmanager

import pymysql


def get_connection():
    return pymysql.connect(
        host=os.environ.get("MYSQL_HOST", "localhost"),
        user=os.environ.get("MYSQL_USER", "root"),
        password=os.environ.get("MYSQL_PASSWORD", ""),
        database=os.environ.get("MYSQL_DATABASE", "library_db"),
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True,
    )


@contextmanager
def db_cursor():
    conn = get_connection()
    try:
        yield conn.cursor()
    finally:
        conn.close()
