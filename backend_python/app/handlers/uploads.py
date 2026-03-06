import os
import uuid
import mimetypes
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from ..database import get_db
from ..models.user import User
from ..models.uploaded_file import UploadedFile
from ..schemas import UploadedFileResponse, UploadedFileUpdate, UploadedFileResponseWrapper, UploadedFileListResponseWrapper
from ..auth import get_current_user
from ..config import get_settings

router = APIRouter(prefix="/uploads", tags=["uploads"])
settings = get_settings()

# Create uploads directory if it doesn't exist
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


def get_file_size(file: UploadFile) -> str:
    """Get file size as string"""
    if hasattr(file.file, 'seek'):
        file.file.seek(0, 2)  # Seek to end
        size = file.file.tell()
        file.file.seek(0)  # Reset to beginning
        return str(size)
    return "0"


def generate_unique_filename(filename: str) -> str:
    """Generate unique filename to prevent collisions"""
    file_ext = Path(filename).suffix
    unique_name = f"{uuid.uuid4()}{file_ext}"
    return unique_name


def get_mime_type(filename: str) -> str:
    """Get MIME type for filename"""
    mime_type, _ = mimetypes.guess_type(filename)
    return mime_type or "application/octet-stream"


@router.post("/upload", response_model=UploadedFileResponseWrapper)
async def upload_file(
    file: UploadFile = File(...),
    comment: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Upload a file and return its information"""
    
    # Validate file size (max 50MB)
    max_size = 50 * 1024 * 1024  # 50MB in bytes
    file_size = get_file_size(file)
    if int(file_size) > max_size:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File size exceeds 50MB limit"
        )
    
    # Generate unique filename and path
    unique_filename = generate_unique_filename(file.filename)
    file_path = UPLOAD_DIR / unique_filename
    
    # Save file to disk
    try:
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save file: {str(e)}"
        )
    
    # Generate file URL (assuming you'll serve files via /uploads/{filename})
    file_url = f"/uploads/{unique_filename}"
    
    # Create database record
    uploaded_file = UploadedFile(
        id=str(uuid.uuid4()),
        filename=file.filename,
        file_path=str(file_path),
        file_url=file_url,
        file_size=file_size,
        mime_type=get_mime_type(file.filename),
        comment=comment,
        uploaded_by=current_user.id
    )
    
    db.add(uploaded_file)
    await db.commit()
    await db.refresh(uploaded_file)
    
    return {
        "success": True,
        "data": uploaded_file
    }


@router.get("/")
async def get_user_files(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all files uploaded by the current user"""
    
    result = await db.execute(
        select(UploadedFile)
        .where(UploadedFile.uploaded_by == current_user.id)
        .order_by(UploadedFile.created_at.desc())
    )
    files = result.scalars().all()
    
    return {
        "success": True,
        "data": files
    }


@router.get("/{file_id}", response_model=UploadedFileResponse)
async def get_file_info(
    file_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get information about a specific file"""
    
    # Users can only access their own files, agents can access any file
    if current_user.role == "ai":
        result = await db.execute(
            select(UploadedFile).where(UploadedFile.id == file_id)
        )
    else:
        result = await db.execute(
            select(UploadedFile).where(UploadedFile.id == file_id, UploadedFile.uploaded_by == current_user.id)
        )
    
    file = result.scalar_one_or_none()
    
    if not file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    return file


@router.get("/{file_id}/download")
async def download_file(
    file_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Download a file (users can only download their own files, agents can download any file)"""
    
    # Users can only access their own files, agents can access any file
    if current_user.role == "ai":
        result = await db.execute(
            select(UploadedFile).where(UploadedFile.id == file_id)
        )
    else:
        result = await db.execute(
            select(UploadedFile).where(UploadedFile.id == file_id, UploadedFile.uploaded_by == current_user.id)
        )
    
    file = result.scalar_one_or_none()
    
    if not file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    # Check if file exists on disk
    if not os.path.exists(file.file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found on server"
        )
    
    from fastapi.responses import FileResponse
    
    return FileResponse(
        path=file.file_path,
        filename=file.filename,
        media_type=file.mime_type
    )


@router.put("/{file_id}", response_model=UploadedFileResponse)
async def update_file_comment(
    file_id: str,
    file_update: UploadedFileUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update file comment (users can only update their own files, agents can update any file)"""
    
    # Users can only access their own files, agents can access any file
    if current_user.role == "ai":
        result = await db.execute(
            select(UploadedFile).where(UploadedFile.id == file_id)
        )
    else:
        result = await db.execute(
            select(UploadedFile).where(UploadedFile.id == file_id, UploadedFile.uploaded_by == current_user.id)
        )
    
    file = result.scalar_one_or_none()
    
    if not file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    # Update comment
    if file_update.comment is not None:
        file.comment = file_update.comment
    
    await db.commit()
    await db.refresh(file)
    
    return file


@router.delete("/{file_id}")
async def delete_file(
    file_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a file (users can only delete their own files, agents can delete any file)"""
    
    # Users can only access their own files, agents can access any file
    if current_user.role == "ai":
        result = await db.execute(
            select(UploadedFile).where(UploadedFile.id == file_id)
        )
    else:
        result = await db.execute(
            select(UploadedFile).where(UploadedFile.id == file_id, UploadedFile.uploaded_by == current_user.id)
        )
    
    file = result.scalar_one_or_none()
    
    if not file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    # Delete file from disk
    try:
        if os.path.exists(file.file_path):
            os.remove(file.file_path)
    except Exception as e:
        # Log error but continue with database deletion
        print(f"Failed to delete file from disk: {str(e)}")
    
    # Delete from database
    await db.delete(file)
    await db.commit()
    
    return {"message": "File deleted successfully"}
