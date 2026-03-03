from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..database import get_db
from ..models.user import User
from ..schemas import UserCreate, AgentCreate, LoginRequest, UserResponse, AgentResponse, LoginResponse
from ..auth import hash_password, verify_password, create_jwt_token
import uuid

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register", response_model=dict)
async def register_client(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    # Check if user already exists
    result = await db.execute(select(User).where(User.email == user_data.email))
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = hash_password(user_data.password)
    new_user = User(
        id=str(uuid.uuid4()),
        username=user_data.username,
        email=user_data.email,
        password_hash=hashed_password,
        role="client"
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    return {
        "success": True,
        "user": {
            "id": new_user.id,
            "username": new_user.username,
            "email": new_user.email,
            "role": new_user.role,
            "created_at": new_user.created_at
        },
        "message": "注册成功！"
    }


@router.post("/register/agent", response_model=dict)
async def register_agent(
    agent_data: AgentCreate,
    db: AsyncSession = Depends(get_db)
):
    # Create new AI agent
    agent_id = str(uuid.uuid4())
    api_key = f"om_{uuid.uuid4().hex}"
    
    new_agent = User(
        id=agent_id,
        username=agent_data.name,
        api_key=api_key,
        role="ai",
        description=agent_data.description
    )
    
    db.add(new_agent)
    await db.commit()
    await db.refresh(new_agent)
    
    return {
        "success": True,
        "agent": {
            "id": new_agent.id,
            "name": new_agent.username,
            "api_key": api_key
        },
        "message": "注册成功！请立即保存你的 API Key。"
    }


@router.post("/login", response_model=LoginResponse)
async def login(
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    # Find user by email
    result = await db.execute(select(User).where(User.email == login_data.email))
    user = result.scalar_one_or_none()
    
    if not user or not user.password_hash:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Verify password
    if not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Create JWT token
    token_data = {"sub": user.id, "username": user.username, "role": user.role}
    access_token = create_jwt_token(token_data)
    
    return LoginResponse(
        access_token=access_token,
        token_type="Bearer",
        user=UserResponse.from_orm(user)
    )
