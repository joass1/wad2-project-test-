<template>
  <v-container class="py-8 main-content">
    <div>
      <h1 class="text-h5 text-primary font-weight-bold mb-1">Progress Analytics</h1>
      <p class="text-body-2 text-muted mb-4">Track your academic and wellness journey</p>
    </div>

    <!-- Stats Section -->
    <v-row dense class="mb-4">
      <v-col cols="12" sm="6" md="3">
        <v-card class="rounded-xl animate-fade-up" variant="outlined" hover>
          <v-card-text class="text-center">
            <v-icon
              icon="mdi-clock-time-four-outline"
              size="26"
              class="mb-2 text-primary"
            />
            <div class="text-subtitle-2">Study Hours</div>
            <div class="text-h6 font-weight-bold mt-1">
              {{ studyStats.studyHours }} Hours
            </div>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" sm="6" md="3">
        <v-card class="rounded-xl animate-fade-up" variant="outlined" hover>
          <v-card-text class="text-center">
            <v-icon icon="mdi-target" size="26" class="mb-2 text-primary" />
            <div class="text-subtitle-2">Tasks Completed</div>
            <div class="text-h6 font-weight-bold mt-1">{{ completionRate }}%</div>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" sm="6" md="3">
        <v-card class="rounded-xl animate-fade-up" variant="outlined" hover>
          <v-card-text class="text-center">
            <v-icon icon="mdi-fire" size="26" class="mb-2 text-primary" />
            <div class="text-subtitle-2">Study Streak</div>
            <div class="text-h6 font-weight-bold mt-1">
              {{ studyStats.studyStreak }} days
            </div>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" sm="6" md="3">
        <v-card class="rounded-xl animate-fade-up" variant="outlined" hover>
          <v-card-text class="text-center">
            <v-icon icon="mdi-heart-outline" size="26" class="mb-2 text-primary" />
            <div class="text-subtitle-2">Wellness Check-ins</div>
            <div class="text-h6 font-weight-bold mt-1">
              {{ wellnessOverview.totalCheckIns }} check-ins
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Tabs -->
    <div class="tab-navigation">
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
        <v-row>
          <!-- Daily Study Time Chart -->
          <v-col cols="12" md="6">
            <v-card class="pa-4">
              <v-card-title>Daily Study Time (Last 7 Days)</v-card-title>
              <v-card-subtitle>Hours spent studying each day</v-card-subtitle>
              <apexchart
                ref="dailyStudyChart"
                type="bar"
                height="250"
                :options="dailyStudyOptions"
                :series="dailyStudySeries"
              />
            </v-card>
          </v-col>

          <!-- Study Time by Subject Chart -->
          <v-col cols="12" md="6">
            <v-card class="pa-4">
              <v-card-title>Study Time by Subject</v-card-title>
              <v-card-subtitle>Distribution of study hours</v-card-subtitle>
              <apexchart
                ref="subjectChart"
                type="donut"
                height="250"
                :options="subjectOptions"
                :series="subjectSeries"
              />
            </v-card>
          </v-col>
        </v-row>

        <v-row>
          <!-- Productivity Trend Chart -->
          <v-col cols="12">
            <v-card class="pa-4">
              <v-card-title>Productivity Trend</v-card-title>
              <v-card-subtitle>Your self-rated productivity over time</v-card-subtitle>
              <apexchart
                ref="productivityChart"
                type="line"
                height="250"
                :options="productivityOptions"
                :series="productivitySeries"
              />
            </v-card>
          </v-col>
        </v-row>
      </v-window-item>

      <v-window-item :value="1">
        <v-row>
          <!-- Task Completion Trends Chart -->
          <v-col cols="12">
            <v-card class="pa-4">
              <v-card-title>Task Completion Trends</v-card-title>
              <v-card-subtitle
                >Tasks created vs completed over the last 7 days</v-card-subtitle
              >
              <apexchart
                ref="taskChart"
                type="bar"
                height="250"
                :options="taskCompletionOptions"
                :series="taskCompletionSeries"
              />
            </v-card>
          </v-col>
        </v-row>
        <!-- Task Stats (Total Tasks, Completed, Completion Rate) -->
        <div>
          <v-row>
            <v-col>
              <v-card class="rounded-xl" elevation="0" variant="outlined">
                <v-card-text class="text-center">
                  <v-icon
                    icon="mdi-format-list-checks"
                    size="26"
                    class="mb-2 text-primary"
                  />
                  <div class="text-subtitle-2">Total Tasks</div>
                  <div class="text-h6 font-weight-bold mt-1">{{ totalTasks }}</div>
                </v-card-text>
              </v-card>
            </v-col>

            <v-col cols="12" sm="4">
              <v-card class="rounded-xl" elevation="0" variant="outlined">
                <v-card-text class="text-center">
                  <v-icon
                    icon="mdi-check-circle-outline"
                    size="26"
                    class="mb-2 text-primary"
                  />
                  <div class="text-subtitle-2">Completed</div>
                  <div class="text-h6 font-weight-bold mt-1">{{ completedTasks }}</div>
                </v-card-text>
              </v-card>
            </v-col>

            <v-col>
              <v-card class="rounded-xl" elevation="0" variant="outlined">
                <v-card-text class="text-center">
                  <v-icon icon="mdi-percent" size="26" class="mb-2 text-primary" />
                  <div class="text-subtitle-2">Completion Rate</div>
                  <div class="text-h6 font-weight-bold mt-1">{{ completionRate }}%</div>
                </v-card-text>
              </v-card>
            </v-col>
          </v-row>
        </div>
      </v-window-item>

      <v-window-item :value="2">
        <v-row>
          <!-- Wellness Trends Chart -->
          <v-col cols="12">
            <v-card class="pa-4">
              <v-card-title>Wellness Trends (Last 7 Days)</v-card-title>
              <v-card-subtitle
                >Track your mood, energy, sleep, and stress levels</v-card-subtitle
              >
              <apexchart
                ref="wellnessChart"
                type="line"
                height="250"
                :options="wellnessOptions"
                :series="wellnessSeries"
              />
            </v-card>
          </v-col>
        </v-row>

        <!-- Wellness Stats (Mood, Energy, Sleep, Stress) -->
        <v-row>
          <v-col cols="12" sm="3">
            <v-card class="rounded-xl" elevation="0" variant="outlined">
              <v-card-text class="text-center">
                <div class="text-subtitle-2">Mood</div>
                <div class="text-h6 font-weight-bold mt-1">{{ mood }}/10</div>
                <div class="text-caption text-disabled">7-day avg</div>
              </v-card-text>
            </v-card>
          </v-col>

          <v-col cols="12" sm="3">
            <v-card class="rounded-xl" elevation="0" variant="outlined">
              <v-card-text class="text-center">
                <div class="text-subtitle-2">Energy</div>
                <div class="text-h6 font-weight-bold mt-1">{{ energy }}/10</div>
                <div class="text-caption text-disabled">7-day avg</div>
              </v-card-text>
            </v-card>
          </v-col>

          <v-col cols="12" sm="3">
            <v-card class="rounded-xl" elevation="0" variant="outlined">
              <v-card-text class="text-center">
                <div class="text-subtitle-2">Sleep</div>
                <div class="text-h6 font-weight-bold mt-1">{{ sleep }}/10</div>
                <div class="text-caption text-disabled">7-day avg</div>
              </v-card-text>
            </v-card>
          </v-col>

          <v-col cols="12" sm="3">
            <v-card class="rounded-xl" elevation="0" variant="outlined">
              <v-card-text class="text-center">
                <div class="text-subtitle-2">Stress</div>
                <div class="text-h6 font-weight-bold mt-1">{{ stress }}/10</div>
                <div class="text-caption text-disabled">7-day avg</div>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
      </v-window-item>

      <v-window-item :value="3">
        <div class="insights-container">
          <div class="card mood">
            <div class="icon">😊</div>
            <div class="content">
              <h3>Mood</h3>
              <p>{{ moodInsight }}</p>
            </div>
          </div>

          <div class="card energy">
            <div class="icon">⚡</div>
            <div class="content">
              <h3>Energy</h3>
              <p>{{ energyInsight }}</p>
            </div>
          </div>

          <div class="card sleep">
            <div class="icon">🛌</div>
            <div class="content">
              <h3>Sleep</h3>
              <p>{{ sleepInsight }}</p>
            </div>
          </div>

          <div class="card stress">
            <div class="icon">😰</div>
            <div class="content">
              <h3>Stress</h3>
              <p>{{ stressInsight }}</p>
            </div>
          </div>
        </div>
      </v-window-item>
    </v-window>
  </v-container>
