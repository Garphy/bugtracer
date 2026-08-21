from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.core.database import get_db
from backend.app.core.deps import get_current_user
from backend.app.models.user import User
from backend.app.schemas.report import ProjectStatsReport, FullProjectReportResponse
from backend.app.services.report_service import ReportService

router = APIRouter(prefix="/reports", tags=["Reports"])

@router.get("/stats/{project_id}", response_model=ProjectStatsReport)
async def get_project_stats(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await ReportService.get_project_stats(db, project_id)

@router.get("/full/{project_id}", response_model=FullProjectReportResponse)
async def get_full_report(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await ReportService.get_full_report(db, project_id)

@router.get("/export/{project_id}")
async def export_csv(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    csv_data = await ReportService.export_csv(db, project_id)
    return Response(
        content=csv_data.encode("utf-8-sig"),  # UTF-8 with BOM for Excel compatibility
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=bugtracer_project_{project_id}.csv"
        }
    )
