from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .base import BaseModel


class Order(BaseModel):
    __tablename__ = "orders"
    
    task_id = Column(String, ForeignKey("tasks.id"), nullable=False)
    client_id = Column(String, ForeignKey("users.id"), nullable=False)
    ai_id = Column(String, ForeignKey("users.id"), nullable=False)
    amount = Column(String, nullable=False)
    status = Column(String, nullable=False)  # "pending_payment", "assigned", "delivered", "completed", "disputed", "refunded", "cancelled"
    deadline = Column(DateTime(timezone=True), nullable=False)
    payment_status = Column(String, nullable=False)  # "unpaid", "paid", "refunded"
    paid_at = Column(DateTime(timezone=True), nullable=True)
    delivered_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    task = relationship("Task", back_populates="orders")
    client = relationship("User", foreign_keys=[client_id], back_populates="orders_as_client")
    ai = relationship("User", foreign_keys=[ai_id], back_populates="orders_as_ai")
    messages = relationship("Message", back_populates="order")
    deliverables = relationship("Deliverable", back_populates="order")
    refund_requests = relationship("RefundRequest", back_populates="order")
    disputes = relationship("Dispute", back_populates="order")
    withdrawals = relationship("Withdrawal", back_populates="order")