</template>

<script setup>
import { ref, computed, onMounted, reactive, watch, nextTick } from "vue";
import ApexCharts from "vue3-apexcharts";
import { db } from "@/lib/firebase"; // or wherever your Firebase is initialized
import {
  collection,
  query,
  where,
  orderBy,
  limit,
  getDocs,
  Timestamp,
} from "firebase/firestore";
import { auth } from "@/lib/firebase"; // if not already imported
import { api } from "@/lib/api.js";
import { useTheme } from "vuetify";

onMounted(() => {
  getTaskStats();
  getWellnessOverview();
  loadWellnessData();
  loadStudyData();
  getTaskGraph();
});

const dailyStudyChart = ref(null);
const subjectChart = ref(null);
const productivityChart = ref(null);
const taskChart = ref(null);
const wellnessChart = ref(null);

const theme = useTheme();
const isDark = computed(() => theme.global.current.value.dark);

function formatToUserTimezone(isoDate, options = {}) {
  const date = new Date(isoDate);
  return new Intl.DateTimeFormat(undefined, {
    timeZone: undefined, // user's local timezone by default
    ...options,
  }).format(date);
}

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

async function loadStudyData() {
  const user = auth.currentUser;
  if (!user) return;
  try {
    const response = await api.get("/api/study-sessions/stats");
    studyStats.studyHours = response.total_hours || 0;
    studyStats.studyStreak = response.sessions_this_month || 0;
  } catch (error) {
    console.error("Error loading study data:", error);
    studyStats.studyHours = 0;
    studyStats.studyStreak = 0;
  }
}

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

