# watcher/app.py
import os, re, csv, smtplib, ssl, datetime, sys, time
from io import StringIO
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr
import requests
from bs4 import BeautifulSoup

# ---------- Robust env helpers ----------
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
SMTP_PORT = env_int("SMTP_PORT", 587)   # 587 = STARTTLS, 465 = SSL
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASS = os.getenv("SMTP_PASS", "")

PUSHOVER_TOKEN = os.getenv("PUSHOVER_TOKEN", "")
PUSHOVER_USER  = os.getenv("PUSHOVER_USER", "")

# ---------
