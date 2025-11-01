<template>
  <v-container class="progress-container py-4 py-md-8 px-2 px-md-8">
    <div class="px-2 px-md-0 mb-4 mb-md-6">
      <h1 class="text-h6 text-md-h5 text-primary font-weight-bold mb-1">Progress Analytics</h1>
      <p class="text-caption text-md-body-2 text-muted">Track your academic and wellness journey</p>
    </div>

    <!-- Stats Section -->
    <v-row dense class="mb-4 mb-md-6 px-2 px-md-0">
      <v-col cols="6" sm="6" md="3">
        <v-card class="rounded-xl animate-fade-up stat-card" variant="outlined" hover>
          <v-card-text class="text-center py-4 py-md-6">
            <v-icon icon="mdi-clock-time-four-outline" size="24" size-md="26" class="mb-2 text-primary" />
            <div class="text-caption text-md-subtitle-2">Study Hours</div>
            <div class="text-h5 text-md-h6 font-weight-bold mt-1">
              {{ studyStats.studyHours }} Hours
            </div>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="6" sm="6" md="3">
        <v-card class="rounded-xl animate-fade-up stat-card" variant="outlined" hover>
          <v-card-text class="text-center py-4 py-md-6">
            <v-icon icon="mdi-target" size="24" size-md="26" class="mb-2 text-primary" />
            <div class="text-caption text-md-subtitle-2">Tasks Completed</div>
            <div class="text-h5 text-md-h6 font-weight-bold mt-1">{{ completionRate }}%</div>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="6" sm="6" md="3">
        <v-card class="rounded-xl animate-fade-up stat-card" variant="outlined" hover>
          <v-card-text class="text-center py-4 py-md-6">
            <v-icon icon="mdi-fire" size="24" size-md="26" class="mb-2 text-primary" />
            <div class="text-caption text-md-subtitle-2">Study Streak</div>
            <div class="text-h5 text-md-h6 font-weight-bold mt-1">
              {{ studyStats.studyStreak }} days
            </div>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="6" sm="6" md="3">
        <v-card class="rounded-xl animate-fade-up stat-card" variant="outlined" hover>
          <v-card-text class="text-center py-4 py-md-6">
            <v-icon icon="mdi-heart-outline" size="24" size-md="26" class="mb-2 text-primary" />
            <div class="text-caption text-md-subtitle-2">Wellness Check-ins</div>
            <div class="text-h5 text-md-h6 font-weight-bold mt-1">
              {{ wellnessOverview.totalCheckIns }} check-ins
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Tabs -->
    <div class="tab-navigation px-2 px-md-0">
      <!-- const tabs = ["Study Analytics", "Task Progress", "Wellness Trends", "Insights"]; -->
      <div class="tab-item" :class="{ active: tab === 0 }" @click="tab = 0">
        Study Analytics
      </div>
      <div class="tab-item" :class="{ active: tab === 1 }" @click="tab = 1">
        Task Progress
      </div>
      <div class="tab-item" :class="{ active: tab === 2 }" @click="tab = 2">
        Wellness Trends
      </div>
      <div class="tab-item" :class="{ active: tab === 3 }" @click="tab = 3">Insights</div>
    </div>

    <v-window v-model="tab" :transition="false" :touch="false">
      <v-window-item :value="0">
        <v-row class="mx-0">
          <v-col cols="12" md="6">
            <v-card class="pa-4 pa-md-6 rounded-xl mb-4 mb-md-0 mx-2 mx-md-0" elevation="0" variant="outlined">
              <v-card-title class="d-flex flex-wrap align-center text-h6 font-weight-bold text-primary mb-2 text-wrap">
                <v-icon color="info" class="mr-2">mdi-chart-bar</v-icon>
                Daily Study Time (Last 7 Days)
              </v-card-title>
              <v-card-subtitle class="text-caption text-md-body-2 pt-0 text-wrap">
                Hours spent studying each day
              </v-card-subtitle>

              <div v-if="hasDailyStudyData">
                <apexchart ref="dailyStudyChart" type="bar" :height="$vuetify.display.mobile ? 200 : 250"
                  :options="dailyStudyOptions" :series="dailyStudySeries" />
              </div>
              <v-alert v-else variant="tonal" color="info" icon="mdi-chart-bar" density="compact" border="start"
                class="mt-4 rounded-lg">
                <div class="text-subtitle-1 font-weight-medium mb-1">
                  No Study Data Yet
                </div>
                <div class="text-body-2 text-medium-emphasis mb-2">
                  Start a study session to begin tracking your time and subjects.
                </div>
                <v-btn to="/timer" size="small" color="primary" variant="flat" prepend-icon="mdi-play-circle-outline"
                  class="text-none">
                  Start Study Session
                </v-btn>
              </v-alert>
            </v-card>
          </v-col>

          <v-col cols="12" md="6">
            <v-card class="pa-4 pa-md-6 rounded-xl mx-2 mx-md-0" elevation="0" variant="outlined">
              <v-card-title class="d-flex flex-wrap align-center text-h6 font-weight-bold text-primary mb-2 text-wrap">
                <v-icon color="warning" class="mr-2">mdi-chart-pie</v-icon>
                Study Time by Subject
              </v-card-title>
              <v-card-subtitle class="text-caption text-md-body-2 pt-0">Distribution of study hours</v-card-subtitle>

              <div v-if="hasSubjectData">
                <apexchart ref="subjectChart" type="donut" :height="$vuetify.display.mobile ? 200 : 250"
                  :options="subjectOptions" :series="subjectSeries" />
              </div>
              <v-alert v-else variant="tonal" color="warning" icon="mdi-chart-pie" density="compact" border="start"
                class="mt-4 rounded-lg">
                <div class="text-subtitle-1 font-weight-medium mb-1">
                  No Subject Data Yet
                </div>
                <div class="text-body-2 text-medium-emphasis mb-2">
                  Start a study session to begin tracking your time and subjects.
                </div>
                <v-btn to="/timer" size="small" color="primary" variant="flat" prepend-icon="mdi-play-circle-outline"
                  class="text-none">
                  Start Study Session
                </v-btn>
              </v-alert>
            </v-card>
          </v-col>
        </v-row>
      </v-window-item>

      <v-window-item :value="1">
        <v-row class="mx-0">
          <!-- Task Completion Trends Chart -->
          <v-col cols="12">
            <v-card class="pa-4 pa-md-6 rounded-xl mb-4 mx-2 mx-md-0 transition-all" elevation="0" variant="outlined">
              <!-- Header -->
              <v-card-title class="d-flex flex-wrap align-center text-h6 font-weight-bold text-primary mb-2 text-wrap">
                <v-icon color="primary" class="mr-2">mdi-clipboard-check-outline</v-icon>
                Task Completion Trends
              </v-card-title>

              <v-card-subtitle class="text-caption text-md-body-2 pt-0 text-wrap">
                Tasks created vs completed over the last 7 days
              </v-card-subtitle>

              <!-- Chart Section -->
              <div v-if="hasTaskData">
                <apexchart ref="taskChart" type="bar" :height="$vuetify.display.mobile ? 200 : 250"
                  :options="taskCompletionOptions" :series="taskCompletionSeries" />
              </div>

              <!-- Empty State -->
              <v-alert v-else variant="tonal" color="primary" icon="mdi-clipboard-check-outline" density="compact"
                border="start" class="mt-4 rounded-lg">
                <div class="text-subtitle-2 text-md-subtitle-1 font-weight-medium mb-1">
                  No Task Activity
                </div>

                <div class="text-body-2 text-medium-emphasis mb-2">
                  Create and complete tasks to visualize your weekly productivity trends.
                </div>

                <v-btn to="/task-tracker" size="small" color="primary" variant="flat"
                  prepend-icon="mdi-plus-circle-outline" class="text-none">
                  Add New Task
                </v-btn>
              </v-alert>
            </v-card>
          </v-col>

        </v-row>
        <!-- Task Stats (Total Tasks, Completed, Completion Rate) -->
        <div class="px-2 px-md-0">
          <v-row dense>
            <v-col cols="12" sm="4">
              <v-card class="rounded-xl" elevation="0" variant="outlined">
                <v-card-text class="text-center py-4 py-md-6">
                  <v-icon icon="mdi-format-list-checks" size="24" size-md="26" class="mb-2 text-primary" />
                  <div class="text-caption text-md-subtitle-2">Total Tasks</div>
                  <div class="text-h5 text-md-h6 font-weight-bold mt-1">{{ totalTasks }}</div>
                </v-card-text>
              </v-card>
            </v-col>

            <v-col cols="12" sm="4">
              <v-card class="rounded-xl" elevation="0" variant="outlined">
                <v-card-text class="text-center py-4 py-md-6">
                  <v-icon icon="mdi-check-circle-outline" size="24" size-md="26" class="mb-2 text-primary" />
                  <div class="text-caption text-md-subtitle-2">Completed</div>
                  <div class="text-h5 text-md-h6 font-weight-bold mt-1">{{ completedTasks }}</div>
                </v-card-text>
              </v-card>
            </v-col>

            <v-col cols="12" sm="4">
              <v-card class="rounded-xl" elevation="0" variant="outlined">
                <v-card-text class="text-center py-4 py-md-6">
                  <v-icon icon="mdi-percent" size="24" size-md="26" class="mb-2 text-primary" />
                  <div class="text-caption text-md-subtitle-2">Completion Rate</div>
                  <div class="text-h5 text-md-h6 font-weight-bold mt-1">{{ completionRate }}%</div>
                </v-card-text>
              </v-card>
            </v-col>
          </v-row>
        </div>
      </v-window-item>

      <v-window-item :value="2">
        <v-row class="mx-0">
          <!-- Wellness Trends Chart -->
          <v-col cols="12">
            <v-card class="pa-4 pa-md-6 rounded-xl mb-4 mx-2 mx-md-0 transition-all" elevation="0" variant="outlined">
              <!-- Title -->
              <v-card-title class="d-flex flex-wrap align-center text-h6 font-weight-bold text-primary mb-2 text-wrap">
                <v-icon color="success" class="mr-2">mdi-heart-pulse</v-icon>
                Wellness Trends (Last 7 Days)
              </v-card-title>

              <!-- Subtitle -->
              <v-card-subtitle class="text-caption text-md-body-2 pt-0 text-wrap">

                Track your mood, energy, sleep, and stress levels
              </v-card-subtitle>

              <!-- Chart Section -->
              <div v-if="hasWellnessData">
                <apexchart ref="wellnessChart" type="line" :height="$vuetify.display.mobile ? 200 : 250"
                  :options="wellnessOptions" :series="wellnessSeries" />
              </div>

              <!-- Empty State (No Data) -->
              <v-alert v-else variant="tonal" color="success" icon="mdi-heart-pulse" density="compact" border="start"
                class="mt-4 rounded-lg">
                <div class="text-subtitle-2 text-md-subtitle-1 font-weight-medium mb-1">
                  No Wellness Check-ins
                </div>

                <div class="text-body-2 text-medium-emphasis mb-2">
                  Log your daily wellness check-ins to start tracking your mood,
                  energy, and sleep trends.
                </div>

                <v-btn to="/checkin" size="small" color="primary" variant="flat" prepend-icon="mdi-play-circle-outline"
                  class="text-none">
                  Check In
                </v-btn>
              </v-alert>
            </v-card>
          </v-col>


        </v-row>

        <!-- Wellness Stats (Mood, Energy, Sleep, Stress) -->
        <v-row class="px-2 px-md-0" dense>
          <v-col cols="6" sm="3">
            <v-card class="rounded-xl" elevation="0" variant="outlined">
              <v-card-text class="text-center py-4 py-md-6">
                <div class="text-caption text-md-subtitle-2">Mood</div>
                <div class="text-h5 text-md-h6 font-weight-bold mt-1">{{ mood }}/10</div>
                <div class="text-caption text-disabled">7-day avg</div>
              </v-card-text>
            </v-card>
          </v-col>

          <v-col cols="6" sm="3">
            <v-card class="rounded-xl" elevation="0" variant="outlined">
              <v-card-text class="text-center py-4 py-md-6">
                <div class="text-caption text-md-subtitle-2">Energy</div>
                <div class="text-h5 text-md-h6 font-weight-bold mt-1">{{ energy }}/10</div>
                <div class="text-caption text-disabled">7-day avg</div>
              </v-card-text>
            </v-card>
          </v-col>

          <v-col cols="6" sm="3">
            <v-card class="rounded-xl" elevation="0" variant="outlined">
              <v-card-text class="text-center py-4 py-md-6">
                <div class="text-caption text-md-subtitle-2">Sleep</div>
                <div class="text-h5 text-md-h6 font-weight-bold mt-1">{{ sleep }}/10</div>
                <div class="text-caption text-disabled">7-day avg</div>
              </v-card-text>
            </v-card>
          </v-col>

          <v-col cols="6" sm="3">
            <v-card class="rounded-xl" elevation="0" variant="outlined">
              <v-card-text class="text-center py-4 py-md-6">
                <div class="text-caption text-md-subtitle-2">Stress</div>
                <div class="text-h5 text-md-h6 font-weight-bold mt-1">{{ stress }}/10</div>
                <div class="text-caption text-disabled">7-day avg</div>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
      </v-window-item>

      <v-window-item :value="3">
        <v-col cols="12">
          <v-card class="pa-4 pa-md-6 rounded-xl mb-4 mx-2 mx-md-0 transition-all" elevation="0" variant="outlined">
            <v-card-title class="d-flex flex-wrap align-center text-h6 font-weight-bold text-primary mb-2 text-wrap">
              <v-icon color="warning" class="mr-2">mdi-lightbulb-on-10</v-icon>
              Personalized Insights
            </v-card-title>
            <v-card-subtitle class="text-caption text-md-body-2 pt-0 text-wrap">
              Tips and observations based on your recent activity.
            </v-card-subtitle>

            <v-list density="comfortable" class="mt-4 rounded-lg bg-transparent">
              <v-list-item v-for="(insight, index) in generatedInsights" :key="index" class="mb-2 pa-2 rounded-lg"
                variant="tonal" color="primary">
                <template #prepend>
                  <v-icon :color="index % 2 === 0 ? 'warning' : 'info'">
                    {{ index % 3 === 0 ? 'mdi-star-four-points' : 'mdi-chevron-right' }}
                  </v-icon>
                </template>
                <v-list-item-title class="text-body-2 text-md-body-1 font-weight-medium text-wrap" v-html="insight">
                </v-list-item-title>
              </v-list-item>

              <v-list-item v-if="generatedInsights.length === 0" class="mb-2 pa-2 rounded-lg" variant="tonal"
                color="warning">
                <template #prepend>
                  <v-icon color="warning">mdi-alert-circle-outline</v-icon>
                </template>
                <v-list-item-title class="text-body-2 text-md-body-1 font-weight-medium text-wrap">
                  Log your study time, tasks, and wellness check-ins to generate personalized insights!
                </v-list-item-title>
              </v-list-item>
            </v-list>
          </v-card>
        </v-col>
      </v-window-item>
    </v-window>
  </v-container>
