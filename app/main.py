from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from mysql.connector import connect

import json
import asyncio

from typing import List

app = FastAPI()

# Cors configuration
origins = ['*']

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket manager class
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)
            
manager = ConnectionManager()

# Home
@app.get('/')
def home():
    return {'Welcome to the api'}

 
@app.websocket('/ws/poly')
async def polydesignWS(websocket: WebSocket):
    await manager.connect(websocket)
    await websocket.receive_text()
    
    while True:
        try:
            result = traitement()
            if result != '[]':
                await manager.broadcast(json.dumps(result))
            
        except WebSocketDisconnect:
            manager.disconnect(websocket)
            break
        await asyncio.sleep(3)   
  

def traitement():
    
    cnx = connect(
                user='root', 
                password='',
                host='127.0.0.1',
                database='test'
                )
    cursor = cnx.cursor()
    
    # Get last saved id
    f = open ('./app/data/last_id.txt', 'r')
    id = int(f.read())
    
    # Query
    query = ("SELECT id, code FROM test "
            "WHERE id > %s "
            "ORDER BY id")
    
    # Execute query
    cursor.execute(query, [id])
    result = cursor.fetchall()
    
    # Write the new id in file
    if len(result) != 0:
        with open('./app/data/last_id.txt', 'w') as f:
            f.write(str(result[-1][0]))
    return json.dumps(result)
