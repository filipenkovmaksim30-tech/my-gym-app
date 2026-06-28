import json
import uuid
from fastapi import APIRouter, Depends, status
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from taskiq.abc.broker import BrokerMessage 

from scheduler import broker 
from app.backend.databases.database import get_session 
from app.backend.crud.reports import create_report

router = APIRouter(prefix="/reports", tags=["Reports"])

@router.post("/trigger/{user_id}", status_code=status.HTTP_202_ACCEPTED, summary="Начало генерации отчета")
async def trigger_report_generation(
    user_id: int, 
    email: EmailStr,
    db: AsyncSession = Depends(get_session)
):
    db_report = await create_report(db, user_id=user_id)

    task_id = f"task-{uuid.uuid4()}"
    task_data = {
        "task_id": task_id,
        "task_name": "generate_user_report",
        "labels": {},
        "args": [],
        "kwargs": {
            "user_id": user_id, 
            "email": email,
            "report_id": db_report.id
        }
    }

    dumped_task = json.dumps(task_data).encode("utf-8")

    message = BrokerMessage(
        message=dumped_task,
        task_id=task_id,
        task_name="generate_user_report",
        labels={}
    )

    await broker.kick(message)

    return {
        "status": "Accepted",
        "report_id": db_report.id,
        "message": f"Генерация отчета запущена. Файл будет отправлен на {email}"
    }