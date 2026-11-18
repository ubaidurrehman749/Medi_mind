import streamlit as st
from core import emergency, records

DISCLAIMER = (
    "⚠️ MediMind AI sirf maloomati madad hai. Yeh licensed doctor ka badal nahi "
    "aur diagnosis ya dawai tajweez nahi karta."
)


def page_home(user):
    st.title(f"Khush aamdeed, {user['full_name']} 👋")
    st.write("Aap ka role:", f"**{user['role']}**")
    st.info(DISCLAIMER)
    st.success(
        "Phase 1 Step 1 tayyar: login, roles, database, emergency detection. "
        "Agla step: AI Doctor Chat aur Symptom Checker."
    )


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
    st.title("📋 Health Records")
    p = records.get_profile(user["id"])
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
            records.save_profile(user["id"], age, gender, blood, fam)
            st.success("Saved.")

    st.subheader("Allergies")
    for a in records.list_allergies(user["id"]):
        c1, c2 = st.columns([4, 1])
        extra = f"- {a['reaction']}" if a["reaction"] else ""
        c1.write(f"**{a['allergen']}** {extra}")
        if c2.button("Delete", key=f"d{a['id']}"):
            records.delete_allergy(user["id"], a["id"])
            st.rerun()
    with st.form("allergy", clear_on_submit=True):
        al = st.text_input("Allergen", max_chars=100)
        rx = st.text_input("Reaction (optional)", max_chars=200)
        if st.form_submit_button("Add allergy") and al.strip():
            records.add_allergy(user["id"], al, rx)
            st.rerun()


def page_about():
    st.title("About MediMind AI")
    st.write(
        "Free-first, open-source healthcare assistant (MVP). Regulatory compliance "
        "(HIPAA/local) ka koi assessment nahi hua; sirf synthetic data istemal karein."
    )
    st.info(DISCLAIMER)
