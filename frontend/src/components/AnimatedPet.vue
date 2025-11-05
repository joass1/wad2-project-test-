<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'

const props = defineProps({
  spriteUrl: { type: String, required: true },
  slice: { type: Number, default: 32 },          // size of one cell/frame
  columns: { type: Number, default: 4 },         // fallback; we auto-detect from image
  scale: { type: Number, default: 5 },           // pet scale
  speed: { type: Number, default: 70 },
  animations: {
    type: Object,
    required: true
  },
  droppedItems: { type: Array, default: () => [] },  // Items dropped on the background
  manualControl: { type: Boolean, default: false },  // Enable WASD keyboard controls
  collisionObjects: { type: Array, default: () => [] },  // Collision rectangles from TMX
  isDead: { type: Boolean, default: false },  // Pet death state
  isDrunk: { type: Boolean, default: false },  // Pet drunk state (3rd+ soju)
  showSojuEmote: { type: Boolean, default: false },  // Show soju emote
  sojuEmoteType: { type: String, default: 'happy' }  // 'happy' or 'drunk'
})

const emit = defineEmits(['item-eaten', 'border-warning', 'petted'])

/* Refs / state */
const actor = ref(null)
const canvasRef = ref(null)
let ctx, img, rafId
const showHeart = ref(false)
let heartTimer = null
let frame = 0
let animKey = 'idle'
let anim
let acc = 0, last = 0
let playingOnce = false
let nextOnceKey = null    // queue a second one-shot (e.g., scared -> jump)

let parent, bounds = { w: 0, h: 0 }
const pos = ref({ x: 0, y: 0 })
let dest = { x: 0, y: 0 }
let idleUntil = 0
let sheetCols = props.columns
let randomEvt = 0
let sleeping = false      // sticky sleep flag
let sleepTimeout = 0      // Timer to auto-wake after sleeping
let eatingItemId = null   // Track which item is being eaten to prevent duplicate emissions

// Drag state
const isDragging = ref(false)
let dragOffset = { x: 0, y: 0 }
let mouseDownTime = 0
let mouseDownPos = { x: 0, y: 0 }
let lastBorderWarning = 0  // Timestamp of last border warning to prevent spam

// Keyboard controls
const keysPressed = {
  w: false,
  a: false,
  s: false,
  d: false
}
let lastKeyPressTime = 0  // Track when user last pressed a key

/* Hitbox adjustment constants */
// Adjust hitbox to be smaller than sprite - tuned for better collision feel
const HITBOX_WIDTH_RATIO = 0.4    // 60% of sprite width
const HITBOX_HEIGHT_RATIO = 0.5   // 70% of sprite height
const HITBOX_Y_OFFSET_RATIO = 0.5 // Start hitbox 40% down from top (keeps bottom aligned)

/**
 * Calculate adjusted hitbox for the pet
 * @param {number} x - Pet X position
 * @param {number} y - Pet Y position
 * @returns {Object} {x, y, width, height} - Adjusted hitbox rectangle
 */
function getPetHitbox(x, y) {
  const petSize = props.slice * props.scale

  // Calculate adjusted dimensions
  const hitboxWidth = petSize * HITBOX_WIDTH_RATIO
  const hitboxHeight = petSize * HITBOX_HEIGHT_RATIO

  // Center horizontally, offset vertically to keep bottom aligned
  const hitboxX = x + (petSize - hitboxWidth) / 2
  const hitboxY = y + (petSize * HITBOX_Y_OFFSET_RATIO)

  return {
    x: hitboxX,
    y: hitboxY,
    width: hitboxWidth,
    height: hitboxHeight
  }
}

/* Helpers */
function setAnim(key, once = false, queueNext = null) {
  // Check if animation exists
  if (!props.animations[key]) {
    // Fallback to idle if animation doesn't exist
    if (!props.animations.idle) return
    key = 'idle'
  }

  animKey = key
  anim = props.animations[key]
  frame = 0
  playingOnce = once && !anim.loop
  nextOnceKey = queueNext

  // sticky sleep -> freeze movement until click
  if (key === 'sleep' || key === 'sleep_loop') {
    sleeping = true
    idleUntil = Number.POSITIVE_INFINITY
  }
}

