from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, validator
import uuid
from sqlalchemy import DateTime


# User schemas
class UserBase(BaseModel):
    username: str
    email: Optional[EmailStr] = None
    role: str


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    
    @validator('username')
    def username_min_length(cls, v):
        if len(v) < 4:
            raise ValueError('Username must be at least 4 characters long')
        return v
    
    @validator('password')
    def password_min_length(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v


class UserResponse(BaseModel):
    id: str
    username: str
    email: Optional[str] = None
    role: str
    balance: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# Agent schemas
class AgentCreate(BaseModel):
    name: str
    description: str
    
    @validator('name')
    def name_min_length(cls, v):
        if len(v) < 4:
            raise ValueError('Name must be at least 4 characters long')
        return v


class AgentResponse(BaseModel):
    id: str
    username: str
    api_key: str
    description: str
    
    class Config:
        from_attributes = True


# Auth schemas
class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    success:bool
    user: UserResponse


# Task schemas
class TaskBase(BaseModel):
    title: str
    description: str
    budget: str
    deadline: datetime
    category: str
    attachments: Optional[List[str]] = None


class TaskCreate(TaskBase):
    pass


class TaskResponse(TaskBase):
    id: str
    status: str
    client_id: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# Bid schemas
class BidBase(BaseModel):
    amount: str
    estimated_days: int
    message: str


class BidCreate(BidBase):
    pass


class BidResponse(BidBase):
    id: str
    task_id: str
    ai_id: str
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# Order schemas
class OrderResponse(BaseModel):
    id: str
    task_id: str
    client_id: str
    ai_id: str
    amount: str
    status: str
    deadline: datetime
    payment_status: str
    paid_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# Message schemas
class MessageBase(BaseModel):
    content: str
    file_url: Optional[str] = None


class MessageCreate(MessageBase):
    pass


class MessageResponse(MessageBase):
    id: str
    order_id: str
    sender_id: str
    sender_type: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# AI Heartbeat schemas
class AiHeartbeatRequest(BaseModel):
    status: str  # "online", "busy", "offline"
    current_load: int


# Refund Request schemas
class ProcessRefundRequest(BaseModel):
    decision: str  # "approved" or "rejected"
    notes: Optional[str] = None
    
    @validator('decision')
    def validate_decision(cls, v):
        if v not in ["approved", "rejected"]:
            raise ValueError('Decision must be either "approved" or "rejected"')
        return v


# Dispute schemas
class ResolveDisputeRequest(BaseModel):
    decision: str  # "refund_client", "release_to_ai", "partial_refund"
    amount_to_client: Optional[str] = None
    amount_to_ai: Optional[str] = None
    notes: Optional[str] = None
    
    @validator('decision')
    def validate_decision(cls, v):
        if v not in ["refund_client", "release_to_ai", "partial_refund"]:
            raise ValueError('Decision must be one of: "refund_client", "release_to_ai", "partial_refund"')
        return v
    
    @validator('amount_to_client', 'amount_to_ai')
    def validate_amounts(cls, v, values):
        if values.get('decision') == 'partial_refund' and not v:
            raise ValueError('Amount fields are required for partial refund decisions')
        return v
