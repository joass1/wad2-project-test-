<template>
  <div class="pet-page-container">
    <!-- Main Content Area -->
    <div class="main-content" :style="{ backgroundImage: `url(${currentBackground})` }">
      <div class="pet-display-area">
        <div class="pet-container">
          <div class="pet-character" :class="petAnimation">
            <div class="pet-avatar">
              <div class="pet-face" :class="currentPet.type">
                <div class="pet-eyes">
                  <div class="eye left"></div>
                  <div class="eye right"></div>
                </div>
                <div class="pet-mouth"></div>
              </div>
            </div>
            <div class="pet-name">{{ currentPet.name }}</div>
            <div class="pet-level">Level {{ currentPet.level }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Right Panel -->
    <div class="right-panel">
      <!-- Pet Status Section -->
      <div class="panel-section">
        <h4 class="section-title">Pet Status</h4>
        <div class="status-item">
          <span class="status-label">Happy</span>
          <div class="status-bar">
            <div class="status-fill" :style="{ width: `${petStatus.happiness}%` }"></div>
          </div>
          <span class="status-value">{{ petStatus.happiness }}%</span>
        </div>
        <div class="status-item">
          <span class="status-label">Health</span>
          <div class="status-bar">
            <div class="status-fill health" :style="{ width: `${petStatus.health}%` }"></div>
          </div>
          <span class="status-value">{{ petStatus.health }}%</span>
        </div>
        <div class="status-item">
          <span class="status-label">Energy</span>
          <div class="status-bar">
            <div class="status-fill energy" :style="{ width: `${petStatus.energy}%` }"></div>
          </div>
          <span class="status-value">{{ petStatus.energy }}%</span>
        </div>
      </div>

      <!-- Food Selection -->
      <div class="panel-section">
        <h4 class="section-title">Food you have</h4>
        <div class="selection-container">
          <button class="nav-btn" @click="previousFood" :disabled="foodIndex === 0">
            <span>‹</span>
          </button>
          <div class="item-display">
            <div class="item-icon food-icon">{{ availableFood[foodIndex].icon }}</div>
            <div class="item-count">{{ availableFood[foodIndex].count }} left</div>
          </div>
          <button class="nav-btn" @click="nextFood" :disabled="foodIndex === availableFood.length - 1">
            <span>›</span>
          </button>
        </div>
        <button class="action-btn" @click="feedPet" :disabled="availableFood[foodIndex].count === 0">
          Feed Pet
        </button>
      </div>

      <!-- Pet Selection -->
      <div class="panel-section">
        <h4 class="section-title">Pet Select</h4>
        <div class="selection-container">
          <button class="nav-btn" @click="previousPet" :disabled="petIndex === 0">
            <span>‹</span>
          </button>
          <div class="item-display">
            <div class="pet-preview" :class="availablePets[petIndex].type">
              <div class="pet-face-small">
                <div class="pet-eyes-small">
                  <div class="eye-small left"></div>
                  <div class="eye-small right"></div>
                </div>
                <div class="pet-mouth-small"></div>
              </div>
            </div>
            <div class="pet-name-small">{{ availablePets[petIndex].name }}</div>
          </div>
          <button class="nav-btn" @click="nextPet" :disabled="petIndex === availablePets.length - 1">
            <span>›</span>
          </button>
        </div>
        <button class="action-btn" @click="selectPet">
          Select Pet
        </button>
      </div>

      <!-- Background Selector -->
      <div class="panel-section">
        <h4 class="section-title">Bg Selector</h4>
        <div class="selection-container">
          <button class="nav-btn" @click="previousBackground" :disabled="bgIndex === 0">
            <span>‹</span>
          </button>
          <div class="item-display">
            <div class="bg-preview" :style="{ backgroundImage: `url(${availableBackgrounds[bgIndex].preview})` }">
              <div class="bg-name">{{ availableBackgrounds[bgIndex].name }}</div>
            </div>
          </div>
          <button class="nav-btn" @click="nextBackground" :disabled="bgIndex === availableBackgrounds.length - 1">
            <span>›</span>
          </button>
        </div>
        <button class="action-btn" @click="selectBackground">
          Select Background
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'

// Pet data
const currentPet = ref({
  name: 'Buddy',
  type: 'cat',
  level: 1
})

const petStatus = reactive({
  happiness: 75,
  health: 80,
  energy: 60
})

// Food selection
const foodIndex = ref(0)
const availableFood = ref([
  { icon: '🍎', name: 'Apple', count: 3 },
  { icon: '🥕', name: 'Carrot', count: 1 },
  { icon: '🐟', name: 'Fish', count: 5 },
  { icon: '🥛', name: 'Milk', count: 2 }
])

// Pet selection
const petIndex = ref(0)
const availablePets = ref([
  { name: 'Buddy', type: 'cat' },
  { name: 'Rex', type: 'dog' },
  { name: 'Fluffy', type: 'rabbit' },
  { name: 'Squeaky', type: 'hamster' }
])

// Background selection
const bgIndex = ref(0)
const availableBackgrounds = ref([
  { 
    name: 'Waterfall Valley', 
    preview: '/photos/pixelbg1.jpg',
    fullImage: '/photos/pixelbg1.jpg',
    cssClass: 'waterfall-bg'
  },
  { 
    name: 'Mountain Peak', 
    preview: '/photos/pixelbg2.jpg',
    fullImage: '/photos/pixelbg2.jpg',
    cssClass: 'forest-bg'
  }
])

const currentBackground = computed(() => availableBackgrounds.value[bgIndex.value].fullImage)

// Pet animation
const petAnimation = ref('idle')

// Navigation functions
function previousFood() {
  if (foodIndex.value > 0) foodIndex.value--
}

function nextFood() {
  if (foodIndex.value < availableFood.value.length - 1) foodIndex.value++
}

function previousPet() {
  if (petIndex.value > 0) petIndex.value--
}

function nextPet() {
  if (petIndex.value < availablePets.value.length - 1) petIndex.value++
}

function previousBackground() {
  if (bgIndex.value > 0) bgIndex.value--
}

function nextBackground() {
  if (bgIndex.value < availableBackgrounds.value.length - 1) bgIndex.value++
}

// Action functions
function feedPet() {
  if (availableFood[foodIndex.value].count > 0) {
    availableFood[foodIndex.value].count--
    petStatus.happiness = Math.min(100, petStatus.happiness + 10)
    petStatus.health = Math.min(100, petStatus.health + 5)
    petAnimation.value = 'happy'
    setTimeout(() => { petAnimation.value = 'idle' }, 2000)
  }
}

function selectPet() {
  currentPet.value = { ...availablePets.value[petIndex.value], level: currentPet.value.level }
  petAnimation.value = 'excited'
  setTimeout(() => { petAnimation.value = 'idle' }, 2000)
}

function selectBackground() {
  petAnimation.value = 'excited'
  setTimeout(() => { petAnimation.value = 'idle' }, 2000)
}
</script>

<style scoped>
.pet-page-container {
  display: flex;
  height: 100vh;
  overflow: hidden;
}

/* Main Content Area */
.main-content {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
  position: relative;
  overflow: hidden;
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
}

.pet-display-area {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.pet-container {
  width: 400px;
  height: 400px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  position: relative;
  background: transparent;
}

.pet-character {
  display: flex;
  flex-direction: column;
  align-items: center;
  transition: all 0.3s ease;
}

.pet-character.idle {
  animation: idle 3s ease-in-out infinite;
}

.pet-character.happy {
  animation: happy 1s ease-in-out;
}

.pet-character.excited {
  animation: excited 0.5s ease-in-out 3;
}

.pet-avatar {
  width: 120px;
  height: 120px;
  background-color: #ffd93d;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 16px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

.pet-face {
  width: 80px;
  height: 80px;
  position: relative;
}

.pet-eyes {
  position: absolute;
  top: 20px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: 12px;
}

.eye {
  width: 8px;
  height: 8px;
  background-color: #333;
  border-radius: 50%;
}

.pet-mouth {
  position: absolute;
  bottom: 15px;
  left: 50%;
  transform: translateX(-50%);
  width: 20px;
  height: 10px;
  border: 2px solid #333;
  border-top: none;
  border-radius: 0 0 20px 20px;
}

.pet-name {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.pet-level {
  font-size: 14px;
  color: var(--text-muted);
  background-color: var(--surface);
  padding: 4px 12px;
  border-radius: 12px;
}

/* Right Panel */
.right-panel {
  width: 280px;
  background-color: var(--surface);
  border-left: 1px solid var(--surface-lighter);
  padding: 24px 16px;
  overflow-y: auto;
}

.panel-section {
  margin-bottom: 32px;
  padding-bottom: 24px;
  border-bottom: 1px solid var(--surface-lighter);
}

.panel-section:last-child {
  border-bottom: none;
  margin-bottom: 0;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 16px 0;
}

.status-item {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.status-label {
  font-size: 14px;
  color: var(--text-muted);
  min-width: 50px;
}

.status-bar {
  flex: 1;
  height: 8px;
  background-color: var(--surface-lighter);
  border-radius: 4px;
  overflow: hidden;
}

.status-fill {
  height: 100%;
  background-color: var(--primary);
  border-radius: 4px;
  transition: width 0.3s ease;
}

.status-fill.health {
  background-color: #4ade80;
}

.status-fill.energy {
  background-color: #f59e0b;
}

.status-value {
  font-size: 12px;
  color: var(--text-muted);
  min-width: 30px;
  text-align: right;
}

.selection-container {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.nav-btn {
  width: 32px;
  height: 32px;
  border: 1px solid var(--surface-lighter);
  background-color: var(--surface);
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
  color: var(--text-muted);
}

.nav-btn:hover:not(:disabled) {
  background-color: var(--surface-light);
  color: var(--text-primary);
}

.nav-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.item-display {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.item-icon {
  font-size: 32px;
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: var(--surface-light);
  border-radius: 12px;
}

.item-count {
  font-size: 12px;
  color: var(--text-muted);
}

.pet-preview {
  width: 48px;
  height: 48px;
  background-color: #ffd93d;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.pet-face-small {
  width: 32px;
  height: 32px;
  position: relative;
}

.pet-eyes-small {
  position: absolute;
  top: 8px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: 6px;
}

.eye-small {
  width: 4px;
  height: 4px;
  background-color: #333;
  border-radius: 50%;
}

.pet-mouth-small {
  position: absolute;
  bottom: 6px;
  left: 50%;
  transform: translateX(-50%);
  width: 10px;
  height: 5px;
  border: 1px solid #333;
  border-top: none;
  border-radius: 0 0 10px 10px;
}

.pet-name-small {
  font-size: 12px;
  color: var(--text-primary);
  font-weight: 500;
}

.bg-preview {
  width: 100%;
  height: 48px;
  border-radius: 8px;
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
}

.bg-name {
  background-color: rgba(0, 0, 0, 0.7);
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.action-btn {
  width: 100%;
  padding: 10px 16px;
  background-color: var(--primary);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.action-btn:hover:not(:disabled) {
  background-color: var(--secondary);
  transform: translateY(-1px);
}

.action-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

/* Animations */
@keyframes idle {
  0%, 100% { transform: translateY(0px); }
  50% { transform: translateY(-5px); }
}

@keyframes happy {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.1); }
}

@keyframes excited {
  0%, 100% { transform: translateY(0px) scale(1); }
  50% { transform: translateY(-10px) scale(1.05); }
}


/* Mobile responsiveness */
@media (max-width: 768px) {
  .pet-page-container {
    flex-direction: column;
    height: auto;
  }
  
  .main-content {
    height: 300px;
    padding: 16px;
  }
  
  .pet-container {
    width: 250px;
    height: 250px;
  }
  
  .right-panel {
    width: 100%;
    padding: 16px;
  }
}
</style>
