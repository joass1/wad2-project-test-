<template>
  <v-container
    fluid
    class="pa-8"
    style="min-height: 100vh; background: var(--background)"
  >
    <!-- Header -->
    <v-card
      class="mb-6"
      elevation="0"
      rounded="lg"
      style="background: var(--surface)"
    >
      <v-card-text class="pa-6">
        <div class="d-flex justify-space-between align-center">
          <div>
            <h1
              class="text-h5 font-weight-regular mb-1"
              style="color: var(--primary)"
            >
              Task Tracker
            </h1>
            <p class="text-body-2" style="color: var(--text-muted)">
              Manage your assignments and deadlines
            </p>
          </div>
          <v-btn
            elevation="0"
            rounded="lg"
            class="text-none"
            style="
              background: var(--primary);
              color: white;
              text-transform: none;
            "
            @click="showAddTask = true"
          >
            <v-icon size="small" class="mr-1">mdi-plus</v-icon>
            Add Task
          </v-btn>
        </div>
      </v-card-text>
    </v-card>

    <v-alert
      v-if="errorMessage"
      type="error"
      variant="tonal"
      color="error"
      class="mb-4"
    >
      {{ errorMessage }}
    </v-alert>

    <v-progress-linear
      v-if="loading"
      indeterminate
      color="primary"
      class="mb-4"
    ></v-progress-linear>

    <!-- Stats Dashboard -->
    <v-row class="mb-6">
      <v-col cols="3">
        <v-card elevation="0" rounded="lg" style="background: var(--surface)">
          <v-card-text class="pa-6 text-center">
            <div
              class="text-h4 font-weight-regular mb-1"
              style="color: var(--text-primary)"
            >
              {{ stats.total }}
            </div>
            <div class="text-caption" style="color: var(--text-muted)">
              Total Tasks
            </div>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="3">
        <v-card
          elevation="0"
          rounded="lg"
          style="background: var(--surface-light)"
        >
          <v-card-text class="pa-6 text-center">
            <div
              class="text-h4 font-weight-regular mb-1"
              style="color: var(--primary)"
            >
              {{ stats.completed }}
            </div>
            <div class="text-caption" style="color: var(--text-muted)">
              Completed
            </div>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="3">
        <v-card
          elevation="0"
          rounded="lg"
          style="background: var(--surface-light)"
        >
          <v-card-text class="pa-6 text-center">
            <div
              class="text-h4 font-weight-regular mb-1"
              style="color: var(--info)"
            >
              {{ stats.dueToday }}
            </div>
            <div class="text-caption" style="color: var(--text-muted)">
              Due Today
            </div>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="3">
        <v-card
          elevation="0"
          rounded="lg"
          style="background: var(--surface-light)"
        >
          <v-card-text class="pa-6 text-center">
            <div
              class="text-h4 font-weight-regular mb-1"
              style="color: var(--error)"
            >
              {{ stats.overdue }}
            </div>
            <div class="text-caption" style="color: var(--text-muted)">
              Overdue
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- View Controls -->
    <v-card
      class="mb-6"
      elevation="0"
      rounded="lg"
      style="background: var(--surface)"
    >
      <v-card-text class="pa-4">
        <v-row align="center" no-gutters>
          <v-col cols="auto">
            <v-btn-toggle
              v-model="view"
              mandatory
              variant="text"
              density="comfortable"
              style="background: transparent"
            >
              <v-btn
                value="board"
                class="text-none"
                style="text-transform: none; color: var(--text-muted)"
                >Board</v-btn
              >
              <v-btn
                value="list"
                class="text-none"
                style="text-transform: none; color: var(--text-muted)"
                >List</v-btn
              >
              <v-btn
                value="upcoming"
                class="text-none"
                style="text-transform: none; color: var(--text-muted)"
                >Upcoming</v-btn
              >
            </v-btn-toggle>
          </v-col>
          <v-spacer></v-spacer>
          <v-col cols="auto" class="d-flex ga-3">
            <v-select
              v-model="filterStatus"
              :items="statusOptions"
              label="Status"
              density="compact"
              variant="outlined"
              hide-details
              style="width: 140px; font-size: 0.875rem"
            ></v-select>
            <v-select
              v-model="filterPriority"
              :items="priorityOptions"
              label="Priority"
              density="compact"
              variant="outlined"
              hide-details
              style="width: 140px; font-size: 0.875rem"
            ></v-select>
            <v-select
              v-model="sortBy"
              :items="sortOptions"
              label="Sort by"
              density="compact"
              variant="outlined"
              hide-details
              style="width: 160px; font-size: 0.875rem"
            ></v-select>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>

    <!-- Board View -->
    <v-row v-if="view === 'board'">
      <v-col
        v-for="status in ['todo', 'inProgress', 'done']"
        :key="status"
        cols="4"
      >
        <v-card
          elevation="0"
          rounded="lg"
          style="background: var(--surface-light)"
        >
          <v-card-text class="pa-5">
            <div class="d-flex justify-space-between align-center mb-4">
              <h3
                class="text-body-1 font-weight-regular"
                style="color: var(--text-secondary)"
              >
                {{ getStatusLabel(status) }}
              </h3>
              <span class="text-caption" style="color: var(--text-muted)">
                {{
                  getFilteredTasks().filter((t) => t.status === status).length
                }}
              </span>
            </div>
            <div style="min-height: 400px">
              <v-card
                v-for="task in getFilteredTasks().filter(
                  (t) => t.status === status
                )"
                :key="task.id"
                class="mb-3"
                elevation="0"
                rounded="lg"
                :style="
                  isOverdue(task)
                    ? 'background: rgba(220, 38, 38, 0.05); border-left: 4px solid var(--error);'
                    : 'background: var(--surface);'
                "
              >
                <v-card-text class="pa-4">
                  <div class="d-flex justify-space-between align-start mb-2">
                    <div class="text-body-2" style="color: var(--text-primary)">
                      {{ task.title }}
                    </div>
                    <v-btn
                      icon
                      size="x-small"
                      variant="text"
                      @click="handleDeleteTask(task.id)"
                      style="color: var(--text-disabled)"
                    >
                      <v-icon size="16">mdi-close</v-icon>
                    </v-btn>
                  </div>
                  <div class="d-flex flex-wrap ga-2 mb-3">
                    <span
                      class="px-2 py-1 text-caption rounded"
                      :style="getPriorityStyle(task.priority)"
                    >
                      {{ task.priority }}
                    </span>
                    <span
                      class="text-caption"
                      style="color: var(--text-muted)"
                      >{{ task.category }}</span
                    >
                    <span
                      v-if="isOverdue(task)"
                      class="px-2 py-1 text-caption rounded font-weight-medium"
                      style="
                        background-color: rgba(220, 38, 38, 0.1);
                        color: var(--error);
                      "
                    >
                      OVERDUE
                    </span>
                  </div>
                  <div class="d-flex align-center mb-3">
                    <v-icon
                      size="14"
                      class="mr-1"
                      :style="
                        isOverdue(task)
                          ? 'color: var(--error);'
                          : 'color: var(--text-muted);'
                      "
                      >mdi-calendar-blank</v-icon
                    >
                    <span
                      class="text-caption"
                      :style="
                        isOverdue(task)
                          ? 'color: var(--error); font-weight: 500;'
                          : 'color: var(--text-muted);'
                      "
                      >{{ formatDate(task.dueDate) }}</span
                    >
                  </div>
                  <v-select
                    :model-value="task.status"
                    @update:model-value="handleStatusChange(task.id, $event)"
                    :items="statusSelectItems"
                    density="compact"
                    variant="outlined"
                    hide-details
                    style="font-size: 0.875rem"
                  ></v-select>
                </v-card-text>
              </v-card>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- List View -->
    <v-card
      v-if="view === 'list'"
      elevation="0"
      rounded="lg"
      style="background: var(--surface)"
    >
      <v-card-text class="pa-6">
        <h2
          class="text-body-1 font-weight-regular mb-4"
          style="color: var(--text-secondary)"
        >
          Your Tasks ({{ getFilteredTasks().length }})
        </h2>
        <div>
          <v-card
            v-for="task in getFilteredTasks()"
            :key="task.id"
            class="mb-3"
            elevation="0"
            rounded="lg"
            :style="
              isOverdue(task)
                ? 'background: rgba(220, 38, 38, 0.05); border-left: 4px solid var(--error);'
                : 'background: var(--surface-light);'
            "
          >
            <v-card-text class="pa-4">
              <div class="d-flex justify-space-between align-start mb-2">
                <div class="text-body-2" style="color: var(--text-primary)">
                  {{ task.title }}
                </div>
                <v-btn
                  icon
                  size="x-small"
                  variant="text"
                  @click="handleDeleteTask(task.id)"
                  style="color: var(--text-disabled)"
                >
                  <v-icon size="16">mdi-close</v-icon>
                </v-btn>
              </div>
              <div class="d-flex flex-wrap ga-2 mb-3">
                <span
                  class="px-2 py-1 text-caption rounded"
                  :style="getPriorityStyle(task.priority)"
                >
                  {{ task.priority }}
                </span>
                <span class="text-caption" style="color: var(--text-muted)">{{
                  task.category
                }}</span>
                <span
                  v-if="isOverdue(task)"
                  class="px-2 py-1 text-caption rounded font-weight-medium"
                  style="
                    background-color: rgba(220, 38, 38, 0.1);
                    color: var(--error);
                  "
                >
                  OVERDUE
                </span>
                <span
                  class="text-caption d-flex align-center"
                  :style="
                    isOverdue(task)
                      ? 'color: var(--error); font-weight: 500;'
                      : 'color: var(--text-muted);'
                  "
                >
                  <v-icon
                    size="14"
                    class="mr-1"
                    :style="isOverdue(task) ? 'color: var(--error);' : ''"
                    >mdi-calendar-blank</v-icon
                  >
                  {{ formatDate(task.dueDate) }}
                </span>
              </div>
              <v-select
                :model-value="task.status"
                @update:model-value="handleStatusChange(task.id, $event)"
                :items="statusSelectItems"
                density="compact"
                variant="outlined"
                hide-details
                style="font-size: 0.875rem"
              ></v-select>
            </v-card-text>
          </v-card>
          <div
            v-if="!loading && getFilteredTasks().length === 0"
            class="text-center py-8 text-body-2"
            style="color: var(--text-muted)"
          >
            No tasks found. Add your first task!
          </div>
        </div>
      </v-card-text>
    </v-card>

    <!-- Upcoming View -->
    <div v-if="view === 'upcoming'">
      <h2
        class="text-h5 font-weight-regular mb-6"
        style="color: var(--text-primary)"
      >
        Upcoming
      </h2>
      <v-card
        v-for="[key, groupTasks] in Object.entries(getUpcomingTasks())"
        :key="key"
        class="mb-4"
        elevation="0"
        rounded="lg"
        style="background: var(--surface)"
      >
        <v-card-text class="pa-6">
          <div class="d-flex align-center ga-2 mb-4">
            <h3
              class="text-body-1 font-weight-regular"
              :style="{
                color:
                  key === 'overdue' ? 'var(--error)' : 'var(--text-secondary)',
              }"
            >
              {{ getGroupLabel(key) }}
            </h3>
            <span class="text-caption" style="color: var(--text-muted)">{{
              groupTasks.length
            }}</span>
          </div>
          <div>
            <v-card
              v-for="task in groupTasks"
              :key="task.id"
              class="mb-3"
              elevation="0"
              rounded="lg"
              :style="
                isOverdue(task)
                  ? 'background: rgba(220, 38, 38, 0.05); border-left: 4px solid var(--error);'
                  : 'background: var(--surface-light);'
              "
            >
              <v-card-text class="pa-4">
                <div class="d-flex justify-space-between align-start mb-2">
                  <div class="text-body-2" style="color: var(--text-primary)">
                    {{ task.title }}
                  </div>
                  <v-btn
                    icon
                    size="x-small"
                    variant="text"
                    @click="handleDeleteTask(task.id)"
                    style="color: var(--text-disabled)"
                  >
                    <v-icon size="16">mdi-close</v-icon>
                  </v-btn>
                </div>
                <div class="d-flex flex-wrap ga-2 mb-3">
                  <span
                    class="px-2 py-1 text-caption rounded"
                    :style="getPriorityStyle(task.priority)"
                  >
                    {{ task.priority }}
                  </span>
                  <span class="text-caption" style="color: var(--text-muted)">{{
                    task.category
                  }}</span>
                  <span
                    v-if="isOverdue(task)"
                    class="px-2 py-1 text-caption rounded font-weight-medium"
                    style="
                      background-color: rgba(220, 38, 38, 0.1);
                      color: var(--error);
                    "
                  >
                    OVERDUE
                  </span>
                  <span
                    class="text-caption d-flex align-center"
                    :style="
                      isOverdue(task)
                        ? 'color: var(--error); font-weight: 500;'
                        : 'color: var(--text-muted);'
                    "
                  >
                    <v-icon
                      size="14"
                      class="mr-1"
                      :style="isOverdue(task) ? 'color: var(--error);' : ''"
                      >mdi-calendar-blank</v-icon
                    >
                    {{ formatDate(task.dueDate) }}
                  </span>
                </div>
                <v-select
                  :model-value="task.status"
                  @update:model-value="handleStatusChange(task.id, $event)"
                  :items="statusSelectItems"
                  density="compact"
                  variant="outlined"
                  hide-details
                  style="font-size: 0.875rem"
                ></v-select>
              </v-card-text>
            </v-card>
          </div>
        </v-card-text>
      </v-card>
    </div>

    <!-- Add Task Dialog -->
    <v-dialog v-model="showAddTask" max-width="500">
      <v-card rounded="lg" elevation="0" style="background: var(--surface)">
        <v-card-title class="pa-5">
          <h2
            class="text-h6 font-weight-regular"
            style="color: var(--text-primary)"
          >
            Add New Task
          </h2>
        </v-card-title>
        <v-card-text class="px-5 pb-5">
          <v-text-field
            v-model="newTask.title"
            label="Task title"
            variant="outlined"
            density="compact"
            class="mb-3"
            hide-details
          ></v-text-field>
          <v-select
            v-model="newTask.status"
            :items="statusSelectItems"
            label="Status"
            variant="outlined"
            density="compact"
            class="mb-3"
            hide-details
          ></v-select>
          <v-select
            v-model="newTask.priority"
            :items="prioritySelectItems"
            label="Priority"
            variant="outlined"
            density="compact"
            class="mb-3"
            hide-details
          ></v-select>
          <v-text-field
            v-model="newTask.dueDate"
            label="Due date"
            type="date"
            variant="outlined"
            density="compact"
            class="mb-3"
            hide-details
          ></v-text-field>
          <v-text-field
            v-model="newTask.category"
            label="Category"
            variant="outlined"
            density="compact"
            hide-details
          ></v-text-field>
        </v-card-text>
        <v-card-actions class="px-5 pb-5">
          <v-spacer></v-spacer>
          <v-btn
            @click="showAddTask = false"
            variant="text"
            class="text-none"
            style="color: var(--text-muted); text-transform: none"
          >
            Cancel
          </v-btn>
          <v-btn
            @click="handleAddTask"
            elevation="0"
            rounded="lg"
            class="text-none"
            style="
              background: var(--primary);
              color: white;
              text-transform: none;
            "
          >
            Add Task
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup>
import { onMounted, ref, watch } from "vue";
import { api } from "@/lib/api.js";