const tab = ref(0);

// ---- Dummy Data ----
// Bar chart (Daily Study Time)
const dailyStudySeries = ref([
  { name: "Study Time (mins)", data: [2, 4, 1, 0, 3, 2, 4] },
]);
const dailyStudyOptions = ref({
  ...getApexThemeOptions(isDark.value),
  chart: { toolbar: { show: false } },
  xaxis: {
    categories: ["Oct 02", "Oct 03", "Oct 04", "Oct 05", "Oct 06", "Oct 07", "Oct 08"],
  },
  colors: ["#6A7A5A"],
  dataLabels: { enabled: false },
});

// Donut chart (Study Time by Subject)
const subjectSeries = ref([30, 15, 25, 10, 20]);
const subjectOptions = ref({
  labels: ["Math", "Science", "English", "History", "Art"],
  colors: ["#6A7A5A", "#8DAF9B", "#BED2BA", "#AAC4BC", "#D7CBB2"],
  legend: { position: "bottom" },
});

// Line chart (Productivity Trend)
const productivitySeries = ref([{ name: "Productivity", data: [0, 2, 4, 3, 5, 6, 4] }]);
const productivityOptions = ref({
  ...getApexThemeOptions(isDark.value),
  chart: { toolbar: { show: false } },
  xaxis: {
    categories: ["Oct 02", "Oct 03", "Oct 04", "Oct 05", "Oct 06", "Oct 07", "Oct 08"],
  },
  yaxis: { min: 0, max: 10 },
  colors: ["#8DAF9B"],
  stroke: { curve: "smooth" },
  markers: { size: 4 },
});

// task progress
const totalTasks = computed(() => taskStat.total);
const completedTasks = computed(() => taskStat.completed);
const completionRate = computed(() =>
  totalTasks.value > 0 ? ((completedTasks.value / totalTasks.value) * 100).toFixed(1) : 0
);

