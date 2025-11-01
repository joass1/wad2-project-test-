<template>
  <v-container class="dashboard-container py-4 py-md-8">
    <h1 class="text-h6 text-md-h5 text-primary font-weight-bold mb-1 px-2 px-md-0">
      <template v-if="loading">Loading...</template>
      <template v-else
        >Welcome back, {{ userProfile?.full_name || "User" }}!</template
      >
    </h1>
    <p class="text-body-2 text-muted mb-4 px-2 px-md-0">
      Here's your wellness dashboard for today
    </p>

    <!-- Buddy container with gradient -->
    <v-card
      class="mb-4 mb-md-6 rounded-xl mx-2 mx-md-0"
      elevation="0"
      variant="outlined"
      :style="gradient"
    >
      <v-card-text class="py-4 py-md-6 px-4 px-md-6">
        <div class="d-flex align-center justify-space-between">
          <div class="d-flex align-center ga-3">
            <div style="font-size: 24px" class="pet-emoji">😊</div>
            <div>
              <div class="text-subtitle-2 text-md-subtitle-1 font-weight-semibold">{{ displayPetName }}</div>
              <div class="text-caption text-md-body-2 text-muted">Doing well</div>
            </div>
          </div>
          <v-chip color="primary" variant="tonal" size="small" class="level-chip">Level 1</v-chip>
        </div>

        <!-- Progress Bars -->
        <div class="mt-4 mt-md-5">
          <div class="d-flex align-center justify-space-between mb-1">
            <div class="text-caption text-md-body-2">Health</div>
            <div class="text-caption text-md-body-2">80%</div>
          </div>
          <v-progress-linear
            model-value="80"
            :height="$vuetify.display.mobile ? 6 : 8"
            rounded
            color="primary"
            class="progress-bar"
          />

          <div class="d-flex align-center justify-space-between mt-3 mt-md-4 mb-1">
            <div class="text-caption text-md-body-2">Happiness</div>
            <div class="text-caption text-md-body-2">70%</div>
          </div>
          <v-progress-linear
            model-value="70"
            :height="$vuetify.display.mobile ? 6 : 8"
            rounded
            color="primary"
            class="progress-bar"
          />
        </div>

        <div class="mt-4 d-flex justify-end">
          <v-btn
            color="primary"
            class="text-white feed-btn"
            prepend-icon="mdi-heart-outline"
            size="small"
            size-md="default"
            @click="navigateToPetPage"
          >
            Feed Pet
          </v-btn>
        </div>
      </v-card-text>
    </v-card>

    <!-- Your Stats Section -->
    <v-row dense class="mb-4 px-2 px-md-0">
      <v-col cols="12" sm="6" md="3">
        <v-card class="rounded-xl stat-card" elevation="0" variant="outlined">
          <v-card-text class="text-center py-4 py-md-6">
            <v-icon
              icon="mdi-clock-time-four-outline"
              size="24"
              size-md="26"
              class="mb-2 text-primary"
            />
            <div class="text-caption text-md-subtitle-2">Study Time Today</div>
            <div class="text-h6 text-md-h6 font-weight-bold mt-1">{{ studyTimeFormatted }}</div>
            <div class="text-caption text-disabled">{{ sessionsCompletedToday }} sessions completed</div>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" sm="6" md="3">
        <v-card class="rounded-xl stat-card" elevation="0" variant="outlined">
          <v-card-text class="text-center py-4 py-md-6">
            <v-icon icon="mdi-target" size="24" size-md="26" class="mb-2 text-primary" />
            <div class="text-caption text-md-subtitle-2">Task Completion</div>
            <div class="text-h6 text-md-h6 font-weight-bold mt-1">{{ taskCompletionPct }}%</div>
            <div class="text-caption text-disabled">{{ tasksCompleted }} of {{ tasksTotal }} tasks done</div>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" sm="6" md="3">
        <v-card class="rounded-xl stat-card" elevation="0" variant="outlined">
          <v-card-text class="text-center py-4 py-md-6">
            <v-icon icon="mdi-fire" size="24" size-md="26" class="mb-2 text-primary" />
            <div class="text-caption text-md-subtitle-2">Study Streak</div>
            <div class="text-h6 text-md-h6 font-weight-bold mt-1">{{ wellnessStreak }} days</div>
            <div class="text-caption text-disabled">Keep it up 🔥</div>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" sm="6" md="3">
        <v-card class="rounded-xl stat-card" elevation="0" variant="outlined">
          <v-card-text class="text-center py-4 py-md-6">
            <v-icon
              icon="mdi-heart-outline"
              size="24"
              size-md="26"
              class="mb-2 text-primary"
            />
            <div class="text-caption text-md-subtitle-2">Wellness Check</div>
            <div class="text-h6 text-md-h6 font-weight-bold mt-1">{{ wellnessDoneToday ? '✅ Done' : '—' }}</div>
            <div class="text-caption text-disabled">{{ wellnessDoneToday ? 'Checked in today' : 'Not yet' }}</div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Google Calendar Integration -->
    <v-row dense class="px-2 px-md-0">
      <v-col cols="12">
        <v-card class="rounded-xl mb-2" elevation="0" variant="outlined">
      <v-card-title class="pb-0 text-subtitle-1 text-md-h6 text-primary">Google Calendar</v-card-title>
      <v-card-subtitle class="pt-0 pb-0 text-caption text-md-body-2"
        >View your upcoming events</v-card-subtitle
      >
      <v-card-text v-if="!calendarConnected" class="py-2 py-md-3 text-center">
        <v-btn
          color="primary"
          variant="outlined"
          @click="connectGoogleCalendar"
          :loading="connectingCalendar"
        >
          Connect Google Calendar
        </v-btn>
        <p class="text-caption text-muted mt-1">
          Securely sync your calendar events
        </p>
      </v-card-text>
      <v-card-text v-else class="py-2 py-md-3">
        <div v-if="calendarEvents.length === 0" class="text-center text-muted">
          No upcoming events
        </div>
        <v-list v-else lines="two" density="compact">
          <v-list-item
            v-for="event in calendarEvents.slice(0, 5)"
            :key="event.id"
            :title="event.summary"
            :subtitle="formatEventTime(event.start, event.end)"
          >
            <template #prepend>
              <v-icon icon="mdi-calendar" color="primary" />
            </template>
          </v-list-item>
        </v-list>
        <div class="mt-1 d-flex justify-space-between align-center">
          <v-btn
            color="error"
            variant="text"
            size="small"
            @click="disconnectGoogleCalendar"
            :loading="disconnectingCalendar"
          >
            Disconnect
          </v-btn>
          <v-btn
            color="primary"
            variant="text"
            size="small"
            @click="loadCalendarEvents"
            :loading="loadingCalendar"
          >
            Refresh
          </v-btn>
        </div>
      </v-card-text>
    </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { useAuth } from "@/composables/useAuth";
