<script setup>
import { ref, computed, onUnmounted, watch, onMounted } from 'vue'
import { useSubjects, useRecurringTopics } from '@/composables/useSubjects'
// NEW: Background imports
import { useBackground } from '@/composables/useBackgrounds'
import BackgroundsGallery from '@/components/BackgroundsGallery.vue'
import { useCoins } from '@/composables/useCoins.js' 

const { subjects, loading: subjectsLoading, fetchSubjects, createSubject, updateSubject, deleteSubject } = useSubjects()
const { topics: recurringTopics, loading: topicsLoading, fetchTopics, createTopic, updateTopic, deleteTopic } = useRecurringTopics()
// NEW: Use Background composable
const { selectedBackgroundId, getCurrentBackground } = useBackground()
const { coins, updateCoins } = useCoins()

const presets = { 'Focus': 25, 'Short Break': 5, 'Long Break': 15 }
const mode = ref('Focus')
const minutes = ref(presets[mode.value])
const timeLeft = ref(presets[mode.value] * 60)
const running = ref(false)
const settingsDialog = ref(false)
const customFocusTime = ref(25)
const customBreakTime = ref(5)
let t = null

// Session Details Data
const selectedSubject = ref(null)
const selectedTopic = ref('') // Can be manual text or selected topic ID
const selectedTask = ref(null) // Reference to task tracker task
const sessionNotes = ref('')

// Task completion dialog
const taskCompletionDialog = ref(false)
const tasksFromTracker = ref([])

// NEW: Store all topics (not filtered by subject)
const allRecurringTopics = ref([])

const loading = computed(() => subjectsLoading.value || topicsLoading.value)

// Tab state
const activeTab = ref('session')

// Subject Dialog
const subjectDialog = ref(false)
const subjectForm = ref({
  name: '',
  color: '#4CAF50',
  icon: '📚',
  description: ''
})
const editingSubject = ref(null)

// Topic Dialog
const topicDialog = ref(false)

// Fetch tasks from tracker
async function fetchTasksFromTracker() {
  try {
    const response = await fetch('/api/tasks')
    const data = await response.json()
    tasksFromTracker.value = data.tasks || []
  } catch (error) {
    console.error('Error fetching tasks:', error)
  }
}

const topicForm = ref({
  subject_id: null, // NOW OPTIONAL - can create topics without subject
  title: '',
  description: '',
  recurrence: 'weekly'
})
const editingTopic = ref(null)

// Color & Icon Options
const colorOptions = [
  { name: 'Green', value: '#4CAF50' },
  { name: 'Blue', value: '#2196F3' },
  { name: 'Purple', value: '#9C27B0' },
  { name: 'Red', value: '#F44336' },
  { name: 'Orange', value: '#FF9800' },
  { name: 'Teal', value: '#009688' },
  { name: 'Pink', value: '#E91E63' },
  { name: 'Indigo', value: '#3F51B5' }
]

const iconOptions = ['📚', '💻', '🧪', '🎨', '📐', '🌍', '📖', '✏️', '🔬', '🎵', '💼', '🏃', '⚽', '🎭']

const total = computed(() => minutes.value * 60)
const pct = computed(() => Math.floor(100 * (total.value - timeLeft.value) / total.value))
const label = computed(() => {
  const mins = Math.floor(timeLeft.value / 60)
  const secs = timeLeft.value % 60
  return `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`
})

// FIX: Added a safe default return to prevent 'Cannot read properties of undefined' errors on mount
const blurredBackgroundStyle = computed(() => {
  // Depend on selectedBackgroundId to react to changes made in the gallery
  // eslint-disable-next-line no-unused-expressions
  selectedBackgroundId.value
  // Use getCurrentBackground() and provide a safe fallback object {} if undefined
  const bg = getCurrentBackground() || {}; 
  
  if (!bg.path) {
    // Return safe defaults when no background is selected
    return {
      backgroundImage: 'none',
      backgroundSize: 'auto',
      backgroundPosition: 'initial',
      backgroundRepeat: 'no-repeat',
      backgroundAttachment: 'initial',
    }
  }

  // Return the image source path and base config when a background is selected
  return {
    backgroundImage: `url(${bg.path})`,
    backgroundSize: 'cover',
    backgroundPosition: 'center',
    backgroundRepeat: 'no-repeat',
    backgroundAttachment: 'fixed',
  }
})

// NEW: Computed list of topics for dropdown
const topicDropdownItems = computed(() => {
  const items = allRecurringTopics.value.map(topic => ({
    title: topic.title,
    value: topic.id,
    subtitle: topic.subject_id 
      ? subjects.value.find(s => s.id === topic.subject_id)?.name 
      : 'No subject'
  }))
  return items
})

// NEW: Filtered topics for the Topics tab (by selected subject)
const filteredTopics = computed(() => {
  if (!selectedSubject.value) {
    return allRecurringTopics.value
  }
  return allRecurringTopics.value.filter(t => t.subject_id === selectedSubject.value)
})

const emit = defineEmits(['toggle-fullscreen'])

watch(running, (newVal) => {
  emit('toggle-fullscreen', newVal)
})

onMounted(async () => {
  await loadSubjects()
  await loadAllRecurringTopics()
  await fetchTasksFromTracker()
})

