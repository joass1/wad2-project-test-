<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'

const props = defineProps({
  scale: { type: Number, default: 3 },  // Scale for the coin size
  speed: { type: Number, default: 8 }   // Animation speed (fps)
})

// Spritesheet configuration for 01PixelCoinGold.png
// 2 rows: first row has 4 columns, second row has 2 columns = 6 total frames
const SPRITE_SIZE = 16  // Assuming 16x16 pixel sprites
const FRAMES = 6
const COLS_ROW1 = 4
const COLS_ROW2 = 2

const canvasRef = ref(null)
let ctx, img, rafId
let frame = 0
let acc = 0, last = 0

function drawFrame() {
  if (!ctx || !img) return

  const s = SPRITE_SIZE
  let sx, sy

  // Calculate source position based on frame
  if (frame < COLS_ROW1) {
    // First row (frames 0-3)
    sx = frame * s
    sy = 0
  } else {
    // Second row (frames 4-5)
    sx = (frame - COLS_ROW1) * s
    sy = s
  }

  ctx.clearRect(0, 0, s, s)
  ctx.drawImage(img, sx, sy, s, s, 0, 0, s, s)
}

function loop(t) {
  rafId = requestAnimationFrame(loop)
  if (!last) last = t
  const dt = (t - last) / 1000
  last = t
  acc += dt

  const frameDur = 1 / props.speed
  while (acc >= frameDur) {
    acc -= frameDur
    frame = (frame + 1) % FRAMES
  }

  drawFrame()
}

onMounted(async () => {
  const c = canvasRef.value
  const dpr = window.devicePixelRatio || 1
  c.width = SPRITE_SIZE * dpr
  c.height = SPRITE_SIZE * dpr
  c.style.width = `${SPRITE_SIZE * props.scale}px`
  c.style.height = `${SPRITE_SIZE * props.scale}px`
  ctx = c.getContext('2d')
  ctx.imageSmoothingEnabled = false
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0)

  img = new Image()
  img.src = '/01PixelCoinGold.png'
  await img.decode()

  rafId = requestAnimationFrame(loop)
})

onBeforeUnmount(() => {
  cancelAnimationFrame(rafId)
})
</script>

<template>
  <canvas ref="canvasRef" class="coin-canvas" />
</template>

<style scoped>
.coin-canvas {
  image-rendering: pixelated;
  display: block;
}
</style>
