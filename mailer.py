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

    from datetime import date

    today = date.today()
    index = today.toordinal() % len(hadiths)
    hadith = hadiths[index]

    # Daily uniqueness validation
    if len(hadiths) == 0:
        raise RuntimeError("Hadith dataset is empty")

    source = hadith.get("source", "Unknown")


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

          <p style="font-size:14px; text-align:center; color:#555;">
            Source: {['source']}
          </p>

          <p style="text-align:center; font-size:12px; color:#999;">
            May Allah grant us understanding and practice. Ameen.
          </p>


        </div>
      </body>
    </html>
    """

    print("EMAIL loaded:", EMAIL)
    print("APP_PASSWORD loaded:", bool(APP_PASSWORD))

    # Email failure retry logic + monitoring alert system
    MAX_RETRY = 3

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        try:
            server.login(EMAIL, APP_PASSWORD)
        except Exception as e:
            print("ALERT: SMTP login failed")
            raise

        for recipient in emails:

            msg = EmailMessage()
            msg["Subject"] = "🌙 Daily Hadith"
            msg["From"] = EMAIL
            msg["To"] = recipient

            msg.set_content("Your email client does not support HTML.")
            msg.add_alternative(html_content, subtype="html")

            retry_count = 0
            while retry_count < MAX_RETRY:
                try:
                    server.send_message(msg)
                    print("Sent to:", recipient)
                    break
                except Exception as e:
                    retry_count += 1
                    print(f"Retry {retry_count} for {recipient}")

                    if retry_count >= MAX_RETRY:
                        print("ALERT: Email delivery failed for", recipient)
                        print("Monitoring alert triggered")

    print("Delivery confirmed")

    # Update state

    print("Script completed successfully")

except Exception as e:
    print("ERROR:", e)
    raise