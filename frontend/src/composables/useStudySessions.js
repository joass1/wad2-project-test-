import { ref } from 'vue'
import { getAuth } from 'firebase/auth'

// Get auth token helper
async function getAuthToken() {
  const auth = getAuth()
  const user = auth.currentUser
  if (!user) throw new Error('Not authenticated')
  return await user.getIdToken()
}

const API_BASE_URL = (import.meta.env?.VITE_API_URL || 'http://localhost:8000') + '/api'

export function useStudySessions() {
  const loading = ref(false)
  const error = ref(null)

  // Start a new study session
  async function startSession(data) {
    loading.value = true
    error.value = null
    
    try {
      const token = await getAuthToken()
      const response = await fetch(`${API_BASE_URL}/study-sessions/start`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(data)
      })
      
      if (!response.ok) {
        const err = await response.json()
        throw new Error(err.detail || 'Failed to start session')
      }
      
      return await response.json()
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  // Update a study session (pause, resume, complete)
  async function updateSession(sessionId, data) {
    loading.value = true
    error.value = null
    
    try {
      const token = await getAuthToken()
      const response = await fetch(`${API_BASE_URL}/study-sessions/${sessionId}`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(data)
      })
      
      if (!response.ok) {
        const err = await response.json()
        throw new Error(err.detail || 'Failed to update session')
      }
      
      return await response.json()
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  // Reset a study session
  async function resetSession(sessionId) {
    loading.value = true
    error.value = null
    
    try {
      const token = await getAuthToken()
      const response = await fetch(`${API_BASE_URL}/study-sessions/${sessionId}/reset`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      
      if (!response.ok) {
        const err = await response.json()
        throw new Error(err.detail || 'Failed to reset session')
      }
      
      return await response.json()
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  // Get current active/paused session
  async function getCurrentSession() {
    loading.value = true
    error.value = null
    
    try {
      const token = await getAuthToken()
      const response = await fetch(`${API_BASE_URL}/study-sessions/current`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      
      if (response.status === 404 || response.status === 204) {
        return null
      }
      
      if (!response.ok) {
        throw new Error('Failed to get current session')
      }
      
      return await response.json()
    } catch (err) {
      error.value = err.message
      return null
    } finally {
      loading.value = false
    }
  }

  // Get daily metrics
  async function getDailyMetrics(date = null) {
    loading.value = true
    error.value = null
    
    try {
      const token = await getAuthToken()
      const url = date 
        ? `${API_BASE_URL}/study-sessions/metrics/daily?date=${date}`
        : `${API_BASE_URL}/study-sessions/metrics/daily`
      
      const response = await fetch(url, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      
      if (!response.ok) {
        throw new Error('Failed to get daily metrics')
      }
      
      return await response.json()
    } catch (err) {
      error.value = err.message
      // Return empty metrics on error
      return {
        date: date || new Date().toISOString().split('T')[0],
        sessions_started: 0,
        sessions_completed: 0,
        total_pauses: 0,
        total_resets: 0
      }
    } finally {
      loading.value = false
    }
  }

  // Get study stats summary
  async function getStats() {
    loading.value = true
    error.value = null
    
    try {
      const token = await getAuthToken()
      const response = await fetch(`${API_BASE_URL}/study-sessions/stats/summary`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      
      if (!response.ok) {
        throw new Error('Failed to get stats')
      }
      
      return await response.json()
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  // List study sessions with optional filters
  async function listSessions(params = {}) {
    loading.value = true
    error.value = null
    
    try {
      const token = await getAuthToken()
      const queryString = new URLSearchParams(params).toString()
      const url = queryString 
        ? `${API_BASE_URL}/study-sessions?${queryString}`
        : `${API_BASE_URL}/study-sessions`
      
      const response = await fetch(url, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      
      if (!response.ok) {
        throw new Error('Failed to list sessions')
      }
      
      return await response.json()
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  // Get a specific session
  async function getSession(sessionId) {
    loading.value = true
    error.value = null
    
    try {
      const token = await getAuthToken()
      const response = await fetch(`${API_BASE_URL}/study-sessions/${sessionId}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      
      if (!response.ok) {
        throw new Error('Failed to get session')
      }
      
      return await response.json()
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  // Delete a session
  async function deleteSession(sessionId) {
    loading.value = true
    error.value = null
    
    try {
      const token = await getAuthToken()
      const response = await fetch(`${API_BASE_URL}/study-sessions/${sessionId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      
      if (!response.ok) {
        throw new Error('Failed to delete session')
      }
      
      return await response.json()
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  return {
    loading,
    error,
    startSession,
    updateSession,
    resetSession,
    getCurrentSession,
    getDailyMetrics,
    getStats,
    listSessions,
    getSession,
    deleteSession
  }
}