import { useGlobalPet } from "@/composables/useGlobalPet";
import { useRouter } from "vue-router";
import { api } from "@/lib/api";

const { userProfile, loading } = useAuth();
const { petName, selectedPet } = useGlobalPet();
const router = useRouter();

const navigateToPetPage = () => {
  router.push({ name: 'PetPage' });
};

const displayPetName = computed(() => {
  return petName.value || selectedPet.value?.label || "Buddy";
});

const gradient = computed(() => ({
  background:
    "linear-gradient(135deg, rgba(170,196,188,.25), rgba(215,203,178,.15))",
  border: "1px solid var(--opal)",
}));

// Dashboard data
const totalMinutesToday = ref(0)
const sessionsCompletedToday = ref(0)
const tasksTotal = ref(0)
const tasksCompleted = ref(0)
const wellnessStreak = ref(0)
const wellnessDoneToday = ref(false)

// Google Calendar data
const calendarConnected = ref(false)
const calendarEvents = ref([])
const connectingCalendar = ref(false)
const disconnectingCalendar = ref(false)
const loadingCalendar = ref(false)

const studyTimeFormatted = computed(() => {
  const h = Math.floor(totalMinutesToday.value / 60)
  const m = totalMinutesToday.value % 60
  if (h <= 0) return `${m}m`
  return `${h}h ${String(m).padStart(2, '0')}m`
})

const taskCompletionPct = computed(() => {
  if (tasksTotal.value === 0) return 0
  return Math.round((tasksCompleted.value / tasksTotal.value) * 100)
})

async function loadDashboardData() {
  try {
    // Study: today's total minutes and sessions
    const today = await api.get('/api/study-sessions/today-summary')
    totalMinutesToday.value = today.total_minutes || 0
    sessionsCompletedToday.value = today.sessions_completed || 0

    // Tasks: totals
    const stats = await api.get('/api/tasks/stats')
    tasksTotal.value = stats.total || 0
    tasksCompleted.value = stats.completed || 0

    // Wellness: streak and today status
    const wellness = await api.get('/api/wellness/overview')
    wellnessStreak.value = wellness.streak || 0

    // Robust today check: query month check-ins and look for today's date
    const now = new Date()
    const yyyy = now.getFullYear()
    const mm = String(now.getMonth() + 1).padStart(2, '0')
    const todayStr = `${yyyy}-${mm}-${String(now.getDate()).padStart(2,'0')}`
    try {
      const monthData = await api.get(`/api/wellness/checkins?month=${mm}&year=${yyyy}`)
      const dates = monthData?.checkInDates || []
      wellnessDoneToday.value = dates.includes(todayStr)
    } catch (e) {
      // Fallback to overview field if monthly query fails
      wellnessDoneToday.value = (wellness.lastCheckInDate === todayStr)
    }

    // Check calendar connection status
    await checkCalendarStatus()
  } catch (e) {
    console.error('Failed to load dashboard data:', e)
  }
}

