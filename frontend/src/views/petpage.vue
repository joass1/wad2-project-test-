<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import AnimatedPet from '@/components/AnimatedPet.vue'
import SpritePreview from '@/components/SpritePreview.vue'
import AnimatedCoin from '@/components/AnimatedCoin.vue'
import TileBackground from '@/components/TileBackground.vue'
import { useCoins } from '@/composables/useCoins.js'
import { useGlobalPet } from '@/composables/useGlobalPet.js'
import { api } from '@/lib/api.js'
import { TILE_MAPS, MAP_LIST } from '@/data/tilemaps.js'
import { PET_CATALOG, PET_KEYS } from '@/data/petCatalog.js'

/* ================= PET CATALOG ================= */
const PETS = PET_CATALOG

/* ==== Status ==== */
const petStatus = reactive({ happiness: 75, health: 80, energy: 60 })

/* ==== Inventory ==== */
const INVENTORY_SLOTS = 16  // 4 rows x 4 columns
const inventory = ref([])  // Empty initially, items added when purchased
const inventoryLoading = ref(false)
const inventoryError = ref(null)

/* ==== Dropped Items (on background) ==== */
const droppedItems = ref([])  // Items dropped on the background for pet to eat
let nextDroppedItemId = 0

/* ==== Pet picker (preview vs active pet) ==== */
const petKeys = PET_KEYS
const petIndex = ref(0) // Preview pet index
const { selectedPetKey: globalPetKey, setGlobalPet } = useGlobalPet()
const selectedPetKey = computed(() => globalPetKey.value) // Active pet from global state
const previewPetKey = computed(() => petKeys[petIndex.value]) // Preview pet

function previousPet() { if (petIndex.value > 0) petIndex.value-- }
function nextPet() { if (petIndex.value < petKeys.length - 1) petIndex.value++ }
function selectPet() { 
  const newPetKey = petKeys[petIndex.value]
  setGlobalPet(newPetKey)
  console.log(`Selected pet: ${PETS[newPetKey].label}`)
}

/* ==== Tile-based Backgrounds ==== */
const bgIndex = ref(0)
const availableBackgrounds = ref(MAP_LIST)
const currentMapKey = computed(() => availableBackgrounds.value[bgIndex.value].key)
const currentMapData = computed(() => TILE_MAPS[currentMapKey.value])

// Collision map data from TileBackground component
const collisionData = ref({
  collisionMap: [],
  tileSize: 32,  // No scaling
  cols: 40,
  rows: 25
})

function previousBackground() { if (bgIndex.value > 0) bgIndex.value-- }
function nextBackground() { if (bgIndex.value < availableBackgrounds.value.length - 1) bgIndex.value++ }

function handleCollisionMapReady(data) {
  collisionData.value = data
}

/* ==== Inventory API ==== */
async function fetchInventory() {
  inventoryLoading.value = true
  inventoryError.value = null
  try {
    const response = await api.get('/api/profile/inventory')
    if (response && Array.isArray(response.inventory)) {
      inventory.value = response.inventory
    } else {
      inventoryError.value = 'Invalid inventory response'
    }
  } catch (error) {
    console.error('Failed to fetch inventory:', error)
    inventoryError.value = error.message || 'Failed to load inventory'
  } finally {
    inventoryLoading.value = false
  }
}

async function saveInventory() {
  try {
    const response = await api.put('/api/profile/inventory', { inventory: inventory.value })
    if (!response || !response.ok) {
      console.error('Failed to save inventory:', response)
    }
  } catch (error) {
    console.error('Failed to save inventory:', error)
  }
}

/* ==== Inventory actions ==== */
function feedPet(slotIndex) {
  const item = inventory.value[slotIndex]
  if (item && item.count > 0) {
    item.count--
    petStatus.happiness = Math.min(100, petStatus.happiness + 10)
    petStatus.health = Math.min(100, petStatus.health + 5)

    // Remove item from inventory if count reaches 0
    if (item.count === 0) {
      inventory.value.splice(slotIndex, 1)
    }

    // Save inventory to backend
    saveInventory()
  }
}

/* ==== Drag and Drop ==== */
let draggedItem = null
let draggedItemIndex = null

