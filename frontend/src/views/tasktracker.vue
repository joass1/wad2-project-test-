<template>
  <v-container
    fluid
    class="task-container py-4 py-md-8 px-2 px-md-8"
    style="min-height: 100vh; background: var(--background)"
  >
    <!-- Header -->
    <v-card
      class="mb-4 mb-md-6 mx-0"
      elevation="0"
      rounded="xl"
      style="background: var(--surface)"
    >
      <v-card-text class="pa-4 pa-md-6">
        <div class="d-flex flex-column flex-md-row justify-space-between align-start align-md-center ga-3">
          <div>
            <h1 class="text-h6 text-md-h5 text-primary font-weight-bold mb-1 px-2 px-md-0">
              Task Tracker
            </h1>
            <p class="text-caption text-md-body-2" style="color: var(--text-muted)">
              Manage your assignments and deadlines
            </p>
          </div>
          <v-btn
            elevation="0"
            rounded="lg"
            class="text-none add-task-btn"
            size="default"
            size-md="default"
            style="
              background: var(--primary);
              color: white;
              text-transform: none;
            "
            @click="openAddTaskDialog"
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
    <v-row class="mb-4 mb-md-6" dense>
      <v-col cols="6" sm="3">
        <v-card elevation="0" rounded="xl" style="background: var(--surface)" class="stat-card">
          <v-card-text class="pa-4 pa-md-6 text-center">
            <div
              class="text-h5 text-md-h4 font-weight-medium mb-1"
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
      <v-col cols="6" sm="3">
        <v-card
          elevation="0"
          rounded="xl"
          style="background: var(--surface-light)"
          class="stat-card"
        >
          <v-card-text class="pa-4 pa-md-6 text-center">
            <div
              class="text-h5 text-md-h4 font-weight-medium mb-1"
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
      <v-col cols="6" sm="3">
        <v-card
          elevation="0"
          rounded="xl"
          style="background: var(--surface-light)"
          class="stat-card"
        >
          <v-card-text class="pa-4 pa-md-6 text-center">
            <div
              class="text-h5 text-md-h4 font-weight-medium mb-1"
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
      <v-col cols="6" sm="3">
        <v-card
          elevation="0"
          rounded="xl"
          style="background: var(--surface-light)"
          class="stat-card"
        >
          <v-card-text class="pa-4 pa-md-6 text-center">
            <div
              class="text-h5 text-md-h4 font-weight-medium mb-1"
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
      class="mb-4 mb-md-6 mx-0"
      elevation="0"
      rounded="xl"
      style="background: var(--surface)"
    >
      <v-card-text class="pa-4 pa-md-6">
        <div class="mb-4 mb-md-0">
          <v-btn-toggle
            v-model="view"
            mandatory
            variant="text"
            density="comfortable"
            class="view-toggle"
            style="background: transparent"
          >
            <v-btn
              value="board"
              class="text-none"
              size="small"
              size-md="default"
              style="text-transform: none; color: var(--text-muted)"
              >Board</v-btn
            >
            <v-btn
              value="list"
              class="text-none"
              size="small"
              size-md="default"
              style="text-transform: none; color: var(--text-muted)"
              >List</v-btn
            >
            <v-btn
              value="upcoming"
              class="text-none"
              size="small"
              size-md="default"
              style="text-transform: none; color: var(--text-muted)"
              >Upcoming</v-btn
            >
          </v-btn-toggle>
        </div>
        <div class="d-flex flex-column flex-md-row ga-3">
          <v-select
            v-model="filterStatus"
            :items="statusOptions"
            label="Status"
            density="compact"
            variant="outlined"
            hide-details
            class="filter-select"
            style="font-size: 0.875rem"
          ></v-select>
          <v-select
            v-model="filterPriority"
            :items="priorityOptions"
            label="Priority"
            density="compact"
            variant="outlined"
            hide-details
            class="filter-select"
            style="font-size: 0.875rem"
          ></v-select>
          <v-select
            v-model="sortBy"
            :items="sortOptions"
            label="Sort by"
            density="compact"
            variant="outlined"
            hide-details
            class="filter-select"
            style="font-size: 0.875rem"
          ></v-select>
        </div>
      </v-card-text>
    </v-card>

    <!-- Board View -->
    <v-row v-if="view === 'board'" class="mx-0">
      <v-col
        v-for="status in ['todo', 'inProgress', 'done']"
        :key="status"
        cols="12"
        sm="12"
        md="6"
        lg="4"
      >
        <v-card
          elevation="0"
          rounded="xl"
          style="background: var(--surface-light)"
          class="mb-4 mb-md-0"
        >
          <v-card-text class="pa-4 pa-md-5">
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
            <div class="board-column">
              <v-card
                v-for="task in getFilteredTasks().filter(
                  (t) => t.status === status
                )"
                :key="task.id"
                class="mb-3"
                elevation="0"
                rounded="xl"
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
                    <div class="d-flex align-center ga-1">
                      <v-btn
                        icon
                        size="x-small"
                        variant="text"
                        @click="startEditTask(task)"
                        style="color: var(--text-muted)"
                        :aria-label="`Edit ${task.title}`"
                      >
                        <svg
                          class="task-action-icon"
                          viewBox="0 0 24 24"
                          fill="none"
                          stroke="currentColor"
                          stroke-width="2"
                        >
                          <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7" />
                          <path
                            d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"
                          />
                        </svg>
                      </v-btn>
                      <v-btn
                        icon
                        size="x-small"
                        variant="text"
                        @click="handleDeleteTask(task.id)"
                        style="color: var(--text-disabled)"
                        :aria-label="`Delete ${task.title}`"
                      >
                        <v-icon size="16">mdi-close</v-icon>
                      </v-btn>
                    </div>
                  </div>
                  <div class="d-flex flex-wrap ga-2 mb-3">
                    <span
                      class="task-chip px-2 py-1 text-caption rounded"
                      :style="getPriorityStyle(task.priority)"
                    >
                      {{ task.priority }}
                    </span>
                    <span
                      class="task-chip px-2 py-1 text-caption"
                      style="color: var(--text-muted)"
                      >{{ task.category }}</span
                    >
                    <span
                      v-if="task.totalStudyMinutes > 0"
                      class="task-chip px-2 py-1 text-caption rounded"
                      style="background-color: rgba(76, 175, 80, 0.1); color: var(--success);"
                    >
                      {{ Math.floor(task.totalStudyMinutes / 60) }}h {{ task.totalStudyMinutes % 60 }}m studied
                    </span>
                    <span
                      v-if="isOverdue(task)"
                      class="task-chip px-2 py-1 text-caption rounded font-weight-medium"
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
      rounded="xl"
      style="background: var(--surface)"
      class="mx-0"
    >
      <v-card-text class="pa-4 pa-md-6">
        <h2
          class="text-subtitle-2 text-md-body-1 font-weight-medium mb-4"
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
            rounded="xl"
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
                <div class="d-flex align-center ga-1">
                  <v-btn
                    icon
                    size="x-small"
                    variant="text"
                    @click="startEditTask(task)"
                    style="color: var(--text-muted)"
                    :aria-label="`Edit ${task.title}`"
                  >
                    <svg
                      class="task-action-icon"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      stroke-width="2"
                    >
                      <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7" />
                      <path
                        d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"
                      />
                    </svg>
                  </v-btn>
                  <v-btn
                    icon
                    size="x-small"
                    variant="text"
                    @click="handleDeleteTask(task.id)"
                    style="color: var(--text-disabled)"
                    :aria-label="`Delete ${task.title}`"
                  >
                    <v-icon size="16">mdi-close</v-icon>
                  </v-btn>
                </div>
              </div>
              <div class="d-flex flex-wrap ga-2 mb-3">
                <span
                  class="task-chip px-2 py-1 text-caption rounded"
                  :style="getPriorityStyle(task.priority)"
                >
                  {{ task.priority }}
                </span>
                <span
                  class="task-chip px-2 py-1 text-caption"
                  style="color: var(--text-muted)"
                  >{{ task.category }}</span
                >
                <span
                  v-if="isOverdue(task)"
                  class="task-chip px-2 py-1 text-caption rounded font-weight-medium"
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
            class="text-center py-8 text-caption text-md-body-2"
            style="color: var(--text-muted)"
          >
            No tasks yet. Add your first task!
          </div>
        </div>
      </v-card-text>
    </v-card>

    <!-- Upcoming View -->
    <div v-if="view === 'upcoming'" class="mx-0">
      <h2
        class="text-h6 text-md-h5 font-weight-medium mb-4 mb-md-6 px-2 px-md-0"
        style="color: var(--text-primary)"
      >
        Upcoming
      </h2>
      <v-card
        v-for="[key, groupTasks] in Object.entries(getUpcomingTasks())"
        :key="key"
        class="mb-4"
        elevation="0"
        rounded="xl"
        style="background: var(--surface)"
      >
        <v-card-text class="pa-4 pa-md-6">
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
              rounded="xl"
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
                  <div class="d-flex align-center ga-1">
                    <v-btn
                      icon
                      size="x-small"
                      variant="text"
                      @click="startEditTask(task)"
                      style="color: var(--text-muted)"
                      :aria-label="`Edit ${task.title}`"
                    >
                      <svg
                        class="task-action-icon"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        stroke-width="2"
                      >
                        <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7" />
                        <path
                          d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"
                        />
                      </svg>
                    </v-btn>
                    <v-btn
                      icon
                      size="x-small"
                      variant="text"
                      @click="handleDeleteTask(task.id)"
                      style="color: var(--text-disabled)"
                      :aria-label="`Delete ${task.title}`"
                    >
                      <v-icon size="16">mdi-close</v-icon>
                    </v-btn>
                  </div>
                </div>
                <div class="d-flex flex-wrap ga-2 mb-3">
                  <span
                    class="task-chip px-2 py-1 text-caption rounded"
                    :style="getPriorityStyle(task.priority)"
                  >
                    {{ task.priority }}
                  </span>
                  <span
                    class="task-chip px-2 py-1 text-caption"
                    style="color: var(--text-muted)"
                    >{{ task.category }}</span
                  >
                  <span
                    v-if="isOverdue(task)"
                    class="task-chip px-2 py-1 text-caption rounded font-weight-medium"
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
          <h2 class="text-h6 font-weight-regular" style="color: var(--text-primary)">
            {{ isEditing ? "Edit Task" : "Add New Task" }}
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
            :menu-props="{ contentClass: 'dropdown-opaque' }"
          ></v-select>
          <v-select
            v-model="newTask.priority"
            :items="prioritySelectItems"
            label="Priority"
            variant="outlined"
            density="compact"
            class="mb-3"
            hide-details
            :menu-props="{ contentClass: 'dropdown-opaque' }"
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
          <v-select
            v-model="newTask.subjectId"
            :items="subjects.map(s => ({ title: s.name, value: s.id }))"
            label="Subject (optional)"
            variant="outlined"
            density="compact"
            class="mb-3"
            hide-details
            :disabled="!subjects || subjects.length === 0"
            :menu-props="{ contentClass: 'dropdown-opaque' }"
          />
          <v-select
            v-model="newTask.typeId"
            :items="typeSelectItems"
            label="Type (optional)"
            variant="outlined"
            density="compact"
            class="mb-3"
            hide-details
            :disabled="typeSelectItems.length === 0"
            :menu-props="{ contentClass: 'dropdown-opaque' }"
          />
          <v-alert
            v-if="addTaskError"
            type="error"
            variant="tonal"
            color="error"
            density="compact"
            class="mt-1 mb-3"
          >
            {{ addTaskError }}
          </v-alert>
        </v-card-text>
        <v-card-actions class="px-5 pb-5">
          <v-spacer></v-spacer>
          <v-btn
            @click="handleCloseAddTaskDialog"
            variant="text"
            class="text-none"
            style="color: var(--text-muted); text-transform: none"
          >
            Cancel
          </v-btn>
          <v-btn
            @click="handleSubmitTask"
            elevation="0"
            rounded="lg"
            class="text-none"
            style="
              background: var(--primary);
              color: white;
              text-transform: none;
            "
          >
            {{ isEditing ? "Save Changes" : "Add Task" }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup>
import { onMounted, ref, watch } from "vue";
import { api } from "@/lib/api.js";
import { useSubjects } from "@/composables/useSubjects";
import { useRecurringTopics } from "@/composables/useSubjects";

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
const { subjects, fetchSubjects } = useSubjects();
const { topics: recurringTypes, fetchTopics } = useRecurringTopics();
const stats = ref({ total: 0, completed: 0, dueToday: 0, overdue: 0 });
const loading = ref(false);
const errorMessage = ref("");
const addTaskError = ref("");
const isEditing = ref(false);
const editingTaskId = ref(null);

const newTaskDefaults = {
  title: "",
  status: "todo",
  priority: "medium",
  dueDate: "",
  subjectId: null,
  typeId: null,
};
const newTask = ref({ ...newTaskDefaults });

// Derive type dropdown items from recurring topics
const typeSelectItems = ref([]);

// handle race condition
let fetchToken = 0;

const fetchTasks = async () => {
  const token = ++fetchToken;
  loading.value = true;
  errorMessage.value = "";
  try {
    // construct query params
    const params = new URLSearchParams();
    if (filterStatus.value !== "all") {
      params.append("status", filterStatus.value);
    }
    if (filterPriority.value !== "all") {
      params.append("priority", filterPriority.value);
    }
    params.append("sortBy", sortBy.value);

    // make api call
    const query = params.toString();
    const response = await api.get(`/api/tasks/${query ? `?${query}` : ""}`);

    // handle race condition
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

onMounted(async () => {
  await Promise.all([fetchTasks(), fetchSubjects(), fetchTopics()]);
  typeSelectItems.value = (recurringTypes.value || []).map(t => ({ title: t.title, value: t.id }));
});

watch([filterStatus, filterPriority, sortBy], () => {
  fetchTasks();
});

watch(showAddTask, (value) => {
  if (!value) {
    addTaskError.value = "";
    isEditing.value = false;
    editingTaskId.value = null;
    newTask.value = { ...newTaskDefaults };
  }
});

// When recurring types list changes, refresh items
watch(recurringTypes, () => {
  typeSelectItems.value = (recurringTypes.value || []).map(t => ({ title: t.title, value: t.id }));
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

const openAddTaskDialog = () => {
  addTaskError.value = "";
  isEditing.value = false;
  editingTaskId.value = null;
  newTask.value = { ...newTaskDefaults };
  showAddTask.value = true;
};

// prepare dialog for edit
const startEditTask = (task) => {
  if (!task) return;
  addTaskError.value = "";
  errorMessage.value = "";
  editingTaskId.value = task.id;
  isEditing.value = true;
  newTask.value = {
    title: task.title ?? "",
    status: task.status ?? "todo",
    priority: task.priority ?? "medium",
    dueDate: task.dueDate ?? "",
    subjectId: task.subjectId ?? null,
    typeId: null,
  };
  showAddTask.value = true;
};

// add/update task
const handleSubmitTask = async () => {
  errorMessage.value = "";
  addTaskError.value = "";

  const trimmedTitle = newTask.value.title.trim();
  if (!trimmedTitle) {
    addTaskError.value = "Task title is required";
    return;
  }

  if (!newTask.value.dueDate) {
    addTaskError.value = "Please select a due date";
    return;
  }

  // Map selected typeId to a human-readable type title to store as topic string on backend
  const selectedType = (typeSelectItems.value || []).find(i => i.value === newTask.value.typeId);
  const payload = {
    title: trimmedTitle,
    status: newTask.value.status,
    priority: newTask.value.priority,
    dueDate: newTask.value.dueDate || null,
    subjectId: newTask.value.subjectId || null,
    topic: selectedType ? selectedType.title : null,
  };

  try {
    loading.value = true;
    if (isEditing.value && editingTaskId.value) {
      await api.patch(`/api/tasks/${editingTaskId.value}`, payload);
    } else {
      await api.post("/api/tasks/add-task", payload);
    }
    handleCloseAddTaskDialog();
    await fetchTasks();
  } catch (error) {
    const fallback = isEditing.value ? "Failed to update task" : "Failed to add task";
    addTaskError.value = error.message || fallback;
  } finally {
    loading.value = false;
  }
};

const handleCloseAddTaskDialog = () => {
  showAddTask.value = false;
  addTaskError.value = "";
  isEditing.value = false;
  editingTaskId.value = null;
  newTask.value = { ...newTaskDefaults };
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

<style scoped>
.task-container {
  padding-left: 8px;
  padding-right: 8px;
}

@media (min-width: 960px) {
  .task-container {
    padding-left: 24px;
    padding-right: 24px;
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

.filter-select {
  flex: 1;
  min-width: 0;
}

@media (min-width: 960px) {
  .filter-select {
    width: 140px;
    flex: none;
  }
}

.view-toggle {
  width: 100%;
  justify-content: center;
}

@media (min-width: 960px) {
  .view-toggle {
    width: auto;
  }
}

.add-task-btn {
  width: 100%;
}

@media (min-width: 960px) {
  .add-task-btn {
    width: auto;
  }
}

.task-chip {
  display: inline-flex;
  align-items: center;
  line-height: 1;
}

.task-action-icon {
  width: 16px;
  height: 16px;
}

.board-column {
  min-height: 200px;
}

@media (min-width: 960px) {
  .board-column {
    min-height: 400px;
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
