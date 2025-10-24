import { ref, computed } from 'vue'
import { PET_CATALOG, PET_KEYS } from '@/data/petCatalog.js'

// Global pet state
const selectedPetKey = ref('catBlack') // Default to black cat
const selectedPet = computed(() => PET_CATALOG[selectedPetKey.value])

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
    setGlobalPet
  }
}
