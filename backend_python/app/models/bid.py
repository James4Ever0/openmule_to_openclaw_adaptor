from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from .base import BaseModel


class Bid(BaseModel):
    __tablename__ = "bids"
    
    task_id = Column(String, ForeignKey("tasks.id"), nullable=False)
    ai_id = Column(String, ForeignKey("users.id"), nullable=False)
    amount = Column(String, nullable=False)
    estimated_days = Column(Integer, nullable=False)
    message = Column(String, nullable=False)
    status = Column(String, nullable=False)  # "pending", "accepted", "rejected"
    
    # Relationships
    task = relationship("Task", back_populates="bids")
    ai = relationship("User", back_populates="bids")
