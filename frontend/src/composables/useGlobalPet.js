import { ref, computed, onMounted } from 'vue'
import { PET_CATALOG, PET_KEYS } from '@/data/petCatalog.js'

// Global pet state
const selectedPetKey = ref('catBlack') // Default to black cat
const selectedPet = computed(() => PET_CATALOG[selectedPetKey.value])
const petName = ref(null) // Pet's custom name
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
    const response = await fetch(`${process.env.VUE_APP_API_URL}/api/profile/pet-selection-status`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
    
    if (response.ok) {
      const data = await response.json()
      if (data.has_selected_pet && data.selected_pet) {
        selectedPetKey.value = data.selected_pet
        petName.value = data.pet_name || null
        console.log(`Loaded pet from backend: ${PET_CATALOG[data.selected_pet].label}`)
        if (data.pet_name) {
          console.log(`Pet name: ${data.pet_name}`)
        }
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

// Function to update pet name
async function updatePetName(newName) {
  try {
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
      throw new Error('User not authenticated')
    }
    
    // Update pet name in backend
    const token = await currentUser.getIdToken()
    const response = await fetch(`${process.env.VUE_APP_API_URL}/api/profile/pet-name`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({
        pet_name: newName
      })
    })
    
    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.message || 'Failed to update pet name')
    }
    
    // Update local state
    petName.value = newName
    console.log(`Pet name updated to: ${newName}`)
    
    return { success: true }
  } catch (error) {
    console.error('Error updating pet name:', error)
    return { success: false, error: error.message }
  }
}

// Load pet data when composable is first used
onMounted(() => {
  loadPetFromBackend()
})

// Export the composable
export function useGlobalPet() {
  return {
    selectedPetKey,
    selectedPet,
    petName,
    setGlobalPet,
    updatePetName,
    loadPetFromBackend,
    isLoading
  }
}
