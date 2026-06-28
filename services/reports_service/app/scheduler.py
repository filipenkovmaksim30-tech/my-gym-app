import os
from taskiq_aio_pika import AioPikaBroker

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@gym_rabbitmq:5672//")
broker = AioPikaBroker(RABBITMQ_URL, queue_name="reports_queue")

from app.tasks import generate_user_report