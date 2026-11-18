from .db import connect


def get_profile(uid):
    with connect() as con:
        r = con.execute(
            "SELECT * FROM patient_profiles WHERE user_id=?", (uid,)
        ).fetchone()
        return dict(r) if r else {}


def save_profile(uid, age, gender, blood_group, family_history):
    with connect() as con:
        con.execute(
            """INSERT INTO patient_profiles(user_id,age,gender,blood_group,family_history)
               VALUES(?,?,?,?,?) ON CONFLICT(user_id) DO UPDATE SET
               age=excluded.age, gender=excluded.gender,
               blood_group=excluded.blood_group,
               family_history=excluded.family_history""",
            (uid, age, gender, blood_group, family_history),
        )


def add_allergy(uid, allergen, reaction=""):
    with connect() as con:
        con.execute(
            "INSERT INTO allergies(patient_id,allergen,reaction) VALUES(?,?,?)",
            (uid, allergen.strip(), reaction.strip()),
        )


def list_allergies(uid):
    with connect() as con:
        rows = con.execute(
            "SELECT id,allergen,reaction FROM allergies WHERE patient_id=?", (uid,)
        )
        return [dict(r) for r in rows]


def delete_allergy(uid, allergy_id):
    with connect() as con:
        con.execute(
            "DELETE FROM allergies WHERE id=? AND patient_id=?", (allergy_id, uid)
        )
