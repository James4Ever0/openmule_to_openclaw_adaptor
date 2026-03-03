from sqlalchemy import Column, String, ForeignKey, JSON
from sqlalchemy.orm import relationship
from .base import BaseModel


class Dispute(BaseModel):
    __tablename__ = "disputes"
    
    order_id = Column(String, ForeignKey("orders.id"), nullable=False)
    client_id = Column(String, ForeignKey("users.id"), nullable=False)
    ai_id = Column(String, ForeignKey("users.id"), nullable=False)
    reason = Column(String, nullable=False)
    details = Column(String, nullable=False)
    status = Column(String, nullable=False)  # "open", "resolved"
    resolution = Column(JSON, nullable=True)  # JSON object with resolution details
    
    # Relationships
    order = relationship("Order", back_populates="disputes")
    client = relationship("User", back_populates="disputes")
