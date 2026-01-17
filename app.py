import streamlit as st
import json
import os
import requests
import google.generativeai as genai
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# --- 1. الإعدادات وسحب المفاتيح من Secrets ---
NEWS_API_KEY = st.secrets["NEWS_API_KEY"]
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
EMAIL_PASSWORD = st.secrets["EMAIL_PASSWORD"]
EMAIL_SENDER = st.secrets["EMAIL_SENDER"]

# إعداد نموذج Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# --- 2. محرك الأخبار والذكاء الاصطناعي ---
def fetch_and_summarize_v3():
    # نستخدم قسم التكنولوجيا العالمي لضمان وجود محتوى دائم
    url = f'https://newsapi.org/v2/top-headlines?category=technology&language=en&pageSize=5&apiKey={NEWS_API_KEY}'
    
    try:
        response = requests.get(url)
        data = response.json()
        articles = data.get('articles', [])
        
        # إذا لم يجد في العناوين، نجرب البحث العام كخطة بديلة
        if not articles:
            url_backup = f'https://newsapi.org/v2/everything?q=technology&language=en&pageSize=3&apiKey={NEWS_API_KEY}'
            articles = requests.get(url_backup).json().get('articles', [])

        if not articles:
            return "❌ عذراً، لا توجد أخبار تقنية متاحة في الوقت الحالي."

        summary_list = [f"🤖 نشرتك التقنية الذكية | {st.date_input('التاريخ', disabled=True)}\n" + "="*30 + "\n"]
        
        for art in articles:
            title = art.get('title')
            link = art.get('url')
            if title and "[Removed]" not in title:
                # نطلب من Gemini الترجمة والتلخيص بأسلوب إبداعي
                prompt = f"Translate to Arabic and summarize this tech news in one catchy sentence with emojis: {title}"
                try:
                    ai_res = model.generate_content(prompt)
                    summary_list.append(f"⭐ {ai_res.text.strip()}\n🔗 المصدر: {link}\n")
                except:
                    # في حال فشل Gemini نضع العنوان الأصلي
                    summary_list.append(f"📌 {title}\n🔗 {link}\n")
        
        return "\n".join(summary_list)
    except Exception as e:
        return f"❌ خطأ فني: {e}"

# --- 3. محرك إرسال الإيميلات ---
def send_automated_email(target_email, body_content):
    msg = MIMEMultipart()
    msg['From'] = EMAIL_SENDER
    msg['To'] = target_email
    msg['Subject'] = "نشرة الذكاء الاصطناعي العالمية 🤖"
    msg.attach(MIMEText(body_content, 'plain', 'utf-8'))
    
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_SENDER, target_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        st.error(f"فشل الإرسال: {e}")
        return False

# --- 4. واجهة المستخدم (Streamlit UI) ---
st.set_page_config(page_title="Global Tech AI News", page_icon="🌐")

st.title("🌐 وكالة الأنباء التقنية الذكية")
st.markdown("""
بناءً على تخصصك في **علم البيانات**، هذا النظام يقوم بـ:
1. جلب أحدث عناوين التكنولوجيا العالمية.
2. استخدام **Gemini AI** لترجمة وتلخيص الأخبار فوراً.
3. إرسالها لبريدك الإلكتروني بضغطة زر.
""")

st.divider()

# خانة إدخال البريد
email_to_send = st.text_input("أدخل بريدك الإلكتروني لتلقي النشرة:")

if st.button("توليد النشرة وإرسالها الآن 🚀"):
    if email_to_send:
        with st.spinner("جاري التواصل مع الأقمار الصناعية وجلب الأخبار..."):
            # 1. جلب الأخبار
            final_report = fetch_and_summarize_v3()
            
            # 2. عرض معاينة للمستخدم
            st.subheader("📝 معاينة النشرة المولدة:")
            st.info(final_report)
            
            # 3. الإرسال الفعلي في حال وجود محتوى
            if "❌" not in final_report:
                if send_automated_email(email_to_send, final_report):
                    st.success(f"✅ تم الإرسال بنجاح إلى {email_to_send}!")
                    st.balloons()
            else:
                st.error("لم يتم الإرسال بسبب عدم وجود محتوى.")
    else:
        st.warning("يرجى كتابة البريد الإلكتروني أولاً.")

st.sidebar.info("مشروع تخرج مصغر - تطوير نظام نشرة إخبارية باستخدام Python و Generative AI.")
