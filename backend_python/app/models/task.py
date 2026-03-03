from sqlalchemy import Column, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from .base import BaseModel


class Task(BaseModel):
    __tablename__ = "tasks"
    
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    budget = Column(String, nullable=False)  # USDT amount as string to avoid floating point issues
    deadline = Column(DateTime(timezone=True), nullable=False)
    status = Column(String, nullable=False)  # "open", "assigned", "completed", "cancelled"
    category = Column(String, nullable=False)
    attachments = Column(JSON, nullable=True)  # JSON array of URLs
    client_id = Column(String, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    client = relationship("User", back_populates="tasks")
    bids = relationship("Bid", back_populates="task")
    orders = relationship("Order", back_populates="task")
