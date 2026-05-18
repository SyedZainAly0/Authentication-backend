import smtplib

from email.mime.text import MIMEText

from app.core.config import settings


def send_verification_email(receiver_email: str, token: str):

    verification_link = (
        f"http://localhost:8008/auth/dashboard?token={token}"
    )

    html = f"""
    <h2>Email Verification</h2>

    <p>Click below to verify your email:</p>

    <a href="{verification_link}">
        Verify Email
    </a>
    """

    msg = MIMEText(html, "html")

    msg["Subject"] = "Verify Your Email"
    msg["From"] = settings.SMTP_EMAIL
    msg["To"] = receiver_email

    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:

        server.starttls()

        server.login(
            settings.SMTP_EMAIL,
            settings.SMTP_PASSWORD
        )

        server.sendmail(
            settings.SMTP_EMAIL,
            receiver_email,
            msg.as_string()
        )