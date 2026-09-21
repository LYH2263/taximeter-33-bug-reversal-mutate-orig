import json, sqlite3
from datetime import datetime, timezone

def _now():
    return datetime.now(timezone.utc).isoformat()

def insert(conn, kind, payload, result, trip_id=None):
    cur = conn.execute(
        "INSERT INTO calc_runs(kind,trip_id,input_json,result_json,created_at) VALUES (?,?,?,?,?)",
        (kind, trip_id, json.dumps(payload, ensure_ascii=False), json.dumps(result, ensure_ascii=False), _now()),
    )
    conn.commit()
    return int(cur.lastrowid)

def insert_reversal(conn, payload, result, original_id, trip_id=None):
    """写入一条 fare 冲正记录并在同一事务内标记原记录；原拆解不改写。"""
    try:
        cur = conn.execute(
            "INSERT INTO calc_runs(kind,trip_id,input_json,result_json,created_at,reversal_of)"
            " VALUES ('fare',?,?,?,?,?)",
            (trip_id, json.dumps(payload, ensure_ascii=False), json.dumps(result, ensure_ascii=False), _now(), original_id),
        )
        new_id = int(cur.lastrowid)
        conn.execute("UPDATE calc_runs SET reversed_by=? WHERE id=?", (new_id, original_id))
        conn.commit()
        return new_id
    except Exception:
        conn.rollback()
        raise

def get(conn, run_id: int) -> dict | None:
    row = conn.execute("SELECT * FROM calc_runs WHERE id=?", (run_id,)).fetchone()
    return dict(row) if row else None

def list_recent(conn, limit=50):
    return [dict(r) for r in conn.execute("SELECT * FROM calc_runs ORDER BY id DESC LIMIT ?", (limit,)).fetchall()]
