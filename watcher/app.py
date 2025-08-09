import os
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr

# Hämta SMTP-uppgifter från secrets
SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")
RECIPIENT = os.getenv("RECIPIENT_EMAIL")

print("DEBUG: SMTP_HOST =", SMTP_HOST)
print("DEBUG: SMTP_PORT =", SMTP_PORT)
print("DEBUG: SMTP_USER =", SMTP_USER)
print("DEBUG: SMTP_PASS length =", len(SMTP_PASS) if SMTP_PASS else "None")
print("DEBUG: RECIPIENT =", RECIPIENT)

# Bygg meddelandet
subject = "Test från Systembolaget Watcher"
text_content = "Detta är ett testmail från GitHub Actions."
html_content = "<html><body><h1>Test från Systembolaget Watcher</h1><p>Detta är ett HTML-testmail från GitHub Actions.</p></body></html>"

msg = MIMEMultipart('alternative')
msg['Subject'] = subject
msg['From'] = formataddr(("Folkungagatan.store-bevakning", SMTP_USER))
msg['To'] = RECIPIENT
msg.attach(MIMEText(text_content, 'plain', _charset='utf-8'))
msg.attach(MIMEText(html_content, 'html', _charset='utf-8'))

try:
    if SMTP_PORT == 465:
        print("DEBUG: Använder SMTP_SSL (port 465)")
        context =
