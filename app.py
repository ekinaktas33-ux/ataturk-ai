"""Atatürk AI — harici paket gerektirmeyen yerel kaynak arama prototipi.

Başlatmak için: python3 app.py
Ardından tarayıcıda http://127.0.0.1:8501 adresini açın.
"""

import html
import json
import os
import re
import unicodedata
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs


ROOT = Path(__file__).parent
DATA_FILE = ROOT / "data" / "sources.json"
# Hosting services provide PORT and require the app to listen on all interfaces.
# Local development stays private to this computer.
PORT = int(os.environ.get("PORT", "8501"))
HOST = "0.0.0.0" if os.environ.get("PORT") else "127.0.0.1"

SYNONYMS = {
    "egitim": {"egitim", "ogretim", "ogretmen", "okul", "maarif", "kuşak", "kusak"},
    "ogretmen": {"ogretmen", "egitim", "ogretim", "okul", "maarif"},
    "bilim": {"bilim", "bilimsel", "teknik", "teknoloji", "akil", "gercek", "arastirma"},
    "teknoloji": {"teknoloji", "bilim", "teknik", "ilerleme", "gelisme"},
    "ekonomi": {"ekonomi", "ekonomik", "iktisat", "ticaret", "uretim", "kalkinma"},
    "iktisat": {"iktisat", "ekonomi", "ekonomik", "ticaret", "uretim", "kalkinma"},
    "yonetim": {"yonetim", "devlet", "siyaset", "millet", "hukumet", "idare"},
    "siyaset": {"siyaset", "yonetim", "devlet", "millet", "hukumet", "idare"},
    "savunma": {"savunma", "asker", "askeri", "ordu", "subay", "guvenlik"},
    "asker": {"asker", "askeri", "ordu", "savunma", "subay", "guvenlik"},
    "tarih": {"tarih", "gecmis", "nutuk", "belge", "milli mucadele"},
    "akil": {"akil", "bilim", "mantik", "gercek", "yontem"},
}


def normalize(text):
    text = text.lower().translate(str.maketrans({"ı": "i", "İ": "i"}))
    text = unicodedata.normalize("NFKD", text)
    text = "".join(char for char in text if not unicodedata.combining(char))
    return re.sub(r"[^a-z0-9]+", " ", text).strip()


def load_sources():
    try:
        data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except (OSError, json.JSONDecodeError):
        return []


def find_sources(question, sources):
    words = {word for word in normalize(question).split() if len(word) > 2}
    expanded = set(words)
    for word in words:
        expanded.update(SYNONYMS.get(word, set()))
    words = expanded
    ranked = []
    for source in sources:
        text = normalize(" ".join(
            str(source.get(key, "")) for key in ("title", "content", "tags", "topic")
        ))
        text_words = set(text.split())
        score = sum(1 for word in words if word in text_words or (len(word) >= 5 and word[:5] in text))
        if score:
            ranked.append((score, source))
    ranked.sort(key=lambda item: item[0], reverse=True)
    return [source for _, source in ranked[:5]]


