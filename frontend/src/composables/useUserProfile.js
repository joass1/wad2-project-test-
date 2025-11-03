import { ref, computed, watch } from 'vue'
import { useAuth } from './useAuth.js'

// Shared reactive state for user profile
const _profile = ref({
  name: '',
  email: '',
  avatar: null,
  level: 1
})

// Track current user ID to detect user changes
let currentUserId = null

// Function to clear localStorage
function clearStorage() {
  try {
    localStorage.removeItem("demo_user")
  } catch (error) {
    console.warn('Failed to clear user profile from localStorage:', error)
  }
}

// Function to load from localStorage (avatar no longer loaded from localStorage, using Firestore instead)
function loadFromStorage() {
  // Avatar is now stored in Firestore, not localStorage
  // This function is kept for backward compatibility but doesn't load avatar
  try {
    const data = JSON.parse(localStorage.getItem("demo_user") || "{}")
    // No longer loading avatar from localStorage
  } catch (error) {
    console.warn('Failed to load user profile from localStorage:', error)
  }
}

export function useUserProfile() {
  const { user: authUser, userProfile: firebaseProfile } = useAuth()
  
  // Computed properties for easy access
  const profile = computed(() => _profile.value)
  const displayName = computed(() => {
    // Use only Firebase data for name
    if (authUser.value?.displayName) {
      return authUser.value.displayName
    }
    if (firebaseProfile.value?.full_name) {
      return firebaseProfile.value.full_name
    }
    if (firebaseProfile.value?.name) {
      return firebaseProfile.value.name
    }
    return authUser.value?.email || 'User'
  })
  const displayEmail = computed(() => {
    // Use only Firebase data for email
    return authUser.value?.email || firebaseProfile.value?.email || ''
  })
  const displayAvatar = computed(() => {
    // Prioritize Firestore avatar, then Firebase Auth photoURL, then localStorage (for temporary previews)
    return firebaseProfile.value?.avatar || authUser.value?.photoURL || _profile.value.avatar || firebaseProfile.value?.avatar_url || null
  })
  const level = computed(() => _profile.value.level || 1)

  // Watch for changes in Firebase auth/profile and update local state
  watch(
    [() => firebaseProfile.value, () => authUser.value],
    ([profile, firebaseUser]) => {
      // Check if user has changed
      const newUserId = firebaseUser?.uid
      if (newUserId !== currentUserId) {
        // User has changed, clear localStorage and reset profile
        if (currentUserId !== null) {
          clearStorage()
        }
        currentUserId = newUserId
        
        // Reset profile state
        _profile.value = {
          name: '',
          email: '',
          avatar: null,
          level: 1
        }
        
        // Load from localStorage for the new user (if any)
        if (newUserId) {
          loadFromStorage()
        }
      }
      
      if (profile) {
        // Firestore is the source of truth - displayAvatar computed will prioritize Firestore
        // Local avatar is only used for temporary previews before Firestore syncs
        // No need to manually sync here since displayAvatar handles the priority
      } else if (firebaseUser) {
        // If no Firestore profile, use Firebase Auth photoURL if available
        // Local avatar is only used for temporary previews
      } else {
        // User logged out, clear everything
        currentUserId = null
        _profile.value = {
          name: '',
          email: '',
          avatar: null,
          level: 1
        }
        clearStorage()
      }
    },
    { immediate: true }
  )

  // Function to update profile data
  function updateProfile(updates) {
    Object.assign(_profile.value, updates)
    saveToStorage()
  }

  // Function to save to localStorage (avatar no longer saved to localStorage, using Firestore instead)
  function saveToStorage() {
    // Avatar is now stored in Firestore, not localStorage
    // This function is kept for backward compatibility but doesn't save avatar
    try {
      // Only save non-avatar data if needed in the future
      const userData = {}
      localStorage.setItem("demo_user", JSON.stringify(userData))
    } catch (error) {
      console.warn('Failed to save user profile to localStorage:', error)
    }
  }

  // Function to update name (local state only, not saved to localStorage)
  function updateName(name) {
    _profile.value.name = name
    // Don't save to localStorage since name comes from Firebase
  }

  // Function to update email (local state only, not saved to localStorage)
  function updateEmail(email) {
    _profile.value.email = email
    // Don't save to localStorage since email comes from Firebase
  }

  // Function to update avatar (for temporary local preview only, doesn't save to localStorage)
  // The actual save to Firestore is handled in profile.vue via API call
  function updateAvatar(avatar) {
    // Only update local state for immediate preview
    // Don't save to localStorage since Firestore is the source of truth
    _profile.value.avatar = avatar
  }

  // Function to update level
  function updateLevel(level) {
    updateProfile({ level })
  }

  return {
    profile,
    displayName,
    displayEmail,
    displayAvatar,
    level,
    updateProfile,
    updateName,
    updateEmail,
    updateAvatar,
    updateLevel,
    saveToStorage,
    clearStorage
  }
}
