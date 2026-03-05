from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from config.database_config import get_db
from app.core.services.dashboard_service import DashboardService
from dto.dashboard_dtos import DashboardMetricsResponse, DashboardActivityItem
from typing import List

router = APIRouter()

@router.get("/metrics", response_model=DashboardMetricsResponse)
async def get_metrics(db: AsyncSession = Depends(get_db)):
    service = DashboardService(db)
    return await service.get_metrics()

@router.get("/activity", response_model=List[DashboardActivityItem])
async def get_activity(db: AsyncSession = Depends(get_db)):
    service = DashboardService(db)
    return await service.get_recent_activity()
