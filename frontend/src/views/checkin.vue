<template>
  <div class="check-in-page">
    <div class="header">
      <h1 class="text-h6 text-md-h5 text-primary font-weight-bold mb-1 px-2 px-md-0">Wellness Check-in</h1>
      <p class="subtitle">Track your wellness and mood</p>
    </div>

    <div class="main-content">
      <div class="wellness-overview">
        <h3 class="section-title">
          <span class="icon">📊</span> Wellness Overview
        </h3>

        <!-- Coin Reward Badge -->
        <div v-if="!hasCheckedInToday" class="coin-reward-badge">
          <AnimatedCoin :scale="1.5" :speed="8" />
          <span class="coin-text">Earn 20 coins today!</span>
        </div>

        <div class="stats-grid">
          <div class="stat-card">
            <div class="stat-label">Streak</div>
            <div class="stat-value">{{ streak }}/7</div>
            <div class="stat-sublabel">This week</div>
          </div>
          <div class="stat-card">
            <div class="stat-label">Total</div>
            <div class="stat-value">{{ totalCheckIns }}</div>
            <div class="stat-sublabel">Check-ins</div>
          </div>
        </div>
      </div>

      <div class="check-in-card">
        <!-- Show message if already checked in today -->
        <div v-if="hasCheckedInToday" class="completion-message">
          <div class="success-icon">✓</div>
          <h3 class="completion-title">{{ getMotivationalMessage }}</h3>
          <p class="completion-subtitle">
            You've completed your check-in for {{ todayFormatted }}. {{ getNextCheckinMessage }}
          </p>
          <p class="coin-reward-message">🎉 You've collected your 20 coins for the day!</p>

          <!-- TEMPORARY: Reset button for testing -->
          <button @click="resetForTesting" class="reset-btn">
            🔄 Reset (Testing Only)
          </button>
        </div>

        <!-- Show check-in form if not checked in today -->
        <div v-else-if="!isCompleted">
          <h3 class="section-title">Today's Check-in</h3>
          <p class="section-subtitle">How are you feeling today?</p>

          <div class="slider-group">
            <div class="slider-header">
              <span class="slider-label">
                <span class="emoji">😊</span> Mood
              </span>
              <span class="slider-value">{{ mood }}/10</span>
            </div>

            <!-- Animated emoji display -->
            <div class="emoji-display">
              <span class="big-emoji" :key="mood">{{ getMoodEmoji }}</span>
            </div>
            
            <!-- Particle container -->
            <div class="particle-container">
              <div 
                v-for="particle in moodParticles" 
                :key="particle.id"
                class="particle"
                :style="{ 
                  left: particle.x + '%',
                  animationDelay: particle.delay + 's'
                }"
              >
                {{ particle.emoji }}
              </div>
            </div>

            <input 
              type="range" 
              v-model.number="mood" 
              min="0" 
              max="10" 
              class="slider"
              :style="{ '--fill-percent': (mood / 10 * 100) + '%' }"
            />
            <p class="slider-feedback">{{ getMoodFeedback }}</p>
          </div>
  
          <div class="slider-group">
            <div class="slider-header">
              <span class="slider-label">
                <span class="emoji">⚡</span> Energy
              </span>
              <span class="slider-value">{{ energy }}/10</span>
            </div>

            <div class="emoji-display">
              <span class="big-emoji" :key="energy">{{ getEnergyEmoji }}</span>
            </div>
            
            <!-- Particle container -->
            <div class="particle-container">
              <div 
                v-for="particle in energyParticles" 
                :key="particle.id"
                class="particle"
                :style="{ 
                  left: particle.x + '%',
                  animationDelay: particle.delay + 's'
                }"
              >
                {{ particle.emoji }}
              </div>
            </div>

            <input 
              type="range" 
              v-model.number="energy" 
              min="0" 
              max="10" 
              class="slider"
              :style="{ '--fill-percent': (energy / 10 * 100) + '%' }"
            />
            <p class="slider-feedback">{{ getEnergyFeedback }}</p>
          </div>

          <div class="slider-group">
            <div class="slider-header">
              <span class="slider-label">
                <span class="emoji">😴</span> Sleep
              </span>
              <span class="slider-value">{{ sleep }}/10</span>
            </div>

            <div class="emoji-display">
              <span class="big-emoji" :key="sleep">{{ getSleepEmoji }}</span>
            </div>
            
            <!-- Particle container -->
            <div class="particle-container">
              <div 
                v-for="particle in sleepParticles" 
                :key="particle.id"
                class="particle"
                :style="{ 
                  left: particle.x + '%',
                  animationDelay: particle.delay + 's'
                }"
              >
                {{ particle.emoji }}
              </div>
            </div>

            <input 
              type="range" 
              v-model.number="sleep" 
              min="0" 
              max="10" 
              class="slider"
              :style="{ '--fill-percent': (sleep / 10 * 100) + '%' }"
            />
            <p class="slider-feedback">{{ getSleepFeedback }}</p>
          </div>

          <div class="slider-group">
            <div class="slider-header">
              <span class="slider-label">
                <span class="emoji">😰</span> Stress
              </span>
              <span class="slider-value">{{ stress }}/10</span>
            </div>

            <div class="emoji-display">
              <span class="big-emoji" :key="stress">{{ getStressEmoji }}</span>
            </div>
            
            <!-- Particle container -->
            <div class="particle-container">
              <div 
                v-for="particle in stressParticles" 
                :key="particle.id"
                class="particle"
                :style="{ 
                  left: particle.x + '%',
                  animationDelay: particle.delay + 's'
                }"
              >
                {{ particle.emoji }}
              </div>
            </div>

            <input 
              type="range" 
              v-model.number="stress" 
              min="0" 
              max="10" 
              class="slider"
              :style="{ '--fill-percent': (stress / 10 * 100) + '%' }"
            />
            <p class="slider-feedback">{{ getStressFeedback }}</p>
          </div>

          <div class="notes-section">
            <label class="notes-label">Notes (optional)</label>
            <textarea 
              v-model="notes" 
              class="notes-textarea"
              placeholder="How was your day? Any thoughts or reflections..."
              rows="4"
            ></textarea>
          </div>

          <button 
            @click="completeCheckIn" 
            :disabled="isSubmitting"
            class="complete-btn"
          >
            {{ isSubmitting ? 'Saving...' : 'Complete Check-in' }}
          </button>
        </div>

        <!-- Show completion message immediately after submitting -->
        <div v-else class="completion-message">
          <div class="success-icon">✓</div>
          <h3>Check-in completed!</h3>
          <p>Great job tracking your wellness today.</p>
          <p class="next-checkin-text">See you tomorrow!</p>

          <!-- TEMPORARY: Reset button for testing -->
          <button @click="resetForTesting" class="reset-btn">
            🔄 Reset (Testing Only)
          </button>
        </div>
      </div>
    </div>

    <div class="history-section">
      <h3 class="section-title">Check-in History</h3>
      <p class="section-subtitle">Click on any date to view your check-in</p>
      
      <div class="history-grid">
        <div class="calendar">
            <div class="calendar-header">
            <button @click="previousMonth" class="nav-btn">‹</button>
            <span class="month-year">{{ currentMonthYear }}</span>
            <button @click="nextMonth" class="nav-btn">›</button>
            </div>
            
            <div class="calendar-grid">
            <div v-for="day in weekDays" :key="day" class="calendar-day-header">
                {{ day }}
            </div>
            <div 
                v-for="date in calendarDates" 
                :key="date.key"
                @click="selectDate(date)"
                :class="['calendar-date', {
                'other-month': date.isOtherMonth,
                'today': date.isToday,
                'selected': date.isSelected,
                'has-checkin': date.hasCheckIn
                }]"
                :style="getDateStyle(date)"
            >
            <span class="date-number">{{ date.day }}</span>
  
            <!-- Hover tooltip -->
            <div v-if="date.hasCheckIn && date.checkInData" class="date-tooltip">
              <div class="tooltip-emoji">{{ getDateEmoji(date.checkInData) }}</div>
              <div class="tooltip-stats">
                <div class="tooltip-row">
                  <span>Mood:</span>
                  <span>{{ date.checkInData.mood }}/10</span>
                </div>
                <div class="tooltip-row">
                  <span>Energy:</span>
                  <span>{{ date.checkInData.energy }}/10</span>
                </div>
              </div>
            </div>

            <!-- Ripple effect container -->
            <span class="ripple"></span>
            </div>
          </div>
        </div>

        <div class="right-sidebar">
          <!-- Legend -->
          <div class="calendar-legend">
            <h4 class="legend-title">Wellness Score</h4>
            <div class="legend-items">
              <div class="legend-item">
                <div class="legend-color legend-green"></div>
                <span class="legend-label">Great (8-10)</span>
              </div>
              <div class="legend-item">
                <div class="legend-color legend-blue"></div>
                <span class="legend-label">Good (6-7.9)</span>
              </div>
              <div class="legend-item">
                <div class="legend-color legend-yellow"></div>
                <span class="legend-label">Okay (4-5.9)</span>
              </div>
              <div class="legend-item">
                <div class="legend-color legend-red"></div>
                <span class="legend-label">Needs Care (&lt;4)</span>
              </div>
            </div>
          </div>

        <div class="pet-stats-panel" v-if="selectedCheckInData">
            <h3 class="section-title">Check-in for {{ selectedDateFormatted }}</h3>

                <div class="pet-stat">
                    <span class="label">Mood:</span>
                    <span class="value">{{ selectedCheckInData.mood }}/10</span>
                </div>

                <div class="pet-stat">
                    <span class="label">Energy:</span>
                    <span class="value">{{ selectedCheckInData.energy }}/10</span>
                </div>

                <div class="pet-stat">
                    <span class="label">Sleep:</span>
                    <span class="value">{{ selectedCheckInData.sleep }}/10</span>
                </div>

                <div class="pet-stat">
                    <span class="label">Stress:</span>
                    <span class="value">{{ selectedCheckInData.stress }}/10</span>
                </div>

                <div v-if="selectedCheckInData.notes" class="notes-display">
                    <span class="label">Notes:</span>
                    <p class="notes-content">{{ selectedCheckInData.notes }}</p>
                </div>
            </div>

            <div v-else class="pet-stats-empty">
                <p>No check-in recorded for this date</p>
            </div>
        </div>
      </div>
    </div>
    
    <div class="wellness-tips">
      <h3 class="section-title">Wellness Tips</h3>
      
      <div class="tips-grid">
        <div class="tip-card">
          <h4 class="tip-title">
            <span class="tip-icon">😊</span> Mood Boosters:
          </h4>
          <ul class="tip-list">
            <li>Practice gratitude daily</li>
            <li>Connect with friends and family</li>
          </ul>
        </div>
        
        <div class="tip-card">
          <h4 class="tip-title">
            <span class="tip-icon">⚡</span> Energy Management:
          </h4>
          <ul class="tip-list">
            <li>Maintain regular sleep schedule</li>
            <li>Stay hydrated throughout the day</li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch} from 'vue'
