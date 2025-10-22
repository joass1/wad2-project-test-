import { ref } from 'vue'
import { api } from '@/lib/api.js'

// Shared state across all components
const coins = ref(null)
const coinsLoading = ref(false)
const coinsError = ref(null)

export function useCoins() {
  // Fetch user's coins from the backend
  const fetchCoins = async () => {
    coinsLoading.value = true
    coinsError.value = null
    try {
      const response = await api.get('/api/profile/coins')
      if (response && typeof response.coins === 'number') {
        coins.value = response.coins
      } else {
        coinsError.value = 'Invalid response'
      }
    } catch (error) {
      console.error('Error fetching coins:', error)
      coinsError.value = error.message || 'Failed to load coins'
    } finally {
      coinsLoading.value = false
    }
  }

  // Update coins in the database
  const updateCoins = async (newAmount) => {
    try {
      const response = await api.put('/api/profile/coins', { coins: newAmount })

      if (response && response.ok) {
        // Update shared state after successful database update
        coins.value = newAmount
        return { success: true, coins: newAmount }
      } else {
        console.error('Failed to update coins:', response)
        return { success: false, error: 'Failed to update coins' }
      }
    } catch (error) {
      console.error('Error updating coins:', error)
      return { success: false, error: error.message || 'Failed to update coins' }
    }
  }

  return {
    coins,
    coinsLoading,
    coinsError,
    fetchCoins,
    updateCoins
  }
}