def page(question="", matches=None):
    sources = load_sources()
    matches = matches or []
    results = ""
    if question:
        if matches:
            items = []
            for source in matches:
                title = html.escape(str(source.get("title", "Başlıksız kaynak")))
                content = html.escape(str(source.get("content", "")))
                citation = " · ".join(
                    html.escape(str(source.get(key, "")))
                    for key in ("date", "type", "source")
                    if source.get(key)
                )
                url = str(source.get("url", ""))
                link = (
                    f'<p><a href="{html.escape(url, quote=True)}" target="_blank" '
                    'rel="noreferrer">Kaynağı aç</a></p>'
                    if url.startswith(("https://", "http://")) else ""
                )
                items.append(
                    f'<article><h3>{title}</h3><p>{content}</p>'
                    f'<small>{citation}</small>{link}</article>'
                )
            results = (
                '<section><h2>Bulunan kaynaklar</h2>'
                '<p>Bu sonuçlar tarihî belgeleri gösterir; Atatürk\'ün '
                'bugün ne düşüneceğini iddia etmez.</p>'
                + "".join(items) + "</section>"
            )
        else:
            results = (
                '<section><h2>Eşleşme bulunamadı</h2><p>Bu koleksiyonda '
                'soruyla eşleşen kaynak yok. Kaynak olmadan tarihî görüş veya '
                'alıntı atfetmek doğru olmaz.</p></section>'
            )

    library = "".join(
        '<li><a href="' + html.escape(str(source.get("url", "#")), quote=True)
        + '" target="_blank" rel="noreferrer">'
        + html.escape(str(source.get("title", "Başlıksız kaynak")))
        + "</a> — " + html.escape(str(source.get("topic", ""))) + "</li>"
        for source in sources
    ) or "<li>Henüz kaynak eklenmemiş.</li>"

    return f"""<!doctype html>
<html lang="tr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Atatürk AI — Tarihî Kaynak Asistanı</title>
<style>
*{{box-sizing:border-box}} body{{margin:0;background:#f3f5f8;color:#172033;font:16px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}}
main{{max-width:850px;margin:48px auto;padding:0 20px}} header,section,.notice{{background:white;border:1px solid #e1e6ef;border-radius:16px;padding:24px;margin:16px 0;box-shadow:0 5px 22px #1c2b440a}}
h1{{margin:0;font-size:34px}} h2{{margin-top:0}} .subtitle{{color:#637087;margin:4px 0 18px}}
.notice{{background:#fff8e7;border-color:#f1dda4}} textarea{{display:block;width:100%;min-height:105px;padding:14px;border:1px solid #cbd3df;border-radius:10px;font:inherit;resize:vertical}}
button{{margin-top:12px;background:#183d70;color:#fff;border:0;border-radius:9px;padding:12px 20px;font:inherit;font-weight:650;cursor:pointer}} article{{border-top:1px solid #e5e9ef;padding:12px 0}} article h3{{margin-bottom:4px}} small{{color:#68758a}} a{{color:#174d8d}}
</style></head><body><main>
<header><h1>Atatürk AI</h1><p class="subtitle">Tarihî kaynaklarla çalışan araştırma prototipi</p>
<form method="post"><label for="question"><strong>Kaynaklarda ara</strong></label>
<textarea id="question" name="question" placeholder="Örnek: Eğitim hakkında hangi kaynaklar var?">{html.escape(question)}</textarea>
<button type="submit">Kaynakları bul</button></form></header>
<div class="notice"><strong>Bilgilendirme:</strong> Bu uygulama Atatürk'ün kendisi değildir ve onun bugünkü görüşlerini temsil etmez. Sonuçlar yalnızca yerel örnek kaynak koleksiyonuna dayanır.</div>
{results}<section><h2>Kaynak koleksiyonu ({len(sources)} kayıt)</h2><ul>{library}</ul>
<p>Yeni kayıtlar <code>data/sources.json</code> dosyasına eklenebilir.</p></section>
<section><h2>Proje ilkeleri</h2><ul><li>Tarihî iddiaları kaynaklarıyla sunmak</li><li>Kaynak bulunmadığında bunu açıkça belirtmek</li><li>Güncel yorumları Atatürk'ün kesin görüşü gibi göstermemek</li><li>Kaynakları uzman incelemesinden geçirmek</li></ul></section>
</main></body></html>"""


class Handler(BaseHTTPRequestHandler):
    def send_page(self, body):
        encoded = body.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def do_GET(self):
        self.send_page(page())

    def do_POST(self):
        length = int(self.headers.get("Content-Length", "0"))
        form = parse_qs(self.rfile.read(length).decode("utf-8"))
        question = form.get("question", [""])[0].strip()
        self.send_page(page(question, find_sources(question, load_sources())))

    def log_message(self, format_string, *args):
        print("[Atatürk AI] " + format_string % args)


if __name__ == "__main__":
    print(f"Atatürk AI açıldı: http://{HOST}:{PORT}")
    print("Durdurmak için Ctrl+C tuşlarına basın.")
    HTTPServer((HOST, PORT), Handler).serve_forever()