import { getFirestore, collection, addDoc, query, where, getDocs, orderBy } from 'firebase/firestore'
import { getAuth } from 'firebase/auth'
import { useCoins } from '@/composables/useCoins.js'
import { api } from '@/lib/api.js'
import confetti from 'canvas-confetti'
import AnimatedCoin from '@/components/AnimatedCoin.vue'
import { useUserProfile } from '@/composables/useUserProfile.js' 

// Initialize Firebase instances
const db = getFirestore()
const auth = getAuth()

// Coins composable (shared state with sidebar)
const { coins, updateCoins } = useCoins()

// User Profile composable
const { displayName } = useUserProfile()

// State
const mood = ref(7)
const energy = ref(7)
const sleep = ref(7)
const stress = ref(3)

// Particle effects
const moodParticles = ref([])
const energyParticles = ref([])
const sleepParticles = ref([])
const stressParticles = ref([])
const notes = ref('')
const isCompleted = ref(false)
const streak = ref(0)
const totalCheckIns = ref(0)
const isSubmitting = ref(false)
const hasCheckedInToday = ref(false)
const checkInHistory = ref({})

// Sliders for particle generation
watch(mood, (newVal, oldVal) => {
  if (Math.abs(newVal - oldVal) > 0) {
    createParticle('mood', newVal)
  }
})

