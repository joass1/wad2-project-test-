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
        <div class="d-flex flex-column flex-md-row justify-space-between align-start align-md-center ga-3">
          <v-tabs
            v-model="view"
            mandatory
            density="comfortable"
            class="view-tabs"
            hide-slider
            style="min-width: 0; flex: 0 0 auto;"
          >
            <v-tab value="board" class="text-none" style="text-transform: none;">Board</v-tab>
            <v-tab value="list" class="text-none" style="text-transform: none;">List</v-tab>
            <v-tab value="upcoming" class="text-none" style="text-transform: none;">Upcoming</v-tab>
          </v-tabs>
          <div class="d-flex flex-column flex-md-row ga-3" style="width: 100%; flex: 1 1 auto; justify-content: flex-end;">
            <v-select
              v-model="filterStatus"
              :items="statusOptions"
              item-title="title"
              item-value="value"
              label="Status"
              density="compact"
              variant="outlined"
              hide-details
              class="filter-select"
              style="font-size: 0.875rem"
              :menu-props="{ contentClass: 'dropdown-opaque' }"
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
              :menu-props="{ contentClass: 'dropdown-opaque' }"
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
              :menu-props="{ contentClass: 'dropdown-opaque' }"
            ></v-select>
          </div>
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
            <div
              class="board-column"
              :class="{ 'drag-over': draggedOverColumn === status }"
              @dragover.prevent="handleDragOver($event, status)"
              @dragenter.prevent="handleDragEnter(status)"
              @dragleave="handleDragLeave($event, status)"
              @drop.prevent="handleDrop($event, status)"
            >
              <v-card
                v-for="task in getFilteredTasks().filter(
                  (t) => t.status === status
                )"
                :key="task.id"
                class="mb-3 task-card"
                :class="{ 'dragging': draggedTaskId === task.id }"
                elevation="0"
                rounded="xl"
                draggable="true"
                @dragstart="handleDragStart($event, task)"
                @dragend="handleDragEnd"
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
                    <div class="d-flex align-center ga-1" @mousedown.stop @click.stop>
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
                        @click="handleArchiveTask(task.id)"
                        style="color: var(--text-disabled)"
                        :aria-label="`Archive ${task.title}`"
                      >
                        <v-icon size="16">mdi-delete</v-icon>
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
                      >{{ getTaskDisplayInfo(task) }}</span
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
                  <div @mousedown.stop @click.stop>
                    <v-select
                      :model-value="task.status"
                      @update:model-value="handleStatusChange(task.id, $event)"
                      :items="statusSelectItems"
                      density="compact"
                      variant="outlined"
                      hide-details
                      style="font-size: 0.875rem"
                      :menu-props="{ contentClass: 'dropdown-opaque' }"
                    ></v-select>
                  </div>
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
                  >{{ getTaskDisplayInfo(task) }}</span
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
                :menu-props="{ contentClass: 'dropdown-opaque' }"
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
                  :menu-props="{ contentClass: 'dropdown-opaque' }"
                ></v-select>
              </v-card-text>
            </v-card>
          </div>
        </v-card-text>
      </v-card>
    </div>

    <!-- Archived Tasks Card (Bottom Right of Page) -->
    <div class="d-flex justify-end mt-6 mb-4">
      <v-card
        v-if="archivedTasks.length > 0"
        class="archived-tasks-card"
        elevation="2"
        rounded="xl"
        style="background: var(--surface)"
      >
      <v-card-text class="pa-4">
        <div class="d-flex align-center justify-space-between mb-3">
          <div class="d-flex align-center ga-2">
            <v-icon size="20" color="var(--text-muted)">mdi-delete</v-icon>
            <h3 class="text-body-1 font-weight-medium" style="color: var(--text-primary)">
              Deleted Tasks
            </h3>
            <span class="text-caption" style="color: var(--text-muted)">
              ({{ archivedTasks.length }})
            </span>
          </div>
          <v-btn
            icon
            size="x-small"
            variant="text"
            @click="showArchivedCard = !showArchivedCard"
            style="color: var(--text-muted)"
          >
            <v-icon size="16">{{ showArchivedCard ? 'mdi-chevron-up' : 'mdi-chevron-down' }}</v-icon>
          </v-btn>
        </div>
        <v-expand-transition>
          <div v-if="showArchivedCard">
            <div v-if="loadingArchived" class="text-center py-4">
              <v-progress-circular indeterminate size="24" color="primary"></v-progress-circular>
            </div>
            <div v-else-if="archivedTasks.length === 0" class="text-center py-4 text-caption" style="color: var(--text-muted)">
              No deleted tasks
            </div>
            <div v-else class="archived-tasks-list">
              <v-card
                v-for="task in archivedTasks"
                :key="task.id"
                class="mb-2"
                elevation="0"
                rounded="lg"
                style="background: var(--surface-light)"
              >
                <v-card-text class="pa-3">
                  <div class="d-flex justify-space-between align-start">
                    <div class="flex-grow-1">
                      <div class="text-body-2 mb-1" style="color: var(--text-primary)">
                        {{ task.title }}
                      </div>
                      <div class="text-caption" style="color: var(--text-muted)">
                        Deleted {{ formatArchiveDate(task.deletedAt) }}
                      </div>
                    </div>
                    <div class="d-flex align-center ga-1">
                      <v-btn
                        icon
                        size="x-small"
                        variant="text"
                        @click="handleRestoreTask(task.id)"
                        style="color: var(--success)"
                        :aria-label="`Restore ${task.title}`"
                      >
                        <v-icon size="16">mdi-restore</v-icon>
                      </v-btn>
                      <v-btn
                        icon
                        size="x-small"
                        variant="text"
                        @click="handlePermanentDeleteTask(task.id)"
                        style="color: var(--error)"
                        :aria-label="`Permanently delete ${task.title}`"
                      >
                        <v-icon size="16">mdi-delete-forever</v-icon>
                      </v-btn>
                    </div>
                  </div>
                </v-card-text>
              </v-card>
            </div>
          </div>
        </v-expand-transition>
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
            v-model="newTask.subjectId"
            :items="subjects"
            item-title="name"
            item-value="id"
            label="Subject"
            variant="outlined"
            density="compact"
            class="mb-3"
            hide-details
            required
            :disabled="!subjects || subjects.length === 0"
            :menu-props="{ contentClass: 'dropdown-opaque' }"
          >
            <template v-slot:item="{ item, props }">
              <v-list-item v-bind="props">
                <template v-slot:prepend>
                  <span class="text-h6 mr-2">{{ item.raw.icon }}</span>
                </template>
              </v-list-item>
            </template>
            <template v-slot:selection="{ item }">
              <span class="text-h6 mr-2">{{ item.raw.icon }}</span>
              <span>{{ item.raw.name }}</span>
            </template>
          </v-select>
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

