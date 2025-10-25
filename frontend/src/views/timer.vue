<script setup>
import { ref, computed, onUnmounted, watch, onMounted } from 'vue'
import { useSubjects, useRecurringTopics } from '@/composables/useSubjects'

const { subjects, loading: subjectsLoading, fetchSubjects, createSubject, updateSubject, deleteSubject } = useSubjects()
const { topics: recurringTopics, loading: topicsLoading, fetchTopics, createTopic, updateTopic, deleteTopic } = useRecurringTopics()

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
const sessionNotes = ref('')

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

// REMOVED: Auto-filter topics by subject - now we load ALL topics always
// watch(selectedSubject, async (newSubjectId) => {
//   if (newSubjectId) {
//     await loadRecurringTopics(newSubjectId)
//   } else {
//     recurringTopics.value = []
//   }
// })

onMounted(async () => {
  await loadSubjects()
  await loadAllRecurringTopics() // NEW: Load ALL topics on mount
})

// ============================================================================
// SUBJECTS FUNCTIONS
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
// RECURRING TOPICS FUNCTIONS
// ============================================================================

// NEW: Load ALL topics regardless of subject
async function loadAllRecurringTopics() {
  try {
    // Call fetchTopics with no subject filter (pass null or don't filter)
    await fetchTopics() // This should fetch all topics
    allRecurringTopics.value = recurringTopics.value
  } catch (error) {
    console.error('Error loading topics:', error)
  }
}