const view = ref("board");
const showAddTask = ref(false);
const filterStatus = ref("all");
const filterPriority = ref("all");
const sortBy = ref("dueDate");

const statusOptions = ["all", "todo", "inProgress", "done"];
const priorityOptions = ["all", "high", "medium", "low"];
const sortOptions = [
  { title: "Sort by Due Date", value: "dueDate" },
  { title: "Sort by Priority", value: "priority" },
];

const statusSelectItems = [
  { title: "To Do", value: "todo" },
  { title: "In Progress", value: "inProgress" },
  { title: "Done", value: "done" },
];

const prioritySelectItems = [
  { title: "High Priority", value: "high" },
  { title: "Medium Priority", value: "medium" },
  { title: "Low Priority", value: "low" },
];

const tasks = ref([]);
const stats = ref({ total: 0, completed: 0, dueToday: 0, overdue: 0 });
const loading = ref(false);
const errorMessage = ref("");

const newTaskDefaults = {
  title: "",
  status: "todo",
  priority: "medium",
  dueDate: "",
  category: "General",
};
const newTask = ref({ ...newTaskDefaults });

// handle race condition
let fetchToken = 0;

const fetchTasks = async () => {
  const token = ++fetchToken;
  loading.value = true;
  errorMessage.value = "";
  try {
    const params = new URLSearchParams();
    if (filterStatus.value !== "all") {
      params.append("status", filterStatus.value);
    }
    if (filterPriority.value !== "all") {
      params.append("priority", filterPriority.value);
    }
    params.append("sortBy", sortBy.value);

    const query = params.toString();
    const response = await api.get(`/api/tasks${query ? `?${query}` : ""}`);

    if (token !== fetchToken) return;

    tasks.value = Array.isArray(response.tasks) ? response.tasks : [];
    const responseStats = response.stats ?? {};
    stats.value = {
      total: responseStats.total ?? 0,
      completed: responseStats.completed ?? 0,
      dueToday: responseStats.dueToday ?? 0,
      overdue: responseStats.overdue ?? 0,
    };
  } catch (error) {
    if (token === fetchToken) {
      errorMessage.value = error.message || "Failed to load tasks";
      tasks.value = [];
      stats.value = { total: 0, completed: 0, dueToday: 0, overdue: 0 };
    }
  } finally {
    if (token === fetchToken) {
      loading.value = false;
    }
  }
};

