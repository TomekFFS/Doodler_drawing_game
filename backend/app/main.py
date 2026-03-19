from fastapi import FastAPI, WebSocket
import json

class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[int, WebSocket] = {}

    async def connect(self, client_id: int, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[client_id] = websocket


app = FastAPI()

@app.get("/")
def read_root():
    return {"status":"ok"}