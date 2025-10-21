<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import AnimatedPet from '@/components/AnimatedPet.vue'
import SpritePreview from '@/components/SpritePreview.vue'
import AnimatedCoin from '@/components/AnimatedCoin.vue'
import { useCoins } from '@/composables/useCoins.js'

/* ===== Global size knob ===== */
const SCALE = 6  // ↓ smaller pet. Try 5 or 4 if you want it even smaller.

/* ================= PET CATALOG ================= */
const PETS = {
  cat: { label: 'Cat', config: { spriteUrl: '/cat-spritesheet.png', slice: 32, scale: SCALE, speed: 70,
    animations: { idle:{row:0,fps:6,loop:true,frames:8,colStart:0}, idle2:{row:1,fps:6,loop:true,frames:8,colStart:0},
    clean:{row:2,fps:8,loop:true,frames:8,colStart:0}, clean2:{row:3,fps:8,loop:true,frames:8,colStart:0},
    move:{row:4,fps:10,loop:true,frames:8,colStart:0}, move2:{row:5,fps:10,loop:true,frames:8,colStart:0},
    sleep:{row:6,fps:5,loop:true,frames:6,colStart:0}, paw:{row:7,fps:10,loop:false,frames:6,colStart:0},
    grabbed:{row:7,fps:8,loop:true,frames:6,colStart:0}, jump:{row:8,fps:12,loop:false,frames:8,colStart:0},
    scared:{row:9,fps:10,loop:false,frames:8,colStart:0}, falling:{row:9,fps:8,loop:true,frames:8,colStart:0}}}},
    
  catGrey: { label: 'Grey Cat', config: { spriteUrl: '/PC _ Computer - Stardew Valley - Animals - Cat (Grey).png', slice: 32, scale: SCALE, speed: 70,
    animations: { idle:{row:0,fps:4,loop:true,frames:4,colStart:0}, move:{row:1,fps:6,loop:true,frames:4,colStart:0},
    sleep:{row:2,fps:2,loop:true,frames:4,colStart:0}, click:{row:3,fps:8,loop:false,frames:4,colStart:0},
    falling:{row:1,fps:6,loop:true,frames:4,colStart:0}, grabbed:{row:0,fps:4,loop:true,frames:4,colStart:0}}}},

  catBlack: { label: 'Black Cat', config: { spriteUrl: '/PC _ Computer - Stardew Valley - Animals - Cat (Black).png', slice: 32, scale: SCALE, speed: 70,
    animations: { idle:{row:0,fps:4,loop:true,frames:4,colStart:0}, move:{row:1,fps:6,loop:true,frames:4,colStart:0},
    sleep:{row:2,fps:2,loop:true,frames:4,colStart:0}, click:{row:3,fps:8,loop:false,frames:4,colStart:0},
    falling:{row:1,fps:6,loop:true,frames:4,colStart:0}, grabbed:{row:0,fps:4,loop:true,frames:4,colStart:0}}}},

  catNew: { label: 'New Cat', config: { spriteUrl: '/PC _ Computer - Stardew Valley - Animals - Cat.png', slice: 32, scale: SCALE, speed: 70,
    animations: { idle:{row:0,fps:4,loop:true,frames:4,colStart:0}, move:{row:1,fps:6,loop:true,frames:4,colStart:0},
    sleep:{row:2,fps:2,loop:true,frames:4,colStart:0}, click:{row:3,fps:8,loop:false,frames:4,colStart:0},
    falling:{row:1,fps:6,loop:true,frames:4,colStart:0}, grabbed:{row:0,fps:4,loop:true,frames:4,colStart:0}}}},

  dogBlonde: { label: 'Blonde Dog', config: { spriteUrl: '/PC _ Computer - Stardew Valley - Animals - Dog (Blonde).png', slice: 32, scale: SCALE, speed: 80,
    animations: { idle:{row:0,fps:4,loop:true,frames:4,colStart:0}, move:{row:1,fps:6,loop:true,frames:4,colStart:0},
    sleep:{row:2,fps:2,loop:true,frames:4,colStart:0}, click:{row:2,fps:8,loop:false,frames:4,colStart:0},
    falling:{row:1,fps:6,loop:true,frames:4,colStart:0}, grabbed:{row:0,fps:4,loop:true,frames:4,colStart:0}}}},

  dogGrey: { label: 'Grey Dog', config: { spriteUrl: '/PC _ Computer - Stardew Valley - Animals - Dog (Grey).png', slice: 32, scale: SCALE, speed: 80,
    animations: { idle:{row:0,fps:4,loop:true,frames:4,colStart:0}, move:{row:1,fps:6,loop:true,frames:4,colStart:0},
    sleep:{row:2,fps:2,loop:true,frames:4,colStart:0}, click:{row:2,fps:8,loop:false,frames:4,colStart:0},
    falling:{row:1,fps:6,loop:true,frames:4,colStart:0}, grabbed:{row:0,fps:4,loop:true,frames:4,colStart:0}}}},

  dogLight: { label: 'Light Dog', config: { spriteUrl: '/PC _ Computer - Stardew Valley - Animals - Dog (Light Brown).png', slice: 32, scale: SCALE, speed: 80,
    animations: { idle:{row:0,fps:4,loop:true,frames:4,colStart:0}, move:{row:1,fps:6,loop:true,frames:4,colStart:0},
    sleep:{row:2,fps:2,loop:true,frames:4,colStart:0}, click:{row:2,fps:8,loop:false,frames:4,colStart:0},
    falling:{row:1,fps:6,loop:true,frames:4,colStart:0}, grabbed:{row:0,fps:4,loop:true,frames:4,colStart:0}}}}
}