async function loadRecurringTopics(subjectId) {
  try {
    await fetchTopics(subjectId)
  } catch (error) {
    console.error('Error loading topics:', error)
  }
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
// TIMER FUNCTIONS
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

function dispatchStudySessionCompleted() {
  console.log('✅ Focus session completed! Dispatching event...');
  
  const subjectName = selectedSubject.value 
    ? subjects.value.find(s => s.id === selectedSubject.value)?.name 
    : null
  
  // Get topic title - could be manual text or a topic ID
  let taskDisplay = selectedTopic.value
  if (selectedTopic.value) {
    // Check if it's a topic ID from the dropdown
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
      notes: sessionNotes.value,
      timestamp: new Date()
    }
  }))
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
    <div v-if="running" class="falling-leaves-background"></div>

    <v-container :class="['py-8', { 'fullscreen-container': running }]" :style="running ? 'max-width: 100%;' : 'max-width: 1400px;'">
      <v-row>
        <!-- Main Timer Card -->
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

        <!-- Session Details Sidebar -->
        <v-col v-if="!running" cols="12" md="5" lg="4">
          <v-card rounded="xl" elevation="0" class="details-card pa-6 mb-4">
            <v-tabs v-model="activeTab" bg-color="transparent" color="primary" class="mb-4" show-arrows="false">
              <v-tab value="session">Session</v-tab>
              <v-tab value="subjects">Subjects</v-tab>
              <v-tab value="topics">Topics</v-tab>
            </v-tabs>

            <v-window v-model="activeTab">
              <!-- Session Tab -->
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
                  <label class="text-body-2 font-weight-medium mb-2 d-block">Task/Topic</label>
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

              <!-- Subjects Tab -->
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

              <!-- Topics Tab -->
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

          <!-- Daily Streaks Card -->
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
        </v-col>
      </v-row>
    </v-container>

    <div v-if="running" class="falling-leaves-overlay">
      <div class="leaf" v-for="i in 20" :key="i" :style="{ 
        left: `${Math.random() * 100}%`, 
        animationDelay: `${Math.random() * 8}s`,
        animationDuration: `${10 + Math.random() * 6}s`
      }">🍂</div>
    </div>

    <!-- Settings Dialog -->
    <v-dialog v-model="settingsDialog" max-width="500">
      <v-card rounded="xl">
        <v-card-title class="text-h6 font-weight-medium pa-6 pb-4 modal-title">
          Timer Settings
        </v-card-title>
        <v-card-text class="px-6 pb-6">
          <div class="mb-6">
            <label class="text-body-2 font-weight-medium mb-2 d-block">Focus Length (minutes)</label>
            <v-text-field v-model="customFocusTime" type="number" density="comfortable" 
                          variant="outlined" rounded="lg" hide-details/>
          </div>

          <div class="mb-6">
            <label class="text-body-2 font-weight-medium mb-2 d-block">Break Length (minutes)</label>
            <v-text-field v-model="customBreakTime" type="number" density="comfortable" 
                          variant="outlined" rounded="lg" hide-details/>
          </div>

          <v-btn block color="primary" rounded="lg" size="large" class="text-none" @click="saveSettings">
            Save Settings
          </v-btn>
        </v-card-text>
      </v-card>
    </v-dialog>

    <!-- Subject Dialog -->
    <v-dialog v-model="subjectDialog" max-width="600">
      <v-card rounded="xl">
        <v-card-title class="text-h6 font-weight-medium pa-6 pb-4">
          {{ editingSubject ? 'Edit Subject' : 'New Subject' }}
        </v-card-title>
        <v-card-text class="px-6 pb-6">
          <v-text-field
            v-model="subjectForm.name"
            label="Subject Name"
            variant="outlined"
            rounded="lg"
            class="mb-4"
            hide-details
          />

          <div class="mb-4">
            <label class="text-body-2 font-weight-medium mb-2 d-block">Color</label>
            <div class="d-flex ga-2 flex-wrap">
              <v-btn
                v-for="color in colorOptions"
                :key="color.value"
                :color="color.value"
                :variant="subjectForm.color === color.value ? 'flat' : 'outlined'"
                size="large"
                icon
                @click="subjectForm.color = color.value"
              />
            </div>
          </div>

          <div class="mb-4">
            <label class="text-body-2 font-weight-medium mb-2 d-block">Icon</label>
            <div class="d-flex ga-2 flex-wrap">
              <v-btn
                v-for="icon in iconOptions"
                :key="icon"
                :variant="subjectForm.icon === icon ? 'flat' : 'outlined'"
                :color="subjectForm.icon === icon ? 'primary' : 'default'"
                size="large"
                @click="subjectForm.icon = icon"
              >
                {{ icon }}
              </v-btn>
            </div>
          </div>

          <v-textarea
            v-model="subjectForm.description"
            label="Description (optional)"
            variant="outlined"
            rounded="lg"
            rows="3"
            class="mb-4"
            hide-details
          />

          <div class="d-flex ga-2">
            <v-btn color="primary" variant="flat" block @click="saveSubject">
              {{ editingSubject ? 'Update' : 'Create' }} Subject
            </v-btn>
            <v-btn variant="text" @click="subjectDialog = false">Cancel</v-btn>
          </div>
        </v-card-text>
      </v-card>
    </v-dialog>

    <!-- Topic Dialog - UPDATED with optional subject -->
    <v-dialog v-model="topicDialog" max-width="600">
      <v-card rounded="xl">
        <v-card-title class="text-h6 font-weight-medium pa-6 pb-4">
          {{ editingTopic ? 'Edit Topic' : 'New Recurring Topic' }}
        </v-card-title>
        <v-card-text class="px-6 pb-6">
          <!-- UPDATED: Optional subject selection -->
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
            hide-details
            persistent-placeholder
            :menu-props="{ contentClass: 'dropdown-opaque' }"
          >
            <template v-slot:prepend-inner v-if="topicForm.subject_id">
              <span class="mr-2">{{ subjects.find(s => s.id === topicForm.subject_id)?.icon }}</span>
            </template>
          </v-select>

          <v-text-field
            v-model="topicForm.title"
            label="Topic Title"
            variant="outlined"
            rounded="lg"
            class="mb-4"
            hide-details
          />

          <v-textarea
            v-model="topicForm.description"
            label="Description (optional)"
            variant="outlined"
            rounded="lg"
            rows="3"
            class="mb-4"
            hide-details
          />

          <v-select
            v-model="topicForm.recurrence"
            :items="['daily', 'weekly', 'monthly']"
            label="Recurrence Pattern"
            variant="outlined"
            rounded="lg"
            class="mb-4"
            hide-details
            :menu-props="{ contentClass: 'dropdown-opaque' }"
          />

          <div class="d-flex ga-2">
            <v-btn color="primary" variant="flat" block @click="saveTopic">
              {{ editingTopic ? 'Update' : 'Create' }} Topic
            </v-btn>
            <v-btn variant="text" @click="topicDialog = false">Cancel</v-btn>
          </div>
        </v-card-text>
      </v-card>
    </v-dialog>
  </div>
</template>

<style scoped>
/* CRITICAL DROPDOWN OPACITY FIX - MUST BE AT TOP */
/* These rules override ALL Vuetify dropdown transparency */

.timer-page {
  position: relative;
  min-height: 100vh;
  transition: all 0.3s ease;
}

