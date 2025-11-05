import { ref } from 'vue'
import { api } from '@/lib/api.js'

// Shared state for minigame progress
const progress = ref(null)
const progressLoading = ref(false)
const progressError = ref(null)

export function useMinigameProgress() {
  // Fetch minigame progress from backend
  const loadProgress = async () => {
    progressLoading.value = true
    progressError.value = null
    try {
      console.log('[useMinigameProgress] Fetching from backend: /api/minigame/progress')
      const response = await api.get('/api/minigame/progress')
      console.log('[useMinigameProgress] Backend response:', JSON.stringify(response, null, 2))

      if (response && response.progress) {
        progress.value = response.progress
        console.log('[useMinigameProgress] Loaded progress:', JSON.stringify(progress.value, null, 2))
        console.log('[useMinigameProgress] Progress details:')
        console.log('  - wave:', progress.value.wave)
        console.log('  - level:', progress.value.level)
        console.log('  - max_health:', progress.value.max_health)
        console.log('  - died_today:', progress.value.died_today)
        return progress.value
      } else {
        // No saved progress found
        console.log('[useMinigameProgress] No saved progress found in response')
        progress.value = null
        return null
      }
    } catch (error) {
      console.error('[useMinigameProgress] Error loading minigame progress:', error)
      progressError.value = error.message || 'Failed to load progress'
      return null
    } finally {
      progressLoading.value = false
    }
  }

  // Save minigame progress to backend
  const saveProgress = async (gameState, timePlayedToday = 0, diedToday = false) => {
    progressLoading.value = true
    progressError.value = null
    try {
      const payload = {
        wave: gameState.wave,
        level: gameState.level,
        weapons: gameState.weapons,
        max_health: gameState.maxHealth,
        speed: gameState.speed,
        time_played_today: timePlayedToday,
        died_today: diedToday,
        last_played: new Date().toISOString()
      }

      console.log('[useMinigameProgress] Saving to backend:', JSON.stringify(payload, null, 2))

      const response = await api.post('/api/minigame/progress', payload)

      console.log('[useMinigameProgress] Save response:', JSON.stringify(response, null, 2))

      if (response && response.ok) {
        progress.value = gameState
        console.log('[useMinigameProgress] Save successful')
        return { success: true }
      } else {
        console.error('[useMinigameProgress] Failed to save progress:', response)
        progressError.value = 'Failed to save progress'
        return { success: false, error: 'Failed to save progress' }
      }
    } catch (error) {
      console.error('[useMinigameProgress] Error saving minigame progress:', error)
      progressError.value = error.message || 'Failed to save progress'
      return { success: false, error: error.message || 'Failed to save progress' }
    } finally {
      progressLoading.value = false
    }
  }

  // Clear progress (reset to wave 1)
  const clearProgress = async () => {
    try {
      const response = await api.delete('/api/minigame/progress')
      if (response && response.ok) {
        progress.value = null
        console.log('Cleared minigame progress')
        return { success: true }
      } else {
        return { success: false, error: 'Failed to clear progress' }
      }
    } catch (error) {
      console.error('Error clearing progress:', error)
      return { success: false, error: error.message }
    }
  }

  return {
    progress,
    progressLoading,
    progressError,
    loadProgress,
    saveProgress,
    clearProgress
  }
}
