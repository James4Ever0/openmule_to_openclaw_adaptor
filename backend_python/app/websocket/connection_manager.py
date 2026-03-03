from typing import Dict, List
from fastapi import WebSocket
import json
import asyncio


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.order_connections: Dict[str, List[str]] = {}  # order_id -> list of user_ids

    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: str):
        if user_id in self.active_connections:
            del self.active_connections[user_id]
        
        # Remove user from order connections
        for order_id in list(self.order_connections.keys()):
            if user_id in self.order_connections[order_id]:
                self.order_connections[order_id].remove(user_id)
                if not self.order_connections[order_id]:
                    del self.order_connections[order_id]

    async def join_order(self, user_id: str, order_id: str):
        if order_id not in self.order_connections:
            self.order_connections[order_id] = []
        if user_id not in self.order_connections[order_id]:
            self.order_connections[order_id].append(user_id)

    async def leave_order(self, user_id: str, order_id: str):
        if order_id in self.order_connections and user_id in self.order_connections[order_id]:
            self.order_connections[order_id].remove(user_id)
            if not self.order_connections[order_id]:
                del self.order_connections[order_id]

    async def send_personal_message(self, message: dict, user_id: str):
        if user_id in self.active_connections:
            websocket = self.active_connections[user_id]
            await websocket.send_text(json.dumps(message))

    async def broadcast_to_order(self, message: dict, order_id: str):
        if order_id in self.order_connections:
            disconnected_users = []
            for user_id in self.order_connections[order_id]:
                if user_id in self.active_connections:
                    websocket = self.active_connections[user_id]
                    try:
                        await websocket.send_text(json.dumps(message))
                    except:
                        disconnected_users.append(user_id)
                else:
                    disconnected_users.append(user_id)
            
            # Clean up disconnected users
            for user_id in disconnected_users:
                if user_id in self.order_connections[order_id]:
                    self.order_connections[order_id].remove(user_id)
                if user_id in self.active_connections:
                    del self.active_connections[user_id]

    async def broadcast(self, message: dict):
        disconnected_users = []
        for user_id, websocket in self.active_connections.items():
            try:
                await websocket.send_text(json.dumps(message))
            except:
                disconnected_users.append(user_id)
        
        # Clean up disconnected users
        for user_id in disconnected_users:
            self.disconnect(user_id)


manager = ConnectionManager()