</template>


<script setup>
import { ref, computed, onMounted, reactive, watch, nextTick } from "vue";
import ApexCharts from "vue3-apexcharts";
import { db } from "@/lib/firebase";
import {
  collection,
  query,
  where,
  orderBy,
  limit,
  getDocs,
  Timestamp,
} from "firebase/firestore";
import { auth } from "@/lib/firebase";
import { api } from "@/lib/api.js";
import { useTheme } from "vuetify";

onMounted(() => {
  getTaskStats();
  getWellnessOverview();
  loadWellnessData();
  getTaskGraph();
  loadWeeklyStudyChart();
  // try1();
});

const filteredInsights = [""];
const generatedInsights = ref([]);
const dailyStudyChart = ref(null);
const subjectChart = ref(null);
const taskChart = ref(null);
const wellnessChart = ref(null);
const theme = useTheme();
const isDark = computed(() => theme.global.current.value.dark);

const hasDailyStudyData = computed(() => {
  return (
    dailyStudySeries.value.length > 0 &&
    dailyStudySeries.value[0].data.some((d) => d > 0)
  );
});

const hasSubjectData = computed(() => {
  return subjectSeries.value.length > 0 && subjectSeries.value.some((s) => s > 0);
});

const hasTaskData = computed(() => {
  return (
    taskCompletionSeries.value.length > 0 &&
    taskCompletionSeries.value.some((series) => series.data.some((d) => d > 0))
  );
});

