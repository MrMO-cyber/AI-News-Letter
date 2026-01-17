import streamlit as st
import json
import os
import requests
import google.generativeai as genai
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# --- 1. الإعدادات من Secrets ---
# تأكد من إضافة هذه المفاتيح في Streamlit Cloud Settings -> Secrets
NEWS_API_KEY = st.secrets["NEWS_API_KEY"]
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
EMAIL_PASSWORD = st.secrets["EMAIL_PASSWORD"]
EMAIL_SENDER = st.secrets["EMAIL_SENDER"]

# --- 2. إعداد نموذج الذكاء الاصطناعي (Gemini) ---
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# --- 3. محرك الأخبار والذكاء الاصطناعي ---
def fetch_and_summarize(topic):
    # جلب الأخبار (نستخدم كلمات بحث عامة لضمان النتائج)
    url = f'https://newsapi.org/v2/everything?q={topic}&language=ar&sortBy=publishedAt&pageSize=3&apiKey={NEWS_API_KEY}'
    
    try:
        response = requests.get(url)
        articles = response.json().get('articles', [])
        
        if not articles:
            return f"لم نجد أخباراً جديدة اليوم حول: {topic}."

        full_content = f"🤖 نشرتك الذكية حول {topic}:\n\n"
        
        for art in articles:
            title = art['title']
            desc = art['description'] if art['description'] else "لا يوجد وصف متاح."
            link = art['url']
            
            # صياغة الطلب للذكاء الاصطناعي
            prompt = f"لخص الخبر التالي بأسلوب مشوق في جملة واحدة مع إيموجي:\nالعنوان: {title}\nالوصف: {desc}"
            
            try:
                ai_response = model.generate_content(prompt)
                summary = ai_response.text
            except:
                summary = "خبر جديد ومهم في هذا المجال."
            
            full_content += f"⭐ {title}\n📝 {summary}\n🔗 اقرأ أكثر: {link}\n\n"
            
        return full_content
    except Exception as e:
        return f"حدث خطأ في جلب الأخبار: {e}"

# --- 4. محرك إرسال الإيميلات ---
def send_newsletter_email(recipient_email, content):
    msg = MIMEMultipart()
    msg['From'] = EMAIL_SENDER
    msg['To'] = recipient_email
    msg['Subject'] = "نشرتك الإخبارية الذكية 🤖"
    
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

# --- 5. واجهة المستخدم (Streamlit) ---
st.set_page_config(page_title="Smart News AI", page_icon="🚀", layout="centered")

st.title("🤖 نظام النشرة الإخبارية الذكية")
st.markdown( "في قلب التقنية")

tab1, tab2 = st.tabs(["📝 تسجيل مشترك", "🚀 إرسال فوري"])

# --- تبويب التسجيل ---
with tab1:
    st.subheader("سجل اهتماماتك")
    with st.form("main_form", clear_on_submit=True):
        name = st.text_input("الاسم")
        email = st.text_input("البريد الإلكتروني")
        user_topics = st.multiselect("اختر اهتماماتك:", ["الذكاء الاصطناعي", "الأمن السيبراني", "البرمجة", "الاقتصاد الرقمي"])
        
        if st.form_submit_button("اشترك الآن"):
            if name and email and user_topics:
                # حفظ في ملف JSON (قاعدة بيانات بسيطة)
                user_data = {"name": name, "email": email, "interests": user_topics}
                try:
                    if os.path.exists('subscribers.json'):
                        with open('subscribers.json', 'r', encoding='utf-8') as f:
                            data = json.load(f)
                    else: data = []
                    data.append(user_data)
                    with open('subscribers.json', 'w', encoding='utf-8') as f:
                        json.dump(data, f, ensure_ascii=False, indent=4)
                    st.success(f"أهلاً بك يا {name}! تم حفظ بياناتك.")
                except: st.error("فشل حفظ البيانات.")
            else: st.warning("يرجى إكمال البيانات.")

# --- تبويب الإرسال الفوري (للتجربة) ---
with tab2:
    st.subheader("اختبر النظام الآن")
    target_email = st.text_input("أدخل بريدك الإلكتروني المسجل:")
    target_topic = st.selectbox("اختر موضوعاً لجلب أخباره:", ["الذكاء الاصطناعي", "الأمن السيبراني", "البرمجة"])
    
    if st.button("أرسل النشرة لإيميلي الآن 📧"):
        if target_email:
            with st.spinner("جاري تحليل الأخبار باستخدام Gemini AI..."):
                # 1. جلب وتلخيص
                newsletter_content = fetch_and_summarize(target_topic)
                
                # 2. عرض المحتوى في الموقع للتأكد
                st.info("المحتوى الذي تم توليده:")
                st.text(newsletter_content)
                
                # 3. الإرسال الفعلي
                success = send_newsletter_email(target_email, newsletter_content)
                if success:
                    st.success(f"تم إرسال النشرة بنجاح إلى {target_email}!")
                    st.balloons()
        else:
            st.error("يرجى كتابة البريد الإلكتروني أولاً.")
