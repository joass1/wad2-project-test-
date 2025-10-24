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
import { ref, onMounted, onBeforeUnmount, computed, watch } from 'vue'
import { useGlobalPet } from '@/composables/useGlobalPet.js'

// Get global pet state
const { selectedPet } = useGlobalPet()

// Dynamic sprite configuration based on selected pet
const spriteConfig = computed(() => {
  const pet = selectedPet.value
  return {
    spriteUrl: pet.config.spriteUrl,
    slice: pet.config.slice,
    scale: pet.config.scale * 0.7, // Make global pet 30% smaller than pet page
    columns: 4, // Auto-detected from image
    animations: pet.config.animations
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
const DRAG_COEFFICIENT = 0.9 // air resistance
let isFalling = false
let isOnGround = false

// Walking behavior
let walkTarget = null
let walkCooldown = 0
const WALK_SPEED = 0.5

// Sleep behavior
let isSleeping = false
let sleepTimer = 0
const SLEEP_CHANCE = 0.4 // 40% chance to sleep when idle

// Scare behavior
let isScared = false
let scareTimer = 0

/* Helper functions */
let playingOnce = false
let nextOnceKey = null

function setAnim(key, once = false, queueNext = null) {
  if (!spriteConfig.value.animations[key]) {
    console.warn(`Animation ${key} not found, using idle`)
    key = 'idle'
  }

  // Only change if it's actually different
  if (animKey === key && !once) return

  animKey = key
  anim = spriteConfig.value.animations[key]
  frame = 0
  lastDrawnFrame = -1
  playingOnce = once && !anim.loop
  nextOnceKey = queueNext

  console.log(`🎬 Animation changed to: ${key}${once ? ' (one-shot)' : ''}`, anim)
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

  // Debug: Log frame drawing for walking animations
  if (animKey === 'move_right' || animKey === 'move_left') {
    console.log(`Drawing frame: ${frame}, col: ${safeCol}, row: ${anim.row}`)
  }

  ctx.save()

  // Clear only when actually redrawing
  ctx.clearRect(0, 0, s, s)

  // No flipping needed - sprites have directional animations

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
    // Pick a new target (only X coordinate for horizontal movement)
    const maxX = window.innerWidth - spriteConfig.value.slice * spriteConfig.value.scale
    walkTarget = {
      x: Math.random() * maxX,
      y: pos.value.y // Keep current Y position
    }
    walkCooldown = 0

    const distance = Math.abs(walkTarget.x - pos.value.x)

    if (distance > 10) {
      // Use walk animation for longer distances, sit (which transitions to idle) for closer
      if (animKey !== 'move_right' && animKey !== 'move_left') {
        setAnim('move_right')
      }
    }
  }

  if (walkTarget !== null) {
    const dx = walkTarget.x - pos.value.x
    const distance = Math.abs(dx)

    if (distance < 5) {
      // Reached target
      walkTarget = null
      walkCooldown = 2 + Math.random() * 5  // Wait 2-7 seconds
      // Play sit animation (which transitions to idle), or occasionally clean
      setAnim(Math.random() < 0.2 ? 'clean' : 'sit', true)
    } else {
      // Move towards target - only horizontal movement
      const moveAmountX = Math.sign(dx) * Math.min(WALK_SPEED, Math.abs(dx))
      pos.value.x += moveAmountX
      // Y position stays the same

      // Use only horizontal animations
      if (dx > 0) {
        // Moving right
        if (animKey !== 'move_right') setAnim('move_right')
      } else {
        // Moving left
        if (animKey !== 'move_left') setAnim('move_left')
      }
    }
  }
  // Removed the else block that was constantly trying to set idle animations
}

function goToSleep() {
  isSleeping = true
  // Play falling asleep animation, then transition to sleep_loop
  setAnim('sleep', true, 'sleep_loop')
  console.log('Pet is falling asleep...')

  // Auto-wake after 10 seconds
  sleepTimer = window.setTimeout(() => {
    if (isSleeping) {
      wakeUp()
    }
  }, 10000)
}

function wakeUp() {
  isSleeping = false

  // Clear sleep timer if it exists
  if (sleepTimer) {
    window.clearTimeout(sleepTimer)
    sleepTimer = 0
  }

  // Play wake animation, then return to idle
  setAnim('wake', true)
  walkCooldown = 1 + Math.random() * 2
  console.log('Pet is waking up!')
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

  console.log('Pet got scared!')

  // Recover after 1 second
  setTimeout(() => {
    isScared = false
    setAnim('idle')
  }, 1000)
}

/* Main loop */
function loop(t) {
  rafId = requestAnimationFrame(loop)

  if (!last) last = t
  const dt = (t - last) / 1000
  last = t
  acc += dt

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
          // One-shot animation finished
          if (nextOnceKey) {
            const nxt = nextOnceKey
            nextOnceKey = null
            setAnim(nxt, true)
          } else if (playingOnce) {
            playingOnce = false
            setAnim('idle')
          } else {
            frame = seqLen - 1
          }
        }
      }
    }
    
    // Debug: Log animation state for walking animations
    if (animKey === 'move_right' || animKey === 'move_left') {
      console.log(`Walking animation: ${animKey}, frame: ${frame}, fps: ${anim.fps}, loop: ${anim.loop}`)
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

// Function to initialize pet
async function initializePet() {
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

    console.log(`Canvas size: ${c.width}x${c.height}, display: ${c.style.width}x${c.style.height}`)

    ctx = c.getContext('2d')
    ctx.imageSmoothingEnabled = false
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0)

    // Load sprite sheet
    console.log(`Loading sprite sheet from: ${spriteConfig.value.spriteUrl}`)
    img = new Image()
    img.src = spriteConfig.value.spriteUrl

    img.onerror = () => {
      console.error(`Failed to load sprite sheet: ${spriteConfig.value.spriteUrl}`)
    }

    await img.decode()

    // Auto-detect columns
    sheetCols = Math.max(1, Math.floor(img.naturalWidth / slice))
    console.log(`Sprite sheet loaded: ${img.naturalWidth}x${img.naturalHeight}px, ${sheetCols} columns`)

    // Set initial position
    pos.value.x = Math.random() * (window.innerWidth - slice * scale)
    pos.value.y = 100

    console.log(`Initial position: ${pos.value.x}, ${pos.value.y}`)

    setAnim('idle')
    rafId = requestAnimationFrame(loop)

    console.log('Pet initialized successfully!')
  } catch (error) {
    console.error('Error initializing GlobalDesktopPet:', error)
  }
}

// Watch for changes in sprite configuration
watch(spriteConfig, async (newConfig, oldConfig) => {
  if (newConfig.spriteUrl !== oldConfig?.spriteUrl) {
    console.log('Pet sprite changed, reinitializing...')
    await initializePet()
  }
}, { deep: true })

/* Lifecycle */
onMounted(async () => {
  await initializePet()
})

onBeforeUnmount(() => {
  cancelAnimationFrame(rafId)
  document.removeEventListener('mousemove', handleMouseMove)
  document.removeEventListener('mouseup', handleMouseUp)
  if (sleepTimer) {
    window.clearTimeout(sleepTimer)
  }
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
