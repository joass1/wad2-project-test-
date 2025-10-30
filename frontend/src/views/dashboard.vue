<template>
  <v-container class="py-8">
    <h1 class="text-h5 text-primary font-weight-bold mb-1">
      <template v-if="loading">Loading...</template>
      <template v-else
        >Welcome back, {{ userProfile?.full_name || "User" }}!</template
      >
    </h1>
    <p class="text-body-2 text-muted mb-4">
      Here's your wellness dashboard for today
    </p>

    <!-- Buddy container with gradient -->
    <v-card
      class="mb-6 rounded-xl"
      elevation="0"
      variant="outlined"
      :style="gradient"
    >
      <v-card-text class="py-6">
        <div class="d-flex align-center justify-space-between">
          <div class="d-flex align-center ga-3">
            <div style="font-size: 28px">😊</div>
            <div>
              <div class="text-subtitle-1 font-weight-semibold">{{ displayPetName }}</div>
              <div class="text-body-2 text-muted">Doing well</div>
            </div>
          </div>
          <v-chip color="primary" variant="tonal">Level 1</v-chip>
        </div>

        <!-- Progress Bars -->
        <div class="mt-5">
          <div class="d-flex align-center justify-space-between mb-1">
            <div class="text-body-2">Health</div>
            <div class="text-body-2">80%</div>
          </div>
          <v-progress-linear
            model-value="80"
            height="8"
            rounded
            color="primary"
          />

          <div class="d-flex align-center justify-space-between mt-4 mb-1">
            <div class="text-body-2">Happiness</div>
            <div class="text-body-2">70%</div>
          </div>
          <v-progress-linear
            model-value="70"
            height="8"
            rounded
            color="primary"
          />
        </div>

        <div class="mt-4 d-flex justify-end">
          <v-btn
            color="primary"
            class="text-white"
            prepend-icon="mdi-heart-outline"
            @click="navigateToPetPage"
          >
            Feed Pet
          </v-btn>
        </div>
      </v-card-text>
    </v-card>

    <!-- Your Stats Section -->
    <v-row dense class="mb-4">
      <v-col cols="12" sm="6" md="3">
        <v-card class="rounded-xl" elevation="0" variant="outlined">
          <v-card-text class="text-center">
            <v-icon
              icon="mdi-clock-time-four-outline"
              size="26"
              class="mb-2 text-primary"
            />
            <div class="text-subtitle-2">Study Time Today</div>
            <div class="text-h6 font-weight-bold mt-1">{{ studyTimeFormatted }}</div>
            <div class="text-caption text-disabled">{{ sessionsCompletedToday }} sessions completed</div>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" sm="6" md="3">
        <v-card class="rounded-xl" elevation="0" variant="outlined">
          <v-card-text class="text-center">
            <v-icon icon="mdi-target" size="26" class="mb-2 text-primary" />
            <div class="text-subtitle-2">Task Completion</div>
            <div class="text-h6 font-weight-bold mt-1">{{ taskCompletionPct }}%</div>
            <div class="text-caption text-disabled">{{ tasksCompleted }} of {{ tasksTotal }} tasks done</div>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" sm="6" md="3">
        <v-card class="rounded-xl" elevation="0" variant="outlined">
          <v-card-text class="text-center">
            <v-icon icon="mdi-fire" size="26" class="mb-2 text-primary" />
            <div class="text-subtitle-2">Study Streak</div>
            <div class="text-h6 font-weight-bold mt-1">{{ wellnessStreak }} days</div>
            <div class="text-caption text-disabled">Keep it up 🔥</div>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" sm="6" md="3">
        <v-card class="rounded-xl" elevation="0" variant="outlined">
          <v-card-text class="text-center">
            <v-icon
              icon="mdi-heart-outline"
              size="26"
              class="mb-2 text-primary"
            />
            <div class="text-subtitle-2">Wellness Check</div>
            <div class="text-h6 font-weight-bold mt-1">{{ wellnessDoneToday ? '✅ Done' : '—' }}</div>
            <div class="text-caption text-disabled">{{ wellnessDoneToday ? 'Checked in today' : 'Not yet' }}</div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>


    <!-- Urgent Tasks + Achievements -->
    <v-row dense>
      <v-col cols="12" md="8">
        <v-card class="rounded-xl mb-4" elevation="0" variant="outlined">
          <v-card-title class="pb-0">Urgent Tasks</v-card-title>
          <v-card-subtitle class="pt-0"
            >Tasks due within 3 days</v-card-subtitle
          >
          <v-card-text class="py-8 text-muted">
            No urgent tasks – you're on top of things! 🎉
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" md="4">
        <v-card class="rounded-xl mb-4" elevation="0" variant="outlined">
          <v-card-title class="pb-0">Achievements</v-card-title>
          <v-card-subtitle class="pt-0"
            >Your progress milestones</v-card-subtitle
          >
          <v-list lines="two">
            <LockedAchievement
              title="First Steps"
              sub="Complete your first study session"
            />
            <LockedAchievement title="Task Master" sub="Complete 10 tasks" />
            <LockedAchievement
              title="Consistent Learner"
              sub="Study 5 days in a row"
            />
            <LockedAchievement
              title="Wellness Warrior"
              sub="Check in for 7 days straight"
            />
          </v-list>
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
  } catch (e) {
    console.error('Failed to load dashboard data:', e)
  }
}

onMounted(loadDashboardData)
</script>

<script>
export default {
  components: {
    LockedAchievement: {
      props: ["title", "sub"],
      template: `
        <v-list-item>
          <template #prepend>
            <v-avatar size="28" color="grey-lighten-3">
              <v-icon icon="mdi-lock-outline" />
            </v-avatar>
          </template>
          <v-list-item-title>{{ title }}</v-list-item-title>
          <v-list-item-subtitle>{{ sub }}</v-list-item-subtitle>
        </v-list-item>
      `,
    },
  },
};
</script>

<style scoped>
.text-muted {
  color: var(--text-muted);
}
</style>
