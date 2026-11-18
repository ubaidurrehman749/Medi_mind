import re
import streamlit as st
from core import ai, emergency
from core.db import connect
from chat_page import _context

PROMPT = """Symptom check request (patient-reported, not verified).
Symptoms: {symptoms}
Started: {onset}
Severity (1-10): {severity}
Pattern: {pattern}
Other details: {extra}

Reply in the same language/script as the symptoms text.
The FIRST LINE must be exactly: URGENCY: <Emergency|Urgent|Routine|Self-care>
Then give, briefly and simply:
1. Possible explanations (possibilities only, NOT a diagnosis)
2. Warning signs that mean they should seek emergency care
3. What to do next (general self-care information only; no medicine names or doses)
4. One or two questions to discuss with a doctor"""

LEVELS = {"emergency": "Emergency", "urgent": "Urgent", "routine": "Routine",
          "self-care": "Self-care"}


def _save(uid, symptoms, urgency, summary):
    with connect() as con:
        con.execute(
            "INSERT INTO symptom_assessments(patient_id,symptoms,urgency,ai_summary) "
            "VALUES(?,?,?,?)", (uid, symptoms, urgency, summary))


def _past(uid):
    with connect() as con:
        rows = con.execute(
            "SELECT symptoms,urgency,created_at FROM symptom_assessments "
            "WHERE patient_id=? ORDER BY id DESC LIMIT 5", (uid,)).fetchall()
    return [dict(r) for r in rows]


def _show(level, body):
    if level == "Emergency":
        st.error("🚨 Emergency: foran emergency care lein (Rescue 1122).")
    elif level == "Urgent":
        st.warning("⚠️ Urgent: jald az jald doctor se check karwayein.")
    elif level == "Routine":
        st.info("🩺 Routine: doctor se aam appointment lein.")
    elif level == "Self-care":
        st.success("🌿 Self-care: aam ehtiyat; halat bigray to doctor se milein.")
    else:
        st.warning("Urgency tay nahi ho saki. Ehtiyatan doctor se mashwara karein.")
    st.write(body)
    st.caption("Yeh diagnosis nahi hai. Licensed doctor se mashwara zaroori hai.")


def page_symptoms(user):
    uid = user["id"]
    st.title("🩺 Symptom Checker")
    st.caption("Sirf maloomati rehnumai. Doctor ka badal nahi.")
    with st.form("symptoms"):
        symptoms = st.text_area("Aap ko kya takleef hai?", max_chars=800)
        onset = st.selectbox("Kab shuru hui?", [
            "Aaj", "1-2 din pehle", "3-7 din pehle", "1-4 hafte pehle",
            "1 mahine se zyada"])
        severity = st.slider("Shiddat (1 halki, 10 bohat shadeed)", 1, 10, 4)
        pattern = st.selectbox("Takleef kaisi hai?", [
            "Lagataar", "Aati jaati", "Barh rahi hai", "Behtar ho rahi hai"])
        extra = st.text_area("Aur kuch (optional)", max_chars=400)
        share = st.checkbox("Profile (umar, gender, allergies) AI se share karein", True)
        go = st.form_submit_button("Check karein")

    if go:
        if not symptoms.strip():
            st.warning("Pehle apni takleef likhein.")
        else:
            full = f"{symptoms} {extra}"
            res = emergency.check_emergency(full)
            if res["is_emergency"]:
                st.error(res["message"])
                _save(uid, symptoms, "Emergency", res["message"])
            else:
                msg = PROMPT.format(symptoms=symptoms, onset=onset, severity=severity,
                                    pattern=pattern, extra=extra or "none")
                with st.spinner("Jaiza le raha hoon..."):
                    reply, err = ai.chat([{"role": "user", "content": msg}],
                                         _context(uid) if share else "")
                if err:
                    st.error(err)
                else:
                    m = re.match(r"\s*URGENCY:\s*(Emergency|Urgent|Routine|Self-care)\s*\n?",
                                 reply, re.I)
                    level = LEVELS.get(m.group(1).lower()) if m else None
                    body = reply[m.end():] if m else reply
                    if severity >= 8 and level in ("Routine", "Self-care"):
                        level = "Urgent"  # shadeed takleef par ehtiyatan upar
                    _show(level, body)
                    _save(uid, symptoms, level or "Unclear", body)

    past = _past(uid)
    if past:
        with st.expander("Pichli assessments"):
            for p in past:
                st.write(f"**{p['urgency']}** - {p['symptoms'][:80]} ({p['created_at'][:10]})")
