from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List
from ..database import get_db
from ..models.user import User
from ..models.order import Order
from ..models.task import Task
from ..models.bid import Bid
from ..schemas import OrderResponse
from ..auth import get_current_user
import uuid

router = APIRouter(prefix="/orders", tags=["orders"])


@router.get("/", response_model=List[OrderResponse])
async def get_orders(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Get orders where user is either client or AI
    result = await db.execute(
        select(Order).where(
            and_(
                Order.client_id == current_user.id,
                Order.ai_id == current_user.id
            )
        ).offset(skip).limit(limit)
    )
    orders = result.scalars().all()
    return orders


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
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
    
    return order


@router.post("/{order_id}/pay")
async def pay_order(
    order_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    if order.client_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only client can pay for order"
        )
    
    if order.payment_status != "unpaid":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order is already paid"
        )
    
    # Update payment status (in real implementation, integrate with payment gateway)
    order.payment_status = "paid"
    order.paid_at = datetime.utcnow()
    order.status = "assigned"
    
    await db.commit()
    
    return {"message": "Order paid successfully"}


@router.post("/{order_id}/deliver")
async def deliver_order(
    order_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    if order.ai_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only AI can deliver order"
        )
    
    if order.status != "assigned":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order cannot be delivered in current status"
        )
    
    # Update order status
    order.status = "delivered"
    order.delivered_at = datetime.utcnow()
    
    await db.commit()
    
    return {"message": "Order delivered successfully"}


@router.post("/{order_id}/accept")
async def accept_order(
    order_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    if order.client_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only client can accept order"
        )
    
    if order.status != "delivered":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order must be delivered before acceptance"
        )
    
    # Update order status
    order.status = "completed"
    order.completed_at = datetime.utcnow()
    
    await db.commit()
    
    return {"message": "Order accepted and completed successfully"}


@router.post("/{order_id}/reject")
async def reject_order(
    order_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    if order.client_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only client can reject order"
        )
    
    if order.status != "delivered":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order must be delivered before rejection"
        )
    
    # Update order status
    order.status = "disputed"
    
    await db.commit()
    
    return {"message": "Order rejected and marked as disputed"}


@router.post("/{order_id}/cancel")
async def cancel_order(
    order_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    if order.client_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only client can cancel order"
        )
    
    if order.status not in ["pending_payment", "assigned"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order cannot be cancelled in current status"
        )
    
    # Update order status
    order.status = "cancelled"
    
    # Refund if paid
    if order.payment_status == "paid":
        order.payment_status = "refunded"
    
    await db.commit()
    
    return {"message": "Order cancelled successfully"}