watch(energy, (newVal, oldVal) => {
  if (Math.abs(newVal - oldVal) > 0) {
    createParticle('energy', newVal)
  }
})

watch(sleep, (newVal, oldVal) => {
  if (Math.abs(newVal - oldVal) > 0) {
    createParticle('sleep', newVal)
  }
})

watch(stress, (newVal, oldVal) => {
  if (Math.abs(newVal - oldVal) > 0) {
    createParticle('stress', newVal)
  }
})

const createParticle = (type, value) => {
  const particleId = Date.now() + Math.random()
  const emoji = getParticleEmoji(type, value)
  
  const particle = {
    id: particleId,
    emoji: emoji,
    x: Math.random() * 100,
    delay: Math.random() * 0.3
  }
  
  if (type === 'mood') moodParticles.value.push(particle)
  if (type === 'energy') energyParticles.value.push(particle)
  if (type === 'sleep') sleepParticles.value.push(particle)
  if (type === 'stress') stressParticles.value.push(particle)

    // Remove after animation
  setTimeout(() => {
    if (type === 'mood') moodParticles.value = moodParticles.value.filter(p => p.id !== particleId)
    if (type === 'energy') energyParticles.value = energyParticles.value.filter(p => p.id !== particleId)
    if (type === 'sleep') sleepParticles.value = sleepParticles.value.filter(p => p.id !== particleId)
    if (type === 'stress') stressParticles.value = stressParticles.value.filter(p => p.id !== particleId)
  }, 1000)
}

const getParticleEmoji = (type, value) => {
  if (type === 'mood') {
    if (value >= 8) return '✨'
    if (value >= 5) return '💫'
    return '💧'
  }
  if (type === 'energy') {
    if (value >= 8) return '⚡'
    if (value >= 5) return '💪'
    return '💤'
  }
  if (type === 'sleep') {
    if (value >= 8) return '🌙'
    if (value >= 5) return '⭐'
    return '☁️'
  }
  if (type === 'stress') {
    if (value <= 3) return '🌸'
    if (value <= 6) return '🍃'
    return '💨'
  }
  return '✨'
}

// Calendar state
const currentDate = ref(new Date())
const selectedDate = ref(new Date())
const weekDays = ['Su', 'Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa']

