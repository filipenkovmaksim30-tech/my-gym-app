import os
from taskiq_aio_pika import AioPikaBroker

RABBITMQ_URL = os.getenv("RABBITMQ_URL")

broker = AioPikaBroker(RABBITMQ_URL, queue_name="reports_queue")

generate_report_task = broker.register_task(name='generate_user_report')