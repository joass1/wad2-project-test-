<template>
  <div class="pet-selection-page">
    <div class="welcome-container">
      <div class="welcome-header">
        <h1 class="welcome-title">Welcome to Pomogotchi!</h1>
        <p class="welcome-subtitle">Choose your first pet companion</p>
      </div>

      <div class="pet-grid">
        <div 
          v-for="(pet, key) in PETS" 
          :key="key"
          class="pet-card"
          :class="{ 'selected': selectedPet === key }"
          @click="selectPet(key)"
        >
          <div class="pet-preview">
            <SpritePreview
              :key="pet.config.spriteUrl + ':' + pet.config.slice"
              :sprite-url="pet.config.spriteUrl"
              :slice="pet.config.slice"
              :scale="3"
              :row="0"
              :col="0"
            />
          </div>
          <div class="pet-info">
            <h3 class="pet-name">{{ pet.label }}</h3>
            <p class="pet-description">{{ getPetDescription(key) }}</p>
          </div>
        </div>
      </div>

      <div v-if="selectedPet" class="pet-name-section">
        <h2 class="section-title">Give your pet a name</h2>
        <input
          v-model="petName"
          type="text"
          class="pet-name-input"
          placeholder="Enter your pet's name"
          maxlength="20"
          @keyup.enter="confirmSelection"
          required
        />
        <p v-if="petNameError" class="name-error">{{ petNameError }}</p>
        <p class="input-hint">Choose a unique name for your companion (max 20 characters)</p>
      </div>

      <div class="selection-actions">
        <button
          class="confirm-btn"
          :disabled="!selectedPet || !petName.trim()"
          @click="confirmSelection"
        >
          Choose {{ selectedPet ? PETS[selectedPet].label : 'Pet' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useGlobalPet } from '@/composables/useGlobalPet.js'
import { PET_CATALOG, PET_KEYS } from '@/data/petCatalog.js'
import SpritePreview from '@/components/SpritePreview.vue'

const router = useRouter()
const { setGlobalPet } = useGlobalPet()

// Pet catalog
const PETS = PET_CATALOG
const selectedPet = ref(null)
const petName = ref('')
const petNameError = ref('')

// Pet descriptions
const petDescriptions = {
  catBlack: "A mysterious black cat with a calm demeanor. Perfect for quiet moments.",
  catGrey: "A gentle grey cat that loves to explore. Great for curious minds.",
  catNew: "A playful orange cat full of energy. Ideal for active users.",
  dogBlonde: "A loyal blonde dog that's always happy. Perfect for positive vibes.",
  dogGrey: "A wise grey dog with a gentle nature. Great for thoughtful users.",
  dogLight: "A friendly light brown dog full of enthusiasm. Ideal for social users."
}

function getPetDescription(petKey) {
  return petDescriptions[petKey] || "A wonderful companion for your journey."
}

function selectPet(petKey) {
  selectedPet.value = petKey
}

async function confirmSelection() {
  if (!selectedPet.value) return

  // Validate pet name
  petNameError.value = ''
  if (!petName.value || !petName.value.trim()) {
    petNameError.value = 'Please enter a name for your pet'
    return
  }

  if (petName.value.trim().length < 2) {
    petNameError.value = 'Pet name must be at least 2 characters'
    return
  }

  if (petName.value.length > 20) {
    petNameError.value = 'Pet name must be 20 characters or less'
    return
  }

  try {
    // Get current user for authentication
    const { auth } = await import('@/lib/firebase')
    const { onAuthStateChanged } = await import('firebase/auth')

    const currentUser = await new Promise((resolve) => {
      const unsubscribe = onAuthStateChanged(auth, (user) => {
        unsubscribe()
        resolve(user)
      })
    })

    if (!currentUser) {
      alert('Please log in to select a pet')
      router.push('/login')
      return
    }

    // Save pet selection to backend
    const token = await currentUser.getIdToken()
    const payload = {
      pet_key: selectedPet.value,
      pet_name: petName.value.trim()
    }

    const response = await fetch(`${process.env.VUE_APP_API_URL}/api/profile/select-pet`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(payload)
    })

    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.message || 'Failed to save pet selection')
    }

    // Set the global pet
    setGlobalPet(selectedPet.value)

    // Navigate to the dashboard
    router.push('/dashboard')
  } catch (error) {
    console.error('Error setting pet:', error)
    alert('There was an error setting your pet. Please try again.')
  }
}
</script>

<style scoped>
.pet-selection-page {
  min-height: 100vh;
  background: var(--background);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.welcome-container {
  max-width: 1200px;
  width: 100%;
  background: var(--surface);
  border-radius: 20px;
  padding: 40px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  border: 1px solid var(--surface-lighter);
}

.welcome-header {
  text-align: center;
  margin-bottom: 40px;
}

.welcome-title {
  font-size: 3rem;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 10px;
  background: linear-gradient(135deg, var(--primary), var(--secondary));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.welcome-subtitle {
  font-size: 1.2rem;
  color: var(--text-muted);
  margin: 0;
}

.pet-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  margin-bottom: 40px;
}

.pet-card {
  background: var(--surface);
  border-radius: 16px;
  padding: 24px;
  border: 3px solid transparent;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  border: 1px solid var(--surface-lighter);
}

.pet-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
  border-color: var(--secondary);
}

.pet-card.selected {
  border-color: var(--primary);
  background: var(--surface-light);
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(106, 122, 90, 0.3);
}

.pet-preview {
  display: flex;
  justify-content: center;
  margin-bottom: 20px;
  padding: 20px;
  background: var(--surface-light);
  border-radius: 12px;
  border: 2px solid var(--surface-lighter);
}

.pet-info {
  text-align: center;
}

.pet-name {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 10px 0;
}

.pet-description {
  font-size: 0.95rem;
  color: var(--text-muted);
  line-height: 1.5;
  margin: 0;
}

.pet-name-section {
  text-align: center;
  margin-bottom: 30px;
  padding: 30px;
  background: var(--surface-light);
  border-radius: 16px;
  border: 2px solid var(--surface-lighter);
}

.section-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 20px 0;
}

.pet-name-input {
  width: 100%;
  max-width: 400px;
  padding: 14px 20px;
  font-size: 1.1rem;
  border: 2px solid var(--surface-lighter);
  border-radius: 12px;
  background: var(--surface);
  color: var(--text-primary);
  transition: all 0.3s ease;
  text-align: center;
}

.pet-name-input:focus {
  outline: none;
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgba(106, 122, 90, 0.1);
}

.input-hint {
  margin: 10px 0 0 0;
  font-size: 0.9rem;
  color: var(--text-muted);
}

.name-error {
  margin: 10px 0 0 0;
  color: #ef4444;
  font-size: 0.9rem;
  font-weight: 500;
}

.selection-actions {
  display: flex;
  justify-content: center;
}

.confirm-btn {
  background: var(--primary);
  color: white;
  border: none;
  border-radius: 12px;
  padding: 16px 32px;
  font-size: 1.1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(106, 122, 90, 0.3);
}

.confirm-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(106, 122, 90, 0.4);
  background: var(--secondary);
}

.confirm-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
  box-shadow: 0 4px 12px rgba(106, 122, 90, 0.2);
}

/* Responsive design */
@media (max-width: 768px) {
  .welcome-container {
    padding: 20px;
  }
  
  .welcome-title {
    font-size: 2rem;
  }
  
  .pet-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }
  
  .pet-card {
    padding: 20px;
  }
}
</style>
