import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", 465))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:8000")

def send_verification_email(email: str, token: str):
    subject = "Подтверждение email для Jarvis"
    verification_url = f"{FRONTEND_URL}/auth/verify?token={token}"
    body = f"""
    Здравствуйте!

    Для подтверждения вашего email перейдите по ссылке:
    {verification_url}

    Если вы не регистрировались в Jarvis, просто проигнорируйте это письмо.

    С уважением,
    Команда Jarvis
    """
    msg = MIMEMultipart()
    msg["From"] = SMTP_USER
    msg["To"] = email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as server:
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(SMTP_USER, email, msg.as_string())
        print(f"Verification email sent to {email}")
    except Exception as e:
        print(f"Failed to send email: {e}")

def send_password_reset_email(email: str, token: str):
    subject = "Сброс пароля для Jarvis"
    reset_url = f"{FRONTEND_URL}/auth/reset-password?token={token}"
    body = f"""
    Здравствуйте!

    Для сброса пароля перейдите по ссылке:
    {reset_url}

    Если вы не запрашивали сброс пароля, просто проигнорируйте это письмо.

    С уважением,
    Команда Jarvis
    """
    msg = MIMEMultipart()
    msg["From"] = SMTP_USER
    msg["To"] = email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as server:
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(SMTP_USER, email, msg.as_string())
        print(f"Password reset email sent to {email}")
    except Exception as e:
        print(f"Failed to send email: {e}")