/* ==== Status / Food ==== */
const petStatus = reactive({ happiness: 75, health: 80, energy: 60 })
const foodIndex = ref(0)
const availableFood = ref([
  { icon: '🍎', name: 'Apple', count: 3 },
  { icon: '🥕', name: 'Carrot', count: 1 },
  { icon: '🐟', name: 'Fish',  count: 5 },
  { icon: '🥛', name: 'Milk',  count: 2 }
])

/* ==== Pet picker (sidebar immediately controls the pet) ==== */
const petKeys = Object.keys(PETS)
const petIndex = ref(0)
const selectedPetKey = computed(() => petKeys[petIndex.value]) // ← follows arrows instantly
function previousPet() { if (petIndex.value > 0) petIndex.value-- }
function nextPet() { if (petIndex.value < petKeys.length - 1) petIndex.value++ }
// Optional: keep a Select button if you like that UX; it’s no longer required.
function selectPet() { /* no-op now, left here for compatibility */ }

/* ==== Backgrounds ==== */
const bgIndex = ref(0)
const availableBackgrounds = ref([
  { name: 'Waterfall Valley', preview: '/photos/pixelbg1.jpg', fullImage: '/photos/pixelbg1.jpg' },
  { name: 'Mountain Peak',    preview: '/photos/pixelbg2.jpg', fullImage: '/photos/pixelbg2.jpg' }
])
const currentBackground = computed(() => availableBackgrounds.value[bgIndex.value].fullImage)
function previousBackground() { if (bgIndex.value > 0) bgIndex.value-- }
function nextBackground() { if (bgIndex.value < availableBackgrounds.value.length - 1) bgIndex.value++ }

/* ==== Food actions ==== */
function previousFood() { if (foodIndex.value > 0) foodIndex.value-- }
function nextFood() { if (foodIndex.value < availableFood.value.length - 1) foodIndex.value++ }
function feedPet() {
  const f = availableFood.value[foodIndex.value]
  if (f.count > 0) {
    f.count--
    petStatus.happiness = Math.min(100, petStatus.happiness + 10)
    petStatus.health    = Math.min(100, petStatus.health + 5)
  }
}

/* ==== Shop ==== */
const showShop = ref(false)

// Use shared coin state
const { coins: playerGold, coinsLoading, coinsError, fetchCoins, updateCoins } = useCoins()

const shopItems = ref([
  { icon: '🍎', name: 'Apple', price: 50, description: 'A crisp, sweet apple that pets love!' },
  { icon: '🥕', name: 'Carrot', price: 30, description: 'Fresh orange carrots, great for pet health.' },
  { icon: '🐟', name: 'Fish', price: 80, description: 'Fresh fish, a premium treat for pets.' },
  { icon: '🥛', name: 'Milk', price: 40, description: 'Fresh milk, good for growing pets.' },
  { icon: '🍖', name: 'Meat', price: 120, description: 'Premium meat, the ultimate pet treat.' },
  { icon: '🧀', name: 'Cheese', price: 60, description: 'Rich cheese, a special treat for pets.' }
])

/* ==== Shopkeeper Animation ==== */
const shopkeeperState = ref('happytalk')  // happytalk, neutral, annoyedclosed
let talkingInterval = null

const shopkeeperImage = computed(() => {
  const images = {
    happytalk: '/shopkeeper/sk_bb_happytalk.png',
    neutral: '/shopkeeper/sk_bb_neutral.png',
    annoyedclosed: '/shopkeeper/sk_bb_annoyedclosed.png'
  }
  return images[shopkeeperState.value]
})

function startTalkingAnimation() {
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
    const newCoinAmount = playerGold.value - item.price

    // Use the shared updateCoins function
    const result = await updateCoins(newCoinAmount)

    if (result.success) {
      // Add to existing food or create new entry
      const existingFood = availableFood.value.find(f => f.name === item.name)
      if (existingFood) {
        existingFood.count++
      } else {
        availableFood.value.push({ icon: item.icon, name: item.name, count: 1 })
      }
    } else {
      alert('Failed to purchase item: ' + (result.error || 'Please try again'))
    }
  }
}

