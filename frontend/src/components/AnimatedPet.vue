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
  collisionMap: { type: Array, default: () => [] },  // 2D boolean array for tile collision
  tileSize: { type: Number, default: 32 },  // Size of each tile (32px, no scaling)
  mapCols: { type: Number, default: 40 },
  mapRows: { type: Number, default: 25 },
  manualControl: { type: Boolean, default: false }  // Enable WASD keyboard controls
})

const emit = defineEmits(['item-eaten', 'border-warning'])

/* Refs / state */
const actor = ref(null)
const canvasRef = ref(null)
let ctx, img, rafId
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
let lastValidPos = { x: 0, y: 0 }  // Store last valid position for collision snap-back
let lastBorderWarning = 0  // Timestamp of last border warning to prevent spam

// Keyboard controls
const keysPressed = {
  w: false,
  a: false,
  s: false,
  d: false
}
let lastKeyPressTime = 0  // Track when user last pressed a key

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

/* Tile-based collision detection */
function isPositionValid(x, y) {
  if (!props.collisionMap || props.collisionMap.length === 0) return true

  const petSize = props.slice * props.scale

  // Check all four corners of the pet's bounding box
  const corners = [
    { px: x, py: y },                           // top-left
    { px: x + petSize, py: y },                 // top-right
    { px: x, py: y + petSize },                 // bottom-left
    { px: x + petSize, py: y + petSize }        // bottom-right
  ]

  for (const corner of corners) {
    const tileCol = Math.floor(corner.px / props.tileSize)
    const tileRow = Math.floor(corner.py / props.tileSize)

    // Check bounds
    if (tileRow < 0 || tileRow >= props.mapRows || tileCol < 0 || tileCol >= props.mapCols) {
      return false // Out of bounds
    }

    // Check if tile is solid
    if (props.collisionMap[tileRow] && props.collisionMap[tileRow][tileCol]) {
      return false // Solid tile
    }
  }

  return true
}

/* Simple pathfinding - check if path to destination is clear */
function hasLineOfSight(x1, y1, x2, y2) {
  const steps = 20
  for (let i = 0; i <= steps; i++) {
    const t = i / steps
    const x = x1 + (x2 - x1) * t
    const y = y1 + (y2 - y1) * t
    if (!isPositionValid(x, y)) {
      return false
    }
  }
  return true
}

function chooseDest() {
  const pad = 24
  const petSize = props.slice * props.scale
  let attempts = 0
  const maxAttempts = 50

  while (attempts < maxAttempts) {
    const newX = pad + Math.random() * Math.max(0, bounds.w - petSize - pad * 2)
    const newY = pad + Math.random() * Math.max(0, bounds.h - petSize - pad * 2)

    if (isPositionValid(newX, newY)) {
      dest.x = newX
      dest.y = newY
      return
    }
    attempts++
  }

  // Fallback: keep current destination if we can't find a valid one
}

/* Collision detection with dropped items */
function checkItemCollision() {
  if (!props.droppedItems || props.droppedItems.length === 0) {
    eatingItemId = null  // Reset when no items
    return false
  }

  const petCenterX = pos.value.x + (props.slice * props.scale) / 2
  const petCenterY = pos.value.y + (props.slice * props.scale) / 2
  const COLLISION_DISTANCE = 60  // Increased distance to ensure detection with PNG items

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

        // Become happy
        idleUntil = performance.now() + 1000

        // Play happy animation if available
        if (props.animations.click) {
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

      // Store current position as last valid position
      lastValidPos.x = pos.value.x
      lastValidPos.y = pos.value.y

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

    // Clamp to boundaries
    newX = Math.max(0, Math.min(newX, bounds.w - petSize))
    newY = Math.max(0, Math.min(newY, bounds.h - petSize))

    // Emit warning if hitting border (throttled to once per second)
    if (hitBorder) {
      const now = Date.now()
      if (now - lastBorderWarning > 1000) {
        emit('border-warning')
        lastBorderWarning = now
      }
    }

    // Check if new position is valid (not on solid tiles)
    if (isPositionValid(newX, newY)) {
      // Valid position - update and store as last valid
      pos.value.x = newX
      pos.value.y = newY
      lastValidPos.x = newX
      lastValidPos.y = newY
    } else {
      // Try sliding along X axis only
      if (isPositionValid(newX, lastValidPos.y)) {
        pos.value.x = newX
        pos.value.y = lastValidPos.y
        lastValidPos.x = newX
      }
      // Try sliding along Y axis only
      else if (isPositionValid(lastValidPos.x, newY)) {
        pos.value.x = lastValidPos.x
        pos.value.y = newY
        lastValidPos.y = newY
      }
      // If neither works, stay at lastValidPos (blocked completely)
    }
  }
}

function handleMouseUp(event) {
  const mouseUpTime = Date.now()
  const holdDuration = mouseUpTime - mouseDownTime

  const dx = event.clientX - mouseDownPos.x
  const dy = event.clientY - mouseDownPos.y
  const distance = Math.sqrt(dx * dx + dy * dy)

  if (holdDuration < 200 && distance < 5) {
    // Quick click - wake up pet if sleeping
    if (sleeping) {
      wakeUpPet()
    } else {
      // Play click animation if available, otherwise use clean
      if (props.animations.click) {
        setAnim('click', true)
      } else if (props.animations.clean) {
        setAnim('clean', true)
      } else {
        setAnim('idle')
      }
    }
  } else if (isDragging.value) {
    isDragging.value = false
    setAnim('idle')
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

      // Clamp to boundaries
      newX = Math.min(Math.max(0, newX), bounds.w - petSize)
      newY = Math.min(Math.max(0, newY), bounds.h - petSize)

      // Check collision and update position
      if (isPositionValid(newX, newY)) {
        pos.value.x = newX
        pos.value.y = newY
        lastValidPos.x = newX
        lastValidPos.y = newY

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
      }
    } else if (!props.manualControl) {
      // Autonomous AI behavior (only when manual control is disabled)
      // Check for nearby items - prioritize walking to food!
      const nearestItem = findNearestItem()
      if (nearestItem) {
        const targetX = nearestItem.x - petSize / 2
        const targetY = nearestItem.y - petSize / 2

        // Check if path to food is clear
        if (hasLineOfSight(pos.value.x, pos.value.y, targetX, targetY)) {
          dest.x = targetX
          dest.y = targetY
          idleUntil = 0  // Override any idle time to move immediately
        } else {
          // Path is blocked, choose new random destination instead
          chooseDest()
          idleUntil = now + (1000 + Math.random() * 2000)
        }
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

          // Clamp to boundaries
          newX = Math.min(Math.max(0, newX), bounds.w - petSize)
          newY = Math.min(Math.max(0, newY), bounds.h - petSize)

          // Check if new position is valid (not on solid tiles)
          if (isPositionValid(newX, newY)) {
            pos.value.x = newX
            pos.value.y = newY
            // Update last valid position during automatic movement
            lastValidPos.x = newX
            lastValidPos.y = newY

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
          } else {
            // Can't move to destination, choose new one
            chooseDest()
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
          // Stay on last frame if it's sit animation (last frame is idle)
          // Otherwise trigger random idle animation
          if (animKey === 'sit') {
            // Sit animation ended on idle frame, just stay there
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

  pos.value.x = Math.random() * 120 + 40
  pos.value.y = Math.random() * 80 + 40

  // Initialize last valid position
  lastValidPos.x = pos.value.x
  lastValidPos.y = pos.value.y

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
</style>
