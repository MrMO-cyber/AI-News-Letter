import streamlit as st
import json
import os
import requests
import google.generativeai as genai
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# --- 1. الإعدادات من Secrets ---
NEWS_API_KEY = st.secrets["NEWS_API_KEY"]
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
EMAIL_PASSWORD = st.secrets["EMAIL_PASSWORD"]
EMAIL_SENDER = st.secrets["EMAIL_SENDER"]

# --- 2. إعداد Gemini ---
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# --- 3. محرك الأخبار الذكي (English Search + Arabic Summary) ---
def fetch_and_summarize(topic):
    # البحث بالإنجليزية لضمان نتائج غنية ودقيقة
    url = f'https://newsapi.org/v2/everything?q={topic}&language=en&sortBy=publishedAt&pageSize=3&apiKey={NEWS_API_KEY}'
    
    try:
        response = requests.get(url)
        articles = response.json().get('articles', [])
        
        if not articles:
            return f"لم نجد أخباراً جديدة عالمية حول: {topic}."

        full_content = f"🤖 نشرتك الذكية المترجمة حول {topic}:\n\n"
        
        for art in articles:
            title = art['title']
            desc = art['description'] if art['description'] else "No description available."
            link = art['url']
            
            # نطلب من Gemini الترجمة والتلخيص بأسلوب ممتع
            prompt = f"""
            Translate and summarize this tech news into Arabic in a creative and engaging way.
            Use Emojis. The summary should be one concise sentence.
            Title: {title}
            Description: {desc}
            """
            
            try:
                ai_response = model.generate_content(prompt)
                summary = ai_response.text
            except:
                summary = "خبر تقني جديد يستحق المتابعة."
            
            full_content += f"⭐ {summary}\n🔗 المصدر: {link}\n\n"
            
        return full_content
    except Exception as e:
        return f"حدث خطأ تقني: {e}"

# --- 4. محرك الإرسال ---
def send_newsletter_email(recipient_email, content):
    msg = MIMEMultipart()
    msg['From'] = EMAIL_SENDER
    msg['To'] = recipient_email
    msg['Subject'] = "نشرتك التقنية العالمية المترجمة 🤖"
    msg.attach(MIMEText(content, 'plain', 'utf-8'))
    
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_SENDER, recipient_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        st.error(f"خطأ في الإرسال: {e}")
        return False

# --- 5. واجهة المستخدم ---
st.set_page_config(page_title="Global AI News", page_icon="🌐")

st.title("🌐 وكالة أنباء الذكاء الاصطناعي")
st.markdown("نجلب لك الأخبار من المصادر العالمية، نترجمها، ونلخصها لك بالذكاء الاصطناعي.")

tab1, tab2 = st.tabs(["📝 تسجيل", "🚀 إرسال فوري"])

with tab1:
    with st.form("reg_form", clear_on_submit=True):
        name = st.text_input("الاسم")
        email = st.text_input("البريد الإلكتروني")
        # كلمات البحث بالإنجليزية لنتائج أفضل في الـ API
        topic_map = {
            "الذكاء الاصطناعي": "Artificial Intelligence",
            "الأمن السيبراني": "Cybersecurity",
            "البرمجة": "Programming",
            "الفضاء": "Space Technology"
        }
        user_choice = st.multiselect("اهتماماتك:", list(topic_map.keys()))
        
        if st.form_submit_button("اشترك"):
            if name and email and user_choice:
                # منطق الحفظ (اختياري في هذه المرحلة)
                st.success(f"أهلاً بك يا {name}!")

with tab2:
    st.subheader("اختبر النظام (ترجمة فورية)")
    target_email = st.text_input("بريدك الإلكتروني:")
    # اختيار المواضيع بالانجليزية خلف الكواليس
    target_topic_ar = st.selectbox("اختر موضوعاً:", ["الذكاء الاصطناعي", "الأمن السيبراني", "البرمجة"])
    
    topic_mapping = {
        "الذكاء الاصطناعي": "Artificial Intelligence",
        "الأمن السيبراني": "Cybersecurity",
        "البرمجة": "Software Development"
    }

    if st.button("أرسل النشرة المترجمة الآن 📧"):
        if target_email:
            with st.spinner("جاري جلب الأخبار العالمية وترجمتها..."):
                content = fetch_and_summarize(topic_mapping[target_topic_ar])
                st.text_area("معاينة المحتوى قبل الإرسال:", content, height=200)
                if send_newsletter_email(target_email, content):
                    st.success("وصلت النشرة المترجمة لبريدك!")
                    st.balloons()
