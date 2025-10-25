<script setup>
import { ref, onMounted, onBeforeUnmount, watch } from 'vue'
import { loadTMXMap, getTilesetForGid, getTileSourceRect } from '@/utils/tmxParser.js'

const props = defineProps({
  tmxPath: {
    type: String,
    required: true
  }
})

const emit = defineEmits(['collision-ready', 'map-loaded'])

const container = ref(null)
const canvasRef = ref(null)
const errorMessage = ref(null)
const showCollisionDebug = ref(false) // Toggle for debugging
let ctx = null
let mapData = null
let tilesetImages = {}
let resizeObserver = null
let scale = 2

// Responsive scaling
function calculateScale() {
  if (!container.value || !mapData) return 1

  const containerWidth = container.value.clientWidth
  const containerHeight = container.value.clientHeight

  const mapPixelWidth = mapData.width * mapData.tileWidth
  const mapPixelHeight = mapData.height * mapData.tileHeight

  // Calculate scale to fit container while maintaining aspect ratio
  const scaleX = containerWidth / mapPixelWidth
  const scaleY = containerHeight / mapPixelHeight

  return Math.min(scaleX, scaleY)
}

// Load all tileset images
async function loadTilesetImages() {
  const loadPromises = []

  for (const tileset of mapData.tilesets) {
    if (tileset.isCollection) {
      // Collection tileset - load each tile's image separately
      console.log(`Loading collection tileset: ${tileset.name} with ${tileset.tiles.length} tiles`)

      // Store collection info
      tilesetImages[tileset.firstGid] = {
        tileset: tileset,
        isCollection: true,
        tileImages: {} // Will store individual tile images
      }

      // Load each tile's image
      for (const tile of tileset.tiles) {
        const promise = new Promise((resolve, reject) => {
          const img = new Image()
          img.onload = () => {
            console.log(`Loaded collection tile ${tile.id}: ${tile.imagePath}`)
            tilesetImages[tileset.firstGid].tileImages[tile.id] = {
              image: img,
              width: tile.width,
              height: tile.height
            }
            resolve()
          }
          img.onerror = (e) => {
            console.error(`Failed to load collection tile image: ${tile.imagePath}`, e)
            reject(new Error(`Failed to load ${tile.imagePath}`))
          }
          img.src = tile.imagePath
        })
        loadPromises.push(promise)
      }
    } else {
      // Regular tileset - single spritesheet
      console.log(`Loading tileset: ${tileset.name} from ${tileset.imagePath}`)
      const promise = new Promise((resolve, reject) => {
        const img = new Image()
        img.onload = () => {
          console.log(`Loaded tileset image: ${tileset.name}`)
          tilesetImages[tileset.firstGid] = {
            image: img,
            tileset: tileset,
            isCollection: false
          }
          resolve()
        }
        img.onerror = (e) => {
          console.error(`Failed to load tileset image: ${tileset.imagePath}`, e)
          console.error(`Tileset name: ${tileset.name}, firstGid: ${tileset.firstGid}`)
          reject(new Error(`Failed to load ${tileset.imagePath}`))
        }
        img.src = tileset.imagePath
      })
      loadPromises.push(promise)
    }
  }

  await Promise.all(loadPromises)
}

