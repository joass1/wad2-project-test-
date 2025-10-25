// Pet catalog with animation definitions
// Animation rows for Stardew Valley style pets:
// Row 0: Moving down
// Row 1: Moving right
// Row 2: Moving up
// Row 3: Moving left
// Row 4: Sitting animation (frames 0-2), Idle standing (frame 3)
// Row 5: Cleaning/grooming
// Row 6: Falling asleep animation (last frame is sleeping)
// Row 7: Sleeping curled up (first frame - loop this), Waking up animation (frames 1-3)

const SCALE = 2  // Global pet scale

export const PET_CATALOG = {
  catBlack: {
    label: 'Black Cat',
    config: {
      spriteUrl: '/PC _ Computer - Stardew Valley - Animals - Cat (Black).png',
      slice: 32,
      scale: SCALE,
      speed: 70,
      animations: {
        move_down: { row: 0, fps: 6, loop: true, frames: 4, colStart: 0 },
        move_right: { row: 1, fps: 6, loop: true, frames: 4, colStart: 0 },
        move_up: { row: 2, fps: 6, loop: true, frames: 4, colStart: 0 },
        move_left: { row: 3, fps: 6, loop: true, frames: 4, colStart: 0 },
        idle: { row: 4, fps: 1, loop: true, frames: 1, colStart: 3 },  // Last frame of row 4 (idle standing)
        sit: { row: 4, fps: 4, loop: false, frames: 4, colStart: 0 },   // Sitting animation (transitions to idle on frame 3)
        clean: { row: 5, fps: 8, loop: false, frames: 4, colStart: 0 },
        eat: { row: 5, fps: 8, loop: false, frames: 4, colStart: 0 },  // Eating animation (cats)
        sleep: { row: 6, fps: 3, loop: false, frames: 4, colStart: 0 }, // Falling asleep animation
        sleep_loop: { row: 7, fps: 1, loop: true, frames: 1, colStart: 0 }, // Sleeping curled up (looping)
        wake: { row: 7, fps: 6, loop: false, frames: 3, colStart: 1 },  // Waking up animation (skip first frame)
        click: { row: 6, fps: 8, loop: false, frames: 4, colStart: 0 }  // Click response animation
      }
    }
  },

  catGrey: {
    label: 'Grey Cat',
    config: {
      spriteUrl: '/PC _ Computer - Stardew Valley - Animals - Cat (Grey).png',
      slice: 32,
      scale: SCALE,
      speed: 70,
      animations: {
        move_down: { row: 0, fps: 6, loop: true, frames: 4, colStart: 0 },
        move_right: { row: 1, fps: 6, loop: true, frames: 4, colStart: 0 },
        move_up: { row: 2, fps: 6, loop: true, frames: 4, colStart: 0 },
        move_left: { row: 3, fps: 6, loop: true, frames: 4, colStart: 0 },
        idle: { row: 4, fps: 1, loop: true, frames: 1, colStart: 3 },
        sit: { row: 4, fps: 4, loop: false, frames: 4, colStart: 0 },
        clean: { row: 5, fps: 8, loop: false, frames: 4, colStart: 0 },
        eat: { row: 5, fps: 8, loop: false, frames: 4, colStart: 0 },  // Eating animation (cats)
        sleep: { row: 6, fps: 3, loop: false, frames: 4, colStart: 0 },
        sleep_loop: { row: 7, fps: 1, loop: true, frames: 1, colStart: 0 },
        wake: { row: 7, fps: 6, loop: false, frames: 3, colStart: 1 },
        click: { row: 6, fps: 8, loop: false, frames: 4, colStart: 0 }
      }
    }
  },

  catNew: {
    label: 'Orange Cat',
    config: {
      spriteUrl: '/PC _ Computer - Stardew Valley - Animals - Cat.png',
      slice: 32,
      scale: SCALE,
      speed: 70,
      animations: {
        move_down: { row: 0, fps: 6, loop: true, frames: 4, colStart: 0 },
        move_right: { row: 1, fps: 6, loop: true, frames: 4, colStart: 0 },
        move_up: { row: 2, fps: 6, loop: true, frames: 4, colStart: 0 },
        move_left: { row: 3, fps: 6, loop: true, frames: 4, colStart: 0 },
        idle: { row: 4, fps: 1, loop: true, frames: 1, colStart: 3 },
        sit: { row: 4, fps: 4, loop: false, frames: 4, colStart: 0 },
        clean: { row: 5, fps: 8, loop: false, frames: 4, colStart: 0 },
        eat: { row: 5, fps: 8, loop: false, frames: 4, colStart: 0 },  // Eating animation (cats)
        sleep: { row: 6, fps: 3, loop: false, frames: 4, colStart: 0 },
        sleep_loop: { row: 7, fps: 1, loop: true, frames: 1, colStart: 0 },
        wake: { row: 7, fps: 6, loop: false, frames: 3, colStart: 1 },
        click: { row: 6, fps: 8, loop: false, frames: 4, colStart: 0 }
      }
    }
  },

  dogBlonde: {
    label: 'Blonde Dog',
    config: {
      spriteUrl: '/PC _ Computer - Stardew Valley - Animals - Dog (Blonde).png',
      slice: 32,
      scale: SCALE,
      speed: 80,
      animations: {
        move_down: { row: 0, fps: 6, loop: true, frames: 4, colStart: 0 },
        move_right: { row: 1, fps: 6, loop: true, frames: 4, colStart: 0 },
        move_up: { row: 2, fps: 6, loop: true, frames: 4, colStart: 0 },
        move_left: { row: 3, fps: 6, loop: true, frames: 4, colStart: 0 },
        idle: { row: 4, fps: 1, loop: true, frames: 1, colStart: 3 },
        sit: { row: 4, fps: 4, loop: false, frames: 4, colStart: 0 },
        clean: { row: 5, fps: 8, loop: false, frames: 4, colStart: 0 },
        eat: { row: 8, fps: 8, loop: false, frames: 3, colStart: 0 },  // Eating animation (dogs)
        sleep: { row: 6, fps: 3, loop: false, frames: 4, colStart: 0 },
        sleep_loop: { row: 7, fps: 1, loop: true, frames: 1, colStart: 0 },
        wake: { row: 7, fps: 6, loop: false, frames: 3, colStart: 1 },
        click: { row: 6, fps: 8, loop: false, frames: 4, colStart: 0 }
      }
    }
  },

  dogGrey: {
    label: 'Grey Dog',
    config: {
      spriteUrl: '/PC _ Computer - Stardew Valley - Animals - Dog (Grey).png',
      slice: 32,
      scale: SCALE,
      speed: 80,
      animations: {
        move_down: { row: 0, fps: 6, loop: true, frames: 4, colStart: 0 },
        move_right: { row: 1, fps: 6, loop: true, frames: 4, colStart: 0 },
        move_up: { row: 2, fps: 6, loop: true, frames: 4, colStart: 0 },
        move_left: { row: 3, fps: 6, loop: true, frames: 4, colStart: 0 },
        idle: { row: 4, fps: 1, loop: true, frames: 1, colStart: 3 },
        sit: { row: 4, fps: 4, loop: false, frames: 4, colStart: 0 },
        clean: { row: 5, fps: 8, loop: false, frames: 4, colStart: 0 },
        eat: { row: 8, fps: 8, loop: false, frames: 3, colStart: 0 },  // Eating animation (dogs)
        sleep: { row: 6, fps: 3, loop: false, frames: 4, colStart: 0 },
        sleep_loop: { row: 7, fps: 1, loop: true, frames: 1, colStart: 0 },
        wake: { row: 7, fps: 6, loop: false, frames: 3, colStart: 1 },
        click: { row: 6, fps: 8, loop: false, frames: 4, colStart: 0 }
      }
    }
  },

  dogLight: {
    label: 'Light Brown Dog',
    config: {
      spriteUrl: '/PC _ Computer - Stardew Valley - Animals - Dog (Light Brown).png',
      slice: 32,
      scale: SCALE,
      speed: 80,
      animations: {
        move_down: { row: 0, fps: 6, loop: true, frames: 4, colStart: 0 },
        move_right: { row: 1, fps: 6, loop: true, frames: 4, colStart: 0 },
        move_up: { row: 2, fps: 6, loop: true, frames: 4, colStart: 0 },
        move_left: { row: 3, fps: 6, loop: true, frames: 4, colStart: 0 },
        idle: { row: 4, fps: 1, loop: true, frames: 1, colStart: 3 },
        sit: { row: 4, fps: 4, loop: false, frames: 4, colStart: 0 },
        clean: { row: 5, fps: 8, loop: false, frames: 4, colStart: 0 },
        eat: { row: 8, fps: 8, loop: false, frames: 3, colStart: 0 },  // Eating animation (dogs)
        sleep: { row: 6, fps: 3, loop: false, frames: 4, colStart: 0 },
        sleep_loop: { row: 7, fps: 1, loop: true, frames: 1, colStart: 0 },
        wake: { row: 7, fps: 6, loop: false, frames: 3, colStart: 1 },
        click: { row: 6, fps: 8, loop: false, frames: 4, colStart: 0 }
      }
    }
  }
}

// Get list of pet keys
export const PET_KEYS = Object.keys(PET_CATALOG)
