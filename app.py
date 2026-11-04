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
    library = "".join(
        '<li><a href="' + html.escape(str(source.get("url", "#")), quote=True)
        + '" target="_blank" rel="noreferrer">'
        + html.escape(str(source.get("title", "Başlıksız kaynak")))
        + "</a><span>" + html.escape(str(source.get("topic", ""))) + "</span></li>"
        for source in sources
    ) or "<li>Henüz kaynak eklenmemiş.</li>"
    template = r'''<!doctype html>
<html lang="tr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="theme-color" content="#a90f26"><title>Atatürk AI — Tarihle sohbet</title>
<style>
:root{color-scheme:light;--red:#a90f26;--red2:#cf2b42;--pale:#fff2f3;--ink:#29171a;--muted:#87777a;--line:#f0dfe1}*{box-sizing:border-box}body{margin:0;color:var(--ink);font:15px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;background:#fff}button,textarea{font:inherit}button{cursor:pointer}.layout{height:100dvh;min-height:590px;display:grid;grid-template-columns:250px minmax(0,1fr);max-width:1500px;margin:auto;background:white;box-shadow:0 0 70px #3b0b1310}.side{background:#fff7f8;border-right:1px solid var(--line);padding:22px 16px;display:flex;flex-direction:column;overflow:auto}.brand{display:flex;align-items:center;gap:10px;margin:0 6px 28px}.mark{width:38px;height:38px;background:var(--red);color:white;border-radius:12px;display:grid;place-items:center;font:700 23px Georgia}.brand b{font-size:13px;letter-spacing:1.5px}.brand small{display:block;font-size:8px;letter-spacing:2px;color:#aa777e}.new{border:1px solid #edd5d9;border-radius:9px;background:#fff;color:var(--red);padding:10px 12px;text-align:left;font-weight:650}.kicker{margin:25px 8px 8px;font-size:9px;letter-spacing:1.6px;color:#a68b8f;font-weight:700}.topic{border:0;background:transparent;color:#65585b;border-radius:8px;text-align:left;padding:10px;font-size:12px}.topic:hover,.topic.active{background:#f8e7e9;color:#841222}.count{margin-top:10px;background:#fff;border:1px solid var(--line);border-radius:10px;padding:13px;display:flex;align-items:center;gap:10px}.counticon{height:30px;width:30px;display:grid;place-items:center;color:var(--red);background:var(--pale);border-radius:8px}.count b,.count small{display:block}.count b{font-size:12px}.count small{font-size:9px;color:var(--muted)}.sidefoot{margin-top:auto;padding:13px 9px 0;color:#8d7479;font-size:9px}.chat{min-width:0;display:flex;flex-direction:column;position:relative;isolation:isolate;background:#fff}.chat:before{content:"";position:absolute;inset:0;z-index:-1;background:linear-gradient(90deg,rgba(255,255,255,.94),rgba(255,255,255,.89) 52%,rgba(255,255,255,.79)),url("https://upload.wikimedia.org/wikipedia/commons/c/c5/Atat%C3%BCrk_portre.png") center 33%/cover no-repeat;pointer-events:none}.bar{height:60px;flex:none;border-bottom:1px solid #f1e8e9;background:#ffffffd9;backdrop-filter:blur(12px);display:flex;align-items:center;justify-content:space-between;padding:0 22px}.online{font-size:11px;color:#695c5e}.online i{display:inline-block;width:7px;height:7px;background:#799779;border-radius:50%;margin-right:7px}.share{border:1px solid #edcdd2;border-radius:8px;background:#fff;color:var(--red);padding:7px 11px;font-size:11px;font-weight:650}.share:hover{background:var(--pale)}.content{flex:1;overflow:auto;padding:25px 26px 14px}.welcome{max-width:640px;text-align:center;margin:0 auto 21px}.portrait{height:100px;width:100px;border:4px solid white;border-radius:50%;margin:0 auto 12px;overflow:hidden;box-shadow:0 4px 18px #54101e25;background:#ddd}.portrait img{width:100%;height:100%;object-fit:cover;object-position:center 22%;filter:grayscale(1)}.credit{font-size:8px;letter-spacing:.5px;color:#987d81;text-decoration:none}.welcome h1{font:600 32px/1.2 Georgia,serif;margin:12px 0 8px}.welcome h1 em{font-style:normal;color:var(--red)}.welcome p{max-width:475px;margin:0 auto;color:#786b6d;font-size:12px}.quick{display:flex;justify-content:center;gap:8px;flex-wrap:wrap;margin-top:17px}.quick button{background:#fff;border:1px solid #eddde0;border-radius:999px;color:#704950;padding:7px 10px;font-size:10px}.messages{max-width:700px;margin:auto;display:flex;flex-direction:column;gap:10px}.row{display:flex;gap:8px;align-items:flex-start}.row.user{justify-content:flex-end}.avatar{height:25px;width:25px;flex:none;border-radius:8px;background:#f8e6e8;color:var(--red);display:grid;place-items:center;font:700 14px Georgia}.bubble{max-width:min(86%,560px);background:#fff;border:1px solid #f0dfe1;border-left:2px solid #c84a5a;border-radius:3px 12px 12px 12px;padding:11px 13px;font-size:12px;white-space:pre-wrap;overflow-wrap:anywhere;box-shadow:0 2px 8px #64162208}.row.user .bubble{background:var(--red);border:1px solid var(--red);color:white;border-radius:12px 3px 12px 12px}.sources{max-width:650px;margin:3px auto 8px 33px;display:grid;gap:7px}.source{background:#fff;border:1px solid #f0dfe1;border-radius:10px;padding:10px 12px;box-shadow:0 2px 8px #64162208}.source b{font-size:11px;color:#4b2027}.source p{margin:4px 0 6px;color:#65595b;font-size:11px;line-height:1.5}.source small{color:#98868a;font-size:9px}.source a{display:inline-block;margin-top:3px;font-size:10px;color:var(--red);text-decoration:none}.source a:hover{text-decoration:underline}.composer-wrap{padding:10px 24px 16px;background:#ffffffdf;backdrop-filter:blur(10px)}.composer{max-width:700px;margin:auto;background:#fff;border:1px solid #ebd9dc;border-radius:12px;padding:10px 11px 8px;box-shadow:0 4px 16px #54101e0b}.composer:focus-within{border-color:#d2919a;box-shadow:0 0 0 3px #f8e7e9}.composer textarea{display:block;width:100%;height:28px;max-height:110px;min-height:28px;resize:none;border:0;outline:0;color:#352126;font-size:12px}.composer textarea::placeholder{color:#a39598}.tools{display:flex;justify-content:space-between;align-items:center}.hint{color:#a08e92;font-size:9px}.send{border:0;background:var(--red);color:white;border-radius:8px;height:30px;width:32px;font-size:18px}.send:hover{background:#850d20}.disclaimer{text-align:center;color:#9b8b8e;font-size:8px;margin:8px auto 0}.drawer{position:absolute;right:0;top:60px;bottom:0;width:min(320px,92vw);overflow:auto;background:#fffafa;border-left:1px solid var(--line);box-shadow:-10px 0 30px #4e111512;padding:17px;z-index:4;display:none}.drawer.open{display:block}.drawer h2{font:600 18px Georgia;margin:3px 0 8px}.drawer p{color:var(--muted);font-size:10px}.drawer ul{padding-left:18px}.drawer li{margin:8px 0;font-size:10px}.drawer li a{color:#922033;text-decoration:none}.drawer li span{display:block;color:#9a898c;font-size:9px}.drawer-close{float:right;border:0;background:none;color:#947e82;font-size:21px}.typing{color:#987d82;font-size:11px}.hidden{display:none!important}
@media(max-width:700px){.layout{display:flex;min-height:100dvh;height:100dvh}.side{display:none}.bar{height:54px;padding:0 13px}.content{padding:17px 13px 10px}.portrait{height:84px;width:84px}.welcome h1{font-size:28px}.welcome p{font-size:11px}.quick{gap:6px}.quick button{font-size:9px}.composer-wrap{padding:8px 10px 11px}.disclaimer{font-size:7px;line-height:1.4}.bubble{font-size:11px}.drawer{top:54px}.share{padding:6px 9px}}
</style></head><body>
<div class="layout"><aside class="side"><div class="brand"><span class="mark">A</span><div><b>ATATÜRK AI</b><small>TARİHLE SOHBET</small></div></div>
<button class="new" id="newChat">＋ Yeni sohbet</button><div class="kicker">KEŞFET</div>
<button class="topic" data-question="Atatürk kimdir?">◉ Atatürk'ü tanı</button><button class="topic" data-question="Kurtuluş Savaşı nasıl başladı?">⌁ Millî Mücadele</button><button class="topic" data-question="Atatürk'ün inkılaplarını anlatır mısın?">✳ Cumhuriyet ve inkılaplar</button><button class="topic" data-question="Türk tarihinin önemli dönemleri nelerdir?">▤ Türk tarihi</button>
<div class="kicker">BİLGİ KÜTÜPHANESİ</div><div class="count"><span class="counticon">▦</span><div><b>__COUNT__ kaynak</b><small>belge ve konu özeti</small></div></div><div class="sidefoot">Akıl · Bilim · Gerçek<br>Kaynağa dayalı tarih anlatımı</div></aside>
<section class="chat"><header class="bar"><span class="online"><i></i>Tarihî danışman <small>· kaynaklı simülasyon</small></span><div><button class="share" id="libraryBtn">Kaynaklar</button> <button class="share" id="shareBtn">↗ Paylaş</button></div></header>
<div class="content" id="content"><div class="welcome" id="welcome"><div class="portrait"><img src="https://upload.wikimedia.org/wikipedia/commons/c/c5/Atat%C3%BCrk_portre.png" alt="Mustafa Kemal Atatürk'ün tarihî portresi"></div><a class="credit" href="https://commons.wikimedia.org/wiki/File:Atat%C3%BCrk_portre.png" target="_blank" rel="noreferrer">FOTOĞRAF: BOĞOS TARKULYAN · WIKIMEDIA COMMONS</a><h1>Merhaba, ben <em>Atatürk AI.</em></h1><p>Atatürk ve Türk tarihi üzerine kaynaklara dayalı bir sohbet. Aklındaki konuyu sor; birlikte inceleyelim.</p><div class="quick"><button data-question="Atatürk'ün eğitim hayatını anlatır mısın?">Eğitim hayatı</button><button data-question="Samsun'a çıkış neden önemliydi?">19 Mayıs</button><button data-question="Cumhuriyet nasıl ilan edildi?">Cumhuriyet</button><button data-question="Atatürk'ün bilim anlayışı nasıldı?">Akıl ve bilim</button></div></div><div class="messages" id="messages"><div class="row"><span class="avatar">A</span><div class="bubble">Merhaba! Atatürk'ün hayatı veya Türk tarihiyle ilgili ne merak ediyorsun? Kaynak bulduğumda dayanağını da paylaşırım.</div></div></div></div>
<div class="composer-wrap"><form class="composer" id="askForm"><textarea id="question" rows="1" placeholder="Bir şey sor… (Enter ile gönder, Shift+Enter ile yeni satır)"></textarea><div class="tools"><span class="hint" id="hint">Yalnızca kaynaklı tarihî özet sunarım</span><button class="send" type="submit" aria-label="Gönder">↑</button></div></form><div class="disclaimer">Bu bir yapay zekâ simülasyonudur; Atatürk'ün gerçek sesi, bilinci veya birebir görüşü değildir.</div></div>
<aside class="drawer" id="drawer"><button class="drawer-close" id="drawerClose" aria-label="Kapat">×</button><h2>Kaynak kütüphanesi</h2><p>Bu sohbette kullanılan ve koleksiyonda bulunan kaynak başlıkları.</p><ul>__LIBRARY__</ul></aside></section></div>
<script>
const form=document.querySelector('#askForm'),input=document.querySelector('#question'),messages=document.querySelector('#messages'),content=document.querySelector('#content'),welcome=document.querySelector('#welcome'),hint=document.querySelector('#hint');
function addBubble(text,who){const row=document.createElement('div');row.className='row '+who;if(who==='assistant'){const avatar=document.createElement('span');avatar.className='avatar';avatar.textContent='A';row.append(avatar)}const bubble=document.createElement('div');bubble.className='bubble';bubble.textContent=text;row.append(bubble);messages.append(row);content.scrollTop=content.scrollHeight;return row}
function addSources(sources){if(!sources.length)return;const container=document.createElement('div');container.className='sources';sources.forEach(source=>{const card=document.createElement('article');card.className='source';const title=document.createElement('b');title.textContent=source.title||'Başlıksız kaynak';const body=document.createElement('p');body.textContent=source.content||'';const meta=document.createElement('small');meta.textContent=[source.date,source.type,source.source].filter(Boolean).join(' · ');card.append(title,body,meta);if(/^https?:\/\//i.test(source.url||'')){const link=document.createElement('a');link.href=source.url;link.target='_blank';link.rel='noreferrer';link.textContent='Kaynağı aç ↗';card.append(document.createElement('br'),link)}container.append(card)});messages.append(container);content.scrollTop=content.scrollHeight}
async function ask(text){const question=(text||input.value).trim();if(!question)return;welcome.classList.add('hidden');addBubble(question,'user');input.value='';input.style.height='28px';const pending=addBubble('Kaynaklarda arıyorum…','assistant');try{const response=await fetch('/ask',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({question})});const result=await response.json();pending.remove();addBubble(result.answer,'assistant');addSources(result.matches||[])}catch(error){pending.remove();addBubble('Şu anda kaynak sunucusuna ulaşamadım. Biraz sonra yeniden dener misin?','assistant')}content.scrollTop=content.scrollHeight}
form.addEventListener('submit',event=>{event.preventDefault();ask()});input.addEventListener('keydown',event=>{if(event.key==='Enter'&&!event.shiftKey){event.preventDefault();ask()}});input.addEventListener('input',()=>{input.style.height='auto';input.style.height=Math.min(input.scrollHeight,110)+'px'});document.querySelectorAll('[data-question]').forEach(button=>button.addEventListener('click',()=>ask(button.dataset.question)));document.querySelector('#newChat').addEventListener('click',()=>{messages.replaceChildren();welcome.classList.remove('hidden');addBubble('Merhaba! Atatürk\'ün hayatı veya Türk tarihiyle ilgili ne merak ediyorsun? Kaynak bulduğumda dayanağını da paylaşırım.','assistant');input.focus()});
document.querySelector('#shareBtn').addEventListener('click',async()=>{try{if(navigator.share)await navigator.share({title:'Atatürk AI · Tarihle sohbet',text:'Atatürk ve Türk tarihi üzerine kaynaklı sohbet',url:location.href});else{await navigator.clipboard.writeText(location.href);hint.textContent='Bağlantı kopyalandı; dilediğin kişiye gönderebilirsin.';setTimeout(()=>hint.textContent='Yalnızca kaynaklı tarihî özet sunarım',3000)}}catch(error){if(error.name!=='AbortError')hint.textContent='Bağlantıyı adres çubuğundan kopyalayabilirsin.'}});document.querySelector('#libraryBtn').addEventListener('click',()=>document.querySelector('#drawer').classList.add('open'));document.querySelector('#drawerClose').addEventListener('click',()=>document.querySelector('#drawer').classList.remove('open'));
</script></body></html>'''
    return template.replace("__COUNT__", str(len(sources))).replace("__LIBRARY__", library)