// Helper function to get date string in YYYY-MM-DD format
const getDateString = (date) => {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

const todayDateString = computed(() => getDateString(new Date()))

const todayFormatted = computed(() => {
  return new Date().toLocaleDateString('en-US', { 
    weekday: 'long',
    month: 'long', 
    day: 'numeric',
    year: 'numeric'
  })
})

// Check if user has already checked in today 
const checkTodayCheckIn = async () => {
  const user = auth.currentUser
  if (!user) return

  try {
    // Get today's date string
    const today = new Date()
    const year = today.getFullYear()
    const month = String(today.getMonth() + 1).padStart(2, '0')
    const day = String(today.getDate()).padStart(2, '0')
    const todayStr = `${year}-${month}-${day}`

    // Use wellness overview API to check today's status
    const overview = await api.get('/api/wellness/overview')
    
    // Check if last check-in date matches today
    hasCheckedInToday.value = (overview.lastCheckInDate === todayStr)
    
    // Also update streak from API
    if (overview.streak !== undefined) {
      streak.value = overview.streak
    }
  } catch (error) {
    console.error('Error checking today\'s check-in:', error)
    // Fallback: try to check from monthly check-ins
    try {
      const today = new Date()
      const year = today.getFullYear()
      const month = String(today.getMonth() + 1).padStart(2, '0')
      const day = String(today.getDate()).padStart(2, '0')
      const todayStr = `${year}-${month}-${day}`
      
      const monthData = await api.get(`/api/wellness/checkins?month=${month}&year=${year}`)
      hasCheckedInToday.value = (monthData.checkInDates || []).includes(todayStr)
    } catch (fallbackError) {
      console.error('Fallback check also failed:', fallbackError)
    }
  }
}

// Load all check-ins for the user
const loadCheckIns = async () => {
  const user = auth.currentUser
  if (!user) return

  try {
    // Load check-ins for current month and previous month (for calendar display)
    const today = new Date()
    const currentYear = today.getFullYear()
    const currentMonth = today.getMonth() + 1
    
    // Load current month
    const currentMonthData = await api.get(`/api/wellness/checkins?month=${currentMonth}&year=${currentYear}`)
    
    // Load previous month (for calendar that shows previous month dates)
    let prevMonth = currentMonth - 1
    let prevYear = currentYear
    if (prevMonth < 1) {
      prevMonth = 12
      prevYear = currentYear - 1
    }
    const prevMonthData = await api.get(`/api/wellness/checkins?month=${prevMonth}&year=${prevYear}`)
    
    // Combine check-ins from both months
    const allCheckIns = [...currentMonthData.checkIns, ...prevMonthData.checkIns]
    
    // Build history object
    const history = {}
    allCheckIns.forEach((checkIn) => {
      history[checkIn.date] = {
        mood: checkIn.mood,
        energy: checkIn.energy,
        sleep: checkIn.sleep,
        stress: checkIn.stress,
        notes: checkIn.notes || ''
      }
    })
    
    checkInHistory.value = history
    totalCheckIns.value = allCheckIns.length
    
    // Update streak from API overview
    try {
      const overview = await api.get('/api/wellness/overview')
      streak.value = overview.streak || 0
    } catch (overviewError) {
      console.error('Error loading overview for streak:', overviewError)
      calculateStreak() // Fallback to local calculation
    }
  } catch (error) {
    console.error('Error loading check-ins:', error)
    // Fallback to local calculation if API fails
    calculateStreak()
  }
}

// Calculate current streak
const calculateStreak = () => {
  let currentStreak = 0
  const today = new Date()
  
  for (let i = 0; i < 7; i++) {
    const checkDate = new Date(today)
    checkDate.setDate(checkDate.getDate() - i)
    const dateStr = getDateString(checkDate)
    
    if (checkInHistory.value[dateStr]) {
      currentStreak++
    } else {
      break
    }
  }
  
  streak.value = currentStreak
}

// Computed properties
const selectedCheckInData = computed(() => {
  const key = getDateString(selectedDate.value) 
  return checkInHistory.value[key] || null
})

const selectedDateFormatted = computed(() => {
  return selectedDate.value.toLocaleDateString('en-US', { 
    month: 'long', 
    day: 'numeric',
    year: 'numeric'
  })
})

// Emoji reactions for each metric
const getMoodEmoji = computed(() => {
  if (mood.value >= 9) return '🤩'
  if (mood.value >= 7) return '😊'
  if (mood.value >= 5) return '🙂'
  if (mood.value >= 3) return '😐'
  if (mood.value >= 1) return '☹️'
  return '😢'
})

const getEnergyEmoji = computed(() => {
  if (energy.value >= 9) return '⚡'
  if (energy.value >= 7) return '💪'
  if (energy.value >= 5) return '👍'
  if (energy.value >= 3) return '😴'
  if (energy.value >= 1) return '🪫'
  return '💤'
})

const getSleepEmoji = computed(() => {
  if (sleep.value >= 9) return '😴'
  if (sleep.value >= 7) return '🛌'
  if (sleep.value >= 5) return '😌'
  if (sleep.value >= 3) return '🥱'
  if (sleep.value >= 1) return '😵'
  return '😵‍💫'
})

const getStressEmoji = computed(() => {
  if (stress.value >= 9) return '😱'
  if (stress.value >= 7) return '😰'
  if (stress.value >= 5) return '😅'
  if (stress.value >= 3) return '😌'
  if (stress.value >= 1) return '😊'
  return '🧘'
})

const getMoodFeedback = computed(() => {
  if (mood.value >= 8) return 'Feeling great!'
  if (mood.value >= 6) return 'Pretty good'
  if (mood.value >= 4) return 'Okay'
  return 'Could be better'
})

const getEnergyFeedback = computed(() => {
  if (energy.value >= 8) return 'High energy!'
  if (energy.value >= 6) return 'Good energy'
  if (energy.value >= 4) return 'Moderate energy'
  return 'Low energy'
})

const getSleepFeedback = computed(() => {
  if (sleep.value >= 8) return 'Great sleep!'
  if (sleep.value >= 6) return 'Good sleep'
  if (sleep.value >= 4) return 'Okay sleep'
  return 'Poor sleep'
})

const getStressFeedback = computed(() => {
  if (stress.value >= 8) return 'Very stressed'
  if (stress.value >= 6) return 'Moderate stress'
  if (stress.value >= 4) return 'Some stress'
  return 'Low stress'
})

const currentMonthYear = computed(() => {
  return currentDate.value.toLocaleDateString('en-US', { 
    month: 'long', 
    year: 'numeric' 
  })
})

const calendarDates = computed(() => {
  const year = currentDate.value.getFullYear()
  const month = currentDate.value.getMonth()
  
  const firstDay = new Date(year, month, 1)
  const lastDay = new Date(year, month + 1, 0)
  const prevLastDay = new Date(year, month, 0)
  
  const firstDayOfWeek = firstDay.getDay()
  const lastDate = lastDay.getDate()
  const prevLastDate = prevLastDay.getDate()
  
  const dates = []
  
  // Previous month dates
  for (let i = firstDayOfWeek - 1; i >= 0; i--) {
    dates.push({
        day: prevLastDate - i,
        isOtherMonth: true,
        isToday: false,
        isSelected: false,
        hasCheckIn: false,
        checkInData: null,
        key: `prev-${prevLastDate - i}`
    })
  }
  
  // Current month dates
  const today = new Date()
  for (let i = 1; i <= lastDate; i++) {
    const isToday = i === today.getDate() && 
                    month === today.getMonth() && 
                    year === today.getFullYear()

    const dateStr = `${year}-${String(month + 1).padStart(2, '0')}-${String(i).padStart(2, '0')}` 
    
    dates.push({
        day: i,
        isOtherMonth: false,
        isToday,
        isSelected: i === selectedDate.value.getDate() && 
                    month === selectedDate.value.getMonth() &&
                    year === selectedDate.value.getFullYear(),
        // Check if there's a check-in for that specific date 
        hasCheckIn: checkInHistory.value[dateStr] !== undefined,
        checkInData: checkInHistory.value[dateStr] || null,
        key: `current-${i}`
    })
  }
  
  // Next month dates
  const remainingDays = 42 - dates.length
  for (let i = 1; i <= remainingDays; i++) {
    dates.push({
      day: i,
      isOtherMonth: true,
      isToday: false,
      isSelected: false,
      hasCheckIn: false,
      key: `next-${i}`
    })
  }
  
  return dates
})

const motivationalMessages = [
  "Amazing work, {name}! 🌟",
  "You're crushing it, {name}! 💪",
  "Fantastic, {name}! Keep it up! 🎉",
  "Way to go, {name}! ✨",
  "Awesome job, {name}! 🚀",
  "You're on fire, {name}! 🔥",
  "Brilliant, {name}! 🌈",
  "Outstanding, {name}! 💫",
  "Keep shining, {name}! ⭐",
  "You're unstoppable, {name}! 🎯"
]

const getMotivationalMessage = computed(() => {
  const today = new Date().toDateString()
  // Use date as seed for consistent message per day
  const index = today.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0) % motivationalMessages.length
  return motivationalMessages[index].replace('{name}', displayName.value || 'there')
})