function startDrag(event, item, index) {
  draggedItem = item
  draggedItemIndex = index
  event.dataTransfer.effectAllowed = 'move'
  event.dataTransfer.setData('text/html', event.target.innerHTML)
}

function onDrop(event) {
  event.preventDefault()

  if (!draggedItem) return

  // Get the pet stage element to calculate relative position
  const petStage = event.currentTarget
  const rect = petStage.getBoundingClientRect()

  // Calculate drop position relative to pet stage
  let x = event.clientX - rect.left
  let y = event.clientY - rect.top

  // Item size (40px emoji)
  const ITEM_SIZE = 40

  // Clamp X to boundaries (left and right edges)
  x = Math.max(ITEM_SIZE / 2, Math.min(x, rect.width - ITEM_SIZE / 2))

  // Adjust Y position so the bottom of the item is at cursor position
  // This prevents the item from being half-buried in the ground
  y = y - ITEM_SIZE / 2

  // Clamp Y to prevent dropping too high or outside bounds
  y = Math.max(0, Math.min(y, rect.height - ITEM_SIZE))

  // Add dropped item to the background
  droppedItems.value.push({
    id: nextDroppedItemId++,
    icon: draggedItem.icon,
    name: draggedItem.name,
    x: x,
    y: y
  })

  // Remove one from inventory
  if (draggedItem.count > 1) {
    draggedItem.count--
  } else {
    inventory.value.splice(draggedItemIndex, 1)
  }

  // Save inventory to backend
  saveInventory()

  // Clear drag state
  draggedItem = null
  draggedItemIndex = null
}

function onDragOver(event) {
  event.preventDefault()
  event.dataTransfer.dropEffect = 'move'
}

// Remove dropped item (when pet eats it)
function removeDroppedItem(itemId) {
  console.log('removeDroppedItem called with ID:', itemId)
  console.log('Current droppedItems:', droppedItems.value)
  const index = droppedItems.value.findIndex(item => item.id === itemId)
  console.log('Found index:', index)
  if (index !== -1) {
    const removedItem = droppedItems.value[index]
    console.log('Removing item:', removedItem)
    droppedItems.value.splice(index, 1)
    // Increase pet stats when eating
    petStatus.happiness = Math.min(100, petStatus.happiness + 10)
    petStatus.health = Math.min(100, petStatus.health + 5)
    console.log('Updated stats - Happiness:', petStatus.happiness, 'Health:', petStatus.health)
  } else {
    console.log('Item not found in droppedItems array!')
  }
}

/* ==== Manual Control ==== */
const manualControlEnabled = ref(false)

function toggleManualControl() {
  manualControlEnabled.value = !manualControlEnabled.value
}

/* ==== Border Warning ==== */
const showBorderWarning = ref(false)
let borderWarningTimeout = null

function handleBorderWarning() {
  showBorderWarning.value = true

  // Clear existing timeout
  if (borderWarningTimeout) {
    clearTimeout(borderWarningTimeout)
  }

  // Auto-hide after 2 seconds
  borderWarningTimeout = setTimeout(() => {
    showBorderWarning.value = false
  }, 2000)
}

/* ==== Shop ==== */
const showShop = ref(false)

// Use shared coin state
const { coins: playerGold, coinsLoading, coinsError, fetchCoins, updateCoins } = useCoins()

const shopItems = ref([
  { icon: '/food/fish.png', name: 'Fish', price: 80, description: 'Fresh fish, a premium treat for pets.' },
  { icon: '/food/milk.png', name: 'Milk', price: 40, description: 'Fresh milk, good for growing pets.' },
  { icon: '/food/beef.png', name: 'Beef', price: 120, description: 'Premium beef, the ultimate pet treat.' },
  { icon: '/food/shrimp.png', name: 'Shrimp', price: 90, description: 'Delicious shrimp, a seafood delight.' },
  { icon: '/food/cherry.png', name: 'Cherry', price: 50, description: 'Sweet cherries, a tasty snack.' },
  { icon: '/food/pumpkin.png', name: 'Pumpkin', price: 60, description: 'Healthy pumpkin, full of nutrients.' },
  { icon: '/food/soju.png', name: 'Soju', price: 100, description: 'Special drink for celebrating!' }
])

