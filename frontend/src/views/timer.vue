<script setup>
import { ref, computed, onUnmounted, watch, onMounted } from 'vue'
import { useSubjects, useRecurringTopics } from '@/composables/useSubjects'
// NEW: Background imports
import { useBackground } from '@/composables/useBackgrounds'
import BackgroundsGallery from '@/components/BackgroundsGallery.vue'
import { useCoins } from '@/composables/useCoins.js'
import { api } from '@/lib/api.js'
import AnimatedCoin from '@/components/AnimatedCoin.vue'
import confetti from 'canvas-confetti'

const { subjects, loading: subjectsLoading, fetchSubjects, createSubject, updateSubject, deleteSubject } = useSubjects()
const { topics: recurringTopics, loading: topicsLoading, fetchTopics, createTopic, updateTopic, deleteTopic } = useRecurringTopics()
// NEW: Use Background composable
const { selectedBackgroundId, getCurrentBackground } = useBackground()
const { coins, updateCoins } = useCoins()

const presets = { 'Focus': 25, 'Break': 5 }
const mode = ref('Focus')
const minutes = ref(presets[mode.value])
const timeLeft = ref(presets[mode.value] * 60)
const running = ref(false)
const settingsDialog = ref(false)
const customFocusTime = ref(25)
const customBreakTime = ref(5)
let t = null

// Session tracking variables
const sessionStartTime = ref(null)
const pauseCount = ref(0)
const totalPausedDurationMs = ref(0)
const pauseStartTime = ref(null)
const currentSessionId = ref(null)
const completionDialog = ref(false)
const recentlyEarnedCoins = ref(0)
const sessionJustCompleted = ref(false)

// Session Details Data
const selectedSubject = ref(null)
const selectedTopic = ref('') // Can be manual text or selected topic ID
const selectedTask = ref(null) // Reference to task tracker task
const sessionNotes = ref('')

// Task completion dialog
const taskCompletionDialog = ref(false)
const tasksFromTracker = ref([])
const isMarkingTaskComplete = ref(false)

// Timer stats
const sessionsToday = ref(0)
const focusScore = ref(0)

// Error message for missing session details
const showStartError = ref(false)

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
    const data = await api.get('/api/tasks')
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

// Computed property for potential coins based on timer duration (50 coins per 25 minutes)
const potentialCoins = computed(() => {
  if (mode.value === 'Focus') {
    return Math.floor(minutes.value * 2)
  }
  return 0
})

// Computed property for session status message
const sessionStatusMessage = computed(() => {
  if (sessionJustCompleted.value) {
    return 'Session has just been completed'
  }
  if (pauseStartTime.value && !running.value) {
    return 'Session has been paused'
  }
  if (running.value) {
    return 'Stay focused!'
  }
  return 'Set your timer'
})

// Computed properties for session subject and task names
const sessionSubjectName = computed(() => {
  if (!selectedSubject.value) return null
  if (selectedSubject.value === 'MISCELLANEOUS') return 'Miscellaneous'
  return subjects.value.find(s => s.id === selectedSubject.value)?.name
})

const sessionTaskTitle = computed(() => {
  if (!selectedTask.value) return null
  return tasksFromTracker.value.find(t => t.id === selectedTask.value)?.title
})

// Filter out completed tasks and filter by selected subject
const availableTasks = computed(() => {
  let filtered = tasksFromTracker.value.filter(task => task.status !== 'done')
  
  // Filter by selected subject if one is selected (and not Miscellaneous)
  if (selectedSubject.value && selectedSubject.value !== 'MISCELLANEOUS') {
    filtered = filtered.filter(task => task.subjectId === selectedSubject.value)
  }
  
  return filtered
})

