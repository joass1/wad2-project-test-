from enum import Enum

class AnimationStates(Enum):
    """Animation states for the pet"""
    IDLE = "idle"
    WALK_LEFT = "walk_left"
    WALK_RIGHT = "walk_right"
    SLEEP = "sleep"
    GRABBED = "grabbed"
    FALLING = "falling"
    LANDED = "landed"