/* ==== Shopkeeper Animation ==== */
const shopkeeperState = ref('happytalk')  // happytalk, neutral, annoyedclosed, disbeliefsmile
let talkingInterval = null

const shopkeeperImage = computed(() => {
  const images = {
    happytalk: '/shopkeeper/sk_bb_happytalk.png',
    neutral: '/shopkeeper/sk_bb_neutral.png',
    annoyedclosed: '/shopkeeper/sk_bb_annoyedclosed.png',
    disbeliefsmile: '/shopkeeper/sk_bb_disbeliefsmile.png',
    disbelieflaugh: '/shopkeeper/sk_bb_disbelieflaugh.png'
  }

  return images[shopkeeperState.value]
})

function startNoMoneyAnimation() {
  // Start with disbelieflaugh when player has no money
  shopkeeperState.value = 'disbelieflaugh'

  // Alternate between disbelieflaugh and disbeliefsmile for 3 seconds
  let elapsed = 0
  let isLaugh = true

  talkingInterval = setInterval(() => {
    if (elapsed >= 3000) {
      // After 3 seconds, stop at disbeliefsmile
      shopkeeperState.value = 'disbeliefsmile'
      clearInterval(talkingInterval)
      talkingInterval = null
    } else {
      // Toggle between disbelieflaugh and disbeliefsmile every 500ms
      isLaugh = !isLaugh
      shopkeeperState.value = isLaugh ? 'disbelieflaugh' : 'disbeliefsmile'
      elapsed += 500
    }
  }, 500)
}

function startTalkingAnimation() {
  // Check if player has no money - use different animation
  if (playerGold.value === 0) {
    startNoMoneyAnimation()
    return
  }

  // Reset to happytalk when shop opens
  shopkeeperState.value = 'happytalk'

  // Alternate between happytalk and neutral for 5 seconds
  let elapsed = 0
  let isHappy = true

  talkingInterval = setInterval(() => {
    if (elapsed >= 3000) {
      // After 5 seconds, stop at neutral
      shopkeeperState.value = 'neutral'
      clearInterval(talkingInterval)
      talkingInterval = null
    } else {
      // Toggle between happytalk and neutral every 500ms
      isHappy = !isHappy
      shopkeeperState.value = isHappy ? 'happytalk' : 'neutral'
      elapsed += 500
    }
  }, 500)
}

function handleShopkeeperClick() {
  // Clear any ongoing animation
  if (talkingInterval) {
    clearInterval(talkingInterval)
    talkingInterval = null
  }
  // Switch to annoyed
  shopkeeperState.value = 'annoyedclosed'

  // Return to neutral after 1.5 seconds
  setTimeout(() => {
    shopkeeperState.value = 'neutral'
  }, 1500)
}

// Watch for shop opening
watch(showShop, (isOpen) => {
  if (isOpen) {
    startTalkingAnimation()
  } else {
    // Clean up animation when shop closes
    if (talkingInterval) {
      clearInterval(talkingInterval)
      talkingInterval = null
    }
  }
})

function toggleShop() {
  showShop.value = !showShop.value
}

async function buyFood(item) {
  if (playerGold.value !== null && playerGold.value >= item.price) {
    // Check if inventory is full (16 unique items max)
    if (inventory.value.length >= INVENTORY_SLOTS) {
      const existingItem = inventory.value.find(f => f.name === item.name)
      if (!existingItem) {
        alert('Inventory is full! Please use some items first.')
        return
      }
    }

    const newCoinAmount = playerGold.value - item.price

    // Use the shared updateCoins function
    const result = await updateCoins(newCoinAmount)

    if (result.success) {
      // Add to inventory: if same item exists, increase count; otherwise add new slot
      const existingItem = inventory.value.find(f => f.name === item.name)
      if (existingItem) {
        existingItem.count++
      } else {
        inventory.value.push({ icon: item.icon, name: item.name, count: 1 })
      }

      // Save inventory to backend
      saveInventory()

      // Check if player can't afford any item after purchase
      const cheapestPrice = Math.min(...shopItems.value.map(i => i.price))
      if (newCoinAmount < cheapestPrice) {
        // Clear any ongoing animation
        if (talkingInterval) {
          clearInterval(talkingInterval)
          talkingInterval = null
        }
        // Start the no-money animation
        startNoMoneyAnimation()
      }
    } else {
      alert('Failed to purchase item: ' + (result.error || 'Please try again'))
    }
  } else if (playerGold.value !== null && playerGold.value < item.price) {
    // Not enough money - show disbeliefsmile animation
    if (talkingInterval) {
      clearInterval(talkingInterval)
      talkingInterval = null
    }
    shopkeeperState.value = 'disbeliefsmile'

    // Return to disbeliefsmile after 2 seconds (stay in no-money state)
    setTimeout(() => {
      shopkeeperState.value = 'disbeliefsmile'
    }, 2000)
  }
}

