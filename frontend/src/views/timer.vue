<script setup>
import { ref, computed, onUnmounted, watch } from 'vue'

const presets = { 'Focus': 25, 'Short Break': 5, 'Long Break': 15 }
const mode = ref('Focus')
const minutes = ref(presets[mode.value])
const timeLeft = ref(presets[mode.value] * 60) // countdown in seconds
const running = ref(false)
const settingsDialog = ref(false)
const customFocusTime = ref(25)
const customBreakTime = ref(5)
let t = null

const total = computed(() => minutes.value * 60)
const pct = computed(() => Math.floor(100 * (total.value - timeLeft.value) / total.value))
const label = computed(() => {
  const mins = Math.floor(timeLeft.value / 60)
  const secs = timeLeft.value % 60
  return `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`
})

// Emit event to parent to toggle sidebar
const emit = defineEmits(['toggle-fullscreen'])

watch(running, (newVal) => {
  emit('toggle-fullscreen', newVal)
})

function switchMode(m) { 
  if (running.value) return
  mode.value = m
  minutes.value = presets[m]
  timeLeft.value = presets[m] * 60
}

function start(){ 
  if (running.value) return
  running.value = true
  t = setInterval(() => { 
    timeLeft.value--
    if (timeLeft.value <= 0){ 
      clearInterval(t)
      running.value = false
      timeLeft.value = 0
      
      // If this was a focus session, dispatch event to update study hours
      if (mode.value === 'Focus') {
        dispatchStudySessionCompleted()
      }
    } 
  }, 1000) 
}

function dispatchStudySessionCompleted() {
  // Dispatch event to notify other components of completed study session
  console.log('✅ Focus session completed! Dispatching event...');
  window.dispatchEvent(new CustomEvent('study-session-completed', {
    detail: {
      duration: minutes.value,
      mode: mode.value,
      timestamp: new Date()
    }
  }));
}

function stop(){ 
  running.value = false
  clearInterval(t) 
}

function reset(){ 
  stop()
  timeLeft.value = minutes.value * 60
}

function openSettings() {
  settingsDialog.value = true
}

function saveSettings() {
  customFocusTime.value = parseInt(customFocusTime.value) || 25
  customBreakTime.value = parseInt(customBreakTime.value) || 5
  presets['Focus'] = customFocusTime.value
  presets['Short Break'] = customBreakTime.value
  
  if (mode.value === 'Focus') {
    minutes.value = customFocusTime.value
    timeLeft.value = customFocusTime.value * 60
  } else if (mode.value === 'Short Break') {
    minutes.value = customBreakTime.value
    timeLeft.value = customBreakTime.value * 60
  }
  
  settingsDialog.value = false
}

onUnmounted(() => clearInterval(t))
</script>

