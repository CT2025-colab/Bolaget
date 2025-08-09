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

msg

