<template>
  <v-container class="py-8 main-content">
    <div>
      <h1 class="text-h5 text-primary font-weight-bold mb-1">Progress Analytics</h1>
      <p class="text-body-2 text-muted mb-4">Track your academic and wellness journey</p>
    </div>

    <!-- Stats Section -->
    <v-row dense class="mb-4">
      <v-col cols="12" sm="6" md="3">
        <v-card class="rounded-xl" elevation="0" variant="outlined">
          <v-card-text class="text-center">
            <v-icon icon="mdi-clock-time-four-outline" size="26" class="mb-2 text-primary" />
            <div class="text-subtitle-2">Study Hours</div>
            <div class="text-h6 font-weight-bold mt-1">1h 25m</div>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" sm="6" md="3">
        <v-card class="rounded-xl" elevation="0" variant="outlined">
          <v-card-text class="text-center">
            <v-icon icon="mdi-target" size="26" class="mb-2 text-primary" />
            <div class="text-subtitle-2">Tasks Completed</div>
            <div class="text-h6 font-weight-bold mt-1">67%</div>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" sm="6" md="3">
        <v-card class="rounded-xl" elevation="0" variant="outlined">
          <v-card-text class="text-center">
            <v-icon icon="mdi-fire" size="26" class="mb-2 text-primary" />
            <div class="text-subtitle-2">Study Streak</div>
            <div class="text-h6 font-weight-bold mt-1">5 days</div>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" sm="6" md="3">
        <v-card class="rounded-xl" elevation="0" variant="outlined">
          <v-card-text class="text-center">
            <v-icon icon="mdi-heart-outline" size="26" class="mb-2 text-primary" />
            <div class="text-subtitle-2">Wellness Check-ins</div>
            <div class="text-h6 font-weight-bold mt-1">0 check-ins</div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
    <!-- Tabs -->
    <div class="tab-navigation">
      <!-- const tabs = ["Study Analytics", "Task Progress", "Wellness Trends", "Insights"]; -->
      <div class="tab-item" :class="{ active: tab === 0 }" @click="tab = 0">Study Analytics</div>
      <div class="tab-item" :class="{ active: tab === 1 }" @click="tab = 1">Task Progress</div>
      <div class="tab-item" :class="{ active: tab === 2 }" @click="tab = 2">Wellness Trends</div>
      <div class="tab-item" :class="{ active: tab === 3 }" @click="tab = 3">Insights</div>

      <!-- 
      <button v-for="tab in tabs" :key="tab" :class="['tab-item', { active: activeTab === tab }]"
        @click="activeTab = tab">
        {{ tab }}
      </button> -->
    </div>


    <v-window v-model="tab" :transition="false" :touch="false">
      <v-window-item :value="0">
        <v-row>
          <!-- Daily Study Time Chart -->
          <v-col cols="12" md="6">
            <v-card class="pa-4">
              <v-card-title>Daily Study Time (Last 7 Days)</v-card-title>
              <v-card-subtitle>Hours spent studying each day</v-card-subtitle>
              <apexchart type="bar" height="250" :options="dailyStudyOptions" :series="dailyStudySeries" />
            </v-card>
          </v-col>

          <!-- Study Time by Subject Chart -->
          <v-col cols="12" md="6">
            <v-card class="pa-4">
              <v-card-title>Study Time by Subject</v-card-title>
              <v-card-subtitle>Distribution of study hours</v-card-subtitle>
              <apexchart type="donut" height="250" :options="subjectOptions" :series="subjectSeries" />
            </v-card>
          </v-col>
        </v-row>

        <v-row>
          <!-- Productivity Trend Chart -->
          <v-col cols="12">
            <v-card class="pa-4">
              <v-card-title>Productivity Trend</v-card-title>
              <v-card-subtitle>Your self-rated productivity over time</v-card-subtitle>
              <apexchart type="line" height="250" :options="productivityOptions" :series="productivitySeries" />
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
              <v-card-subtitle>Tasks created vs completed over the last 7 days</v-card-subtitle>
              <apexchart type="bar" height="250" :options="taskCompletionOptions" :series="taskCompletionSeries" />
            </v-card>
          </v-col>
        </v-row>
        <!-- Task Stats (Total Tasks, Completed, Completion Rate) -->
        <div>
          <v-row>
            <v-col>
              <v-card class="rounded-xl" elevation="0" variant="outlined">
                <v-card-text class="text-center">
                  <v-icon icon="mdi-format-list-checks" size="26" class="mb-2 text-primary" />
                  <div class="text-subtitle-2">Total Tasks</div>
                  <div class="text-h6 font-weight-bold mt-1">{{ totalTasks }}</div>
                </v-card-text>
              </v-card>
            </v-col>

            <v-col cols="12" sm="4">
              <v-card class="rounded-xl" elevation="0" variant="outlined">
                <v-card-text class="text-center">
                  <v-icon icon="mdi-check-circle-outline" size="26" class="mb-2 text-primary" />
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
              <v-card-subtitle>Track your mood, energy, sleep, and stress levels</v-card-subtitle>
              <apexchart type="line" height="250" :options="wellnessOptions" :series="wellnessSeries" />
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
import { ref, computed } from "vue";
import ApexCharts from "vue3-apexcharts";

