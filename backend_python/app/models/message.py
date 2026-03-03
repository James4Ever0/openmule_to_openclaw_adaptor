from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship
from .base import BaseModel


class Message(BaseModel):
    __tablename__ = "messages"
    
    order_id = Column(String, ForeignKey("orders.id"), nullable=False)
    sender_id = Column(String, ForeignKey("users.id"), nullable=False)
    sender_type = Column(String, nullable=False)  # "client" or "ai"
    content = Column(String, nullable=False)
    file_url = Column(String, nullable=True)
    
    # Relationships
    order = relationship("Order", back_populates="messages")
    sender = relationship("User", back_populates="sent_messages")
