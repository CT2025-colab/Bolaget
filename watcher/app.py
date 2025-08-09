import os, smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr

# Hämta secrets (med säkra fallbacks)
SMTP_HOST = os.getenv("SMTP_HOST", "")
SMTP_PORT = int(os.getenv("SMTP_PORT") or 587)  # 465 = SSL, 587 = STARTTLS
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASS = os.getenv("SMTP_PASS", "")
RECIPIENT  = os.getenv("RECIPIENT_EMAIL", "")

# Debug (utan att visa lösen)
print("DEBUG host=", SMTP_HOST)
print("DEBUG port=", SMTP_PORT)
print("DEBUG user=", SMTP_USER)
print("DEBUG rcpt=", RECIPIENT)
print("DEBUG pass length=", len(SMTP_PASS) if SMTP_PASS else 0)

# Bygg testmeddelande
subject = "Test från Systembolaget Watcher (GitHub Actions)"
text = "Detta är ett testmail."
html = "<html><body><h2>Test från Systembolaget Watcher</h2><p>Detta är ett <b>HTML</b>-testmail.</p></body></html>"

msg = MIMEMultipart('alternative')
msg['Subject'] = subject
msg['From'] = formataddr(("Folkungagatan.store-bevakning", SMTP_USER))
msg['To'] = RECIPIENT
msg.attach(MIMEText(text, 'plain', _charset='utf-8'))
msg.attach(MIMEText(html, 'html', _charset='utf-8'))

try:
    if SMTP_PORT == 465:
        # Implicit SSL (One.com: send.one.com:465)
        ctx = ssl.create_default_context()
        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, context=ctx, timeout=30) as s:
            s.login(SMTP_USER, SMTP_PASS)
            s.send_message(msg)
    else:
        # STARTTLS (vanligtvis port 587)
        ctx = ssl.create_default_context()
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=30) as s:
            s.ehlo()
            s.starttls(context=ctx)
            s.ehlo()
            s.login(SMTP_USER, SMTP_PASS)
            s.send_message(msg)
    print("DEBUG: Mail skickat ✅")
except Exception as e:
    print("ERROR: Misslyckades att skicka mail:", repr(e))
