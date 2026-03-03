from sqlalchemy import Column, String, ForeignKey, JSON
from sqlalchemy.orm import relationship
from .base import BaseModel


class RefundRequest(BaseModel):
    __tablename__ = "refund_requests"
    
    order_id = Column(String, ForeignKey("orders.id"), nullable=False)
    client_id = Column(String, ForeignKey("users.id"), nullable=False)
    ai_id = Column(String, ForeignKey("users.id"), nullable=False)
    reason = Column(String, nullable=False)
    evidence = Column(JSON, nullable=True)  # JSON array of URLs
    status = Column(String, nullable=False)  # "pending", "approved", "rejected"
    
    # Relationships
    order = relationship("Order", back_populates="refund_requests")
    client = relationship("User", back_populates="refund_requests")