onMounted(fetchTasks);

watch([filterStatus, filterPriority, sortBy], () => {
  fetchTasks();
});

const getFilteredTasks = () => tasks.value;

// get upcoming tasks
const getUpcomingTasks = () => {
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const grouped = {};

  getFilteredTasks()
    .filter((task) => task.status !== "done")
    .forEach((task) => {
      if (!task.dueDate) return;
      const taskDate = new Date(task.dueDate);
      if (Number.isNaN(taskDate.getTime())) return;

      const diff = Math.floor((taskDate - today) / (1000 * 60 * 60 * 24));
      let key;
      if (diff < 0) key = "overdue";
      else if (diff === 0) key = "today";
      else if (diff === 1) key = "tomorrow";
      else key = task.dueDate;

      if (!grouped[key]) grouped[key] = [];
      grouped[key].push(task);
    });

  return grouped;
};

// add task
const handleAddTask = async () => {
  if (!newTask.value.title.trim()) {
    return;
  }

  const payload = {
    title: newTask.value.title.trim(),
    status: newTask.value.status,
    priority: newTask.value.priority,
    dueDate: newTask.value.dueDate || null,
    category: newTask.value.category || "General",
  };

  try {
    loading.value = true;
    await api.post("/api/tasks/add-task", payload);
    showAddTask.value = false;
    newTask.value = { ...newTaskDefaults };
    await fetchTasks();
  } catch (error) {
    errorMessage.value = error.message || "Failed to add task";
  } finally {
    loading.value = false;
  }
};