function randomIdleAnim() {
  // Use animations that exist in the current pet's config
  const idleOptions = []

  // Check which idle animations are available
  // Note: Don't include 'sit' here - it will transition to idle automatically
  // We only want one-shot animations like clean
  if (props.animations.clean && Math.random() < 0.3) {
    idleOptions.push('clean')
  }

  // Most of the time, just sit (which transitions to idle)
  if (idleOptions.length === 0 || Math.random() < 0.7) {
    if (props.animations.sit) {
      setAnim('sit', true)  // Play sit once, then it stays on idle frame
    } else {
      setAnim('idle')
    }
    return
  }

  const chosen = idleOptions[Math.floor(Math.random() * idleOptions.length)]
  setAnim(chosen, true)
}

/* AABB Collision Detection *
/**
 * Check if two rectangles collide
 * @param {Object} rect1 - {x, y, width, height}
 * @param {Object} rect2 - {x, y, width, height}
 * @returns {boolean}
 */
function aabbCollision(rect1, rect2) {
  return (
    rect1.x < rect2.x + rect2.width &&
    rect1.x + rect1.width > rect2.x &&
    rect1.y < rect2.y + rect2.height &&
    rect1.y + rect1.height > rect2.y
  )
}

/**
 * Check if position collides with any collision objects
 * @param {number} x - X position
 * @param {number} y - Y position
 * @returns {boolean}
 */
function checkCollisionAtPosition(x, y) {
  if (!props.collisionObjects || props.collisionObjects.length === 0) return false

  // Use adjusted hitbox instead of full sprite size
  const petRect = getPetHitbox(x, y)

  for (const obj of props.collisionObjects) {
    if (aabbCollision(petRect, obj)) {
      return true
    }
  }

  return false
}

/**
 * Get valid position with smooth wall sliding
 * Tries to move in both X and Y, then individually if combined movement fails
 * @param {number} newX - Desired X position
 * @param {number} newY - Desired Y position
 * @param {number} currentX - Current X position
 * @param {number} currentY - Current Y position
 * @returns {Object} {x, y} - Valid position
 */
function getValidPositionWithSliding(newX, newY, currentX, currentY) {
  const petSize = props.slice * props.scale

  // Clamp to boundaries first
  newX = Math.max(0, Math.min(newX, bounds.w - petSize))
  newY = Math.max(0, Math.min(newY, bounds.h - petSize))

  // Try full movement (both X and Y)
  if (!checkCollisionAtPosition(newX, newY)) {
    return { x: newX, y: newY }
  }

  // Try sliding along X axis only (keep current Y)
  if (!checkCollisionAtPosition(newX, currentY)) {
    return { x: newX, y: currentY }
  }

  // Try sliding along Y axis only (keep current X)
  if (!checkCollisionAtPosition(currentX, newY)) {
    return { x: currentX, y: newY }
  }

  // Can't move - stay at current position
  return { x: currentX, y: currentY }
}

function chooseDest() {
  const pad = 24
  const petSize = props.slice * props.scale
  let attempts = 0
  const maxAttempts = 50

  // Try to find a valid random destination (avoiding collisions)
  while (attempts < maxAttempts) {
    const newX = pad + Math.random() * Math.max(0, bounds.w - petSize - pad * 2)
    const newY = pad + Math.random() * Math.max(0, bounds.h - petSize - pad * 2)

    // Check if this position is collision-free
    if (!checkCollisionAtPosition(newX, newY)) {
      dest.x = newX
      dest.y = newY
      return
    }
    attempts++
  }

  // If no valid position found, keep current destination
}

/* Collision detection with dropped items */
function checkItemCollision() {
  if (!props.droppedItems || props.droppedItems.length === 0) {
    eatingItemId = null  // Reset when no items
    return false
  }

  const petCenterX = pos.value.x + (props.slice * props.scale) / 2
  const petCenterY = pos.value.y + (props.slice * props.scale) / 2
  const COLLISION_DISTANCE = 30  // Increased distance to ensure detection with PNG items

  for (const item of props.droppedItems) {
    // Calculate distance between pet center and item position
    const itemCenterX = item.x
    const itemCenterY = item.y + 20  // Adjust for item center (40px height / 2)

    const dx = itemCenterX - petCenterX
    const dy = itemCenterY - petCenterY
    const distance = Math.sqrt(dx * dx + dy * dy)

    if (distance < COLLISION_DISTANCE) {
      // Only emit once per item to prevent duplicate emissions
      if (eatingItemId !== item.id) {
        eatingItemId = item.id
        console.log(`Pet eating ${item.name}! Distance: ${distance.toFixed(2)}px, Item ID: ${item.id}`)
        emit('item-eaten', item.id)

        // Wake up if sleeping
        if (sleeping) {
          wakeUpPet()
        }

        // Stop movement and play eat animation
        idleUntil = performance.now() + (2000 + Math.random() * 2000)  // Stop for 2-4 seconds

        // Play eat animation if available, otherwise use click
        if (props.animations.eat) {
          setAnim('eat', true)
        } else if (props.animations.click) {
          setAnim('click', true)
        }
      }
      return true
    }
  }

  // Reset eatingItemId when not colliding with any item
  eatingItemId = null
  return false
}