const hasWellnessData = computed(() => {
  return wellnessSeries.value.length > 0 &&
    wellnessSeries.value.some((series) => series.data.some((d) => d > 0));
});


const taskStat = reactive({
  completed: 0,
  dueToday: 0,
  overdue: 0,
  total: 0,
});

const wellnessOverview = reactive({
  streak: 0,
  totalCheckIns: 0,
  lastCheckInDate: "",
});

const studyStats = reactive({
  studyHours: 0,
  studyStreak: 0,
});

const tab = ref(0);

// Bar chart (Daily Study Time)
const dailyStudySeries = ref([]);
const dailyStudyOptions = ref({
  ...getApexThemeOptions(isDark.value),
  chart: { toolbar: { show: false } },
  xaxis: { categories: [] },
  colors: ["#6A7A5A"],
  dataLabels: { enabled: false },
});

// Donut chart (Study Time by Subject)
const subjectSeries = ref([]);
const subjectOptions = ref({
  labels: [],
  colors: [],
  legend: { position: "bottom" },
});

// task progress
const totalTasks = computed(() => taskStat.total);
const completedTasks = computed(() => taskStat.completed);
const completionRate = computed(() =>
  totalTasks.value > 0 ? ((completedTasks.value / totalTasks.value) * 100).toFixed(1) : 0
);

