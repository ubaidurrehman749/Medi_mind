import streamlit as st
from core import auth, db
import views
import chat_page
import symptom_page
import report_page
import medicine_page

st.set_page_config(page_title="MediMind AI", page_icon="🩺", layout="wide")
db.init_db()

st.markdown(
    """<style>
.stApp{background:linear-gradient(135deg,#eaf6fb,#f4fbfa)}
[data-testid="stSidebar"]{background:rgba(14,116,144,.08);backdrop-filter:blur(10px)}
h1,h2,h3{color:#0e7490}
</style>""",
    unsafe_allow_html=True,
)

NAV = {
    "patient": [
        "Home", "AI Doctor", "Symptom Checker", "Medical Reports", "Medicines",
        "Emergency Check", "Health Records", "About",
    ],
    "doctor": ["Home", "Emergency Check", "About"],
}


def auth_screen():
    st.title("🩺 MediMind AI")
    st.caption("Your Personal AI Health Companion")
    st.info(views.DISCLAIMER)
    tab_in, tab_up = st.tabs(["Login", "Register"])
    with tab_in:
        with st.form("login"):
            email = st.text_input("Email")
            pw = st.text_input("Password", type="password")
            if st.form_submit_button("Login"):
                user = auth.login(email, pw)
                if user:
                    st.session_state.user = user
                    st.rerun()
                st.error("Email ya password ghalat hai.")
    with tab_up:
        with st.form("register"):
            name = st.text_input("Poora naam")
            email = st.text_input("Email", key="re")
            pw = st.text_input(
                "Password (kam az kam 8 characters)", type="password", key="rp"
            )
            role = st.selectbox("Role", ["patient", "doctor"])
            consent = st.checkbox(
                "Main apni maloomat ki processing aur AI madad ke liye razamand "
                "hoon. Main sirf synthetic/demo data istemal karunga."
            )
            if st.form_submit_button("Register"):
                user, err = auth.register(email, pw, name, role, consent)
                if err:
                    st.error(err)
                else:
                    st.session_state.user = user
                    st.rerun()


user = st.session_state.get("user")
if not user:
    auth_screen()
    st.stop()

with st.sidebar:
    st.header("🩺 MediMind AI")
    page = st.radio("Menu", NAV[user["role"]])
    if st.button("Logout"):
        st.session_state.clear()
        st.rerun()

if page == "Home":
    views.page_home(user)
elif page == "AI Doctor":
    chat_page.page_chat(user)
elif page == "Symptom Checker":
    symptom_page.page_symptoms(user)
elif page == "Medical Reports":
    report_page.page_reports(user)
elif page == "Medicines":
    medicine_page.page_medicines(user)
elif page == "Emergency Check":
    views.page_emergency()
elif page == "Health Records":
    views.page_records(user)
else:
    views.page_about()