/* Find nearest dropped item */
function findNearestItem() {
  if (!props.droppedItems || props.droppedItems.length === 0) return null

  let nearest = null
  let minDist = Infinity

  const petCenterX = pos.value.x + (props.slice * props.scale) / 2
  const petCenterY = pos.value.y + (props.slice * props.scale) / 2

  for (const item of props.droppedItems) {
    // Calculate item center position for accurate pathfinding
    const itemCenterX = item.x
    const itemCenterY = item.y + 20  // Center of 40px item

    const dx = itemCenterX - petCenterX
    const dy = itemCenterY - petCenterY
    const distance = Math.sqrt(dx * dx + dy * dy)

    if (distance < minDist) {
      minDist = distance
      nearest = item
    }
  }

  return nearest
}


function scheduleRandomEvent() {
  // Schedule sleep events periodically (every 60 seconds)
  const ms = 60000
  randomEvt = window.setTimeout(() => {
    if (!sleeping && !playingOnce && !isDragging.value) {
      // Check if this is a dog and add running behavior
      // All pets can sleep when idle
      const idleStates = ['idle', 'sit', 'clean']
      if (idleStates.includes(animKey) && props.animations.sleep && props.animations.sleep_loop) {
        // Play row 6 falling asleep animation, then transition to row 7 first frame (sleep_loop)
        setAnim('sleep', true, 'sleep_loop')
        // Set sleeping flag after animation starts
        sleeping = true
        idleUntil = Number.POSITIVE_INFINITY // Stay asleep until woken

        // Auto-wake after 10 seconds
        sleepTimeout = window.setTimeout(() => {
          if (sleeping) {
            wakeUpPet()
          }
        }, 10000)
      }
    }
    scheduleRandomEvent()
  }, ms)
}


function wakeUpPet() {
  sleeping = false
  idleUntil = 0

  // Clear sleep timeout if it exists
  if (sleepTimeout) {
    window.clearTimeout(sleepTimeout)
    sleepTimeout = 0
  }

  // Play wake animation if available
  if (props.animations.wake) {
    setAnim('wake', true)
  } else {
    setAnim('idle')
  }
}

/* Keyboard handlers */
function handleKeyDown(event) {
  if (!props.manualControl) return

  const key = event.key.toLowerCase()
  if (key === 'w' || key === 'a' || key === 's' || key === 'd') {
    event.preventDefault()
    keysPressed[key] = true
    lastKeyPressTime = performance.now()
  }
}

function handleKeyUp(event) {
  if (!props.manualControl) return

  const key = event.key.toLowerCase()
  if (key === 'w' || key === 'a' || key === 's' || key === 'd') {
    keysPressed[key] = false
  }
}

/* Mouse handlers */
function handleMouseDown(event) {
  event.preventDefault()
  event.stopPropagation()

  mouseDownTime = Date.now()
  mouseDownPos = { x: event.clientX, y: event.clientY }

  const parentRect = parent.getBoundingClientRect()
  dragOffset.x = event.clientX - parentRect.left - pos.value.x
  dragOffset.y = event.clientY - parentRect.top - pos.value.y

  document.addEventListener('mousemove', handleMouseMove, { passive: false })
  document.addEventListener('mouseup', handleMouseUp)
}