const taskCompletionSeries = ref([
  { name: "Created Tasks", data: [] },
  { name: "Completed Tasks", data: [] },
]);

const taskCompletionOptions = ref({
  ...getApexThemeOptions(isDark.value),
  chart: { type: "bar", toolbar: { show: false } },
  xaxis: { categories: [] },
  yaxis: { min: 0 },
  colors: ["#4CAF50", "#FF7043"],
  dataLabels: { enabled: false },
});

const wellnessSeries = ref([]);

const wellnessOptions = ref({
  ...getApexThemeOptions(isDark.value),
  chart: {
    ...getApexThemeOptions(isDark.value).chart,
    type: "line",
    toolbar: { show: false },
  },
  xaxis: { categories: [] },
  yaxis: { min: 0, max: 10 },
  stroke: { width: 2, curve: "smooth" },
  markers: { size: 4 },
  colors: ["#FF7043", "#42A5F5", "#8DAF9B", "#FFD54F"],
});

//Data for Wellness Stats (Mood, Energy, Sleep, Stress)
const mood = ref(0);
const energy = ref(0);
const sleep = ref(0);
const stress = ref(0);

function formatToUserTimezone(isoDate, options = {}) {
  const date = new Date(isoDate);
  return new Intl.DateTimeFormat(undefined, {
    timeZone: undefined,
    ...options,
  }).format(date);
}

async function try1() {
  try {
    const mockSession = {
      duration_minutes: 50,
      subject: 'Computer Science',
      task: 'Implement linked list in Python',
      task_id: 'task_abc123',
      notes: 'Practiced building and traversing linked lists; review time complexity later.',
      session_type: 'focus'
    }

    // Make sure your Axios instance points to the correct backend base URL
    const response = await api.post("/api/study-sessions/", mockSession)

    console.log("Session created:", response.data)
    return response.data

  } catch (error) {
    console.error("Failed to create session:", error)
  }
}

