from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware

from mysql.connector import connect

import json
import asyncio

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
    
# Query
query = ("SELECT id, code FROM test "
         "WHERE id > %s "
         "ORDER BY id")

# Home
@app.get('/')
def home():
    return {'Welcome to the api'}

 
@app.websocket('/ws/poly')
async def polydesignWS(websocket: WebSocket):
    await websocket.accept()
    await websocket.receive_text()
    
    while True:
        try:
            result = traitement()
            if result != '[]':
                await websocket.send_json(result)
            
        except Exception as e:
            print('error:', e)
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
    
    # Execute query
    cursor.execute(query, [id])
    result = cursor.fetchall()
    
    # Write the new id in file
    if len(result) != 0:
        with open('./app/data/last_id.txt', 'w') as f:
            f.write(str(result[-1][0]))
    return json.dumps(result)