class Handler(BaseHTTPRequestHandler):
    def send_page(self, body):
        encoded = body.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def send_json(self, payload):
        encoded = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def do_GET(self):
        self.send_page(page())

    def do_POST(self):
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length).decode("utf-8")
        try:
            question = json.loads(raw).get("question", "").strip()
        except (json.JSONDecodeError, AttributeError):
            question = parse_qs(raw).get("question", [""])[0].strip()

        if self.path == "/ask":
            normalized = normalize(question)
            if re.match(r"^(merhaba|selam|slm|hey|hello)\b", normalized):
                answer = "Merhaba! Atatürk'ün hayatı veya Türk tarihiyle ilgili ne merak ediyorsun? Kaynak bulduğumda dayanağını da paylaşırım."
                matches = []
            elif re.search(r"nasilsin|ne haber|naber", normalized):
                answer = "İyiyim, teşekkürler! Buradayım; tarih sorularını birlikte inceleyebiliriz. Sen nasılsın?"
                matches = []
            elif re.search(r"tesekkur|sag ol", normalized):
                answer = "Rica ederim! İstersen konunun öncesini, sonuçlarını veya başka bir tarih başlığını da konuşabiliriz."
                matches = []
            elif re.search(r"sen kimsin|kimsin|ne ise yariyorsun", normalized):
                answer = "Ben Atatürk AI adlı tarih sohbeti simülasyonuyum. Atatürk ve Türk tarihiyle ilgili kaynak özetleri sunarım; gerçek Atatürk'ün sesi, bilinci veya birebir görüşü değilim."
                matches = []
            elif not question:
                answer = "Bir soru yazarsan tarihî kaynaklarda arayayım."
                matches = []
            else:
                matches = find_sources(question, load_sources())
                if matches:
                    answer = "Kaynaklarda bulduğum bilgiler aşağıda. Bunlar tarihî belgelerin kısa özetleridir; günümüz için Atatürk'e ait doğrudan görüşler değildir."
                else:
                    answer = "Bu soruyla doğrudan eşleşen bir kaynak bulamadım. Bir isim, tarih veya konu ekleyerek farklı biçimde sorabilir misin? Kaynak olmadan tarihî görüş ya da alıntı atfetmek istemem."
            self.send_json({"answer": answer, "matches": matches})
            return

        self.send_page(page())

    def log_message(self, format_string, *args):
        print("[Atatürk AI] " + format_string % args)


if __name__ == "__main__":
    print(f"Atatürk AI açıldı: http://{HOST}:{PORT}")
    print("Durdurmak için Ctrl+C tuşlarına basın.")
    HTTPServer((HOST, PORT), Handler).serve_forever()
