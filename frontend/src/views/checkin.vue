<template>
  <div class="check-in-page">
    <div class="header">
      <h1>Wellness Check-in</h1>
      <p class="subtitle">Track your wellness and mood</p>
    </div>

    <div class="main-content">
      <div class="wellness-overview">
        <h3 class="section-title">
          <span class="icon">📊</span> Wellness Overview
        </h3>
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
          <h3>Already Checked In Today!</h3>
          <p>You've completed your wellness check-in for {{ todayFormatted }}.</p>
          <p class="next-checkin-text">Come back tomorrow for your next check-in!</p>
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
            <input 
              type="range" 
              v-model.number="mood" 
              min="0" 
              max="10" 
              class="slider"
            />
            <p class="slider-feedback">{{ getMoodFeedback }}</p>
          </div>

           Energy Slider 
          <div class="slider-group">
            <div class="slider-header">
              <span class="slider-label">
                <span class="emoji">⚡</span> Energy
              </span>
              <span class="slider-value">{{ energy }}/10</span>
            </div>
            <input 
              type="range" 
              v-model.number="energy" 
              min="0" 
              max="10" 
              class="slider"
            />
            <p class="slider-feedback">{{ getEnergyFeedback }}</p>
          </div>

           Sleep Slider 
          <div class="slider-group">
            <div class="slider-header">
              <span class="slider-label">
                <span class="emoji">😴</span> Sleep
              </span>
              <span class="slider-value">{{ sleep }}/10</span>
            </div>
            <input 
              type="range" 
              v-model.number="sleep" 
              min="0" 
              max="10" 
              class="slider"
            />
            <p class="slider-feedback">{{ getSleepFeedback }}</p>
          </div>

           Stress Slider 
          <div class="slider-group">
            <div class="slider-header">
              <span class="slider-label">
                <span class="emoji">😰</span> Stress
              </span>
              <span class="slider-value">{{ stress }}/10</span>
            </div>
            <input 
              type="range" 
              v-model.number="stress" 
              min="0" 
              max="10" 
              class="slider"
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
          <h3>Check-in Complete!</h3>
          <p>Great job tracking your wellness today.</p>
          <p class="next-checkin-text">See you tomorrow!</p>
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
            >
                {{ date.day }}
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
import { ref, computed, onMounted} from 'vue'
import { getFirestore, collection, addDoc, query, where, getDocs, orderBy } from 'firebase/firestore'
import { getAuth } from 'firebase/auth'

// Initialize Firebase instances 
const db = getFirestore()
const auth = getAuth()

// State
const mood = ref(7)
const energy = ref(7)
const sleep = ref(7)
const stress = ref(3)
const notes = ref('')
const isCompleted = ref(false)
const streak = ref(0)
const totalCheckIns = ref(0)
const isSubmitting = ref(false)
const hasCheckedInToday = ref(false)
const checkInHistory = ref({})

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

  const today = new Date()
  today.setHours(0, 0, 0, 0)
  const tomorrow = new Date(today)
  tomorrow.setDate(tomorrow.getDate() + 1)

  try {
    const q = query(
      collection(db, 'wellnessCheckIns'),
      where('userId', '==', user.uid),
      where('date', '>=', today),
      where('date', '<', tomorrow)
    )
    
    const querySnapshot = await getDocs(q)
    hasCheckedInToday.value = !querySnapshot.empty
  } catch (error) {
    console.error('Error checking today\'s check-in:', error)
  }
}

// Load all check-ins for the user
const loadCheckIns = async () => {
  const user = auth.currentUser
  if (!user) return

  try {
    const q = query(
      collection(db, 'wellnessCheckIns'),
      where('userId', '==', user.uid),
      orderBy('date', 'desc')
    )
    
    const querySnapshot = await getDocs(q)
    const history = {}
    
    querySnapshot.forEach((doc) => {
      const data = doc.data()
      const dateStr = getDateString(data.date.toDate())
      history[dateStr] = {
        mood: data.mood,
        energy: data.energy,
        sleep: data.sleep,
        stress: data.stress,
        notes: data.notes || ''
      }
    })
    
    checkInHistory.value = history
    totalCheckIns.value = querySnapshot.size
    calculateStreak()
  } catch (error) {
    console.error('Error loading check-ins:', error)
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
  const key = selectedDate.value.toISOString().split('T')[0]
  return checkInHistory.value[key] || null
})

const selectedDateFormatted = computed(() => {
  return selectedDate.value.toLocaleDateString('en-US', { 
    month: 'long', 
    day: 'numeric',
    year: 'numeric'
  })
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
        key: `prev-${prevLastDate - i}`
    })
  }
  
  // Current month dates
  const today = new Date()
  for (let i = 1; i <= lastDate; i++) {
    const isToday = i === today.getDate() && 
                    month === today.getMonth() && 
                    year === today.getFullYear()
    
    dates.push({
        day: i,
        isOtherMonth: false,
        isToday,
        isSelected: i === selectedDate.value.getDate() && 
                    month === selectedDate.value.getMonth() &&
                    year === selectedDate.value.getFullYear(),
        // Check if there's a check-in for that specific date 
        hasCheckIn: checkInHistory.value[`${year}-${String(month + 1).padStart(2, '0')}-${String(i).padStart(2, '0')}`] !== undefined,
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
    const checkInData = {
      userId: user.uid,
      date: new Date(),
      mood: mood.value,
      energy: energy.value,
      sleep: sleep.value,
      stress: stress.value,
      notes: notes.value,
      createdAt: new Date()
    }

    await addDoc(collection(db, 'wellnessCheckIns'), checkInData)
    
    isCompleted.value = true
    hasCheckedInToday.value = true
    
    // Reload data
    await loadCheckIns()
  } catch (error) {
    console.error('Error saving check-in:', error)
    alert('Failed to save check-in. Please try again.')
  } finally {
    isSubmitting.value = false
  }
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

// Load data when component mounts 
onMounted(async () => {
  await checkTodayCheckIn()
  await loadCheckIns()
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
  height: 6px;
  border-radius: 3px;
  background: linear-gradient(to right, #e5e5e5 0%, #5a8a7a 100%);
  outline: none;
  -webkit-appearance: none;
  margin-bottom: 0.5rem;
}

.slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: var(--primary);
  cursor: pointer;
  border: 2px solid white;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.slider::-moz-range-thumb {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: var(--primary);
  cursor: pointer;
  border: 2px solid white;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
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
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.2s;
}

.calendar-date:hover {
  background: #f5f5f5;
}

.calendar-date.other-month {
  color: #ccc;
}

.calendar-date.today {
  background: #1a1a1a;
  color: white;
  font-weight: 600;
}

.calendar-date.selected {
  background: var(--primary);
  color: white;
}

.calendar-date.has-checkin {
  position: relative;
}

.calendar-date.has-checkin::after {
  content: '';
  position: absolute;
  bottom: 4px;
  width: 4px;
  height: 4px;
  background: var(--primary);
  border-radius: 50%;
}

.calendar-date.has-checkin.today::after {
  background: var(--surface);
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
</style>