function handleMouseMove(event) {
  event.preventDefault()

  const dx = event.clientX - mouseDownPos.x
  const dy = event.clientY - mouseDownPos.y
  const distance = Math.sqrt(dx * dx + dy * dy)

  if (distance > 5) {
    if (!isDragging.value) {
      isDragging.value = true

      // Wake up if sleeping
      if (sleeping) {
        wakeUpPet()
      }

      // Use clean animation when grabbed if available, otherwise idle
      if (props.animations.clean) {
        setAnim('clean')
      } else {
        setAnim('idle')
      }
    }

    const parentRect = parent.getBoundingClientRect()
    const petSize = props.slice * props.scale

    // Calculate new position
    let newX = event.clientX - parentRect.left - dragOffset.x
    let newY = event.clientY - parentRect.top - dragOffset.y

    // Check if trying to go outside boundaries
    const hitBorder = newX < 0 || newX > bounds.w - petSize || newY < 0 || newY > bounds.h - petSize

    // Emit warning if hitting border (throttled to once per second)
    if (hitBorder) {
      const now = Date.now()
      if (now - lastBorderWarning > 1000) {
        emit('border-warning')
        lastBorderWarning = now
      }
    }

    // Update position with collision detection and wall sliding
    const validPos = getValidPositionWithSliding(newX, newY, pos.value.x, pos.value.y)
    pos.value.x = validPos.x
    pos.value.y = validPos.y
  }
}

function handleMouseUp(event) {
  const mouseUpTime = Date.now()
  const holdDuration = mouseUpTime - mouseDownTime

  const dx = event.clientX - mouseDownPos.x
  const dy = event.clientY - mouseDownPos.y
  const distance = Math.sqrt(dx * dx + dy * dy)

  if (holdDuration < 200 && distance < 5) {
    // Don't do anything if pet is dead
    if (props.isDead) {
      console.log('Pet is dead. Feed it to revive!')
      return
    }

    // Don't do anything if pet is drunk
    if (props.isDrunk) {
      console.log('Pet is drunk! Wait for it to sober up...')
      return
    }

    // Quick click - wake up pet if sleeping
    if (sleeping) {
      wakeUpPet()
    } else {
      // Stop all movement for animation duration + hold time
      idleUntil = performance.now() + (500 + 1000 + Math.random() * 2000)  // Animation + 1s hold + random wait

      // Clear any existing heart timer
      if (heartTimer) {
        clearTimeout(heartTimer)
      }

      // Show heart and play click animation (not as one-shot, so it stays on last frame)
      showHeart.value = true

      // Play click animation if available, otherwise use clean
      if (props.animations.click) {
        setAnim('click', false)  // Play animation without auto-transition to idle
      } else if (props.animations.clean) {
        setAnim('clean', false)
      } else {
        setAnim('idle')
      }

      console.log('Pet received love!')
      try { emit('petted') } catch (e) {}

      // Hide heart after 1.5 seconds (animation duration)
      heartTimer = setTimeout(() => {
        showHeart.value = false
        heartTimer = null
      }, 1500)

      // After animation finishes (0.5s for 4 frames at 8fps) + 1 second hold, transition to idle
      setTimeout(() => {
        if (animKey === 'click') {
          setAnim('idle')
        }
      }, 500 + 1000)  // Animation duration + 1 second hold
    }
  } else if (isDragging.value) {
    isDragging.value = false
    if (!props.isDead) {
      setAnim('idle')
    }
    idleUntil = performance.now() + (1000 + Math.random() * 2000)
  }

  document.removeEventListener('mousemove', handleMouseMove)
  document.removeEventListener('mouseup', handleMouseUp)
}

