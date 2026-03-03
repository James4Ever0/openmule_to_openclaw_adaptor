from fastapi import WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Dict, Any
import json
import asyncio
from ..database import get_db
from ..models.user import User
from ..models.order import Order
from ..auth import verify_jwt_token
from .connection_manager import manager


async def get_current_user_ws(websocket: WebSocket, token: str, db: AsyncSession) -> User:
    try:
        payload = verify_jwt_token(token)
        if payload is None:
            return None
        
        user_id = payload.get("sub")
        if user_id is None:
            return None
        
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        
        return user
    except:
        return None


async def websocket_endpoint(websocket: WebSocket, token: str = None, db: AsyncSession = Depends(get_db)):
    await websocket.accept()
    
    if not token:
        await websocket.send_text(json.dumps({
            "type": "error",
            "message": "Authentication token required"
        }))
        await websocket.close()
        return
    
    current_user = await get_current_user_ws(websocket, token, db)
    if not current_user:
        await websocket.send_text(json.dumps({
            "type": "error", 
            "message": "Invalid authentication token"
        }))
        await websocket.close()
        return
    
    # Connect user
    await manager.connect(websocket, current_user.id)
    
    try:
        await websocket.send_text(json.dumps({
            "type": "connection",
            "message": "Connected successfully",
            "user_id": current_user.id
        }))
        
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            message_type = message_data.get("type")
            
            if message_type == "join_order":
                order_id = message_data.get("order_id")
                if order_id:
                    # Verify user has access to this order
                    result = await db.execute(select(Order).where(Order.id == order_id))
                    order = result.scalar_one_or_none()
                    
                    if order and (order.client_id == current_user.id or order.ai_id == current_user.id):
                        await manager.join_order(current_user.id, order_id)
                        await websocket.send_text(json.dumps({
                            "type": "joined_order",
                            "order_id": order_id
                        }))
                    else:
                        await websocket.send_text(json.dumps({
                            "type": "error",
                            "message": "Access denied to order"
                        }))
            
            elif message_type == "leave_order":
                order_id = message_data.get("order_id")
                if order_id:
                    await manager.leave_order(current_user.id, order_id)
                    await websocket.send_text(json.dumps({
                        "type": "left_order",
                        "order_id": order_id
                    }))
            
            elif message_type == "ping":
                await websocket.send_text(json.dumps({
                    "type": "pong",
                    "timestamp": message_data.get("timestamp")
                }))
            
            else:
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": f"Unknown message type: {message_type}"
                }))
                
    except WebSocketDisconnect:
        manager.disconnect(current_user.id)
    except Exception as e:
        await websocket.send_text(json.dumps({
            "type": "error",
            "message": str(e)
        }))
        manager.disconnect(current_user.id)


# Helper functions for broadcasting
async def broadcast_new_message(message_data: dict, order_id: str):
    """Broadcast new message to all users in an order"""
    await manager.broadcast_to_order({
        "type": "new_message",
        "order_id": order_id,
        "message": message_data
    }, order_id)


async def broadcast_order_update(order_data: dict, order_id: str):
    """Broadcast order status update to all users in an order"""
    await manager.broadcast_to_order({
        "type": "order_update",
        "order_id": order_id,
        "order": order_data
    }, order_id)


async def broadcast_bid_update(bid_data: dict, task_id: str):
    """Broadcast bid update to task owner"""
    # This would require finding the task owner and sending them a message
    # Implementation depends on your specific requirements
    pass
