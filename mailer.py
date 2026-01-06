import json
import smtplib
import os
from email.message import EmailMessage
from datetime import datetime

# ======================
# CONFIGURATION
# ======================

import os

EMAIL = os.getenv("EMAIL")
APP_PASSWORD = os.getenv("APP_PASSWORD")


BASE_DIR = "/Users/workstation/Desktop/CIISS_HADITH_SENDER"

HADITH_FILE = os.path.join(BASE_DIR, "hadiths.json")
EMAIL_FILE = os.path.join(BASE_DIR, "emails.json")
STATE_FILE = os.path.join(BASE_DIR, "state.json")
LOG_FILE = os.path.join(BASE_DIR, "cron.log")

def log(msg):
    with open(LOG_FILE, "a") as f:
        f.write(f"[{datetime.now()}] {msg}\n")

try:
    log("Script started")

    with open(HADITH_FILE) as f:
        hadiths = json.load(f)

    with open(EMAIL_FILE) as f:
        emails = json.load(f)

    with open(STATE_FILE) as f:
        state = json.load(f)

    index = state.get("last_sent_index", 0)
    hadith = hadiths[index]

    html_content = f"""
    <html>
      <body style="font-family: Arial, sans-serif; background:#f9f9f9; padding:20px;">
        <div style="max-width:600px; margin:auto; background:white; padding:25px; border-radius:8px;">
          <h2 style="text-align:center;">🌙 Daily Hadith</h2>
          <hr>
          <p style="font-size:24px; text-align:center; direction:rtl;">
            {hadith['arabic']}
          </p>
          <p style="font-size:16px; text-align:center; color:#555;">
            {hadith['translation']}
          </p>
          <hr>
          <p style="text-align:center; font-size:12px; color:#999;">
            May Allah grant us understanding and practice. Ameen.
          </p>
        </div>
      </body>
    </html>
    """

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL, APP_PASSWORD)

        for recipient in emails:
            msg = EmailMessage()
            msg["Subject"] = "🌙 Daily Hadith"
            msg["From"] = EMAIL
            msg["To"] = recipient

            msg.set_content("Your email client does not support HTML.")
            msg.add_alternative(html_content, subtype="html")

            server.send_message(msg)
            log(f"Sent to {recipient}")

    state["last_sent_index"] = (index + 1) % len(hadiths)

    with open(STATE_FILE, "w") as f:
        json.dump(state, f)

    log("Script completed successfully")

except Exception as e:
    log(f"ERROR: {e}")