import os
import time
import uuid
import aiofiles
from typing import Optional, Tuple
from fastapi import UploadFile, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.app.core.config import settings
from backend.app.models.attachment import Attachment
from backend.app.models.user import User
from backend.app.models.project import Project

class UploadService:
    @staticmethod
    async def save_upload_file(
        db: AsyncSession,
        file: UploadFile,
        project_id: int,
        user: User,
        bug_id: Optional[int] = None
    ) -> Attachment:
        original_name = file.filename or "unknown"
        ext = original_name.split(".")[-1].lower() if "." in original_name else ""

        if settings.ALLOWED_EXTENSIONS and ext not in settings.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"不支持该文件格式 (.{ext})，仅支持: {', '.join(settings.ALLOWED_EXTENSIONS[:8])} 等"
            )

        # Check project
        stmt_prj = select(Project).where(Project.id == project_id)
        res_prj = await db.execute(stmt_prj)
        if not res_prj.scalars().first():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="项目不存在")

        # Project directory
        project_dir = os.path.join(settings.UPLOAD_DIR, str(project_id))
        os.makedirs(project_dir, exist_ok=True)

        # Generate unique stored filename (compatible with legacy style: hex timestamp + uuid/random)
        timestamp_hex = hex(int(time.time()))[2:]
        random_hex = uuid.uuid4().hex[:8]
        stored_name = f"{timestamp_hex}_{random_hex}.{ext}" if ext else f"{timestamp_hex}_{random_hex}"
        file_path = os.path.join(project_dir, stored_name)

        # Save file asynchronously
        file_size = 0
        async with aiofiles.open(file_path, "wb") as out_file:
            while content := await file.read(1024 * 1024):  # 1MB chunk
                file_size += len(content)
                if file_size > settings.MAX_UPLOAD_SIZE:
                    # Clean up
                    await out_file.close()
                    if os.path.exists(file_path):
                        os.remove(file_path)
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"文件超出最大限制 ({settings.MAX_UPLOAD_SIZE // (1024*1024)}MB)"
                    )
                await out_file.write(content)

        # Create Attachment record
        attachment = Attachment(
            bug_id=bug_id,
            project_id=project_id,
            uploader_id=user.id,
            original_name=original_name,
            stored_name=stored_name,
            file_path=file_path,
            file_size=file_size,
            mime_type=file.content_type or "application/octet-stream"
        )
        db.add(attachment)
        await db.commit()
        await db.refresh(attachment)
        return attachment

    @staticmethod
    async def delete_attachment(db: AsyncSession, attachment_id: int, user: User):
        stmt = select(Attachment).where(Attachment.id == attachment_id)
        result = await db.execute(stmt)
        att = result.scalars().first()
        if not att:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="附件不存在")

        # Permission check
        if user.role != "admin" and att.uploader_id != user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权删除该附件")

        if os.path.exists(att.file_path):
            try:
                os.remove(att.file_path)
            except Exception:
                pass

        await db.delete(att)
        await db.commit()
