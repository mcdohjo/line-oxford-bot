import feedparser
import requests
import json
import os
from datetime import datetime
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

LINE_TOKEN = os.getenv("LINE_TOKEN")
USER_ID = os.getenv("USER_ID")

with open("oxford3000.json", "r", encoding="utf-8") as f:
    oxford = json.load(f)

oxford_words = set([w["word"].lower() for w in oxford])

def get_news():
    feed = feedparser.parse("https://www.thairath.co.th/rss/news")
    return feed.entries[:3]

def translate(text):
    prompt = f"แปลเป็นอังกฤษง่ายๆ:\n{text}"
    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    return res.choices[0].message.content

def analyze(text):
    words = text.split()
    ox_found = set()
    result = []

    for w in words:
        clean = w.lower().strip(".,!?")
        if clean in oxford_words:
            ox_found.add(clean)
            result.append(f"**{w}**")
        else:
            result.append(w)

    return " ".join(result), len(words), len(ox_found), list(ox_found)

def send_line(msg):
    url = "https://api.line.me/v2/bot/message/push"
    headers = {
        "Authorization": f"Bearer {LINE_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "to": USER_ID,
        "messages": [{"type": "text", "text": msg[:5000]}]
    }
    requests.post(url, headers=headers, json=data)

def run():
    news = get_news()

    for n in news:
        th = n.title
        en = translate(th)

        text, total, ox_count, words = analyze(en)

        msg = f"""
📰 {datetime.now().strftime('%d/%m/%Y')}

{text}

📊 คำทั้งหมด: {total}
📊 Oxford3000: {ox_count}

📌 คำ:
{", ".join(words)}
"""
        send_line(msg)

if __name__ == "__main__":
    run()