// Fetch coins and inventory when component mounts
onMounted(() => {
  if (playerGold.value === null && !coinsLoading.value) {
    fetchCoins()
  }
  // Always fetch inventory on mount
  fetchInventory()
})
</script>

<template>
  <div class="pet-page-container">
    <!-- Main Content -->
    <div class="main-content">
      <div
        class="pet-stage"
        @drop="onDrop"
        @dragover="onDragOver"
      >
        <!-- Tile-based background -->
        <TileBackground
          :key="currentMapKey"
          :map-data="currentMapData"
          :tile-size="32"
          :scale="1"
          @collision-map-ready="handleCollisionMapReady"
        />

        <!-- 🔑 key makes sure AnimatedPet remounts when selectedPetKey changes -->
        <AnimatedPet
          :key="selectedPetKey"
          :sprite-url="PETS[selectedPetKey].config.spriteUrl"
          :slice="PETS[selectedPetKey].config.slice"
          :scale="PETS[selectedPetKey].config.scale"
          :speed="PETS[selectedPetKey].config.speed"
          :animations="PETS[selectedPetKey].config.animations"
          :dropped-items="droppedItems"
          :collision-map="collisionData.collisionMap"
          :tile-size="collisionData.tileSize"
          :map-cols="collisionData.cols"
          :map-rows="collisionData.rows"
          :manual-control="manualControlEnabled"
          @item-eaten="removeDroppedItem"
          @border-warning="handleBorderWarning"
        />

        <!-- Dropped items on background -->
        <div
          v-for="item in droppedItems"
          :key="item.id"
          class="dropped-item"
          :style="{ left: (item.x) + 'px',
           top: item.y + 'px' }"
        >
          <img :src="item.icon" :alt="item.name" class="dropped-food-image" />
        </div>
      </div>
      
              <!-- Shop Button -->
              <button class="shop-button" @click="toggleShop">
                <img src="/shopkeeper/shop_cart_sized.png" alt="Shop" class="shop-icon" />
              </button>

              <!-- Border Warning Popup -->
              <div v-if="showBorderWarning" class="border-warning">
                <div class="warning-icon">⚠️</div>
                <div class="warning-text">Why are you trying to drag your pet into the VOID</div>
              </div>
    </div>

    <!-- Right Panel -->
    <div class="right-panel">
      <!-- Pet Status -->
      <div class="panel-section">
        <h4 class="section-title">Pet Status</h4>
        <div class="status-item">
          <span class="status-label">Happy</span>
          <div class="status-bar"><div class="status-fill" :style="{ width: `${petStatus.happiness}%` }"></div></div>
          <span class="status-value">{{ petStatus.happiness }}%</span>
        </div>
        <div class="status-item">
          <span class="status-label">Health</span>
          <div class="status-bar"><div class="status-fill health" :style="{ width: `${petStatus.health}%` }"></div></div>
          <span class="status-value">{{ petStatus.health }}%</span>
        </div>
        
      </div>

      <!-- Inventory -->
      <div class="panel-section">
        <h4 class="section-title">Inventory</h4>
        <div class="inventory-grid">
          <div
            v-for="(item, index) in inventory"
            :key="index"
            class="inventory-slot filled"
            draggable="true"
            @dragstart="startDrag($event, item, index)"
            @click="feedPet(index)"
          >
            <div class="slot-icon">
              <img :src="item.icon" :alt="item.name" class="food-image" />
            </div>
            <div class="slot-count">{{ item.count }}</div>
          </div>
          <!-- Empty slots to fill the grid -->
          <div
            v-for="emptySlot in (INVENTORY_SLOTS - inventory.length)"
            :key="'empty-' + emptySlot"
            class="inventory-slot empty"
          >
          </div>
        </div>
      </div>

      <!-- Pet Select -->
      <div class="panel-section">
        <h4 class="section-title">Pet Select</h4>
        <div class="selection-container">
          <button class="nav-btn" @click="previousPet" :disabled="petIndex === 0">‹</button>

          <div class="item-display" @click="nextPet">
            <!-- 🔑 key forces preview to redraw as you scroll -->
            <SpritePreview
              :key="PETS[previewPetKey].config.spriteUrl + ':' + PETS[previewPetKey].config.slice"
              :sprite-url="PETS[previewPetKey].config.spriteUrl"
              :slice="PETS[previewPetKey].config.slice"
              :scale="2.5"
              :row="0"
              :col="0"
            />
            <div class="pet-name-small">{{ PETS[previewPetKey].label }}</div>
          </div>

          <button class="nav-btn" @click="nextPet" :disabled="petIndex === petKeys.length - 1">›</button>
        </div>

        <!-- Optional now; you can remove if you want instant-switch only -->
        <button class="action-btn" @click="selectPet">Select Pet</button>
      </div>

      <!-- Background -->
      <div class="panel-section">
        <h4 class="section-title">Map</h4>
        <div class="selection-container">
          <button class="nav-btn" @click="previousBackground" :disabled="bgIndex === 0">‹</button>
          <div class="item-display">
            <div class="map-name-display">{{ availableBackgrounds[bgIndex].name }}</div>
          </div>
          <button class="nav-btn" @click="nextBackground" :disabled="bgIndex === availableBackgrounds.length - 1">›</button>
        </div>
      </div>

      <!-- Manual Control -->
      <div class="panel-section">
        <h4 class="section-title">Controls</h4>
        <button
          class="control-toggle-btn"
          :class="{ active: manualControlEnabled }"
          @click="toggleManualControl"
        >
          
          <span class="control-text">{{ manualControlEnabled ? 'Manual (WASD)' : 'Auto Roam' }}</span>
        </button>
        <div v-if="manualControlEnabled" class="control-hint">
          Use W/A/S/D keys to move your pet
        </div>
      </div>
    </div>

    <!-- Shop Popup -->
    <div v-if="showShop" class="shop-overlay" @click="toggleShop">
      <div class="shop-popup" @click.stop>
        <div class="shop-header">
          <h3>Pet Shop</h3>
          <div class="header-gold">
            <template v-if="coinsLoading">
              <span class="gold-amount">Loading...</span>
            </template>
            <template v-else-if="coinsError">
              <span class="gold-amount error">Error: {{ coinsError }}</span>
            </template>
            <template v-else>
              <AnimatedCoin :scale="1.5" :speed="8" />
              <span class="gold-amount">{{ playerGold }}</span>
            </template>
          </div>
          <button class="close-shop" @click="toggleShop">×</button>
        </div>
        
        <div class="shop-content">
          <div class="shop-layout">
                    <!-- Character Dialogue Area -->
                    <div class="character-section">
                      <div class="character-portrait" @click="handleShopkeeperClick">
                        <img :src="shopkeeperImage" alt="Shopkeeper" class="character-image" />
                      </div>
                      <div class="character-name">Anya the Petkeeper</div>
                      <div class="dialogue-box">
                        <div class="dialogue-text">
                          <template v-if="coinsLoading">
                            Please wait while I check your coin balance...
                          </template>
                          <template v-else-if="coinsError">
                            Oh no! I can't check your coins right now. There seems to be a problem: {{ coinsError }}
                          </template>
                          <template v-else-if="playerGold === null">
                            I'm having trouble reading your coin balance. Please try again later.
                          </template>
                          <template v-else-if="playerGold > 0">
                            Welcome to the pet shop! How can I help you today? Be sure to have enough coins when you buy from me!
                          </template>
                          <template v-else>
                            Sorry, but you don't have any coins. Come back when you can afford something!
                          </template>
                        </div>
                      </div>
                    </div>
            
            <!-- Shop Items -->
            <div class="items-section">
              <div class="shop-items">
                <div
                  v-for="item in shopItems"
                  :key="item.name"
                  class="shop-item"
                >
                  <div class="item-icon">
                    <img :src="item.icon" :alt="item.name" class="food-image" />
                  </div>
                  <div class="item-info">
                    <div class="item-name">{{ item.name }}</div>
                    <div class="item-description">{{ item.description }}</div>
                  </div>
                  <div class="item-price">
                    <div class="price-container">
                      <AnimatedCoin :scale="1" :speed="8" />
                      <span class="price">{{ item.price }}</span>
                    </div>
                    <button
                      class="buy-btn"
                      @click="buyFood(item)"
                      :disabled="coinsLoading || coinsError || playerGold === null || playerGold < item.price"
                    >
                      Buy
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.pet-page-container{display:flex;height:100vh;overflow:hidden;}
.main-content{flex:1;display:flex;align-items:stretch;justify-content:stretch;padding:24px;position:relative;overflow:hidden;background-size:cover;background-position:center;margin-right:280px;}
.pet-stage{position:relative;width:100%;height:100%;overflow:hidden;}
.right-panel{width:280px;background:var(--surface);border-left:1px solid var(--surface-lighter);padding:24px 16px;overflow-y:auto;height:100vh;position:fixed;right:0;top:0;}
.panel-section{margin-bottom:32px;padding-bottom:24px;border-bottom:1px solid var(--surface-lighter);}
.section-title{font-weight:600;margin-bottom:16px;}
.status-item{display:flex;align-items:center;gap:12px;margin-bottom:8px;}
.status-label{width:60px;text-transform:capitalize;}
.status-bar{flex:1;height:8px;background:var(--surface-lighter);border-radius:4px;overflow:hidden;}
.status-fill{height:100%;background:var(--primary);}
.status-fill.health{background:#4ade80;}
.status-fill.energy{background:#f59e0b;}
.selection-container{display:flex;align-items:center;gap:12px;margin-bottom:12px;}
.nav-btn{width:32px;height:32px;border:1px solid var(--surface-lighter);background:var(--surface);border-radius:6px;cursor:pointer;}
.item-display{flex:1;display:flex;flex-direction:column;align-items:center;gap:8px;}
.item-icon{font-size:32px;width:48px;height:48px;display:grid;place-items:center;background:var(--surface-light);border-radius:12px;}
.item-count{font-size:12px;color:var(--text-muted);}
.pet-name-small{font-size:12px;}
.bg-preview{width:100%;height:48px;border-radius:8px;background-size:cover;background-position:center;display:flex;align-items:center;justify-content:center;overflow:hidden;}
.bg-name{background:rgba(0,0,0,0.7);color:#fff;padding:4px 8px;border-radius:4px;font-size:12px;}
.map-name-display{text-align:center;font-weight:600;color:var(--text-primary);padding:8px;background:var(--surface-light);border-radius:8px;font-size:14px;}
.action-btn{width:100%;padding:10px 16px;background:var(--primary);color:#fff;border:none;border-radius:8px;cursor:pointer;}

/* Control Toggle Button */
.control-toggle-btn{
  width:100%;
  padding:12px 16px;
  background:var(--surface-light);
  border:2px solid var(--surface-lighter);
  border-radius:8px;
  cursor:pointer;
  display:flex;
  align-items:center;
  gap:12px;
  transition:all 0.3s ease;
  font-size:14px;
  font-weight:600;
}
.control-toggle-btn:hover{
  background:var(--surface-lighter);
  border-color:var(--primary);
  transform:translateY(-1px);
}
.control-toggle-btn.active{
  background:var(--primary);
  border-color:var(--primary);
  color:#fff;
}
.control-icon{
  font-size:20px;
}
.control-text{
  flex:1;
  text-align:left;
}
.control-hint{
  margin-top:8px;
  padding:8px 12px;
  background:rgba(0,123,255,0.1);
  border-radius:6px;
  font-size:12px;
  color:var(--primary);
  text-align:center;
}

/* Inventory Grid */
.inventory-grid{
  display:grid;
  grid-template-columns:repeat(4, 1fr);
  grid-template-rows:repeat(4, 1fr);
  gap:8px;
}
.inventory-slot{
  position:relative;
  aspect-ratio:1;
  border:2px solid var(--surface-lighter);
  border-radius:8px;
  display:flex;
  align-items:center;
  justify-content:center;
  background:var(--surface-light);
  transition:all 0.2s ease;
}
.inventory-slot.empty{
  background:var(--surface);
  opacity:0.5;
}
.inventory-slot.filled{
  cursor:grab;
  background:var(--surface-light);
}
.inventory-slot.filled:active{
  cursor:grabbing;
}
.inventory-slot.filled:hover{
  border-color:var(--primary);
  transform:scale(1.05);
  box-shadow:0 2px 8px rgba(0,0,0,0.1);
}
.slot-icon{
  font-size:28px;
  width:100%;
  height:100%;
  display:flex;
  align-items:center;
  justify-content:center;
}
.food-image{
  width:100%;
  height:100%;
  object-fit:contain;
  image-rendering:pixelated;
}
.slot-count{
  position:absolute;
  bottom:4px;
  right:4px;
  background:rgba(0,0,0,0.7);
  color:#fff;
  font-size:10px;
  font-weight:bold;
  padding:2px 6px;
  border-radius:4px;
  min-width:16px;
  text-align:center;
}

/* Dropped Items on Background */
.dropped-item{
  position:absolute;
  width:40px;
  height:40px;
  pointer-events:none;
  animation:dropBounce 0.5s ease-out;
  z-index:10;
}
.dropped-food-image{
  width:100%;
  height:100%;
  object-fit:contain;
  image-rendering:pixelated;
}
@keyframes dropBounce{
  0%{transform:scale(0) translateY(-20px);opacity:0;}
  50%{transform:scale(1.2);}
  100%{transform:scale(1) translateY(0);opacity:1;}
}

/* Shop Button */
.shop-button{
  position:absolute;
  top:20px;
  right:20px;
  background:transparent;
  border:none;
  border-radius:8px;
  padding:8px;
  cursor:pointer;
  box-shadow:0 2px 8px rgba(0,0,0,0.2);
  transition:all 0.3s ease;
  z-index:100;
}
.shop-button:hover{
  transform:translateY(-2px);
  box-shadow:0 4px 12px rgba(0,0,0,0.3);
}
.shop-icon{
  width:40px;
  height:40px;
  object-fit:contain;
}

/* Shop Popup */
.shop-overlay{
  position:fixed;
  top:0;
  left:0;
  width:100vw;
  height:100vh;
  background:rgba(0,0,0,0.7);
  display:flex;
  align-items:center;
  justify-content:center;
  z-index:1000;
}
.shop-popup{
  background:var(--surface);
  border-radius:12px;
  width:700px;
  max-height:80vh;
  overflow:hidden;
  box-shadow:0 8px 32px rgba(0,0,0,0.3);
}
.shop-header{
  background:var(--primary);
  color:#fff;
  padding:16px 20px;
  display:flex;
  justify-content:space-between;
  align-items:center;
}
.shop-header h3{
  margin:0;
  font-size:18px;
}
.header-gold{
  background:rgba(255,255,255,0.2);
  padding:8px 12px;
  border-radius:6px;
  font-weight:600;
  font-size:14px;
  display:flex;
  align-items:center;
  gap:8px;
}
.gold-amount{
  color:#fff;
  font-weight:600;
  font-size:14px;
}
.gold-amount.error{
  color:#ff6b6b;
  font-size:12px;
}
.close-shop{
  background:none;
  border:none;
  color:#fff;
  font-size:24px;
  cursor:pointer;
  padding:0;
  width:32px;
  height:32px;
  display:flex;
  align-items:center;
  justify-content:center;
  border-radius:50%;
  transition:background 0.2s ease;
}
.close-shop:hover{
  background:rgba(255,255,255,0.2);
}
.shop-content{
  padding:20px;
  max-height:60vh;
  overflow:hidden;
}
.shop-layout{
  display:flex;
  gap:20px;
  height:100%;
}
.character-section{
  width:200px;
  display:flex;
  flex-direction:column;
  gap:12px;
  flex-shrink:0;
}
.character-portrait{
  width:100%;
  height:280px;
  background:var(--surface-light);
  border-radius:8px;
  display:flex;
  align-items:center;
  justify-content:center;
  overflow:hidden;
  cursor:pointer;
  transition:transform 0.2s ease, box-shadow 0.2s ease;
}
.character-portrait:hover{
  transform:scale(1.02);
  box-shadow:0 2px 8px rgba(0,0,0,0.2);
}
.character-portrait:active{
  transform:scale(0.98);
}
.character-image{
  width:100%;
  height:100%;
  object-fit:contain;
}
.character-name{
  text-align:center;
  font-weight:600;
  color:var(--text-primary);
  font-size:14px;
  margin-top:8px;
}
.dialogue-box{
  background:var(--surface-light);
  border:2px solid var(--primary);
  border-radius:8px;
  padding:12px;
  position:relative;
}
.dialogue-box::before{
  content:"";
  position:absolute;
  top:-8px;
  left:20px;
  width:0;
  height:0;
  border-left:8px solid transparent;
  border-right:8px solid transparent;
  border-bottom:8px solid var(--primary);
}
.dialogue-text{
  font-size:12px;
  line-height:1.4;
  color:var(--text-primary);
  font-style:italic;
}
.items-section{
  flex:1;
  display:flex;
  flex-direction:column;
  overflow-y:auto;
  max-height:50vh;
}
.shop-items{
  display:flex;
  flex-direction:column;
  gap:12px;
}
.shop-item{
  display:flex;
  align-items:center;
  gap:12px;
  padding:12px;
  background:var(--surface-light);
  border-radius:8px;
  border:1px solid var(--surface-lighter);
}
.item-icon{
  font-size:24px;
  width:40px;
  height:40px;
  display:flex;
  align-items:center;
  justify-content:center;
  background:var(--surface);
  border-radius:6px;
}
.item-info{
  flex:1;
}
.item-name{
  font-weight:600;
  color:var(--text-primary);
  margin-bottom:4px;
}
.item-description{
  font-size:12px;
  color:var(--text-muted);
  line-height:1.4;
}
.item-price{
  display:flex;
  flex-direction:column;
  align-items:flex-end;
  gap:8px;
}
.price-container{
  display:flex;
  align-items:center;
  gap:4px;
}
.price{
  font-weight:600;
  color:var(--primary);
}
.buy-btn{
  background:var(--primary);
  color:#fff;
  border:none;
  border-radius:6px;
  padding:6px 12px;
  font-size:12px;
  font-weight:600;
  cursor:pointer;
  transition:all 0.2s ease;
}
.buy-btn:hover:not(:disabled){
  background:var(--primary-dark);
  transform:translateY(-1px);
}
.buy-btn:disabled{
  background:var(--surface-lighter);
  color:var(--text-muted);
  cursor:not-allowed;
}

/* Border Warning Popup */
.border-warning{
  position:absolute;
  top:50%;
  left:50%;
  transform:translate(-50%, -50%);
  background:rgba(255, 59, 48, 0.95);
  color:#fff;
  padding:16px 24px;
  border-radius:12px;
  box-shadow:0 8px 24px rgba(0,0,0,0.3);
  display:flex;
  align-items:center;
  gap:12px;
  z-index:9999;
  animation:warningSlide 0.3s ease-out;
  font-weight:600;
  font-size:14px;
}
.warning-icon{
  font-size:24px;
  animation:warningShake 0.5s ease-in-out infinite;
}
.warning-text{
  white-space:nowrap;
}
@keyframes warningSlide{
  from{
    opacity:0;
    transform:translate(-50%, -60%);
  }
  to{
    opacity:1;
    transform:translate(-50%, -50%);
  }
}
@keyframes warningShake{
  0%, 100%{transform:rotate(0deg);}
  25%{transform:rotate(-10deg);}
  75%{transform:rotate(10deg);}
}
</style>
