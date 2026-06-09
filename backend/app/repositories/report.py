import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.report import Report


class ReportRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, report: Report) -> Report:
        self.session.add(report)
        await self.session.commit()
        await self.session.refresh(report)
        return report

    async def get_by_id(self, report_id: uuid.UUID) -> Report | None:
        result = await self.session.execute(
            select(Report).where(Report.id == report_id)
        )
        return result.scalar_one_or_none()

    async def list_all(
        self, status: str | None, offset: int, limit: int
    ) -> tuple[list[Report], int]:
        base = select(Report)
        if status is not None:
            base = base.where(Report.status == status)
        total_result = await self.session.execute(
            select(func.count()).select_from(base.subquery())
        )
        total = total_result.scalar_one()
        result = await self.session.execute(
            base.order_by(Report.created_at.desc()).offset(offset).limit(limit)
        )
        return list(result.scalars().all()), total

    async def update(self, report: Report, data: dict) -> Report:
        for key, value in data.items():
            setattr(report, key, value)
        await self.session.commit()
        await self.session.refresh(report)
        return report
