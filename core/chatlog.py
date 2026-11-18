from .db import connect


def save_message(uid, role, content):
    with connect() as con:
        con.execute(
            "INSERT INTO chat_history(user_id,role,content) VALUES(?,?,?)",
            (uid, role, content),
        )


def load_history(uid, limit=30):
    with connect() as con:
        rows = con.execute(
            "SELECT role,content FROM chat_history WHERE user_id=? "
            "ORDER BY id DESC LIMIT ?",
            (uid, limit),
        ).fetchall()
    return [dict(r) for r in reversed(rows)]


def clear_history(uid):
    with connect() as con:
        con.execute("DELETE FROM chat_history WHERE user_id=?", (uid,))
