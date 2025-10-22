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
    """Get sprite sheet configuration with customizable sprite extraction"""
    return {
        "sprite_sheet": {
            "url": "/cat-spritesheet.png",
            "slice": 32,  # Size of one sprite cell
            "scale": 3,   # Display scale multiplier
            "columns": 12  # Auto-detected on frontend
        },
        "animations": {
            # Format: { row, frames, fps, loop, colStart }
            # You can customize these to extract different sprites from the sheet
            "idle":     {"row": 0, "frames": 8, "fps": 6,  "loop": True,  "colStart": 0},
            "idle2":    {"row": 1, "frames": 8, "fps": 6,  "loop": True,  "colStart": 0},
            "clean":    {"row": 2, "frames": 8, "fps": 8,  "loop": True,  "colStart": 0},
            "clean2":   {"row": 3, "frames": 8, "fps": 8,  "loop": True,  "colStart": 0},
            "walk":     {"row": 4, "frames": 8, "fps": 10, "loop": True,  "colStart": 0},
            "walk2":    {"row": 5, "frames": 8, "fps": 10, "loop": True,  "colStart": 0},
            "walk_left":  {"row": 4, "frames": 8, "fps": 10, "loop": True,  "colStart": 0},
            "walk_right": {"row": 5, "frames": 8, "fps": 10, "loop": True,  "colStart": 0},
            "sleep":    {"row": 6, "frames": 6, "fps": 5,  "loop": True,  "colStart": 0},
            "grabbed":  {"row": 7, "frames": 6, "fps": 8,  "loop": True,  "colStart": 0},
            "jump":     {"row": 8, "frames": 8, "fps": 12, "loop": False, "colStart": 0},
            "falling":  {"row": 9, "frames": 8, "fps": 12, "loop": True,  "colStart": 0},
            "scared":   {"row": 9, "frames": 8, "fps": 10, "loop": False, "colStart": 0},
            "idle_to_sleep": {"row": 6, "frames": 3, "fps": 5, "loop": False, "colStart": 0},
            "sleep_to_idle": {"row": 6, "frames": 3, "fps": 5, "loop": False, "colStart": 3}
        },
        "physics": {
            "gravity": 0.8,
            "terminal_velocity": 15,
            "drag_coefficient": 0.95,
            "walk_speed": 2
        }
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
