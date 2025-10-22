import { ref, computed, watch } from 'vue'
import { useAuth } from './useAuth.js'

// Shared reactive state for user profile
const _profile = ref({
  name: '',
  email: '',
  avatar: null,
  level: 1
})

// Initialize from localStorage on module load
function loadFromStorage() {
  try {
    const data = JSON.parse(localStorage.getItem("demo_user") || "{}")
    if (data?.name) _profile.value.name = data.name
    if (data?.email) _profile.value.email = data.email
    if (data?.avatar) _profile.value.avatar = data.avatar
  } catch (error) {
    console.warn('Failed to load user profile from localStorage:', error)
  }
}

// Load from storage immediately
loadFromStorage()

export function useUserProfile() {
  const { user: authUser, userProfile: firebaseProfile } = useAuth()
  
  // Computed properties for easy access
  const profile = computed(() => _profile.value)
  const displayName = computed(() => {
    // Prioritize locally stored name, then Firebase displayName, then email as last resort
    if (_profile.value.name && _profile.value.name.trim() !== '') {
      return _profile.value.name
    }
    return authUser.value?.displayName || authUser.value?.email || 'User'
  })
  const displayEmail = computed(() => _profile.value.email || authUser.value?.email || '')
  const displayAvatar = computed(() => _profile.value.avatar || authUser.value?.photoURL || null)
  const level = computed(() => _profile.value.level || 1)

  // Watch for changes in Firebase auth/profile and update local state
  watch(
    [() => firebaseProfile.value, () => authUser.value],
    ([profile, firebaseUser]) => {
      if (profile) {
        const fallbackName = firebaseUser?.displayName || firebaseUser?.email || ""
        // Only update name if local name is empty or not set
        if (!_profile.value.name || _profile.value.name.trim() === '') {
          _profile.value.name = profile.full_name || profile.name || fallbackName || _profile.value.name
        }
        _profile.value.email = profile.email || firebaseUser?.email || _profile.value.email
        _profile.value.avatar = profile.avatar || profile.avatar_url || firebaseUser?.photoURL || _profile.value.avatar
      } else if (firebaseUser) {
        // Only update name if local name is empty or not set
        if (!_profile.value.name || _profile.value.name.trim() === '') {
          _profile.value.name = firebaseUser.displayName || firebaseUser.email || _profile.value.name
        }
        _profile.value.email = firebaseUser.email || _profile.value.email
        _profile.value.avatar = firebaseUser.photoURL || _profile.value.avatar
      }
    },
    { immediate: true }
  )

  // Function to update profile data
  function updateProfile(updates) {
    Object.assign(_profile.value, updates)
    saveToStorage()
  }

  // Function to save to localStorage
  function saveToStorage() {
    try {
      const userData = {
        name: _profile.value.name,
        email: _profile.value.email,
        avatar: _profile.value.avatar,
        level: _profile.value.level
      }
      localStorage.setItem("demo_user", JSON.stringify(userData))
    } catch (error) {
      console.warn('Failed to save user profile to localStorage:', error)
    }
  }

  // Function to update name
  function updateName(name) {
    updateProfile({ name })
  }

  // Function to update email
  function updateEmail(email) {
    updateProfile({ email })
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
    saveToStorage
  }
}
