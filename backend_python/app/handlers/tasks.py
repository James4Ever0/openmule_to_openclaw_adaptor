from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from sqlalchemy.orm import selectinload
from typing import List, Optional
from ..database import get_db
from ..models.user import User
from ..models.task import Task
from ..models.bid import Bid
from ..schemas import TaskCreate, TaskResponse
from ..auth import get_current_user
import uuid

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
        query = query.where(Task.budget >= min_budget)
    if max_budget:
        query = query.where(Task.budget <= max_budget)
    
    # Apply sorting
    if sort == "budget_desc":
        query = query.order_by(Task.budget.desc())
    elif sort == "budget_asc":
        query = query.order_by(Task.budget.asc())
    else:  # "new" or default
        query = query.order_by(Task.created_at.desc())
    
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
            "total": len(task_list),
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
    
    new_task = Task(
        id=str(uuid.uuid4()),
        title=task_data.title,
        description=task_data.description,
        budget=task_data.budget,
        deadline=task_data.deadline,
        status="open",
        category=task_data.category,
        attachments=task_data.attachments,
        client_id=current_user.id
    )
    
    db.add(new_task)
    await db.commit()
    await db.refresh(new_task)
    
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


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: str,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    return task


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