// Parse collision objects from objectgroup
function parseCollisionObjects() {
  const collisionGroup = mapData.objectGroups.find(g => g.name === 'collision')
  if (!collisionGroup) {
    console.warn('No collision layer found in TMX map')
    return []
  }

  console.log('Parsing collision objects from TMX...')
  console.log(`Map dimensions: ${mapData.width}×${mapData.height} tiles`)
  console.log(`Tile size: ${mapData.tileWidth}×${mapData.tileHeight}px`)
  console.log(`Original map size: ${mapData.width * mapData.tileWidth}×${mapData.height * mapData.tileHeight}px`)
  console.log(`Container size: ${container.value?.clientWidth}×${container.value?.clientHeight}px`)
  console.log(`Scale factor: ${scale}`)
  console.log(`Scaled map size: ${mapData.width * mapData.tileWidth * scale}×${mapData.height * mapData.tileHeight * scale}px`)

  // Convert objects to scaled rectangles
  const collisionObjects = collisionGroup.objects.map(obj => {
    const scaled = {
      id: obj.id,
      x: obj.x * scale,
      y: obj.y * scale,
      width: obj.width * scale,
      height: obj.height * scale,
      // Keep original for debugging
      originalX: obj.x,
      originalY: obj.y,
      originalWidth: obj.width,
      originalHeight: obj.height
    }
    return scaled
  })

  console.log(`✅ Created ${collisionObjects.length} collision rectangles`)
  console.log('First 5 collision objects (TMX → Scaled):')
  collisionObjects.slice(0, 5).forEach(obj => {
    console.log(`  ID ${obj.id}: [${obj.originalX}, ${obj.originalY}, ${obj.originalWidth}×${obj.originalHeight}] → [${obj.x.toFixed(1)}, ${obj.y.toFixed(1)}, ${obj.width.toFixed(1)}×${obj.height.toFixed(1)}]`)
  })

  return collisionObjects
}

// Draw collision rectangles for debugging
function drawCollisionDebug(collisionObjects) {
  if (!ctx || !showCollisionDebug.value) return

  ctx.strokeStyle = 'rgba(255, 0, 0, 0.8)'
  ctx.lineWidth = 2
  ctx.fillStyle = 'rgba(255, 0, 0, 0.2)'

  for (const obj of collisionObjects) {
    ctx.fillRect(obj.x, obj.y, obj.width, obj.height)
    ctx.strokeRect(obj.x, obj.y, obj.width, obj.height)
  }
}

// Render the map
function renderMap() {
  if (!ctx || !mapData || Object.keys(tilesetImages).length === 0) {
    console.warn('Cannot render map - missing context or data')
    console.log('ctx:', !!ctx, 'mapData:', !!mapData, 'tilesetImages:', Object.keys(tilesetImages).length)
    return
  }

  const canvas = canvasRef.value
  const scaledWidth = mapData.width * mapData.tileWidth * scale
  const scaledHeight = mapData.height * mapData.tileHeight * scale

  console.log(`Rendering map at ${scaledWidth}x${scaledHeight} (scale: ${scale})`)

  // Set canvas size
  canvas.width = scaledWidth
  canvas.height = scaledHeight
  canvas.style.width = `${scaledWidth}px`
  canvas.style.height = `${scaledHeight}px`

  // Clear canvas
  ctx.clearRect(0, 0, scaledWidth, scaledHeight)
  ctx.imageSmoothingEnabled = false

  // Render each layer
  console.log(`Rendering ${mapData.layers.length} layers`)
  for (const layer of mapData.layers) {
    renderLayer(layer)
  }

  // Render object groups (like trees)
  console.log(`Rendering ${mapData.objectGroups.length} object groups`)
  for (const objGroup of mapData.objectGroups) {
    if (objGroup.name !== 'collision') {
      renderObjectGroup(objGroup)
    }
  }

  console.log('✅ Rendering complete')

  // Draw collision debug overlay if enabled
  const collisionObjects = parseCollisionObjects()
  drawCollisionDebug(collisionObjects)
}

// Render a single layer
function renderLayer(layer) {
  for (let row = 0; row < layer.height; row++) {
    for (let col = 0; col < layer.width; col++) {
      const gid = layer.data[row][col]
      if (gid === 0) continue // Empty tile

      const tileInfo = getTilesetForGid(gid, mapData.tilesets)
      if (!tileInfo) continue

      const tilesetData = tilesetImages[tileInfo.tileset.firstGid]
      if (!tilesetData) continue

      const sourceRect = getTileSourceRect(tileInfo.localId, tileInfo.tileset)

      const destX = col * mapData.tileWidth * scale
      const destY = row * mapData.tileHeight * scale
      const destWidth = mapData.tileWidth * scale
      const destHeight = mapData.tileHeight * scale

      ctx.drawImage(
        tilesetData.image,
        sourceRect.x, sourceRect.y, sourceRect.width, sourceRect.height,
        destX, destY, destWidth, destHeight
      )
    }
  }
}