// ============================================================================
// SUBJECTS FUNCTIONS (Unchanged)
// ============================================================================

async function loadSubjects() {
  try {
    await fetchSubjects()
  } catch (error) {
    console.error('Error loading subjects:', error)
    alert('Failed to load subjects: ' + error.message)
  }
}

function openSubjectDialog(subject = null) {
  if (subject) {
    editingSubject.value = subject
    subjectForm.value = { ...subject }
  } else {
    editingSubject.value = null
    subjectForm.value = {
      name: '',
      color: '#4CAF50',
      icon: '📚',
      description: ''
    }
  }
  subjectDialog.value = true
}

async function saveSubject() {
  try {
    if (editingSubject.value) {
      await updateSubject(editingSubject.value.id, {
        name: subjectForm.value.name,
        color: subjectForm.value.color,
        icon: subjectForm.value.icon,
        description: subjectForm.value.description
      })
    } else {
      await createSubject({
        name: subjectForm.value.name,
        color: subjectForm.value.color,
        icon: subjectForm.value.icon,
        description: subjectForm.value.description
      })
    }
    
    subjectDialog.value = false
  } catch (error) {
    console.error('Error saving subject:', error)
    alert('Failed to save subject: ' + error.message)
  }
}

async function handleDeleteSubject(subjectId) {
  if (!confirm('Delete this subject? This will also remove its topics.')) {
    return
  }
  
  try {
    await deleteSubject(subjectId)
    
    if (selectedSubject.value === subjectId) {
      selectedSubject.value = null
    }
  } catch (error) {
    console.error('Error deleting subject:', error)
    alert('Failed to delete subject: ' + error.message)
  }
}

// ============================================================================
// RECURRING TOPICS FUNCTIONS (Unchanged)
// ============================================================================

// NEW: Load ALL topics regardless of subject

async function loadAllRecurringTopics() {
  try {
    await fetchTopics()
    allRecurringTopics.value = recurringTopics.value
  } catch (error) {
    console.error('Error loading topics:', error)
  }
}

function showTaskCompletionDialog() {
  taskCompletionDialog.value = true
}