.fullscreen-mode {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 100;
  overflow-y: auto;
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
  background: var(--surface) !important;
  border: 1px solid var(--surface-lighter);
  transition: all 0.3s ease;
  position: relative;
  z-index: 10;
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

.falling-leaves-background {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 1;
  background: linear-gradient(135deg, 
    rgba(255, 245, 230, 0.4) 0%, 
    rgba(255, 229, 204, 0.4) 25%, 
    rgba(255, 218, 179, 0.4) 50%, 
    rgba(255, 207, 153, 0.4) 75%, 
    rgba(255, 194, 128, 0.4) 100%);
}

[data-theme="dark"] .falling-leaves-background {
  background: linear-gradient(135deg, 
    rgba(42, 24, 16, 0.5) 0%, 
    rgba(61, 36, 21, 0.5) 25%, 
    rgba(74, 45, 26, 0.5) 50%, 
    rgba(87, 54, 31, 0.5) 75%, 
    rgba(100, 64, 36, 0.5) 100%);
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

/* FIX: Dropdown transparency - make ALL backgrounds opaque */
/* High specificity selectors to override Vuetify defaults */
.v-overlay .v-overlay__content {
  background: var(--surface) !important;
}

.v-menu > .v-overlay__content {
  background: var(--surface) !important;
}

.v-menu .v-list {
  background: var(--surface) !important;
}

.v-menu .v-list-item {
  background: var(--surface) !important;
}

.v-select .v-overlay__content {
  background: var(--surface) !important;
}

.v-select .v-list {
  background: var(--surface) !important;
}

.v-select .v-list-item {
  background: var(--surface) !important;
}

.v-combobox .v-overlay__content {
  background: var(--surface) !important;
}

.v-combobox .v-list {
  background: var(--surface) !important;
}

.v-combobox .v-list-item {
  background: var(--surface) !important;
}

/* Deep selectors for nested components */
:deep(.v-overlay__content) {
  background: var(--surface) !important;
}

:deep(.v-menu .v-overlay__content) {
  background: var(--surface) !important;
}

:deep(.v-list) {
  background: var(--surface) !important;
}

:deep(.v-list-item) {
  background: var(--surface) !important;
}

:deep(.v-select__content) {
  background: var(--surface) !important;
}

:deep(.v-select__menu-content) {
  background: var(--surface) !important;
}

:deep(.v-combobox__content) {
  background: var(--surface) !important;
}

:deep(.v-combobox__menu-content) {
  background: var(--surface) !important;
}

:deep(.v-autocomplete__content) {
  background: var(--surface) !important;
}

:deep(.v-menu__content) {
  background: var(--surface) !important;
}

/* Additional fix for dropdown content class */
:deep(.dropdown-opaque) {
  background: var(--surface) !important;
}

:deep(.dropdown-opaque .v-list) {
  background: var(--surface) !important;
}

:deep(.dropdown-opaque .v-list-item) {
  background: var(--surface) !important;
}

:deep(.dropdown-opaque .v-overlay__content) {
  background: var(--surface) !important;
}

/* Force opaque for ALL vuetify overlays on this page */
:deep(.v-overlay__scrim) {
  background: rgba(0, 0, 0, 0.5) !important;
}

:deep(.v-field__overlay) {
  background: var(--surface) !important;
}

/* Target dialog overlays specifically */
.v-dialog .v-overlay__content {
  background: var(--surface) !important;
}

.v-dialog .v-card {
  background: var(--surface) !important;
}

/* Menu content wrappers */
.v-overlay--active .v-overlay__content > .v-card,
.v-overlay--active .v-overlay__content > .v-sheet,
.v-overlay--active .v-overlay__content > .v-list {
  background: var(--surface) !important;
}

/* GLOBAL FIX: Apply to ALL select/combobox menus on page */
.v-application .v-menu > .v-overlay__content,
.v-application .v-select__menu > .v-overlay__content,
.v-application .v-combobox__menu > .v-overlay__content,
.v-application .v-autocomplete__menu > .v-overlay__content {
  background: var(--surface) !important;
}

.v-application .v-menu .v-list,
.v-application .v-select__menu .v-list,
.v-application .v-combobox__menu .v-list,
.v-application .v-autocomplete__menu .v-list {
  background: var(--surface) !important;
}

.v-application .v-menu .v-list-item,
.v-application .v-select__menu .v-list-item,
.v-application .v-combobox__menu .v-list-item,
.v-application .v-autocomplete__menu .v-list-item {
  background: var(--surface) !important;
}

/* Force all overlays on this component to be opaque */
.timer-page .v-overlay__content,
.timer-page .v-menu,
.timer-page .v-list,
.timer-page .v-list-item {
  background: var(--surface) !important;
}

/* CRITICAL: Force dropdown opacity with highest specificity */
.v-overlay .v-menu__content,
.v-overlay .v-select__content,
.v-overlay .v-autocomplete__content {
  background-color: var(--surface) !important;
  opacity: 1 !important;
}

.v-menu__content .v-list,
.v-select__content .v-list,
.v-autocomplete__content .v-list {
  background-color: var(--surface) !important;
  opacity: 1 !important;
}

.v-menu__content .v-list-item,
.v-select__content .v-list-item,
.v-autocomplete__content .v-list-item {
  background-color: var(--surface) !important;
}

/* Fix dialog card border radius - ensure no mixed edges */
.v-dialog > .v-overlay__content > .v-card {
  border-radius: 24px !important;
  overflow: hidden;
}

.v-dialog .v-card-title,
.v-dialog .v-card-text {
  background: var(--surface) !important;
}

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
/* UNSCOPED GLOBAL STYLES - CRITICAL FIXES  */
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