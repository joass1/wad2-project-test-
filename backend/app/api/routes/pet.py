from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict
import os

router = APIRouter(prefix="/pet", tags=["pet"])

from app.core.pet_engine.pet_state import PetState
pet_state = PetState()

class PetConfig(BaseModel):
    canvas_width: int
    canvas_height: int

class Position(BaseModel):
    x: float
    y: float

@router.get("/config")
async def get_pet_config():
    """Get available animations and sprite paths"""
    return {
        "animations": {
            "idle": "/static/sprites/cat/idle.gif",
            "walk_left": "/static/sprites/cat/walking_negative.gif",
            "walk_right": "/static/sprites/cat/walking_positive.gif",
            "sleep": "/static/sprites/cat/sleep.gif",
            "idle_to_sleep": "/static/sprites/cat/idle_to_sleep.gif",
            "sleep_to_idle": "/static/sprites/cat/sleep_to_idle.gif",
            "falling": "/static/sprites/cat/walking_negative.gif",
            "grabbed": "/static/sprites/cat/idle.gif"  
        },
        "default_size": {"width": 100, "height": 100},
        "frame_rate": 100
    }

@router.get("/state")
async def get_pet_state():
    """Get current pet state"""
    pet_state.update_position()
    return pet_state.to_dict()

@router.post("/position")
async def update_position(position: Position):
    """Update pet position (for dragging)"""
    pet_state.set_position(position.x, position.y)
    return pet_state.to_dict()

@router.post("/grab")
async def grab_pet(grabbed: bool):
    """Handle grab/release"""
    pet_state.set_grabbed(grabbed)
    return pet_state.to_dict()

@router.post("/init")
async def initialize_pet(config: PetConfig):
    """Initialize pet with canvas dimensions"""
    global pet_state
    pet_state = PetState(config.canvas_width, config.canvas_height)
    return {"status": "initialized"}