const statusOptions = [
  { title: "All", value: "all" },
  { title: "To Do", value: "todo" },
  { title: "In Progress", value: "inProgress" },
  { title: "Done", value: "done" },
];
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
const archivedTasks = ref([]);
const showArchivedCard = ref(false);
const loadingArchived = ref(false);
const { subjects, fetchSubjects } = useSubjects();
const { topics: recurringTypes, fetchTopics } = useRecurringTopics();
const stats = ref({ total: 0, completed: 0, dueToday: 0, overdue: 0 });
const loading = ref(false);
const errorMessage = ref("");
const addTaskError = ref("");
const isEditing = ref(false);
const editingTaskId = ref(null);

// Drag and drop state
const draggedTaskId = ref(null);
const draggedTaskStatus = ref(null);
const draggedOverColumn = ref(null);

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

const fetchArchivedTasks = async () => {
  loadingArchived.value = true;
  try {
    const response = await api.get("/api/tasks/archived");
    archivedTasks.value = Array.isArray(response) ? response : [];
    // Auto-show archived card if there are archived tasks
    if (archivedTasks.value.length > 0) {
      showArchivedCard.value = true;
    }
  } catch (error) {
    console.error("Failed to load archived tasks:", error);
    archivedTasks.value = [];
  } finally {
    loadingArchived.value = false;
  }
};

