import math
from datetime import datetime, timezone
from typing import Optional, List, Dict, Tuple, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, and_, update, delete
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status
from backend.app.models.bug import Bug, STATUS_MAP, STATUS_NAMES
from backend.app.models.project import Project
from backend.app.models.module import Module
from backend.app.models.user import User
from backend.app.models.attachment import Attachment
from backend.app.models.comment import Comment
from backend.app.models.activity import Activity
from backend.app.schemas.bug import BugCreate, BugUpdate, BugStatusUpdate
from backend.app.core.search_parser import parse_search_query

DEFAULT_STATUS_FILTER = [1, 2, 3]  # new, key, part_fixed

class BugService:
    @staticmethod
    async def list_bugs(
        db: AsyncSession,
        project_id: int,
        module_id: Optional[int] = None,
        statuses: Optional[List[int]] = None,
        search: Optional[str] = None,
        mode: str = "admin",  # 'admin' or 'coder'
        current_user: Optional[User] = None,
        order_by: str = "id",
        order_desc: bool = True,
        page: int = 1,
        page_size: int = 30
    ) -> Dict[str, Any]:
        parsed_search = parse_search_query(search)
        
        # Base query
        stmt = select(Bug).where(Bug.project_id == project_id)
        
        # Apply search parser conditions if search query exists
        if not parsed_search.is_empty:
            if parsed_search.bug_ids:
                stmt = stmt.where(Bug.id.in_(parsed_search.bug_ids))
            if parsed_search.creator_id:
                stmt = stmt.where(Bug.creator_id == parsed_search.creator_id)
            if parsed_search.assignee_id:
                stmt = stmt.where(Bug.assignee_id == parsed_search.assignee_id)
            if parsed_search.exclude_assignee_id:
                stmt = stmt.where(Bug.assignee_id != parsed_search.exclude_assignee_id)
            if parsed_search.time_start and parsed_search.time_end:
                stmt = stmt.where(Bug.updated_at >= parsed_search.time_start, Bug.updated_at <= parsed_search.time_end)
            if parsed_search.keyword:
                kw = f"%{parsed_search.keyword}%"
                stmt = stmt.where(or_(Bug.content.like(kw), Bug.title.like(kw), Bug.ver.like(kw)))
                
        # Module filter
        if module_id is not None and module_id > 0:
            stmt = stmt.where(Bug.module_id == module_id)
            
        # Status filter
        if statuses is not None and len(statuses) > 0:
            stmt = stmt.where(Bug.status.in_(statuses))
        elif parsed_search.is_empty:
            # Default filter when not searching
            stmt = stmt.where(Bug.status.in_(DEFAULT_STATUS_FILTER))
            
        # Coder mode filter
        if mode == "coder" and current_user:
            stmt = stmt.where(Bug.assignee_id == current_user.id)
            
        # Total counts
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_res = await db.execute(count_stmt)
        total = total_res.scalar_one()
        
        # Ordering
        order_col = Bug.id
        if order_by == "updated_at" or order_by == "changetime":
            order_col = Bug.updated_at
        elif order_by == "created_at":
            order_col = Bug.created_at
        elif order_by == "status":
            order_col = Bug.status
        elif order_by == "priority":
            order_col = Bug.priority
            
        stmt = stmt.order_by(order_col.desc() if order_desc else order_col.asc())
        
        # Pagination
        offset = (page - 1) * page_size
        stmt = stmt.offset(offset).limit(page_size)
        
        # Load related entities
        stmt = stmt.options(
            selectinload(Bug.project),
            selectinload(Bug.module),
            selectinload(Bug.creator),
            selectinload(Bug.assignee),
            selectinload(Bug.last_changer),
            selectinload(Bug.attachments)
        )
        
        result = await db.execute(stmt)
        bugs = list(result.scalars().all())
        
        items = []
        for b in bugs:
            items.append({
                "id": b.id,
                "project_id": b.project_id,
                "project_name": b.project.name if b.project else "",
                "module_id": b.module_id,
                "module_name": b.module.name if b.module else "未分类",
                "status": b.status,
                "status_code": b.status_code,
                "status_name": b.status_name,
                "ver": b.ver,
                "content": b.content,
                "has_attachment": len(b.attachments) > 0,
                "creator_id": b.creator_id,
                "creator_name": b.creator.fullname if b.creator else "匿名",
                "assignee_id": b.assignee_id,
                "assignee_name": b.assignee.fullname if (b.assignee and b.assignee_id > 0) else "未指派",
                "last_changer_name": b.last_changer.fullname if b.last_changer else "",
                "is_assigned_to_me": (current_user is not None and b.assignee_id == current_user.id),
                "priority": b.priority,
                "created_at": b.created_at,
                "updated_at": b.updated_at
            })
            
        # Total project bugs
        total_project_bugs_stmt = select(func.count(Bug.id)).where(Bug.project_id == project_id)
        total_project_bugs_res = await db.execute(total_project_bugs_stmt)
        total_project_bugs = total_project_bugs_res.scalar_one()
        
        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": math.ceil(total / page_size) if total > 0 else 1,
            "items": items,
            "counts_summary": {
                "shown": total,
                "total_in_project": total_project_bugs
            }
        }

    @staticmethod
    async def get_bug(db: AsyncSession, bug_id: int) -> Dict[str, Any]:
        stmt = (
            select(Bug)
            .where(Bug.id == bug_id)
            .options(
                selectinload(Bug.project),
                selectinload(Bug.module),
                selectinload(Bug.creator),
                selectinload(Bug.assignee),
                selectinload(Bug.last_changer),
                selectinload(Bug.attachments),
                selectinload(Bug.comments).selectinload(Comment.user),
                selectinload(Bug.activities).selectinload(Activity.user)
            )
        )
        result = await db.execute(stmt)
        b = result.scalars().first()
        if not b:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="缺陷不存在")

        attachments_out = []
        for att in b.attachments:
            attachments_out.append({
                "id": att.id,
                "bug_id": att.bug_id,
                "project_id": att.project_id,
                "original_name": att.original_name,
                "stored_name": att.stored_name,
                "file_size": att.file_size,
                "mime_type": att.mime_type,
                "url": f"/api/upload/file/{att.project_id}/{att.stored_name}",
                "created_at": att.created_at
            })

        comments_out = []
        for c in b.comments:
            comments_out.append({
                "id": c.id,
                "bug_id": c.bug_id,
                "user_id": c.user_id,
                "user": {
                    "id": c.user.id,
                    "username": c.user.username,
                    "fullname": c.user.fullname,
                    "role": c.user.role
                } if c.user else None,
                "content": c.content,
                "created_at": c.created_at
            })

        activities_out = []
        for act in b.activities:
            activities_out.append({
                "id": act.id,
                "bug_id": act.bug_id,
                "user_id": act.user_id,
                "user": {
                    "id": act.user.id,
                    "username": act.user.username,
                    "fullname": act.user.fullname,
                    "role": act.user.role
                } if act.user else None,
                "action_type": act.action_type,
                "old_value": act.old_value,
                "new_value": act.new_value,
                "detail": act.detail,
                "created_at": act.created_at
            })

        return {
            "id": b.id,
            "project_id": b.project_id,
            "project_name": b.project.name if b.project else "",
            "module_id": b.module_id,
            "module_name": b.module.name if b.module else "未分类",
            "status": b.status,
            "status_code": b.status_code,
            "status_name": b.status_name,
            "ver": b.ver,
            "content": b.content,
            "creator_id": b.creator_id,
            "creator": {
                "id": b.creator.id,
                "username": b.creator.username,
                "fullname": b.creator.fullname,
                "role": b.creator.role
            } if b.creator else None,
            "assignee_id": b.assignee_id,
            "assignee": {
                "id": b.assignee.id,
                "username": b.assignee.username,
                "fullname": b.assignee.fullname,
                "role": b.assignee.role
            } if (b.assignee and b.assignee_id > 0) else None,
            "last_changer_id": b.last_changer_id,
            "last_changer": {
                "id": b.last_changer.id,
                "username": b.last_changer.username,
                "fullname": b.last_changer.fullname,
                "role": b.last_changer.role
            } if b.last_changer else None,
            "priority": b.priority,
            "close_reason": b.close_reason,
            "created_at": b.created_at,
            "updated_at": b.updated_at,
            "fixed_at": b.fixed_at,
            "attachments": attachments_out,
            "comments": comments_out,
            "activities": activities_out
        }

    @staticmethod
    async def create_bug(db: AsyncSession, bug_in: BugCreate, current_user: User) -> Bug:
        # Check project
        stmt_prj = select(Project).where(Project.id == bug_in.project_id)
        res_prj = await db.execute(stmt_prj)
        if not res_prj.scalars().first():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="项目不存在")

        bug = Bug(
            project_id=bug_in.project_id,
            module_id=bug_in.module_id if bug_in.module_id and bug_in.module_id > 0 else None,
            ver=bug_in.ver or "",
            content=bug_in.content,
            status=bug_in.status if bug_in.status in STATUS_MAP else 1,
            creator_id=current_user.id,
            assignee_id=bug_in.assignee_id or 0,
            last_changer_id=current_user.id,
            priority=bug_in.priority
        )
        db.add(bug)
        await db.flush()

        # Link attachments if provided
        if bug_in.attachment_ids:
            att_stmt = select(Attachment).where(Attachment.id.in_(bug_in.attachment_ids))
            att_res = await db.execute(att_stmt)
            for att in att_res.scalars().all():
                att.bug_id = bug.id
                
        # Link attachments by filename if provided
        if bug_in.files:
            att_stmt = select(Attachment).where(
                Attachment.project_id == bug.project_id,
                Attachment.stored_name.in_(bug_in.files)
            )
            att_res = await db.execute(att_stmt)
            for att in att_res.scalars().all():
                att.bug_id = bug.id

        # Log Activity
        act = Activity(
            bug_id=bug.id,
            user_id=current_user.id,
            action_type="create",
            old_value="",
            new_value="new",
            detail=f"提交了缺陷 #{bug.id}"
        )
        db.add(act)

        await db.commit()
        await db.refresh(bug)
        return bug

    @staticmethod
    async def update_bug(db: AsyncSession, bug_id: int, bug_in: BugUpdate, current_user: User) -> Bug:
        stmt = select(Bug).where(Bug.id == bug_id)
        result = await db.execute(stmt)
        bug = result.scalars().first()
        if not bug:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="缺陷不存在")

        changes = []
        if bug_in.module_id is not None and bug_in.module_id != bug.module_id:
            changes.append(f"所属模块变更: {bug.module_id} -> {bug_in.module_id}")
            bug.module_id = bug_in.module_id if bug_in.module_id > 0 else None

        if bug_in.ver is not None and bug_in.ver != bug.ver:
            changes.append(f"版本变更: {bug.ver} -> {bug_in.ver}")
            bug.ver = bug_in.ver

        if bug_in.content is not None and bug_in.content != bug.content:
            changes.append("修改了描述内容")
            bug.content = bug_in.content

        if bug_in.assignee_id is not None and bug_in.assignee_id != bug.assignee_id:
            changes.append(f"重新指派: {bug.assignee_id} -> {bug_in.assignee_id}")
            bug.assignee_id = bug_in.assignee_id

        if bug_in.priority is not None and bug_in.priority != bug.priority:
            changes.append(f"优先级变更: {bug.priority} -> {bug_in.priority}")
            bug.priority = bug_in.priority

        if bug_in.status is not None and bug_in.status != bug.status:
            old_status = bug.status_name
            bug.status = bug_in.status
            new_status = bug.status_name
            changes.append(f"状态变更: {old_status} -> {new_status}")
            if bug.status == 4:  # fixed
                bug.fixed_at = datetime.now(timezone.utc)

        if bug_in.close_reason is not None:
            bug.close_reason = bug_in.close_reason

        # Link any newly provided attachment_ids or files
        if bug_in.attachment_ids:
            att_stmt = select(Attachment).where(Attachment.id.in_(bug_in.attachment_ids))
            att_res = await db.execute(att_stmt)
            for att in att_res.scalars().all():
                att.bug_id = bug.id

        if bug_in.files:
            att_stmt = select(Attachment).where(
                Attachment.project_id == bug.project_id,
                Attachment.stored_name.in_(bug_in.files)
            )
            att_res = await db.execute(att_stmt)
            for att in att_res.scalars().all():
                att.bug_id = bug.id

        bug.last_changer_id = current_user.id
        bug.updated_at = datetime.now(timezone.utc)

        if changes:
            act = Activity(
                bug_id=bug.id,
                user_id=current_user.id,
                action_type="edit",
                old_value="",
                new_value="",
                detail="; ".join(changes)
            )
            db.add(act)

        await db.commit()
        await db.refresh(bug)
        return bug

    @staticmethod
    async def update_status(db: AsyncSession, bug_id: int, status_update: BugStatusUpdate, current_user: User) -> Bug:
        stmt = select(Bug).where(Bug.id == bug_id)
        result = await db.execute(stmt)
        bug = result.scalars().first()
        if not bug:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="缺陷不存在")

        old_status_name = bug.status_name
        bug.status = status_update.status
        if status_update.close_reason:
            bug.close_reason = status_update.close_reason

        if bug.status == 4:  # fixed
            bug.fixed_at = datetime.now(timezone.utc)
            
        bug.last_changer_id = current_user.id
        bug.updated_at = datetime.now(timezone.utc)

        act = Activity(
            bug_id=bug.id,
            user_id=current_user.id,
            action_type="status_change",
            old_value=old_status_name,
            new_value=bug.status_name,
            detail=f"状态设为 [{bug.status_name}]" + (f" 原因: {status_update.close_reason}" if status_update.close_reason else "")
        )
        db.add(act)

        await db.commit()
        await db.refresh(bug)
        return bug

    @staticmethod
    async def add_comment(db: AsyncSession, bug_id: int, content: str, current_user: User) -> Comment:
        stmt = select(Bug).where(Bug.id == bug_id)
        result = await db.execute(stmt)
        bug = result.scalars().first()
        if not bug:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="缺陷不存在")

        comment = Comment(
            bug_id=bug.id,
            user_id=current_user.id,
            content=content
        )
        db.add(comment)

        bug.last_changer_id = current_user.id
        bug.updated_at = datetime.now(timezone.utc)

        act = Activity(
            bug_id=bug.id,
            user_id=current_user.id,
            action_type="comment",
            old_value="",
            new_value="",
            detail=f"发表了讨论: {content[:50]}"
        )
        db.add(act)

        await db.commit()
        await db.refresh(comment)
        return comment
