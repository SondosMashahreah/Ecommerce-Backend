import os
import smtplib
from email.message import EmailMessage


SMTP_EMAIL = os.getenv("SMTP_EMAIL")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")


def send_otp_email(to_email: str, otp: str):
    message = EmailMessage()

    message["Subject"] = "Your OTP Code"
    message["From"] = SMTP_EMAIL
    message["To"] = to_email

    message.set_content(
        f"Your OTP code is: {otp}\n"
        "This code will expire in 5 minutes."
    )

    with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
        smtp.starttls()
        smtp.login(SMTP_EMAIL, SMTP_PASSWORD)
        smtp.send_message(message)