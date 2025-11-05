<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import AnimatedPet from '@/components/AnimatedPet.vue'
import AnimatedCoin from '@/components/AnimatedCoin.vue'
import TMXTileBackground from '@/components/TMXTileBackground.vue'
import PetMinigame from '@/components/PetMinigame.vue'
import SpritePreview from '@/components/SpritePreview.vue'
import { useCoins } from '@/composables/useCoins.js'
import { useGlobalPet } from '@/composables/useGlobalPet.js'
import { api } from '@/lib/api.js'
import { PET_CATALOG } from '@/data/petCatalog.js'

/* ================= PET CATALOG ================= */
const PETS = PET_CATALOG

/* ==== Status ==== */
const petStatus = reactive({ happiness: 100, health: 100, energy: 60, is_dead: false, soju_count: 0 })
const petStatusLoading = ref(false)

// Computed property for death state
const isPetDead = computed(() => petStatus.is_dead || petStatus.happiness === 0 || petStatus.health === 0)

// Alert state for low stats
const showLowStatsAlert = ref(false)
const lowStatsMessage = ref('')

// Soju emote state
const showSojuEmote = ref(false)
const sojuEmoteType = ref('happy') // 'happy' or 'drunk'
const isDrunk = ref(false) // Track if pet is currently drunk (3rd+ drink)

/* ==== Inventory ==== */
const INVENTORY_SLOTS = 16  // 4 rows x 4 columns
const inventory = ref([])  // Empty initially, items added when purchased
const inventoryLoading = ref(false)
const inventoryError = ref(null)

/* ==== Dropped Items (on background) ==== */
const droppedItems = ref([])  // Items dropped on the background for pet to eat
let nextDroppedItemId = 0

/* ==== Global Pet State ==== */
const {
  selectedPetKey: globalPetKey,
  petStatus: globalPetStatus,
  updatePetStatus,
  setPetDead
} = useGlobalPet()
const selectedPetKey = computed(() => globalPetKey.value) // Active pet from global state

/* ==== TMX Map Backgrounds ==== */
const tmxMapPath = ref('/background/pet map.tmx')

// Collision data from TMX map
const collisionData = ref({
  collisionObjects: [],
  mapWidth: 0,
  mapHeight: 0,
  scale: 1
})

function handleCollisionReady(data) {
  collisionData.value = data
  console.log('Collision data ready:', data)
}

