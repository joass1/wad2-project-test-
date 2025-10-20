# Sprite Sheet Configuration Guide

This guide explains how to customize sprite extraction for the pet system.

## Overview

The pet system now uses **sprite sheets** instead of individual GIF files. Sprites are extracted from a single image file (e.g., `cat-spritesheet.png`) using configurable row and column coordinates.

## Sprite Sheet Structure

The sprite sheet is organized as a grid:
- **Columns**: Individual frames of animation (horizontal)
- **Rows**: Different animations or actions (vertical)
- **Slice**: The pixel size of each cell (default: 32x32)

Example:
```
Row 0: [idle frame 1] [idle frame 2] [idle frame 3] ... [idle frame 8]
Row 1: [idle2 frame 1] [idle2 frame 2] ...
Row 2: [clean frame 1] [clean frame 2] ...
...
```

## Configuration Format

### Frontend (GlobalDesktopPet.vue)

Located at lines 31-42 in `GlobalDesktopPet.vue`:

```javascript
animations: {
  idle:     { row: 0, frames: 8, fps: 6,  loop: true,  colStart: 0 },
  grabbed:  { row: 7, frames: 6, fps: 8,  loop: true,  colStart: 0 },
  falling:  { row: 9, frames: 8, fps: 12, loop: true,  colStart: 0 }
}
```

### Backend (pet.py)

Located at lines 29-47 in `backend/app/api/routes/pet.py`:

```python
"animations": {
    "idle":     {"row": 0, "frames": 8, "fps": 6,  "loop": True,  "colStart": 0},
    "grabbed":  {"row": 7, "frames": 6, "fps": 8,  "loop": True,  "colStart": 0},
    "falling":  {"row": 9, "frames": 8, "fps": 12, "loop": True,  "colStart": 0}
}
```

## Animation Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `row` | Number | Which row in the sprite sheet (0-indexed) |
| `frames` | Number | How many frames to use from this row |
| `fps` | Number | Frames per second (animation speed) |
| `loop` | Boolean | Whether to loop the animation continuously |
| `colStart` | Number | Starting column (default: 0, allows offset within row) |

## Current Animation Mappings

### Default Cat Sprite Sheet

| Animation | Row | Frames | Usage |
|-----------|-----|--------|-------|
| `idle` | 0 | 8 | Default standing still |
| `idle2` | 1 | 8 | Alternate idle animation |
| `clean` | 2 | 8 | Cleaning/grooming |
| `clean2` | 3 | 8 | Alternate cleaning |
| `walk` / `walk_left` | 4 | 8 | Walking left |
| `walk2` / `walk_right` | 5 | 8 | Walking right |
| `sleep` | 6 | 6 | Sleeping |
| `grabbed` | 7 | 6 | When being dragged (paw animation) |
| `jump` | 8 | 8 | Jumping |
| `falling` / `scared` | 9 | 8 | Falling or scared |

## How to Customize Sprite Extraction

### Example 1: Use Different Sprite for Grabbed State

Want the cat to show a different animation when grabbed? Change row 7 to another row:

**In GlobalDesktopPet.vue:**
```javascript
grabbed: { row: 8, frames: 8, fps: 12, loop: true, colStart: 0 }  // Use jump animation
```

**In pet.py:**
```python
"grabbed": {"row": 8, "frames": 8, "fps": 12, "loop": True, "colStart": 0}
```

### Example 2: Extract Partial Animation

Want to use only frames 3-6 from row 2?

```javascript
custom_anim: { row: 2, frames: 4, fps: 8, loop: true, colStart: 3 }
```

This will use columns 3, 4, 5, 6 from row 2.

### Example 3: Add Custom Animation

To add a new custom animation:

1. **Identify the row and columns** in your sprite sheet
2. **Add to frontend** (`GlobalDesktopPet.vue` line 31-42):
   ```javascript
   my_custom: { row: 10, frames: 6, fps: 10, loop: true, colStart: 0 }
   ```

3. **Add to backend** (`pet.py` line 29-47):
   ```python
   "my_custom": {"row": 10, "frames": 6, "fps": 10, "loop": True, "colStart": 0}
   ```

4. **Use in code** by calling `setAnim('my_custom')`

### Example 4: Different Sprite Sheet

To use a completely different sprite sheet:

**In GlobalDesktopPet.vue (line 25):**
```javascript
spriteUrl: '/my-custom-spritesheet.png',
slice: 64,  // If your sprites are 64x64 instead of 32x32
```

**In pet.py (line 24-27):**
```python
"sprite_sheet": {
    "url": "/my-custom-spritesheet.png",
    "slice": 64,
    "scale": 3
}
```

## Physics Configuration

You can also customize physics behavior in the backend:

**In pet.py (line 48-53):**
```python
"physics": {
    "gravity": 0.8,              # Falling acceleration
    "terminal_velocity": 15,      # Maximum fall speed
    "drag_coefficient": 0.95,     # Air resistance (0-1, closer to 1 = more drag)
    "walk_speed": 2              # Horizontal walking speed
}
```

**In GlobalDesktopPet.vue (lines 69-71):**
```javascript
const GRAVITY = 0.8          // pixels per frame^2
const TERMINAL_VELOCITY = 15  // max falling speed
const DRAG_COEFFICIENT = 0.95 // air resistance
```

## Testing Your Changes

1. **Save your changes** to both frontend and backend files
2. **Restart the backend** server if you changed `pet.py`
3. **Refresh the frontend** to see the sprite sheet in action
4. **Drag the pet** to test the grabbed animation
5. **Drop the pet** above a bordered element to test falling

## Bordered Div Collision

The pet will fall and land on any HTML element that has a visible border. The collision detection checks:
- Elements with `border-width > 0`
- Elements with `border-top-width > 0`
- Horizontal overlap between pet and element
- Pet is above the element

To create "platforms" for the pet to land on, add CSS borders:
```css
.platform {
  border: 2px solid #ccc;
  padding: 20px;
}
```

## Animation States

The pet automatically switches between animations:
- **idle/idle2/clean** - When standing still
- **walk/walk2** - When walking naturally
- **grabbed** (row 7) - When being dragged
- **falling** (row 9) - When dropped and falling
- **sleep** (row 6) - After idle for a while

## Tips

- **Higher FPS** = faster animation
- **More frames** = smoother animation
- **loop: false** = animation plays once then stops
- **colStart** allows using different sections of the same row
- The pet automatically flips horizontally based on walking direction

## File Locations

- Frontend sprite config: `frontend/src/components/GlobalDesktopPet.vue` (lines 23-43)
- Backend sprite config: `backend/app/api/routes/pet.py` (lines 19-54)
- Backend physics logic: `backend/app/core/pet_engine/pet_state.py`
- Sprite sheet file: `frontend/public/cat-spritesheet.png`