// Render object group (for tile objects like trees)
function renderObjectGroup(objGroup) {
  console.log(`Rendering object group: ${objGroup.name}, objects: ${objGroup.objects.length}`)
  for (const obj of objGroup.objects) {
    if (!obj.gid) {
      console.log('Skipping object without gid:', obj)
      continue // Skip objects without gid
    }

    console.log(`Rendering object with gid ${obj.gid} at (${obj.x}, ${obj.y})`)

    const tileInfo = getTilesetForGid(obj.gid, mapData.tilesets)
    if (!tileInfo) {
      console.warn(`No tileset found for gid ${obj.gid}`)
      continue
    }

    console.log(`Found tileset: ${tileInfo.tileset.name}, localId: ${tileInfo.localId}`)

    const tilesetData = tilesetImages[tileInfo.tileset.firstGid]
    if (!tilesetData) {
      console.warn(`No tileset image loaded for firstGid ${tileInfo.tileset.firstGid}`)
      continue
    }

    // Tiled objects use bottom-left origin, convert to top-left
    const destX = obj.x * scale
    const destY = (obj.y - obj.height) * scale
    const destWidth = obj.width * scale
    const destHeight = obj.height * scale

    console.log(`Drawing at (${destX}, ${destY}), size: ${destWidth}x${destHeight}`)

    if (tilesetData.isCollection) {
      // Collection tileset - get individual tile image
      const tileImage = tilesetData.tileImages[tileInfo.localId]
      if (!tileImage) {
        console.warn(`No tile image found for localId ${tileInfo.localId}`)
        continue
      }

      console.log(`Drawing collection tile ${tileInfo.localId}, image size: ${tileImage.width}x${tileImage.height}`)

      // Draw the entire tile image (no source rect needed)
      ctx.drawImage(
        tileImage.image,
        destX, destY, destWidth, destHeight
      )
    } else {
      // Regular tileset - use source rectangle
      const sourceRect = getTileSourceRect(tileInfo.localId, tileInfo.tileset)
      console.log('Source rect:', sourceRect)

      ctx.drawImage(
        tilesetData.image,
        sourceRect.x, sourceRect.y, sourceRect.width, sourceRect.height,
        destX, destY, destWidth, destHeight
      )
    }
  }
}

// Handle container resize
function handleResize() {
  if (!mapData) return

  scale = calculateScale()
  renderMap()

  // Re-emit collision data with new scale
  const collisionObjects = parseCollisionObjects()
  emit('collision-ready', {
    collisionObjects,
    mapWidth: mapData.width * mapData.tileWidth * scale,
    mapHeight: mapData.height * mapData.tileHeight * scale,
    scale
  })
}

// Keyboard handler for debug toggle
function handleKeyPress(event) {
  if (event.key === 'c' && event.ctrlKey) {
    event.preventDefault()
    showCollisionDebug.value = !showCollisionDebug.value
    console.log(`🔍 Collision debug: ${showCollisionDebug.value ? 'ON' : 'OFF'}`)
    renderMap() // Re-render to show/hide collision boxes
  }
}