<template>
  <div :class="['timer-page', { 'fullscreen-mode': running }]">
    <!-- Falling Leaves Background (BEHIND cards, shown when timer is running) -->
    <div v-if="running" class="falling-leaves-background"></div>

    <v-container :class="['py-8', { 'fullscreen-container': running }]" :style="running ? 'max-width: 100%;' : 'max-width: 1400px;'">
      <v-row>
        <!-- Main Timer Card -->
        <v-col :cols="running ? 12 : 12" :md="running ? 12 : 7" :lg="running ? 12 : 8">
          <v-card rounded="xl" elevation="0" :class="['timer-card', { 'fullscreen-card': running }]" class="pa-10">
            <div class="mb-2">
              <h2 class="text-h5 font-weight-medium mb-1 timer-title">Study Timer</h2>
              <p class="text-body-2 text-medium-emphasis">Focus with the Pomodoro Technique</p>
            </div>

            <!-- Study Session Section -->
            <div class="session-box mt-6 pa-6 rounded-lg">
              <div class="d-flex justify-space-between align-center mb-6">
                <div>
                  <div class="text-subtitle-2 text-medium-emphasis mb-1">Study Session</div>
                  <div class="text-caption text-medium-emphasis">Set your timer</div>
                </div>
                <v-chip color="primary" size="small" variant="flat" class="px-4">Ready</v-chip>
              </div>

              <!-- Mode Selection Pills -->
              <div class="d-flex ga-2 mb-8 flex-wrap justify-center">
                <v-chip v-for="m in Object.keys(presets)" :key="m"
                        :color="mode===m?'primary':'secondary'" 
                        :variant="mode===m?'flat':'tonal'"
                        class="cursor-pointer px-4"
                        @click="switchMode(m)">
                  {{ m }} • {{ presets[m] }}m
                </v-chip>
              </div>

              <!-- Timer Display -->
              <div class="text-center mb-8">
                <div :class="['timer-display', 'mb-4', { 'timer-display-large': running }]">{{ label }}</div>
                <v-progress-linear :model-value="pct" height="8" rounded color="primary" 
                                   bg-color="surface-lighter" class="mb-2"/>
              </div>

              <!-- Action Buttons -->
              <div class="d-flex ga-3 justify-center">
                <v-btn color="primary" size="large" rounded="lg" @click="start" :disabled="running" 
                       class="px-8 text-none" elevation="0">
                  <v-icon start>mdi-play</v-icon>Start
                </v-btn>
                <v-btn color="secondary" size="large" rounded="lg" variant="tonal" @click="stop" 
                       :disabled="!running" class="px-6 text-none" elevation="0">
                  <v-icon start>mdi-pause</v-icon>Pause
                </v-btn>
                <v-btn size="large" rounded="lg" variant="text" @click="reset" 
                       class="text-none reset-btn">
                  <v-icon start>mdi-restore</v-icon>Reset
                </v-btn>
              </div>

              <!-- Session Stats -->
              <div v-if="!running" class="d-flex justify-space-around mt-8 pt-6 stats-divider">
                <div class="text-center">
                  <div class="text-h4 font-weight-medium stat-number">0</div>
                  <div class="text-caption text-medium-emphasis">Sessions Today</div>
                </div>
                <div class="text-center">
                  <div class="text-h4 font-weight-medium stat-number">70%</div>
                  <div class="text-caption text-medium-emphasis">Focus Score</div>
                </div>
              </div>
            </div>

            <!-- Focus Tips Section - hide when running -->
            <div v-if="!running" class="tips-section mt-6 pa-6 rounded-lg">
              <div class="text-subtitle-2 font-weight-medium mb-4 tips-title">Focus Tips</div>
              <v-row>
                <v-col cols="12" md="6">
                  <div class="text-body-2 font-weight-medium mb-2">During Study Sessions:</div>
                  <ul class="text-caption text-medium-emphasis" style="line-height: 1.8;">
                    <li>Turn off notifications</li>
                    <li>Keep water nearby</li>
                    <li>Use comfortable lighting</li>
                    <li>Take notes by hand when possible</li>
                  </ul>
                </v-col>
                <v-col cols="12" md="6">
                  <div class="text-body-2 font-weight-medium mb-2">During Breaks:</div>
                  <ul class="text-caption text-medium-emphasis" style="line-height: 1.8;">
                    <li>Step away from your desk</li>
                    <li>Do light stretching</li>
                    <li>Get some fresh air</li>
                    <li>Avoid social media</li>
                  </ul>
                </v-col>
              </v-row>
            </div>
          </v-card>
        </v-col>

        <!-- Session Details Sidebar - hide when running -->
        <v-col v-if="!running" cols="12" md="5" lg="4">
          <v-card rounded="xl" elevation="0" class="details-card pa-6 mb-4">
            <div class="text-subtitle-1 font-weight-medium mb-1 session-title">Session Details</div>
            <p class="text-caption text-medium-emphasis mb-4">Set up your study session</p>
            
            <div class="mb-4">
              <label class="text-body-2 font-weight-medium mb-2 d-block">Subject</label>
              <v-select density="comfortable" variant="outlined" rounded="lg" 
                        placeholder="Select subject" hide-details/>
            </div>

            <div class="mb-4">
              <label class="text-body-2 font-weight-medium mb-2 d-block">Task/Topic</label>
              <v-text-field density="comfortable" variant="outlined" rounded="lg" 
                            placeholder="What will you work on?" hide-details/>
            </div>

            <div class="mb-4">
              <label class="text-body-2 font-weight-medium mb-2 d-block">Notes (optional)</label>
              <v-textarea density="comfortable" variant="outlined" rounded="lg" rows="3"
                          placeholder="Any additional notes..." hide-details/>
            </div>

            <v-btn block color="primary" rounded="lg" variant="tonal" class="text-none mt-2" @click="openSettings">
              <v-icon start>mdi-cog</v-icon>Timer Settings
            </v-btn>
          </v-card>

          <!-- Daily Streaks Card -->
          <v-card rounded="xl" elevation="0" class="streaks-card pa-6">
            <div class="text-subtitle-2 font-weight-medium mb-4 streaks-title">Daily Streaks</div>
            <v-row dense>
              <v-col cols="4" class="text-center">
                <div class="text-h5 font-weight-bold streak-number">0</div>
                <div class="text-caption text-medium-emphasis">Study</div>
              </v-col>
              <v-col cols="4" class="text-center">
                <div class="text-h5 font-weight-bold streak-number">0</div>
                <div class="text-caption text-medium-emphasis">Check-in</div>
              </v-col>
              <v-col cols="4" class="text-center">
                <div class="text-h5 font-weight-bold streak-number">0</div>
                <div class="text-caption text-medium-emphasis">Wellness</div>
              </v-col>
            </v-row>
          </v-card>
        </v-col>
      </v-row>
    </v-container>

    <!-- Falling Leaves IN FRONT of cards -->
    <div v-if="running" class="falling-leaves-overlay">
      <div class="leaf" v-for="i in 20" :key="i" :style="{ 
        left: `${Math.random() * 100}%`, 
        animationDelay: `${Math.random() * 8}s`,
        animationDuration: `${10 + Math.random() * 6}s`
      }">🍂</div>
    </div>

    <!-- 8-Bit Pixel Cat Pet Section -->
    <div v-if="running" class="pet-container">
      <div class="pixel-cat-wrapper walking">
        <div class="pixel-cat">
          <!-- Row 1 - Ears -->
          <div class="cat-row">
            <span class="p"></span><span class="p"></span><span class="p o"></span><span class="p o"></span><span class="p"></span><span class="p"></span><span class="p"></span><span class="p"></span><span class="p o"></span><span class="p o"></span><span class="p"></span><span class="p"></span>
          </div>
          <!-- Row 2 - Top of ears -->
          <div class="cat-row">
            <span class="p"></span><span class="p o"></span><span class="p pk"></span><span class="p w"></span><span class="p o"></span><span class="p"></span><span class="p"></span><span class="p o"></span><span class="p pk"></span><span class="p w"></span><span class="p o"></span><span class="p"></span>
          </div>
          <!-- Row 3 - Top of head -->
          <div class="cat-row">
            <span class="p o"></span><span class="p o"></span><span class="p o"></span><span class="p o"></span><span class="p o"></span><span class="p o"></span><span class="p o"></span><span class="p o"></span><span class="p o"></span><span class="p o"></span><span class="p o"></span><span class="p o"></span>
          </div>
          <!-- Row 4 - Face start -->
          <div class="cat-row">
            <span class="p o"></span><span class="p w"></span><span class="p w"></span><span class="p w"></span><span class="p w"></span><span class="p w"></span><span class="p w"></span><span class="p w"></span><span class="p w"></span><span class="p w"></span><span class="p w"></span><span class="p o"></span>
          </div>
          <!-- Row 5 - Eyes -->
          <div class="cat-row">
            <span class="p o"></span><span class="p w"></span><span class="p bk"></span><span class="p bk"></span><span class="p w"></span><span class="p w"></span><span class="p w"></span><span class="p w"></span><span class="p bk"></span><span class="p bk"></span><span class="p w"></span><span class="p o"></span>
          </div>
          <!-- Row 6 - Eyes detail -->
          <div class="cat-row">
            <span class="p o"></span><span class="p w"></span><span class="p bk"></span><span class="p bk"></span><span class="p w"></span><span class="p w"></span><span class="p w"></span><span class="p w"></span><span class="p bk"></span><span class="p bk"></span><span class="p w"></span><span class="p o"></span>
          </div>
          <!-- Row 7 - Nose -->
          <div class="cat-row">
            <span class="p o"></span><span class="p w"></span><span class="p w"></span><span class="p w"></span><span class="p br"></span><span class="p br"></span><span class="p br"></span><span class="p br"></span><span class="p w"></span><span class="p w"></span><span class="p w"></span><span class="p o"></span>
          </div>
          <!-- Row 8 - Mouth top -->
          <div class="cat-row">
            <span class="p o"></span><span class="p w"></span><span class="p w"></span><span class="p br"></span><span class="p rd"></span><span class="p rd"></span><span class="p rd"></span><span class="p rd"></span><span class="p br"></span><span class="p w"></span><span class="p w"></span><span class="p o"></span>
          </div>
          <!-- Row 9 - Mouth -->
          <div class="cat-row">
            <span class="p o"></span><span class="p w"></span><span class="p br"></span><span class="p rd"></span><span class="p rd"></span><span class="p rd"></span><span class="p rd"></span><span class="p rd"></span><span class="p rd"></span><span class="p br"></span><span class="p w"></span><span class="p o"></span>
          </div>
          <!-- Row 10 - Chin -->
          <div class="cat-row">
            <span class="p"></span><span class="p o"></span><span class="p br"></span><span class="p br"></span><span class="p br"></span><span class="p br"></span><span class="p br"></span><span class="p br"></span><span class="p br"></span><span class="p br"></span><span class="p o"></span><span class="p"></span>
          </div>
          <!-- Row 11 - Neck/Body start -->
          <div class="cat-row">
            <span class="p"></span><span class="p"></span><span class="p o"></span><span class="p w"></span><span class="p w"></span><span class="p w"></span><span class="p w"></span><span class="p w"></span><span class="p w"></span><span class="p o"></span><span class="p"></span><span class="p"></span>
          </div>
          <!-- Row 12 - Body -->
          <div class="cat-row">
            <span class="p"></span><span class="p o"></span><span class="p w"></span><span class="p w"></span><span class="p o"></span><span class="p o"></span><span class="p o"></span><span class="p o"></span><span class="p w"></span><span class="p w"></span><span class="p o"></span><span class="p"></span>
          </div>
          <!-- Row 13 - Paws -->
          <div class="cat-row">
            <span class="p o"></span><span class="p o"></span><span class="p o"></span><span class="p o"></span><span class="p"></span><span class="p"></span><span class="p"></span><span class="p"></span><span class="p o"></span><span class="p o"></span><span class="p o"></span><span class="p o"></span>
          </div>
        </div>
      </div>
    </div>

    <!-- Timer Settings Modal -->
    <v-dialog v-model="settingsDialog" max-width="500px">
      <v-card rounded="xl" class="pa-6">
        <v-card-title class="text-h6 pa-0 mb-4 d-flex justify-space-between align-center">
          <span class="modal-title">Timer Settings</span>
          <v-btn icon="mdi-close" variant="text" size="small" @click="settingsDialog = false"></v-btn>
        </v-card-title>

        <v-card-text class="pa-0">
          <div class="mb-4">
            <label class="text-body-2 font-weight-medium mb-2 d-block">Study Session Length (minutes)</label>
            <v-text-field v-model="customFocusTime" type="number" density="comfortable" 
                          variant="outlined" rounded="lg" hide-details/>
          </div>

          <div class="mb-6">
            <label class="text-body-2 font-weight-medium mb-2 d-block">Break Length (minutes)</label>
            <v-text-field v-model="customBreakTime" type="number" density="comfortable" 
                          variant="outlined" rounded="lg" hide-details/>
          </div>

          <v-btn block color="primary" rounded="lg" size="large" class="text-none" @click="saveSettings">
            Save Settings
          </v-btn>
        </v-card-text>
      </v-card>
    </v-dialog>
  </div>
