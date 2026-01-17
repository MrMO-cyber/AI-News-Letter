import streamlit as st
import json
import os
import requests
import google.generativeai as genai
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# --- الإعدادات من Secrets ---
NEWS_API_KEY = st.secrets["NEWS_API_KEY"]
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
EMAIL_PASSWORD = st.secrets["EMAIL_PASSWORD"]
EMAIL_SENDER = st.secrets["EMAIL_SENDER"]

# إعداد Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# --- الدوال الأساسية ---
def fetch_and_summarize(topic):
    url = f'https://newsapi.org/v2/everything?q={topic}&language=ar&sortBy=publishedAt&pageSize=2&apiKey={NEWS_API_KEY}'
    response = requests.get(url)
    articles = response.json().get('articles', [])
    summary_text = ""
    for art in articles:
        prompt = f"لخص هذا الخبر بأسلوب ممتع في جملتين مع إيموجي: {art['title']} - {art['description']}"
        try:
            res = model.generate_content(prompt)
            summary_text += f"📌 {art['title']}\n📝 {res.text}\n🔗 {art['url']}\n\n"
        except:
            summary_text += f"📌 {art['title']}\n🔗 {art['url']}\n\n"
    return summary_text

def send_mail(to_email, content):
    msg = MIMEMultipart()
    msg['From'] = EMAIL_SENDER
    msg['To'] = to_email
    msg['Subject'] = "نشرتك الإخبارية الذكية 🤖"
    msg.attach(MIMEText(content, 'plain'))
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(EMAIL_SENDER, EMAIL_PASSWORD)
    server.sendmail(EMAIL_SENDER, to_email, msg.as_string())
    server.quit()

# --- واجهة الموقع ---
st.set_page_config(page_title="AI Newsletter", page_icon="🚀")
st.title("🤖 نظام النشرة الإخبارية الذكية")

tab1, tab2 = st.tabs(["📝 تسجيل مشترك جديد", "🚀 إرسال النشرة الآن"])

with tab1:
    with st.form("reg_form"):
        name = st.text_input("الاسم")
        email = st.text_input("البريد الإلكتروني")
        topics = st.multiselect("الاهتمامات:", ["الذكاء الاصطناعي", "الأمن السيبراني", "البرمجة"])
        if st.form_submit_button("اشترك"):
            # منطق الحفظ (نفس الكود السابق)
            st.success("تم الحفظ!")

with tab2:
    st.subheader("تجربة إرسال فورية")
    user_email = st.text_input("أدخل إيميلك المسجل لإرسال النشرة له فوراً:")
    if st.button("أرسل لي الأخبار الآن 📧"):
        with st.spinner("جاري العمل..."):
            # في الواقع، سنبحث عن اهتمامات هذا الإيميل من الملف، لكن للتجربة سنأخذ "الذكاء الاصطناعي"
            news_content = fetch_and_summarize("الذكاء الاصطناعي")
            send_mail(user_email, news_content)
            st.success(f"تم الإرسال لـ {user_email} بنجاح!")
