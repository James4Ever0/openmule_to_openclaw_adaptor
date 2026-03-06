from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, cast, Numeric
from sqlalchemy.orm import selectinload
from typing import List, Optional
from ..database import get_db
from ..models.user import User
from ..models.task import Task
from ..models.bid import Bid
from ..models.uploaded_file import UploadedFile
from ..models.task_file import TaskFile
from ..schemas import TaskCreate, TaskResponse
from ..auth import get_current_user, get_current_user_optional
import uuid
from decimal import Decimal

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("/")
async def get_tasks(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    status: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    min_budget: Optional[str] = Query(None),
    max_budget: Optional[str] = Query(None),
    sort: Optional[str] = Query("new"),
    page: int = Query(1, ge=1),
    owned: Optional[bool] = Query(None),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db)
):
    # Build query with filters
    query = select(Task).options(selectinload(Task.client))
    
    # Apply filters
    if status:
        query = query.where(Task.status == status)
    if category:
        query = query.where(Task.category == category)
    if min_budget:
        try:
            min_budget_decimal = Decimal(min_budget)
            query = query.where(cast(Task.budget, Numeric) >= min_budget_decimal)
        except (ValueError, TypeError):
            pass  # Invalid min_budget, ignore filter
    if max_budget:
        try:
            max_budget_decimal = Decimal(max_budget)
            query = query.where(cast(Task.budget, Numeric) <= max_budget_decimal)
        except (ValueError, TypeError):
            pass  # Invalid max_budget, ignore filter
    if owned:
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required to view owned tasks"
            )
        query = query.where(Task.client_id == current_user.id)
    
    # Apply sorting
    if sort == "budget_desc":
        query = query.order_by(cast(Task.budget, Numeric).desc())
    elif sort == "budget_asc":
        query = query.order_by(cast(Task.budget, Numeric).asc())
    else:  # "new" or default
        query = query.order_by(Task.created_at.desc())
    
    # Get total count first (before pagination)
    count_query = select(func.count()).select_from(query.subquery())
    count_result = await db.execute(count_query)
    total_count = count_result.scalar()
    
    # Apply pagination
    offset = (page - 1) * limit
    query = query.offset(offset).limit(limit)
    
    result = await db.execute(query)
    tasks = result.scalars().all()
    
    # Get bid counts for all tasks
    task_ids = [task.id for task in tasks]
    bid_counts_query = (
        select(Bid.task_id, func.count(Bid.id).label('bid_count'))
        .where(Bid.task_id.in_(task_ids))
        .group_by(Bid.task_id)
    )
    bid_counts_result = await db.execute(bid_counts_query)
    bid_counts = {row.task_id: row.bid_count for row in bid_counts_result}
    
    # Format response
    task_list = []
    for task in tasks:
        task_dict = {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "budget": task.budget,
            "deadline": task.deadline,
            "status": task.status,
            "category": task.category,
            "attachments": task.attachments,
            "client_id": task.client_id,
            "created_at": task.created_at,
            "client": {
                "id": task.client.id,
                "username": task.client.username
            } if task.client else None,
            "bid_count": bid_counts.get(task.id, 0)
        }
        task_list.append(task_dict)
    
    return {
        "success": True,
        "data": {
            "tasks": task_list,
            "total": total_count,
            "page": page,
            "limit": limit
        }
    }


@router.post("/")
async def create_task(
    task_data: TaskCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if current_user.role != "client":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only clients can create tasks"
        )
    
    # Additional validation for task budget
    try:
        budget_float = float(task_data.budget)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Budget must be a valid number"
        )
    
    if budget_float <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Budget must be greater than 0"
        )
    
    new_task = Task(
        id=str(uuid.uuid4()),
        title=task_data.title,
        description=task_data.description,
        budget=task_data.budget,
        deadline=task_data.deadline,
        status="open",
        category=task_data.category,
        attachments=task_data.attachments,  # Keep for compatibility
        client_id=current_user.id
    )
    
    db.add(new_task)
    await db.commit()
    await db.refresh(new_task)
    
    # If attachments contain file URLs, try to find and link uploaded files
    if task_data.attachments:
        await link_attachments_to_task(new_task.id, task_data.attachments, current_user.id, db)
    
    # Return response in expected format
    task_dict = {
        "id": new_task.id,
        "title": new_task.title,
        "description": new_task.description,
        "budget": new_task.budget,
        "deadline": new_task.deadline,
        "status": new_task.status,
        "category": new_task.category,
        "attachments": new_task.attachments,
        "client_id": new_task.client_id,
        "created_at": new_task.created_at,
        "client": {
            "id": current_user.id,
            "username": current_user.username
        },
        "bid_count": 0
    }
    
    return {
        "success": True,
        "data": task_dict
    }


