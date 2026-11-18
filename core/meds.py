from .db import connect


def add_med(uid, name, dosage="", schedule=""):
    with connect() as con:
        con.execute(
            "INSERT INTO medications(patient_id,name,dosage,schedule) VALUES(?,?,?,?)",
            (uid, name.strip(), dosage.strip(), schedule.strip()),
        )


def list_meds(uid):
    with connect() as con:
        rows = con.execute(
            "SELECT id,name,dosage,schedule FROM medications "
            "WHERE patient_id=? AND active=1 ORDER BY id",
            (uid,),
        ).fetchall()
    return [dict(r) for r in rows]


def delete_med(uid, med_id):
    with connect() as con:
        con.execute(
            "DELETE FROM medications WHERE id=? AND patient_id=?", (med_id, uid)
        )