const getNextCheckinMessage = computed(() => {
  const messages = [
    "Come back tomorrow to keep your streak going!",
    "See you tomorrow for another check-in!",
    "Your wellness journey continues tomorrow!",
    "Can't wait to see you again tomorrow!",
    "Tomorrow brings another opportunity!"
  ]
  const today = new Date().toDateString()
  const index = today.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0) % messages.length
  return messages[index]
})

// Methods
const completeCheckIn = async () => {
  if (hasCheckedInToday.value) {
    return // Prevent double submission
  }

  isSubmitting.value = true
  const user = auth.currentUser

  if (!user) {
    alert('Please log in to save your check-in')
    isSubmitting.value = false
    return
  }

  try {
    // Get today's date in YYYY-MM-DD format
    const today = new Date()
    const year = today.getFullYear()
    const month = String(today.getMonth() + 1).padStart(2, '0')
    const day = String(today.getDate()).padStart(2, '0')
    const dateStr = `${year}-${month}-${day}`

    // Submit check-in using the wellness API endpoint
    const checkInPayload = {
      date: dateStr,
      mood: mood.value,
      energy: energy.value,
      sleep: sleep.value,
      stress: stress.value,
      notes: notes.value || null
    }

    const response = await api.post('/api/wellness/checkin', checkInPayload)

    // Update local state
    isCompleted.value = true
    hasCheckedInToday.value = true

    // Confetti Celebration
    triggerCelebration()

    // Award coins for completing wellness check-in (20 coins)
    try {
      const currentCoins = coins.value || 0
      const newCoins = currentCoins + 20

      const result = await updateCoins(newCoins)
      if (result.success) {
        console.log(`✅ Wellness check-in rewarded 20 coins! Total: ${newCoins}`)
      }
    } catch (coinError) {
      console.error('Error awarding coins:', coinError)
      // Don't fail the check-in if coins fail to update
    }

    // Update streak from API response
    if (response.overview) {
      streak.value = response.overview.streak || 0
    }

    // Reload data
    await loadCheckIns()

    // Emit event to notify other components (e.g., profile.vue) that a check-in was submitted
    window.dispatchEvent(new CustomEvent('wellness-checkin-submitted', {
      detail: {
        date: dateStr,
        streak: response.overview?.streak || streak.value,
        overview: response.overview
      }
    }))
  } catch (error) {
    console.error('Error saving check-in:', error)
    alert('Failed to save check-in. Please try again.')
  } finally {
    isSubmitting.value = false
  }
}

const triggerCelebration = () => {
  // Main confetti burst
  confetti({
    particleCount: 150,
    spread: 120,
    origin: { y: 0.6 },
    colors: ['#5a8a7a', '#6A7A5A', '#AAC4BC', '#FFD700', '#FF69B4']
  })
  
  // Side bursts
  setTimeout(() => {
    confetti({
      particleCount: 80,
      angle: 60,
      spread: 80,
      origin: { x: 0 },
      colors: ['#5a8a7a', '#AAC4BC', '#FFD700']
    })
  }, 200)
  
  setTimeout(() => {
    confetti({
      particleCount: 80,
      angle: 120,
      spread: 80,
      origin: { x: 1 },
      colors: ['#5a8a7a', '#AAC4BC', '#FFD700']
    })
  }, 400)
  
  // Emoji confetti!
  setTimeout(() => {
    confetti({
      particleCount: 30,
      spread: 100,
      origin: { y: 0.6 },
      shapes: ['circle'],
      scalar: 2,
      colors: ['#FF69B4', '#FFD700', '#98FB98']
    })
  }, 300)
}

const previousMonth = () => {
  currentDate.value = new Date(
    currentDate.value.getFullYear(),
    currentDate.value.getMonth() - 1,
    1
  )
}

const nextMonth = () => {
  currentDate.value = new Date(
    currentDate.value.getFullYear(),
    currentDate.value.getMonth() + 1,
    1
  )
}

const selectDate = (date) => {
  if (!date.isOtherMonth) {
    selectedDate.value = new Date(
      currentDate.value.getFullYear(),
      currentDate.value.getMonth(),
      date.day
    )
  }
}

// Get heat map background color based on overall wellness score
const getDateStyle = (date) => {
  if (!date.hasCheckIn || date.isOtherMonth) return {}
  
  const dateStr = `${currentDate.value.getFullYear()}-${String(currentDate.value.getMonth() + 1).padStart(2, '0')}-${String(date.day).padStart(2, '0')}`
  const data = checkInHistory.value[dateStr]
  
  if (!data) return {}
  
  const average = (data.mood + data.energy + data.sleep + (10 - data.stress)) / 4
  
  let color
  if (average >= 8) color = 'rgba(74, 222, 128, 0.3)' // Green
  else if (average >= 6) color = 'rgba(96, 165, 250, 0.3)' // Blue
  else if (average >= 4) color = 'rgba(251, 191, 36, 0.3)' // Yellow
  else color = 'rgba(248, 113, 113, 0.3)' // Red
  
  return { 
    background: color,
    transform: 'scale(1)'
  }
}

// Get mood color for the indicator dot
const getMoodColor = (mood) => {
  if (mood >= 8) return '#10b981' // Green
  if (mood >= 6) return '#3b82f6' // Blue
  if (mood >= 4) return '#f59e0b' // Orange
  return '#ef4444' // Red
}

// Get emoji for date based on overall wellness
const getDateEmoji = (data) => {
  const average = (data.mood + data.energy + data.sleep + (10 - data.stress)) / 4
  if (average >= 8) return '🌟'
  if (average >= 6) return '😊'
  if (average >= 4) return '😐'
  return '😔'
}

// TEMPORARY: Reset for testing purposes
const resetForTesting = () => {
  isCompleted.value = false
  hasCheckedInToday.value = false
  mood.value = 7
  energy.value = 7
  sleep.value = 7
  stress.value = 3
  notes.value = ''
  
  console.log('✅ Reset for testing - you can check in again!')
}

