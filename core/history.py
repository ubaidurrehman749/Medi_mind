from .db import connect


def add_item(uid, condition, notes=""):
    with connect() as con:
        con.execute(
            "INSERT INTO medical_history(patient_id,condition,notes) VALUES(?,?,?)",
            (uid, condition.strip(), notes.strip()),
        )


def list_items(uid):
    with connect() as con:
        rows = con.execute(
            "SELECT id,condition,notes,created_at FROM medical_history "
            "WHERE patient_id=? ORDER BY id DESC",
            (uid,),
        ).fetchall()
    return [dict(r) for r in rows]


def delete_item(uid, item_id):
    with connect() as con:
        con.execute(
            "DELETE FROM medical_history WHERE id=? AND patient_id=?", (item_id, uid)
        )


def export_all(uid):
    """Patient ka apna saara data ek dictionary mein (download ke liye)."""
    queries = {
        "profile": "SELECT age,gender,blood_group,family_history FROM patient_profiles WHERE user_id=?",
        "allergies": "SELECT allergen,reaction FROM allergies WHERE patient_id=?",
        "medical_history": "SELECT condition,notes,created_at FROM medical_history WHERE patient_id=?",
        "medications": "SELECT name,dosage,schedule FROM medications WHERE patient_id=? AND active=1",
        "reports": "SELECT filename,report_type,ai_summary,created_at FROM medical_reports WHERE patient_id=?",
        "symptom_assessments": "SELECT symptoms,urgency,ai_summary,created_at FROM symptom_assessments WHERE patient_id=?",
    }
    out = {}
    with connect() as con:
        for key, sql in queries.items():
            out[key] = [dict(r) for r in con.execute(sql, (uid,)).fetchall()]
    return out
