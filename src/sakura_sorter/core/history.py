import sqlite3
from pathlib import Path
from datetime import datetime, timezone
from sakura_sorter.core.config import CONFIG_DIR

HISTORY_DB_FILE = CONFIG_DIR / "history.db"

def _get_conn():
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(HISTORY_DB_FILE)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts TEXT NOT NULL,
            src TEXT NOT NULL,
            destinations TEXT,
            success INTEGER,
            message TEXT
        )
    """)
    return conn

def log_action(src: str, destinations: list[str], success: bool, message: str = ""):
    conn = _get_conn()
    dest_str = ",".join(destinations)
    ts = datetime.now(timezone.utc).isoformat()
    conn.execute("INSERT INTO history (ts, src, destinations, success, message) VALUES (?, ?, ?, ?, ?)",
                 (ts, src, dest_str, int(success), message))
    conn.commit()
    conn.close()

def read_history(limit: int = 200):
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, ts, src, destinations, success, message FROM history ORDER BY id DESC LIMIT ?", (limit,))
    rows = cur.fetchall()
    conn.close()
    entries = []
    for row in rows:
        eid, ts, src, dests, success, msg = row
        entries.append({
            "id": eid,
            "ts": ts,
            "src": src,
            "destinations": dests.split(",") if dests else [],
            "success": bool(success),
            "message": msg
        })
    return entries

def search_history(query: str, status: str = "All"):
    query = query.lower()
    conn = _get_conn()
    cur = conn.cursor()
    sql = "SELECT id, ts, src, destinations, success, message FROM history"
    conditions = []
    params = []

    if query:
        conditions.append("(LOWER(src) LIKE ? OR LOWER(destinations) LIKE ? OR LOWER(message) LIKE ?)")
        qparam = f"%{query}%"
        params.extend([qparam, qparam, qparam])

    if status == "Only OK":
        conditions.append("success = 1")
    elif status == "Only Failed":
        conditions.append("success = 0")

    if conditions:
        sql += " WHERE " + " AND ".join(conditions)

    sql += " ORDER BY id DESC"
    cur.execute(sql, params)
    rows = cur.fetchall()
    conn.close()
    entries = []
    for row in rows:
        eid, ts, src, dests, success, msg = row
        entries.append({
            "id": eid,
            "ts": ts,
            "src": src,
            "destinations": dests.split(",") if dests else [],
            "success": bool(success),
            "message": msg
        })
    return entries

def delete_entry_by_id(eid: int):
    conn = _get_conn()
    conn.execute("DELETE FROM history WHERE id = ?", (eid,))
    conn.commit()
    conn.close()

def delete_all_history():
    conn = _get_conn()
    conn.execute("DELETE FROM history")
    conn.commit()
    conn.close()
