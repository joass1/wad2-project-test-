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
      idle2:  { row: 1, frames: 8, fps: 6,  loop: true,  colStart: 0 },
      clean:  { row: 2, frames: 8, fps: 8,  loop: true,  colStart: 0 },
      clean2: { row: 3, frames: 8, fps: 8,  loop: true,  colStart: 0 },
      move:   { row: 4, frames: 8, fps: 10, loop: true,  colStart: 0 },
      move2:  { row: 5, frames: 8, fps: 10, loop: true,  colStart: 0 },
      sleep:   { row: 6, frames: 6, fps: 5,  loop: true,  colStart: 0 },
      paw:     { row: 7, frames: 6, fps: 10, loop: false, colStart: 0 },
      grabbed: { row: 7, frames: 6, fps: 8,  loop: true,  colStart: 0 },
      jump:    { row: 8, frames: 8, fps: 12, loop: false, colStart: 0 },
      scared:  { row: 9, frames: 8, fps: 10, loop: false, colStart: 0 },
      falling: { row: 9, frames: 8, fps: 8,  loop: true,  colStart: 0 }
    })
  }
})

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
  // Favor longer calm states; sometimes fall asleep
  const pool = Math.random() < 0.35
    ? ['sleep']                                  // 35% chance to snooze
    : ['idle', 'idle2', 'clean', 'clean2']       // otherwise mild idles
  setAnim(pool[Math.floor(Math.random() * pool.length)])
}

function chooseDest() {
  const pad = 24
  dest.x = pad + Math.random() * Math.max(0, bounds.w - props.slice * props.scale - pad * 2)
  dest.y = pad + Math.random() * Math.max(0, bounds.h - props.slice * props.scale - pad * 2)
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
  const ms = 10000 + Math.random() * 20000 // 10–30s
  randomEvt = window.setTimeout(() => {
    // no ambient events while sleeping or during one-shots
    if (!sleeping && !playingOnce && ['idle','idle2','clean','clean2'].includes(animKey)) {
      // tiny surprise even when idle
      setAnim(Math.random() < 0.5 ? 'scared' : 'jump', true)
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
    pos.value.x = event.clientX - parentRect.left - dragOffset.x
    pos.value.y = event.clientY - parentRect.top - dragOffset.y
  }
}

function handleMouseUp(event) {
  const mouseUpTime = Date.now()
  const holdDuration = mouseUpTime - mouseDownTime

  const dx = event.clientX - mouseDownPos.x
  const dy = event.clientY - mouseDownPos.y
  const distance = Math.sqrt(dx * dx + dy * dy)

  if (holdDuration < 200 && distance < 5) {
    // Quick click - wake or scare
    if (sleeping) {
      sleeping = false
      idleUntil = 0
      setAnim('scared', true, 'jump')
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

  // movement only when not sticky sleeping, not dragging, and on ground
  if (!sleeping && !isDragging.value && isOnGround && !isFalling) {
    const now = performance.now()
    const w = props.slice * props.scale

    if (now >= idleUntil) {
      const dx = dest.x - pos.value.x
      const dist = Math.abs(dx)

      if (dist < 2) {
        // Longer idle: 3–10s, then pick a new target
        idleUntil = now + (3000 + Math.random() * 7000)
        randomIdleAnim()
        chooseDest()
      } else {
        // walk horizontally (Y controlled by physics)
        const vx = (dx / dist) * props.speed
        pos.value.x = Math.min(Math.max(0, pos.value.x + vx * dt), bounds.w - w)
        dir = vx >= 0 ? 1 : -1

        // more frequent loitering: around 12% chance per second to pause 2–5s
        if (Math.random() < 0.12 * dt) {
          idleUntil = now + (2000 + Math.random() * 3000)
          randomIdleAnim()
        }

        if (!playingOnce && (animKey !== 'move' && animKey !== 'move2')) {
          setAnim(Math.random() < 0.7 ? 'move' : 'move2')
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
})

onBeforeUnmount(() => {
  cancelAnimationFrame(rafId)
  window.removeEventListener('resize', measure)
  canvasRef.value?.removeEventListener('mousedown', handleMouseDown)
  document.removeEventListener('mousemove', handleMouseMove)
  document.removeEventListener('mouseup', handleMouseUp)
  window.clearTimeout(randomEvt)
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
