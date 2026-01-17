import streamlit as st
import json
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# جلب الإعدادات من Secrets
NEWS_API_KEY = st.secrets["NEWS_API_KEY"]
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
EMAIL_PASSWORD = st.secrets["EMAIL_PASSWORD"]
EMAIL_SENDER = st.secrets["EMAIL_SENDER"]

st.title("🤖 نظام النشرة الإخبارية الذكية")

# --- قسم التسجيل ---
with st.form(key="reg_form"):
    name = st.text_input("الاسم الكامل")
    email = st.text_input("البريد الإلكتروني")
    topics = st.multiselect("اختر اهتماماتك:", ["الذكاء الاصطناعي", "الأمن السيبراني", "البرمجة", "الاقتصاد"])
    submit = st.form_submit_button("اشترك الآن ✅")

if submit:
    # (كود الحفظ في subscribers.json كما هو)
    st.success(f"تم تسجيلك يا {name}!")

# --- قسم الإرسال التجريبي (هذا ما سيجعلك تستلم إيميل الآن) ---
st.divider()
st.subheader("🚀 تجربة الإرسال")
test_email = st.text_input("أدخل إيميلك المسجل لتجربة الإرسال الفوري:")

if st.button("أرسل لي النشرة الآن 📧"):
    with st.spinner("جاري جلب الأخبار وتلخيصها بالذكاء الاصطناعي..."):
        # هنا سنضع كود الإرسال الذي جربناه في كولاب
        # سيقوم بجلب الأخبار بناءً على اهتمامات المستخدم وإرسالها
        st.info("سيتم إرسال النشرة إلى بريدك خلال لحظات...")
        # (ملاحظة: تأكد من ربط الدوال التي كتبناها في news_engine هنا)