/* Movement / render loop */
function loop(t) {
  rafId = requestAnimationFrame(loop)
  if (!last) last = t
  const dt = (t - last) / 1000
  last = t
  acc += dt

  // If pet is dead, display death sprite and stop all movement
  if (props.isDead) {
    // Set death sprite to row 7, column 1 (fixed frame, no animation)
    frame = 1  // Column 1
    anim = { row: 7, fps: 1, loop: false, frames: 1, colStart: 1 }
    animKey = 'dead'
    drawFrame()
    return  // Stop processing movement
  }

  // If pet is drunk, display drunk sprite (row 6, last column) and stop movement
  if (props.isDrunk) {
    // Set drunk sprite to row 6, last column (fixed frame, no animation)
    const lastCol = sheetCols - 1  // Last column index
    frame = 0  // Reset frame
    anim = { row: 6, fps: 1, loop: false, frames: 1, colStart: lastCol }
    animKey = 'drunk'
    drawFrame()
    return  // Stop processing movement
  }

  // Check for item collision
  checkItemCollision()

  // movement only when not sticky sleeping and not dragging
  if (!sleeping && !isDragging.value) {
    const now = performance.now()
    const petSize = props.slice * props.scale

    // Check if user is controlling with keyboard
    const isUsingKeyboard = props.manualControl && (keysPressed.w || keysPressed.a || keysPressed.s || keysPressed.d)
    const hasRecentKeyPress = props.manualControl && (now - lastKeyPressTime < 100)

    if (isUsingKeyboard || hasRecentKeyPress) {
      // Manual keyboard control
      let vx = 0
      let vy = 0
      const keyboardSpeed = props.speed * 1.5 // Faster for keyboard control

      if (keysPressed.w) vy -= keyboardSpeed
      if (keysPressed.s) vy += keyboardSpeed
      if (keysPressed.a) vx -= keyboardSpeed
      if (keysPressed.d) vx += keyboardSpeed

      // Normalize diagonal movement
      if (vx !== 0 && vy !== 0) {
        const magnitude = Math.sqrt(vx * vx + vy * vy)
        vx = (vx / magnitude) * keyboardSpeed
        vy = (vy / magnitude) * keyboardSpeed
      }

      // Apply movement
      let newX = pos.value.x + vx * dt
      let newY = pos.value.y + vy * dt

      // Update position with collision detection and wall sliding
      const validPos = getValidPositionWithSliding(newX, newY, pos.value.x, pos.value.y)
      pos.value.x = validPos.x
      pos.value.y = validPos.y

      // Set appropriate animation based on direction
      if (vx !== 0 || vy !== 0) {
        const absDx = Math.abs(vx)
        const absDy = Math.abs(vy)

        // Check if this is a dog and if we should use running animations
        if (absDx > absDy) {
          if (vx > 0) setAnim('move_right')
          else setAnim('move_left')
        } else {
          if (vy > 0) setAnim('move_down')
          else setAnim('move_up')
        }
      } else {
        setAnim('idle')
      }
    } else if (!props.manualControl) {
      // Autonomous AI behavior (only when manual control is disabled)
      // Check for nearby items - prioritize walking to food!
      const nearestItem = findNearestItem()
      if (nearestItem) {
        const targetX = nearestItem.x - petSize / 2
        const targetY = nearestItem.y - petSize / 2

        // Move to food (no collision checking)
        dest.x = targetX
        dest.y = targetY
        idleUntil = 0  // Override any idle time to move immediately
      }

      if (now >= idleUntil) {
        const dx = dest.x - pos.value.x
        const dy = dest.y - pos.value.y
        const dist = Math.sqrt(dx * dx + dy * dy)

        if (dist < 5) {
          // Reached destination
          if (!nearestItem) {
            // No item nearby, choose random destination
            idleUntil = now + (3000 + Math.random() * 7000)
            randomIdleAnim()
            chooseDest()
          }
        } else {
          // Move in both X and Y directions
          const vx = (dx / dist) * props.speed
          const vy = (dy / dist) * props.speed
          let newX = pos.value.x + vx * dt
          let newY = pos.value.y + vy * dt

          // Update position with collision detection and wall sliding
          const validPos = getValidPositionWithSliding(newX, newY, pos.value.x, pos.value.y)
          pos.value.x = validPos.x
          pos.value.y = validPos.y

          // Determine which direction is dominant for animation
          const absDx = Math.abs(dx)
          const absDy = Math.abs(dy)

          // Choose animation based on dominant direction
          // Check if this is a dog and if we should use running animations
          if (absDx > absDy) {
            // Moving horizontally more than vertically
            if (vx > 0) {
              if (animKey !== 'move_right') setAnim('move_right')
            } else {
              if (animKey !== 'move_left') setAnim('move_left')
            }
          } else {
            // Moving vertically more than horizontally
            if (vy > 0) {
              if (animKey !== 'move_down') setAnim('move_down')
            } else {
              if (animKey !== 'move_up') setAnim('move_up')
            }
          }

          // more frequent loitering: around 12% chance per second to pause 2–5s (but not if chasing food!)
          if (!nearestItem && Math.random() < 0.12 * dt) {
            idleUntil = now + (2000 + Math.random() * 3000)
            randomIdleAnim()
          }
        }
      }
    }
  }

  // frame stepping with robust length
  const frameDur = 1 / anim.fps
  while (acc >= frameDur) {
    acc -= frameDur
    frame++
    const seqLen = getSeqLength(anim)
    if (frame >= seqLen) {
      if (anim.loop) {
        frame = 0
      } else {
        // one-shot finished
        if (nextOnceKey) {
          const nxt = nextOnceKey
          nextOnceKey = null
          setAnim(nxt, true)
        } else {
          playingOnce = false
          // Stay on last frame if it's sit or click animation
          // Otherwise trigger random idle animation
          if (animKey === 'sit' || animKey === 'click') {
            // Sit/click animation ended, stay on last frame
            frame = seqLen - 1
          } else if (!sleeping) {
            randomIdleAnim()
          }
        }
      }
    }
  }

  drawFrame()
}