// Fetch coins when component mounts if not already loaded
onMounted(() => {
  if (playerGold.value === null && !coinsLoading.value) {
    fetchCoins()
  }
})
</script>

<template>
  <div class="pet-page-container">
    <!-- Main Content -->
    <div class="main-content" :style="{ backgroundImage: `url(${currentBackground})` }">
      <div class="pet-stage">
        <!-- 🔑 key makes sure AnimatedPet remounts when selectedPetKey changes -->
        <AnimatedPet 
          :key="selectedPetKey" 
          :sprite-url="PETS[selectedPetKey].config.spriteUrl"
          :slice="PETS[selectedPetKey].config.slice"
          :scale="PETS[selectedPetKey].config.scale"
          :speed="PETS[selectedPetKey].config.speed"
          :animations="PETS[selectedPetKey].config.animations"
        />
      </div>
      
              <!-- Shop Button -->
              <button class="shop-button" @click="toggleShop">
                <img src="/fruitstand.png" alt="Shop" class="shop-icon" />
              </button>
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
        <div class="status-item">
          <span class="status-label">Energy</span>
          <div class="status-bar"><div class="status-fill energy" :style="{ width: `${petStatus.energy}%` }"></div></div>
          <span class="status-value">{{ petStatus.energy }}%</span>
        </div>
      </div>

      <!-- Food -->
      <div class="panel-section">
        <h4 class="section-title">Food</h4>
        <div class="selection-container">
          <button class="nav-btn" @click="previousFood" :disabled="foodIndex === 0">‹</button>
          <div class="item-display">
            <div class="item-icon">{{ availableFood[foodIndex].icon }}</div>
            <div class="item-count">{{ availableFood[foodIndex].count }} left</div>
          </div>
          <button class="nav-btn" @click="nextFood" :disabled="foodIndex === availableFood.length - 1">›</button>
        </div>
        <button class="action-btn" @click="feedPet" :disabled="availableFood[foodIndex].count === 0">Feed</button>
      </div>

      <!-- Pet Select -->
      <div class="panel-section">
        <h4 class="section-title">Pet Select</h4>
        <div class="selection-container">
          <button class="nav-btn" @click="previousPet" :disabled="petIndex === 0">‹</button>

          <div class="item-display" @click="nextPet">
            <!-- 🔑 key forces preview to redraw as you scroll -->
            <SpritePreview
              :key="PETS[petKeys[petIndex]].config.spriteUrl + ':' + PETS[petKeys[petIndex]].config.slice"
              :sprite-url="PETS[petKeys[petIndex]].config.spriteUrl"
              :slice="PETS[petKeys[petIndex]].config.slice"
              :scale="2.5"
              :row="0"
              :col="0"
            />
            <div class="pet-name-small">{{ PETS[petKeys[petIndex]].label }}</div>
          </div>

          <button class="nav-btn" @click="nextPet" :disabled="petIndex === petKeys.length - 1">›</button>
        </div>

        <!-- Optional now; you can remove if you want instant-switch only -->
        <button class="action-btn" @click="selectPet">Select Pet</button>
      </div>

      <!-- Background -->
      <div class="panel-section">
        <h4 class="section-title">Background</h4>
        <div class="selection-container">
          <button class="nav-btn" @click="previousBackground" :disabled="bgIndex === 0">‹</button>
          <div class="item-display">
            <div class="bg-preview" :style="{ backgroundImage: `url(${availableBackgrounds[bgIndex].preview})` }">
              <div class="bg-name">{{ availableBackgrounds[bgIndex].name }}</div>
            </div>
          </div>
          <button class="nav-btn" @click="nextBackground" :disabled="bgIndex === availableBackgrounds.length - 1">›</button>
        </div>
      </div>
    </div>

    <!-- Shop Popup -->
    <div v-if="showShop" class="shop-overlay" @click="toggleShop">
      <div class="shop-popup" @click.stop>
        <div class="shop-header">
          <h3>🛒 Pet Shop</h3>
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
                  <div class="item-icon">{{ item.icon }}</div>
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
.main-content{flex:1;display:flex;align-items:stretch;justify-content:stretch;padding:24px;position:relative;overflow:hidden;background-size:cover;background-position:center;}
.pet-stage{position:relative;width:100%;height:100%;overflow:hidden;}
.right-panel{width:280px;background:var(--surface);border-left:1px solid var(--surface-lighter);padding:24px 16px;overflow-y:auto;}
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
.action-btn{width:100%;padding:10px 16px;background:var(--primary);color:#fff;border:none;border-radius:8px;cursor:pointer;}

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
</style>
