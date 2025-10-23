<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'

const props = defineProps({
  spriteUrl: { type: String, default: 'cat-spritesheet.png' },
  slice: { type: Number, default: 32 },          // size of one cell/frame
  columns: { type: Number, default: 12 },        // fallback; we auto-detect from image
  scale: { type: Number, default: 8 },           // BIGGER pet (was 6)
  speed: { type: Number, default: 70 },
  animations: {
    type: Object,
    default: () => ({
      idle:   { row: 0, frames: 8, fps: 6,  loop: true,  colStart: 0 },
      move:   { row: 4, frames: 8, fps: 10, loop: true,  colStart: 0 },
      sleep:  { row: 6, frames: 6, fps: 5,  loop: true,  colStart: 0 },
      click:  { row: 3, frames: 4, fps: 8,  loop: false, colStart: 0 }
    })
  },
  droppedItems: { type: Array, default: () => [] }  // Items dropped on the background
})

const emit = defineEmits(['item-eaten'])

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
let dir = 1               // 1=right, -1=left
let sheetCols = props.columns
let randomEvt = 0
let sleeping = false      // sticky sleep flag
let eatingItemId = null   // Track which item is being eaten to prevent duplicate emissions

// Physics state
let velocity = { x: 0, y: 0 }
const GRAVITY = 0.8
const TERMINAL_VELOCITY = 15
const DRAG_COEFFICIENT = 0.95
let isFalling = false
let isOnGround = false

// Drag state
const isDragging = ref(false)
let dragOffset = { x: 0, y: 0 }
let mouseDownTime = 0
let mouseDownPos = { x: 0, y: 0 }

/* Helpers */
function setAnim(key, once = false, queueNext = null) {
  // For Stardew pets (identified by having a 'click' animation), only allow
  // side-to-side animations (no forward/backward variants)
  if (props.animations.click) {
    const allowed = ['idle', 'move', 'sleep', 'click', 'falling', 'grabbed']
    if (!allowed.includes(key)) {
      key = 'idle' // fallback to idle for any disallowed animation
    }
  }

  if (!props.animations[key]) return
  animKey = key
  anim = props.animations[key]
  frame = 0
  playingOnce = once && !anim.loop
  nextOnceKey = queueNext

  // sticky sleep -> freeze movement until click
  if (key === 'sleep') {
    sleeping = true
    idleUntil = Number.POSITIVE_INFINITY
  }
}

function randomIdleAnim() {
  // Stardew pets: only simple idles; Original cat: richer set
  if (props.animations.click) {
    // Stardew sprites: stick to simple idle or sleep
    const pool = Math.random() < 0.3 ? ['sleep'] : ['idle']
    setAnim(pool[Math.floor(Math.random() * pool.length)])
  } else {
    // Original cat keeps richer ambient idles
    const pool = Math.random() < 0.35
      ? ['sleep']
      : ['idle', 'idle2', 'clean', 'clean2']
    setAnim(pool[Math.floor(Math.random() * pool.length)])
  }
}

function chooseDest() {
  const pad = 24
  dest.x = pad + Math.random() * Math.max(0, bounds.w - props.slice * props.scale - pad * 2)
  dest.y = pad + Math.random() * Math.max(0, bounds.h - props.slice * props.scale - pad * 2)
}

/* Apply physics to dropped items */
function applyItemPhysics() {
  if (!props.droppedItems || props.droppedItems.length === 0) return

  const ITEM_GRAVITY = 0.8
  const ITEM_SIZE = 40

  for (const item of props.droppedItems) {
    if (item.isOnGround) continue

    // Apply gravity
    item.velocityY = item.velocityY || 0
    item.velocityY += ITEM_GRAVITY

    // Update position
    item.y += item.velocityY

    // Find ground below item using same logic as pet
    const groundY = findGroundBelowItem(item.x, ITEM_SIZE)

    // Check if item hit the ground
    if (item.y >= groundY) {
      item.y = groundY
      item.velocityY = 0
      item.isOnGround = true
    }
  }
}