// TEMPORARY: Add test data
const addTestData = async () => {
  const user = auth.currentUser
  if (!user) {
    console.log('No user logged in')
    return
  }

  const testDays = 20 // Add 20 days of test data
  const promises = []

  for (let i = 0; i < testDays; i++) {
    const testDate = new Date()
    testDate.setDate(testDate.getDate() - i)
    
    const dayOfWeek = testDate.getDay()
    const isWeekend = dayOfWeek === 0 || dayOfWeek === 6
    
    // Better moods on weekends, lower stress
    const moodBoost = isWeekend ? 2 : 0
    const stressReduction = isWeekend ? 3 : 0

    const checkInData = {
      userId: user.uid,
      date: testDate,
      mood: Math.min(10, Math.floor(Math.random() * 5) + 5 + moodBoost), // 5-10, higher on weekends
      energy: Math.floor(Math.random() * 6) + 4, // 4-9
      sleep: Math.floor(Math.random() * 5) + 5, // 5-9
      stress: Math.max(0, Math.floor(Math.random() * 7) - stressReduction), // 0-6, lower on weekends
      notes: isWeekend ? '🎉 Weekend vibes!' : `Check-in for ${testDate.toLocaleDateString()}`,
      createdAt: new Date()
    }

    promises.push(addDoc(collection(db, 'wellnessCheckIns'), checkInData))
  }

  try {
    await Promise.all(promises)
    console.log(`✅ Added ${testDays} realistic test check-ins!`)
    
    // Reload data
    await loadCheckIns()
  } catch (error) {
    console.error('Error adding test data:', error)
  }
}

// Load data when component mounts 
onMounted(async () => {
  await checkTodayCheckIn()
  await loadCheckIns()

  // TEMPORARY: Auto-add test data if calendar is empty
  if (totalCheckIns.value < 100) {
    console.log('Adding test data to visualize calendar...')
    await addTestData()
  }

  // DEBUG: Check if data loaded
  console.log('Check-in history:', checkInHistory.value)
  console.log('Total check-ins:', totalCheckIns.value)
  console.log('Sample date check (2025-10-29):', checkInHistory.value['2025-10-29'])
})


</script>

<style scoped>
.check-in-page {
  max-width: 1400px;
  margin: 0 auto;
  padding: 2rem;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  background: var(--background);
  min-height: 100vh;
}

.header {
  margin-bottom: 2rem;
}

.header h1 {
  font-size: 2rem;
  font-weight: 600;
  color: (--text-primary);
  margin: 0 0 0.5rem 0;
}

.subtitle {
  color: var(--text-muted);
  margin: 0;
  font-size: 0.95rem;
}

.main-content {
  display: grid;
  grid-template-columns: 300px 1fr;
  gap: 1.5rem;
  margin-bottom: 2rem;
  align-items: start;
}

/* Wellness Overview */
.wellness-overview {
  background: var(--surface);
  border: 1px solid var(--surface-lighter);
  border-radius: 12px;
  padding: 1.5rem;
  height: fit-content;
}

/* Coin Reward Badge */
.coin-reward-badge {
  background: linear-gradient(135deg, rgba(255, 215, 0, 0.15), rgba(255, 215, 0, 0.1));
  border: 2px solid rgba(255, 215, 0, 0.4);
  border-radius: 12px;
  padding: 12px;
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 1rem;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.coin-reward-badge::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 215, 0, 0.1), transparent);
  transition: left 0.6s;
}

.coin-reward-badge:hover::before {
  left: 100%;
}

.coin-reward-badge:hover {
  background: linear-gradient(135deg, rgba(255, 215, 0, 0.2), rgba(255, 215, 0, 0.15));
  border-color: rgba(255, 215, 0, 0.6);
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(255, 215, 0, 0.3);
}

.coin-text {
  font-size: 14px;
  font-weight: 600;
  color: #b8860b;
  flex: 1;
}

/* Coin Reward Message in completion */
.coin-reward-message {
  color: #b8860b;
  font-weight: 600;
  font-size: 1rem;
  margin: 0.75rem 0;
  animation: fadeIn 0.5s ease;
}

.section-title {
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 1rem 0;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.icon {
  font-size: 1.1rem;
}

.stats-grid {
  display: grid;
  gap: 0.75rem;
}

.stat-card {
  background: var(--background);
  border: 1px solid rgba(170,196,188,0.25);
  border-radius: 10px;
  padding: 1rem;
  text-align: center;
}

/* Pulsing streak animation when active */
.stat-card:first-child .stat-value {
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% {
    transform: scale(1);
    text-shadow: 0 0 5px rgba(255, 215, 0, 0.3);
  }
  50% {
    transform: scale(1.05);
    text-shadow: 0 0 15px rgba(255, 215, 0, 0.6), 0 0 25px rgba(255, 215, 0, 0.4);
  }
}

.stat-label {
  font-size: 0.8rem;
  color: var(--text-muted);
  margin-bottom: 0.4rem;
}

.stat-value {
  font-size: 1.75rem;
  font-weight: 700;
  color: var(--primary);
  margin-bottom: 0.2rem;
}

.stat-sublabel {
  font-size: 0.75rem;
  color: #888;
}

/* Check-in Card */
.check-in-card {
  background: var(--background);
  border: 1.5px solid rgba(170,196,188,0.4);
  border-radius: 12px;
  padding: 2rem;
}

.section-subtitle {
  color: var(--text-muted);
  margin: 0 0 1.5rem 0;
  font-size: 0.95rem;
}

.next-checkin-text {
  color: var(--text-muted);
  font-size: 0.9rem;
  margin-top: 0.5rem;
}

.notes-display {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid #eee;
}

.notes-display .label {
  display: block;
  color: var(--text-muted);
  margin-bottom: 0.5rem;
  font-weight: 500;
}

.notes-content {
  color: var(--text-primary);
  margin: 0;
  white-space: pre-wrap;
  line-height: 1.6;
}

/* Sliders */
.slider-group {
  margin-bottom: 1.75rem;
}

.slider-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
}