async function loadWeeklyStudyChart() {
  try {
    const data = await api.get("/api/study-sessions/stats/summary");
    console.log(data);
    const dailyData = data.daily_hours_past_week;
    studyStats.studyHours = data.total_hours || 0;
    studyStats.studyStreak = data.study_streak || 0;
    if (!dailyData || dailyData.length === 0) {
      console.error("No daily study hours data found in API response");
      return;
    }

    const dates = dailyData.map(item => item.date);
    const hours = dailyData.map(item => item.hours);

    dailyStudySeries.value = [{ name: "Study Time (hrs)", data: hours }];

    dailyStudyOptions.value = {
      ...dailyStudyOptions.value,
      xaxis: {
        ...dailyStudyOptions.value.xaxis,
        categories: dates.map((date) =>
          new Date(date).toLocaleDateString(undefined, { month: "short", day: "numeric" })
        ),
      },
    };

    const subjectData = data.subject_hours_past_week;

    if (!subjectData || subjectData.length === 0) {
      console.warn("No subject study hours data found for pie chart");
    }

    const subjects = subjectData.map(item => item.subject);
    const subjectHours = subjectData.map(item => item.hours);

    subjectSeries.value = subjectHours;

    subjectOptions.value = {
      ...subjectOptions.value,
      labels: subjects,
    };
    subjectOptions.value.colors = subjects.map(hashStringToColor);

  } catch (error) {
    console.error("Failed to load weekly study chart:", error);
  }
}

function getApexThemeOptions(isDark) {
  return {
    theme: {
      mode: isDark ? "dark" : "light",
    },
    chart: {
      foreColor: isDark ? "#e0e0e0" : "#333",
      background: "transparent",
    },
    grid: {
      borderColor: isDark ? "#444" : "#eee",
    },
    xaxis: {
      labels: { style: { colors: isDark ? "#ccc" : "#555" } },
      axisBorder: { color: isDark ? "#666" : "#ccc" },
      axisTicks: { color: isDark ? "#666" : "#ccc" },
    },
    yaxis: {
      labels: { style: { colors: isDark ? "#ccc" : "#555" } },
    },
    tooltip: {
      theme: isDark ? "dark" : "light",
    },
    legend: {
      labels: { colors: isDark ? "#ddd" : "#444" },
    },
  };
}

async function getTaskGraph() {
  const user = auth.currentUser;
  if (!user) return;
  try {
    const response = await api.get("/api/tasks/weekly-activity");
    taskCompletionOptions.value.xaxis.categories = response.map((item) =>
      formatToUserTimezone(item.date, { month: "short", day: "numeric" })
    );

    taskCompletionSeries.value[0].data = response.map((item) => item.created);
    taskCompletionSeries.value[1].data = response.map((item) => item.completed);
  } catch (error) {
    console.error("Error loading data for task graph:", error);
  }
}

// async function loadStudyData() {
//   const user = auth.currentUser;
//   if (!user) return;
//   try {
//     const response = await api.get("/api/study-sessions/stats/summary");
//     studyStats.studyHours = response.total_hours || 0;
//     studyStats.studyStreak = response.sessions_this_month || 0;
//   } catch (error) {
//     console.error("Error loading study data:", error);
//     studyStats.studyHours = 0;
//     studyStats.studyStreak = 0;
//   }
// }

// async function loadStudyStreak() {
//   const user = auth.currentUser;
//   if (!user) return;
//   try {
//     const response = await api.get("/api/study-sessions/streak");
//     studyStats.studyStreak = response.current_streak || 0;
//   } catch (error) {
//     console.error("Error loading study data:", error);
//     studyStats.studyStreak = 0;
//   }
// }

async function getTaskStats() {
  try {
    const tasksStats = await api.get("/api/tasks/stats");
    Object.assign(taskStat, {
      completed: tasksStats.completed,
      total: tasksStats.total,
    });
  } catch (error) {
    console.error("Failed to fetch task stats:", error);
  }
}

async function getWellnessOverview() {
  try {
    const user = auth.currentUser; // Ensure the user is logged in
    if (!user) return;

    // Query Firestore for wellness check-ins
    const q = query(
      collection(db, "wellnessCheckIns"),
      where("userId", "==", user.uid),
      orderBy("date", "desc")
    );

    const snapshot = await getDocs(q);
    const checkIns = snapshot.docs.map((doc) => doc.data());

    // Total Check-ins
    wellnessOverview.totalCheckIns = checkIns.length;

    // Last Check-in Date
    if (checkIns.length > 0) {
      const lastCheckIn = checkIns[0].date.toDate(); // Get the latest check-in date
      wellnessOverview.lastCheckInDate = lastCheckIn.toLocaleDateString(undefined, {
        weekday: "long",
        year: "numeric",
        month: "long",
        day: "numeric",
      });
    }

    // Calculate Streak (Consecutive Check-ins)
    wellnessOverview.streak = calculateStreak(checkIns);
  } catch (error) {
    console.error("Failed to fetch wellness stats:", error);
  }
}

// Function to calculate streak based on check-in dates
function calculateStreak(checkIns) {
  let streak = 0;
  const now = new Date();

  // Loop through check-ins in reverse order (most recent to least recent)
  for (let i = 0; i < checkIns.length; i++) {
    const checkInDate = checkIns[i].date.toDate();

    // Check if this check-in is on the current day or consecutive days
    const diff = Math.floor((now - checkInDate) / (1000 * 60 * 60 * 24)); // days difference

    if (diff === streak) {
      streak++; // Increment streak if consecutive day
    } else if (diff > streak) {
      break; // If there's a gap in check-ins, stop counting the streak
    }
  }

  return streak;
}

