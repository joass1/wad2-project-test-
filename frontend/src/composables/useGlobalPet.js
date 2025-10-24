import { ref, computed, onMounted } from 'vue'
import { PET_CATALOG, PET_KEYS } from '@/data/petCatalog.js'

// Global pet state
const selectedPetKey = ref('catBlack') // Default to black cat
const selectedPet = computed(() => PET_CATALOG[selectedPetKey.value])
const isLoading = ref(false)

// Function to load pet from backend
async function loadPetFromBackend() {
  try {
    isLoading.value = true
    
    // Get current user
    const { auth } = await import('@/lib/firebase')
    const { onAuthStateChanged } = await import('firebase/auth')
    
    const currentUser = await new Promise((resolve) => {
      const unsubscribe = onAuthStateChanged(auth, (user) => {
        unsubscribe()
        resolve(user)
      })
    })
    
    if (!currentUser) {
      console.log('No user logged in, using default pet')
      return
    }
    
    // Fetch pet selection from backend
    const token = await currentUser.getIdToken()
    const response = await fetch('/api/profile/pet-selection-status', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
    
    if (response.ok) {
      const data = await response.json()
      if (data.has_selected_pet && data.selected_pet) {
        selectedPetKey.value = data.selected_pet
        console.log(`Loaded pet from backend: ${PET_CATALOG[data.selected_pet].label}`)
      }
    }
  } catch (error) {
    console.error('Error loading pet from backend:', error)
  } finally {
    isLoading.value = false
  }
}

// Function to update the global pet
function setGlobalPet(petKey) {
  if (PET_KEYS.includes(petKey)) {
    selectedPetKey.value = petKey
    console.log(`Global pet changed to: ${PET_CATALOG[petKey].label}`)
    console.log('New pet config:', PET_CATALOG[petKey])
  } else {
    console.error(`Invalid pet key: ${petKey}`)
  }
}

// Export the composable
export function useGlobalPet() {
  return {
    selectedPetKey,
    selectedPet,
    setGlobalPet,
    loadPetFromBackend,
    isLoading
  }
}
