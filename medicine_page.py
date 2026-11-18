import streamlit as st
from core import ai, emergency, meds, records

PROMPT = """Give general educational information about this medicine: {name}
Patient's question (may be empty): {question}
Answer language: {lang}
Patient's allergies: {allergies}
Patient's current medicines: {current}

Use these short sections:
1. Common uses
2. Common side effects
3. Precautions (who should be careful)
4. Possible allergy or interaction concerns with the patient's listed allergies/medicines
   (for professional review; say "cannot confirm" if unsure)
5. When to contact a doctor or pharmacist

Rules:
- Do NOT tell the patient to start, stop, skip or change any medicine or dose. Do not
  suggest doses. If asked about changing a dose, tell them to ask their doctor/pharmacist.
- If you do not recognize the medicine name, say so. Never guess or invent facts.
- Keep it short and simple."""


def page_medicines(user):
    uid = user["id"]
    st.title("💊 Medicines")
    st.caption("Sirf maloomati. Dawai shuru, band ya dose tabdeel karna doctor ka kaam hai.")

    st.subheader("Meri dawaiyan")
    my = meds.list_meds(uid)
    for m in my:
        c1, c2 = st.columns([4, 1])
        extra = " | ".join(x for x in (m["dosage"], m["schedule"]) if x)
        c1.write(f"**{m['name']}** {('- ' + extra) if extra else ''}")
        if c2.button("Delete", key=f"dm{m['id']}"):
            meds.delete_med(uid, m["id"])
            st.rerun()
    if not my:
        st.write("Abhi koi dawai save nahi.")
    with st.form("addmed", clear_on_submit=True):
        name = st.text_input("Dawai ka naam", max_chars=100)
        dosage = st.text_input("Dose (jaisa doctor ne likha)", max_chars=60)
        sched = st.text_input("Kab lena hai (jaise subah/shaam)", max_chars=60)
        if st.form_submit_button("Dawai save karein") and name.strip():
            meds.add_med(uid, name, dosage, sched)
            st.rerun()

    st.divider()
    st.subheader("Dawai ki maloomat")
    mname = st.text_input("Kis dawai ke baare mein janna hai?", max_chars=100)
    question = st.text_area("Koi khaas sawal (optional)", max_chars=300)
    lang = st.selectbox("Jawab ki zubaan", ["Roman Urdu", "English", "اردو"])
    if st.button("Maloomat dikhayein"):
        if not mname.strip():
            st.warning("Pehle dawai ka naam likhein.")
            return
        res = emergency.check_emergency(f"{mname} {question}")
        if res["is_emergency"]:
            st.error(res["message"])
            return
        allergies = [a["allergen"] for a in records.list_allergies(uid)]
        hits = [a for a in allergies
                if a.lower() in mname.lower() or mname.lower() in a.lower()]
        if hits:
            st.error("⚠️ Aap ki darj allergy ke saath naam milta hai: " + ", ".join(hits)
                     + ". Is dawai se pehle doctor/pharmacist se poochhein.")
        msg = PROMPT.format(
            name=mname, question=question or "none", lang=lang,
            allergies=", ".join(allergies) or "none recorded",
            current=", ".join(m["name"] for m in my) or "none recorded")
        with st.spinner("Maloomat jama ho rahi hain..."):
            reply, err = ai.chat([{"role": "user", "content": msg}])
        if err:
            st.error(err)
        else:
            st.write(reply)
            st.info("🤖 Yeh AI ki tayyar ki hui wazahat hai, kisi verified source se tasdeeq "
                    "shuda nahi. Dawai ke patte (leaflet) ya pharmacist se zaroor mila lein. "
                    "Allergy check mein sirf seedha naam code ne dekha; baqi AI ka andaza hai.")
