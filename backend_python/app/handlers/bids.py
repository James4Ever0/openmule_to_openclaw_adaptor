from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List
from ..database import get_db
from ..models.user import User
from ..models.task import Task
from ..models.bid import Bid
from ..schemas import BidCreate, BidResponse
from ..auth import get_current_user
import uuid

router = APIRouter(tags=["bids"])


@router.post("/tasks/{task_id}/bids", response_model=BidResponse)
async def create_bid(
    task_id: str,
    bid_data: BidCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if current_user.role != "ai":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only AI agents can create bids"
        )
    
    # Check if task exists and is open
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    if task.status != "open":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Task is not open for bidding"
        )
    
    # Check if AI already bid on this task
    existing_bid_result = await db.execute(
        select(Bid).where(and_(Bid.task_id == task_id, Bid.ai_id == current_user.id))
    )
    existing_bid = existing_bid_result.scalar_one_or_none()
    
    if existing_bid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already bid on this task"
        )
    
    # Additional validation for bid amount
    try:
        amount_float = float(bid_data.amount)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bid amount must be a valid number"
        )
    
    if amount_float <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bid amount must be greater than 0"
        )
    
    new_bid = Bid(
        id=str(uuid.uuid4()),
        task_id=task_id,
        ai_id=current_user.id,
        amount=bid_data.amount,
        estimated_days=bid_data.estimated_days,
        message=bid_data.message,
        status="pending"
    )
    
    db.add(new_bid)
    await db.commit()
    await db.refresh(new_bid)
    
    return new_bid


@router.get("/tasks/{task_id}/bids", response_model=List[BidResponse])
async def get_task_bids(
    task_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Check if task exists and user has access
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Only task owner can see all bids
    if task.client_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only task owner can view bids"
        )
    
    result = await db.execute(select(Bid).where(Bid.task_id == task_id))
    bids = result.scalars().all()
    return bids


@router.get("/bids/my-bids", response_model=List[BidResponse])
async def get_user_bids(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if current_user.role != "ai":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only AI agents have bids"
        )
    
    result = await db.execute(select(Bid).where(Bid.ai_id == current_user.id))
    bids = result.scalars().all()
    return bids


@router.post("/tasks/{task_id}/bids/accept")
async def accept_bid(
    task_id: str,
    bid_data: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    bid_id = bid_data.get("bid_id")
    if not bid_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="bid_id is required"
        )
    # Check if task exists and user is owner
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
            detail="Only task owner can accept bids"
        )
    
    # Get the bid
    result = await db.execute(select(Bid).where(Bid.id == bid_id))
    bid = result.scalar_one_or_none()
    
    if not bid:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bid not found"
        )
    
    if bid.task_id != task_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bid does not belong to this task"
        )
    
    # Accept the bid and update task status
    bid.status = "accepted"
    task.status = "assigned"
    
    await db.commit()
    
    return {"message": "Bid accepted successfully"}


@router.delete("/tasks/{task_id}/bids/{bid_id}")
async def reject_bid(
    task_id: str,
    bid_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Check if task exists and user is owner
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
            detail="Only task owner can reject bids"
        )
    
    # Get the bid
    result = await db.execute(select(Bid).where(Bid.id == bid_id))
    bid = result.scalar_one_or_none()
    
    if not bid:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bid not found"
        )
    
    if bid.task_id != task_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bid does not belong to this task"
        )
    
    # Reject the bid
    bid.status = "rejected"
    await db.commit()
    
    return {"message": "Bid rejected successfully"}
