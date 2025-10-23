<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'

const props = defineProps({
  mapData: {
    type: Object,
    required: true
  },
  tileSize: {
    type: Number,
    default: 32 // Base tile size in pixels
  },
  scale: {
    type: Number,
    default: 6 // Scale factor for pixel art
  }
})

const emit = defineEmits(['collision-map-ready'])

const container = ref(null)
const canvasRef = ref(null)
let ctx = null

const scaledTileSize = computed(() => props.tileSize * props.scale)

// Tile type to image path mapping
const tileImages = {
  grass: '/background/tiles/Grass_Middle.png',
  path: '/background/tiles/Path_Middle.png',
  water: '/background/tiles/Water_Middle.png',
  farmland: '/background/tiles/FarmLand_Tile.png'
}

const decorationImages = {
  tree: '/background/decorations/Oak_Tree.png',
  rock: '/background/decorations/rock.png',
  log: '/background/decorations/log.png',
  red_flower: '/background/decorations/red_flower.png',
  yellow_flower: '/background/decorations/yellow_flower.png',
  lillies: '/background/decorations/lillies.png'
}

// Define which tiles/decorations are solid (non-walkable)
const solidTiles = new Set(['water'])
const solidDecorations = new Set(['tree', 'rock', 'log'])

// Preload images
const loadedImages = {}

async function preloadImages() {
  const allImages = { ...tileImages, ...decorationImages }
  const loadPromises = []

  for (const [key, path] of Object.entries(allImages)) {
    const promise = new Promise((resolve, reject) => {
      const img = new Image()
      img.onload = () => {
        loadedImages[key] = img
        resolve()
      }
      img.onerror = reject
      img.src = path
    })
    loadPromises.push(promise)
  }

  await Promise.all(loadPromises)
}

// Generate collision map based on ground and object layers
function generateCollisionMap() {
  const groundLayer = props.mapData.groundLayer
  const objectLayer = props.mapData.objectLayer

  const rows = groundLayer.length
  const cols = groundLayer[0].length

  const collisionMap = []

  for (let row = 0; row < rows; row++) {
    collisionMap[row] = []
    for (let col = 0; col < cols; col++) {
      const groundTile = groundLayer[row][col]
      const decoration = objectLayer[row][col]

      // Tile is solid if ground is solid OR decoration is solid
      const isSolid = solidTiles.has(groundTile) || solidDecorations.has(decoration)
      collisionMap[row][col] = isSolid
    }
  }

  return collisionMap
}

// Render the tile background
function renderBackground() {
  if (!ctx || !props.mapData) return

  const groundLayer = props.mapData.groundLayer
  const objectLayer = props.mapData.objectLayer

  const rows = groundLayer.length
  const cols = groundLayer[0].length

  // Set canvas size
  const canvasWidth = cols * scaledTileSize.value
  const canvasHeight = rows * scaledTileSize.value

  const canvas = canvasRef.value
  canvas.width = canvasWidth
  canvas.height = canvasHeight
  canvas.style.width = `${canvasWidth}px`
  canvas.style.height = `${canvasHeight}px`

  // Clear canvas
  ctx.clearRect(0, 0, canvasWidth, canvasHeight)

  // Render ground layer
  for (let row = 0; row < rows; row++) {
    for (let col = 0; col < cols; col++) {
      const tileType = groundLayer[row][col]
      const img = loadedImages[tileType]

      if (img) {
        ctx.drawImage(
          img,
          col * scaledTileSize.value,
          row * scaledTileSize.value,
          scaledTileSize.value,
          scaledTileSize.value
        )
      }
    }
  }

  // Render object layer
  for (let row = 0; row < rows; row++) {
    for (let col = 0; col < cols; col++) {
      const decoration = objectLayer[row][col]

      if (decoration) {
        const img = loadedImages[decoration]

        if (img) {
          ctx.drawImage(
            img,
            col * scaledTileSize.value,
            row * scaledTileSize.value,
            scaledTileSize.value,
            scaledTileSize.value
          )
        }
      }
    }
  }
}

onMounted(async () => {
  // Setup canvas
  const canvas = canvasRef.value
  ctx = canvas.getContext('2d')
  ctx.imageSmoothingEnabled = false

  // Preload all images
  await preloadImages()

  // Render the background
  renderBackground()

  // Generate and emit collision map
  const collisionMap = generateCollisionMap()
  emit('collision-map-ready', {
    collisionMap,
    tileSize: scaledTileSize.value,
    cols: props.mapData.groundLayer[0].length,
    rows: props.mapData.groundLayer.length
  })
})

onBeforeUnmount(() => {
  ctx = null
})
</script>

<template>
  <div ref="container" class="tile-background">
    <canvas ref="canvasRef" class="tile-canvas"></canvas>
  </div>
</template>

<style scoped>
.tile-background {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  overflow: hidden;
}

.tile-canvas {
  image-rendering: pixelated;
  image-rendering: -moz-crisp-edges;
  image-rendering: crisp-edges;
  position: absolute;
  top: 0;
  left: 0;
}
</style>
