import hashlib
import hmac
import os
import re
import sqlite3
from . import db

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
ITER = 200_000


def _hash(password, salt):
    return hashlib.pbkdf2_hmac("sha256", password.encode(), salt, ITER).hex()


def register(email, password, full_name, role, consent):
    """Returns (user_dict, None) ya (None, error_message)."""
    email = email.strip().lower()
    full_name = full_name.strip()
    if role not in ("patient", "doctor"):
        return None, "Invalid role."
    if not EMAIL_RE.match(email):
        return None, "Valid email likhein."
    if len(password) < 8:
        return None, "Password kam az kam 8 characters ka ho."
    if not full_name or len(full_name) > 100:
        return None, "Naam zaroori hai (max 100 characters)."
    if not consent:
        return None, "Aage barhne ke liye consent zaroori hai."
    salt = os.urandom(16)
    try:
        with db.connect() as con:
            cur = con.execute(
                "INSERT INTO users(email,password_hash,salt,full_name,role) "
                "VALUES(?,?,?,?,?)",
                (email, _hash(password, salt), salt.hex(), full_name, role),
            )
            uid = cur.lastrowid
            con.execute(
                "INSERT INTO user_consents(user_id,purpose,granted) VALUES(?,?,1)",
                (uid, "data_processing_and_ai_assistance"),
            )
            if role == "doctor":
                con.execute("INSERT INTO doctor_profiles(user_id) VALUES(?)", (uid,))
    except sqlite3.IntegrityError:
        return None, "Yeh email pehle se registered hai."
    return {"id": uid, "email": email, "full_name": full_name, "role": role}, None


def login(email, password):
    with db.connect() as con:
        r = con.execute(
            "SELECT * FROM users WHERE email=?", (email.strip().lower(),)
        ).fetchone()
    if not r:
        return None
    expected = _hash(password, bytes.fromhex(r["salt"]))
    if not hmac.compare_digest(expected, r["password_hash"]):
        return None
    return {
        "id": r["id"],
        "email": r["email"],
        "full_name": r["full_name"],
        "role": r["role"],
    }