const taskCompletionSeries = ref([
  { name: "Created Tasks", data: [] }, // Data for tasks created
  { name: "Completed Tasks", data: [] }, // Data for tasks completed
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
  chart: { type: "line", toolbar: { show: false } },
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

async function loadWellnessData() {
  try {
    const user = auth.currentUser;
    if (!user) return;

    const now = new Date();
    const sevenDaysAgo = new Date();
    sevenDaysAgo.setDate(now.getDate() - 6); // last 7 days

    // Query Firestore for wellness check-ins from the last 7 days
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

    // Prepare arrays for chart data and dates
    const formattedDates = [];
    const moodData = [];
    const energyData = [];
    const sleepData = [];
    const stressData = [];

    // Loop over last 7 days and fill in data or zero if missing
    for (let i = 0; i < 7; i++) {
      const date = new Date(sevenDaysAgo);
      date.setDate(sevenDaysAgo.getDate() + i);
      const dateStr = date.toLocaleDateString("en-US", {
        month: "short",
        day: "2-digit",
      });
      formattedDates.push(dateStr);

      const dayData = dataMap[dateStr] || {}; // If no data, return an empty object

      // If the data is missing, treat it as 0; if data exists, use the actual value
      moodData.push(dayData.mood !== undefined ? dayData.mood : 0);
      energyData.push(dayData.energy !== undefined ? dayData.energy : 0);
      sleepData.push(dayData.sleep !== undefined ? dayData.sleep : 0);
      stressData.push(dayData.stress !== undefined ? dayData.stress : 0);
    }

    // Update chart data & x-axis
    wellnessSeries.value = [
      { name: "Mood", data: moodData },
      { name: "Energy", data: energyData },
      { name: "Sleep", data: sleepData },
      { name: "Stress", data: stressData },
    ];
    wellnessOptions.value.xaxis.categories = formattedDates;

    // Compute 7-day averages safely (excluding zeroes that represent missing data)
    const avg = (arr) => {
      // Filter out zeroes only if they are missing data (not explicitly entered 0)
      const validData = arr.filter(
        (value) => value !== 0 || arr.indexOf(value) === arr.lastIndexOf(value)
      );
      return validData.length > 0
        ? (validData.reduce((a, b) => a + b, 0) / validData.length).toFixed(1)
        : 0;
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

// Insights
const moodInsight = computed(() => {
  if (mood.value >= 8) return "You're feeling great! Keep up the positive vibes.";
  if (mood.value >= 5) return "Your mood is stable, but there's room to improve.";
  return "Consider some self-care to boost your mood.";
});

const energyInsight = computed(() => {
  if (energy.value >= 8) return "Energy levels are high! Great job maintaining that.";
  if (energy.value >= 5) return "Your energy is decent but try to rest more.";
  return "Low energy detected—make sure you're getting enough rest.";
});

const sleepInsight = computed(() => {
  if (sleep.value >= 8) return "You're sleeping well. Keep it consistent!";
  if (sleep.value >= 5)
    return "Sleep quality is average, consider improving your bedtime routine.";
  return "Poor sleep can affect your productivity; prioritize rest.";
});

const stressInsight = computed(() => {
  if (stress.value <= 3) return "Stress levels are low—nice work managing it.";
  if (stress.value <= 6) return "Moderate stress detected, try to relax when you can.";
  return "High stress! Consider mindfulness or breaks.";
});

const insights = computed(() => [
  {
    title: "Mood",
    text: moodInsight.value,
    icon: "mdi-emoticon-happy-outline",
    colorClass:
      mood.value >= 8
        ? "insight-positive"
        : mood.value >= 5
        ? "insight-neutral"
        : "insight-negative",
  },
  {
    title: "Energy",
    text: energyInsight.value,
    icon: "mdi-battery-charging",
    colorClass:
      energy.value >= 8
        ? "insight-positive"
        : energy.value >= 5
        ? "insight-neutral"
        : "insight-negative",
  },
  {
    title: "Sleep",
    text: sleepInsight.value,
    icon: "mdi-sleep",
    colorClass:
      sleep.value >= 8
        ? "insight-positive"
        : sleep.value >= 5
        ? "insight-neutral"
        : "insight-negative",
  },
  {
    title: "Stress",
    text: stressInsight.value,
    icon: "mdi-alert-circle-outline",
    colorClass:
      stress.value <= 3
        ? "insight-positive"
        : stress.value <= 6
        ? "insight-neutral"
        : "insight-negative",
  },
]);
watch(isDark, async (newVal) => {
  const themeOptions = getApexThemeOptions(newVal);
  await nextTick();

  const charts = [
    dailyStudyChart,
    subjectChart,
    productivityChart,
    taskChart,
    wellnessChart,
  ];

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
            categories: preservedCategories, // ✅ keep labels safe
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
});
</script>

<style scoped>
.text-muted {
  color: var(--text-muted);
}

.main-content {
  padding: 32px;
  background-color: var(--background);
  max-width: 1200px;
  margin: 0 auto;
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

.insights-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 32px 24px 24px 24px;
  /* padding with extra top */
  border-radius: 16px;
  border: 1.5px solid #d1d5db;
  width: 100%;
  box-sizing: border-box;
  margin-top: 16px;
  /* space between tab and container */
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
  font-size: 30px;
  margin-right: 16px;
  flex-shrink: 0;
  line-height: 1;
  margin-top: 4px;
}

/* Content inside the card */
.content h3 {
  margin: 0 0 4px 0;
  font-size: 17px;
  font-weight: 600;
  color: #333;
}

.content p {
  margin: 0;
  font-size: 14px;
  color: #555;
  line-height: 1.4;
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

/* Responsive adjustments */
@media (max-width: 600px) {
  .stat-card {
    padding: 20px 12px;
    border-radius: 12px;
  }
}
</style>
