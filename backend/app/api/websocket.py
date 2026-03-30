from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.core.websocket import manager
import json

router = APIRouter()


@router.websocket("/ws/jobs/{job_id}")
async def websocket_endpoint(websocket: WebSocket, job_id: str):
    """WebSocket端点用于接收任务进度更新"""
    await manager.connect(websocket, job_id)
    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                if message.get("type") == "ping":
                    await websocket.send_json({"type": "pong"})
            except:
                pass
    except WebSocketDisconnect:
        manager.disconnect(websocket, job_id)
