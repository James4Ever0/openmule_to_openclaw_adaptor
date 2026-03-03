from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from .base import BaseModel


class User(BaseModel):
    __tablename__ = "users"
    
    username = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=True)
    password_hash = Column(String, nullable=True)
    api_key = Column(String, unique=True, nullable=True)
    role = Column(String, nullable=False)  # "client" or "ai"
    balance = Column(String, nullable=True)  # Only for AI agents
    description = Column(String, nullable=True)  # Only for AI agents
    
    # Relationships
    tasks = relationship("Task", back_populates="client")
    bids = relationship("Bid", back_populates="ai")
    orders_as_client = relationship("Order", foreign_keys="Order.client_id", back_populates="client")
    orders_as_ai = relationship("Order", foreign_keys="Order.ai_id", back_populates="ai")
    sent_messages = relationship("Message", back_populates="sender")
    refund_requests = relationship("RefundRequest", back_populates="client")
    disputes = relationship("Dispute", back_populates="client")
    withdrawals = relationship("Withdrawal", back_populates="ai")
    transactions = relationship("Transaction", back_populates="user")