// Watch for changes in available tasks - clear selectedTask if it becomes unavailable
watch([availableTasks, selectedTask], ([available, selected]) => {
  if (selected && !available.find(t => t.id === selected)) {
    // Selected task is no longer available (was marked as done), clear it
    selectedTask.value = null
  }
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

// Computed subjects list with "Miscellaneous" always included
const subjectsWithMiscellaneous = computed(() => {
  const miscOption = {
    id: 'MISCELLANEOUS',
    name: 'Miscellaneous',
    icon: '📋',
    color: '#9E9E9E',
    description: 'General sessions'
  }
  return [miscOption, ...subjects.value]
})

// Check if Miscellaneous is selected
const isMiscellaneousSelected = computed(() => {
  return selectedSubject.value === 'MISCELLANEOUS'
})

// Watch for subject changes - clear topic and task when switching to Miscellaneous or when task doesn't match new subject
watch(selectedSubject, (newSubject, oldSubject) => {
  if (newSubject === 'MISCELLANEOUS') {
    // Clear topic and task when Miscellaneous is selected
    selectedTopic.value = ''
    selectedTask.value = null
  } else if (newSubject && oldSubject && newSubject !== oldSubject) {
    // Subject changed - clear task if it doesn't belong to the new subject
    if (selectedTask.value) {
      const task = tasksFromTracker.value.find(t => t.id === selectedTask.value)
      if (task && task.subjectId !== newSubject) {
        selectedTask.value = null
      }
    }
    // Clear topic when subject changes (topics are subject-specific)
    selectedTopic.value = ''
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
  await loadTodayStats()
})

async function loadTodayStats() {
  try {
    const data = await api.get('/api/study-sessions/timer-stats')
    console.log('DEBUG: Timer stats response:', data)
    sessionsToday.value = data.sessions_completed || 0
    
    // Use focus score from backend which calculates:
    // (total_started_seconds - total_paused_seconds) / total_started_seconds * 100
    // If paused seconds >= total session seconds, it returns 0
    console.log('DEBUG: focus_score from backend:', data.focus_score)
    console.log('DEBUG: total_started_minutes:', data.total_started_minutes)
    console.log('DEBUG: total_paused_minutes:', data.total_paused_minutes)
    
    if (data.focus_score !== undefined && data.focus_score !== null) {
      console.log('DEBUG: Using backend focus_score:', data.focus_score)
      focusScore.value = data.focus_score
    } else {
      console.log('DEBUG: Backend focus_score not available, using fallback calculation')
      // Fallback calculation if backend doesn't provide focus_score
      const totalStartedSeconds = (data.total_started_minutes || 0) * 60
      const totalPausedSeconds = (data.total_paused_minutes || 0) * 60
      
      if (totalStartedSeconds > 0) {
        // If paused seconds >= total session seconds, focus score is 0%
        if (totalPausedSeconds >= totalStartedSeconds) {
          focusScore.value = 0
        } else {
          // Focus score = (timer running seconds - paused seconds) / total session seconds * 100
          const runningSeconds = totalStartedSeconds - totalPausedSeconds
          const score = (runningSeconds / totalStartedSeconds) * 100
          focusScore.value = Math.round(score * 10) / 10 // Round to 1 decimal place
        }
      } else {
        // No sessions started, show default 100%
        focusScore.value = 100
      }
    }
    console.log('DEBUG: Final focusScore.value:', focusScore.value)
  } catch (error) {
    console.error('Error loading today stats:', error)
    sessionsToday.value = 0
    focusScore.value = 100
  }
}

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
  
  isMarkingTaskComplete.value = true
  
  try {
    // Update task status to 'done' regardless of current status (todo or in_progress)
    await api.patch(`/api/tasks/${selectedTask.value}`, {
      status: 'done'
    })
    
    // Clear the selected task since it's now completed and won't be in the dropdown
    selectedTask.value = null
    
    // Refresh tasks list to reflect the update
    await fetchTasksFromTracker()
    
    // Close the dialog after successful update
    taskCompletionDialog.value = false
    
    // Show success feedback
    console.log('Task marked as completed successfully!')
  } catch (error) {
    console.error('Error updating task:', error)
    const errorMessage = error?.message || error?.detail || 'Failed to update task status. Please try again.'
    alert(errorMessage)
  } finally {
    isMarkingTaskComplete.value = false
  }
}

function dismissTaskCompletionDialog() {
  taskCompletionDialog.value = false
  resetCompletionMessage()
}

function closeCompletionDialog() {
  completionDialog.value = false
  resetCompletionMessage()
}

function resetCompletionMessage() {
  // Reset completion message after a short delay to allow user to see it
  setTimeout(() => {
    sessionJustCompleted.value = false
  }, 2000)
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
  if (timeLeft.value <= 0) return // Disable if timer is at 0
  
  // Check if session details are configured
  if (!selectedSubject.value) {
    showStartError.value = true
    // Auto-hide after 3 seconds
    setTimeout(() => {
      showStartError.value = false
    }, 3000)
    return
  }
  
  // Reset coin message when starting a new session
  recentlyEarnedCoins.value = 0
  // Reset completion message when starting/resuming
  sessionJustCompleted.value = false
  
  // If resuming from pause, calculate pause duration
  if (pauseStartTime.value) {
    const pauseDuration = Date.now() - pauseStartTime.value
    totalPausedDurationMs.value += pauseDuration
    pauseStartTime.value = null
    
    // Update session status to active
    if (currentSessionId.value) {
      updateSessionStatus('active')
    }
  }
  
  // If starting a new session, record start time
  if (!sessionStartTime.value) {
    sessionStartTime.value = Date.now()
    startNewSession()
  }
  
  running.value = true
  t = setInterval(() => { 
    timeLeft.value--
    if (timeLeft.value <= 0){ 
      clearInterval(t)
      running.value = false
      timeLeft.value = 0
      
      if (mode.value === 'Focus') {
        sessionJustCompleted.value = true
        dispatchStudySessionCompleted()
      }
    } 
  }, 1000) 
}

async function startNewSession() {
  try {
    // Get subject name - handle Miscellaneous
    let subjectName = null
    if (selectedSubject.value === 'MISCELLANEOUS') {
      subjectName = 'Miscellaneous'
    } else if (selectedSubject.value) {
      subjectName = subjects.value.find(s => s.id === selectedSubject.value)?.name
    }

    // Get topic/task display - only if not Miscellaneous
    let taskDisplay = null
    if (!isMiscellaneousSelected.value && selectedTopic.value) {
      const topic = allRecurringTopics.value.find(t => t.id === selectedTopic.value)
      if (topic) {
        taskDisplay = topic.title
      } else {
        taskDisplay = selectedTopic.value // Manual text entry
      }
    }

    // Only include task_id if not Miscellaneous and task is selected
    const taskId = isMiscellaneousSelected.value ? null : selectedTask.value

    const response = await api.post('/api/study-sessions/start', {
      planned_duration_minutes: minutes.value,
      subject: subjectName,
      task: taskDisplay,
      task_id: taskId,
      notes: sessionNotes.value,
      session_type: mode.value.toLowerCase()
    })
    
    currentSessionId.value = response.id
  } catch (error) {
    console.error('Error starting session:', error)
  }
}

async function updateSessionStatus(status) {
  if (!currentSessionId.value) return
  
  try {
    const updateData = {
      status: status
    }
    
    // If pausing, also update time remaining
    if (status === 'paused') {
      updateData.time_remaining_seconds = timeLeft.value
    }
    
    await api.patch(`/api/study-sessions/${currentSessionId.value}`, updateData)
  } catch (error) {
    console.error('Error updating session status:', error)
  }
}

async function dispatchStudySessionCompleted() {
  console.log('Focus session completed! Dispatching event...');

  // Calculate actual session duration
  const totalDurationMs = sessionStartTime.value ? Date.now() - sessionStartTime.value : minutes.value * 60 * 1000
  const totalPausedMs = pauseStartTime.value 
    ? totalPausedDurationMs.value + (Date.now() - pauseStartTime.value)
    : totalPausedDurationMs.value
  const actualDurationMs = totalDurationMs - totalPausedMs
  // Ensure minimum duration of 1 minute (API requirement)
  const actualDurationMinutes = Math.max(1, Math.floor(actualDurationMs / 60000))

  // Get subject name - handle Miscellaneous
  let subjectName = null
  if (selectedSubject.value === 'MISCELLANEOUS') {
    subjectName = 'Miscellaneous'
  } else if (selectedSubject.value) {
    subjectName = subjects.value.find(s => s.id === selectedSubject.value)?.name
  }

  // Get topic title - only if not Miscellaneous
  let taskDisplay = null
  if (!isMiscellaneousSelected.value && selectedTopic.value) {
    const topic = allRecurringTopics.value.find(t => t.id === selectedTopic.value)
    if (topic) {
      taskDisplay = topic.title
    } else {
      taskDisplay = selectedTopic.value // Manual text entry
    }
  }

  // Log session to API
  try {
    if (currentSessionId.value) {
      // Update existing session to completed
      // Ensure minimum duration of 1 minute
      const validDuration = Math.max(1, actualDurationMinutes)
      await api.patch(`/api/study-sessions/${currentSessionId.value}`, {
        status: 'completed',
        actual_duration_minutes: validDuration,
        time_remaining_seconds: 0,
        pause_count: pauseCount.value,
        total_paused_duration_minutes: Math.round(totalPausedMs / 60000 * 10) / 10
      })
    } else {
      // Create new completed session (fallback if session wasn't started properly)
      // Use planned duration if actual duration is invalid
      const durationToUse = actualDurationMinutes > 0 ? actualDurationMinutes : minutes.value
      const taskId = isMiscellaneousSelected.value ? null : selectedTask.value
      
      await api.post('/api/study-sessions/', {
        duration_minutes: Math.max(1, durationToUse), // Ensure at least 1 minute
        subject: subjectName,
        task: taskDisplay,
        task_id: taskId,
        notes: sessionNotes.value,
        session_type: mode.value.toLowerCase()
      })
    }
  } catch (error) {
    console.error('Error logging study session:', error)
    // Log more details about the error
    if (error.response) {
      console.error('Error response:', error.response.data)
      console.error('Error status:', error.response.status)
    }
  }

  // Dispatch event for other components
  window.dispatchEvent(new CustomEvent('study-session-completed', {
    detail: {
      duration: actualDurationMinutes,
      mode: mode.value,
      subject: subjectName,
      task: taskDisplay,
      task_id: selectedTask.value,
      notes: sessionNotes.value,
      pause_count: pauseCount.value,
      total_paused_duration_minutes: Math.round(totalPausedMs / 60000 * 10) / 10,
      timestamp: new Date()
    }
  }))

  // Award coins for completing study session (50 coins per 25 minutes = 2 coins per minute)
  try {
    const durationMinutes = actualDurationMinutes || minutes.value
    const coinsEarned = Math.floor(durationMinutes * 2)

    console.log(`Calculating coins: ${durationMinutes} minutes × 2 = ${coinsEarned} coins`)

    if (coinsEarned > 0) {
      const currentCoins = coins.value || 0
      const newCoins = currentCoins + coinsEarned
      console.log(`Updating coins: ${currentCoins} + ${coinsEarned} = ${newCoins}`)

      const result = await updateCoins(newCoins)
      if (result.success) {
        console.log(`Study session rewarded ${coinsEarned} coins! Total: ${newCoins}`)
        recentlyEarnedCoins.value = coinsEarned
      }
    } else {
      console.log('No coins earned (duration too short)')
      recentlyEarnedCoins.value = 0
    }
  } catch (coinError) {
    console.error('Error awarding study session coins:', coinError)
    // Don't fail the session completion if coins fail to update
    recentlyEarnedCoins.value = 0
  }

  // Show task completion dialog if task was selected, otherwise show completion modal
  if (selectedTask.value) {
    triggerCelebration()
    showTaskCompletionDialog()
  } else {
    completionDialog.value = true
    triggerCelebration()
  }
  
  // Refresh today's stats after session completion
  await loadTodayStats()
  
  // Reset session tracking
  sessionStartTime.value = null
  pauseCount.value = 0
  totalPausedDurationMs.value = 0
  pauseStartTime.value = null
  currentSessionId.value = null
}

function triggerCelebration() {
  // Main confetti burst
  confetti({
    particleCount: 150,
    spread: 120,
    origin: { y: 0.6 },
    colors: ['#5a8a7a', '#6A7A5A', '#AAC4BC', '#FFD700', '#FF69B4']
  })
  
  // Side bursts
  setTimeout(() => {
    confetti({
      particleCount: 80,
      angle: 60,
      spread: 80,
      origin: { x: 0 },
      colors: ['#5a8a7a', '#AAC4BC', '#FFD700']
    })
  }, 200)
  
  setTimeout(() => {
    confetti({
      particleCount: 80,
      angle: 120,
      spread: 80,
      origin: { x: 1 },
      colors: ['#5a8a7a', '#AAC4BC', '#FFD700']
    })
  }, 400)
  
  // Additional burst
  setTimeout(() => {
    confetti({
      particleCount: 30,
      spread: 100,
      origin: { y: 0.6 },
      shapes: ['circle'],
      scalar: 2,
      colors: ['#FF69B4', '#FFD700', '#98FB98']
    })
  }, 300)
}

function stop(){ 
  running.value = false
  clearInterval(t) 
  
  // Track pause
  if (sessionStartTime.value && !pauseStartTime.value) {
    pauseCount.value++
    pauseStartTime.value = Date.now()
    
    // Update session status to paused
    if (currentSessionId.value) {
      updateSessionStatus('paused')
    }
  }
}

async function reset(){ 
  stop()
  timeLeft.value = minutes.value * 60
  
  // Cancel current session if it exists
  if (currentSessionId.value) {
    try {
      await api.patch(`/api/study-sessions/${currentSessionId.value}`, {
        status: 'cancelled'
      })
    } catch (error) {
      console.error('Error cancelling session:', error)
    }
  }
  
  // Reset session tracking
  sessionStartTime.value = null
  pauseCount.value = 0
  totalPausedDurationMs.value = 0
  pauseStartTime.value = null
  currentSessionId.value = null
  recentlyEarnedCoins.value = 0 // Reset coin message
  sessionJustCompleted.value = false // Reset completion message
}

function openSettings() {
  settingsDialog.value = true
}

function saveSettings() {
  customFocusTime.value = parseInt(customFocusTime.value) || 25
  customBreakTime.value = parseInt(customBreakTime.value) || 5
  presets['Focus'] = customFocusTime.value
  presets['Break'] = customBreakTime.value
  
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
    
    <v-container :class="['timer-container py-4 py-md-8', { 'fullscreen-container': running }]" :style="running ? 'max-width: 100%;' : 'max-width: 1400px;'">
      <v-row justify="center" class="ma-0">
        <v-col cols="12" :md="running ? 12 : 8" :lg="running ? 12 : 8" class="pa-0">
          <v-card rounded="xl" elevation="0" :class="['timer-card', { 'fullscreen-card': running }]" class="pa-6 pa-md-10">
            <div class="mb-2">
              <h2 class="text-h6 text-md-h5 text-primary font-weight-bold mb-1 px-2 px-md-0">Study Timer</h2>
              <p class="text-body-2 text-medium-emphasis">Focus with the Pomodoro Technique</p>
            </div>

            <div class="session-box mt-4 mt-md-6 pa-4 pa-md-6 rounded-lg">
              <div class="d-flex justify-space-between align-center mb-4 mb-md-6">
                <div>
                  <div class="text-subtitle-2 text-md-subtitle-2 text-medium-emphasis mb-1">Study Session</div>
                  <div class="text-caption text-medium-emphasis">{{ sessionStatusMessage }}</div>
                </div>
                <!-- Session Info Badge (shown when running, top right) -->
                <v-chip 
                  v-if="running && (sessionSubjectName || sessionTaskTitle)"
                  color="primary" 
                  size="small" 
                  variant="flat" 
                  class="px-3 px-md-4"
                >
                  <template v-if="sessionSubjectName && sessionTaskTitle">
                    {{ sessionSubjectName }} | {{ sessionTaskTitle }}
                  </template>
                  <template v-else-if="sessionSubjectName">
                    {{ sessionSubjectName }}
                  </template>
                  <template v-else-if="sessionTaskTitle">
                    {{ sessionTaskTitle }}
                  </template>
                </v-chip>
              </div>

              <div class="d-flex ga-2 mb-6 mb-md-8 flex-wrap justify-center">
                <v-chip v-for="m in Object.keys(presets)" :key="m"
                        :color="mode===m?'primary':'secondary'" 
                        :variant="mode===m?'flat':'tonal'"
                        class="cursor-pointer px-3 px-md-4"
                        size="small"
                        size-md="default"
                        @click="switchMode(m)">
                  {{ m }} • {{ presets[m] }}m
                </v-chip>
              </div>

              <div class="text-center mb-6 mb-md-8">
                <div :class="['timer-display', 'mb-4', { 'timer-display-large': running }]">{{ label }}</div>
                <v-progress-linear :model-value="pct" :height="$vuetify.display.mobile ? 6 : 8" rounded color="primary"
                                  bg-color="surface-lighter" class="mb-2"/>
              </div>

              <!-- Coin Reward Display -->
              <div v-if="!running && mode === 'Focus'" class="coin-reward-display mb-4">
                <AnimatedCoin :scale="1.5" :speed="8" />
                <div class="coin-info">
                  <div v-if="recentlyEarnedCoins > 0" class="coin-amount">You have just earned {{ recentlyEarnedCoins }} coins!</div>
                  <div v-else class="coin-amount">{{ potentialCoins }} coins</div>
                  <div v-if="recentlyEarnedCoins === 0" class="coin-note">Awarded on completion only</div>
                </div>
              </div>

              <div class="d-flex ga-2 ga-md-3 justify-center flex-wrap">
                <v-btn color="primary" :size="$vuetify.display.mobile ? 'default' : 'large'" rounded="lg" @click="start" :disabled="running || timeLeft <= 0" 
                       class="px-6 px-md-8 text-none" elevation="0">
                  <v-icon start>mdi-play</v-icon>Start
                </v-btn>
                <v-btn color="secondary" :size="$vuetify.display.mobile ? 'default' : 'large'" rounded="lg" variant="tonal" @click="stop" 
                       :disabled="!running" class="px-4 px-md-6 text-none" elevation="0">
                  <v-icon start>mdi-pause</v-icon>Pause
                </v-btn>
                <v-btn :size="$vuetify.display.mobile ? 'default' : 'large'" rounded="lg" variant="text" @click="reset" 
                       class="text-none reset-btn">
                  <v-icon start>mdi-restore</v-icon>Reset
                </v-btn>
              </div>

              <div v-if="!running" class="d-flex justify-space-around mt-6 mt-md-8 pt-4 pt-md-6 stats-divider">
                <div class="text-center">
                  <div class="text-h5 text-md-h4 font-weight-medium stat-number">{{ sessionsToday }}</div>
                  <div class="text-caption text-medium-emphasis">Sessions Today</div>
                </div>
                <div class="text-center">
                  <div class="text-h5 text-md-h4 font-weight-medium stat-number">{{ focusScore }}%</div>
                  <div class="text-caption text-medium-emphasis">Focus Score</div>
                </div>
              </div>
            </div>

            <div v-if="!running" class="tips-section mt-4 mt-md-6 pa-4 pa-md-6 rounded-lg">
              <div class="text-subtitle-2 font-weight-medium mb-3 mb-md-4 tips-title">Focus Tips</div>
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

        <v-col v-if="!running" cols="12" md="4" lg="4" class="pa-0">
          <v-card rounded="xl" elevation="0" class="details-card pa-4 pa-md-6 mb-4">
            <v-tabs v-model="activeTab" bg-color="transparent" color="primary" class="mb-4" show-arrows="false">
              <v-tab value="session">Session</v-tab>
              <v-tab value="subjects">Subjects</v-tab>
              <v-tab value="topics">Type</v-tab>
            </v-tabs>

            <v-window v-model="activeTab">
              <v-window-item value="session">
                <div class="text-subtitle-2 text-md-subtitle-1 font-weight-medium mb-1 session-title">Session Details</div>
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
                    :items="subjectsWithMiscellaneous"
                    item-title="name"
                    item-value="id"
                    density="comfortable" 
                    variant="outlined" 
                    rounded="lg" 
                    placeholder="Select subject (required)" 
                    hide-details
                    required
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
                </div>

                <div class="mb-4">
                  <label class="text-body-2 font-weight-medium mb-2 d-block">
                    Type (Recurring)
                    <span v-if="!isMiscellaneousSelected" class="text-error">*</span>
                  </label>
                  <v-combobox
                    v-model="selectedTopic"
                    :items="topicDropdownItems"
                    item-title="title"
                    item-value="value"
                    variant="outlined"
                    rounded="lg"
                    :placeholder="isMiscellaneousSelected ? 'Type or select a recurring type (optional)' : 'Type or select a recurring type'"
                    hide-details
                    density="comfortable"
                    :disabled="isMiscellaneousSelected"
                    :menu-props="{ contentClass: 'dropdown-opaque' }"
                  >
                    <template v-slot:item="{ props, item }">
                      <v-list-item v-bind="props">
                        <template v-slot:title>{{ item.raw.title }}</template>
                        <template v-slot:subtitle>{{ item.raw.subtitle }}</template>
                      </v-list-item>
                    </template>
                  </v-combobox>
                  <div v-if="isMiscellaneousSelected" class="text-caption text-medium-emphasis mt-1">
                    Restricted for miscellaneous sessions
                  </div>
                </div>

                <div class="mb-4">
                  <label class="text-body-2 font-weight-medium mb-2 d-block">
                    Task (from Task Tracker)
                    <span v-if="!isMiscellaneousSelected" class="text-error">*</span>
                  </label>
                  <v-select
                    v-model="selectedTask"
                    :items="availableTasks"
                    item-title="title"
                    item-value="id"
                    variant="outlined"
                    rounded="lg"
                    :placeholder="isMiscellaneousSelected ? 'Select a task (optional)' : selectedSubject ? 'Select a task for ' + (selectedSubject === 'MISCELLANEOUS' ? 'Miscellaneous' : subjects.find(s => s.id === selectedSubject)?.name) : 'Select a subject first'"
                    hide-details
                    density="comfortable"
                    clearable
                    :disabled="isMiscellaneousSelected || !selectedSubject"
                    :menu-props="{ contentClass: 'dropdown-opaque' }"
                  >
                    <template v-slot:item="{ props, item }">
                      <v-list-item v-bind="props">
                        <template v-slot:title>{{ item.raw.title }}</template>
                        <template v-slot:subtitle>
                          {{ item.raw.priority }} | {{ item.raw.subjectId ? (subjects.find(s => s.id === item.raw.subjectId)?.name || 'Unknown Subject') : 'No Subject' }}
                        </template>
                      </v-list-item>
                    </template>
                  </v-select>
                  <div v-if="isMiscellaneousSelected" class="text-caption text-medium-emphasis mt-1">
                    Restricted for miscellaneous sessions
                  </div>
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
                    <div class="text-subtitle-1 font-weight-medium session-title">Type of Work</div>
                    <p class="text-caption text-medium-emphasis">
                      {{ selectedSubject ? 'Types for selected subject' : 'Recurring types' }}
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
                    {{ selectedSubject ? 'No types for this subject yet' : 'No recurring types yet. Create one!' }}
                  </p>
                  <v-btn size="small" variant="text" color="primary" @click="openTopicDialog()">
                    Add a recurring type
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
          <span class="text-h6">{{ editingTopic ? 'Edit Topic' : 'New Recurring Work' }}</span>
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
            
            <v-text-field
              v-model="topicForm.title"
              label="Type of work e.g. Paper"
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
              :menu-props="{ contentClass: 'dropdown-opaque' }"
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

    <!-- Study Session Completion Dialog (shown when no task is selected) -->
    <v-dialog v-model="completionDialog" max-width="500px" persistent>
      <v-card rounded="xl">
        <v-card-title class="pa-6 text-center">
          <div class="w-100">
            <v-icon size="64" color="primary" class="mb-4">mdi-check-circle</v-icon>
            <div class="text-h5 font-weight-bold text-primary mb-2">Congrats on finishing a study session!</div>
            <div class="text-body-2 text-medium-emphasis">Great job staying focused! 🎉</div>
          </div>
        </v-card-title>
        
        <v-card-actions class="pa-6 pt-0 justify-center">
          <v-btn
            color="primary"
            variant="flat"
            size="large"
            rounded="lg"
            @click="closeCompletionDialog"
            class="text-none px-8"
          >
            Awesome!
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Start Error Message -->
    <div v-if="showStartError" class="start-error-message">
      Fill up your session details to start the timer!
    </div>

    <!-- Task Completion Dialog -->
    <v-dialog v-model="taskCompletionDialog" max-width="400px" persistent>
      <v-card rounded="xl">
        <v-card-title class="pa-6">
          <span class="text-h6 text-primary font-weight-bold">Session Complete! 🎉</span>
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
            :loading="isMarkingTaskComplete"
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

.timer-container {
  padding-left: 8px;
  padding-right: 8px;
  margin-left: auto;
  margin-right: auto;
}

@media (min-width: 960px) {
  .timer-container {
    padding-left: 16px;
    padding-right: 16px;
  }
}

.timer-card, .details-card {
  /* IMPORTANT: Give cards a slight opacity to see the background through, but maintain readability */
  background-color: rgba(255, 255, 255, 0.9) !important; 
  border: 1px solid var(--surface-lighter);
  transition: all 0.3s ease;
  position: relative;
  z-index: 10;
}

@media (min-width: 960px) {
  .timer-card:not(.fullscreen-card) {
    max-width: 900px;
    margin-left: auto;
    margin-right: auto;
  }
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
[data-theme="dark"] .details-card {
  background-color: rgba(30, 30, 30, 0.9) !important; 
}


.session-box, .tips-section {
  background: var(--surface-light) !important;
  border: 1px solid var(--surface-lighter);
}

.timer-title, .session-title, .tips-title {
  color: var(--primary) !important;
}

.timer-display {
  font-size: 56px;
  font-weight: 600;
  color: var(--primary) !important;
  letter-spacing: -2px;
  transition: font-size 0.3s ease;
}

@media (min-width: 600px) {
  .timer-display {
    font-size: 72px;
  }
}

.timer-display-large {
  font-size: 96px !important;
}

@media (min-width: 600px) {
  .timer-display-large {
    font-size: 120px !important;
  }
}

.stat-number {
  color: var(--primary) !important;
}

.stats-divider {
  border-top: 1px solid var(--surface-lighter);
}

/* Coin Reward Display */
.coin-reward-display {
  background: linear-gradient(135deg, rgba(255, 215, 0, 0.15), rgba(255, 215, 0, 0.1));
  border: 2px solid rgba(255, 215, 0, 0.4);
  border-radius: 12px;
  padding: 12px 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
  max-width: 320px;
  margin: 0 auto;
}

.coin-reward-display::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 215, 0, 0.1), transparent);
  transition: left 0.6s;
}

.coin-reward-display:hover::before {
  left: 100%;
}

.coin-reward-display:hover {
  background: linear-gradient(135deg, rgba(255, 215, 0, 0.2), rgba(255, 215, 0, 0.15));
  border-color: rgba(255, 215, 0, 0.6);
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(255, 215, 0, 0.3);
}

.coin-info {
  text-align: left;
}

.coin-amount {
  font-size: 16px;
  font-weight: 700;
  color: var(--warning);
}

.coin-note {
  font-size: 12px;
  font-weight: 500;
  color: var(--text-muted);
  font-style: italic;
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

/* 1. FORCE ALL DROPDOWN MENUS TO BE OPAQUE AND VISIBLE */
/* Target every possible Vuetify menu selector */

/* Main overlay content */
.v-overlay.v-menu .v-overlay__content,
.v-overlay.v-menu .v-overlay__content .v-list,
.v-overlay.v-menu .v-overlay__content .v-card,
.v-overlay.v-menu .v-overlay__content .v-sheet {
  background: var(--surface) !important;
  opacity: 1 !important;
  z-index: 10000 !important;
  visibility: visible !important;
}

[data-theme="dark"] .v-overlay.v-menu .v-overlay__content,
[data-theme="dark"] .v-overlay.v-menu .v-overlay__content .v-list,
[data-theme="dark"] .v-overlay.v-menu .v-overlay__content .v-card,
[data-theme="dark"] .v-overlay.v-menu .v-overlay__content .v-sheet {
  background: var(--surface) !important;
  opacity: 1 !important;
  z-index: 10000 !important;
  visibility: visible !important;
}

/* Select menus specifically */
.v-menu.v-select__menu .v-overlay__content,
.v-menu.v-combobox__menu .v-overlay__content,
.v-menu.v-autocomplete__menu .v-overlay__content {
  background: var(--surface) !important;
  opacity: 1 !important;
  z-index: 10000 !important;
  visibility: visible !important;
}

[data-theme="dark"] .v-menu.v-select__menu .v-overlay__content,
[data-theme="dark"] .v-menu.v-combobox__menu .v-overlay__content,
[data-theme="dark"] .v-menu.v-autocomplete__menu .v-overlay__content {
  background: var(--surface) !important;
  opacity: 1 !important;
  z-index: 10000 !important;
  visibility: visible !important;
}

/* List items */
.v-menu .v-list,
.v-select__menu .v-list,
.v-combobox__menu .v-list,
.v-autocomplete__menu .v-list {
  background: var(--surface) !important;
  opacity: 1 !important;
  z-index: 10000 !important;
  visibility: visible !important;
}

[data-theme="dark"] .v-menu .v-list,
[data-theme="dark"] .v-select__menu .v-list,
[data-theme="dark"] .v-combobox__menu .v-list,
[data-theme="dark"] .v-autocomplete__menu .v-list {
  background: var(--surface) !important;
  opacity: 1 !important;
  z-index: 10000 !important;
  visibility: visible !important;
}

.v-menu .v-list-item,
.v-select__menu .v-list-item,
.v-combobox__menu .v-list-item,
.v-autocomplete__menu .v-list-item {
  background: transparent !important;
  opacity: 1 !important;
  color: var(--text-primary) !important;
}

.v-menu .v-list-item-title,
.v-select__menu .v-list-item-title,
.v-combobox__menu .v-list-item-title,
.v-autocomplete__menu .v-list-item-title {
  opacity: 1 !important;
  color: var(--text-primary) !important;
}

.v-menu .v-list-item-subtitle,
.v-select__menu .v-list-item-subtitle,
.v-combobox__menu .v-list-item-subtitle,
.v-autocomplete__menu .v-list-item-subtitle {
  opacity: 1 !important;
  color: var(--text-muted) !important;
}

/* Ensure dropdown overlays are above everything */
.v-overlay.v-menu {
  z-index: 10000 !important;
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

/* Start Error Message */
.start-error-message {
  position: fixed;
  bottom: 24px;
  left: 50%;
  transform: translateX(-50%);
      background-color: var(--error);
      color: #ffffff;
  padding: 8px 16px;
  border-radius: 8px;
  font-size: 0.75rem;
  font-weight: 500;
  z-index: 1000;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
  animation: slideUp 0.3s ease-out;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateX(-50%) translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateX(-50%) translateY(0);
  }
}
</style>