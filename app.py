import streamlit as st
import json
import os
import requests
import google.generativeai as genai
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# --- 1. الإعدادات ---
NEWS_API_KEY = st.secrets["NEWS_API_KEY"]
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
EMAIL_PASSWORD = st.secrets["EMAIL_PASSWORD"]
EMAIL_SENDER = st.secrets["EMAIL_SENDER"]

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# --- 2. دالة جلب الأخبار المعدلة مع فحص الأخطاء ---
def fetch_and_summarize(topic):
    # استخدام بحث عام جداً لضمان النتائج
    url = f'https://newsapi.org/v2/everything?q={topic}&language=en&pageSize=3&apiKey={NEWS_API_KEY}'
    
    try:
        response = requests.get(url)
        data = response.json()
        articles = data.get('articles', [])
        
        if not articles:
            return "❌ خطأ: NewsAPI لم يجد أي مقالات لهذا الموضوع حالياً."

        summary_list = []
        summary_list.append(f"🤖 نشرة أخبار: {topic}\n" + "="*20 + "\n")
        
        for art in articles:
            title = art.get('title', 'بدون عنوان')
            desc = art.get('description', 'لا يوجد وصف')
            link = art.get('url', '#')
            
            # فحص إذا كان العنوان أو الوصف يحتوي على محتوى حقيقي
            if title and desc:
                prompt = f"Translate to Arabic and summarize in one short creative sentence with emoji: {title}. Context: {desc}"
                try:
                    ai_res = model.generate_content(prompt)
                    clean_text = ai_res.text.strip()
                    summary_list.append(f"⭐ {clean_text}\n🔗 {link}\n")
                except:
                    summary_list.append(f"⭐ {title} (ترجمة آلية)\n🔗 {link}\n")
        
        # تحويل القائمة إلى نص واحد طويل
        final_text = "\n".join(summary_list)
        return final_text

    except Exception as e:
        return f"❌ خطأ فني: {e}"

# --- 3. دالة الإرسال ---
def send_email(to_email, body):
    msg = MIMEMultipart()
    msg['From'] = EMAIL_SENDER
    msg['To'] = to_email
    msg['Subject'] = "نشرتك التقنية الذكية 🤖"
    msg.attach(MIMEText(body, 'plain', 'utf-8'))
    
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_SENDER, to_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        st.error(f"فشل إرسال الإيميل: {e}")
        return False

# --- 4. واجهة Streamlit ---
st.title("🚀 محرك الأخبار الذكي")

user_email = st.text_input("بريدك الإلكتروني:")
topic_choice = st.selectbox("اختر موضوع البحث:", ["Artificial Intelligence", "Cybersecurity", "Programming"])

if st.button("تشغيل النظام وإرسال النشرة"):
    if user_email:
        with st.spinner("1. جاري جلب الأخبار... 2. جاري التلخيص بـ Gemini..."):
            # تنفيذ الجلب
            content = fetch_and_summarize(topic_choice)
            
            # --- خطوة الفحص (Debug) ---
            st.subheader("📝 معاينة المحتوى المستخرج:")
            st.text_area("النص الذي سيتم إرساله:", value=content, height=200)
            
            # تنفيذ الإرسال إذا كان المحتوى غير فارغ
            if "❌" not in content:
                if send_email(user_email, content):
                    st.success("✅ تم توليد المحتوى وإرساله بنجاح!")
                    st.balloons()
            else:
                st.error("توقف النظام: لا يوجد محتوى صالح للإرسال.")
    else:
        st.warning("أدخل البريد الإلكتروني أولاً.")
