import os, re, csv, smtplib, ssl, datetime, sys, time
from io import StringIO
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr
import requests
from bs4 import BeautifulSoup

# ---------- Robust defaults ----------
def env_int(name, default):
    try:
        v = os.getenv(name)
        return int(v) if v not in (None, "", " ") else int(default)
    except Exception:
        return int(default)

# CLI > env > default(7)
try:
    DAYS_AHEAD = int(sys.argv[1])
except Exception:
    DAYS_AHEAD = env_int("DAYS_AHEAD", 7)

RECIPIENT = os.getenv("RECIPIENT_EMAIL", "tomass@folkungagatan.com")
SMTP_HOST = os.getenv("SMTP_HOST", "send.one.com")
SMTP_PORT = env_int("SMTP_PORT", 587)
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASS = os.getenv("SMTP_PASS", "")

PUSHOVER_TOKEN = os.getenv("PUSHOVER_TOKEN", "")
PUSHOVER_USER  = os.getenv("PUSHOVER_USER", "")

# ---------- Helpers ----------
def load_producers(path=os.path.join(os.path.dirname(__file__), "producers.txt")):
    with open(path, "r", encoding="utf-8") as f:
        raw = f.read().strip()
    return [p.strip() for p in next(csv.reader(StringIO(raw))) if p.strip()]

def fetch_list(date_iso, retries=3, backoff=2.0):
    base = "https://www.systembolaget.se/sortiment/tillfalligt-sortiment/"
    params = {"saljstart-fran": date_iso, "saljstart-till": date_iso}
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.5 Safari/605.1.15",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "sv-SE,sv;q=0.9,en;q=0.8",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
        "Connection": "close",
    }
    last_exc = None
    for i in range(retries):
        try:
            r = requests.get(base, params=params, headers=headers, timeout=30)
            if r.status_code == 200:
                return r.text, r.url
            last_exc = Exception(f"HTTP {r.status_code}")
        except Exception as e:
            last_exc = e
        time.sleep(backoff * (i+1))
    raise last_exc or Exception("Unknown fetch error")

def parse_items(html):
    soup = BeautifulSoup(html, "html.parser")
    items = []
    for a in soup.select('a[href*="/produkt/"]'):
        title = a.get_text(" ", strip=True)
        href = a.get("href", "")
        if not href: 
            continue
        if href.startswith("/"):
            href = "https://www.systembolaget.se" + href
        items.append({"title": title, "url": href})
    page_lower = soup.get_text(" ", strip=True).lower()
    return items, page_lower

def match_items(items, page_lower, producers):
    hits, seen = [], set()
    for prod in producers:
        patt = re.escape(prod.lower())
        found = False
        for it in items:
            if re.search(patt, (it["title"] or "").lower()):
                key = (prod, it["title"], it["url"])
                if key not in seen:
                    seen.add(key); hits.append((prod, it["title"], it["url"]))
                    found = True
        if not found and re.search(patt, page_lower):
            hits.append((prod, "(träff på sidan - kunde inte extrahera produktnamn)", ""))
    return hits

def build_email(target_date, hits, source_link):
    if hits:
        rows = "\n".join(
            f'<li><strong>{p}</strong> — {t}<br><a href="{(u or source_link)}">{(u or source_link)}</a></li>'
            for (p, t, u) in hits
        )
        subject = f"Bevakning: träffar {target_date} – Systembolagets tillfälliga"
        html = f'''
        <div style="font-family:system-ui,-apple-system,Segoe UI,Roboto,Arial,sans-serif;font-size:16px;line-height:1.5;color:#111;">
          <h2 style="margin:0 0 8px 0;">Bevakning – lansering {target_date}</h2>
          <p style="margin:8px 0;">Källa: <a href="{source_link}">{source_link}</a></p>
          <p>Följande producenter på din lista har träffar:</p>
          <ul style="margin:0 0 16px 20px; padding:0;">{rows}</ul>
          <p style="font-size:13px;color:#555;margin-top:16px;">/Folkungagatan.store-bevakning</p>
        </div>'''
        text = ";\n".join([f"{p} — {t} {u or source_link}" for (p,t,u) in hits])
    else:
        subject = f"Bevakning: inga träffar {target_date}"
        html = f'''
        <div style="font-family:system-ui,-apple-system,Segoe UI,Roboto,Arial,sans-serif;font-size:16px;line-height:1.5;color:#111;">
          <h2 style="margin:0 0 8px 0;">Bevakning – lansering {target_date}</h2>
          <p style="margin:8px 0;">Källa: <a href="{source_link}">{source_link}</a></p>
          <p>Inga träffar för dina bevakade producenter den här gången.</p>
          <p style="font-size:13px;color:#555;margin-top:16px;">/Folkungagatan.store-bevakning</p>
        </div>'''
        text = f"Inga träffar {target_date}"
    return subject, text, html

def send_email(subject, text, html):
    if not (SMTP_HOST and SMTP_USER and SMTP_PASS and RECIPIENT):
        print("SMTP config incomplete; skipping email.")
        return False
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = formataddr(("Folkungagatan.store-bevakning", SMTP_USER))
    msg['To'] = RECIPIENT
    msg.attach(MIMEText(text, 'plain', _charset='utf-8'))
    msg.attach(MIMEText(html, 'html', _charset='utf-8'))
    ctx = ssl.create_default_context()
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=30) as server:
        server.starttls(context=ctx)
        server.login(SMTP_USER, SMTP_PASS)
        server.send_message(msg)
    return True

def main():
    target_date = (datetime.datetime.now() + datetime.timedelta(days=DAYS_AHEAD)).date().isoformat()
    source_link = f"https://www.systembolaget.se/sortiment/tillfalligt-sortiment/?saljstart-fran={target_date}&saljstart-till={target_date}"
    producers = load_producers()
    try:
        html, final_url = fetch_list(target_date)
        items, page_lower = parse_items(html)
        hits = match_items(items, page_lower, producers)
        subject, text, body = build_email(target_date, hits, source_link)
        send_email(subject, text, body)
        print(subject)
    except Exception as e:
        # soft-fail: send status mail if possible, but never raise
        subject = f"Bevakning: kunde inte hämta listan {target_date}"
        text = f"Källa: {source_link}\nFel: {e}"
        body = f"<div><p>Källa: <a href='{source_link}'>{source_link}</a></p><p style='color:#b00'>Fel: {e}</p></div>"
        try:
            send_email(subject, text, body)
        except Exception as _:
            pass
        print("Fetch error but handled:", e)

if __name__ == "__main__":
    main()