onMounted(async () => {
  try {
    console.log('Loading TMX map from:', props.tmxPath)

    // Load TMX map
    mapData = await loadTMXMap(props.tmxPath)
    console.log('✅ Loaded TMX map:', mapData)
    console.log('Map size:', mapData.width, 'x', mapData.height)
    console.log('Tile size:', mapData.tileWidth, 'x', mapData.tileHeight)
    console.log('Tilesets:', mapData.tilesets.length)
    console.log('Layers:', mapData.layers.length)

    // Setup canvas
    ctx = canvasRef.value.getContext('2d')
    ctx.imageSmoothingEnabled = false

    // Load all tileset images
    console.log('Loading tileset images...')
    await loadTilesetImages()
    console.log('✅ Loaded', Object.keys(tilesetImages).length, 'tileset images')

    // Calculate initial scale
    scale = calculateScale()
    console.log('Map scale:', scale)

    // Render the map
    console.log('Rendering map...')
    renderMap()
    console.log('✅ Map rendered')

    // Parse and emit collision data
    const collisionObjects = parseCollisionObjects()
    console.log('Collision objects:', collisionObjects.length)
    emit('collision-ready', {
      collisionObjects,
      mapWidth: mapData.width * mapData.tileWidth * scale,
      mapHeight: mapData.height * mapData.tileHeight * scale,
      scale
    })

    emit('map-loaded', { mapData, scale })

    // Setup resize observer for responsiveness
    if (container.value && window.ResizeObserver) {
      resizeObserver = new ResizeObserver(handleResize)
      resizeObserver.observe(container.value)
    }

    // Add keyboard listener for collision debug toggle
    window.addEventListener('keydown', handleKeyPress)

    console.log('💡 Press Ctrl+C to toggle collision debug overlay')
  } catch (error) {
    console.error('❌ Failed to load TMX map:', error)
    console.error('Error details:', error.message)
    console.error('Stack:', error.stack)
    errorMessage.value = `Failed to load map: ${error.message}`
  }
})

onBeforeUnmount(() => {
  if (resizeObserver) {
    resizeObserver.disconnect()
  }
  window.removeEventListener('keydown', handleKeyPress)
  ctx = null
  mapData = null
  tilesetImages = {}
})

// Watch for tmxPath changes
watch(() => props.tmxPath, async () => {
  if (!props.tmxPath) return

  try {
    mapData = await loadTMXMap(props.tmxPath)
    await loadTilesetImages()
    scale = calculateScale()
    renderMap()

    const collisionObjects = parseCollisionObjects()
    emit('collision-ready', {
      collisionObjects,
      mapWidth: mapData.width * mapData.tileWidth * scale,
      mapHeight: mapData.height * mapData.tileHeight * scale,
      scale
    })
  } catch (error) {
    console.error('Failed to reload TMX map:', error)
  }
})
</script>

<template>
  <div ref="container" class="tmx-background">
    <canvas ref="canvasRef" class="tmx-canvas"></canvas>

    <!-- Collision Debug Indicator -->
    <div v-if="showCollisionDebug" class="debug-indicator">
      🔍 Collision Debug ON (Ctrl+C to toggle)
    </div>

    <!-- Error Overlay -->
    <div v-if="errorMessage" class="error-overlay">
      <div class="error-message">
        <h3>Map Loading Error</h3>
        <p>{{ errorMessage }}</p>
        <p class="error-hint">Check the browser console for more details</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.tmx-background {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  overflow: hidden;
  background: #87CEEB; /* Sky blue fallback */
}

.tmx-canvas {
  image-rendering: pixelated;
  image-rendering: -moz-crisp-edges;
  image-rendering: crisp-edges;
  position: absolute;
  top: 0;
  left: 0;
}

.error-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.error-message {
  background: #fff;
  padding: 30px;
  border-radius: 12px;
  max-width: 500px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
}

.error-message h3 {
  margin: 0 0 15px 0;
  color: #d32f2f;
}

.error-message p {
  margin: 10px 0;
  color: #333;
}

.error-hint {
  font-size: 12px;
  color: #666;
  font-style: italic;
}

.debug-indicator {
  position: absolute;
  top: 10px;
  left: 10px;
  background: rgba(255, 0, 0, 0.9);
  color: white;
  padding: 8px 16px;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 600;
  z-index: 999;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}
</style>