/* Sequence helpers (avoid “disappearing” on sparse rows) */
function getSeqLength(a) {
  if (Array.isArray(a.sequence) && a.sequence.length) return a.sequence.length
  const start = a.colStart ?? 0
  return Math.max(1, Math.min(a.frames ?? 1, sheetCols - start))
}
function getSourceCol(a, f) {
  if (Array.isArray(a.sequence) && a.sequence.length) {
    return a.sequence[f % a.sequence.length]
  }
  const start = a.colStart ?? 0
  const len = getSeqLength(a)
  return start + (f % len)
}

/* Drawing (with left/right flip) */
function drawFrame() {
  const s = props.slice
  const colIndex = getSourceCol(anim, frame)
  const safeCol = Math.max(0, Math.min(colIndex, sheetCols - 1))
  const sx = safeCol * s
  const sy = anim.row * s

  ctx.save()
  ctx.clearRect(0, 0, s, s)
  // No flipping - using directional sprites
  ctx.drawImage(img, sx, sy, s, s, 0, 0, s, s)
  ctx.restore()

  actor.value.style.transform = `translate(${pos.value.x}px, ${pos.value.y}px)`
}

/* Measuring stage bounds */
function measure() {
  if (!parent) return
  const r = parent.getBoundingClientRect()
  bounds.w = r.width
  bounds.h = r.height
}

/* Lifecycle */
onMounted(async () => {
  parent = actor.value?.parentElement
  measure()
  window.addEventListener('resize', measure)

  // Watch for parent size changes (e.g., when sidebar toggles)
  let resizeObserver
  if (parent && window.ResizeObserver) {
    resizeObserver = new ResizeObserver(() => {
      measure()
    })
    resizeObserver.observe(parent)
  }

  const c = canvasRef.value
  const dpr = window.devicePixelRatio || 1
  c.width = props.slice * dpr
  c.height = props.slice * dpr
  c.style.width = `${props.slice * props.scale}px`
  c.style.height = `${props.slice * props.scale}px`
  ctx = c.getContext('2d')
  ctx.imageSmoothingEnabled = false
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0)

  img = new Image()
  img.src = props.spriteUrl
  await img.decode()

  // auto-detect columns from image width to prevent out-of-range reads
  sheetCols = Math.max(1, Math.floor(img.naturalWidth / props.slice))

  // Spawn pet in a safe position (center of map, avoiding collisions)
  const petSize = props.slice * props.scale
  const centerX = (bounds.w - petSize) / 2
  const centerY = (bounds.h - petSize) / 2

  // Try to spawn at center first
  if (!checkCollisionAtPosition(centerX, centerY)) {
    pos.value.x = centerX
    pos.value.y = centerY
  } else {
    // If center is blocked, try to find a safe spawn point
    let spawnAttempts = 0
    let foundSafeSpot = false

    while (spawnAttempts < 100 && !foundSafeSpot) {
      const testX = Math.random() * Math.max(0, bounds.w - petSize)
      const testY = Math.random() * Math.max(0, bounds.h - petSize)

      if (!checkCollisionAtPosition(testX, testY)) {
        pos.value.x = testX
        pos.value.y = testY
        foundSafeSpot = true
      }
      spawnAttempts++
    }

    // Fallback: spawn at center even if blocked (will get corrected on first move)
    if (!foundSafeSpot) {
      pos.value.x = centerX
      pos.value.y = centerY
    }
  }

  console.log(`Pet spawned at (${pos.value.x}, ${pos.value.y})`)

  chooseDest()
  setAnim('idle')
  idleUntil = 0

  scheduleRandomEvent()
  rafId = requestAnimationFrame(loop)
  c.addEventListener('mousedown', handleMouseDown)

  // Add keyboard event listeners
  window.addEventListener('keydown', handleKeyDown)
  window.addEventListener('keyup', handleKeyUp)

  // Store resizeObserver for cleanup
  actor.value._resizeObserver = resizeObserver
})