.slider-label {
  font-weight: 500;
  color: #333;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.emoji {
  font-size: 1.1rem;
}

.slider-value {
  font-weight: 600;
  color: var(--primary);
  font-size: 0.95rem;
}

.slider {
  width: 100%;
  height: 12px;
  border-radius: 20px;
  background: #e5e5e5;
  outline: none;
  -webkit-appearance: none;
  margin-bottom: 0.5rem;
  position: relative;
  transition: all 0.3s ease;
  box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.1);
}

.slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: white;
  cursor: pointer;
  border: 3px solid var(--primary);
  box-shadow: 0 2px 8px rgba(90, 138, 122, 0.4);
  transition: all 0.2s ease;
  position: relative;
  z-index: 2;
}

.slider::-moz-range-thumb {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: white;
  cursor: pointer;
  border: 3px solid var(--primary);
  box-shadow: 0 2px 8px rgba(90, 138, 122, 0.4);
  transition: all 0.2s ease;
}

/* Filled track (green fill) for Webkit browsers */
.slider::-webkit-slider-runnable-track {
  width: 100%;
  height: 12px;
  background: linear-gradient(to right, 
    var(--primary) 0%, 
    var(--primary) var(--fill-percent, 70%), 
     #e5e5e5 var(--fill-percent, 70%)
  );
  border-radius: 20px;
} 

/* Filled track for Firefox */
.slider::-moz-range-progress {
  height: 12px;
  background: linear-gradient(90deg, #5a8a7a 0%, #6fa88e 100%);
  border-radius: 20px;
  box-shadow: 0 2px 4px rgba(90, 138, 122, 0.3);
}

.slider-feedback {
  font-size: 0.85rem;
  color: var(--primary);
  margin: 0;
  font-weight: 500;
}

/* Notes */
.notes-section {
  margin-bottom: 1.5rem;
}

.notes-label {
  display: block;
  font-weight: 500;
  color: #333;
  margin-bottom: 0.5rem;
  font-size: 0.95rem;
}

.notes-textarea {
  width: 100%;
  padding: 0.875rem;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-family: inherit;
  font-size: 0.95rem;
  resize: vertical;
  background: var(--surface);
}

.notes-textarea:focus {
  outline: none;
  border-color: var(--primary);
}

/* Complete Button */
.complete-btn {
  width: 100%;
  padding: 1rem;
  background: #6A7A5A;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s;
}

.complete-btn:hover {
  background: #5a6a4a;
}

/* Completion Message */
.completion-message {
  text-align: center;
  padding: 2rem;
}

.success-icon {
  width: 60px;
  height: 60px;
  background: var(--primary);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
  margin: 0 auto 1rem;
}

.completion-message h3 {
  color: var(--text-primary);
  margin: 0 0 0.5rem 0;
}

.completion-message p {
  color: var(--text-muted);
  margin: 0 0 1.5rem 0;
}

.reset-btn {
  padding: 0.75rem 1.5rem;
  background: var(--surface);
  color: var(--primary);
  border: 1px solid #5a8a7a;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
}

.reset-btn:hover {
  background: #f5f5f5;
}

/* Calendar */
.history-section {
  background: var(--surface);
  border: 1px solid var(--surface-lighter);
  border-radius: 12px;
  padding: 2rem;
  margin-bottom: 2rem;
}

.calendar {
  max-width: 500px;
  margin-top: 1.5rem;
}

.calendar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.month-year {
  font-weight: 600;
  color: var(--text-primary);
}

.nav-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: var(--primary);
  padding: 0.25rem 0.75rem;
}

.nav-btn:hover {
  background: #f5f5f5;
  border-radius: 4px;
}

.calendar-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 0.25rem;
}

.calendar-day-header {
  text-align: center;
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--text-muted);
  padding: 0.5rem;
}

.calendar-date {
  aspect-ratio: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
  font-weight: 500;
}
.date-number {
  position: relative;
  z-index: 2;
}

/* Heat map effect for check-in dates */
.calendar-date.has-checkin {
  font-weight: 600;
  border: 2px solid rgba(90, 138, 122, 0.3);
}

.calendar-date.has-checkin:hover {
  transform: scale(1.15) translateY(-2px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15);
  border-color: var(--primary);
  z-index: 10;
}

/* Hover tooltip */
.date-tooltip {
  position: absolute;
  bottom: 110%;
  left: 50%;
  transform: translateX(-50%) translateY(10px);
  background: rgba(0, 0, 0, 0.9);
  color: white;
  padding: 0.75rem;
  border-radius: 8px;
  font-size: 0.75rem;
  white-space: nowrap;
  opacity: 0;
  pointer-events: none;
  transition: all 0.3s ease;
  z-index: 100;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
  min-width: 120px;
}

.date-tooltip::after {
  content: '';
  position: absolute;
  top: 100%;
  left: 50%;
  transform: translateX(-50%);
  border: 6px solid transparent;
  border-top-color: rgba(0, 0, 0, 0.9);
}

.calendar-date:hover .date-tooltip {
  opacity: 1;
  transform: translateX(-50%) translateY(0);
}

.tooltip-emoji {
  font-size: 1.5rem;
  text-align: center;
  margin-bottom: 0.5rem;
}