function hashStringToColor(str) {
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    hash = str.charCodeAt(i) + ((hash << 5) - hash);
  }
  const hue = Math.abs(hash) % 360;
  return `hsl(${hue}, 70%, 60%)`; // you can adjust saturation/lightness
}

async function loadWellnessData() {
  try {
    const user = auth.currentUser;
    if (!user) return;

    const now = new Date();
    const sevenDaysAgo = new Date();
    sevenDaysAgo.setDate(now.getDate() - 6); // last 7 days

    const q = query(
      collection(db, "wellnessCheckIns"),
      where("userId", "==", user.uid),
      where("date", ">=", sevenDaysAgo),
      orderBy("date", "asc"),
      limit(7)
    );

    const snapshot = await getDocs(q);
    const data = snapshot.docs.map((doc) => doc.data());

    // Build a map keyed by date string for quick lookup
    const dataMap = {};
    data.forEach((d) => {
      const dateStr = d.date.toDate
        ? d.date.toDate().toLocaleDateString("en-US", { month: "short", day: "2-digit" })
        : new Date(d.date).toLocaleDateString("en-US", {
          month: "short",
          day: "2-digit",
        });
      dataMap[dateStr] = d;
    });

    const formattedDates = [];
    const moodData = [];
    const energyData = [];
    const sleepData = [];
    const stressData = [];
    const notesData = [];

    for (let i = 0; i < 7; i++) {
      const date = new Date(sevenDaysAgo);
      date.setDate(sevenDaysAgo.getDate() + i);
      const dateStr = date.toLocaleDateString("en-US", {
        month: "short",
        day: "2-digit",
      });
      formattedDates.push(dateStr);

      const dayData = dataMap[dateStr] || {};

      moodData.push(dayData.mood !== undefined ? dayData.mood : 0);
      energyData.push(dayData.energy !== undefined ? dayData.energy : 0);
      sleepData.push(dayData.sleep !== undefined ? dayData.sleep : 0);
      stressData.push(dayData.stress !== undefined ? dayData.stress : 0);
      notesData.push(dayData.notes || "");
    }

    // Update chart data & x-axis
    wellnessSeries.value = [
      { name: "Mood", data: moodData },
      { name: "Energy", data: energyData },
      { name: "Sleep", data: sleepData },
      { name: "Stress", data: stressData },
    ];
    wellnessOptions.value.xaxis.categories = formattedDates;

    const avg = (arr) => {
      const validData = arr.filter(
        (value) => value !== 0 || arr.indexOf(value) === arr.lastIndexOf(value)
      );
      return validData.length > 0
        ? (validData.reduce((a, b) => a + b, 0) / validData.length).toFixed(1)
        : 0;
    };

    wellnessOptions.value.tooltip = {
      shared: true,
      custom: function ({ series, dataPointIndex, w }) {
        const dateLabel = formattedDates[dataPointIndex];
        const mood = series[0][dataPointIndex];
        const energy = series[1][dataPointIndex];
        const sleep = series[2][dataPointIndex];
        const stress = series[3][dataPointIndex];
        const note = notesData[dataPointIndex] || "No notes";

        return `
      <div style="min-width: 150px; padding: 8px;">  <!-- Added min-width and some padding -->
        <div class="apexcharts-tooltip-title" style="font-weight: 600; padding-bottom: 8px;">${dateLabel}</div>
        <div class="apexcharts-tooltip-series-group apexcharts-active" style="display: flex; align-items: center; padding: 4px 0;">
          <span class="apexcharts-tooltip-marker" style="background-color: #FF7043; margin-right: 6px; border-radius: 50%; width: 10px; height: 10px; display: inline-block;"></span>
          <span>Mood: ${mood}</span>
        </div>
        <div class="apexcharts-tooltip-series-group" style="display: flex; align-items: center; padding: 4px 0;">
          <span class="apexcharts-tooltip-marker" style="background-color: #42A5F5; margin-right: 6px; border-radius: 50%; width: 10px; height: 10px; display: inline-block;"></span>
          <span>Energy: ${energy}</span>
        </div>
        <div class="apexcharts-tooltip-series-group" style="display: flex; align-items: center; padding: 4px 0;">
          <span class="apexcharts-tooltip-marker" style="background-color: #80CBC4; margin-right: 6px; border-radius: 50%; width: 10px; height: 10px; display: inline-block;"></span>
          <span>Sleep: ${sleep}</span>
        </div>
        <div class="apexcharts-tooltip-series-group" style="display: flex; align-items: center; padding: 4px 0;">
          <span class="apexcharts-tooltip-marker" style="background-color: #FFD54F; margin-right: 6px; border-radius: 50%; width: 10px; height: 10px; display: inline-block;"></span>
          <span>Stress: ${stress}</span>
        </div>
<div style="
    border-top: 1px solid #eee;
    margin-top: 10px;
    padding-top: 8px;
    font-style: italic;
    font-size: 13px;
    white-space: normal;
    word-break: break-word;
">
  Notes: ${note}
</div>
    `;
      },
    };

    // Calculate the average for each field (mood, energy, sleep, stress)
    mood.value = avg(moodData);
    energy.value = avg(energyData);
    sleep.value = avg(sleepData);
    stress.value = avg(stressData);
  } catch (error) {
    console.error("Error loading wellness data:", error);
  }
}

