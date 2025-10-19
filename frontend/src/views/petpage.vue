<script setup>
import { ref, reactive, computed } from 'vue'
import AnimatedPet from '@/components/AnimatedPet.vue'
import SpritePreview from '@/components/SpritePreview.vue'

/* ===== Global size knob ===== */
const SCALE = 4  // ↓ smaller pet. Try 5 or 4 if you want it even smaller.

/* ================= PET CATALOG ================= */
const PETS = {
  bear: { label: 'Bear', config: { spriteUrl: '/MiniBear.png', slice: 32, scale: SCALE, speed: 70,
    animations: { move:{row:0,fps:10,loop:true,frames:8}, idle:{row:1,fps:6,loop:true,frames:8},
    clean:{row:2,fps:8,loop:true,frames:8}, move2:{row:3,fps:10,loop:true,frames:8},
    sleep:{row:6,fps:5,loop:true,frames:6}, jump:{row:7,fps:12,loop:false,frames:4}, scared:{row:8,fps:10,loop:false,frames:6}}}},
  fox: { label: 'Fox', config: { spriteUrl: '/MiniFox.png', slice: 32, scale: SCALE, speed: 80,
    animations: { move:{row:0,fps:12,loop:true,frames:8}, idle:{row:1,fps:6,loop:true,frames:6},
    clean:{row:2,fps:8,loop:true,frames:6}, sleep:{row:3,fps:5,loop:true,frames:4},
    jump:{row:4,fps:12,loop:false,frames:4}, scared:{row:4,fps:12,loop:false,frames:4}}}},
  deer1:{label:'Deer 1',config:{spriteUrl:'/MiniDeer1.png',slice:32,scale:SCALE,speed:70,
    animations:{move:{row:0,fps:10,loop:true,frames:6},idle:{row:1,fps:6,loop:true,frames:6},
    clean:{row:2,fps:8,loop:true,frames:6},jump:{row:3,fps:12,loop:false,frames:6},sleep:{row:4,fps:5,loop:true,frames:5}}}},
  deer2:{label:'Deer 2',config:{spriteUrl:'/MiniDeer2.png',slice:32,scale:SCALE,speed:70,
    animations:{move:{row:0,fps:10,loop:true,frames:7},idle:{row:1,fps:6,loop:true,frames:7},
    clean:{row:2,fps:8,loop:true,frames:7},jump:{row:3,fps:12,loop:false,frames:7},sleep:{row:4,fps:5,loop:true,frames:7}}}},
  bunny:{label:'Bunny',config:{spriteUrl:'/MiniBunny.png',slice:32,scale:SCALE,speed:85,
    animations:{move:{row:0,fps:12,loop:true,frames:4},idle:{row:1,fps:6,loop:true,frames:4},
    jump:{row:2,fps:14,loop:false,frames:4},sleep:{row:3,fps:5,loop:true,frames:4}}}},
  boar:{label:'Boar',config:{spriteUrl:'/MiniBoar.png',slice:32,scale:SCALE,speed:75,
    animations:{move:{row:0,fps:10,loop:true,frames:6},idle:{row:1,fps:6,loop:true,frames:6},
    clean:{row:2,fps:8,loop:true,frames:6},jump:{row:3,fps:12,loop:false,frames:6},sleep:{row:4,fps:5,loop:true,frames:5}}}},
  bird:{label:'Bird',config:{spriteUrl:'/MiniBird.png',slice:16,scale:SCALE+2,speed:90,
    animations:{move:{row:0,fps:14,loop:true,frames:3},idle:{row:1,fps:8,loop:true,frames:3},
    jump:{row:2,fps:12,loop:false,frames:3},sleep:{row:3,fps:5,loop:true,frames:3}}}},
  wolf:{label:'Wolf',config:{spriteUrl:'/MiniWolf.png',slice:32,scale:SCALE,speed:80,
    animations:{move:{row:0,fps:12,loop:true,frames:8},idle:{row:1,fps:6,loop:true,frames:8},
    clean:{row:2,fps:8,loop:true,frames:8},scared:{row:5,fps:10,loop:false,frames:8},
    sleep:{row:6,fps:5,loop:true,frames:7},jump:{row:7,fps:12,loop:false,frames:7}}}}
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
</script>

<template>
  <div class="pet-page-container">
    <!-- Main Content -->
    <div class="main-content" :style="{ backgroundImage: `url(${currentBackground})` }">
      <div class="pet-stage">
        <!-- 🔑 key makes sure AnimatedPet remounts when selectedPetKey changes -->
        <AnimatedPet :key="selectedPetKey" :config="PETS[selectedPetKey].config" />
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
</style>