</template>

<style scoped>
.timer-page {
  position: relative;
  min-height: 100vh;
  transition: all 0.3s ease;
}

.fullscreen-mode {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 100;
  overflow-y: auto;
}

.fullscreen-container {
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
}

.fullscreen-card {
  max-width: 900px;
  margin: 0 auto;
}

.timer-card {
  background: var(--surface) !important;
  border: 1px solid var(--surface-lighter);
  transition: all 0.3s ease;
  position: relative;
  z-index: 10;
}

.details-card, .streaks-card {
  background: var(--surface) !important;
  border: 1px solid var(--surface-lighter);
  position: relative;
  z-index: 10;
}

.session-box {
  background: var(--surface-light) !important;
  border: 1px solid var(--surface-lighter);
}

.tips-section {
  background: var(--surface-light) !important;
  border: 1px solid var(--surface-lighter);
}

.timer-title,
.session-title,
.tips-title,
.streaks-title,
.modal-title {
  color: var(--primary) !important;
}

.timer-display {
  font-size: 72px;
  font-weight: 600;
  color: var(--primary) !important;
  letter-spacing: -2px;
  transition: font-size 0.3s ease;
}

.timer-display-large {
  font-size: 120px !important;
}

.stat-number,
.streak-number {
  color: var(--primary) !important;
}