.tooltip-stats {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.tooltip-row {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
}

.tooltip-row span:first-child {
  opacity: 0.7;
}

.tooltip-row span:last-child {
  font-weight: 600;
  color: #4ade80;
}

/* Ripple effect on click */
.ripple {
  position: absolute;
  border-radius: 50%;
  background: rgba(90, 138, 122, 0.5);
  width: 100%;
  height: 100%;
  transform: scale(0);
  opacity: 0;
  pointer-events: none;
}

.calendar-date:active .ripple {
  animation: ripple-animation 0.6s ease-out;
}

@keyframes ripple-animation {
  to {
    transform: scale(2.5);
    opacity: 0;
  }
}

/* Today highlighting */
.calendar-date.today {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  font-weight: 700;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
  border: none;
}

.calendar-date.today:hover {
  transform: scale(1.15) translateY(-2px);
  box-shadow: 0 8px 20px rgba(102, 126, 234, 0.6);
}

/* Selected date */
.calendar-date.selected {
  background: var(--primary);
  color: white;
  font-weight: 700;
  box-shadow: 0 4px 12px rgba(90, 138, 122, 0.5);
}

/* Remove old dot indicator */
.calendar-date.has-checkin::after {
  display: none;
}

/* Month transition animation */
.calendar-grid {
  animation: fadeIn 0.4s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Hover effect for all dates */
.calendar-date:not(.other-month):hover {
  background: rgba(90, 138, 122, 0.1);
  transform: scale(1.1);
}

.calendar-date.other-month {
  opacity: 0.3;
  cursor: default;
}

.calendar-date.other-month:hover {
  transform: none;
  background: none;
}

/* Wellness Tips */
.wellness-tips {
  background: var(--surface);
  border: 1px solid var(--surface-lighter);
  border-radius: 12px;
  padding: 2rem;
}

.tips-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
  margin-top: 1.5rem;
}

.tip-card {
  padding: 1.25rem;
  background: var(--background);
  border: 1px solid rgba(170,196,188,0.2);
  border-radius: 10px;
}

.tip-title {
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 0.75rem 0;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.tip-icon {
  font-size: 1.1rem;
}

.tip-list {
  margin: 0;
  padding-left: 1.25rem;
  color: var(--text-muted);
}

.tip-list li {
  margin-bottom: 0.5rem;
  font-size: 0.9rem;
}

.tip-list li:last-child {
  margin-bottom: 0;
}

/* Pet Stats Panel */
.pet-stats-panel, .pet-stats-empty {
  margin-top: 1.5rem;
  padding: 1.5rem;
  background: var(--surface);
  border: 1px solid rgba(170,196,188,0.25);
  border-radius: 12px;
}

.pet-stat {
  display: flex;
  justify-content: space-between;
  padding: 0.5rem 0;
  font-size: 0.95rem;
}

.pet-stat .label {
  color: var(--text-muted);
}

.pet-stat .value {
  font-weight: 600;
  color: var(--primary);
}

/* Responsive */
@media (max-width: 768px) {
  .main-content {
    grid-template-columns: 1fr;
  }
  
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

.history-grid {
  display: grid;
  grid-template-columns: 1fr 1fr; /* two equal columns */
  gap: 1.5rem; /* spacing between columns */
}

@media (max-width: 768px) {
  .history-grid {
    grid-template-columns: 1fr; /* stack vertically on small screens */
  }
}

.pet-stats-panel-wrapper {
  background: var(--surface);
  border: 1px solid var(--surface-lighter);
  border-radius: 12px;
  padding: 1.5rem;
}

/* Animated Emoji Display */
.emoji-display {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 80px;
  margin-bottom: 0.5rem;
  position: relative;
}

.big-emoji {
  font-size: 4rem;
  animation: emojiPop 0.4s cubic-bezier(0.68, -0.55, 0.265, 1.55);
  display: inline-block;
  filter: drop-shadow(0 4px 8px rgba(0,0,0,0.1));
}

@keyframes emojiPop {
  0% {
    transform: scale(0.5) rotate(-20deg);
    opacity: 0;
  }
  50% {
    transform: scale(1.15) rotate(5deg);
  }
  100% {
    transform: scale(1) rotate(0deg);
    opacity: 1;
  }
}

/* Particle System */
.slider-group {
  position: relative;
  margin-bottom: 1.75rem;
}

.particle-container {
  position: absolute;
  top: 145px;
  left: 0;
  right: 0;
  height: 60px;
  pointer-events: none;
  overflow: hidden;
}

.particle {
  position: absolute;
  font-size: 1.5rem;
  animation: floatUp 1s ease-out forwards;
  opacity: 0;
}

@keyframes floatUp {
  0% {
    transform: translateY(0) scale(1) rotate(0deg);
    opacity: 1;
  }
  50% {
    opacity: 1;
    transform: translateY(-20px) scale(1.3) rotate(180deg);
  }
  100% {
    transform: translateY(-60px) scale(0.5) rotate(360deg);
    opacity: 0;
  }
}

/* Pulsing animation for slider feedback */
.slider-feedback {
  font-size: 0.85rem;
  color: var(--primary);
  margin: 0;
  font-weight: 500;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-5px); }
  to { opacity: 1; transform: translateY(0); }
}

/* Complete button with extra pizzazz */
.complete-btn {
  width: 100%;
  padding: 1rem;
  background: linear-gradient(135deg, #6A7A5A 0%, #5a8a7a 100%);
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(90, 138, 122, 0.3);
  position: relative;
  overflow: hidden;
}

.complete-btn::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 0;
  height: 0;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.3);
  transform: translate(-50%, -50%);
  transition: width 0.6s, height 0.6s;
}

.complete-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(90, 138, 122, 0.4);
}

.complete-btn:hover::before {
  width: 300px;
  height: 300px;
}

.complete-btn:active {
  transform: translateY(0);
}

/* Calendar Legend */
.calendar-legend {
  margin-top: 1.5rem;
  padding: 1rem 1.5rem;
  background: var(--surface);
  border: 1px solid rgba(170, 196, 188, 0.2);
  border-radius: 10px;
}

.legend-title {
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 0.75rem 0;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.legend-items {
  display: flex;
  gap: 1.5rem;
  flex-wrap: wrap;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.legend-color {
  width: 24px;
  height: 24px;
  border-radius: 6px;
  border: 2px solid rgba(90, 138, 122, 0.3);
}

.legend-green {
  background: rgba(74, 222, 128, 0.4);
}

.legend-blue {
  background: rgba(96, 165, 250, 0.4);
}

.legend-yellow {
  background: rgba(251, 191, 36, 0.4);
}

.legend-red {
  background: rgba(248, 113, 113, 0.4);
}

.legend-label {
  font-size: 0.85rem;
  color: var(--text-muted);
  font-weight: 500;
}
</style>