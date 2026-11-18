"""Report files se text nikalna, values check karna, aur database mein save karna."""
import io
import re

from .db import connect

MAX_BYTES = 5 * 1024 * 1024
MAGIC = {"pdf": b"%PDF", "png": b"\x89PNG", "jpg": b"\xff\xd8", "jpeg": b"\xff\xd8"}

LINE_RE = re.compile(
    r"^(?P<name>[A-Za-z][A-Za-z0-9 ()/%.,-]{1,40}?)\s+"
    r"(?P<val>\d+(?:\.\d+)?)\s*(?P<unit>[A-Za-z%/µ0-9^.*]*)\s+"
    r"(?P<lo>\d+(?:\.\d+)?)\s*(?:-|–|to)\s*(?P<hi>\d+(?:\.\d+)?)"
)


def validate_file(filename, data):
    """Returns error message ya None."""
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in MAGIC:
        return "Sirf PDF, JPG ya PNG file chalegi."
    if len(data) > MAX_BYTES:
        return "File 5 MB se chhoti honi chahiye."
    if not data.startswith(MAGIC[ext]):
        return "File ka format ghalat hai ya kharab hai."
    return None


def extract_text(filename, data):
    """Returns (text, None) ya (None, error_message)."""
    err = validate_file(filename, data)
    if err:
        return None, err
    ext = filename.rsplit(".", 1)[-1].lower()
    try:
        if ext == "pdf":
            from pypdf import PdfReader
            reader = PdfReader(io.BytesIO(data))
            text = "\n".join((p.extract_text() or "") for p in reader.pages[:10])
            if len(text.strip()) < 20:
                return None, ("Is PDF mein text nahi mila (shayad scanned hai). "
                              "Report ki saaf photo (JPG/PNG) upload karein.")
            return text.strip(), None
        from PIL import Image
        import pytesseract
        img = Image.open(io.BytesIO(data))
        text = pytesseract.image_to_string(img)
        if len(text.strip()) < 20:
            return None, "Photo se text nahi parha ja saka. Saaf, seedhi aur roshan photo lein."
        return text.strip(), None
    except ImportError:
        return None, "Zaroori tools install nahi hain. requirements.txt aur packages.txt check karein."
    except Exception as e:  # tesseract missing, kharab file, wagaira
        if e.__class__.__name__ == "TesseractNotFoundError":
            return None, "OCR tool (tesseract) server par maujood nahi. packages.txt check karein."
        return None, "File parhne mein masla aaya. Doosri file try karein."


def find_flags(text):
    """Report ki un lines se values nikalta hai jin mein reference range likhi ho.
    Returns [{'test','value','unit','range','status'}]. AI ka istemal nahi hota."""
    out = []
    for line in text.splitlines():
        m = LINE_RE.match(line.strip())
        if not m:
            continue
        val, lo, hi = float(m["val"]), float(m["lo"]), float(m["hi"])
        if lo >= hi:
            continue
        status = "Low" if val < lo else "High" if val > hi else "Normal"
        out.append({"test": m["name"].strip(), "value": m["val"], "unit": m["unit"],
                    "range": f"{m['lo']} - {m['hi']}", "status": status})
    return out


def save_report(uid, filename, report_type, text, summary):
    with connect() as con:
        con.execute(
            "INSERT INTO medical_reports(patient_id,filename,report_type,extracted_text,ai_summary) "
            "VALUES(?,?,?,?,?)", (uid, filename, report_type, text, summary))


def list_reports(uid):
    with connect() as con:
        rows = con.execute(
            "SELECT id,filename,report_type,ai_summary,created_at FROM medical_reports "
            "WHERE patient_id=? ORDER BY id DESC LIMIT 20", (uid,)).fetchall()
    return [dict(r) for r in rows]


def delete_report(uid, report_id):
    with connect() as con:
        con.execute("DELETE FROM medical_reports WHERE id=? AND patient_id=?", (report_id, uid))
