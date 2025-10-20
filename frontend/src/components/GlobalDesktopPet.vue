<template>
  <div
    v-if="showPet"
    ref="actor"
    class="global-pet"
    :style="{
      left: pos.x + 'px',
      top: pos.y + 'px',
      cursor: isDragging ? 'grabbing' : 'grab'
    }"
    @mousedown="handleMouseDown"
  >
    <canvas ref="canvasRef" class="pet-canvas" />
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'

// Removed backend dependencies - fully frontend pet system

// Sprite sheet configuration - customizable via props or config
const spriteConfig = ref({
  spriteUrl: '/cat-spritesheet.png',
  slice: 32,           // Size of one sprite cell
  scale: 3,            // Display scale
  columns: 12,         // Auto-detected from image

  // Sprite extraction configuration - specify row and column ranges
  animations: {
    idle:     { row: 0, frames: 8, fps: 10,  loop: true,  colStart: 0 },
    idle2:    { row: 1, frames: 8, fps: 10,  loop: true,  colStart: 0 },
    clean:    { row: 2, frames: 8, fps: 8,  loop: true,  colStart: 0 },
    walk:     { row: 4, frames: 8, fps: 8, loop: true,  colStart: 0 },
    walk2:    { row: 5, frames: 8, fps: 8, loop: true,  colStart: 0 },
    sleep:    { row: 6, frames: 6, fps: 8,  loop: true,  colStart: 0 },
    grabbed:  { row: 7, frames: 6, fps: 8,  loop: true,  colStart: 0 },  // Paw animation when grabbed
    jump:     { row: 8, frames: 8, fps: 12, loop: false, colStart: 0 },
    falling:  { row: 9 , frames: 8, fps: 8, loop: true,  colStart: 0 },  // Scared animation when falling
    scared:   { row: 9, frames: 8, fps: 10, loop: false, colStart: 0 }
  }
})

/* Refs / state */
const showPet = ref(true)
const actor = ref(null)
const canvasRef = ref(null)
let ctx, img, rafId

// Animation state
let frame = 0
let animKey = 'idle'
let anim
let acc = 0, last = 0
let dir = 1  // 1=right, -1=left
let sheetCols = spriteConfig.value.columns

// Position and movement
const pos = ref({ x: 100, y: 100 })
let velocity = { x: 0, y: 0 }

// Drag state
const isDragging = ref(false)
let dragOffset = { x: 0, y: 0 }

// Physics state
const GRAVITY = 0.8          // pixels per frame^2
const TERMINAL_VELOCITY = 15  // max falling speed
const DRAG_COEFFICIENT = 0.95 // air resistance
let isFalling = false
let isOnGround = false

// Walking behavior
let walkTarget = null
let walkCooldown = 0
const WALK_SPEED = 1

// Sleep behavior
let isSleeping = false
let sleepTimer = 0
const SLEEP_CHECK_INTERVAL = 15000 // Check every 15 seconds if should sleep
const SLEEP_CHANCE = 0.6 // 60% chance to sleep when idle
const SLEEP_DURATION = 8000 // Sleep for 8 seconds

// Scare behavior
let isScared = false
let scareTimer = 0

/* Helper functions */
function setAnim(key) {
  if (!spriteConfig.value.animations[key]) {
    console.warn(` Animation ${key} not found, using idle`)
    key = 'idle'
  }

  // Only change if it's actually different
  if (animKey === key) return

  animKey = key
  anim = spriteConfig.value.animations[key]
  frame = 0
  lastDrawnFrame = -1  // Add this line to force redraw on animation change

  console.log(`🎬 Animation changed to: ${key}`)
}

function getSeqLength(a) {
  const start = a.colStart ?? 0
  return Math.max(1, Math.min(a.frames ?? 1, sheetCols - start))
}

function getSourceCol(a, f) {
  const start = a.colStart ?? 0
  const len = getSeqLength(a)
  return start + (f % len)
}

// Add this at the top with other state variables
let lastDrawnFrame = -1

function drawFrame() {
  if (!ctx || !img || !anim) return

  // Only redraw if the frame has changed
  if (frame === lastDrawnFrame) return
  lastDrawnFrame = frame

  const s = spriteConfig.value.slice
  const colIndex = getSourceCol(anim, frame)
  const safeCol = Math.max(0, Math.min(colIndex, sheetCols - 1))
  const sx = safeCol * s
  const sy = anim.row * s

  ctx.save()
  
  // Clear only when actually redrawing
  ctx.clearRect(0, 0, s, s)

  // Flip horizontally based on direction
  if (dir === -1) {
    ctx.translate(s, 0)
    ctx.scale(-1, 1)
  }

  // Draw the sprite
  ctx.drawImage(img, sx, sy, s, s, 0, 0, s, s)
  ctx.restore()
}