async function updateAllChartsTheme(isDarkMode) {
  const themeOptions = getApexThemeOptions(isDarkMode);
  await nextTick();

  const charts = [dailyStudyChart, subjectChart, taskChart, wellnessChart];

  charts.forEach((chartRef) => {
    if (chartRef.value?.chart?.updateOptions) {
      const currentConfig = chartRef.value.chart.w.config;

      // Preserve categories even if themeOptions overrides them
      const preservedCategories = currentConfig?.xaxis?.categories?.length
        ? currentConfig.xaxis.categories
        : chartRef.value?.options?.xaxis?.categories ||
        wellnessOptions.value?.xaxis?.categories ||
        [];

      chartRef.value.chart.updateOptions(
        {
          ...currentConfig,
          ...themeOptions,
          xaxis: {
            ...currentConfig.xaxis,
            ...themeOptions.xaxis,
            categories: preservedCategories,
          },
          yaxis: {
            ...currentConfig.yaxis,
            ...themeOptions.yaxis,
          },
          legend: {
            ...currentConfig.legend,
            ...themeOptions.legend,
          },
          grid: {
            ...currentConfig.grid,
            ...themeOptions.grid,
          },
        },
        false,
        true
      );
    }
  });
}

watch(isDark, (newVal) => {
  updateAllChartsTheme(newVal);
});
function generateInsights() {
  const insights = [];
  const { studyHours, studyStreak, prevStudyHours = 0 } = studyStats;
  const completionRateValue = Number(completionRate.value);
  const avgSleep = Number(sleep.value);
  const avgStress = Number(stress.value);
  const avgEnergy = Number(energy.value);
  const avgMood = Number(mood.value);

  if (studyHours > 0) {
    if (studyHours > 20) {
      insights.push(`📘 You’ve logged <strong>${studyHours} hours</strong> of study — impressive dedication this week!`);
    } else if (studyHours > 10) {
      insights.push(`⏱️ Consistent effort with <strong>${studyHours} hrs</strong> logged. Keep your pace steady!`);
    } else {
      insights.push(`📅 Total study time: <strong>${studyHours} hrs</strong>. Try short daily goals to build rhythm.`);
    }
  }

  if (prevStudyHours > 0) {
    const diff = studyHours - prevStudyHours;
    if (diff > 2) {
      insights.push(`📈 You studied <strong>${diff} hrs more</strong> than last week — great improvement!`);
    } else if (diff < -2) {
      insights.push(`📉 You studied <strong>${Math.abs(diff)} hrs less</strong> than last week. Try reviewing what slowed you down.`);
    }
  }

  if (completionRateValue > 0) {
    if (completionRateValue >= 90) {
      insights.push(`✅ <strong>Outstanding!</strong> You’ve completed <strong>${completionRateValue}%</strong> of your tasks.`);
    } else if (completionRateValue >= 70) {
      insights.push(`🗂️ Solid performance — <strong>${completionRateValue}%</strong> done. Keep the final push strong.`);
    } else {
      insights.push(`📋 Only <strong>${completionRateValue}%</strong> tasks done. Try batching similar tasks for efficiency.`);
    }
  }

  if (studyStreak > 0) {
    if (studyStreak > 5) {
      insights.push(`🔥 You’re on a <strong>${studyStreak}-day streak!</strong> The momentum is strong.`);
    } else {
      insights.push(`📆 A <strong>${studyStreak}-day streak</strong> shows progress. Keep building the habit.`);
    }
  }

  if (avgSleep > 0) {
    if (avgSleep < 6) {
      insights.push(`😴 You’re averaging <strong>${avgSleep} hrs</strong> of sleep — aim for 7–9 to stay sharp.`);
    } else if (avgSleep >= 7 && avgSleep <= 9) {
      insights.push(`🌙 <strong>Healthy sleep!</strong> ${avgSleep} hrs on average keeps focus high.`);
    }
  }

  if (avgStress > 0) {
    if (avgStress > 7) {
      insights.push(`⚠️ High stress (<strong>${avgStress}/10</strong>). Schedule breaks or try breathing exercises.`);
    } else if (avgStress < 4) {
      insights.push(`😌 Low stress levels — you’re managing things well.`);
    }
  }

  if (avgEnergy > 0) {
    if (avgEnergy < 4) {
      insights.push(`📉 Energy seems low (<strong>${avgEnergy}/10</strong>). A quick walk or hydration can help.`);
    } else if (avgEnergy > 7) {
      insights.push(`⚡ You’re full of energy! Channel it into your most demanding tasks.`);
    }
  }

  if (avgMood > 0) {
    if (avgMood < 4) {
      insights.push(`☁️ Mood’s a bit low (<strong>${avgMood}/10</strong>). Try celebrating small wins.`);
    } else if (avgMood > 7) {
      insights.push(`😄 Great mood! Perfect time for creative or deep work.`);
    }
  }

  // Combined or cross-pattern insights
  if (avgSleep < 6 && avgEnergy < 5) {
    insights.push(`🧠 Low energy may stem from lack of sleep. Prioritize rest before long sessions.`);
  }
  if (avgStress > 7 && avgMood < 5) {
    insights.push(`💭 High stress may be affecting mood. Consider a short break or relaxation activity.`);
  }
  if (avgEnergy > 7 && studyHours < 8) {
    insights.push(`⚡ You have high energy but limited study hours — maybe use that drive to push further!`);
  }
  if (completionRateValue < 50 && avgStress > 6) {
    insights.push(`📊 Tasks piling up might be raising stress. Break goals into smaller, quicker wins.`);
  }

  // If no meaningful data — show general study tips
  if (insights.length === 0) {
    insights.push(`💡 Tip: Set a specific study start time — it helps build consistency.`);
    insights.push(`📖 Try the <strong>Pomodoro Technique</strong>: 25 min study + 5 min break.`);
    insights.push(`🌱 Remember: consistency beats intensity. Even short focused sessions add up!`);
  }

  generatedInsights.value = insights;
}