/* Find ground level for dropped items */
function findGroundBelowItem(itemX, itemSize) {
  if (!parent) return bounds.h - itemSize

  const allElements = parent.querySelectorAll('*')
  const itemLeft = itemX - itemSize / 2
  const itemRight = itemX + itemSize / 2

  let closestGround = bounds.h - itemSize

  for (const el of allElements) {
    if (el === actor.value || actor.value?.contains(el)) continue

    const computedStyle = window.getComputedStyle(el)
    const hasBorder = parseFloat(computedStyle.borderWidth) > 0 ||
                     parseFloat(computedStyle.borderTopWidth) > 0

    if (!hasBorder) continue

    const parentRect = parent.getBoundingClientRect()
    const rect = el.getBoundingClientRect()

    const relativeTop = rect.top - parentRect.top
    const relativeLeft = rect.left - parentRect.left
    const relativeRight = relativeLeft + rect.width

    const horizontalOverlap = itemRight > relativeLeft && itemLeft < relativeRight

    if (horizontalOverlap && relativeTop > 0) {
      const groundY = relativeTop - itemSize
      if (groundY < closestGround && groundY >= 0) {
        closestGround = groundY
      }
    }
  }

  return closestGround
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
    // Only check collision with items that have landed
    if (!item.isOnGround) continue

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

        // Wake up and become happy
        sleeping = false
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
    // Only pathfind to items that have landed on the ground
    if (!item.isOnGround) continue

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

/* Physics - works within container bounds */
function findGroundBelow() {
  if (!parent) return bounds.h

  const allElements = parent.querySelectorAll('*')
  const petBottom = pos.value.y + props.slice * props.scale
  const petLeft = pos.value.x
  const petRight = pos.value.x + props.slice * props.scale

  let closestGround = bounds.h - props.slice * props.scale

  for (const el of allElements) {
    if (el === actor.value || actor.value?.contains(el)) continue

    const computedStyle = window.getComputedStyle(el)
    const hasBorder = parseFloat(computedStyle.borderWidth) > 0 ||
                     parseFloat(computedStyle.borderTopWidth) > 0

    if (!hasBorder) continue

    const parentRect = parent.getBoundingClientRect()
    const rect = el.getBoundingClientRect()

    // Convert to parent-relative coordinates
    const relativeTop = rect.top - parentRect.top
    const relativeLeft = rect.left - parentRect.left
    const relativeRight = relativeLeft + rect.width

    const horizontalOverlap = petRight > relativeLeft && petLeft < relativeRight

    if (horizontalOverlap && relativeTop > petBottom - 20) {
      const groundY = relativeTop - props.slice * props.scale
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

  if (Math.abs(petBottom - groundY) < 3) {
    isOnGround = true
    isFalling = false
    pos.value.y = groundY
    velocity.y = 0

    if (animKey === 'falling') {
      setAnim('idle')
    }
  } else if (petBottom < groundY) {
    isOnGround = false
    isFalling = true

    if (animKey !== 'falling' && animKey !== 'grabbed') {
      setAnim('falling')
    }

    velocity.y += GRAVITY
    velocity.y = Math.min(velocity.y, TERMINAL_VELOCITY)
    velocity.y *= DRAG_COEFFICIENT

    pos.value.y += velocity.y

    if (pos.value.y > groundY) {
      pos.value.y = groundY
      velocity.y = 0
    }
  }

  // Keep within container bounds
  const maxX = bounds.w - props.slice * props.scale
  pos.value.x = Math.max(0, Math.min(maxX, pos.value.x))
}

function scheduleRandomEvent() {
  // Stardew Valley pets sleep every minute, original cat has random events
  const ms = props.animations.click ? 60000 : (10000 + Math.random() * 20000) // 1min for Stardew, 10-30s for original
  randomEvt = window.setTimeout(() => {
    if (props.animations.click) {
      // Stardew Valley pets: sleep every minute
      if (!sleeping && !playingOnce) {
        setAnim('sleep')
        sleeping = true
        idleUntil = Number.POSITIVE_INFINITY // Stay asleep until clicked
      }
    } else {
      // Original cat: random events
      if (!sleeping && !playingOnce && ['idle','idle2','clean','clean2'].includes(animKey)) {
        setAnim(Math.random() < 0.5 ? 'scared' : 'jump', true)
      }
    }
    scheduleRandomEvent()
  }, ms)
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
      setAnim('grabbed')
      sleeping = false // wake up if sleeping
    }

    const parentRect = parent.getBoundingClientRect()
    const petSize = props.slice * props.scale

    // Calculate new position
    let newX = event.clientX - parentRect.left - dragOffset.x
    let newY = event.clientY - parentRect.top - dragOffset.y

    // Clamp to boundaries
    newX = Math.max(0, Math.min(newX, bounds.w - petSize))
    newY = Math.max(0, Math.min(newY, bounds.h - petSize))

    pos.value.x = newX
    pos.value.y = newY
  }
}

function handleMouseUp(event) {
  const mouseUpTime = Date.now()
  const holdDuration = mouseUpTime - mouseDownTime

  const dx = event.clientX - mouseDownPos.x
  const dy = event.clientY - mouseDownPos.y
  const distance = Math.sqrt(dx * dx + dy * dy)

  if (holdDuration < 200 && distance < 5) {
    // Quick click - use appropriate animation based on pet type
    if (sleeping) {
      sleeping = false
      idleUntil = 0
    }
    
    // Check if this is a Stardew Valley pet (has click animation) or original cat
    if (props.animations.click) {
      // Stardew Valley pets: use flat animation for click
      setAnim('click', true)
    } else {
      setAnim('scared', true, 'jump')
    }
  } else if (isDragging.value) {
    isDragging.value = false

    const groundY = findGroundBelow()
    if (pos.value.y < groundY - 5) {
      setAnim('falling')
      isFalling = true
    } else {
      setAnim('idle')
      idleUntil = performance.now() + (1000 + Math.random() * 2000)
    }
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

  // Apply physics first
  applyPhysics()

  // Apply physics to dropped items
  applyItemPhysics()

  // Check for item collision
  checkItemCollision()

  // movement only when not sticky sleeping, not dragging, and on ground
  if (!sleeping && !isDragging.value && isOnGround && !isFalling) {
    const now = performance.now()
    const w = props.slice * props.scale

    // Check for nearby items - prioritize walking to food!
    const nearestItem = findNearestItem()
    if (nearestItem) {
      // Set destination to the nearest item
      dest.x = nearestItem.x - (props.slice * props.scale) / 2
      dest.y = nearestItem.y - (props.slice * props.scale) / 2
      idleUntil = 0  // Override any idle time to move immediately
    }

    if (now >= idleUntil) {
      const dx = dest.x - pos.value.x
      const dist = Math.abs(dx)

      if (dist < 2) {
        // Reached destination
        if (!nearestItem) {
          // No item nearby, choose random destination
          idleUntil = now + (3000 + Math.random() * 7000)
          randomIdleAnim()
          chooseDest()
        }
      } else {
        // walk horizontally (Y controlled by physics)
        const vx = (dx / dist) * props.speed
        const newX = pos.value.x + vx * dt
        const clampedX = Math.min(Math.max(0, newX), bounds.w - w)

        // Check if we hit a boundary and change direction
        if (clampedX !== newX) {
          // Hit left or right edge, choose new destination in opposite direction
          chooseDest()
          return
        }

        pos.value.x = clampedX
        dir = vx >= 0 ? 1 : -1

        // more frequent loitering: around 12% chance per second to pause 2–5s (but not if chasing food!)
        if (!nearestItem && Math.random() < 0.12 * dt) {
          idleUntil = now + (2000 + Math.random() * 3000)
          randomIdleAnim()
        }

        if (!playingOnce && animKey !== 'move') {
          // Stardew pets always use 'move'; original cat can alternate
          if (props.animations.click) {
            setAnim('move')
          } else {
            setAnim(Math.random() < 0.7 ? 'move' : 'move2')
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
          // if it ended while sleeping, remain asleep; else mellow out
          if (!sleeping) randomIdleAnim()
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
  if (dir === -1) {
    ctx.translate(s, 0)
    ctx.scale(-1, 1)
  }
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

  chooseDest()
  setAnim('idle')
  idleUntil = 0

  scheduleRandomEvent()
  rafId = requestAnimationFrame(loop)
  c.addEventListener('mousedown', handleMouseDown)

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
