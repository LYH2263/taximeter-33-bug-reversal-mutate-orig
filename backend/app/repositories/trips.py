import sqlite3

def list_all(conn: sqlite3.Connection) -> list[dict]:
    return [dict(r) for r in conn.execute("SELECT * FROM trips ORDER BY id").fetchall()]

def get(conn: sqlite3.Connection, trip_id: int) -> dict | None:
    row = conn.execute("SELECT * FROM trips WHERE id=?", (trip_id,)).fetchone()
    return dict(row) if row else None
