import os
from taskiq_aio_pika import AioPikaBroker
from taskiq import AsyncTaskiqTask

RABBITMQ_URL = os.getenv("RABBITMQ_URL")
broker = AioPikaBroker(
    RABBITMQ_URL, 
    queue_name="reports_queue", 
    declare_exchange=False,
    exchange="taskiq"
)