from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from app.core.domain.guia_aerea import GuiaAerea
from app.core.domain.manifiesto import Manifiesto
from utl.generic_util import DateUtil
from utl.constantes import Constantes
from datetime import datetime, timedelta, time
from typing import List, Optional
from dto.dashboard_dtos import DashboardMetricsResponse, DashboardActivityItem, DashboardHistoryItem
from core.context.user_context import get_user_session

class DashboardService:
    def __init__(self, db: AsyncSession):
        self.db = db

    def _apply_user_filter(self, query):
        session = get_user_session()
        # Si es OPERADOR, solo ve sus propios registros
        if session and session.role_code == Constantes.Rol.OPERADOR:
            return query.where(GuiaAerea.usuario_id == session.user_id)
        return query

    async def get_metrics(self) -> DashboardMetricsResponse:
        # 1. Base Dates
        today = DateUtil.get_current_local_date()
        start_of_day = datetime.combine(today, time.min)
        
        # 2. Daily Totals (All created today)
        daily_query = select(func.count(GuiaAerea.guia_aerea_id)).where(
            and_(GuiaAerea.creado >= start_of_day, GuiaAerea.habilitado == True)
        )
        daily_query = self._apply_user_filter(daily_query)
        daily_result = await self.db.execute(daily_query)
        daily_total = daily_result.scalar() or 0

        # 3. Weekly & Monthly
        last_week = start_of_day - timedelta(days=7)
        weekly_query = select(func.count(GuiaAerea.guia_aerea_id)).where(
            and_(GuiaAerea.creado >= last_week, GuiaAerea.habilitado == True)
        )
        weekly_query = self._apply_user_filter(weekly_query)
        weekly_result = await self.db.execute(weekly_query)
        weekly_total = weekly_result.scalar() or 0

        last_month = start_of_day - timedelta(days=30)
        monthly_query = select(func.count(GuiaAerea.guia_aerea_id)).where(
            and_(GuiaAerea.creado >= last_month, GuiaAerea.habilitado == True)
        )
        monthly_query = self._apply_user_filter(monthly_query)
        monthly_result = await self.db.execute(monthly_query)
        monthly_total = monthly_result.scalar() or 0

        # 4. Confidence & Processed (Processed = ESTGA003)
        processed_query = select(
            func.avg(GuiaAerea.confidence_total),
            func.count(GuiaAerea.guia_aerea_id)
        ).where(
            and_(
                GuiaAerea.creado >= start_of_day, 
                GuiaAerea.estado_registro_codigo == Constantes.EstadoRegistroGuiaAereea.PROCESADO,
                GuiaAerea.habilitado == True
            )
        )
        processed_query = self._apply_user_filter(processed_query)
        conf_result = await self.db.execute(processed_query)
        avg_conf, processed_count = conf_result.fetchone()
        
        # 5. Pending (OBSERVADO/REVISIÓN) - Global count for better visibility
        pending_query = select(func.count(GuiaAerea.guia_aerea_id)).where(
            and_(
                GuiaAerea.estado_registro_codigo == Constantes.EstadoRegistroGuiaAereea.OBSERVADO, 
                GuiaAerea.habilitado == True
            )
        )
        pending_query = self._apply_user_filter(pending_query)
        pending_result = await self.db.execute(pending_query)
        pending_count = pending_result.scalar() or 0

        # 6. Integration Metrics (Count based on Guía Aérea as per user instruction)
        accepted_query = select(func.count(GuiaAerea.guia_aerea_id)).where(
            and_(
                GuiaAerea.estado_registro_codigo == Constantes.EstadoRegistroGuiaAereea.PROCESADO,
                GuiaAerea.habilitado == True
            )
        )
        accepted_query = self._apply_user_filter(accepted_query)
        
        observed_query = select(func.count(GuiaAerea.guia_aerea_id)).where(
            and_(
                GuiaAerea.estado_registro_codigo == Constantes.EstadoRegistroGuiaAereea.OBSERVADO,
                GuiaAerea.habilitado == True
            )
        )
        observed_query = self._apply_user_filter(observed_query)
        
        accepted_res = await self.db.execute(accepted_query)
        observed_res = await self.db.execute(observed_query)
        
        accepted_total = accepted_res.scalar() or 0
        observed_total = observed_res.scalar() or 0

        # 7. History (Last 30 days)
        history_query = select(
            func.date(GuiaAerea.creado).label('date'),
            func.count(GuiaAerea.guia_aerea_id).label('total')
        ).where(
            and_(
                GuiaAerea.creado >= start_of_day - timedelta(days=30),
                GuiaAerea.habilitado == True
            )
        ).group_by(func.date(GuiaAerea.creado)).order_by(func.date(GuiaAerea.creado))
        history_query = self._apply_user_filter(history_query)
        
        history_res = await self.db.execute(history_query)
        history_data = history_res.all()
        
        # Fill missing days with 0
        history_map = {str(row.date): row.total for row in history_data}
        history_list = []
        for i in range(30, -1, -1):
            d = (today - timedelta(days=i)).strftime("%Y-%m-%d")
            history_list.append(DashboardHistoryItem(
                date=d,
                total=history_map.get(d, 0)
            ))

        return DashboardMetricsResponse(
            dailyTotal=daily_total,
            weeklyTotal=weekly_total,
            monthlyTotal=monthly_total,
            processedCount=processed_count or 0,
            pendingCount=pending_count,
            observedCount=observed_total,
            averageConfidence=round(float(avg_conf or 0) * 100, 2),
            sunatPending=0,
            sunatAccepted=accepted_total,
            sunatRejected=0,
            history=history_list
        )

    async def get_recent_activity(self) -> List[DashboardActivityItem]:
        query = select(GuiaAerea).where(GuiaAerea.habilitado == True).order_by(GuiaAerea.creado.desc()).limit(5)
        query = self._apply_user_filter(query)
        result = await self.db.execute(query)
        guias = result.scalars().all()
        
        activities = []
        for g in guias:
            status = 'success' if g.estado_registro_codigo == Constantes.EstadoRegistroGuiaAereea.PROCESADO else \
                     'warning' if g.estado_registro_codigo == Constantes.EstadoRegistroGuiaAereea.OBSERVADO else \
                     'error' if g.estado_registro_codigo == Constantes.EstadoRegistroGuiaAereea.RECHAZADO else 'info'
            
            action = 'Extracción completada' if g.estado_registro_codigo == Constantes.EstadoRegistroGuiaAereea.PROCESADO else \
                     'Revisión requerida' if g.estado_registro_codigo == Constantes.EstadoRegistroGuiaAereea.OBSERVADO else \
                     'Documento rechazado' if g.estado_registro_codigo == Constantes.EstadoRegistroGuiaAereea.RECHAZADO else \
                     'Procesando...'
                     
            activities.append(DashboardActivityItem(
                id=str(g.guia_aerea_id),
                action=action,
                documentNumber=g.numero,
                time=DateUtil.get_time_ago(g.creado),
                user=g.creado_por or 'Sistema',
                status=status
            ))
        return activities