/* Physics and collision detection */
function findGroundBelow() {
  // Get all elements with borders in the viewport
  const allElements = document.querySelectorAll('*')
  const petBottom = pos.value.y + spriteConfig.value.slice * spriteConfig.value.scale
  const petLeft = pos.value.x
  const petRight = pos.value.x + spriteConfig.value.slice * spriteConfig.value.scale

  let closestGround = window.innerHeight - spriteConfig.value.slice * spriteConfig.value.scale

  for (const el of allElements) {
    // Skip the pet itself
    if (el === actor.value || actor.value?.contains(el)) continue

    const computedStyle = window.getComputedStyle(el)
    const hasBorder = parseFloat(computedStyle.borderWidth) > 0 ||
                     parseFloat(computedStyle.borderTopWidth) > 0

    if (!hasBorder) continue

    const rect = el.getBoundingClientRect()

    // Check if pet is above this element and horizontally aligned
    const horizontalOverlap = petRight > rect.left && petLeft < rect.right

    if (horizontalOverlap && rect.top > petBottom - 20) {
      const groundY = rect.top - spriteConfig.value.slice * spriteConfig.value.scale
      if (groundY < closestGround && groundY >= pos.value.y - 5) {
        closestGround = groundY
      }
    }
  }

  return closestGround
}

function applyPhysics() {
  if (isDragging.value) {
    velocity.y = 0
    velocity.x = 0
    isFalling = false
    return
  }

  const groundY = findGroundBelow()
  const petBottom = pos.value.y

  // Check if on ground
  if (Math.abs(petBottom - groundY) < 3) {
    isOnGround = true
    isFalling = false
    pos.value.y = groundY
    velocity.y = 0

    // Landing animation
    if (animKey === 'falling') {
      setAnim('idle')
    }
  } else if (petBottom < groundY) {
    // In the air - apply gravity
    isOnGround = false
    isFalling = true

    if (animKey !== 'falling' && animKey !== 'grabbed') {
      setAnim('falling')
    }

    velocity.y += GRAVITY
    velocity.y = Math.min(velocity.y, TERMINAL_VELOCITY)
    velocity.y *= DRAG_COEFFICIENT  // Air resistance for slow fall

    pos.value.y += velocity.y

    // Don't fall through ground
    if (pos.value.y > groundY) {
      pos.value.y = groundY
      velocity.y = 0
    }
  }

  // Keep on screen horizontally
  const maxX = window.innerWidth - spriteConfig.value.slice * spriteConfig.value.scale
  pos.value.x = Math.max(0, Math.min(maxX, pos.value.x))
}

function updateWalking(dt) {
  if (isDragging.value || isFalling || !isOnGround || isSleeping || isScared) return

  walkCooldown -= dt

  // Check if should fall asleep (when idle and on ground)
  if (walkTarget === null && walkCooldown > 0 && Math.random() < SLEEP_CHANCE * dt / 5) {
    goToSleep()
    return
  }

  if (walkTarget === null && walkCooldown <= 0) {
    // Pick a new target
    const maxX = window.innerWidth - spriteConfig.value.slice * spriteConfig.value.scale
    walkTarget = Math.random() * maxX
    walkCooldown = 0

    if (Math.abs(walkTarget - pos.value.x) > 10) {
      setAnim(Math.random() < 0.5 ? 'walk' : 'walk2')
    }
  }

  if (walkTarget !== null) {
    const dx = walkTarget - pos.value.x

    if (Math.abs(dx) < 5) {
      // Reached target
      walkTarget = null
      walkCooldown = 2 + Math.random() * 5  // Wait 2-7 seconds
      setAnim(Math.random() < 0.3 ? 'clean' : 'idle')
    } else {
      // Move towards target - KEEP WALKING ANIMATION
      const moveAmount = Math.sign(dx) * Math.min(WALK_SPEED, Math.abs(dx))
      pos.value.x += moveAmount
      dir = dx > 0 ? 1 : -1

      // Ensure walk animation is active while moving
      if (animKey !== 'walk' && animKey !== 'walk2') {
        setAnim(Math.random() < 0.5 ? 'walk' : 'walk2')
      }
    }
  }
  // Removed the else block that was constantly trying to set idle animations
}

function goToSleep() {
  isSleeping = true
  sleepTimer = 0
  setAnim('sleep')
  console.log('😴 Pet is sleeping...')
}

function wakeUp() {
  isSleeping = false
  sleepTimer = 0
  setAnim('idle')
  walkCooldown = 1 + Math.random() * 2
  console.log('👀 Pet woke up!')
}

function getScarred() {
  if (isSleeping) {
    wakeUp()
  }

  isScared = true
  scareTimer = 0
  setAnim('scared')

  // Run away in random direction
  const maxX = window.innerWidth - spriteConfig.value.slice * spriteConfig.value.scale
  walkTarget = Math.random() < 0.5 ? 0 : maxX

  console.log('😱 Pet got scared!')

  // Recover after 1 second
  setTimeout(() => {
    isScared = false
    setAnim(Math.random() < 0.5 ? 'walk' : 'walk2')
  }, 1000)
}

