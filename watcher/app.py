import os
import sys
import smtplib
from email.mime.text import MIMEText

# Hämta SMTP-inställningar från secrets
SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = os.getenv("SMTP_PORT")
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL")

print("DEBUG: SMTP_HOST =", SMTP_HOST)
print("DEBUG: SMTP_PORT =", SMTP_PORT)
print("DEBUG: SMTP_USER =", SMTP_USER)
print("DEBUG: SMTP_PASS length =", len(SMTP_PASS) if SMTP_PASS else "None")
print("DEBUG: RECIPIENT_EMAIL =", RECIPIENT_EMAIL)

# Testmail
subject = "Test från GitHub Actions"
body = "Detta är ett testmail från Systembolaget Watcher-scriptet."

msg = MIMEText(body)
msg["Subject"] = subject
msg["From"] = SMTP_USER
msg["To"] = RECIPIENT_EMAIL

try:
    print("DEBUG: Försöker ansluta till SMTP-server...")
    with smtplib.SMTP(SMTP_HOST, int(SMTP_PORT)) as server:
        server.starttls()
        print("DEBUG: TLS-anslutning upprättad")
        server.login(SMTP_USER, SMTP_PASS)
        print("DEBUG: Inloggning lyckades")
        server.send_message(msg)
        print("DEBUG: Mail skickat OK")
except Exception as e:
    print("ERROR: Misslyckades att skicka mail:", e)
