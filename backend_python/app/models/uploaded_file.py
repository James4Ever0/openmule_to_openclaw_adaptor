from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from .base import BaseModel


class UploadedFile(BaseModel):
    __tablename__ = "uploaded_files"
    
    filename = Column(String, nullable=False)  # Original filename
    file_path = Column(String, nullable=False)  # Storage path on server
    file_url = Column(String, nullable=False)   # Public URL for accessing the file
    file_size = Column(String, nullable=False)  # File size in bytes
    mime_type = Column(String, nullable=False)  # MIME type of the file
    comment = Column(Text, nullable=True)       # Optional comment for the file
    uploaded_by = Column(String, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    uploader = relationship("User", back_populates="uploaded_files")
    task_files = relationship("TaskFile", back_populates="file", cascade="all, delete-orphan")
