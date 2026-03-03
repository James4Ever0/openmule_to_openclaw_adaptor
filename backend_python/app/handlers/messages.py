from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List
from ..database import get_db
from ..models.user import User
from ..models.order import Order
from ..models.message import Message
from ..schemas import MessageCreate, MessageResponse
from ..auth import get_current_user
import uuid

router = APIRouter(prefix="/messages", tags=["messages"])


@router.get("/orders/{order_id}/messages", response_model=List[MessageResponse])
async def get_messages(
    order_id: str,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Check if order exists and user has access
    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Check if user has access to this order
    if order.client_id != current_user.id and order.ai_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    result = await db.execute(
        select(Message)
        .where(Message.order_id == order_id)
        .offset(skip)
        .limit(limit)
        .order_by(Message.created_at)
    )
    messages = result.scalars().all()
    return messages


@router.post("/orders/{order_id}/messages", response_model=MessageResponse)
async def send_message(
    order_id: str,
    message_data: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Check if order exists and user has access
    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Check if user has access to this order
    if order.client_id != current_user.id and order.ai_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Determine sender type
    sender_type = "client" if current_user.role == "client" else "ai"
    
    new_message = Message(
        id=str(uuid.uuid4()),
        order_id=order_id,
        sender_id=current_user.id,
        sender_type=sender_type,
        content=message_data.content,
        file_url=message_data.file_url
    )
    
    db.add(new_message)
    await db.commit()
    await db.refresh(new_message)
    
    return new_message
