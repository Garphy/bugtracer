import os
from typing import Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.core.config import settings
from backend.app.core.database import get_db
from backend.app.core.deps import get_current_user
from backend.app.models.user import User
from backend.app.schemas.attachment import UploadResponse
from backend.app.services.upload_service import UploadService

router = APIRouter(prefix="/upload", tags=["Uploads"])

@router.post("", response_model=UploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    project_id: int = Form(...),
    bug_id: Optional[int] = Form(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        attachment = await UploadService.save_upload_file(
            db=db,
            file=file,
            project_id=project_id,
            user=current_user,
            bug_id=bug_id
        )
        url = f"/api/upload/file/{attachment.project_id}/{attachment.stored_name}"
        return {
            "success": True,
            "filename": attachment.stored_name,
            "original_name": attachment.original_name,
            "url": url,
            "id": attachment.id,
            "error": None
        }
    except HTTPException as e:
        return {
            "success": False,
            "filename": "",
            "original_name": file.filename or "",
            "url": "",
            "id": None,
            "error": e.detail
        }
    except Exception as e:
        return {
            "success": False,
            "filename": "",
            "original_name": file.filename or "",
            "url": "",
            "id": None,
            "error": str(e)
        }

@router.get("/file/{project_id}/{filename}")
async def get_uploaded_file(project_id: int, filename: str):
    # Prevent path traversal
    safe_filename = os.path.basename(filename)
    file_path = os.path.join(settings.UPLOAD_DIR, str(project_id), safe_filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文件不存在")
    return FileResponse(file_path)

@router.delete("/{attachment_id}")
async def delete_attachment(
    attachment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    await UploadService.delete_attachment(db, attachment_id, current_user)
    return {"message": "附件已删除"}
