import sqlite3

def get_active(conn: sqlite3.Connection) -> dict:
    row = conn.execute("SELECT * FROM tariff ORDER BY id LIMIT 1").fetchone()
    return dict(row) if row else {}
