<template>
  <div 
    v-if="showPet && petConfig"
    class="global-pet" 
    :style="{ 
      left: petState.x + 'px', 
      top: petState.y + 'px',
    }"
    @mousedown="handleMouseDown"
  >
    <img 
      v-if="currentSprite"
      :src="currentSprite" 
      :width="petSize" 
      :height="petSize"
      draggable="false"
      alt="Desktop Pet"
      class="pet-sprite"
      @error="handleImageError"
    />
    <div v-else class="pet-loading">🐱</div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { usePet } from '@/composables/usePet'

const { petState, petConfig, isConnected, movePet, grabPet, initializePet } = usePet()

const showPet = ref(true)
const isDragging = ref(false)
const dragOffset = ref({ x: 0, y: 0 })
const petSize = ref(100)

// Get current sprite URL with ALL animations mapped
const currentSprite = computed(() => {
  if (!petConfig.value || !petConfig.value.animations) {
    console.warn('⚠️ Pet config not loaded yet')
    return ''
  }
  
  const animation = petState.value.animation || 'idle'
  let spritePath = ''
  
  switch(animation) {
    case 'idle':
      spritePath = petConfig.value.animations.idle
      break
    case 'grabbed':
      spritePath = petConfig.value.animations.idle  // Use idle.gif when grabbed
      break
    case 'walk_left':
      spritePath = petConfig.value.animations.walk_left
      break
    case 'walk_right':
      spritePath = petConfig.value.animations.walk_right
      break
    case 'sleep':
      spritePath = petConfig.value.animations.sleep
      break
    case 'idle_to_sleep':
      spritePath = petConfig.value.animations.idle_to_sleep
      break
    case 'sleep_to_idle':
      spritePath = petConfig.value.animations.sleep_to_idle
      break
    case 'falling':
      spritePath = petConfig.value.animations.falling
      break
    default:
      spritePath = petConfig.value.animations.idle
  }
  
  const fullUrl = spritePath ? `http://localhost:8000${spritePath}` : ''
  console.log(`🎨 Animation: ${animation} -> ${fullUrl}`)
  return fullUrl
})

const handleImageError = (e) => {
  console.error('❌ Failed to load sprite:', currentSprite.value)
}

// Mouse drag handlers
const handleMouseDown = (event) => {
  console.log('🖱️ Mouse down on pet!', {
    x: petState.value.x,
    y: petState.value.y,
    animation: petState.value.animation
  })
  
  event.preventDefault()
  event.stopPropagation()
  
  isDragging.value = true
  
  dragOffset.value = {
    x: event.clientX - petState.value.x,
    y: event.clientY - petState.value.y
  }
  
  console.log('📍 Grab offset:', dragOffset.value)
  
  // Tell backend pet is grabbed
  grabPet(true)
  
  // Add listeners to document for smooth dragging
  document.addEventListener('mousemove', handleMouseMove, { passive: false })
  document.addEventListener('mouseup', handleMouseUp)
}

const handleMouseMove = (event) => {
  if (!isDragging.value) return
  
  event.preventDefault()
  
  const newX = event.clientX - dragOffset.value.x
  const newY = event.clientY - dragOffset.value.y
  
  // Keep pet on screen
  const constrainedX = Math.max(0, Math.min(window.innerWidth - petSize.value, newX))
  const constrainedY = Math.max(0, Math.min(window.innerHeight - petSize.value, newY))
  
  console.log('🚀 Moving to:', constrainedX, constrainedY)
  
  movePet(constrainedX, constrainedY)
}

const handleMouseUp = () => {
  console.log('🖐️ Mouse up - releasing pet')
  
  if (!isDragging.value) return
  
  isDragging.value = false
  grabPet(false)
  
  // Remove listeners
  document.removeEventListener('mousemove', handleMouseMove)
  document.removeEventListener('mouseup', handleMouseUp)
}

// Watch pet state changes
watch(() => petState.value, (newState, oldState) => {
  console.log('🔄 Pet state updated:', {
    oldPos: oldState ? `${oldState.x},${oldState.y}` : 'none',
    newPos: `${newState.x},${newState.y}`,
    animation: newState.animation
  })
}, { deep: true })

// Watch config loading
watch(() => petConfig.value, (newConfig) => {
  if (newConfig) {
    console.log('✅ Pet config loaded:', newConfig)
  }
})

onMounted(() => {
  console.log('🎮 GlobalDesktopPet mounted')
  console.log('📦 Initial Pet config:', petConfig.value)
  console.log('🐱 Initial pet state:', petState.value)
  
  // Initialize pet at window size
  initializePet(window.innerWidth, window.innerHeight)
  
  // Force check config after a delay
  setTimeout(() => {
    console.log('⏰ Config after 1s:', petConfig.value)
  }, 1000)
})

onUnmounted(() => {
  console.log('💀 GlobalDesktopPet unmounting')
  // Clean up
  document.removeEventListener('mousemove', handleMouseMove)
  document.removeEventListener('mouseup', handleMouseUp)
})
</script>

<style scoped>
.global-pet {
  position: fixed;
  z-index: 9999;
  pointer-events: auto;
  cursor: grab;
  user-select: none;
  -webkit-user-select: none;
  -webkit-user-drag: none;
  transition: none; /* Remove any transitions that might interfere */
}

.global-pet:active {
  cursor: grabbing;
}

.pet-sprite {
  display: block;
  pointer-events: none;
  image-rendering: pixelated;
  image-rendering: -moz-crisp-edges;
  image-rendering: crisp-edges;
  -webkit-user-drag: none;
  user-select: none;
}

.pet-loading {
  font-size: 60px;
  animation: bounce 1s infinite;
}

@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}
</style>
