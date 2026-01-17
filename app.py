
import streamlit as st
import json
import os

st.set_page_config(page_title="News AI", page_icon="🤖")
st.title("🤖 نظام النشرة الإخبارية الذكية")

with st.form(key="reg_form"):
    name = st.text_input("الاسم الكامل")
    email = st.text_input("البريد الإلكتروني")
    topics = st.multiselect("اختر اهتماماتك:", ["الذكاء الاصطناعي", "الأمن السيبراني", "البرمجة", "الاقتصاد"])
    submit = st.form_submit_button("اشترك الآن ✅")

if submit:
    if name and email and topics:
        user = {"name": name, "email": email, "interests": topics}
        try:
            if os.path.exists('subscribers.json'):
                with open('subscribers.json', 'r', encoding='utf-8') as file:
                    data = json.load(file)
            else: data = []
            data.append(user)
            with open('subscribers.json', 'w', encoding='utf-8') as file:
                json.dump(data, file, ensure_ascii=False, indent=4)
            st.success(f"أهلاً بك يا {name}! تم تسجيلك.")
        except Exception as e: st.error(f"خطأ: {e}")
    else: st.warning("أكمل البيانات")
