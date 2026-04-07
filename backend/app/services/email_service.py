import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", 465))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:8000")

def send_email(to: str, subject: str, body: str):
    """Универсальная отправка email через SMTP_SSL."""
    msg = MIMEMultipart()
    msg["From"] = SMTP_USER
    msg["To"] = to
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as server:
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(SMTP_USER, to, msg.as_string())
        print(f"Email sent to {to}")
    except Exception as e:
        print(f"Failed to send email to {to}: {e}")

def send_verification_email(email: str, token: str):
    verification_url = f"{FRONTEND_URL}/auth/verify?token={token}"
    subject = "Подтверждение email для Jarvis"
    body = f"""
    Здравствуйте!

    Для подтверждения вашего email перейдите по ссылке:
    {verification_url}

    Если вы не регистрировались в Jarvis, просто проигнорируйте это письмо.

    С уважением,
    Команда Jarvis
    """
    send_email(email, subject, body)

def send_password_reset_email(email: str, token: str):
    reset_url = f"{FRONTEND_URL}/auth/reset-password?token={token}"
    subject = "Сброс пароля для Jarvis"
    body = f"""
    Здравствуйте!

    Для сброса пароля перейдите по ссылке:
    {reset_url}

    Если вы не запрашивали сброс пароля, просто проигнорируйте это письмо.

    С уважением,
    Команда Jarvis
    """
    send_email(email, subject, body)

def send_event_reminder_email(email: str, event_title: str, start_time: datetime):
    subject = f"Напоминание: {event_title}"
    formatted_time = start_time.strftime('%d.%m.%Y %H:%M')
    body = f"""
    Здравствуйте!

    Напоминаем, что событие "{event_title}" начнётся в {formatted_time}.

    Удачи!
    Команда Jarvis
    """
    send_email(email, subject, body)