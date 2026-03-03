from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List
from ..database import get_db
from ..models.user import User
from ..models.order import Order
from ..models.refund_request import RefundRequest
from ..models.dispute import Dispute
from ..schemas import ProcessRefundRequest, ResolveDisputeRequest
from ..auth import get_current_user

router = APIRouter(prefix="/cs", tags=["customer-service"])


@router.get("/refund-requests")
async def get_refund_requests(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if current_user.role != "admin":  # Assuming admin role for CS
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only customer service can access refund requests"
        )
    
    result = await db.execute(
        select(RefundRequest)
        .offset(skip)
        .limit(limit)
        .order_by(RefundRequest.created_at.desc())
    )
    refund_requests = result.scalars().all()
    
    return {"refund_requests": refund_requests}


@router.get("/refund-requests/{refund_id}")
async def get_refund_request(
    refund_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only customer service can access refund requests"
        )
    
    result = await db.execute(select(RefundRequest).where(RefundRequest.id == refund_id))
    refund_request = result.scalar_one_or_none()
    
    if not refund_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Refund request not found"
        )
    
    return refund_request


@router.post("/refund-requests/{refund_id}/process")
async def process_refund(
    refund_id: str,
    process_data: ProcessRefundRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only customer service can process refund requests"
        )
    
    result = await db.execute(select(RefundRequest).where(RefundRequest.id == refund_id))
    refund_request = result.scalar_one_or_none()
    
    if not refund_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Refund request not found"
        )
    
    if refund_request.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Refund request has already been processed"
        )
    
    # Update refund request status
    refund_request.status = process_data.decision
    
    # If approved, update order payment status
    if process_data.decision == "approved":
        order_result = await db.execute(select(Order).where(Order.id == refund_request.order_id))
        order = order_result.scalar_one_or_none()
        if order:
            order.payment_status = "refunded"
            order.status = "refunded"
    
    await db.commit()
    
    return {"message": f"Refund request {process_data.decision} successfully"}


@router.get("/disputes")
async def get_disputes(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only customer service can access disputes"
        )
    
    result = await db.execute(
        select(Dispute)
        .offset(skip)
        .limit(limit)
        .order_by(Dispute.created_at.desc())
    )
    disputes = result.scalars().all()
    
    return {"disputes": disputes}


@router.get("/disputes/{dispute_id}")
async def get_dispute(
    dispute_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only customer service can access disputes"
        )
    
    result = await db.execute(select(Dispute).where(Dispute.id == dispute_id))
    dispute = result.scalar_one_or_none()
    
    if not dispute:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dispute not found"
        )
    
    return dispute


@router.post("/disputes/{dispute_id}/resolve")
async def resolve_dispute(
    dispute_id: str,
    resolve_data: ResolveDisputeRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only customer service can resolve disputes"
        )
    
    result = await db.execute(select(Dispute).where(Dispute.id == dispute_id))
    dispute = result.scalar_one_or_none()
    
    if not dispute:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dispute not found"
        )
    
    if dispute.status != "open":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Dispute has already been resolved"
        )
    
    # Update dispute status and resolution
    dispute.status = "resolved"
    dispute.resolution = {
        "decision": resolve_data.decision,
        "amount_to_client": resolve_data.amount_to_client,
        "amount_to_ai": resolve_data.amount_to_ai,
        "notes": resolve_data.notes
    }
    
    # Update order status based on resolution
    order_result = await db.execute(select(Order).where(Order.id == dispute.order_id))
    order = order_result.scalar_one_or_none()
    if order:
        if resolve_data.decision == "refund_client":
            order.status = "refunded"
            order.payment_status = "refunded"
        elif resolve_data.decision == "release_to_ai":
            order.status = "completed"
            order.completed_at = datetime.utcnow()
    
    await db.commit()
    
    return {"message": "Dispute resolved successfully"}