async function markTaskAsComplete() {
  if (!selectedTask.value) return
  
  try {
    await fetch(`/api/tasks/${selectedTask.value}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status: 'done' })
    })
    taskCompletionDialog.value = false
  } catch (error) {
    console.error('Error updating task:', error)
    alert('Failed to update task status')
  }
}

function dismissTaskCompletionDialog() {
  taskCompletionDialog.value = false
}

// UPDATED: Open topic dialog - subject_id is now optional
function openTopicDialog(topic = null) {
  if (topic) {
    editingTopic.value = topic
    topicForm.value = { ...topic }
  } else {
    editingTopic.value = null
    topicForm.value = {
      subject_id: selectedSubject.value || null, // Can be null
      title: '',
      description: '',
      recurrence: 'weekly'
    }
  }
  topicDialog.value = true
}

async function saveTopic() {
  try {
    if (editingTopic.value) {
      await updateTopic(editingTopic.value.id, {
        title: topicForm.value.title,
        description: topicForm.value.description,
        recurrence: topicForm.value.recurrence,
        subject_id: topicForm.value.subject_id // Can be null
      })
    } else {
      await createTopic({
        subject_id: topicForm.value.subject_id, // Can be null
        title: topicForm.value.title,
        description: topicForm.value.description,
        recurrence: topicForm.value.recurrence
      })
    }
    
    // Reload all topics after save
    await loadAllRecurringTopics()
    topicDialog.value = false
  } catch (error) {
    console.error('Error saving topic:', error)
    alert('Failed to save topic: ' + error.message)
  }
}

async function handleDeleteTopic(topicId) {
  if (!confirm('Delete this recurring topic?')) {
    return
  }
  
  try {
    await deleteTopic(topicId)
    // Reload all topics after delete
    await loadAllRecurringTopics()
  } catch (error) {
    console.error('Error deleting topic:', error)
    alert('Failed to delete topic: ' + error.message)
  }
}

// Open subjects tab from dropdown
function goToManageSubjects() {
  activeTab.value = 'subjects'
}

// NEW: Get topic title from ID for display
function getTopicTitle(topicId) {
  const topic = allRecurringTopics.value.find(t => t.id === topicId)
  return topic ? topic.title : topicId
}

// ============================================================================
// TIMER FUNCTIONS (Unchanged)
// ============================================================================

function switchMode(m) { 
  if (running.value) return
  mode.value = m
  minutes.value = presets[m]
  timeLeft.value = presets[m] * 60
}

function start(){ 
  if (running.value) return
  running.value = true
  t = setInterval(() => { 
    timeLeft.value--
    if (timeLeft.value <= 0){ 
      clearInterval(t)
      running.value = false
      timeLeft.value = 0
      
      if (mode.value === 'Focus') {
        dispatchStudySessionCompleted()
      }
    } 
  }, 1000) 
}

async function dispatchStudySessionCompleted() {
  console.log('Focus session completed! Dispatching event...');

  const subjectName = selectedSubject.value
    ? subjects.value.find(s => s.id === selectedSubject.value)?.name
    : null

  // Get topic title - could be manual text or a topic ID
  let taskDisplay = selectedTopic.value
  if (selectedTopic.value) {
    const topic = allRecurringTopics.value.find(t => t.id === selectedTopic.value)
    if (topic) {
      taskDisplay = topic.title
    }
  }

  window.dispatchEvent(new CustomEvent('study-session-completed', {
    detail: {
      duration: minutes.value,
      mode: mode.value,
      subject: subjectName,
      task: taskDisplay,
      task_id: selectedTask.value,
      notes: sessionNotes.value,
      timestamp: new Date()
    }
  }))

  // Award coins for completing study session (pro-rated: 10 coins per 25 minutes)
  try {
    const durationMinutes = minutes.value
    const coinsEarned = Math.floor((durationMinutes) * 10)

    console.log(`Calculating coins: ${durationMinutes} minutes × 10 / 25 = ${coinsEarned} coins`)

    if (coinsEarned > 0) {
      const currentCoins = coins.value || 0
      const newCoins = currentCoins + coinsEarned
      console.log(`Updating coins: ${currentCoins} + ${coinsEarned} = ${newCoins}`)

      const result = await updateCoins(newCoins)
      if (result.success) {
        console.log(`Study session rewarded ${coinsEarned} coins! Total: ${newCoins}`)
      }
    } else {
      console.log('No coins earned (duration too short)')
    }
  } catch (coinError) {
    console.error('Error awarding study session coins:', coinError)
    // Don't fail the session completion if coins fail to update
  }

  // Show completion dialog with task option
  if (selectedTask.value) {
    showTaskCompletionDialog()
  }
}

function stop(){ 
  running.value = false
  clearInterval(t) 
}

function reset(){ 
  stop()
  timeLeft.value = minutes.value * 60
}

function openSettings() {
  settingsDialog.value = true
}

function saveSettings() {
  customFocusTime.value = parseInt(customFocusTime.value) || 25
  customBreakTime.value = parseInt(customBreakTime.value) || 5
  presets['Focus'] = customFocusTime.value
  presets['Short Break'] = customBreakTime.value
  
  if (mode.value === 'Focus') {
    minutes.value = customFocusTime.value
    timeLeft.value = customFocusTime.value * 60
  }
  settingsDialog.value = false
}

onUnmounted(() => { clearInterval(t) })
</script>

<template>
  <div :class="['timer-page', { 'fullscreen-mode': running }]">

    <div v-if="!running" class="main-page-blurred-background"></div>
    
    
    
    <div v-if="running && getCurrentBackground().path" class="fullscreen-gif-background"></div>
    
    <v-container :class="['py-8', { 'fullscreen-container': running }]" :style="running ? 'max-width: 100%;' : 'max-width: 1400px;'">
      <v-row>
        <v-col :cols="running ? 12 : 12" :md="running ? 12 : 7" :lg="running ? 12 : 8">
          <v-card rounded="xl" elevation="0" :class="['timer-card', { 'fullscreen-card': running }]" class="pa-10">
            <div class="mb-2">
              <h2 class="text-h5 font-weight-medium mb-1 timer-title">Study Timer</h2>
              <p class="text-body-2 text-medium-emphasis">Focus with the Pomodoro Technique</p>
            </div>

            <div class="session-box mt-6 pa-6 rounded-lg">
              <div class="d-flex justify-space-between align-center mb-6">
                <div>
                  <div class="text-subtitle-2 text-medium-emphasis mb-1">Study Session</div>
                  <div class="text-caption text-medium-emphasis">Set your timer</div>
                </div>
                <v-chip color="primary" size="small" variant="flat" class="px-4">Ready</v-chip>
              </div>

              <div class="d-flex ga-2 mb-8 flex-wrap justify-center">
                <v-chip v-for="m in Object.keys(presets)" :key="m"
                        :color="mode===m?'primary':'secondary'" 
                        :variant="mode===m?'flat':'tonal'"
                        class="cursor-pointer px-4"
                        @click="switchMode(m)">
                  {{ m }} • {{ presets[m] }}m
                </v-chip>
              </div>

              <div class="text-center mb-8">
                <div :class="['timer-display', 'mb-4', { 'timer-display-large': running }]">{{ label }}</div>
                <v-progress-linear :model-value="pct" height="8" rounded color="primary" 
                                  bg-color="surface-lighter" class="mb-2"/>
              </div>

              <div class="d-flex ga-3 justify-center">
                <v-btn color="primary" size="large" rounded="lg" @click="start" :disabled="running" 
                       class="px-8 text-none" elevation="0">
                  <v-icon start>mdi-play</v-icon>Start
                </v-btn>
                <v-btn color="secondary" size="large" rounded="lg" variant="tonal" @click="stop" 
                       :disabled="!running" class="px-6 text-none" elevation="0">
                  <v-icon start>mdi-pause</v-icon>Pause
                </v-btn>
                <v-btn size="large" rounded="lg" variant="text" @click="reset" 
                       class="text-none reset-btn">
                  <v-icon start>mdi-restore</v-icon>Reset
                </v-btn>
              </div>

              <div v-if="!running" class="d-flex justify-space-around mt-8 pt-6 stats-divider">
                <div class="text-center">
                  <div class="text-h4 font-weight-medium stat-number">0</div>
                  <div class="text-caption text-medium-emphasis">Sessions Today</div>
                </div>
                <div class="text-center">
                  <div class="text-h4 font-weight-medium stat-number">70%</div>
                  <div class="text-caption text-medium-emphasis">Focus Score</div>
                </div>
              </div>
            </div>

            <div v-if="!running" class="tips-section mt-6 pa-6 rounded-lg">
              <div class="text-subtitle-2 font-weight-medium mb-4 tips-title">Focus Tips</div>
              <v-row>
                <v-col cols="12" md="6">
                  <div class="text-body-2 font-weight-medium mb-2">During Study Sessions:</div>
                  <ul class="text-caption text-medium-emphasis" style="line-height: 1.8;">
                    <li>Turn off notifications</li>
                    <li>Keep water nearby</li>
                    <li>Use comfortable lighting</li>
                    <li>Take notes by hand when possible</li>
                  </ul>
                </v-col>
                <v-col cols="12" md="6">
                  <div class="text-body-2 font-weight-medium mb-2">During Breaks:</div>
                  <ul class="text-caption text-medium-emphasis" style="line-height: 1.8;">
                    <li>Step away from your desk</li>
                    <li>Do light stretching</li>
                    <li>Get some fresh air</li>
                    <li>Avoid social media</li>
                  </ul>
                </v-col>
              </v-row>
            </div>
          </v-card>
        </v-col>

        <v-col v-if="!running" cols="12" md="5" lg="4">
          <v-card rounded="xl" elevation="0" class="details-card pa-6 mb-4">
            <v-tabs v-model="activeTab" bg-color="transparent" color="primary" class="mb-4" show-arrows="false">
              <v-tab value="session">Session</v-tab>
              <v-tab value="subjects">Subjects</v-tab>
              <v-tab value="topics">Topics</v-tab>
            </v-tabs>

            <v-window v-model="activeTab">
              <v-window-item value="session">
                <div class="text-subtitle-1 font-weight-medium mb-1 session-title">Session Details</div>
                <p class="text-caption text-medium-emphasis mb-4">Set up your study session</p>
                
                <div class="mb-4">
                  <div class="d-flex justify-space-between align-center mb-2">
                    <label class="text-body-2 font-weight-medium">Subject</label>
                    <v-btn 
                      size="x-small" 
                      variant="text" 
                      color="primary"
                      @click="goToManageSubjects"
                      class="text-none"
                    >
                      <v-icon start size="small">mdi-plus</v-icon>
                      Manage
                    </v-btn>
                  </div>
                  <v-select 
                    v-model="selectedSubject"
                    :items="subjects"
                    item-title="name"
                    item-value="id"
                    density="comfortable" 
                    variant="outlined" 
                    rounded="lg" 
                    placeholder="Select subject" 
                    hide-details
                    :disabled="subjects.length === 0"
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
                    
                    <template v-slot:no-data>
                      <v-list-item>
                        <v-list-item-title class="text-center text-caption">
                          No subjects yet. Click "Manage" to create one!
                        </v-list-item-title>
                      </v-list-item>
                    </template>
                  </v-select>
                </div>

                <div class="mb-4">
                  <label class="text-body-2 font-weight-medium mb-2 d-block">Topic (Recurring)</label>
                  <v-combobox
                    v-model="selectedTopic"
                    :items="topicDropdownItems"
                    item-title="title"
                    item-value="value"
                    variant="outlined"
                    rounded="lg"
                    placeholder="Type or select a recurring topic"
                    hide-details
                    density="comfortable"
                    :menu-props="{ contentClass: 'dropdown-opaque' }"
                  >
                    <template v-slot:item="{ props, item }">
                      <v-list-item v-bind="props">
                        <template v-slot:title>{{ item.raw.title }}</template>
                        <template v-slot:subtitle>{{ item.raw.subtitle }}</template>
                      </v-list-item>
                    </template>
                  </v-combobox>
                </div>

                <div class="mb-4">
                  <label class="text-body-2 font-weight-medium mb-2 d-block">Task (from Task Tracker)</label>
                  <v-select
                    v-model="selectedTask"
                    :items="tasksFromTracker"
                    item-title="title"
                    item-value="id"
                    variant="outlined"
                    rounded="lg"
                    placeholder="Select a task (optional)"
                    hide-details
                    density="comfortable"
                    clearable
                    :menu-props="{ contentClass: 'dropdown-opaque' }"
                  >
                    <template v-slot:item="{ props, item }">
                      <v-list-item v-bind="props">
                        <template v-slot:title>{{ item.raw.title }}</template>
                        <template v-slot:subtitle>
                          <v-chip size="x-small" :color="item.raw.priority === 'high' ? 'error' : item.raw.priority === 'medium' ? 'warning' : 'success'" class="mr-1">
                            {{ item.raw.priority }}
                          </v-chip>
                          {{ item.raw.category }}
                        </template>
                      </v-list-item>
                    </template>
                  </v-select>
                </div>

                <div class="mb-4">
                  <label class="text-body-2 font-weight-medium mb-2 d-block">Notes (optional)</label>
                  <v-textarea 
                    v-model="sessionNotes"
                    density="comfortable" 
                    variant="outlined" 
                    rounded="lg" 
                    rows="3"
                    placeholder="Any additional notes..." 
                    hide-details
                  />
                </div>

                <v-btn block color="primary" rounded="lg" variant="tonal" class="text-none mt-2" @click="openSettings">
                  <v-icon start>mdi-cog</v-icon>Timer Settings
                </v-btn>
              </v-window-item>

              <v-window-item value="subjects">
                <div class="d-flex justify-space-between align-center mb-4">
                  <div>
                    <div class="text-subtitle-1 font-weight-medium session-title">My Subjects</div>
                    <p class="text-caption text-medium-emphasis">Manage your study subjects</p>
                  </div>
                  <v-btn color="primary" size="small" icon @click="openSubjectDialog()">
                    <v-icon>mdi-plus</v-icon>
                  </v-btn>
                </div>

                <v-progress-linear v-if="loading" indeterminate color="primary" class="mb-2" height="2" />

                <div v-if="subjects.length === 0 && !loading" class="text-center pa-4">
                  <v-icon size="48" color="medium-emphasis" class="mb-2">mdi-book-outline</v-icon>
                  <p class="text-caption text-medium-emphasis">No subjects yet</p>
                  <v-btn size="small" variant="text" color="primary" @click="openSubjectDialog()">
                    Create your first subject
                  </v-btn>
                </div>

                <v-list v-else class="pa-0">
                  <v-list-item
                    v-for="subject in subjects"
                    :key="subject.id"
                    rounded="lg"
                    class="mb-2"
                    :style="{ borderLeft: `4px solid ${subject.color}` }"
                  >
                    <template v-slot:prepend>
                      <span class="text-h6 mr-2">{{ subject.icon }}</span>
                    </template>

                    <v-list-item-title class="font-weight-medium">
                      {{ subject.name }}
                    </v-list-item-title>
                    
                    <template v-slot:append>
                      <v-menu>
                        <template v-slot:activator="{ props }">
                          <v-btn icon="mdi-dots-vertical" variant="text" v-bind="props" size="small" />
                        </template>
                        <v-list density="compact" class="dropdown-opaque">
                          <v-list-item @click="openSubjectDialog(subject)">
                            <v-list-item-title>
                              <v-icon start size="small">mdi-pencil</v-icon>Edit
                            </v-list-item-title>
                          </v-list-item>
                          <v-list-item @click="handleDeleteSubject(subject.id)">
                            <v-list-item-title class="text-error">
                              <v-icon start size="small">mdi-delete</v-icon>Delete
                            </v-list-item-title>
                          </v-list-item>
                        </v-list>
                      </v-menu>
                    </template>
                  </v-list-item>
                </v-list>
              </v-window-item>

              <v-window-item value="topics">
                <div class="d-flex justify-space-between align-center mb-4">
                  <div>
                    <div class="text-subtitle-1 font-weight-medium session-title">Recurring Topics</div>
                    <p class="text-caption text-medium-emphasis">
                      {{ selectedSubject ? 'Topics for selected subject' : 'All topics' }}
                    </p>
                  </div>
                  <v-btn 
                    color="primary" 
                    size="small" 
                    icon 
                    @click="openTopicDialog()"
                  >
                    <v-icon>mdi-plus</v-icon>
                  </v-btn>
                </div>

                <v-progress-linear v-if="loading" indeterminate color="primary" class="mb-2" height="2" />

                <div v-if="filteredTopics.length === 0 && !loading" class="text-center pa-4">
                  <v-icon size="48" color="medium-emphasis" class="mb-2">mdi-clipboard-list-outline</v-icon>
                  <p class="text-caption text-medium-emphasis">
                    {{ selectedSubject ? 'No topics for this subject yet' : 'No recurring topics yet. Create one!' }}
                  </p>
                  <v-btn size="small" variant="text" color="primary" @click="openTopicDialog()">
                    Add a recurring topic
                  </v-btn>
                </div>

                <v-list v-else class="pa-0">
                  <v-list-item
                    v-for="topic in filteredTopics"
                    :key="topic.id"
                    rounded="lg"
                    class="mb-2"
                  >
                    <v-list-item-title class="font-weight-medium">
                      {{ topic.title }}
                      <v-chip size="x-small" color="primary" variant="outlined" class="ml-2">
                        {{ topic.recurrence }}
                      </v-chip>
                    </v-list-item-title>
                    <v-list-item-subtitle v-if="topic.description">
                      {{ topic.description }}
                    </v-list-item-subtitle>
                    
                    <template v-slot:append>
                      <v-menu>
                        <template v-slot:activator="{ props }">
                          <v-btn icon="mdi-dots-vertical" variant="text" v-bind="props" size="small" />
                        </template>
                        <v-list density="compact" class="dropdown-opaque">
                          <v-list-item @click="openTopicDialog(topic)">
                            <v-list-item-title>
                              <v-icon start size="small">mdi-pencil</v-icon>Edit
                            </v-list-item-title>
                          </v-list-item>
                          <v-list-item @click="handleDeleteTopic(topic.id)">
                            <v-list-item-title class="text-error">
                              <v-icon start size="small">mdi-delete</v-icon>Delete
                            </v-list-item-title>
                          </v-list-item>
                        </v-list>
                      </v-menu>
                    </template>
                  </v-list-item>
                </v-list>
              </v-window-item>
            </v-window>
          </v-card>

          <v-card rounded="xl" elevation="0" class="streaks-card pa-6">
            <div class="text-subtitle-2 font-weight-medium mb-4 streaks-title">Daily Streaks</div>
            <v-row dense>
              <v-col cols="4" class="text-center">
                <div class="text-h5 font-weight-bold streak-number">0</div>
                <div class="text-caption text-medium-emphasis">Study</div>
              </v-col>
              <v-col cols="4" class="text-center">
                <div class="text-h5 font-weight-bold streak-number">0</div>
                <div class="text-caption text-medium-emphasis">Check-in</div>
              </v-col>
              <v-col cols="4" class="text-center">
                <div class="text-h5 font-weight-bold streak-number">0</div>
                <div class="text-caption text-medium-emphasis">Wellness</div>
              </v-col>
            </v-row>
          </v-card>
          
          <backgrounds-gallery class="mt-4" />
        </v-col>
      </v-row>
    </v-container>

    <div v-if="running && !getCurrentBackground().path" class="falling-leaves-overlay">
      <div class="leaf" v-for="i in 20" :key="i" :style="{ 
        left: `${Math.random() * 100}%`, 
        animationDelay: `${Math.random() * 8}s`,
        animationDuration: `${10 + Math.random() * 6}s`
      }">🍂</div>
    </div>
      
    <div v-if="running && !getCurrentBackground().path" class="falling-leaves-overlay">
      <div class="leaf" v-for="i in 20" :key="i" :style="{ 
        left: `${Math.random() * 100}%`, 
        animationDelay: `${Math.random() * 8}s`,
        animationDuration: `${10 + Math.random() * 6}s`
      }">🍂</div>
    </div>

    <!-- Subject Dialog -->
    <v-dialog v-model="subjectDialog" max-width="500px" persistent>
      <v-card rounded="xl">
        <v-card-title class="pa-6">
          <span class="text-h6">{{ editingSubject ? 'Edit Subject' : 'New Subject' }}</span>
        </v-card-title>
        
        <v-card-text class="pa-6 pt-0">
          <v-form @submit.prevent="saveSubject">
            <v-text-field
              v-model="subjectForm.name"
              label="Subject Name"
              variant="outlined"
              rounded="lg"
              class="mb-4"
              required
            />
            
            <div class="mb-4">
              <label class="text-body-2 font-weight-medium mb-2 d-block">Icon</label>
              <div class="d-flex flex-wrap ga-2">
                <v-chip
                  v-for="icon in iconOptions"
                  :key="icon"
                  :color="subjectForm.icon === icon ? 'primary' : 'default'"
                  :variant="subjectForm.icon === icon ? 'flat' : 'outlined'"
                  @click="subjectForm.icon = icon"
                  class="cursor-pointer"
                >
                  {{ icon }}
                </v-chip>
              </div>
            </div>
            
            <div class="mb-4">
              <label class="text-body-2 font-weight-medium mb-2 d-block">Color</label>
              <div class="d-flex flex-wrap ga-2">
                <div
                  v-for="color in colorOptions"
                  :key="color.value"
                  @click="subjectForm.color = color.value"
                  :style="{ 
                    backgroundColor: color.value,
                    border: subjectForm.color === color.value ? '3px solid #000' : '1px solid #ddd'
                  }"
                  class="color-swatch cursor-pointer"
                  :title="color.name"
                />
              </div>
            </div>
            
            <v-textarea
              v-model="subjectForm.description"
              label="Description (optional)"
              variant="outlined"
              rounded="lg"
              rows="3"
            />
          </v-form>
        </v-card-text>
        
        <v-card-actions class="pa-6 pt-0">
          <v-spacer />
          <v-btn
            variant="text"
            @click="subjectDialog = false"
            class="text-none"
          >
            Cancel
          </v-btn>
          <v-btn
            color="primary"
            variant="flat"
            @click="saveSubject"
            class="text-none"
          >
            {{ editingSubject ? 'Update' : 'Create' }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Topic Dialog -->
    <v-dialog v-model="topicDialog" max-width="500px" persistent>
      <v-card rounded="xl">
        <v-card-title class="pa-6">
          <span class="text-h6">{{ editingTopic ? 'Edit Topic' : 'New Recurring Topic' }}</span>
        </v-card-title>
        
        <v-card-text class="pa-6 pt-0">
          <v-form @submit.prevent="saveTopic">
            <v-select
              v-model="topicForm.subject_id"
              :items="subjects"
              item-title="name"
              item-value="id"
              label="Subject (optional)"
              variant="outlined"
              rounded="lg"
              class="mb-4"
              clearable
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
            
            <v-text-field
              v-model="topicForm.title"
              label="Topic Title"
              variant="outlined"
              rounded="lg"
              class="mb-4"
              required
            />
            
            <v-select
              v-model="topicForm.recurrence"
              :items="['daily', 'weekly', 'biweekly', 'monthly']"
              label="Recurrence"
              variant="outlined"
              rounded="lg"
              class="mb-4"
            />
            
            <v-textarea
              v-model="topicForm.description"
              label="Description (optional)"
              variant="outlined"
              rounded="lg"
              rows="3"
            />
          </v-form>
        </v-card-text>
        
        <v-card-actions class="pa-6 pt-0">
          <v-spacer />
          <v-btn
            variant="text"
            @click="topicDialog = false"
            class="text-none"
          >
            Cancel
          </v-btn>
          <v-btn
            color="primary"
            variant="flat"
            @click="saveTopic"
            class="text-none"
          >
            {{ editingTopic ? 'Update' : 'Create' }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Settings Dialog -->
    <v-dialog v-model="settingsDialog" max-width="400px">
      <v-card rounded="xl">
        <v-card-title class="pa-6">
          <span class="text-h6">Timer Settings</span>
        </v-card-title>
        
        <v-card-text class="pa-6 pt-0">
          <v-text-field
            v-model.number="customFocusTime"
            label="Focus Duration (minutes)"
            type="number"
            variant="outlined"
            rounded="lg"
            class="mb-4"
            min="1"
            max="480"
          />
          
          <v-text-field
            v-model.number="customBreakTime"
            label="Break Duration (minutes)"
            type="number"
            variant="outlined"
            rounded="lg"
            min="1"
            max="60"
          />
        </v-card-text>
        
        <v-card-actions class="pa-6 pt-0">
          <v-spacer />
          <v-btn
            variant="text"
            @click="settingsDialog = false"
            class="text-none"
          >
            Cancel
          </v-btn>
          <v-btn
            color="primary"
            variant="flat"
            @click="saveSettings"
            class="text-none"
          >
            Save
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Task Completion Dialog -->
    <v-dialog v-model="taskCompletionDialog" max-width="400px">
      <v-card rounded="xl">
        <v-card-title class="pa-6">
          <span class="text-h6">Session Complete! 🎉</span>
        </v-card-title>
        
        <v-card-text class="pa-6 pt-0">
          <p class="text-body-2 mb-4">Great focus session! Did you complete this task?</p>
          <p class="text-body-2 font-weight-medium">
            {{ tasksFromTracker.find(t => t.id === selectedTask)?.title }}
          </p>
        </v-card-text>
        
        <v-card-actions class="px-6 pb-6">
          <v-spacer />
          <v-btn
            variant="text"
            @click="dismissTaskCompletionDialog"
            class="text-none"
          >
            Not Yet
          </v-btn>
          <v-btn
            color="primary"
            variant="flat"
            @click="markTaskAsComplete"
            class="text-none"
          >
            Yes, Complete Task!
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
    
  </div>
</template>

<style scoped>

.timer-page {
  position: relative;
  min-height: 100vh;
  transition: all 0.3s ease;
  /* Remove all v-binds from here */
  background-color: var(--v-theme-surface-light) !important;
}

/* NEW: Background element for the blurred, non-running state */
.main-page-blurred-background {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 1; /* Behind all content cards (z-index: 10) */
  
  /* Bind the source and other properties */
  background-image: v-bind('blurredBackgroundStyle.backgroundImage');
  background-size: v-bind('blurredBackgroundStyle.backgroundSize');
  background-position: v-bind('blurredBackgroundStyle.backgroundPosition');
  background-attachment: v-bind('blurredBackgroundStyle.backgroundAttachment');
  
  /* Apply the visual effects here, only to this layer */
  filter: blur(3px) brightness(0.9);
  opacity: 0.4; 
  animation-play-state: paused;
}

/* Ensure your main content cards are opaque */
.timer-card, .details-card, .streaks-card {
  background-color: rgba(255, 255, 255, 0.95) !important; /* Make sure they are opaque */
  position: relative;
  z-index: 10; /* Ensure content is on top */
}

.fullscreen-mode {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 100;
  overflow-y: auto;
  /* Reset background properties when in fullscreen, letting .fullscreen-gif-background take over */
  background-image: none !important; 
  filter: none !important;
  opacity: 1 !important;
}

/* NEW: Fullscreen GIF background element */
.fullscreen-gif-background {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 1; /* Below the main card (.timer-card has z-index: 10) */
  /* Use the path for the active GIF */
  background-image: v-bind('getCurrentBackground().path ? `url(${getCurrentBackground().path})` : `none`');
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  filter: none; /* No blur/fade when running */
  opacity: 1;
}


.fullscreen-container {
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
}

.fullscreen-card {
  max-width: 900px;
  margin: 0 auto;
}

.timer-card, .details-card, .streaks-card {
  /* IMPORTANT: Give cards a slight opacity to see the background through, but maintain readability */
  background-color: rgba(255, 255, 255, 0.9) !important; 
  border: 1px solid var(--surface-lighter);
  transition: all 0.3s ease;
  position: relative;
  z-index: 10;
}

.background-select-card {
  height: 100%;
  background: rgba(255, 255, 255, 0.95) !important; 
  border: 1px solid var(--surface-lighter);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  min-height: 80px;
  transition: all 0.2s ease;
}

.background-select-card:hover {
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  transform: translateY(-1px);
}

[data-theme="dark"] .background-select-card {
  background: rgba(30, 30, 30, 0.95) !important;
}

/* Dark mode adjustment for card opacity */
[data-theme="dark"] .timer-card, 
[data-theme="dark"] .details-card, 
[data-theme="dark"] .streaks-card {
  background-color: rgba(30, 30, 30, 0.9) !important; 
}


.session-box, .tips-section {
  background: var(--surface-light) !important;
  border: 1px solid var(--surface-lighter);
}

.timer-title, .session-title, .tips-title, .streaks-title {
  color: var(--primary) !important;
}

.timer-display {
  font-size: 72px;
  font-weight: 600;
  color: var(--primary) !important;
  letter-spacing: -2px;
  transition: font-size 0.3s ease;
}

.timer-display-large {
  font-size: 120px !important;
}

.stat-number, .streak-number {
  color: var(--primary) !important;
}

.stats-divider {
  border-top: 1px solid var(--surface-lighter);
}

.reset-btn {
  color: var(--primary) !important;
}

.cursor-pointer {
  cursor: pointer;
}

ul {
  padding-left: 20px;
}

li {
  margin-bottom: 4px;
}

.falling-leaves-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 20;
}

.leaf {
  position: absolute;
  top: -50px;
  font-size: 28px;
  animation: fall linear infinite;
}

@keyframes fall {
  0% {
    transform: translateY(0) rotate(0deg);
    opacity: 0.9;
  }
  100% {
    transform: translateY(110vh) rotate(360deg);
    opacity: 0.2;
  }
}

.v-list-item {
  border: 1px solid var(--surface-lighter);
}

/* High specificity selectors to override Vuetify defaults */
.v-overlay .v-overlay__content {
  background: var(--surface) !important;
}


:deep(.v-overlay__scrim) {
  background: rgba(0, 0, 0, 0.5) !important;
}

/* GLOBAL FIX: Apply to ALL select/combobox menus on page */
.v-application .v-menu > .v-overlay__content,
.v-application .v-select__menu > .v-overlay__content,
.v-application .v-combobox__menu > .v-overlay__content,
.v-application .v-autocomplete__menu > .v-overlay__content {
  background: var(--surface) !important;
}
/* ... (Rest of existing opacity fix styles) ... */

/* Remove tab navigation arrows */
.v-tabs__wrapper {
  overflow: visible !important;
}

:deep(.v-slide-group__prev),
:deep(.v-slide-group__next) {
  display: none !important;
}

/* Ensure all form inputs in dialogs have proper styling */
.v-dialog .v-field {
  background: transparent !important;
}

.v-dialog .v-field__outline {
  opacity: 1 !important;
}
</style>

<style>
/* ========================================= */
/* UNSCOPED GLOBAL STYLES - CRITICAL FIXES  */
/* ========================================= */

/* 1. FORCE ALL DROPDOWN MENUS TO BE OPAQUE */
/* Target every possible Vuetify menu selector */

/* Main overlay content */
.v-overlay.v-menu .v-overlay__content,
.v-overlay.v-menu .v-overlay__content .v-list,
.v-overlay.v-menu .v-overlay__content .v-card,
.v-overlay.v-menu .v-overlay__content .v-sheet {
  background: white !important;
  opacity: 1 !important;
}

[data-theme="dark"] .v-overlay.v-menu .v-overlay__content,
[data-theme="dark"] .v-overlay.v-menu .v-overlay__content .v-list,
[data-theme="dark"] .v-overlay.v-menu .v-overlay__content .v-card,
[data-theme="dark"] .v-overlay.v-menu .v-overlay__content .v-sheet {
  background: #1e1e1e !important;
  opacity: 1 !important;
}

/* Select menus specifically */
.v-menu.v-select__menu .v-overlay__content,
.v-menu.v-combobox__menu .v-overlay__content,
.v-menu.v-autocomplete__menu .v-overlay__content {
  background: white !important;
  opacity: 1 !important;
}

[data-theme="dark"] .v-menu.v-select__menu .v-overlay__content,
[data-theme="dark"] .v-menu.v-combobox__menu .v-overlay__content,
[data-theme="dark"] .v-menu.v-autocomplete__menu .v-overlay__content {
  background: #1e1e1e !important;
  opacity: 1 !important;
}

/* List items */
.v-menu .v-list,
.v-select__menu .v-list,
.v-combobox__menu .v-list,
.v-autocomplete__menu .v-list {
  background: white !important;
  opacity: 1 !important;
}

[data-theme="dark"] .v-menu .v-list,
[data-theme="dark"] .v-select__menu .v-list,
[data-theme="dark"] .v-combobox__menu .v-list,
[data-theme="dark"] .v-autocomplete__menu .v-list {
  background: #1e1e1e !important;
  opacity: 1 !important;
}

.v-menu .v-list-item,
.v-select__menu .v-list-item,
.v-combobox__menu .v-list-item,
.v-autocomplete__menu .v-list-item {
  background: transparent !important;
}

/* 2. FIX DIALOG BORDER RADIUS - NO MIXED EDGES */
.v-dialog .v-overlay__content {
  border-radius: 24px !important;
  overflow: hidden !important;
}

.v-dialog .v-overlay__content .v-card {
  border-radius: 24px !important;
  overflow: hidden !important;
}
.color-swatch {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  transition: transform 0.2s ease;
}

.color-swatch:hover {
  transform: scale(1.1);
}

.cursor-pointer {
  cursor: pointer;
}

/* 3. REMOVE LINE THROUGH LABEL IN V-SELECT */
.v-field--variant-outlined .v-label {
  background: transparent !important;
}

.v-field--variant-outlined.v-field--focused .v-label,
.v-field--variant-outlined.v-field--active .v-label {
  background: white !important;
  padding: 0 4px !important;
}

[data-theme="dark"] .v-field--variant-outlined.v-field--focused .v-label,
[data-theme="dark"] .v-field--variant-outlined.v-field--active .v-label {
  background: #1e1e1e !important;
  padding: 0 4px !important;
}
</style>