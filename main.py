from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

app.mount("/static", StaticFiles(directory = "static"), name = "static")

@app.get("/")
def main():
    # Robust — always resolves relative to main.py
    BASE_DIR = Path(__file__).parent
    return FileResponse(BASE_DIR / "static" / "index.html")

class WebSocketEvent(BaseModel):
    type: str  # Expected to be "chat" or "system"
    message: str
    user_id: Optional[str] = None
    active_users: Optional[int] = None

class ConnectionManager:
    def __init__(self):
        self.active_connections = []
    
    async def connect(self, websocket: WebSocket): 
        await websocket.accept() # awaiting for the handshake "allowed connection to the websocket"
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket) #removing the user from the user's list

    async def broadcast(self, event: WebSocketEvent, exclude: WebSocket = None):
        for connection in self.active_connections:
            if connection != exclude:
                await connection.send_json(event.model_dump())
    
    def get_users(self):
        return self.active_connections


manager = ConnectionManager() # the websocket connection manager
#to which we will be referring to in our routes

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await manager.connect(websocket)
    
    #calculate the current users
    user_count = len(manager.active_connections)

    #create the joining event
    join_event = WebSocketEvent(
        type= "system", 
        message= f"User#{client_id}, has joined", 
        active_users= user_count
    )

    #broadcast it 
    await manager.broadcast(join_event)

    #the message handling 
    try:
        while True:
            data = await websocket.receive_text()

            chat_event = WebSocketEvent(
                type="chat",
                message= data,
                user_id= str(client_id)
            )
            await manager.broadcast(chat_event)

    except WebSocketDisconnect:
        manager.disconnect(websocket)

        #calculate the current users
        user_count = len(manager.active_connections)

        #create the leaving event
        leave_event = WebSocketEvent(
            type= "system", 
            message= f"User#{client_id}, has disconnected", 
            active_users= user_count
        )

        #broadcast it
        await manager.broadcast(leave_event)