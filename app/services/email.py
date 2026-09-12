import os
import resend

resend.api_key = os.getenv("RESEND_API_KEY")


def send_otp_email(to_email: str, otp: str):
    resend.Emails.send({
        "from": "onboarding@resend.dev",
        "to": [to_email],
        "subject": "Your OTP Code",
        "text": (
            f"Your OTP code is: {otp}\n"
            "This code will expire in 5 minutes."
        ),
    })