async def link_attachments_to_task(task_id: str, attachments: List[str], user_id: str, db: AsyncSession):
    """Helper function to link uploaded files to task based on URLs"""
    for attachment_url in attachments:
        # Extract filename from URL to find the uploaded file
        if attachment_url.startswith('/uploads/'):
            filename = attachment_url.split('/')[-1]
            # Find uploaded file by URL
            result = await db.execute(
                select(UploadedFile).where(
                    UploadedFile.file_url == attachment_url,
                    UploadedFile.uploaded_by == user_id
                )
            )
            uploaded_file = result.scalar_one_or_none()
            
            if uploaded_file:
                # Check if already linked
                existing_result = await db.execute(
                    select(TaskFile).where(
                        TaskFile.task_id == task_id,
                        TaskFile.file_id == uploaded_file.id
                    )
                )
                existing = existing_result.scalar_one_or_none()
                
                if not existing:
                    # Create task-file link
                    task_file = TaskFile(
                        task_id=task_id,
                        file_id=uploaded_file.id
                    )
                    db.add(task_file)
    
    await db.commit()


@router.get("/{task_id}")
async def get_task(
    task_id: str,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Task)
        .options(
            selectinload(Task.client), 
            selectinload(Task.bids).selectinload(Bid.ai),
            selectinload(Task.task_files).selectinload(TaskFile.file)
        )
        .where(Task.id == task_id)
    )
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Format task files with file details
    task_files_with_details = []
    for task_file in task.task_files:
        if task_file.file:
            task_files_with_details.append({
                "id": task_file.id,
                "task_id": task_file.task_id,
                "file_id": task_file.file_id,
                "created_at": task_file.created_at,
                "file": {
                    "id": task_file.file.id,
                    "filename": task_file.file.filename,
                    "file_url": task_file.file.file_url,
                    "file_size": task_file.file.file_size,
                    "mime_type": task_file.file.mime_type,
                    "comment": task_file.file.comment,
                    "uploaded_by": task_file.file.uploaded_by,
                    "created_at": task_file.file.created_at
                }
            })
    
    # Format response with bids and task files
    task_dict = {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "budget": task.budget,
        "deadline": task.deadline,
        "status": task.status,
        "category": task.category,
        "attachments": task.attachments,  # Keep for compatibility
        "client_id": task.client_id,
        "created_at": task.created_at,
        "client": {
            "id": task.client.id,
            "username": task.client.username
        } if task.client else None,
        "task_files": task_files_with_details,
        "bids": [
            {
                "id": bid.id,
                "task_id": bid.task_id,
                "ai_id": bid.ai_id,
                "amount": bid.amount,
                "estimated_days": bid.estimated_days,
                "message": bid.message,
                "status": bid.status,
                "created_at": bid.created_at,
                "ai_username": bid.ai.username if bid.ai else None
            }
            for bid in task.bids
        ]
    }
    
    return task_dict


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: str,
    task_data: TaskCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    if task.client_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only task owner can update task"
        )
    
    # Additional validation for task budget
    try:
        budget_float = float(task_data.budget)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Budget must be a valid number"
        )
    
    if budget_float <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Budget must be greater than 0"
        )
    
    # Update task fields
    task.title = task_data.title
    task.description = task_data.description
    task.budget = task_data.budget
    task.deadline = task_data.deadline
    task.category = task_data.category
    task.attachments = task_data.attachments
    
    await db.commit()
    await db.refresh(task)
    
    return task


@router.delete("/{task_id}")
async def delete_task(
    task_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    if task.client_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only task owner can delete task"
        )
    
    if task.status not in ["open", "cancelled"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete task in current status"
        )
    
    await db.delete(task)
    await db.commit()
    
    return {"message": "Task deleted successfully"}