onMounted(async () => {
  await Promise.all([fetchTasks(), fetchSubjects(), fetchTopics(), fetchArchivedTasks()]);
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

// Helper function to get subject name from task
const getTaskSubjectName = (task) => {
  if (!task.subjectId) return null;
  const subject = subjects.value.find(s => s.id === task.subjectId);
  return subject ? subject.name : null;
};

// Helper function to get task display info (subject and type)
const getTaskDisplayInfo = (task) => {
  const subjectName = getTaskSubjectName(task);
  const type = task.topic || null;
  
  if (subjectName && type) {
    return `${subjectName} | ${type}`;
  } else if (subjectName) {
    return subjectName;
  } else if (type) {
    return type;
  }
  return 'No Subject';
};

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
  
  // Map topic string back to typeId if it matches a recurring topic
  let typeIdValue = null;
  if (task.topic && typeSelectItems.value.length > 0) {
    const matchingType = typeSelectItems.value.find(item => item.title === task.topic);
    if (matchingType) {
      typeIdValue = matchingType.value;
    }
  }
  
  newTask.value = {
    title: task.title ?? "",
    status: task.status ?? "todo",
    priority: task.priority ?? "medium",
    dueDate: task.dueDate ?? "",
    subjectId: task.subjectId ?? null, // Ensure subjectId is properly set
    typeId: typeIdValue,
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

  if (!newTask.value.subjectId) {
    addTaskError.value = "Please select a subject";
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
    subjectId: newTask.value.subjectId || null, // Explicitly include subjectId (required field)
    topic: selectedType ? selectedType.title : null,
  };

  try {
    loading.value = true;
    if (isEditing.value && editingTaskId.value) {
      await api.patch(`/api/tasks/${editingTaskId.value}`, payload);
    } else {
      await api.post("/api/tasks/add-task", payload);
    }
    await fetchTasks(); // Refresh tasks to show updated subject
    handleCloseAddTaskDialog();
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

// archive task
const handleArchiveTask = async (id) => {
  try {
    loading.value = true;
    await api.del(`/api/tasks/${id}`);
    await fetchTasks();
    await fetchArchivedTasks();
  } catch (error) {
    errorMessage.value = error.message || "Failed to archive task";
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

const formatArchiveDate = (dateString) => {
  if (!dateString) return "recently";
  const date = new Date(dateString);
  if (Number.isNaN(date.getTime())) return "recently";
  const now = new Date();
  const diffMs = now - date;
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
  
  if (diffDays === 0) return "today";
  if (diffDays === 1) return "yesterday";
  if (diffDays < 7) return `${diffDays} days ago`;
  if (diffDays < 30) {
    const weeks = Math.floor(diffDays / 7);
    return `${weeks} week${weeks > 1 ? 's' : ''} ago`;
  }
  return date.toLocaleDateString("en-US", { month: "short", day: "numeric" });
};

const handleRestoreTask = async (id) => {
  try {
    loading.value = true;
    await api.post(`/api/tasks/${id}/restore`);
    await fetchTasks();
    await fetchArchivedTasks();
  } catch (error) {
    errorMessage.value = error.message || "Failed to restore task";
  } finally {
    loading.value = false;
  }
};

const handlePermanentDeleteTask = async (id) => {
  if (!confirm("Are you sure you want to permanently delete this task? This action cannot be undone.")) {
    return;
  }
  try {
    loading.value = true;
    await api.del(`/api/tasks/${id}/permanent`);
    await fetchArchivedTasks();
  } catch (error) {
    errorMessage.value = error.message || "Failed to permanently delete task";
  } finally {
    loading.value = false;
  }
};

// Drag and drop handlers
const handleDragStart = (event, task) => {
  draggedTaskId.value = task.id;
  draggedTaskStatus.value = task.status;
  event.dataTransfer.effectAllowed = 'move';
  event.dataTransfer.setData('text/plain', task.id);
};

const handleDragEnd = () => {
  draggedTaskId.value = null;
  draggedTaskStatus.value = null;
  draggedOverColumn.value = null;
};

const handleDragOver = (event, targetStatus) => {
  event.preventDefault();
  if (canMoveToStatus(targetStatus)) {
    event.dataTransfer.dropEffect = 'move';
    if (draggedOverColumn.value !== targetStatus) {
      draggedOverColumn.value = targetStatus;
    }
  } else {
    event.dataTransfer.dropEffect = 'none';
    if (draggedOverColumn.value === targetStatus) {
      draggedOverColumn.value = null;
    }
  }
};

const handleDragEnter = (targetStatus) => {
  if (canMoveToStatus(targetStatus)) {
    draggedOverColumn.value = targetStatus;
  }
};

const handleDragLeave = (event, targetStatus) => {
  // Only clear if we're actually leaving the column (not just moving to a child)
  const relatedTarget = event.relatedTarget;
  const columnElement = event.currentTarget;
  
  // Check if we're actually leaving the column (relatedTarget might be null)
  if (!relatedTarget || !columnElement.contains(relatedTarget)) {
    if (draggedOverColumn.value === targetStatus) {
      draggedOverColumn.value = null;
    }
  }
};

const handleDrop = async (event, targetStatus) => {
  event.preventDefault();
  draggedOverColumn.value = null;
  
  if (!draggedTaskId.value || !canMoveToStatus(targetStatus)) {
    return;
  }

  const taskId = draggedTaskId.value;
  const currentStatus = draggedTaskStatus.value;
  
  // Only update if status actually changed
  if (currentStatus !== targetStatus) {
    try {
      await api.patch(`/api/tasks/${taskId}`, { status: targetStatus });
      await fetchTasks();
    } catch (error) {
      errorMessage.value = error.message || "Failed to update task status";
    }
  }
  
  draggedTaskId.value = null;
  draggedTaskStatus.value = null;
};

// Validate forward-only movement
const canMoveToStatus = (targetStatus) => {
  if (!draggedTaskStatus.value) return false;
  
  const statusOrder = { todo: 0, inProgress: 1, done: 2 };
  const currentOrder = statusOrder[draggedTaskStatus.value];
  const targetOrder = statusOrder[targetStatus];
  
  // Only allow forward movement (same or next status)
  return targetOrder >= currentOrder;
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

.view-tabs {
  width: 100%;
}

@media (min-width: 960px) {
  .view-tabs {
    width: auto;
  }
}

/* Hide scrollbar and ensure tabs don't scroll */
.view-tabs :deep(.v-tabs__wrapper) {
  overflow: hidden !important;
}

.view-tabs :deep(.v-slide-group__content) {
  overflow: hidden !important;
}

.view-tabs :deep(.v-tab) {
  min-width: auto;
  padding: 0 16px;
  transition: background-color 0.2s ease;
}

/* Active tab - darker shade */
.view-tabs :deep(.v-tab.v-tab--selected) {
  background-color: rgba(0, 0, 0, 0.08) !important;
}

/* Hover state on tabs - even darker */
.view-tabs :deep(.v-tab:hover) {
  background-color: rgba(0, 0, 0, 0.12) !important;
}

/* Active tab on hover - darkest */
.view-tabs :deep(.v-tab.v-tab--selected:hover) {
  background-color: rgba(0, 0, 0, 0.15) !important;
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
  transition: background-color 0.2s ease;
}

.board-column.drag-over {
  background-color: rgba(99, 102, 241, 0.1);
  border-radius: 12px;
  border: 2px dashed rgba(99, 102, 241, 0.3);
}

@media (min-width: 960px) {
  .board-column {
    min-height: 400px;
  }
}

.task-card {
  cursor: grab;
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.task-card:active {
  cursor: grabbing;
}

.task-card.dragging {
  opacity: 0.5;
  transform: scale(0.95);
}

.task-card :deep(button),
.task-card :deep(.v-btn),
.task-card :deep(.v-select) {
  pointer-events: auto;
}

.task-card :deep(button):hover,
.task-card :deep(.v-btn):hover {
  cursor: pointer;
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

/* Archived Tasks Card - At bottom right of page */
.archived-tasks-card {
  width: 320px;
  max-width: 100%;
  max-height: 500px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15) !important;
}

.archived-tasks-list {
  max-height: 400px;
  overflow-y: auto;
}

@media (max-width: 600px) {
  .archived-tasks-card {
    width: 100%;
    float: none;
  }
}
</style>
