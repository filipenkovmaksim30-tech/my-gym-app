from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.backend.databases.models import Report, ReportStatus

async def create_report(session: AsyncSession, user_id: int):
    new_report = Report(
        user_id=user_id,
        status=ReportStatus.PROCESSING
    )
    session.add(new_report)
    await session.commit()
    await session.refresh(new_report)
    return new_report