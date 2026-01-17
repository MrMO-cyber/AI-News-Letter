def fetch_and_summarize_v3():
    # المحاولة الأولى: أهم عناوين التقنية العالمية
    urls = [
        f'https://newsapi.org/v2/top-headlines?category=technology&language=en&pageSize=5&apiKey={NEWS_API_KEY}',
        f'https://newsapi.org/v2/everything?q=AI+OR+Tech&language=en&sortBy=publishedAt&pageSize=5&apiKey={NEWS_API_KEY}',
        f'https://newsapi.org/v2/top-headlines?sources=techcrunch&pageSize=5&apiKey={NEWS_API_KEY}'
    ]
    
    articles = []
    for url in urls:
        try:
            response = requests.get(url)
            data = response.json()
            if data.get('status') == 'ok' and data.get('articles'):
                articles = data.get('articles')
                break # توقف عند أول نجاح
        except:
            continue

    if not articles:
        return "❌ فشل النظام في الاتصال بمصادر الأخبار. تأكد من صلاحية مفتاح NewsAPI الخاص بك."

    summary_list = [f"🤖 نشرة التكنولوجيا العالمية المحدثة\n" + "="*30 + "\n"]
    
    for art in articles:
        title = art.get('title')
        link = art.get('url')
        if title and "[Removed]" not in title:
            # نطلب من Gemini الترجمة والتلخيص
            prompt = f"Summarize this news in one short, exciting Arabic sentence with emojis: {title}"
            try:
                ai_res = model.generate_content(prompt)
                summary_list.append(f"⭐ {ai_res.text.strip()}\n🔗 المصدر: {link}\n")
            except:
                summary_list.append(f"📌 {title}\n🔗 {link}\n")
    
    return "\n".join(summary_list)
