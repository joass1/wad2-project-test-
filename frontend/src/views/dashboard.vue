<template>
  <v-container class="dashboard-container py-4 py-md-8">
    <h1
      class="text-h6 text-md-h5 text-primary font-weight-bold mb-1 px-2 px-md-0"
    >
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
      :style="gradient"
    >
      <v-card-text class="py-4 py-md-6 px-4 px-md-6">
        <div class="d-flex align-center justify-space-between">
          <div class="d-flex align-center ga-3">
            <div style="font-size: 24px" class="pet-emoji">😊</div>
            <div>
              <div
                class="text-subtitle-2 text-md-subtitle-1 font-weight-semibold"
              >
                {{ displayPetName }}
              </div>
              <div class="text-caption text-md-body-2 text-muted">
                <span v-if="isPetDead" style="color: var(--error)"
                  >Has died</span
                >
                <span
                  v-else-if="petHappiness < 20 || petHealth < 20"
                  style="color: var(--warning)"
                  >Starving</span
                >
                <span
                  v-else-if="petHappiness < 40 || petHealth < 40"
                  style="color: var(--warning)"
                  >Getting hungry</span
                >
                <span v-else>Doing well</span>
              </div>
            </div>
          </div>
          <v-chip
            color="primary"
            variant="tonal"
            size="small"
            class="level-chip"
            >Level 1</v-chip
          >
        </div>

        <!-- Progress Bars -->
        <div class="mt-4 mt-md-5">
          <div v-if="isPetDead" class="pet-dead-message mb-3">
            <div
              class="text-caption text-md-body-2 text-center"
              style="color: var(--error)"
            >
              Your pet has died! Feed it to revive it.
            </div>
          </div>
          <div class="status-item">
            <span class="status-label">Happy</span>
            <div class="status-bar">
              <div
                class="status-fill"
                :style="{ width: `${petHappiness}%` }"
              ></div>
            </div>
            <span class="status-value">{{ petHappiness }}%</span>
          </div>
          <div class="status-item" style="margin-bottom: 0">
            <span class="status-label">Health</span>
            <div class="status-bar">
              <div
                class="status-fill health"
                :style="{ width: `${petHealth}%` }"
              ></div>
            </div>
            <span class="status-value">{{ petHealth }}%</span>
          </div>
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
        <v-card class="rounded-xl stat-card" elevation="0">
          <v-card-text class="text-center py-4 py-md-6">
            <v-icon
              icon="mdi-clock-time-four-outline"
              size="24"
              size-md="26"
              class="mb-2 text-primary"
            />
            <div class="text-caption text-md-subtitle-2">Study Time Today</div>
            <div class="text-h6 text-md-h6 font-weight-bold mt-1">
              {{ studyTimeFormatted }}
            </div>
            <div class="text-caption text-disabled">
              {{ sessionsCompletedToday }} sessions completed
            </div>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" sm="6" md="3">
        <v-card class="rounded-xl stat-card" elevation="0">
          <v-card-text class="text-center py-4 py-md-6">
            <v-icon
              icon="mdi-target"
              size="24"
              size-md="26"
              class="mb-2 text-primary"
            />
            <div class="text-caption text-md-subtitle-2">Task Completion</div>
            <div class="text-h6 text-md-h6 font-weight-bold mt-1">
              {{ taskCompletionPct }}%
            </div>
            <div class="text-caption text-disabled">
              {{ tasksCompleted }} of {{ tasksTotal }} tasks done
            </div>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" sm="6" md="3">
        <v-card class="rounded-xl stat-card" elevation="0">
          <v-card-text class="text-center py-4 py-md-6">
            <v-icon
              icon="mdi-fire"
              size="24"
              size-md="26"
              class="mb-2 text-primary"
            />
            <div class="text-caption text-md-subtitle-2">Study Streak</div>
            <div class="text-h6 text-md-h6 font-weight-bold mt-1">
              {{ wellnessStreak }} days
            </div>
            <div class="text-caption text-disabled">Keep it up 🔥</div>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" sm="6" md="3">
        <v-card class="rounded-xl stat-card" elevation="0">
          <v-card-text class="text-center py-4 py-md-6">
            <v-icon
              icon="mdi-heart-outline"
              size="24"
              size-md="26"
              class="mb-2 text-primary"
            />
            <div class="text-caption text-md-subtitle-2">Wellness Check</div>
            <div class="text-h6 text-md-h6 font-weight-bold mt-1">
              {{ wellnessDoneToday ? "✅ Done" : "—" }}
            </div>
            <div class="text-caption text-disabled">
              {{ wellnessDoneToday ? "Checked in today" : "Not yet" }}
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Google Calendar Integration -->
    <v-row dense class="px-2 px-md-0">
      <v-col cols="12">
        <v-card class="rounded-xl mb-2" elevation="0">
          <v-card-title class="pb-0 text-subtitle-1 text-md-h6 text-primary"
            >Google Calendar</v-card-title
          >
          <v-card-subtitle class="pt-0 pb-0 text-caption text-md-body-2"
            >View your upcoming events</v-card-subtitle
          >
          <v-card-text
            v-if="!calendarConnected"
            class="py-2 py-md-3 text-center"
          >
            <v-btn
              color="primary"
              @click="connectGoogleCalendar"
              :loading="connectingCalendar"
            >
              Connect Google Calendar
            </v-btn>
            <p class="text-caption text-muted mt-1">
              Securely sync your calendar events
            </p>
          </v-card-text>
          <v-card-text v-else class="py-2 py-md-3 pa-0">
            <div
              v-if="calendarEvents.length === 0"
              class="text-center text-muted py-8"
            >
              No upcoming events this week
            </div>
            <div v-else class="calendar-week-view">
              <div class="calendar-scroll-container">
                <!-- Calendar Header -->
                <div class="calendar-header">
                  <div class="timezone-label">{{ timezoneLabel }}</div>
                  <div class="days-header">
                    <div
                      v-for="day in weekDays"
                      :key="day.key"
                      :class="['day-header', { 'current-day': day.isToday }]"
                    >
                      <div class="day-name">{{ day.name }}</div>
                      <div
                        class="day-number"
                        :class="{ highlighted: day.isToday }"
                      >
                        {{ day.date }}
                      </div>
                      <div
                        v-if="day.pendingTasks > 0"
                        class="pending-tasks-banner"
                      >
                        <v-icon icon="mdi-check-circle" size="12" />
                        {{ day.pendingTasks }} pending task{{
                          day.pendingTasks > 1 ? "s" : ""
                        }}
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Calendar Grid -->
                <div
                  ref="calendarGridContainer"
                  class="calendar-grid-container"
                >
                  <!-- Time Axis -->
                  <div class="time-axis">
                    <div
                      v-for="hour in timeSlots"
                      :key="hour"
                      class="time-slot"
                    >
                      {{ formatHour(hour) }}
                    </div>
                  </div>

                  <!-- Days Grid -->
                  <div class="days-grid">
                    <div
                      v-for="day in weekDays"
                      :key="day.key"
                      class="day-column"
                      :class="{ 'current-day-column': day.isToday }"
                    >
                      <div
                        v-for="hour in timeSlots"
                        :key="hour"
                        class="time-cell"
                      ></div>
                      <!-- Current time indicator line (only for today) -->
                      <div
                        v-if="day.isToday"
                        class="current-time-line"
                        :style="currentTimeLineStyle"
                      >
                        <div class="current-time-dot"></div>
                      </div>
                      <!-- Events for this day -->
                      <div
                        v-for="event in day.events"
                        :key="event.id"
                        class="calendar-event"
                        :style="getEventStyle(event)"
                        :title="`${event.summary} - ${formatEventTime(
                          event.start,
                          event.end
                        )}`"
                      >
                        <div class="event-dot"></div>
                        <div class="event-content">
                          <div class="event-title">{{ event.summary }}</div>
                          <div v-if="event.start.dateTime" class="event-time">
                            {{ formatEventTimeShort(event.start, event.end) }}
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <div class="mt-2 d-flex justify-space-between align-center px-2">
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
import { computed, nextTick, onMounted, ref, watch } from "vue";
import { useRouter } from "vue-router";
import { useDisplay } from "vuetify";
import { useAuth } from "@/composables/useAuth";
import { useGlobalPet } from "@/composables/useGlobalPet";
import { api } from "@/lib/api";

const { userProfile, loading } = useAuth();
const { petName, selectedPet, petStatus } = useGlobalPet();
const router = useRouter();
const { mobile } = useDisplay();

// Computed values for pet status, clamped to 0-100
const petHappiness = computed(() => {
  const value = petStatus.value?.happiness ?? 70;
  return Math.max(0, Math.min(100, value));
});

const petHealth = computed(() => {
  const value = petStatus.value?.health ?? 80;
  return Math.max(0, Math.min(100, value));
});

const isPetDead = computed(() => {
  return (
    petStatus.value?.isDead ||
    petStatus.value?.is_dead ||
    petHappiness.value === 0 ||
    petHealth.value === 0
  );
});

const navigateToPetPage = () => {
  router.push({ name: "PetPage" });
};

const displayPetName = computed(() => {
  return petName.value || selectedPet.value?.label || "Buddy";
});

const gradient = computed(() => ({
  background:
    "linear-gradient(135deg, rgba(170,196,188,.25), rgba(215,203,178,.15))",
}));

// Dashboard data
const totalMinutesToday = ref(0);
const sessionsCompletedToday = ref(0);
const tasksTotal = ref(0);
const tasksCompleted = ref(0);
const wellnessStreak = ref(0);
const wellnessDoneToday = ref(false);

// Google Calendar data
const calendarConnected = ref(false);
const calendarEvents = ref([]);
const connectingCalendar = ref(false);
const disconnectingCalendar = ref(false);
const loadingCalendar = ref(false);
const calendarGridContainer = ref(null);

const studyTimeFormatted = computed(() => {
  const h = Math.floor(totalMinutesToday.value / 60);
  const m = totalMinutesToday.value % 60;
  if (h <= 0) return `${m}m`;
  return `${h}h ${String(m).padStart(2, "0")}m`;
});

const taskCompletionPct = computed(() => {
  if (tasksTotal.value === 0) return 0;
  return Math.round((tasksCompleted.value / tasksTotal.value) * 100);
});

async function loadDashboardData() {
  try {
    // Study: today's total minutes and sessions
    const today = await api.get("/api/study-sessions/today-summary");
    totalMinutesToday.value = today.total_minutes || 0;
    sessionsCompletedToday.value = today.sessions_completed || 0;

    // Tasks: totals
    const stats = await api.get("/api/tasks/stats");
    tasksTotal.value = stats.total || 0;
    tasksCompleted.value = stats.completed || 0;

    // Wellness: streak and today status
    const wellness = await api.get("/api/wellness/overview");
    wellnessStreak.value = wellness.streak || 0;

    // Robust today check: query month check-ins and look for today's date
    const now = new Date();
    const yyyy = now.getFullYear();
    const mm = String(now.getMonth() + 1).padStart(2, "0");
    const todayStr = `${yyyy}-${mm}-${String(now.getDate()).padStart(2, "0")}`;
    try {
      const monthData = await api.get(
        `/api/wellness/checkins?month=${mm}&year=${yyyy}`
      );
      const dates = monthData?.checkInDates || [];
      wellnessDoneToday.value = dates.includes(todayStr);
    } catch (e) {
      // Fallback to overview field if monthly query fails
      wellnessDoneToday.value = wellness.lastCheckInDate === todayStr;
    }

    // Check calendar connection status
    await checkCalendarStatus();
  } catch (e) {
    console.error("Failed to load dashboard data:", e);
  }
}

// Note: Calendar connection success is now handled via popup detection

async function checkCalendarStatus() {
  try {
    console.log("Checking calendar connection status...");
    const status = await api.get("/api/google/oauth/calendar/status");
    console.log("Calendar status response:", status);
    calendarConnected.value = status.connected || false;
    console.log("Calendar connected:", calendarConnected.value);
    if (calendarConnected.value) {
      await loadCalendarEvents();
    }
  } catch (e) {
    console.error("Failed to check calendar status:", e);
    calendarConnected.value = false;
  }
}

async function connectGoogleCalendar() {
  connectingCalendar.value = true;
  try {
    const response = await api.get("/api/google/oauth/start");

    // Open OAuth flow in a popup window
    const popup = window.open(
      response.authorizeUrl,
      "google-calendar-oauth",
      "width=500,height=600,scrollbars=yes,resizable=yes,status=yes,location=yes,toolbar=no,menubar=no"
    );

    if (!popup) {
      throw new Error("Popup blocked. Please allow popups for this site.");
    }

    // Poll for popup completion
    const checkPopup = setInterval(() => {
      try {
        // Check if popup is closed
        if (popup.closed) {
          clearInterval(checkPopup);
          // Refresh calendar status after popup closes
          setTimeout(() => {
            checkCalendarStatus();
          }, 1000);
          return;
        }

        // Check if popup navigated to our dashboard (success)
        if (popup.location.href.includes("/dashboard")) {
          clearInterval(checkPopup);
          popup.close();
          // Refresh calendar status
          setTimeout(() => {
            checkCalendarStatus();
          }, 500);
        }
      } catch (e) {
        // Cross-origin error, popup is still on Google domain
      }
    }, 1000);
  } catch (e) {
    console.error("Failed to start calendar connection:", e);
    // Fallback to new tab if popup fails
    if (e.message.includes("Popup blocked")) {
      alert("Popup was blocked. Please allow popups and try again.");
    }
  } finally {
    connectingCalendar.value = false;
  }
}

async function disconnectGoogleCalendar() {
  disconnectingCalendar.value = true;
  try {
    await api.del("/api/google/oauth/disconnect");
    calendarConnected.value = false;
    calendarEvents.value = [];
  } catch (e) {
    console.error("Failed to disconnect calendar:", e);
  } finally {
    disconnectingCalendar.value = false;
  }
}

async function loadCalendarEvents() {
  loadingCalendar.value = true;
  try {
    const now = new Date();
    // fetch events similar to google calendar (sun to sat of current week)
    const dayOfWeek = now.getDay(); // 0 = sunday

    // get start of this week (Sunday 00:00)
    const startOfWeek = new Date(now);
    startOfWeek.setTime(now.getTime() - dayOfWeek * 24 * 60 * 60 * 1000);
    startOfWeek.setHours(0, 0, 0, 0);
    const timeMin = startOfWeek.toISOString();

    // get end of this week (Saturday 23:59)
    const endOfWeek = new Date(startOfWeek);
    endOfWeek.setTime(startOfWeek.getTime() + 6 * 24 * 60 * 60 * 1000);
    endOfWeek.setHours(23, 59, 59, 999);
    const timeMax = endOfWeek.toISOString();

    // console.log("Fetching calendar events:", { timeMin, timeMax });

    const response = await api.get("/api/google/oauth/calendar/events", {
      params: {
        timeMin,
        timeMax,
        // maxResults: ,
      },
    });

    // console.log("Calendar API response:", response);
    calendarEvents.value = response.items || [];
    // console.log("Parsed events:", calendarEvents.value);
  } catch (e) {
    console.error("Failed to load calendar events:", e);
    calendarEvents.value = [];
  } finally {
    loadingCalendar.value = false;
  }
}

function formatEventTime(start, end) {
  const startDate = new Date(start.dateTime || start.date);
  const endDate = new Date(end.dateTime || end.date);

  const options = {
    weekday: "short",
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  };
  const startStr = startDate.toLocaleDateString("en-US", options);

  if (start.dateTime && end.dateTime) {
    const endStr = endDate.toLocaleTimeString("en-US", {
      hour: "numeric",
      minute: "2-digit",
    });
    return `${startStr} - ${endStr}`;
  } else {
    return startStr;
  }
}

// Calendar week view computed properties
const timezoneLabel = computed(() => {
  const tz = Intl.DateTimeFormat().resolvedOptions().timeZone;
  const offset = new Date().getTimezoneOffset();
  const sign = offset <= 0 ? "+" : "-";
  const hours = String(Math.floor(Math.abs(offset) / 60)).padStart(2, "0");
  return `GMT${sign}${hours}`;
});

const timeSlots = computed(() => {
  // 12 AM (0) to 11 PM (23) = 24 hours
  const slots = [];
  for (let h = 0; h <= 23; h++) {
    slots.push(h);
  }
  return slots;
});

const weekDays = computed(() => {
  const now = new Date();
  const dayOfWeek = now.getDay(); // 0 = Sunday
  const startOfWeek = new Date(now);
  startOfWeek.setDate(now.getDate() - dayOfWeek);
  startOfWeek.setHours(0, 0, 0, 0);

  const days = [];
  const dayNames = ["SUN", "MON", "TUE", "WED", "THU", "FRI", "SAT"];

  for (let i = 0; i < 7; i++) {
    const date = new Date(startOfWeek);
    date.setDate(startOfWeek.getDate() + i);

    const isToday = date.toDateString() === now.toDateString();
    const dateStr = date.getDate().toString();
    const key = `day-${i}`;

    // Get events for this day
    let dayEvents = calendarEvents.value.filter((event) => {
      const eventStart = new Date(event.start.dateTime || event.start.date);
      return (
        eventStart.getDate() === date.getDate() &&
        eventStart.getMonth() === date.getMonth() &&
        eventStart.getFullYear() === date.getFullYear()
      );
    });

    // Sort events by start time
    dayEvents = dayEvents.sort((a, b) => {
      const aStart = new Date(a.start.dateTime || a.start.date);
      const bStart = new Date(b.start.dateTime || b.start.date);
      return aStart - bStart;
    });

    // Assign overlap positions to events
    // Group events by overlapping time ranges
    const processedEvents = dayEvents.map((event) => {
      const eventStart = new Date(event.start.dateTime || event.start.date);
      const eventEnd = new Date(event.end.dateTime || event.end.date);

      // Find all events that overlap with this event
      const overlappingEvents = dayEvents.filter((otherEvent) => {
        const otherStart = new Date(
          otherEvent.start.dateTime || otherEvent.start.date
        );
        const otherEnd = new Date(
          otherEvent.end.dateTime || otherEvent.end.date
        );

        // Check if events overlap
        return eventStart < otherEnd && eventEnd > otherStart;
      });

      // Find this event's position among overlapping events (sorted by start time)
      overlappingEvents.sort((a, b) => {
        const aStart = new Date(a.start.dateTime || a.start.date);
        const bStart = new Date(b.start.dateTime || b.start.date);
        return aStart - bStart;
      });

      const overlapIndex = overlappingEvents.findIndex(
        (e) => e.id === event.id || e.summary === event.summary
      );

      return {
        ...event,
        _overlapIndex: overlapIndex >= 0 ? overlapIndex : 0,
        _overlapCount: overlappingEvents.length,
      };
    });

    // Count pending tasks (all-day events or tasks without time)
    const pendingTasks = dayEvents.filter(
      (e) => !e.start.dateTime || e.start.date
    ).length;

    days.push({
      key,
      name: dayNames[i],
      date: dateStr,
      fullDate: date,
      isToday,
      events: processedEvents,
      pendingTasks,
    });
  }

  return days;
});

function formatHour(hour) {
  if (hour === 0) return "12 AM";
  if (hour < 12) return `${hour} AM`;
  if (hour === 12) return "12 PM";
  return `${hour - 12} PM`;
}

function formatEventTimeShort(start, end) {
  if (!start.dateTime || !end.dateTime) return "";
  const startDate = new Date(start.dateTime);
  const endDate = new Date(end.dateTime);

  const startTime = startDate.toLocaleTimeString("en-US", {
    hour: "numeric",
    minute: "2-digit",
    hour12: true,
  });
  const endTime = endDate.toLocaleTimeString("en-US", {
    hour: "numeric",
    minute: "2-digit",
    hour12: true,
  });
  return `${startTime} - ${endTime}`;
}

function getEventStyle(event) {
  // For all-day events
  if (!event.start.dateTime || event.start.date) {
    const allDayColor = "rgba(66, 133, 244, 0.1)";
    return {
      top: "0px",
      height: "40px",
      background: `linear-gradient(${allDayColor}, ${allDayColor}), var(--surface)`,
    };
  }

  const startDate = new Date(event.start.dateTime);
  const endDate = new Date(event.end.dateTime);

  // Each hour slot is 60px (matching .time-cell height)
  const hourHeight = 60;
  const startHour = startDate.getHours();
  const startMinutes = startDate.getMinutes();
  const endHour = endDate.getHours();
  const endMinutes = endDate.getMinutes();

  // Calculate top position from 12 AM (hour 0)
  // Events can now start at any hour from 0 to 23
  const topOffset = startHour * hourHeight + (startMinutes / 60) * hourHeight;

  // Calculate height (duration)
  const startTotalMinutes = startHour * 60 + startMinutes;
  const endTotalMinutes = endHour * 60 + endMinutes;
  const durationMinutes = endTotalMinutes - startTotalMinutes;

  // Clamp height if event extends beyond 11:59 PM
  const maxMinutes = 24 * 60; // End of day (midnight next day)
  let adjustedDurationMinutes = durationMinutes;
  if (endTotalMinutes > maxMinutes) {
    adjustedDurationMinutes = maxMinutes - startTotalMinutes;
  }

  const height = Math.max((adjustedDurationMinutes / 60) * hourHeight, 20); // Minimum 20px height

  // Handle overlapping events - position them in a staggered display
  const overlapIndex = event._overlapIndex || 0;
  const overlapCount = event._overlapCount || 1;

  // Base margin for events
  const margin = 4; // px margin on each side

  const timedColor = "rgba(234, 67, 53, 0.1)";
  const style = {
    top: `${topOffset}px`,
    height: `${height}px`,
    background: `linear-gradient(${timedColor}, ${timedColor}), var(--surface)`,
    borderLeft: "3px solid #ea4335",
    zIndex: 2 + overlapIndex,
  };

  // Set positioning based on overlap
  if (mobile.value && overlapCount > 1) {
    // MOBILE: Staggered layout - each overlapping event is offset slightly to the right
    const staggerOffset = 12; // pixels to stagger each event
    const maxStaggerDepth = 5; // Limit stagger depth to prevent events going off-screen
    const staggerIndex = overlapIndex % maxStaggerDepth;

    style.left = `${staggerOffset * staggerIndex + margin}px`;
    style.right = `${margin}px`;
  } else if (overlapCount > 1) {
    // DESKTOP: Side-by-side layout for overlapping events
    const widthPercent = 100 / overlapCount;
    const leftPercent = overlapIndex * widthPercent;
    const gap = 2; // gap between side-by-side events
    const isFirst = overlapIndex === 0;
    const isLast = overlapIndex === overlapCount - 1;

    style.left = `calc(${leftPercent}% + ${isFirst ? margin : gap / 2}px)`;
    style.right = `calc(${100 - leftPercent - widthPercent}% + ${
      isLast ? margin : gap / 2
    }px)`;
  } else {
    // Single event - full width with margins (both mobile and desktop)
    style.left = `${margin}px`;
    style.right = `${margin}px`;
  }

  return style;
}

// Current time for the indicator line (updates every minute)
const currentTime = ref(new Date());

// Update current time every minute to move the indicator line
function startTimeUpdater() {
  setInterval(() => {
    currentTime.value = new Date();
  }, 60000); // Update every minute
}

const currentTimeLineStyle = computed(() => {
  const now = currentTime.value;
  const currentHour = now.getHours();
  const currentMinutes = now.getMinutes();

  // Each hour is 60px, calculate position from 12 AM
  const hourHeight = mobile.value ? 50 : 60;
  const topPosition =
    currentHour * hourHeight + (currentMinutes / 60) * hourHeight;

  return {
    top: `${topPosition}px`,
  };
});

// Scroll calendar to current time
function scrollToCurrentTime() {
  if (!calendarGridContainer.value) return;

  const now = new Date();
  const currentHour = now.getHours();
  const currentMinutes = now.getMinutes();

  // Each hour is 60px, calculate scroll position
  const hourHeight = mobile.value ? 50 : 60;
  const scrollPosition =
    currentHour * hourHeight + (currentMinutes / 60) * hourHeight;

  // Scroll to current time, with some offset to center it slightly
  const offset = 200; // Offset to show some time before current time
  calendarGridContainer.value.scrollTop = Math.max(0, scrollPosition - offset);
}

// Watch for calendar events to load, then scroll to current time
watch(
  calendarEvents,
  () => {
    if (calendarEvents.value.length > 0) {
      nextTick(() => {
        scrollToCurrentTime();
      });
    }
  },
  { deep: true }
);

onMounted(() => {
  loadDashboardData();
  // Start updating current time every minute
  startTimeUpdater();
  // Scroll to current time after a brief delay to ensure DOM is ready
  nextTick(() => {
    setTimeout(() => {
      scrollToCurrentTime();
    }, 300);
  });
});
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
}

/* Status bars matching pet page */
.status-item {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

@media (max-width: 960px) {
  .status-item {
    gap: 8px;
    margin-bottom: 6px;
  }
}

.status-label {
  width: 60px;
  text-transform: capitalize;
  font-size: 13px;
  color: var(--text-primary);
}

@media (max-width: 960px) {
  .status-label {
    width: 50px;
    font-size: 12px;
  }
}

.status-bar {
  flex: 1;
  height: 8px;
  background: var(--surface-lighter);
  border-radius: 4px;
  overflow: hidden;
}

.status-fill {
  height: 100%;
  background: var(--primary);
}

.status-fill.health {
  background: #4ade80;
}

.status-value {
  font-size: 13px;
  color: var(--text-primary);
  min-width: 40px;
  text-align: right;
}

@media (max-width: 960px) {
  .status-value {
    font-size: 12px;
    min-width: 35px;
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

/* Google Calendar Week View Styles */
.calendar-week-view {
  font-family: "Google Sans", -apple-system, BlinkMacSystemFont, sans-serif;
  background: var(--surface);
  border-radius: 8px;
  overflow: hidden;
  color: var(--text-primary);
}

.calendar-header {
  display: flex;
  border-bottom: 1px solid var(--surface-lighter);
  background: var(--surface);
  position: sticky;
  top: 0;
  z-index: 10;
  box-sizing: border-box;
  min-width: fit-content;
  width: 100%;
  overflow-y: scroll;
}

.timezone-label {
  width: 48px;
  padding: 8px 4px;
  font-size: 11px;
  color: var(--text-muted);
  text-align: center;
  border-right: 1px solid var(--surface-lighter);
  flex-shrink: 0;
  box-sizing: border-box;
}

.days-header {
  display: flex;
  flex: 1 1 0;
  min-width: 0;
  box-sizing: border-box;
}

.day-header {
  flex: 1 1 0;
  min-width: 0;
  padding: 8px 4px;
  text-align: center;
  border-right: 1px solid var(--surface-lighter);
  box-sizing: border-box;
}

.day-header:last-child {
  border-right: none;
}

.day-header.current-day {
  background-color: rgba(106, 122, 90, 0.08);
}

[data-theme="dark"] .day-header.current-day {
  background-color: rgba(141, 175, 155, 0.15);
}

.day-name {
  font-size: 11px;
  color: var(--text-muted);
  margin-bottom: 4px;
  font-weight: 500;
}

.day-header.current-day .day-name {
  color: var(--primary);
  font-weight: 600;
}

.day-number {
  font-size: 22px;
  color: var(--text-primary);
  font-weight: 400;
  line-height: 1.2;
}

.day-number.highlighted {
  background-color: var(--primary);
  color: white;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto;
}

.pending-tasks-banner {
  margin-top: 4px;
  background-color: var(--surface-light);
  color: var(--primary);
  padding: 2px 6px;
  border-radius: 12px;
  font-size: 10px;
  display: inline-flex;
  align-items: center;
  gap: 4px;
  white-space: nowrap;
}

.calendar-scroll-container {
  overflow-x: auto;
  max-width: 100%;
}

.calendar-header {
  display: flex;
  position: sticky;
  top: 0;
  background: var(--surface);
  z-index: 10;
  border-bottom: 1px solid var(--surface-lighter);
  min-width: fit-content; /* Prevent shrinking */
}

.timezone-label {
  width: 48px;
  flex-shrink: 0;
  padding: 8px 4px;
  font-size: 11px;
  color: var(--text-muted);
  text-align: right;
  border-right: 1px solid var(--surface-lighter);
}

.day-header:last-child {
  border-right: none;
}

.calendar-grid-container {
  display: flex;
  position: relative;
  max-height: 800px;
  overflow-y: auto;
  scroll-behavior: smooth;
  background: var(--surface);
  box-sizing: border-box;
  min-width: fit-content;
  width: 100%;
  /* Total height for 24 hours: 24 * 60px = 1440px */
  /* Users can scroll through the full day */
}

.time-axis {
  width: 48px;
  flex-shrink: 0;
  border-right: 1px solid var(--surface-lighter);
  position: sticky;
  left: 0;
  background: var(--surface);
  z-index: 5;
  box-sizing: border-box;
}

.time-slot {
  height: 60px;
  padding: 4px 4px;
  font-size: 11px;
  color: var(--text-muted);
  text-align: right;
  border-bottom: 1px solid var(--surface-lighter);
  position: relative;
  box-sizing: border-box;
}

/* Remove the ::after pseudo-element as it creates duplicate border */
.time-slot::after {
  display: none;
}

.days-grid {
  display: flex;
  flex: 1 1 0;
  min-width: 0;
  position: relative;
  box-sizing: border-box;
}

.day-column {
  flex: 1 1 0;
  min-width: 0;
  position: relative;
  border-right: 1px solid var(--surface-lighter);
  min-height: 1440px; /* 24 hours * 60px = 1440px - full day height */
  box-sizing: border-box;
}

.day-column:last-child {
  border-right: none;
}

.day-column.current-day-column {
  background-color: rgba(106, 122, 90, 0.05);
}

[data-theme="dark"] .day-column.current-day-column {
  background-color: rgba(141, 175, 155, 0.1);
}

.time-cell {
  height: 60px;
  border-bottom: 1px solid var(--surface-lighter);
  position: relative;
}

.time-cell:hover {
  background-color: var(--surface-light);
}

.calendar-event {
  position: absolute;
  padding: 2px 6px;
  border-radius: 4px;
  cursor: pointer;
  overflow: hidden;
  font-size: 12px;
  z-index: 2;
  transition: all 0.2s ease;
  /* Default positioning - will be overridden by inline styles for overlapping events */
  left: 4px;
  right: 4px;
}

.calendar-event:hover {
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  z-index: 3;
}

.event-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: #ea4335;
  position: absolute;
  left: 4px;
  top: 6px;
}

.event-content {
  margin-left: 14px;
}

.event-title {
  font-weight: 500;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  font-size: 12px;
  line-height: 1.3;
}

.event-time {
  font-size: 11px;
  color: var(--text-muted);
  margin-top: 2px;
}

/* Current time indicator line */
.current-time-line {
  position: absolute;
  left: 0;
  right: 0;
  height: 2px;
  background-color: #ea4335;
  z-index: 10;
  pointer-events: none;
}

.current-time-dot {
  position: absolute;
  left: -6px;
  top: -5px;
  width: 12px;
  height: 12px;
  background-color: #ea4335;
  border-radius: 50%;
  border: 2px solid white;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
}

/* Mobile responsive for calendar */
@media (max-width: 960px) {
  .calendar-grid-container {
    max-height: 600px;
  }

  .day-column {
    min-width: 80px;
    min-height: 1200px;
  }

  .day-header {
    min-width: 80px;
  }

  .timezone-label {
    width: 40px;
    font-size: 10px;
  }

  .time-axis {
    width: 40px;
  }

  .time-slot {
    font-size: 10px;
    height: 50px;
  }

  .time-cell {
    height: 50px;
  }

  .day-number {
    font-size: 18px;
  }

  .day-number.highlighted {
    width: 28px;
    height: 28px;
    font-size: 16px;
    background-color: var(--primary);
  }

  .pending-tasks-banner {
    font-size: 9px;
    padding: 1px 4px;
  }

  .calendar-event {
    font-size: 11px;
    padding: 1px 4px;
  }

  .event-title {
    font-size: 11px;
  }

  .event-time {
    font-size: 10px;
  }
}
</style>
