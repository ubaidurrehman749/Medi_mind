import streamlit as st
from core import ai, reports

TYPES = ["CBC", "LFT", "RFT", "Lipid Profile", "Blood Glucose",
         "Thyroid Profile", "Urine Examination", "Other"]
ICON = {"Low": "⬇️ Low", "High": "⬆️ High", "Normal": "✅ Normal"}

PROMPT = """Explain this lab report to a patient in simple language.
Report type: {rtype}
Answer language: {lang}
Values outside the report's own reference range (computed by code, not by you):
{flags}

Report text (OCR/PDF extracted, may contain errors):
{text}

Rules:
- Start with a 2-line plain summary.
- For each flagged value: what the test measures and what a low/high result can possibly
  mean in general. Do NOT diagnose any disease from lab values.
- Mention limitations: one test only, OCR errors possible, lab ranges differ, doctor must
  interpret with symptoms and history.
- No medicine names, doses, or treatment advice.
- End with 3 questions the patient can ask their doctor.
- If a value looks unreadable, say so instead of guessing."""


def page_reports(user):
    uid = user["id"]
    st.title("🧪 Medical Reports")
    st.caption("Sirf maloomati wazahat. Diagnosis nahi. Asli report sirf doctor samjhata hai.")
    st.warning("Abhi sirf demo/synthetic reports upload karein.")

    rtype = st.selectbox("Report ki qism", TYPES)
    lang = st.selectbox("Jawab ki zubaan", ["Roman Urdu", "English", "اردو"])
    consent = st.checkbox("Main report ka text AI ko bhejne ki ijazat deta/deti hoon.")
    up = st.file_uploader("Report upload karein (PDF, JPG, PNG, 5 MB tak)",
                          type=["pdf", "jpg", "jpeg", "png"])

    if st.button("Report samjhein"):
        if not consent:
            st.warning("Pehle ijazat wala box tick karein.")
        elif up is None:
            st.warning("Pehle file upload karein.")
        else:
            with st.spinner("Report parh raha hoon..."):
                text, err = reports.extract_text(up.name, up.getvalue())
            if err:
                st.error(err)
            else:
                flags = reports.find_flags(text)
                if flags:
                    st.subheader("Values (report ki apni range ke mutabiq)")
                    st.dataframe(
                        [{"Test": f["test"], "Value": f"{f['value']} {f['unit']}",
                          "Range": f["range"], "Status": ICON[f["status"]]} for f in flags],
                        use_container_width=True)
                else:
                    st.info("Range wali values khud nahi mil sakeen. AI wazahat phir bhi dega.")
                flag_txt = "\n".join(
                    f"- {f['test']}: {f['value']} {f['unit']} (range {f['range']}) -> {f['status']}"
                    for f in flags if f["status"] != "Normal") or "None detected by code"
                msg = PROMPT.format(rtype=rtype, lang=lang, flags=flag_txt, text=text[:6000])
                with st.spinner("Wazahat tayyar ho rahi hai..."):
                    reply, aerr = ai.chat([{"role": "user", "content": msg}])
                if aerr:
                    st.error(aerr)
                else:
                    st.subheader("Saada zubaan mein wazahat")
                    st.write(reply)
                    st.caption("AI ki wazahat hai, diagnosis nahi. Doctor se zaroor milein.")
                    reports.save_report(uid, up.name, rtype, text, reply)

    past = reports.list_reports(uid)
    if past:
        st.subheader("Pichli reports")
        for r in past:
            with st.expander(f"{r['report_type']} - {r['filename']} ({r['created_at'][:10]})"):
                st.write(r["ai_summary"] or "Summary nahi hai.")
                if st.button("Delete", key=f"dr{r['id']}"):
                    reports.delete_report(uid, r["id"])
                    st.rerun()
