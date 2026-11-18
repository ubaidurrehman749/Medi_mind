import json

import streamlit as st
from core import emergency, history, records

DISCLAIMER = (
    "⚠️ MediMind AI sirf maloomati madad hai. Yeh licensed doctor ka badal nahi "
    "aur diagnosis ya dawai tajweez nahi karta."
)


def page_home(user):
    st.title(f"Khush aamdeed, {user['full_name']} 👋")
    st.write("Aap ka role:", f"**{user['role']}**")
    st.info(DISCLAIMER)
    if user["role"] == "patient":
        st.success(
            "Menu se AI Doctor, Symptom Checker, Medical Reports, Medicines aur "
            "Health Records istemal karein. Emergency mein foran Rescue 1122 par call karein."
        )
    else:
        st.success("Doctor portal abhi tayyar ho raha hai (Phase 2).")


def page_emergency():
    st.title("🚨 Emergency Check")
    st.caption("Yeh check internet/AI ke baghair chalta hai.")
    text = st.text_area(
        "Apni takleef likhein (English / اردو / Roman Urdu)", max_chars=1000
    )
    if st.button("Check karein"):
        res = emergency.check_emergency(text)
        if res["is_emergency"]:
            st.error(res["message"])
            st.write("Warning signs mile:", ", ".join(res["reasons"]))
        elif text.strip():
            st.success(
                "Koi foran emergency alamat nahi mili. Lekin agar halat bigarti hai "
                "ya aap fikarmand hain to doctor se rabta karein."
            )
        else:
            st.warning("Pehle takleef likhein.")
    st.caption("Pakistan: Rescue 1122 (apne ilaqe mein coverage verify karein).")


def page_records(user):
    uid = user["id"]
    st.title("📋 Health Records")
    p = records.get_profile(uid)
    with st.form("profile"):
        age = st.number_input("Umar", 0, 120, int(p.get("age") or 0))
        genders = ["", "Male", "Female", "Other"]
        gender = st.selectbox(
            "Gender", genders, index=genders.index(p.get("gender") or "")
        )
        blood = st.text_input(
            "Blood group", p.get("blood_group") or "", max_chars=5
        )
        fam = st.text_area(
            "Family history (optional)", p.get("family_history") or "", max_chars=500
        )
        if st.form_submit_button("Save profile"):
            records.save_profile(uid, age, gender, blood, fam)
            st.success("Saved.")

    st.subheader("Allergies")
    for a in records.list_allergies(uid):
        c1, c2 = st.columns([4, 1])
        extra = f"- {a['reaction']}" if a["reaction"] else ""
        c1.write(f"**{a['allergen']}** {extra}")
        if c2.button("Delete", key=f"d{a['id']}"):
            records.delete_allergy(uid, a["id"])
            st.rerun()
    with st.form("allergy", clear_on_submit=True):
        al = st.text_input("Allergen", max_chars=100)
        rx = st.text_input("Reaction (optional)", max_chars=200)
        if st.form_submit_button("Add allergy") and al.strip():
            records.add_allergy(uid, al, rx)
            st.rerun()

    st.subheader("Medical History")
    st.caption("Purani bimariyan, surgeries ya lambi bimari (jaise Diabetes, Asthma).")
    items = history.list_items(uid)
    for h in items:
        c1, c2 = st.columns([4, 1])
        note = f"- {h['notes']}" if h["notes"] else ""
        c1.write(f"**{h['condition']}** {note}")
        if c2.button("Delete", key=f"dh{h['id']}"):
            history.delete_item(uid, h["id"])
            st.rerun()
    if not items:
        st.write("Abhi koi history darj nahi.")
    with st.form("hist", clear_on_submit=True):
        cond = st.text_input("Bimari / surgery", max_chars=120)
        notes = st.text_input("Tafseel (optional, jaise kab se)", max_chars=200)
        if st.form_submit_button("History add karein") and cond.strip():
            history.add_item(uid, cond, notes)
            st.rerun()

    st.subheader("Mera data")
    st.caption("Apna saara record download karein. Allergies ya history upar se delete kar sakte hain.")
    st.download_button(
        "Mera data download karein (JSON)",
        data=json.dumps(history.export_all(uid), ensure_ascii=False, indent=2),
        file_name="medimind_data.json",
        mime="application/json",
    )


def page_about():
    st.title("About MediMind AI")
    st.write(
        "Free-first, open-source healthcare assistant (MVP). Regulatory compliance "
        "(HIPAA/local) ka koi assessment nahi hua; sirf synthetic data istemal karein."
    )
    st.info(DISCLAIMER)
