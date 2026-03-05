from pydantic import BaseModel
from typing import List, Optional

class DashboardHistoryItem(BaseModel):
    date: str
    total: int

class DashboardMetricsResponse(BaseModel):
    dailyTotal: int
    weeklyTotal: int
    monthlyTotal: int
    processedCount: int
    pendingCount: int
    observedCount: int
    averageConfidence: float
    sunatPending: int
    sunatAccepted: int
    sunatRejected: int
    history: List[DashboardHistoryItem]

class DashboardActivityItem(BaseModel):
    id: str
    action: str
    documentNumber: str
    time: str
    user: str
    status: str

class DashboardActivityResponse(BaseModel):
    activities: List[DashboardActivityItem]
