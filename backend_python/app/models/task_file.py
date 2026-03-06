from sqlalchemy import Column, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from .base import BaseModel


class TaskFile(BaseModel):
    __tablename__ = "task_files"
    
    task_id = Column(String, ForeignKey("tasks.id"), nullable=False)
    file_id = Column(String, ForeignKey("uploaded_files.id"), nullable=False)
    
    # Relationships
    task = relationship("Task", back_populates="task_files")
    file = relationship("UploadedFile", back_populates="task_files")