const tab = ref(0)

const studyProgress = ref(80);
const taskComplete = ref(20);
const studyStreak = ref(40);
const checkIn = ref(60);

const activeTab = ref("Study Analytics");
const tabs = ["Study Analytics", "Task Progress", "Wellness Trends", "Insights"];

// ---- Dummy Data ----
// Bar chart (Daily Study Time)
const dailyStudySeries = ref([
  { name: "Study Time (mins)", data: [2, 4, 1, 0, 3, 2, 4] },
]);
const dailyStudyOptions = ref({
  chart: { toolbar: { show: false } },
  xaxis: {
    categories: ["Oct 02", "Oct 03", "Oct 04", "Oct 05", "Oct 06", "Oct 07", "Oct 08"],
  },
  colors: ["#6A7A5A"],
  grid: { borderColor: "#eee" },
  dataLabels: {
    enabled: false, // Disable the data labels on top of bars
  },
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
  chart: { toolbar: { show: false } },
  xaxis: {
    categories: ["Oct 02", "Oct 03", "Oct 04", "Oct 05", "Oct 06", "Oct 07", "Oct 08"],
  },
  yaxis: { min: 0, max: 10 },
  colors: ["#8DAF9B"],
  stroke: { curve: "smooth" },
  markers: { size: 4 },
  grid: { borderColor: "#eee" },
});

// task progress

// Sample data for Task Completion
const totalTasks = ref(10); // Total number of tasks
const completedTasks = ref(6); // Completed tasks
const completionRate = ref(((completedTasks.value / totalTasks.value) * 100).toFixed(2)); // Completion rate calculation

// Task Completion Trends Bar Chart (Created vs Completed)
const taskCompletionSeries = ref([
  { name: "Created Tasks", data: [2, 3, 1, 2, 4, 3, 2] }, // Example data for tasks created
  { name: "Completed Tasks", data: [1, 2, 1, 1, 2, 3, 1] }, // Example data for tasks completed
]);

const taskCompletionOptions = ref({
  chart: {
    type: "bar",
    toolbar: { show: false },
  },
  xaxis: {
    categories: ["Oct 02", "Oct 03", "Oct 04", "Oct 05", "Oct 06", "Oct 07", "Oct 08"],
  },
  yaxis: {
    min: 0,
  },
  colors: ["#4CAF50", "#FF7043"], // Green for created, red for completed
  grid: { borderColor: "#eee" },
  dataLabels: { enabled: false },
});

// Dummy Data for Wellness Trends (Mood, Energy, Sleep, Stress)
const wellnessSeries = ref([
  { name: "Mood", data: [7, 6, 8, 7, 9, 6, 8] },
  { name: "Energy", data: [6, 5, 7, 6, 8, 7, 6] },
  { name: "Sleep", data: [8, 7, 8, 7, 8, 7, 7] },
  { name: "Stress", data: [4, 5, 3, 4, 3, 2, 4] },
]);

const wellnessOptions = ref({
  chart: {
    type: "line",
    toolbar: { show: false },
  },
  xaxis: {
    categories: ["Oct 02", "Oct 03", "Oct 04", "Oct 05", "Oct 06", "Oct 07", "Oct 08"],
  },
  yaxis: {
    min: 0,
    max: 10,
  },
  stroke: {
    width: 2,
    curve: "smooth",
  },
  markers: {
    size: 4,
  },
  grid: {
    borderColor: "#eee",
  },
  colors: ["#FF7043", "#42A5F5", "#8DAF9B", "#FFD54F"], // Custom colors for each trend
});

// Dummy Data for Wellness Stats (Mood, Energy, Sleep, Stress)
const mood = ref(7);
const energy = ref(6);
const sleep = ref(7);
const stress = ref(4);

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
  content: '';
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
</style>
