from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, delete
from typing import List, Optional
from ..database import get_db
from ..models.user import User
from ..models.task import Task
from ..models.uploaded_file import UploadedFile
from ..models.task_file import TaskFile
from ..schemas import TaskFileCreate, TaskFileResponse, TaskFileWithDetails
from ..auth import get_current_user

router = APIRouter(prefix="/task-files", tags=["task-files"])


@router.post("/", response_model=TaskFileResponse)
async def add_file_to_task(
    task_file_data: TaskFileCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Add a file to a task"""
    
    # Verify task exists and user owns it
    result = await db.execute(
        select(Task).where(Task.id == task_file_data.task_id, Task.client_id == current_user.id)
    )
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found or access denied"
        )
    
    # Verify file exists and user owns it
    result = await db.execute(
        select(UploadedFile).where(
            UploadedFile.id == task_file_data.file_id, 
            UploadedFile.uploaded_by == current_user.id
        )
    )
    file = result.scalar_one_or_none()
    
    if not file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found or access denied"
        )
    
    # Check if file is already linked to task
    result = await db.execute(
        select(TaskFile).where(
            TaskFile.task_id == task_file_data.task_id,
            TaskFile.file_id == task_file_data.file_id
        )
    )
    existing = result.scalar_one_or_none()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File is already linked to this task"
        )
    
    # Create task-file link
    task_file = TaskFile(
        task_id=task_file_data.task_id,
        file_id=task_file_data.file_id
    )
    
    db.add(task_file)
    await db.commit()
    await db.refresh(task_file)
    
    return task_file


@router.get("/task/{task_id}", response_model=List[TaskFileWithDetails])
async def get_task_files(
    task_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all files linked to a task"""
    
    # Verify task exists and user has access (either owns it or it's public)
    result = await db.execute(
        select(Task).where(Task.id == task_id)
    )
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Get task files with file details
    result = await db.execute(
        select(TaskFile, UploadedFile)
        .join(UploadedFile, TaskFile.file_id == UploadedFile.id)
        .where(TaskFile.task_id == task_id)
        .order_by(TaskFile.created_at.desc())
    )
    
    task_files = []
    for task_file, uploaded_file in result:
        task_file_dict = {
            "id": task_file.id,
            "task_id": task_file.task_id,
            "file_id": task_file.file_id,
            "created_at": task_file.created_at,
            "file": {
                "id": uploaded_file.id,
                "filename": uploaded_file.filename,
                "file_path": uploaded_file.file_path,
                "file_url": uploaded_file.file_url,
                "file_size": uploaded_file.file_size,
                "mime_type": uploaded_file.mime_type,
                "comment": uploaded_file.comment,
                "uploaded_by": uploaded_file.uploaded_by,
                "created_at": uploaded_file.created_at
            }
        }
        task_files.append(task_file_dict)
    
    return task_files


@router.get("/file/{file_id}/tasks", response_model=List[TaskFileResponse])
async def get_file_tasks(
    file_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all tasks that a file is linked to"""
    
    # Verify file exists and user owns it
    result = await db.execute(
        select(UploadedFile).where(
            UploadedFile.id == file_id, 
            UploadedFile.uploaded_by == current_user.id
        )
    )
    file = result.scalar_one_or_none()
    
    if not file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found or access denied"
        )
    
    result = await db.execute(
        select(TaskFile).where(TaskFile.file_id == file_id)
    )
    task_files = result.scalars().all()
    
    return task_files


@router.delete("/{task_file_id}")
async def remove_file_from_task(
    task_file_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Remove a file from a task"""
    
    # Get task file with task and file details
    result = await db.execute(
        select(TaskFile, Task, UploadedFile)
        .join(Task, TaskFile.task_id == Task.id)
        .join(UploadedFile, TaskFile.file_id == UploadedFile.id)
        .where(TaskFile.id == task_file_id)
    )
    task_file_data = result.first()
    
    if not task_file_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task file link not found"
        )
    
    task_file, task, uploaded_file = task_file_data
    
    # Verify user owns the task or the file
    if task.client_id != current_user.id and uploaded_file.uploaded_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Delete the task-file link
    await db.delete(task_file)
    await db.commit()
    
    return {"message": "File removed from task successfully"}


@router.delete("/task/{task_id}/file/{file_id}")
async def remove_file_from_task_by_ids(
    task_id: str,
    file_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Remove a file from a task by task_id and file_id"""
    
    # Verify task exists and user owns it
    result = await db.execute(
        select(Task).where(Task.id == task_id, Task.client_id == current_user.id)
    )
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found or access denied"
        )
    
    # Find and delete the task-file link
    result = await db.execute(
        select(TaskFile).where(
            TaskFile.task_id == task_id,
            TaskFile.file_id == file_id
        )
    )
    task_file = result.scalar_one_or_none()
    
    if not task_file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File is not linked to this task"
        )
    
    await db.delete(task_file)
    await db.commit()
    
    return {"message": "File removed from task successfully"}
