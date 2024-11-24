from fastapi import WebSocket
from typing import Dict, List
import json

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, workflow_id: str):
        await websocket.accept()
        if workflow_id not in self.active_connections:
            self.active_connections[workflow_id] = []
        self.active_connections[workflow_id].append(websocket)

    async def disconnect(self, websocket: WebSocket, workflow_id: str):
        if workflow_id in self.active_connections:
            self.active_connections[workflow_id].remove(websocket)

    async def send_update(self, workflow_id: str, data: dict):
        if workflow_id in self.active_connections:
            for connection in self.active_connections[workflow_id]:
                await connection.send_json(data)

manager = ConnectionManager()
