from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from ..database import get_db
from ..models.user import User
from ..models.order import Order
from ..models.withdrawal import Withdrawal
from ..schemas import AiHeartbeatRequest
from ..auth import get_current_user

router = APIRouter(prefix="/ai", tags=["ai"])


@router.get("/stats")
async def get_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if current_user.role != "ai":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only AI agents can access stats"
        )
    
    # Get completed orders count
    completed_orders_result = await db.execute(
        select(func.count(Order.id))
        .where(and_(Order.ai_id == current_user.id, Order.status == "completed"))
    )
    completed_orders = completed_orders_result.scalar()
    
    # Get total earnings
    total_earnings_result = await db.execute(
        select(func.sum(Order.amount))
        .where(and_(Order.ai_id == current_user.id, Order.status == "completed"))
    )
    total_earnings = total_earnings_result.scalar() or "0"
    
    # Get active orders count
    active_orders_result = await db.execute(
        select(func.count(Order.id))
        .where(and_(Order.ai_id == current_user.id, Order.status.in_(["assigned", "delivered"])))
    )
    active_orders = active_orders_result.scalar()
    
    return {
        "completed_orders": completed_orders,
        "total_earnings": total_earnings,
        "active_orders": active_orders,
        "current_balance": current_user.balance or "0"
    }


@router.get("/withdrawals")
async def get_withdrawals(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if current_user.role != "ai":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only AI agents can access withdrawals"
        )
    
    result = await db.execute(
        select(Withdrawal).where(Withdrawal.ai_id == current_user.id)
    )
    withdrawals = result.scalars().all()
    
    return {
        "withdrawals": withdrawals,
        "current_balance": current_user.balance or "0"
    }


@router.post("/heartbeat")
async def heartbeat(
    heartbeat_data: AiHeartbeatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if current_user.role != "ai":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only AI agents can send heartbeat"
        )
    
    # Update AI agent status (you might want to add a status field to User model)
    # For now, just return success
    return {
        "status": "received",
        "message": "Heartbeat received successfully"
    }
