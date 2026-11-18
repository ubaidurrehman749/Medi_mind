import streamlit as st
from core import ai, chatlog, emergency, records


def _context(uid):
    p = records.get_profile(uid)
    parts = []
    if p.get("age"):
        parts.append(f"Age: {p['age']}")
    if p.get("gender"):
        parts.append(f"Gender: {p['gender']}")
    allergies = [a["allergen"] for a in records.list_allergies(uid)]
    if allergies:
        parts.append("Allergies: " + ", ".join(allergies))
    return "\n".join(parts)


def page_chat(user):
    uid = user["id"]
    st.title("💬 AI Doctor")
    st.caption("Sirf maloomati madad. Doctor ka badal nahi.")
    share = st.checkbox(
        "Meri profile (umar, gender, allergies) AI ke saath share karein", value=True
    )
    if st.button("Chat history saaf karein"):
        chatlog.clear_history(uid)
        st.rerun()

    for m in chatlog.load_history(uid):
        with st.chat_message("user" if m["role"] == "user" else "assistant"):
            st.write(m["content"])

    text = st.chat_input("Apna sawal likhein (English / اردو / Roman Urdu)", max_chars=1000)
    if not text:
        return
    with st.chat_message("user"):
        st.write(text)

    # Emergency check pehle: AI ka intezar nahi hota.
    res = emergency.check_emergency(text)
    if res["is_emergency"]:
        chatlog.save_message(uid, "user", text)
        chatlog.save_message(uid, "assistant", res["message"])
        with st.chat_message("assistant"):
            st.error(res["message"])
        return

    history = chatlog.load_history(uid, limit=12) + [{"role": "user", "content": text}]
    with st.chat_message("assistant"):
        with st.spinner("Soch raha hoon..."):
            reply, err = ai.chat(history, _context(uid) if share else "")
        if err:
            st.error(err + " Aap ka sawal save nahi hua, dobara bhej dein.")
            return
        st.write(reply)
    chatlog.save_message(uid, "user", text)
    chatlog.save_message(uid, "assistant", reply)