/* Main loop */
function loop(t) {
  rafId = requestAnimationFrame(loop)

  if (!last) last = t
  const dt = (t - last) / 1000
  last = t
  acc += dt

  // Update sleep timer
  if (isSleeping) {
    sleepTimer += dt * 1000 // Convert to milliseconds
    if (sleepTimer >= SLEEP_DURATION) {
      wakeUp()
    }
  }

  // Apply physics
  applyPhysics()

  // Update walking behavior
  if (!isDragging.value) {
    updateWalking(dt)
  }

  // Frame stepping
  if (anim) {
    const frameDur = 1 / anim.fps
    while (acc >= frameDur) {
      acc -= frameDur
      frame++
      const seqLen = getSeqLength(anim)
      if (frame >= seqLen) {
        if (anim.loop) {
          frame = 0
        } else {
          frame = seqLen - 1
        }
      }
    }
  }

  drawFrame()
}

/* Mouse handlers - Click to scare, drag to move */
let mouseDownTime = 0
let mouseDownPos = { x: 0, y: 0 }

const handleMouseDown = (event) => {
  event.preventDefault()
  event.stopPropagation()

  mouseDownTime = Date.now()
  mouseDownPos = { x: event.clientX, y: event.clientY }

  dragOffset.x = event.clientX - pos.value.x
  dragOffset.y = event.clientY - pos.value.y

  document.addEventListener('mousemove', handleMouseMove, { passive: false })
  document.addEventListener('mouseup', handleMouseUp)
}

const handleMouseMove = (event) => {
  event.preventDefault()

  // Check if mouse moved enough to be considered a drag (more than 5px)
  const dx = event.clientX - mouseDownPos.x
  const dy = event.clientY - mouseDownPos.y
  const distance = Math.sqrt(dx * dx + dy * dy)

  if (distance > 5) {
    // It's a drag, not a click
    if (!isDragging.value) {
      isDragging.value = true
      setAnim('grabbed')
    }

    pos.value.x = event.clientX - dragOffset.x
    pos.value.y = event.clientY - dragOffset.y
  }
}

const handleMouseUp = (event) => {
  const mouseUpTime = Date.now()
  const holdDuration = mouseUpTime - mouseDownTime

  // Calculate mouse movement
  const dx = event.clientX - mouseDownPos.x
  const dy = event.clientY - mouseDownPos.y
  const distance = Math.sqrt(dx * dx + dy * dy)

  // If it was a quick click (less than 200ms and less than 5px movement)
  if (holdDuration < 200 && distance < 5) {
    // Quick click - scare the pet!
    getScarred()
  } else if (isDragging.value) {
    // It was a drag - handle drop
    isDragging.value = false

    // Check if should fall
    const groundY = findGroundBelow()
    if (pos.value.y < groundY - 5) {
      setAnim('falling')
      isFalling = true
    } else {
      setAnim('idle')
      walkTarget = null
      walkCooldown = 1 + Math.random() * 3
    }
  }

  document.removeEventListener('mousemove', handleMouseMove)
  document.removeEventListener('mouseup', handleMouseUp)
}

/* Lifecycle */
onMounted(async () => {
  try {
    

    // Setup canvas
    const c = canvasRef.value
    if (!c) {
      console.error('Canvas ref not found!')
      return
    }

    const dpr = window.devicePixelRatio || 1
    const slice = spriteConfig.value.slice
    const scale = spriteConfig.value.scale

    c.width = slice * dpr
    c.height = slice * dpr
    c.style.width = `${slice * scale}px`
    c.style.height = `${slice * scale}px`

    console.log(`�� Canvas size: ${c.width}x${c.height}, display: ${c.style.width}x${c.style.height}`)

    ctx = c.getContext('2d')
    ctx.imageSmoothingEnabled = false
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0)

    // Load sprite sheet
    console.log(`📥 Loading sprite sheet from: ${spriteConfig.value.spriteUrl}`)
    img = new Image()
    img.src = spriteConfig.value.spriteUrl

    img.onerror = () => {
      console.error(`❌ Failed to load sprite sheet: ${spriteConfig.value.spriteUrl}`)
    }

    await img.decode()

    // Auto-detect columns
    sheetCols = Math.max(1, Math.floor(img.naturalWidth / slice))
    console.log(`✅ Sprite sheet loaded: ${img.naturalWidth}x${img.naturalHeight}px, ${sheetCols} columns`)

    // Set initial position
    pos.value.x = Math.random() * (window.innerWidth - slice * scale)
    pos.value.y = 100

    console.log(`📍 Initial position: ${pos.value.x}, ${pos.value.y}`)

    setAnim('idle')
    rafId = requestAnimationFrame(loop)

    console.log('✅ Pet initialized successfully!')
  } catch (error) {
    console.error('❌ Error initializing GlobalDesktopPet:', error)
  }
})

onBeforeUnmount(() => {
  cancelAnimationFrame(rafId)
  document.removeEventListener('mousemove', handleMouseMove)
  document.removeEventListener('mouseup', handleMouseUp)
})
</script>

<style scoped>
.global-pet {
  position: fixed;
  z-index: 9999;
  pointer-events: auto;
  user-select: none;
  -webkit-user-select: none;
  will-change: transform;
}

.pet-canvas {
  image-rendering: pixelated;
  image-rendering: -moz-crisp-edges;
  image-rendering: crisp-edges;
  display: block;
  border-radius: 6px;
  pointer-events: none;
}
</style>