onBeforeUnmount(() => {
  cancelAnimationFrame(rafId)
  window.removeEventListener('resize', measure)
  canvasRef.value?.removeEventListener('mousedown', handleMouseDown)
  document.removeEventListener('mousemove', handleMouseMove)
  document.removeEventListener('mouseup', handleMouseUp)
  window.clearTimeout(randomEvt)
  window.clearTimeout(sleepTimeout)
  if (heartTimer) {
    clearTimeout(heartTimer)
  }

  // Remove keyboard event listeners
  window.removeEventListener('keydown', handleKeyDown)
  window.removeEventListener('keyup', handleKeyUp)

  // Clean up ResizeObserver
  if (actor.value?._resizeObserver) {
    actor.value._resizeObserver.disconnect()
  }
})
</script>

<template>
  <!-- parent stage must be position:relative -->
  <div ref="actor" class="pet-actor">
    <canvas ref="canvasRef" class="pet-canvas" />
    <img v-if="showHeart && !isDead && !isDrunk" src="/heart.png" class="heart-icon" />
    <img v-if="isDead" src="/dead.png" class="dead-icon" />
    <img
      v-if="showSojuEmote && !isDead"
      :src="`/soju ${sojuEmoteType}.png`"
      :class="['soju-emote', { 'soju-drunk-pulse': isDrunk && sojuEmoteType === 'drunk' }]"
    />
  </div>
</template>

<style scoped>
.pet-actor {
  position: absolute;
  left: 0;
  top: 0;
  will-change: transform;
  pointer-events: auto;
}
.pet-canvas {
  image-rendering: pixelated;
  cursor: grab;
  border-radius: 6px;
  user-select: none;
  -webkit-user-select: none;
}
.pet-canvas:active {
  cursor: grabbing;
}

.heart-icon {
  position: absolute;
  top: 0%;
  left: 50%;
  transform: translateX(-50%);
  width: 50%;
  height: auto;
  pointer-events: none;
  animation: heart-float 1.5s ease-out;
  z-index: 10;
}

.dead-icon {
  position: absolute;
  top: -10%;
  left: 50%;
  transform: translateX(-50%);
  width: 60%;
  height: auto;
  pointer-events: none;
  z-index: 10;
  animation: dead-pulse 2s ease-in-out infinite;
}

@keyframes heart-float {
  0% {
    opacity: 0;
    transform: translateX(-50%) translateY(10px);
  }
  20% {
    opacity: 1;
  }
  80% {
    opacity: 1;
  }
  100% {
    opacity: 0;
    transform: translateX(-50%) translateY(-20px);
  }
}

@keyframes dead-pulse {
  0%, 100% {
    opacity: 0.8;
    transform: translateX(-50%) scale(1);
  }
  50% {
    opacity: 1;
    transform: translateX(-50%) scale(1.05);
  }
}

.soju-emote {
  position: absolute;
  top: 0%;
  left: 50%;
  transform: translateX(-50%);
  width: 55%;
  height: auto;
  pointer-events: none;
  animation: soju-float 2.5s ease-out;
  z-index: 10;
}

@keyframes soju-float {
  0% {
    opacity: 0;
    transform: translateX(-50%) translateY(10px) scale(0.8);
  }
  15% {
    opacity: 1;
    transform: translateX(-50%) translateY(0px) scale(1);
  }
  85% {
    opacity: 1;
    transform: translateX(-50%) translateY(-5px) scale(1);
  }
  100% {
    opacity: 0;
    transform: translateX(-50%) translateY(-25px) scale(0.9);
  }
}

/* Drunk pulse animation - stays visible for 5 seconds like dead.png */
.soju-drunk-pulse {
  animation: soju-drunk-pulse 2s ease-in-out infinite !important;
}

@keyframes soju-drunk-pulse {
  0%, 100% {
    opacity: 0.85;
    transform: translateX(-50%) translateY(-5px) scale(1);
  }
  50% {
    opacity: 1;
    transform: translateX(-50%) translateY(-8px) scale(1.08);
  }
}
</style>