.stats-divider {
  border-top: 1px solid var(--surface-lighter);
}

.reset-btn {
  color: var(--primary) !important;
}

.cursor-pointer {
  cursor: pointer;
}

ul {
  padding-left: 20px;
}

li {
  margin-bottom: 4px;
}

/* Falling Leaves Background - BEHIND cards */
.falling-leaves-background {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 1;
  background: linear-gradient(135deg, 
    rgba(255, 245, 230, 0.4) 0%, 
    rgba(255, 229, 204, 0.4) 25%, 
    rgba(255, 218, 179, 0.4) 50%, 
    rgba(255, 207, 153, 0.4) 75%, 
    rgba(255, 194, 128, 0.4) 100%);
}

[data-theme="dark"] .falling-leaves-background {
  background: linear-gradient(135deg, 
    rgba(42, 24, 16, 0.5) 0%, 
    rgba(61, 36, 21, 0.5) 25%, 
    rgba(74, 45, 26, 0.5) 50%, 
    rgba(87, 54, 31, 0.5) 75%, 
    rgba(100, 64, 36, 0.5) 100%);
}

/* Falling Leaves Overlay - IN FRONT of cards */
.falling-leaves-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 20;
}

.leaf {
  position: absolute;
  top: -50px;
  font-size: 28px;
  animation: fall linear infinite;
}

