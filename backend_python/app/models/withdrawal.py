from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship
from .base import BaseModel


class Withdrawal(BaseModel):
    __tablename__ = "withdrawals"
    
    ai_id = Column(String, ForeignKey("users.id"), nullable=False)
    order_id = Column(String, ForeignKey("orders.id"), nullable=False)
    amount = Column(String, nullable=False)
    wallet_address = Column(String, nullable=False)
    status = Column(String, nullable=False)  # "processing", "completed", "failed"
    
    # Relationships
    ai = relationship("User", back_populates="withdrawals")
    order = relationship("Order", back_populates="withdrawals")
