from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship
from .base import BaseModel


class Deliverable(BaseModel):
    __tablename__ = "deliverables"
    
    order_id = Column(String, ForeignKey("orders.id"), nullable=False)
    file_url = Column(String, nullable=False)
    description = Column(String, nullable=False)
    
    # Relationships
    order = relationship("Order", back_populates="deliverables")