// delete task
const handleDeleteTask = async (id) => {
  try {
    loading.value = true;
    await api.del(`/api/tasks/${id}`);
    await fetchTasks();
  } catch (error) {
    errorMessage.value = error.message || "Failed to delete task";
  } finally {
    loading.value = false;
  }
};

// update task status
const handleStatusChange = async (id, newStatus) => {
  if (!newStatus) return;
  const existing = tasks.value.find((task) => task.id === id);
  if (existing && existing.status === newStatus) return;
  try {
    await api.patch(`/api/tasks/${id}`, { status: newStatus });
    await fetchTasks();
  } catch (error) {
    errorMessage.value = error.message || "Failed to update task";
  }
};

const getPriorityStyle = (priority) => {
  const styles = {
    high: "background-color: rgba(220, 38, 38, 0.1); color: var(--error);",
    medium: "background-color: rgba(201, 169, 89, 0.1); color: var(--warning);",
    low: "background-color: rgba(141, 175, 155, 0.15); color: var(--success);",
  };
  return styles[priority];
};

const getStatusLabel = (status) => {
  const labels = {
    todo: "To Do",
    inProgress: "In Progress",
    done: "Done",
  };
  return labels[status];
};

const getGroupLabel = (key) => {
  if (key === "overdue") return "Overdue";
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  if (key === "today") {
    return `${today.toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
    })} · Today`;
  }
  if (key === "tomorrow") {
    const tomorrow = new Date(today);
    tomorrow.setDate(tomorrow.getDate() + 1);
    return `${tomorrow.toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
    })} · Tomorrow`;
  }
  const date = new Date(key);
  if (Number.isNaN(date.getTime())) return key;
  return date.toLocaleDateString("en-US", { month: "short", day: "numeric" });
};

const formatDate = (dateString) => {
  if (!dateString) return "No due date";
  const date = new Date(dateString);
  if (Number.isNaN(date.getTime())) return "No due date";
  return date.toLocaleDateString("en-US", { month: "short", day: "numeric" });
};

const isOverdue = (task) => {
  if (!task?.dueDate) return false;
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const dueDate = new Date(task.dueDate);
  dueDate.setHours(0, 0, 0, 0);
  return dueDate < today && task.status !== "done";
};
</script>
