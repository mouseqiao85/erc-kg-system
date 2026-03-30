from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List
import json
import asyncio


class ConnectionManager:
    """WebSocket连接管理器"""
    
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, job_id: str):
        await websocket.accept()
        if job_id not in self.active_connections:
            self.active_connections[job_id] = []
        self.active_connections[job_id].append(websocket)
    
    def disconnect(self, websocket: WebSocket, job_id: str):
        if job_id in self.active_connections:
            if websocket in self.active_connections[job_id]:
                self.active_connections[job_id].remove(websocket)
            if not self.active_connections[job_id]:
                del self.active_connections[job_id]
    
    async def send_progress(self, job_id: str, progress: int, message: str, data: dict = None):
        if job_id in self.active_connections:
            payload = {
                "type": "progress",
                "job_id": job_id,
                "progress": progress,
                "message": message,
                "data": data or {}
            }
            for connection in self.active_connections[job_id]:
                try:
                    await connection.send_json(payload)
                except:
                    pass
    
    async def send_complete(self, job_id: str, result: dict):
        if job_id in self.active_connections:
            payload = {
                "type": "complete",
                "job_id": job_id,
                "result": result
            }
            for connection in self.active_connections[job_id]:
                try:
                    await connection.send_json(payload)
                except:
                    pass
    
    async def send_error(self, job_id: str, error: str):
        if job_id in self.active_connections:
            payload = {
                "type": "error",
                "job_id": job_id,
                "error": error
            }
            for connection in self.active_connections[job_id]:
                try:
                    await connection.send_json(payload)
                except:
                    pass


manager = ConnectionManager()