// Note: Calendar connection success is now handled via popup detection

async function checkCalendarStatus() {
  try {
    console.log('Checking calendar connection status...')
    const status = await api.get('/api/google/oauth/calendar/status')
    console.log('Calendar status response:', status)
    calendarConnected.value = status.connected || false
    console.log('Calendar connected:', calendarConnected.value)
    if (calendarConnected.value) {
      await loadCalendarEvents()
    }
  } catch (e) {
    console.error('Failed to check calendar status:', e)
    calendarConnected.value = false
  }
}

async function connectGoogleCalendar() {
  connectingCalendar.value = true
  try {
    const response = await api.get('/api/google/oauth/start')

    // Open OAuth flow in a popup window
    const popup = window.open(
      response.authorizeUrl,
      'google-calendar-oauth',
      'width=500,height=600,scrollbars=yes,resizable=yes,status=yes,location=yes,toolbar=no,menubar=no'
    )

    if (!popup) {
      throw new Error('Popup blocked. Please allow popups for this site.')
    }

    // Poll for popup completion
    const checkPopup = setInterval(() => {
      try {
        // Check if popup is closed
        if (popup.closed) {
          clearInterval(checkPopup)
          // Refresh calendar status after popup closes
          setTimeout(() => {
            checkCalendarStatus()
          }, 1000)
          return
        }

        // Check if popup navigated to our dashboard (success)
        if (popup.location.href.includes('/dashboard')) {
          clearInterval(checkPopup)
          popup.close()
          // Refresh calendar status
          setTimeout(() => {
            checkCalendarStatus()
          }, 500)
        }
      } catch (e) {
        // Cross-origin error, popup is still on Google domain
      }
    }, 1000)

  } catch (e) {
    console.error('Failed to start calendar connection:', e)
    // Fallback to new tab if popup fails
    if (e.message.includes('Popup blocked')) {
      alert('Popup was blocked. Please allow popups and try again.')
    }
  } finally {
    connectingCalendar.value = false
  }
}

async function disconnectGoogleCalendar() {
  disconnectingCalendar.value = true
  try {
    await api.del('/api/google/oauth/disconnect')
    calendarConnected.value = false
    calendarEvents.value = []
  } catch (e) {
    console.error('Failed to disconnect calendar:', e)
  } finally {
    disconnectingCalendar.value = false
  }
}

async function loadCalendarEvents() {
  loadingCalendar.value = true
  try {
    const now = new Date()
    const timeMin = now.toISOString()
    const timeMax = new Date(now.getTime() + 7 * 24 * 60 * 60 * 1000).toISOString() // Next 7 days

    console.log('Fetching calendar events:', { timeMin, timeMax })

    const response = await api.get('/api/google/oauth/calendar/events', {
      params: {
        timeMin,
        timeMax,
        maxResults: 10
      }
    })

    console.log('Calendar API response:', response)
    calendarEvents.value = response.items || []
    console.log('Parsed events:', calendarEvents.value)
  } catch (e) {
    console.error('Failed to load calendar events:', e)
    calendarEvents.value = []
  } finally {
    loadingCalendar.value = false
  }
}

function formatEventTime(start, end) {
  const startDate = new Date(start.dateTime || start.date)
  const endDate = new Date(end.dateTime || end.date)

  const options = { weekday: 'short', month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit' }
  const startStr = startDate.toLocaleDateString('en-US', options)

  if (start.dateTime && end.dateTime) {
    const endStr = endDate.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' })
    return `${startStr} - ${endStr}`
  } else {
    return startStr
  }
}

onMounted(() => {
  loadDashboardData()
})
</script>



<style scoped>
.dashboard-container {
  max-width: 100%;
}

.text-muted {
  color: var(--text-muted);
}

/* Mobile responsive adjustments */
@media (max-width: 960px) {
  .dashboard-container {
    padding-left: 8px;
    padding-right: 8px;
  }
  
  .pet-emoji {
    font-size: 24px !important;
  }
  
  .level-chip {
    font-size: 11px !important;
    height: 22px !important;
  }
  
  .progress-bar {
    margin-top: 4px;
  }
  
  .feed-btn {
    font-size: 12px !important;
    height: 36px !important;
  }
  
  .stat-card {
    margin-bottom: 12px;
  }
}

/* Very small screens */
@media (max-width: 600px) {
  .dashboard-container {
    padding-left: 4px;
    padding-right: 4px;
  }
}

/* Ensure cards have proper spacing on mobile */
@media (max-width: 960px) {
  :deep(.v-row) {
    margin-left: -4px;
    margin-right: -4px;
  }
  
  :deep(.v-col) {
    padding-left: 4px;
    padding-right: 4px;
  }
}
</style>
