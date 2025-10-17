from fastapi import APIRouter
from fastapi_socketio import SocketManager
import asyncio
from app.core.pet_engine.pet_state import PetState

router = APIRouter()

# This will be initialized in main.py
socket_manager = None
pet_state = PetState()

async def broadcast_pet_state():
    """Continuously broadcast pet state updates"""
    while True:
        pet_state.update_position(dt=0.1)
        await socket_manager.emit('pet_update', pet_state.to_dict())
        await asyncio.sleep(0.1)  # 10 updates per second

@router.on('connect')
async def handle_connect(sid, environ):
    print(f'Client connected: {sid}')
    await socket_manager.emit('pet_state', pet_state.to_dict(), room=sid)

@router.on('move_pet')
async def handle_move_pet(sid, data):
    pet_state.set_position(data['x'], data['y'])
    await socket_manager.emit('pet_update', pet_state.to_dict(), broadcast=True)

@router.on('grab_pet')
async def handle_grab(sid, data):
    pet_state.set_grabbed(data['grabbed'])
    await socket_manager.emit('pet_update', pet_state.to_dict(), broadcast=True)