function handleMapLoaded(data) {
  console.log('TMX map loaded:', data)
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

/* ==== Pet Status API ==== */
async function fetchPetStatus() {
  petStatusLoading.value = true
  try {
    const response = await api.get('/api/profile/pet-status')
    if (response) {
      petStatus.happiness = response.happiness ?? 100
      petStatus.health = response.health ?? 100
      petStatus.is_dead = response.is_dead ?? false
      petStatus.soju_count = response.soju_count ?? 0

      // Sync to global pet status
      updatePetStatus({
        happiness: petStatus.happiness,
        health: petStatus.health,
        isDead: petStatus.is_dead || petStatus.happiness === 0 || petStatus.health === 0
      })
      setPetDead(petStatus.is_dead || petStatus.happiness === 0 || petStatus.health === 0)

      // Show alert if pet needs food
      checkPetNeeds()
    }
  } catch (error) {
    console.error('Failed to fetch pet status:', error)
  } finally {
    petStatusLoading.value = false
  }
}

async function savePetStatus() {
  try {
    const response = await api.put('/api/profile/pet-status', {
      happiness: petStatus.happiness,
      health: petStatus.health,
      soju_count: petStatus.soju_count
    })
    if (response && response.ok) {
      console.log('Pet status saved successfully')
      // Update is_dead status from server response
      if (response.pet_status) {
        petStatus.is_dead = response.pet_status.is_dead
      }
    }
  } catch (error) {
    console.error('Failed to save pet status:', error)
  }
}

function checkPetNeeds() {
  // Check if pet is dead
  if (petStatus.is_dead || petStatus.happiness === 0 || petStatus.health === 0) {
    lowStatsMessage.value = 'Your pet has died! Feed it to revive it.'
    showLowStatsAlert.value = true
    return
  }

  // Check if pet needs food urgently (below 20)
  if (petStatus.happiness < 20 || petStatus.health < 20) {
    lowStatsMessage.value = 'Your pet is starving! Feed it immediately!'
    showLowStatsAlert.value = true
    return
  }

  // Check if pet needs food soon (below 40)
  if (petStatus.happiness < 40 || petStatus.health < 40) {
    lowStatsMessage.value = 'Your pet is getting hungry. Feed it soon!'
    showLowStatsAlert.value = true
    return
  }

  // Pet is healthy
  showLowStatsAlert.value = false
}

/* ==== Inventory actions ==== */
function feedPet(slotIndex) {
  const item = inventory.value[slotIndex]
  if (item && item.count > 0) {
    // Find food configuration by name
    const foodConfig = shopItems.value.find(shopItem => shopItem.name === item.name)

    item.count--

    // Check if item is soju
    const isSoju = item.name === 'Soju'

    if (isSoju && foodConfig) {
      // Handle soju consumption
      petStatus.soju_count++
      console.log('Soju consumed (clicked)! Count:', petStatus.soju_count)

      if (petStatus.soju_count <= 2) {
        // First 2 drinks: use configured happiness value
        const happinessGain = foodConfig.soju_1st_2nd_happiness || 10
        petStatus.happiness = Math.min(100, petStatus.happiness + happinessGain)
        sojuEmoteType.value = 'happy'
        console.log(`First/Second soju: +${happinessGain} happiness`)

        // Show soju emote for 2.5 seconds
        showSojuEmote.value = true
        setTimeout(() => {
          showSojuEmote.value = false
        }, 2500)
      } else {
        // 3rd drink onwards: use configured values
        const happinessGain = foodConfig.soju_3rd_plus_happiness || 20
        const healthChange = foodConfig.soju_3rd_plus_health || -20
        petStatus.happiness = Math.min(100, petStatus.happiness + happinessGain)
        petStatus.health = Math.max(0, petStatus.health + healthChange)
        sojuEmoteType.value = 'drunk'
        console.log(`Third+ soju: +${happinessGain} happiness, ${healthChange} health - PET IS DRUNK!`)

        // Set drunk state for 5 seconds
        isDrunk.value = true
        showSojuEmote.value = true

        setTimeout(() => {
          isDrunk.value = false
          showSojuEmote.value = false
        }, 5000)
      }

      petStatus.is_dead = false  // Revive pet if it was dead
    } else if (foodConfig) {
      // Regular food: use configured happiness and health values
      const happinessGain = foodConfig.happiness || 10
      const healthGain = foodConfig.health || 5
      petStatus.happiness = Math.min(100, petStatus.happiness + happinessGain)
      petStatus.health = Math.min(100, petStatus.health + healthGain)
      petStatus.is_dead = false  // Revive pet if it was dead
      console.log(`Regular food (clicked): +${happinessGain} happiness, +${healthGain} health`)
    } else {
      // Fallback if item not found in configuration
      console.warn('Food configuration not found for:', item.name)
      petStatus.happiness = Math.min(100, petStatus.happiness + 10)
      petStatus.health = Math.min(100, petStatus.health + 5)
      petStatus.is_dead = false
    }

    // Remove item from inventory if count reaches 0
    if (item.count === 0) {
      inventory.value.splice(slotIndex, 1)
    }

    console.log('Updated stats - Happiness:', petStatus.happiness, 'Health:', petStatus.health)

    // Save inventory and pet status to backend
    saveInventory()
    savePetStatus()
    checkPetNeeds()
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

    // Find food configuration by name
    const foodConfig = shopItems.value.find(item => item.name === removedItem.name)

    // Check if item is soju
    const isSoju = removedItem.name === 'Soju'

    if (isSoju && foodConfig) {
      // Handle soju consumption
      petStatus.soju_count++
      console.log('Soju consumed! Count:', petStatus.soju_count)

      if (petStatus.soju_count <= 2) {
        // First 2 drinks: use configured happiness value
        const happinessGain = foodConfig.soju_1st_2nd_happiness || 10
        petStatus.happiness = Math.min(100, petStatus.happiness + happinessGain)
        sojuEmoteType.value = 'happy'
        console.log(`First/Second soju: +${happinessGain} happiness`)

        // Show soju emote for 2.5 seconds
        showSojuEmote.value = true
        setTimeout(() => {
          showSojuEmote.value = false
        }, 2500)
      } else {
        // 3rd drink onwards: use configured values
        const happinessGain = foodConfig.soju_3rd_plus_happiness || 20
        const healthChange = foodConfig.soju_3rd_plus_health || -20
        petStatus.happiness = Math.min(100, petStatus.happiness + happinessGain)
        petStatus.health = Math.max(0, petStatus.health + healthChange)
        sojuEmoteType.value = 'drunk'
        console.log(`Third+ soju: +${happinessGain} happiness, ${healthChange} health - PET IS DRUNK!`)

        // Set drunk state for 5 seconds
        isDrunk.value = true
        showSojuEmote.value = true

        setTimeout(() => {
          isDrunk.value = false
          showSojuEmote.value = false
        }, 5000) // 5 seconds drunk state
      }

      petStatus.is_dead = false  // Revive pet if it was dead
    } else if (foodConfig) {
      // Regular food: use configured happiness and health values
      const happinessGain = foodConfig.happiness || 10
      const healthGain = foodConfig.health || 5
      petStatus.happiness = Math.min(100, petStatus.happiness + happinessGain)
      petStatus.health = Math.min(100, petStatus.health + healthGain)
      petStatus.is_dead = false  // Revive pet if it was dead
      console.log(`Regular food: +${happinessGain} happiness, +${healthGain} health`)
    } else {
      // Fallback if item not found in configuration
      console.warn('Food configuration not found for:', removedItem.name)
      petStatus.happiness = Math.min(100, petStatus.happiness + 10)
      petStatus.health = Math.min(100, petStatus.health + 5)
      petStatus.is_dead = false
    }

    console.log('Updated stats - Happiness:', petStatus.happiness, 'Health:', petStatus.health)

    // Save updated status to backend
    savePetStatus()

    // Check if pet still needs food
    checkPetNeeds()
  } else {
    console.log('Item not found in droppedItems array!')
  }
}

/* ==== Manual Control ==== */
const manualControlEnabled = ref(false)

/* ==== Test Functions ==== */
function testDeteriorate() {
  // Decrease happiness and health by 15 points
  petStatus.happiness = Math.max(0, petStatus.happiness - 15)
  petStatus.health = Math.max(0, petStatus.health - 15)

  // Update death state
  if (petStatus.happiness === 0 || petStatus.health === 0) {
    petStatus.is_dead = true
  }

  // Save to backend
  savePetStatus()

  // Check and show alerts
  checkPetNeeds()

  console.log('Test deteriorate: Happiness:', petStatus.happiness, 'Health:', petStatus.health)
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

/* ==== Pet Switching ==== */
const showPetSwitch = ref(false)
const selectedNewPet = ref(null)
const PET_SWITCH_COST = 10000
const showPetSwitchCelebration = ref(false)
const switchedPetInfo = ref(null)

// Pet descriptions for shop
const petDescriptions = {
  catBlack: "A mysterious black cat with a calm demeanor.",
  catGrey: "A gentle grey cat that loves to explore.",
  catNew: "A playful orange cat full of energy.",
  dogBlonde: "A loyal blonde dog that's always happy.",
  dogGrey: "A wise grey dog with a gentle nature.",
  dogLight: "A friendly light brown dog full of enthusiasm."
}

function showSwitchCelebration(petKey, petLabel) {
  switchedPetInfo.value = { key: petKey, label: petLabel }
  showPetSwitchCelebration.value = true

  // Auto-hide after 3.5 seconds
  setTimeout(() => {
    showPetSwitchCelebration.value = false
    switchedPetInfo.value = null
  }, 3500)
}

function openPetSwitch() {
  showPetSwitch.value = true
  selectedNewPet.value = null
}

function closePetSwitch() {
  showPetSwitch.value = false
  selectedNewPet.value = null
}

function selectNewPet(petKey) {
  selectedNewPet.value = petKey
}

async function confirmPetSwitch() {
  if (!selectedNewPet.value) return

  // Check if user is trying to select the same pet
  if (selectedNewPet.value === selectedPetKey.value) {
    alert('You already have this pet!')
    return
  }

  // Check if user has enough coins
  if (playerGold.value < PET_SWITCH_COST) {
    alert(`You need ${PET_SWITCH_COST} coins to switch pets!`)
    return
  }

  try {
    // Deduct coins
    const newCoinAmount = playerGold.value - PET_SWITCH_COST
    const result = await updateCoins(newCoinAmount)

    if (!result.success) {
      alert('Failed to process payment: ' + (result.error || 'Please try again'))
      return
    }

    // Update pet in backend
    const response = await api.post('/api/profile/switch-pet', {
      pet_key: selectedNewPet.value
    })

    if (response && response.ok) {
      // Store the pet info before closing the dialog
      const newPetKey = selectedNewPet.value
      const newPetLabel = PETS[selectedNewPet.value].label

      // Update global pet state
      globalPetKey.value = newPetKey

      // Close the dialog
      closePetSwitch()

      // Show celebration animation
      showSwitchCelebration(newPetKey, newPetLabel)
    } else {
      // Refund coins if backend update failed
      await updateCoins(playerGold.value + PET_SWITCH_COST)
      alert('Failed to switch pet. Please try again.')
    }
  } catch (error) {
    console.error('Error switching pet:', error)
    // Try to refund coins
    await updateCoins(playerGold.value + PET_SWITCH_COST)
    alert('An error occurred while switching pets. Please try again.')
  }
}

/* ==== Minigame ==== */
const showMinigame = ref(false)

function toggleMinigame() {
  showMinigame.value = !showMinigame.value
}

// Use shared coin state
const { coins: playerGold, coinsLoading, coinsError, fetchCoins, updateCoins } = useCoins()

const shopItems = ref([
  {
    icon: '/food/fish.png',
    name: 'Fish',
    price: 80,
    description: 'Fresh fish, a premium treat for pets.',
    happiness: 15,
    health: 15
  },
  {
    icon: '/food/milk.png',
    name: 'Milk',
    price: 40,
    description: 'Fresh milk, good for growing pets.',
    happiness: 10,
    health: 10
  },
  {
    icon: '/food/beef.png',
    name: 'Beef',
    price: 120,
    description: 'Premium beef, the ultimate pet treat.',
    happiness: 25,
    health: 20
  },
  {
    icon: '/food/shrimp.png',
    name: 'Shrimp',
    price: 90,
    description: 'Delicious shrimp, a seafood delight.',
    happiness: 18,
    health: 12
  },
  {
    icon: '/food/cherry.png',
    name: 'Cherry',
    price: 50,
    description: 'Sweet cherries, a tasty snack.',
    happiness: 12,
    health: 8
  },
  {
    icon: '/food/pumpkin.png',
    name: 'Pumpkin',
    price: 60,
    description: 'Healthy pumpkin, full of nutrients.',
    happiness: 10,
    health: 18
  },
  {
    icon: '/food/soju.png',
    name: 'Soju',
    price: 100,
    description: 'Special drink for celebrating! Bad things happen after the 2nd drink',
    // Soju has special logic: first 2 drinks vs 3rd+ drinks
    soju_1st_2nd_happiness: 20,
    soju_3rd_plus_happiness: -10,
    soju_3rd_plus_health: -20
  }
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

  // Fetch pet status on mount
  fetchPetStatus()
})

// Watch pet status and save periodically (debounced)
let saveStatusTimeout = null
watch(() => [petStatus.happiness, petStatus.health], () => {
  // Debounce saving to avoid too many requests
  if (saveStatusTimeout) {
    clearTimeout(saveStatusTimeout)
  }
  saveStatusTimeout = setTimeout(() => {
    savePetStatus()
    checkPetNeeds()
  }, 2000)  // Save 2 seconds after last change

  // Sync happiness and health to global pet status
  updatePetStatus({
    happiness: petStatus.happiness,
    health: petStatus.health
  })
})

// Watch dead state and sync to global pet
watch(isPetDead, (newIsDead) => {
  setPetDead(newIsDead)
  console.log('Pet dead state synced to global:', newIsDead)
})

// Daily tasks state
const showDailyTasks = ref(false)
const dailyTasks = ref([
  { id: 'pet', label: 'Pet your pet', completed: false },
  { id: 'study', label: 'Complete one 25 min study session', completed: false },
  { id: 'checkin', label: "Do today's wellness check-in", completed: false }
])

function getTodayKey() {
  const d = new Date()
  return `dailyTasks-${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`
}

function loadDailyTasks() {
  try {
    const saved = localStorage.getItem(getTodayKey())
    if (saved) {
      const parsed = JSON.parse(saved)
      dailyTasks.value = dailyTasks.value.map(t => ({ ...t, completed: !!parsed[t.id] }))
    }
  } catch {}
}

function saveDailyTasks() {
  const map = dailyTasks.value.reduce((acc, t) => { acc[t.id] = !!t.completed; return acc }, {})
  try { localStorage.setItem(getTodayKey(), JSON.stringify(map)) } catch {}
}

function toggleTask(task) {
  task.completed = !task.completed
  saveDailyTasks()
}

onMounted(() => {
  loadDailyTasks()
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
        <!-- TMX Map Background -->
        <TMXTileBackground
          :tmx-path="tmxMapPath"
          @collision-ready="handleCollisionReady"
          @map-loaded="handleMapLoaded"
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
          :manual-control="manualControlEnabled"
          :collision-objects="collisionData.collisionObjects"
          :is-dead="isPetDead"
          :is-drunk="isDrunk"
          :show-soju-emote="showSojuEmote"
          :soju-emote-type="sojuEmoteType"
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

              <!-- Low Stats Alert -->
              <div v-if="showLowStatsAlert" class="low-stats-alert" :class="{ 'dead-alert': isPetDead }">
                <div class="alert-content">
                  {{ lowStatsMessage }}
                </div>
                <button @click="showLowStatsAlert = false" class="close-alert">×</button>
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

      <!-- Daily Tasks (moved from floating dialog into sidebar) -->
      <div class="panel-section">
        <h4 class="section-title">Daily Tasks</h4>
        <v-list density="compact" class="daily-task-list">
          <v-list-item
            v-for="task in dailyTasks"
            :key="task.id"
            @click="toggleTask(task)"
            class="daily-task-item"
          >
            <template #prepend>
              <v-checkbox-btn :model-value="task.completed" color="primary"></v-checkbox-btn>
            </template>
            <v-list-item-title class="wrap-text">{{ task.label }}</v-list-item-title>
          </v-list-item>
        </v-list>
      </div>

      <!-- Minigame Section -->
      <div class="panel-section">
        <h4 class="section-title">Mini Game</h4>
        <div class="minigame-section">
          <p class="minigame-description">Play once per day to earn coins!</p>
          <button class="action-btn minigame-action-btn" @click="toggleMinigame">
            
            Play Game
          </button>
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

      <!-- Testing -->
      <div class="panel-section">
        <button
          class="test-deteriorate-btn"
          @click="testDeteriorate"
        >
           Test Deteriorate (-15)
        </button>
      </div>
    </div>

    <!-- Minigame Overlay -->
    <div v-if="showMinigame" class="minigame-overlay" @click="toggleMinigame">
      <div class="minigame-popup" @click.stop>
        <button class="close-minigame" @click="toggleMinigame">×</button>
        <PetMinigame
          :pet-sprite-url="PETS[selectedPetKey].config.spriteUrl"
          :pet-slice="PETS[selectedPetKey].config.slice"
          :pet-scale="PETS[selectedPetKey].config.scale"
          :pet-animations="PETS[selectedPetKey].config.animations"
        />
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

                <!-- Pet Switching Special Item -->
                <div class="shop-item special-item">
                  <div class="item-icon special-icon">
                    🔄
                  </div>
                  <div class="item-info">
                    <div class="item-name">Switch Pet</div>
                    <div class="item-description">Change your pet companion to a different species!</div>
                  </div>
                  <div class="item-price">
                    <div class="price-container">
                      <AnimatedCoin :scale="1" :speed="8" />
                      <span class="price">{{ PET_SWITCH_COST }}</span>
                    </div>
                    <button
                      class="buy-btn special-btn"
                      @click="openPetSwitch"
                      :disabled="coinsLoading || coinsError || playerGold === null || playerGold < PET_SWITCH_COST"
                    >
                      Switch
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Pet Switching Dialog -->
    <div v-if="showPetSwitch" class="shop-overlay" @click="closePetSwitch">
      <div class="pet-switch-popup" @click.stop>
        <div class="pet-switch-header">
          <h3>Switch Your Pet</h3>
          <div class="header-gold">
            <AnimatedCoin :scale="1.5" :speed="8" />
            <span class="gold-amount">{{ playerGold }}</span>
          </div>
          <button class="close-shop" @click="closePetSwitch">×</button>
        </div>

        <div class="pet-switch-content">
          <p class="switch-description">
            Choose a new pet companion! Cost: <AnimatedCoin :scale="1" :speed="8" style="display: inline-block; vertical-align: middle;" /> <strong>{{ PET_SWITCH_COST }} coins</strong>
          </p>

          <div class="pet-switch-grid">
            <div
              v-for="(pet, key) in PETS"
              :key="key"
              class="pet-switch-card"
              :class="{
                'selected': selectedNewPet === key,
                'current': key === selectedPetKey,
                'disabled': key === selectedPetKey
              }"
              @click="key !== selectedPetKey && selectNewPet(key)"
            >
              <div class="pet-switch-preview">
                <SpritePreview
                  :sprite-url="pet.config.spriteUrl"
                  :slice="pet.config.slice"
                  :scale="2"
                  :row="0"
                  :col="0"
                />
              </div>
              <div class="pet-switch-info">
                <h4 class="pet-switch-name">{{ pet.label }}</h4>
                <p class="pet-switch-desc">{{ petDescriptions[key] }}</p>
                <span v-if="key === selectedPetKey" class="current-badge">Current Pet</span>
              </div>
            </div>
          </div>

          <div class="pet-switch-actions">
            <button class="cancel-switch-btn" @click="closePetSwitch">
              Cancel
            </button>
            <button
              class="confirm-switch-btn"
              :disabled="!selectedNewPet || selectedNewPet === selectedPetKey || playerGold < PET_SWITCH_COST"
              @click="confirmPetSwitch"
            >
              Switch Pet ({{ PET_SWITCH_COST }} coins)
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Pet Switch Celebration -->
    <div v-if="showPetSwitchCelebration" class="pet-switch-celebration-overlay">
      <div class="pet-switch-celebration">
        <div class="celebration-sparkle">✨</div>
        <div class="celebration-icon-container">
          <SpritePreview
            v-if="switchedPetInfo"
            :sprite-url="PETS[switchedPetInfo.key].config.spriteUrl"
            :slice="PETS[switchedPetInfo.key].config.slice"
            :scale="4"
            :row="0"
            :col="0"
          />
        </div>
        <div class="celebration-title">Pet Switched!</div>
        <div class="celebration-subtitle">{{ switchedPetInfo?.label }}</div>
        <div class="celebration-message">Your new companion is ready!</div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.pet-page-container{
  display:flex;
  height:100vh;
  overflow:hidden;
}

@media (max-width: 960px) {
  .pet-page-container {
    flex-direction: column;
  }
}

.main-content{
  flex:1;
  display:flex;
  align-items:stretch;
  justify-content:stretch;
  padding:24px;
  position:relative;
  overflow:hidden;
  background-size:cover;
  background-position:center;
  margin-right:280px;
}

@media (max-width: 960px) {
  .main-content {
    margin-right: 0;
    padding: 12px;
    height: auto;
    max-height: 35vh;
    flex-shrink: 0;
    overflow: hidden;
  }
  
  .pet-stage {
    height: 100%;
    max-height: 35vh;
    overflow: hidden;
  }
}

.pet-stage{
  position:relative;
  width:100%;
  height:100%;
  overflow:hidden;
}

.right-panel{
  width:280px;
  background:var(--surface);
  border-left:1px solid var(--surface-lighter);
  padding:24px 16px;
  overflow-y:auto;
  height:100vh;
  position:fixed;
  right:0;
  top:0;
}

@media (max-width: 960px) {
  .right-panel {
    width: 100%;
    position: relative;
    height: auto;
    flex: 1;
    min-height: 0;
    border-left: none;
    border-top: 1px solid var(--surface-lighter);
    padding: 16px 12px;
    overflow-y: auto;
  }
}
.panel-section{
  margin-bottom:32px;
  padding-bottom:24px;
  border-bottom:1px solid var(--surface-lighter);
}

@media (max-width: 960px) {
  .panel-section {
    margin-bottom: 20px;
    padding-bottom: 16px;
  }
}

.section-title{
  font-weight:600;
  margin-bottom:16px;
  font-size: 14px;
}

@media (max-width: 960px) {
  .section-title {
    font-size: 13px;
    margin-bottom: 12px;
  }
}
.status-item{
  display:flex;
  align-items:center;
  gap:12px;
  margin-bottom:8px;
}

@media (max-width: 960px) {
  .status-item {
    gap: 8px;
    margin-bottom: 6px;
  }
}

.status-label{
  width:60px;
  text-transform:capitalize;
  font-size: 13px;
}

@media (max-width: 960px) {
  .status-label {
    width: 50px;
    font-size: 12px;
  }
}
.status-bar{flex:1;height:8px;background:var(--surface-lighter);border-radius:4px;overflow:hidden;}
.status-fill{height:100%;background:var(--primary);}
.status-fill.health{background:#4ade80;}
.status-fill.energy{background:#f59e0b;}
.selection-container{
  display:flex;
  align-items:center;
  gap:12px;
  margin-bottom:12px;
}

@media (max-width: 960px) {
  .selection-container {
    gap: 8px;
    margin-bottom: 10px;
  }
}
.nav-btn{width:32px;height:32px;border:1px solid var(--surface-lighter);background:var(--surface);border-radius:6px;cursor:pointer;}
.item-display{flex:1;display:flex;flex-direction:column;align-items:center;gap:8px;}
.item-icon{font-size:32px;width:48px;height:48px;display:grid;place-items:center;background:var(--surface-light);border-radius:12px;}
.item-count{font-size:12px;color:var(--text-muted);}
.pet-name-small{
  font-size:12px;
}

@media (max-width: 960px) {
  .pet-name-small {
    font-size: 11px;
  }
}
.bg-preview{width:100%;height:48px;border-radius:8px;background-size:cover;background-position:center;display:flex;align-items:center;justify-content:center;overflow:hidden;}
.bg-name{background:rgba(0,0,0,0.7);color:#fff;padding:4px 8px;border-radius:4px;font-size:12px;}
.map-name-display{text-align:center;font-weight:600;color:var(--text-primary);padding:8px;background:var(--surface-light);border-radius:8px;font-size:14px;}
.action-btn{
  width:100%;
  padding:10px 16px;
  background:var(--primary);
  color:#fff;
  border:none;
  border-radius:8px;
  cursor:pointer;
  font-size: 14px;
}

@media (max-width: 960px) {
  .action-btn {
    padding: 8px 12px;
    font-size: 13px;
  }
}

/* Minigame Section Styles */
.minigame-section {
  text-align: center;
  padding: 12px 0;
}

.minigame-description {
  margin: 0 0 12px 0;
  color: var(--text-muted);
  font-size: 14px;
}

.minigame-action-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  font-weight: 600;
  transition: all 0.3s ease;
}

.minigame-action-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}

.game-icon {
  font-size: 18px;
}

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

/* Test Deteriorate Button */
.test-deteriorate-btn {
  width: 100%;
  margin-top: 12px;
  padding: 10px 16px;
  background: rgba(255, 59, 48, 0.1);
  border: 2px solid rgba(255, 59, 48, 0.3);
  border-radius: 8px;
  cursor: pointer;
  font-size: 13px;
  font-weight: 600;
  color: #dc2626;
  transition: all 0.3s ease;
}

.test-deteriorate-btn:hover {
  background: rgba(255, 59, 48, 0.2);
  border-color: #dc2626;
  transform: translateY(-1px);
}

.test-deteriorate-btn:active {
  transform: translateY(0);
}

/* Inventory Grid */
.inventory-grid{
  display:grid;
  grid-template-columns:repeat(4, 1fr);
  grid-template-rows:repeat(4, 1fr);
  gap:8px;
}

@media (max-width: 960px) {
  .inventory-grid {
    grid-template-columns: repeat(3, 1fr);
    grid-template-rows: repeat(5, 1fr);
    gap: 6px;
  }
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

@media (max-width: 960px) {
  .shop-button {
    top: 10px;
    right: 10px;
    padding: 6px;
  }

  .shop-icon {
    width: 32px;
    height: 32px;
  }
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
  display:flex;
  flex-direction:column;
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
  max-height:calc(80vh - 56px);
  overflow-y:auto;
}
.shop-layout{
  display:flex;
  gap:20px;
  height:100%;
  align-items:stretch;
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

/* Low Stats Alert */
.low-stats-alert {
  position: absolute;
  top: 20px;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(255, 193, 7, 0.95);
  color: #000;
  padding: 16px 48px 16px 24px;
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
  z-index: 9999;
  animation: alertSlide 0.3s ease-out;
  font-weight: 600;
  font-size: 16px;
  max-width: 500px;
  text-align: center;
}

.low-stats-alert.dead-alert {
  background: rgba(220, 38, 38, 0.95);
  color: #fff;
}

.alert-content {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.close-alert {
  position: absolute;
  right: 8px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: inherit;
  font-size: 28px;
  line-height: 1;
  cursor: pointer;
  padding: 4px 8px;
  opacity: 0.7;
  transition: opacity 0.2s;
}

.close-alert:hover {
  opacity: 1;
}

@keyframes alertSlide {
  from {
    opacity: 0;
    transform: translateX(-50%) translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateX(-50%) translateY(0);
  }
}

/* Pet Name Editing Styles */
.pet-name-display{
  display:flex;
  flex-direction:column;
  gap:12px;
}
.current-pet-name{
  font-size:16px;
  font-weight:600;
  color:var(--text-primary);
  padding:12px;
  background:var(--surface-light);
  border-radius:8px;
  text-align:center;
}
.edit-name-btn{
  display:flex;
  align-items:center;
  justify-content:center;
  gap:8px;
  padding:8px 12px;
  background:var(--primary);
  color:#fff;
  border:none;
  border-radius:6px;
  cursor:pointer;
  font-size:12px;
  font-weight:600;
  transition:all 0.2s ease;
}
.edit-name-btn:hover{
  background:var(--primary-dark);
  transform:translateY(-1px);
}
.edit-icon{
  font-size:14px;
}
.pet-name-edit{
  display:flex;
  flex-direction:column;
  gap:8px;
}
.name-input{
  padding:10px 12px;
  border:2px solid var(--surface-lighter);
  border-radius:6px;
  background:var(--surface);
  color:var(--text-primary);
  font-size:14px;
  transition:border-color 0.2s ease;
}
.name-input:focus{
  outline:none;
  border-color:var(--primary);
}
.name-error{
  color:#ff6b6b;
  font-size:12px;
  font-weight:500;
}
.edit-buttons{
  display:flex;
  gap:8px;
}
.save-btn{
  flex:1;
  padding:8px 12px;
  background:var(--primary);
  color:#fff;
  border:none;
  border-radius:6px;
  cursor:pointer;
  font-size:12px;
  font-weight:600;
  transition:all 0.2s ease;
}
.save-btn:hover{
  background:var(--primary-dark);
}

/* Responsive: Shop Popup */
@media (max-width: 960px) {
  .shop-popup{
    width: 95vw;
    max-height: 85vh;
    border-radius: 12px;
  }

  .shop-header{
    padding: 12px 16px;
  }

  .shop-content{
    padding: 12px;
    max-height: calc(85vh - 56px);
    overflow-y: auto;
  }

  .shop-layout{
    flex-direction: column;
    gap: 12px;
    height: auto;
  }

  .character-section{
    width: 100%;
    display: grid;
    grid-template-columns: 120px 1fr;
    grid-auto-rows: auto;
    align-items: start;
    column-gap: 12px;
    row-gap: 8px;
  }

  .character-portrait{
    grid-column: 1;
    grid-row: 1 / span 2;
    width: 100%;
    height: 150px;
    min-width: 120px;
  }

  .character-name{ grid-column: 2; grid-row: 1; margin-top: 0; text-align: left; }
  .dialogue-box{ grid-column: 2; grid-row: 2; padding: 10px; }

  /* Arrow points towards the portrait on the left */
  .dialogue-box::before{
    top: 14px;
    left: -8px;
    border-left: none;
    border-right: 8px solid var(--primary);
    border-top: 8px solid transparent;
    border-bottom: 8px solid transparent;
  }

  .items-section{
    max-height: none;
    overflow-y: auto;
  }

  .shop-items{ gap: 10px; }

  .shop-item{ padding: 10px; }

  .item-icon{ width: 36px; height: 36px; font-size: 22px; }

  .buy-btn{ padding: 6px 10px; font-size: 12px; }
}
.cancel-btn{
  flex:1;
  padding:8px 12px;
  background:var(--surface-lighter);
  color:var(--text-muted);
  border:none;
  border-radius:6px;
  cursor:pointer;
  font-size:12px;
  font-weight:600;
  transition:all 0.2s ease;
}
.cancel-btn:hover{
  background:var(--surface-light);
}

/* Minigame Overlay */
.minigame-overlay{
  position:fixed;
  top:0;
  left:0;
  width:100vw;
  height:100vh;
  background:rgba(0,0,0,0.9);
  display:flex;
  align-items:center;
  justify-content:center;
  z-index:2000;
}

.minigame-popup{
  background:#1a1a1a;
  border-radius:12px;
  width:820px;
  height:640px;
  overflow:hidden;
  box-shadow:0 8px 32px rgba(0,0,0,0.5);
  display:flex;
  flex-direction:column;
  position:relative;
  border:4px solid #3b82f6;
}

.close-minigame{
  position:absolute;
  top:10px;
  right:10px;
  background:rgba(239,68,68,0.9);
  border:none;
  color:#fff;
  font-size:28px;
  cursor:pointer;
  padding:4px 12px;
  width:40px;
  height:40px;
  display:flex;
  align-items:center;
  justify-content:center;
  border-radius:8px;
  transition:background 0.2s ease;
  z-index:10;
  font-weight:bold;
  line-height:1;
}

.close-minigame:hover{
  background:#dc2626;
}

@media (max-width: 960px) {
  .minigame-popup{
    width: 95vw;
    height: 85vh;
  }
}

/* Pet Switching Styles */
.special-item {
  background: linear-gradient(135deg, rgba(147, 51, 234, 0.1), rgba(59, 130, 246, 0.1)) !important;
  border: 2px solid rgba(147, 51, 234, 0.3) !important;
}

.special-icon {
  font-size: 32px !important;
  background: linear-gradient(135deg, #9333ea, #3b82f6) !important;
}

.special-btn {
  background: linear-gradient(135deg, #9333ea, #3b82f6) !important;
}

.special-btn:hover:not(:disabled) {
  background: linear-gradient(135deg, #7c3aed, #2563eb) !important;
}

.pet-switch-popup {
  background: var(--surface);
  border-radius: 16px;
  width: 800px;
  max-width: 95vw;
  max-height: 85vh;
  overflow: hidden;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  display: flex;
  flex-direction: column;
}

.pet-switch-header {
  background: linear-gradient(135deg, #9333ea, #3b82f6);
  color: #fff;
  padding: 16px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.pet-switch-header h3 {
  margin: 0;
  font-size: 20px;
}

.pet-switch-content {
  padding: 24px;
  overflow-y: auto;
  max-height: calc(85vh - 70px);
}

.switch-description {
  text-align: center;
  font-size: 14px;
  color: var(--text-primary);
  margin-bottom: 20px;
  padding: 12px;
  background: var(--surface-light);
  border-radius: 8px;
}

.pet-switch-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.pet-switch-card {
  background: var(--surface-light);
  border: 3px solid transparent;
  border-radius: 12px;
  padding: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

.pet-switch-card:hover:not(.disabled) {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
  border-color: #3b82f6;
}

.pet-switch-card.selected {
  border-color: #9333ea;
  background: linear-gradient(135deg, rgba(147, 51, 234, 0.1), rgba(59, 130, 246, 0.1));
  box-shadow: 0 8px 24px rgba(147, 51, 234, 0.3);
}

.pet-switch-card.disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.pet-switch-card.current {
  border-color: var(--primary);
  background: var(--surface);
}

.pet-switch-preview {
  width: 100%;
  height: 120px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--surface);
  border-radius: 8px;
  margin-bottom: 12px;
  padding: 12px;
}

.pet-switch-info {
  width: 100%;
}

.pet-switch-name {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 8px 0;
}

.pet-switch-desc {
  font-size: 12px;
  color: var(--text-muted);
  margin: 0 0 8px 0;
  line-height: 1.4;
}

.current-badge {
  display: inline-block;
  background: var(--primary);
  color: white;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 600;
}

.pet-switch-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
}

.cancel-switch-btn {
  padding: 12px 24px;
  background: var(--surface-lighter);
  color: var(--text-muted);
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
  transition: all 0.2s ease;
}

.cancel-switch-btn:hover {
  background: var(--surface-light);
  color: var(--text-primary);
}

.confirm-switch-btn {
  padding: 12px 24px;
  background: linear-gradient(135deg, #9333ea, #3b82f6);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
  transition: all 0.2s ease;
}

.confirm-switch-btn:hover:not(:disabled) {
  background: linear-gradient(135deg, #7c3aed, #2563eb);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(147, 51, 234, 0.4);
}

.confirm-switch-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

@media (max-width: 768px) {
  .pet-switch-grid {
    grid-template-columns: 1fr;
  }

  .pet-switch-actions {
    flex-direction: column;
  }

  .cancel-switch-btn,
  .confirm-switch-btn {
    width: 100%;
  }
}

/* Pet Switch Celebration Styles */
.pet-switch-celebration-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10000;
  animation: fadeIn 0.3s ease-out;
}

.pet-switch-celebration {
  background: linear-gradient(135deg,
    rgba(255, 255, 255, 0.98) 0%,
    rgba(252, 252, 254, 0.96) 50%,
    rgba(250, 250, 255, 0.95) 100%
  );
  border-radius: 24px;
  padding: 48px 64px;
  text-align: center;
  position: relative;
  box-shadow:
    0 20px 60px rgba(147, 51, 234, 0.3),
    0 0 0 1px rgba(147, 51, 234, 0.1),
    inset 0 1px 0 rgba(255, 255, 255, 0.8);
  animation: celebrationSlideUp 0.5s cubic-bezier(0.34, 1.56, 0.64, 1);
  overflow: hidden;
  backdrop-filter: blur(10px);
}

.pet-switch-celebration::before {
  content: '';
  position: absolute;
  top: -2px;
  left: -2px;
  right: -2px;
  bottom: -2px;
  background: linear-gradient(135deg, #9333ea, #3b82f6, #9333ea);
  border-radius: 24px;
  z-index: -1;
  animation: borderGlow 3s ease-in-out infinite;
}

@keyframes borderGlow {
  0%, 100% {
    opacity: 0.6;
  }
  50% {
    opacity: 1;
  }
}

.celebration-sparkle {
  font-size: 48px;
  margin-bottom: 16px;
  animation: sparkleFloat 2s ease-in-out infinite;
}

@keyframes sparkleFloat {
  0%, 100% {
    transform: translateY(0) rotate(0deg);
  }
  25% {
    transform: translateY(-10px) rotate(5deg);
  }
  75% {
    transform: translateY(-5px) rotate(-5deg);
  }
}

.celebration-icon-container {
  width: 160px;
  height: 160px;
  margin: 0 auto 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, rgba(147, 51, 234, 0.1), rgba(59, 130, 246, 0.1));
  border-radius: 50%;
  border: 3px solid;
  border-color: #9333ea;
  box-shadow:
    0 10px 30px rgba(147, 51, 234, 0.3),
    inset 0 2px 10px rgba(255, 255, 255, 0.5);
  animation: iconPulse 2s ease-in-out infinite;
}

@keyframes iconPulse {
  0%, 100% {
    transform: scale(1);
    box-shadow: 0 10px 30px rgba(147, 51, 234, 0.3), inset 0 2px 10px rgba(255, 255, 255, 0.5);
  }
  50% {
    transform: scale(1.05);
    box-shadow: 0 15px 40px rgba(147, 51, 234, 0.5), inset 0 2px 10px rgba(255, 255, 255, 0.7);
  }
}

.celebration-title {
  font-size: 32px;
  font-weight: 700;
  background: linear-gradient(135deg, #9333ea, #3b82f6);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 12px;
  animation: titleBounce 0.6s cubic-bezier(0.34, 1.56, 0.64, 1) 0.2s backwards;
}

@keyframes titleBounce {
  0% {
    opacity: 0;
    transform: translateY(20px) scale(0.8);
  }
  100% {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.celebration-subtitle {
  font-size: 24px;
  font-weight: 600;
  color: #9333ea;
  margin-bottom: 8px;
  animation: subtitleFadeIn 0.6s ease-out 0.4s backwards;
}

@keyframes subtitleFadeIn {
  0% {
    opacity: 0;
    transform: translateY(10px);
  }
  100% {
    opacity: 1;
    transform: translateY(0);
  }
}

.celebration-message {
  font-size: 16px;
  color: #6b7280;
  animation: messageFadeIn 0.6s ease-out 0.6s backwards;
}

@keyframes messageFadeIn {
  0% {
    opacity: 0;
  }
  100% {
    opacity: 1;
  }
}

@keyframes celebrationSlideUp {
  0% {
    opacity: 0;
    transform: translateY(50px) scale(0.9);
  }
  100% {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

@keyframes fadeIn {
  0% {
    opacity: 0;
  }
  100% {
    opacity: 1;
  }
}

@media (max-width: 768px) {
  .pet-switch-celebration {
    padding: 32px 24px;
    max-width: 90vw;
  }

  .celebration-icon-container {
    width: 120px;
    height: 120px;
  }

  .celebration-title {
    font-size: 24px;
  }

  .celebration-subtitle {
    font-size: 18px;
  }

  .celebration-message {
    font-size: 14px;
  }
}

.daily-task-item { cursor: pointer; }
.wrap-text { white-space: normal; overflow: visible; text-overflow: initial; }
:deep(.daily-task-list .v-list-item__content) { white-space: normal; }
</style>