watch(
  [
    () => studyStats.studyHours,
    completionRate,
    () => studyStats.studyStreak,
    mood,
    energy,
    sleep,
    stress
  ],
  generateInsights,
  { deep: true, immediate: true }
);


</script>

<style scoped>
.progress-container {
  max-width: 100%;
  padding-left: 8px;
  padding-right: 8px;
}

@media (min-width: 960px) {
  .progress-container {
    padding-left: 24px;
    padding-right: 24px;
    max-width: 1200px;
    margin: 0 auto;
  }
}

.stat-card {
  margin-bottom: 8px;
}

@media (min-width: 600px) {
  .stat-card {
    margin-bottom: 0;
  }
}

/* Mobile responsiveness for tab navigation */
@media (max-width: 960px) {
  .tab-navigation {
    padding: 4px 8px;
    gap: 4px;
    scrollbar-width: none;
    /* Firefox */
  }

  .tab-navigation::-webkit-scrollbar {
    display: none;
    /* Chrome, Safari */
  }

  .tab-item {
    padding: 10px 14px;
    font-size: 0.875rem;
    border-radius: 8px;
  }

  .tab-item.active::after {
    bottom: -3px;
    /* keeps underline visible */
  }
}

.text-muted {
  color: var(--text-muted);
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

/* TAB */
.tab-navigation {
  display: flex;
  gap: 0;
  margin-bottom: 24px;
  background-color: var(--surface-lighter);
  border-radius: 12px;
  padding: 4px;
  position: relative;
  overflow-x: auto;
  overflow-y: hidden;
  -webkit-overflow-scrolling: touch;
}

@media (min-width: 960px) {
  .tab-navigation {
    overflow-x: visible;
  }
}

.tab-item {
  padding: 12px 24px;
  cursor: pointer;
  border-radius: 8px;
  transition: all 0.3s ease;
  color: var(--text-muted);
  font-weight: 500;
  position: relative;
  flex: 1;
  text-align: center;
  background: transparent;
  white-space: nowrap;
}


.tab-item:hover {
  background-color: rgba(255, 255, 255, 0.5);
  color: var(--text-primary);
}

.tab-item.active {
  background-color: var(--surface);
  color: var(--text-primary);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  font-weight: 600;
}

.tab-item.active::after {
  content: "";
  position: absolute;
  bottom: -4px;
  left: 50%;
  transform: translateX(-50%);
  width: 20px;
  height: 3px;
  background-color: var(--primary);
  border-radius: 2px;
}

.v-card {
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
  background: var(--surface);
  border: 1px solid var(--surface-lighter);
}

.v-icon {
  color: #42a5f5;
}

.card {
  display: flex;
  align-items: flex-start;
  background-color: #fff;
  border-left: 5px solid transparent;
  border-radius: 12px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
  padding: 16px 20px;
  transition: box-shadow 0.3s ease;
}

/* Icon styling */
.icon {
  font-size: 24px;
  margin-right: 12px;
  flex-shrink: 0;
  line-height: 1;
  margin-top: 4px;
}

@media (min-width: 960px) {
  .icon {
    font-size: 30px;
    margin-right: 16px;
  }
}

/* Content inside the card */
.content h3 {
  margin: 0 0 4px 0;
  font-size: 15px;
  font-weight: 600;
  color: #333;
}

@media (min-width: 960px) {
  .content h3 {
    font-size: 17px;
  }
}

.content p {
  margin: 0;
  font-size: 13px;
  color: #555;
  line-height: 1.4;
}

@media (min-width: 960px) {
  .content p {
    font-size: 14px;
  }
}

/* Specific color styles */
.card.mood {
  background-color: #eaf2fe;
  border-color: #90caf9;
}

.card.energy {
  background-color: #fff4e5;
  border-color: #ffb74d;
}

.card.sleep {
  background-color: #e6f4ea;
  border-color: #81c784;
}

.card.stress {
  background-color: #fdecea;
  border-color: #e57373;
}

.animate-fade-up {
  opacity: 0;
  transform: translateY(12px);
  animation: fadeUp 0.6s forwards;
  animation-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  animation-delay: 0.15s;
}

@keyframes fadeUp {
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
