import os
import sqlite3
from contextlib import contextmanager
from . import config

SCHEMA = """
PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS users(
  id INTEGER PRIMARY KEY, email TEXT UNIQUE NOT NULL, password_hash TEXT NOT NULL,
  salt TEXT NOT NULL, full_name TEXT NOT NULL, role TEXT NOT NULL CHECK(role IN ('patient','doctor')),
  language TEXT DEFAULT 'English', created_at TEXT DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS patient_profiles(
  user_id INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
  age INTEGER, gender TEXT, blood_group TEXT, family_history TEXT);
CREATE TABLE IF NOT EXISTS doctor_profiles(
  user_id INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
  specialty TEXT, license_no TEXT, verified INTEGER DEFAULT 0);
CREATE TABLE IF NOT EXISTS medical_history(
  id INTEGER PRIMARY KEY, patient_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  condition TEXT NOT NULL, notes TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS allergies(
  id INTEGER PRIMARY KEY, patient_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  allergen TEXT NOT NULL, reaction TEXT);
CREATE TABLE IF NOT EXISTS medications(
  id INTEGER PRIMARY KEY, patient_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  name TEXT NOT NULL, dosage TEXT, schedule TEXT, active INTEGER DEFAULT 1);
CREATE TABLE IF NOT EXISTS medical_reports(
  id INTEGER PRIMARY KEY, patient_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  filename TEXT, report_type TEXT, extracted_text TEXT, ai_summary TEXT,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS symptom_assessments(
  id INTEGER PRIMARY KEY, patient_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  symptoms TEXT, urgency TEXT, ai_summary TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS appointments(
  id INTEGER PRIMARY KEY, patient_id INTEGER NOT NULL REFERENCES users(id),
  doctor_id INTEGER NOT NULL REFERENCES users(id), slot TEXT NOT NULL,
  status TEXT DEFAULT 'booked', created_at TEXT DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS consultations(
  id INTEGER PRIMARY KEY, appointment_id INTEGER REFERENCES appointments(id),
  patient_id INTEGER NOT NULL REFERENCES users(id), doctor_id INTEGER NOT NULL REFERENCES users(id),
  status TEXT DEFAULT 'open', created_at TEXT DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS consultation_notes(
  id INTEGER PRIMARY KEY, consultation_id INTEGER NOT NULL REFERENCES consultations(id) ON DELETE CASCADE,
  note TEXT NOT NULL, is_ai_draft INTEGER DEFAULT 0, doctor_approved INTEGER DEFAULT 0,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS chat_history(
  id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  role TEXT NOT NULL, content TEXT NOT NULL, created_at TEXT DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS health_metrics(
  id INTEGER PRIMARY KEY, patient_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  metric TEXT NOT NULL, value REAL NOT NULL, unit TEXT, recorded_at TEXT DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS reminders(
  id INTEGER PRIMARY KEY, patient_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  title TEXT NOT NULL, remind_at TEXT, done INTEGER DEFAULT 0);
CREATE TABLE IF NOT EXISTS user_consents(
  id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  purpose TEXT NOT NULL, granted INTEGER NOT NULL, created_at TEXT DEFAULT CURRENT_TIMESTAMP);
"""


@contextmanager
def connect():
    d = os.path.dirname(config.DB_PATH)
    if d:
        os.makedirs(d, exist_ok=True)
    con = sqlite3.connect(config.DB_PATH)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    try:
        yield con
        con.commit()
    finally:
        con.close()


def init_db():
    with connect() as con:
        con.executescript(SCHEMA)
