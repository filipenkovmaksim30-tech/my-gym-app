import os
import json
import asyncio
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from aio_pika import connect_robust, IncomingMessage


SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = os.getenv("SMTP_PORT")
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")  
EMAIL_FROM = "app-gym.local"

def send_email_with_pdf(to_email: str, subject: str, body: str, file_path: str):
    msg = MIMEMultipart()
    msg['From'] = EMAIL_FROM
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    if os.path.exists(file_path):
        with open(file_path, "rb") as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename={os.path.basename(file_path)}',
            )
            msg.attach(part)
    else:
        print(f"[Notifications] Ошибка: файл {file_path} не найден в папке /tmp!")
        return

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(EMAIL_FROM, to_email, msg.as_string())
        print(f"[Notifications] Письмо с отчетом успешно отправлено в Mailtrap для: {to_email}")
    except Exception as e:
        print(f"[Notifications] Ошибка отправки почты через SMTP: {e}")

async def process_notification(message: IncomingMessage):
    """Асинхронный обработчик сообщений из очереди RabbitMQ"""
    async with message.process():
        try:
            payload = json.loads(message.body.decode())
            email = payload.get("email")
            file_path = payload.get("file_path")
            
            print(f"[Notifications] Получена задача из очереди для {email}")
            await asyncio.to_thread(
                send_email_with_pdf,
                to_email=email,
                subject="Твой аналитический отчет по тренировкам",
                body="Привет! Твой отчет по прогрессу в жиме лежа сформирован. График во вложении.",
                file_path=file_path
            )
        except Exception as e:
            print(f"[Notifications] Ошибка при обработке сообщения: {e}")

async def main():
    RABBITMQ_URL = os.getenv("RABBITMQ_URL")
    connection = await connect_robust(RABBITMQ_URL)
    channel = await connection.channel()
    
    queue = await channel.declare_queue("notifications_queue", durable=True)
    await queue.consume(process_notification)
    
    print("[Notifications] Сервис уведомлений успешно запущен и слушает RabbitMQ...")
    await asyncio.Future() 

if __name__ == "__main__":
    asyncio.run(main())