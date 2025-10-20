from typing import Dict
import random
from datetime import datetime
import time

class PetState:
    """Manages the pet's state with physics similar to InteractablePet"""
    
    def __init__(self, canvas_width: int = 800, canvas_height: int = 600):
        # Position
        self.x: float = 100
        self.y: float = canvas_height - 100
        
        # Physics (velocity and acceleration)
        self.v_x: float = 0
        self.v_y: float = 0
        self.a_x: float = 0
        self.a_y: float = 0
        
        # State
        self.current_animation: str = "idle"
        self.frame_index: int = 0
        self.is_grabbed: bool = False
        
        self.canvas_width = canvas_width
        self.canvas_height = canvas_height
        self.pet_size = 100  # Default pet size
        
        # Roaming behavior
        self.is_roaming = False
        self.roam_target_x = None
        self.roam_timer = 0
        self.roam_cooldown = random.randint(3, 8)
        
        # Sleep behavior
        self.is_sleeping = False
        self.sleep_timer = 0
        self.sleep_duration = 0
        
        # Animation transition
        self.transition_start_time = None
        self.transition_duration = 1.0
        
        self.last_update = datetime.now()
    
    def reset_movement(self):
        """Reset movement based on current animation"""
        # Set velocity and acceleration based on animation state
        if self.current_animation in ["walk_left", "walk"]:
            self.v_x = -2
            self.v_y = 0
            self.a_x = 0
            self.a_y = 0
        elif self.current_animation in ["walk_right", "walk2"]:
            self.v_x = 2
            self.v_y = 0
            self.a_x = 0
            self.a_y = 0
        elif self.current_animation == "falling":
            self.v_x = 0
            self.a_x = 0
            self.a_y = 0.8  # Gravity acceleration (slower fall)
        elif self.current_animation in ["idle", "idle2", "sleep", "grabbed", "clean", "clean2"]:
            self.v_x = 0
            self.v_y = 0
            self.a_x = 0
            self.a_y = 0
    
    def do_movement(self):
        """Apply physics and keep pet on screen (like InteractablePet.do_movement)"""
        # Update velocity based on acceleration
        self.v_x += self.a_x
        self.v_y += self.a_y
        
        # Update position based on velocity
        self.x += self.v_x
        self.y += self.v_y
        
        # Keep x position on screen (wrap around)
        if self.x < 0:
            self.x = 0
        if self.x > self.canvas_width - self.pet_size:
            self.x = self.canvas_width - self.pet_size
        
        # Handle y position - floor collision and falling
        floor_level = self.canvas_height - self.pet_size
        
        if self.y > floor_level:
            # Hit the floor
            self.y = floor_level
            self.v_y = 0
            
            # Transition from falling to landed/idle
            if self.current_animation == "falling":
                self.current_animation = "idle"
                self.a_y = 0
                self.reset_movement()
    
    def update_position(self, dt: float = 0.1):
        """Main update loop (combines update() and on_tick() logic)"""
        
        # Don't update if grabbed (like InteractablePet event handlers)
        if self.is_grabbed:
            return
        
        # Handle animation transitions
        if self.transition_start_time:
            elapsed = time.time() - self.transition_start_time
            if elapsed >= self.transition_duration:
                self.finish_transition()
            return
        
        # Handle sleeping
        if self.is_sleeping:
            self.sleep_timer += dt
            if self.sleep_timer >= self.sleep_duration:
                self.wake_up()
            return
        
        # Apply movement physics
        self.do_movement()
        
        # Check if falling (above ground and not in transition)
        floor_level = self.canvas_height - self.pet_size
        if self.y < floor_level and self.current_animation not in ["falling", "sleep", "idle_to_sleep", "sleep_to_idle"]:
            # Start falling if above ground
            if not self.is_roaming:
                self.current_animation = "falling"
                self.reset_movement()
        
        # Normal roaming behavior (only when on ground)
        if self.y >= floor_level and not self.is_roaming and self.current_animation not in ["sleep", "idle_to_sleep", "sleep_to_idle", "falling"]:
            self.roam_timer += dt
            
            if self.roam_timer >= self.roam_cooldown:
                self.start_roaming()
        
        # Update roaming movement
        if self.is_roaming:
            self.update_roaming(dt)
    
    def start_roaming(self):
        """Start walking to a random location with sprite animations"""
        self.roam_target_x = random.randint(100, self.canvas_width - 100)
        self.is_roaming = True

        # Set animation and velocity based on direction
        # Use walk (row 4) or walk2 (row 5) animations
        if self.roam_target_x > self.x:
            self.current_animation = random.choice(["walk_right", "walk2"])
        else:
            self.current_animation = random.choice(["walk_left", "walk"])

        self.reset_movement()
    
    def update_roaming(self, dt: float):
        """Continue roaming movement"""
        # Check if reached target
        if abs(self.x - self.roam_target_x) < 10:
            self.is_roaming = False
            self.v_x = 0
            # Randomly choose idle animation (idle, idle2, or clean)
            self.current_animation = random.choice(["idle", "idle2", "clean", "clean2"])
            self.reset_movement()
            self.roam_timer = 0
            self.roam_cooldown = random.randint(3, 8)

            # 30% chance to sleep after walking
            if random.random() < 0.3:
                self.go_to_sleep()
    
    def go_to_sleep(self):
        """Transition to sleep"""
        self.current_animation = "idle_to_sleep"
        self.transition_start_time = time.time()
        self.transition_duration = 1.0
    
    def finish_transition(self):
        """Complete animation transition"""
        if self.current_animation == "idle_to_sleep":
            self.current_animation = "sleep"
            self.is_sleeping = True
            self.sleep_duration = random.randint(5, 10)
            self.sleep_timer = 0
        elif self.current_animation == "sleep_to_idle":
            self.current_animation = "idle"
        
        self.transition_start_time = None
        self.reset_movement()
    
    def wake_up(self):
        """Wake up from sleep"""
        self.is_sleeping = False
        self.current_animation = "sleep_to_idle"
        self.transition_start_time = time.time()
        self.transition_duration = 1.0
    
    def set_grabbed(self, grabbed: bool):
        """Handle grab/release with sprite-based animations"""
        self.is_grabbed = grabbed

        if grabbed:
            # Use grabbed sprite animation (paw animation - row 7)
            self.current_animation = "grabbed"
            self.is_roaming = False
            self.is_sleeping = False
            self.transition_start_time = None

            # Stop all movement
            self.v_x = 0
            self.v_y = 0
            self.a_x = 0
            self.a_y = 0
        else:
            # stop_move event - check if should fall
            floor_level = self.canvas_height - self.pet_size

            if self.y < floor_level:
                # Pet is above ground, start falling with scared animation (row 9)
                self.current_animation = "falling"
                self.v_y = 0  # Start with zero velocity
                self.a_y = 0.8  # Slower gravity for gentle fall
            else:
                # On ground, return to idle
                self.current_animation = "idle"
                self.reset_movement()
    
    def set_position(self, x: float, y: float):
        """Set position directly (like InteractablePet.do_move)"""
        self.x = x
        self.y = y
    
    def to_dict(self) -> Dict:
        """Serialize state for API"""
        return {
            "x": self.x,
            "y": self.y,
            "animation": self.current_animation,
            "frame": self.frame_index,
            "is_grabbed": self.is_grabbed
        }
