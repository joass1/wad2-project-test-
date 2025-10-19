<script setup>
import { ref, watch, nextTick } from 'vue'

const props = defineProps({
  spriteUrl: { type: String, required: true },
  slice: { type: Number, default: 32 },
  scale: { type: Number, default: 2 },
  row: { type: Number, default: 0 },
  col: { type: Number, default: 0 }
})

const canvasRef = ref(null)

async function draw() {
  await nextTick()
  const c = canvasRef.value
  if (!c) return
  const ctx = c.getContext('2d', { alpha: true })
  const dpr = window.devicePixelRatio || 1
  c.width = props.slice * dpr
  c.height = props.slice * dpr
  c.style.width = `${props.slice * props.scale}px`
  c.style.height = `${props.slice * props.scale}px`
  ctx.imageSmoothingEnabled = false
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0)

  const img = new Image()
  img.src = props.spriteUrl
  await img.decode()

  const sx = props.col * props.slice
  const sy = props.row * props.slice
  ctx.clearRect(0, 0, props.slice, props.slice)
  ctx.drawImage(img, sx, sy, props.slice, props.slice, 0, 0, props.slice, props.slice)
}

watch(() => [props.spriteUrl, props.slice, props.row, props.col, props.scale], draw, { immediate: true })
</script>

<template>
  <canvas ref="canvasRef" class="preview"></canvas>
</template>

<style scoped>
.preview { image-rendering: pixelated; border-radius: 6px; display: block; }
</style>
