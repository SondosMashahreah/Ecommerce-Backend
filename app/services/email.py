import smtplib
from email.message import EmailMessage


def send_otp_email(to_email: str, otp: str):
    message = EmailMessage()

    message["Subject"] = "Your OTP Code"
    message["From"] = "no-reply@ecommerce.local"
    message["To"] = to_email

    message.set_content(
        f"Your OTP code is: {otp}\n"
        "This code will expire in 5 minutes."
    )

    with smtplib.SMTP("localhost", 1025) as smtp:
        smtp.send_message(message)
