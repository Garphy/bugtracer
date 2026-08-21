import io
import csv
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status
from backend.app.models.bug import Bug, STATUS_MAP, STATUS_NAMES
from backend.app.models.project import Project
from backend.app.models.module import Module
from backend.app.models.user import User
from backend.app.models.attachment import Attachment

ACTIVE_STATUS_IDS = [1, 2, 3]  # new, key, part_fixed
FIXED_STATUS_IDS = [0, 4]      # closed, fixed

class ReportService:
    @staticmethod
    async def get_project_stats(db: AsyncSession, project_id: int) -> Dict[str, Any]:
        # Project check
        stmt_prj = select(Project).where(Project.id == project_id)
        res_prj = await db.execute(stmt_prj)
        project = res_prj.scalars().first()
        if not project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="项目不存在")

        # 1. Status breakdown
        stmt_status = select(
            Bug.status,
            func.count(Bug.id).label("count")
        ).where(Bug.project_id == project_id).group_by(Bug.status)
        res_status = await db.execute(stmt_status)
        status_map = {row.status: row.count for row in res_status.all()}

        total_bugs = sum(status_map.values())
        active_bugs = sum(status_map.get(s, 0) for s in ACTIVE_STATUS_IDS)
        fixed_bugs = sum(status_map.get(s, 0) for s in FIXED_STATUS_IDS)
        closed_bugs = status_map.get(0, 0)
        key_bugs = status_map.get(2, 0)

        status_distribution = {
            STATUS_MAP.get(s, f"status_{s}"): count for s, count in status_map.items()
        }

        # 2. Member stats
        # Get all users in project or with bugs in project
        stmt_users = select(User).where(User.is_active == True).order_by(User.role, User.id)
        res_users = await db.execute(stmt_users)
        users = list(res_users.scalars().all())

        # Aggregate counts by assignee and status
        stmt_user_bugs = select(
            Bug.assignee_id,
            Bug.status,
            func.count(Bug.id).label("count")
        ).where(Bug.project_id == project_id).group_by(Bug.assignee_id, Bug.status)
        res_user_bugs = await db.execute(stmt_user_bugs)
        
        user_bugs_matrix = {}
        for row in res_user_bugs.all():
            aid = row.assignee_id or 0
            if aid not in user_bugs_matrix:
                user_bugs_matrix[aid] = {}
            user_bugs_matrix[aid][row.status] = row.count

        member_stats = []
        # Add '0' (Unassigned) if has bugs
        if 0 in user_bugs_matrix:
            u_map = user_bugs_matrix[0]
            member_stats.append({
                "user_id": 0,
                "fullname": "未指派",
                "username": "unassigned",
                "role": "none",
                "active_count": sum(u_map.get(s, 0) for s in ACTIVE_STATUS_IDS),
                "fixed_count": sum(u_map.get(s, 0) for s in FIXED_STATUS_IDS),
                "key_count": u_map.get(2, 0),
                "total_count": sum(u_map.values())
            })

        for u in users:
            u_map = user_bugs_matrix.get(u.id, {})
            u_total = sum(u_map.values())
            if u_total > 0 or u.role == "coder":
                member_stats.append({
                    "user_id": u.id,
                    "fullname": u.fullname,
                    "username": u.username,
                    "role": u.role,
                    "active_count": sum(u_map.get(s, 0) for s in ACTIVE_STATUS_IDS),
                    "fixed_count": sum(u_map.get(s, 0) for s in FIXED_STATUS_IDS),
                    "key_count": u_map.get(2, 0),
                    "total_count": u_total
                })

        # 3. Module stats
        stmt_modules = select(Module).where(Module.project_id == project_id).order_by(Module.sort_order)
        res_modules = await db.execute(stmt_modules)
        modules = list(res_modules.scalars().all())

        stmt_mod_bugs = select(
            Bug.module_id,
            Bug.status,
            func.count(Bug.id).label("count")
        ).where(Bug.project_id == project_id).group_by(Bug.module_id, Bug.status)
        res_mod_bugs = await db.execute(stmt_mod_bugs)
        
        mod_bugs_matrix = {}
        for row in res_mod_bugs.all():
            mid = row.module_id or 0
            if mid not in mod_bugs_matrix:
                mod_bugs_matrix[mid] = {}
            mod_bugs_matrix[mid][row.status] = row.count

        module_stats = []
        for m in modules:
            m_map = mod_bugs_matrix.get(m.id, {})
            module_stats.append({
                "module_id": m.id,
                "module_name": m.name,
                "active_count": sum(m_map.get(s, 0) for s in ACTIVE_STATUS_IDS),
                "fixed_count": sum(m_map.get(s, 0) for s in FIXED_STATUS_IDS),
                "total_count": sum(m_map.values())
            })

        # 4. Daily trend (past 14 days)
        today = datetime.now(timezone.utc).date()
        daily_trend = []
        for i in range(13, -1, -1):
            d = today - timedelta(days=i)
            dt_start = datetime(d.year, d.month, d.day, 0, 0, 0, tzinfo=timezone.utc)
            dt_end = datetime(d.year, d.month, d.day, 23, 59, 59, tzinfo=timezone.utc)
            
            # Created count
            c_stmt = select(func.count(Bug.id)).where(
                Bug.project_id == project_id,
                Bug.created_at >= dt_start,
                Bug.created_at <= dt_end
            )
            c_res = await db.execute(c_stmt)
            created_count = c_res.scalar_one()

            # Fixed count
            f_stmt = select(func.count(Bug.id)).where(
                Bug.project_id == project_id,
                Bug.fixed_at >= dt_start,
                Bug.fixed_at <= dt_end
            )
            f_res = await db.execute(f_stmt)
            fixed_count = f_res.scalar_one()

            daily_trend.append({
                "date": d.strftime("%m-%d"),
                "created": created_count,
                "fixed": fixed_count
            })

        return {
            "project_id": project.id,
            "project_name": project.name,
            "total_bugs": total_bugs,
            "active_bugs": active_bugs,
            "fixed_bugs": fixed_bugs,
            "closed_bugs": closed_bugs,
            "key_bugs": key_bugs,
            "member_stats": member_stats,
            "module_stats": module_stats,
            "status_distribution": status_distribution,
            "daily_trend": daily_trend
        }

    @staticmethod
    async def get_full_report(db: AsyncSession, project_id: int) -> Dict[str, Any]:
        stats = await ReportService.get_project_stats(db, project_id)

        # Get all bugs for report grouped by module
        stmt = (
            select(Bug)
            .where(Bug.project_id == project_id)
            .order_by(Bug.module_id, Bug.id.desc())
            .options(
                selectinload(Bug.module),
                selectinload(Bug.creator),
                selectinload(Bug.assignee),
                selectinload(Bug.attachments)
            )
        )
        result = await db.execute(stmt)
        bugs = list(result.scalars().all())

        bugs_by_module: Dict[str, List] = {}
        for b in bugs:
            mod_name = b.module.name if b.module else "通用模块"
            if mod_name not in bugs_by_module:
                bugs_by_module[mod_name] = []
                
            bugs_by_module[mod_name].append({
                "id": b.id,
                "project_id": b.project_id,
                "module_id": b.module_id,
                "module_name": mod_name,
                "status": b.status,
                "status_code": b.status_code,
                "status_name": b.status_name,
                "ver": b.ver,
                "content": b.content,
                "has_attachment": len(b.attachments) > 0,
                "creator_name": b.creator.fullname if b.creator else "匿名",
                "assignee_name": b.assignee.fullname if (b.assignee and b.assignee_id > 0) else "未指派",
                "priority": b.priority,
                "created_at": b.created_at,
                "updated_at": b.updated_at
            })

        return {
            "project_id": stats["project_id"],
            "project_name": stats["project_name"],
            "stats": stats,
            "bugs_by_module": bugs_by_module
        }

    @staticmethod
    async def export_csv(db: AsyncSession, project_id: int) -> str:
        stmt = (
            select(Bug)
            .where(Bug.project_id == project_id)
            .order_by(Bug.id.desc())
            .options(
                selectinload(Bug.module),
                selectinload(Bug.creator),
                selectinload(Bug.assignee)
            )
        )
        result = await db.execute(stmt)
        bugs = list(result.scalars().all())

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["ID", "所属模块", "状态", "版本", "描述", "提交人", "指派人", "创建时间", "更新时间"])

        for b in bugs:
            writer.writerow([
                b.id,
                b.module.name if b.module else "未分类",
                b.status_name,
                b.ver,
                b.content.replace("\n", " "),
                b.creator.fullname if b.creator else "",
                b.assignee.fullname if (b.assignee and b.assignee_id > 0) else "未指派",
                b.created_at.strftime("%Y-%m-%d %H:%M:%S") if b.created_at else "",
                b.updated_at.strftime("%Y-%m-%d %H:%M:%S") if b.updated_at else ""
            ])

        return output.getvalue()
