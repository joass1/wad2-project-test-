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

// Function to load from localStorage (only for avatar)
function loadFromStorage() {
  try {
    const data = JSON.parse(localStorage.getItem("demo_user") || "{}")
    if (data?.avatar) _profile.value.avatar = data.avatar
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
    // Prioritize localStorage avatar, then Firebase
    return _profile.value.avatar || authUser.value?.photoURL || firebaseProfile.value?.avatar || firebaseProfile.value?.avatar_url || null
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
        // Only update avatar from Firebase if no localStorage avatar exists
        if (!_profile.value.avatar) {
          _profile.value.avatar = profile.avatar || profile.avatar_url || firebaseUser?.photoURL || _profile.value.avatar
        }
      } else if (firebaseUser) {
        // Only update avatar from Firebase Auth if no localStorage avatar exists
        if (!_profile.value.avatar) {
          _profile.value.avatar = firebaseUser.photoURL || _profile.value.avatar
        }
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

  // Function to save to localStorage (only avatar)
  function saveToStorage() {
    try {
      const userData = {
        avatar: _profile.value.avatar
      }
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

  // Function to update avatar
  function updateAvatar(avatar) {
    updateProfile({ avatar })
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
