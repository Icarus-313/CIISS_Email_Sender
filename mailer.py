import json
import smtplib
import os
from email.message import EmailMessage

# ======================
# ENV VARIABLES
# ======================

EMAIL = os.getenv("EMAIL")
APP_PASSWORD = os.getenv("APP_PASSWORD")

if not EMAIL or not APP_PASSWORD:
    raise RuntimeError("EMAIL or APP_PASSWORD environment variable not set")

# ======================
# FILE PATHS (RELATIVE)
# ======================

HADITH_FILE = "hadiths.json"
EMAIL_FILE = "emails.json"
STATE_FILE = "state.json"

print("Mailer started")

try:
    # Load data
    with open(HADITH_FILE, encoding="utf-8") as f:
        hadiths = json.load(f)

    with open(EMAIL_FILE, encoding="utf-8") as f:
        emails = json.load(f)

    # Load or initialize state
    if os.path.exists(STATE_FILE):
     with open(STATE_FILE, encoding="utf-8") as f:
        state = json.load(f)
    else:
        state = {"last_sent_index": 0}
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f)
    index = state.get("last_sent_index", 0)
    hadith = hadiths[index]

    print("Hadith index:", index)
    print("Recipients:", emails)

    # Email content
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

    print("EMAIL loaded:", EMAIL)
    print("APP_PASSWORD loaded:", bool(APP_PASSWORD))

    # Send emails
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
            print("Sent to:", recipient)

    # Update state
    state["last_sent_index"] = (index + 1) % len(hadiths)

    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f)

    print("Script completed successfully")

except Exception as e:
    print("ERROR:", e)
    raise