@keyframes fall {
  0% {
    transform: translateY(0) rotate(0deg);
    opacity: 0.9;
  }
  100% {
    transform: translateY(110vh) rotate(360deg);
    opacity: 0.2;
  }
}

/* 8-Bit Pixel Cat Pet */
.pet-container {
  position: fixed;
  bottom: 5%;
  left: 0;
  right: 0;
  height: 100px;
  z-index: 30;
  pointer-events: none;
}

.pixel-cat-wrapper {
  position: absolute;
  bottom: 0;
}

.pixel-cat-wrapper.walking {
  animation: walk-pixel 30s linear infinite;
}

.pixel-cat {
  display: flex;
  flex-direction: column;
  gap: 0;
  image-rendering: pixelated;
  transform-origin: center;
}

.cat-row {
  display: flex;
  gap: 0;
  height: 6px;
}

.p {
  width: 6px;
  height: 6px;
  background: transparent;
}

/* Light mode cat colors */
.p.e { background: #FF8C00; } /* ears - dark orange */
.p.h { background: #FFA500; } /* head - orange */
.p.y { background: #000000; } /* eyes - black */
.p.n { background: #FF6B9D; } /* nose - pink */
.p.m { background: #8B4513; } /* mouth - brown */
.p.b { background: #FFB84D; } /* body - light orange */

/* Dark mode cat colors */
[data-theme="dark"] .p.e { background: #B8A788; }
[data-theme="dark"] .p.h { background: #D7CBB2; }
[data-theme="dark"] .p.y { background: #1A1D23; }
[data-theme="dark"] .p.n { background: #8DAF9B; }
[data-theme="dark"] .p.m { background: #6A7A5A; }
[data-theme="dark"] .p.b { background: #E5D9C3; }

@keyframes walk-pixel {
  0% {
    left: -100px;
    transform: scaleX(1);
  }
  49% {
    left: calc(100% + 100px);
    transform: scaleX(1);
  }
  50% {
    left: calc(100% + 100px);
    transform: scaleX(-1);
  }
  99% {
    left: -100px;
    transform: scaleX(-1);
  }
  100% {
    left: -100px;
    transform: scaleX(1);
  }
}

/* Subtle walking bounce */
.pixel-cat-wrapper.walking .pixel-cat {
  animation: pixel-bounce 0.8s ease-in-out infinite;
}

@keyframes pixel-bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-3px); }
}
</style>