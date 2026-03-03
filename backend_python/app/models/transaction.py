from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship
from .base import BaseModel


class Transaction(BaseModel):
    __tablename__ = "transactions"
    
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    order_id = Column(String, ForeignKey("orders.id"), nullable=True)
    amount = Column(String, nullable=False)
    transaction_type = Column(String, nullable=False)  # "income", "withdrawal"
    status = Column(String, nullable=False)  # "pending", "completed", "failed"
    
    # Relationships
    user = relationship("User", back_populates="transactions")
    order = relationship("Order")
