<template>
  <v-navigation-drawer
    :model-value="modelValue"
    @update:model-value="$emit('update:modelValue', $event)"
    :rail="!isMobile && !modelValue"
    app
    :permanent="!isMobile"
    :temporary="isMobile"
    :width="287"
    class="sb-drawer"
  >
    <div class="sidebar-container">
      <!-- Close button for mobile -->
      <v-btn
        v-if="isMobile && modelValue"
        icon
        variant="text"
        size="small"
        class="close-btn"
        @click="$emit('update:modelValue', false)"
      >
        <v-icon>mdi-close</v-icon>
      </v-btn>

      <!-- Profile header -->
      <div class="profile-header">
        <div class="profile-avatar-container" @click="navigateToProfile">
          <div class="profile-avatar" :class="{ 'premium-border': allAchievementsCompleted }">
            <img v-if="displayAvatar" :src="displayAvatar" alt="Profile Avatar" class="avatar-image" />
            <span v-else class="avatar-text">{{ (displayName || 'U').charAt(0).toUpperCase() }}</span>
            <div v-if="allAchievementsCompleted" class="premium-badge">
              <span>⭐</span>
            </div>
          </div>
          <transition name="slide-fade">
            <div v-show="!isMobile || modelValue" class="profile-info">
              <div class="profile-name">{{ displayName || 'Guest' }}</div>
            </div>
          </transition>
        </div>
      </div>

      <!-- Nav -->
      <div class="nav-container">
        <v-list nav density="comfortable">
        <v-list-item to="/dashboard" :prepend-icon="(!isMobile || modelValue) ? 'mdi-home-outline' : ''" :title="(!isMobile || modelValue) ? 'Dashboard' : ''" rounded="lg">
          <v-icon v-if="isMobile && !modelValue">mdi-home-outline</v-icon>
          <v-tooltip v-if="isMobile && !modelValue" activator="parent" location="end">Dashboard</v-tooltip>
        </v-list-item>
        
        <v-list-item to="/timer" :prepend-icon="(!isMobile || modelValue) ? 'mdi-timer-outline' : ''" :title="(!isMobile || modelValue) ? 'Study Timer' : ''" rounded="lg">
          <v-icon v-if="isMobile && !modelValue">mdi-timer-outline</v-icon>
          <v-tooltip v-if="isMobile && !modelValue" activator="parent" location="end">Study Timer</v-tooltip>
        </v-list-item>
        
        <v-list-item to="/task-tracker" :prepend-icon="(!isMobile || modelValue) ? 'mdi-checkbox-marked-outline' : ''" :title="(!isMobile || modelValue) ? 'Task Tracker' : ''" rounded="lg">
          <v-icon v-if="isMobile && !modelValue">mdi-checkbox-marked-outline</v-icon>
          <v-tooltip v-if="isMobile && !modelValue" activator="parent" location="end">Task Tracker</v-tooltip>
        </v-list-item>
        
        <v-list-item to="/progress" :prepend-icon="(!isMobile || modelValue) ? 'mdi-chart-line' : ''" :title="(!isMobile || modelValue) ? 'Progress' : ''" rounded="lg">
          <v-icon v-if="isMobile && !modelValue">mdi-chart-line</v-icon>
          <v-tooltip v-if="isMobile && !modelValue" activator="parent" location="end">Progress</v-tooltip>
        </v-list-item>
        
        <v-list-item to="/checkin" :prepend-icon="(!isMobile || modelValue) ? 'mdi-heart-outline' : ''" :title="(!isMobile || modelValue) ? 'Daily Check-in' : ''" rounded="lg">
          <v-icon v-if="isMobile && !modelValue">mdi-heart-outline</v-icon>
          <v-tooltip v-if="isMobile && !modelValue" activator="parent" location="end">Daily Check-in</v-tooltip>
        </v-list-item>
        
        <v-list-item to="/pet" :prepend-icon="(!isMobile || modelValue) ? 'mdi-paw' : ''" :title="(!isMobile || modelValue) ? 'Pet' : ''" rounded="lg">
          <v-icon v-if="isMobile && !modelValue">mdi-paw</v-icon>
          <v-tooltip v-if="isMobile && !modelValue" activator="parent" location="end">Pet</v-tooltip>
        </v-list-item>
        
        <v-list-item to="/profile" :prepend-icon="(!isMobile || modelValue) ? 'mdi-account-outline' : ''" :title="(!isMobile || modelValue) ? 'Profile' : ''" rounded="lg">
          <v-icon v-if="isMobile && !modelValue">mdi-account-outline</v-icon>
          <v-tooltip v-if="isMobile && !modelValue" activator="parent" location="end">Profile</v-tooltip>
        </v-list-item>
        </v-list>
      </div>

      <div class="spacer"></div>

      <!-- Coin display -->
      <transition name="slide-fade">
        <div v-show="!isMobile || modelValue" class="coin-display">
          <template v-if="coinsLoading">
            <div class="coin-loading">Loading coins...</div>
          </template>
          <template v-else-if="coinsError">
            <div class="coin-error">
              <div class="error-icon">⚠️</div>
              <div class="error-text">{{ coinsError }}</div>
            </div>
          </template>
          <template v-else>
            <AnimatedCoin :scale="2" :speed="8" />
            <div class="coin-amount">{{ coins }}</div>
          </template>
        </div>
      </transition>

      <!-- Bottom theme toggle -->
      <div class="theme-toggle-container">
        <ThemeToggle compact />
      </div>
    </div>
  </v-navigation-drawer>
</template>

<script setup>
import { ref, watch, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useDisplay } from 'vuetify'
import ThemeToggle from '@/components/ThemeToggle.vue'
import AnimatedCoin from '@/components/AnimatedCoin.vue'
import { useCoins } from '@/composables/useCoins.js'
import { useUserProfile } from '@/composables/useUserProfile.js'
import { useAuth } from '@/composables/useAuth.js'
import { api } from '@/lib/api.js'

defineProps({
  modelValue: Boolean
})

const emit = defineEmits(['update:modelValue'])

// Router for navigation
const router = useRouter()

// Responsive detection
const { mobile } = useDisplay()
const isMobile = ref(mobile.value)

// Watch for screen size changes
watch(mobile, () => {
  isMobile.value = mobile.value
}, { immediate: true })

// Use shared coin state
const { coins, coinsLoading, coinsError, fetchCoins } = useCoins()

// Use shared profile state
const { displayName, displayAvatar } = useUserProfile()

// Use auth state to wait for authentication
const { loading: authLoading, isAuthed, user: authUser } = useAuth()

// Achievements data
const achievementsData = ref({
  achievements: [],
  totalUnlocked: 0,
  totalAchievements: 6,
  completionPercentage: 0,
})

// Computed property to check if all achievements are completed
const allAchievementsCompleted = computed(() => {
  if (!achievementsData.value.achievements || achievementsData.value.achievements.length === 0) {
    return false
  }
  // Check if all 6 achievements are claimed
  const claimedCount = achievementsData.value.achievements.filter(a => a.claimed).length
  return claimedCount === achievementsData.value.totalAchievements && achievementsData.value.totalAchievements === 6
})

// Function to load achievements
async function loadAchievements() {
  if (!authUser.value) return
  
  try {
    const achievementsResponse = await api.get('/api/achievements/')
    achievementsData.value.achievements = achievementsResponse.achievements || []
    achievementsData.value.totalUnlocked = achievementsResponse.total_unlocked || 0
    achievementsData.value.totalAchievements = achievementsResponse.total_achievements || 6
    achievementsData.value.completionPercentage = achievementsResponse.completion_percentage || 0
  } catch (error) {
    console.error('Error loading achievements in sidebar:', error)
  }
}

// Function to refresh achievements (can be called from events)
function refreshAchievements() {
  loadAchievements()
}

// Navigate to profile page
function navigateToProfile() {
  router.push('/profile')
  // Close drawer on mobile after navigation
  if (isMobile.value) {
    emit('update:modelValue', false)
  }
}

// Watch for authentication to be ready before fetching coins and achievements
watch([authLoading, isAuthed], ([loading, authed]) => {
  // Only fetch coins when auth is ready and user is authenticated
  if (!loading && authed && coins.value === null && !coinsLoading.value) {
    fetchCoins()
  }
  // Load achievements when auth is ready
  if (!loading && authed) {
    loadAchievements()
  }
}, { immediate: true })

// Listen for achievement events to refresh achievements
onMounted(() => {
  window.addEventListener('achievement-claimed', refreshAchievements)
  window.addEventListener('achievement-unlocked', refreshAchievements)
  window.addEventListener('achievement-unclaimed', refreshAchievements)
})

onUnmounted(() => {
  window.removeEventListener('achievement-claimed', refreshAchievements)
  window.removeEventListener('achievement-unlocked', refreshAchievements)
  window.removeEventListener('achievement-unclaimed', refreshAchievements)
})
</script>

<style scoped>
.sb-drawer {
  border-right: 1px solid var(--surface-lighter);
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

/* Close button for mobile */
.close-btn {
  position: absolute;
  top: 12px;
  right: 12px;
  z-index: 10;
  background: var(--surface);
  color: var(--text-primary);
  border: 1px solid var(--surface-lighter);
  border-radius: 999px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.15);
}

/* Slide fade transition */
.slide-fade-enter-active {
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.slide-fade-leave-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.slide-fade-enter-from {
  transform: translateX(-20px);
  opacity: 0;
}

.slide-fade-leave-to {
  transform: translateX(-20px);
  opacity: 0;
}

.sidebar-container {
  padding: 24px;
  display: flex;
  flex-direction: column;
  height: 100%;
  background: linear-gradient(135deg, var(--surface) 0%, var(--surface-light) 100%);
  position: relative;
  overflow: hidden;
  min-height: 0;
}

.sidebar-container::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, var(--primary), var(--secondary), var(--primary));
  border-radius: 0 0 8px 8px;
}

/* Profile Header */
.profile-header {
  margin-bottom: 32px;
  position: relative;
  overflow: hidden;
  flex-shrink: 0;
}

.profile-avatar-container {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  background: var(--surface-light);
  border-radius: 16px;
  border: 2px solid var(--surface-lighter);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  cursor: pointer;
  position: relative;
}

.profile-avatar-container:hover {
  background: rgba(255, 255, 255, 0.8);
  transform: translateY(-2px);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.15);
}

.profile-avatar-container:active {
  transform: translateY(0);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

/* Dark mode profile header */
[data-theme="dark"] .profile-avatar-container {
  background: rgba(255, 255, 255, 0.2);
  border: 2px solid rgba(255, 255, 255, 0.3);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
}

[data-theme="dark"] .profile-avatar-container:hover {
  background: rgba(255, 255, 255, 0.3);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.5);
}

[data-theme="dark"] .profile-avatar-container:active {
  transform: translateY(0);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
}

.profile-avatar {
  width: 56px;
  height: 56px;
  background: linear-gradient(135deg, var(--primary), var(--secondary));
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  font-weight: bold;
  color: #ffffff;
  position: relative;
  overflow: visible;
  box-shadow: 0 4px 15px rgba(106, 122, 90, 0.3);
  border: 3px solid rgba(255, 255, 255, 0.8);
  transition: all 0.3s ease;
  flex-shrink: 0;
}

.profile-avatar:hover {
  transform: scale(1.05) rotate(5deg);
  box-shadow: 0 6px 25px rgba(106, 122, 90, 0.4);
}

/* Premium Border Styles - Unlocked when all achievements are completed */
.profile-avatar.premium-border {
  border: 4px solid transparent;
  background: linear-gradient(135deg, var(--primary), var(--secondary)) padding-box,
              linear-gradient(135deg, #ffd700, #ffed4e, #ffd700, #ff6b6b, #4ecdc4, #45b7d1, #ffd700) border-box;
  background-origin: border-box;
  background-clip: padding-box, border-box;
  box-shadow: 0 0 15px rgba(255, 215, 0, 0.4),
              0 4px 15px rgba(106, 122, 90, 0.3),
              inset 0 0 20px rgba(255, 215, 0, 0.1);
  animation: premiumGlow 3s ease-in-out infinite;
}

.profile-avatar.premium-border::before {
  content: '';
  position: absolute;
  inset: -4px;
  border-radius: 50%;
  padding: 4px;
  background: linear-gradient(135deg, #ffd700, #ffed4e, #ffd700, #ff6b6b, #4ecdc4, #45b7d1, #ffd700);
  -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  -webkit-mask-composite: xor;
  mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  mask-composite: exclude;
  animation: premiumRotate 4s linear infinite;
  z-index: -1;
}

@keyframes premiumGlow {
  0%, 100% {
    box-shadow: 0 0 15px rgba(255, 215, 0, 0.4),
                0 4px 15px rgba(106, 122, 90, 0.3),
                inset 0 0 20px rgba(255, 215, 0, 0.1);
  }
  50% {
    box-shadow: 0 0 25px rgba(255, 215, 0, 0.6),
                0 4px 15px rgba(106, 122, 90, 0.3),
                inset 0 0 30px rgba(255, 215, 0, 0.2);
  }
}

@keyframes premiumRotate {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

.profile-avatar.premium-border:hover {
  transform: scale(1.08) rotate(5deg);
  box-shadow: 0 0 30px rgba(255, 215, 0, 0.6),
              0 6px 25px rgba(106, 122, 90, 0.4),
              inset 0 0 40px rgba(255, 215, 0, 0.2);
}

/* Premium Badge */
.premium-badge {
  position: absolute;
  top: -4px;
  right: -4px;
  width: 24px;
  height: 24px;
  background: linear-gradient(135deg, #ffd700, #ffed4e);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 8px rgba(255, 215, 0, 0.5),
              0 0 12px rgba(255, 215, 0, 0.3);
  border: 2px solid rgba(255, 255, 255, 0.9);
  z-index: 10;
  animation: premiumBadgePulse 2s ease-in-out infinite;
}

.premium-badge span {
  font-size: 10px;
  filter: drop-shadow(0 1px 2px rgba(0, 0, 0, 0.3));
}

@keyframes premiumBadgePulse {
  0%, 100% {
    transform: scale(1);
    box-shadow: 0 2px 8px rgba(255, 215, 0, 0.5),
                0 0 12px rgba(255, 215, 0, 0.3);
  }
  50% {
    transform: scale(1.1);
    box-shadow: 0 2px 12px rgba(255, 215, 0, 0.7),
                0 0 20px rgba(255, 215, 0, 0.5);
  }
}

.avatar-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 50%;
}

.avatar-text {
  font-size: 24px;
  font-weight: bold;
  color: #ffffff;
}

.profile-info {
  flex: 1;
  min-width: 0;
}

.profile-name {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 8px;
  background: linear-gradient(135deg, var(--text-primary), var(--primary));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

/* Navigation Container */
.nav-container {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  overflow-x: hidden;
  margin-bottom: 16px;
}

/* Spacer */
.spacer {
  flex: 0 0 16px;
}

/* Coin Display */
.coin-display {
  background: linear-gradient(135deg, rgba(255, 215, 0, 0.15), rgba(255, 215, 0, 0.1));
  border: 2px solid rgba(255, 215, 0, 0.4);
  border-radius: 16px;
  padding: 16px 20px;
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
  flex-shrink: 0;
}

.coin-display::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 215, 0, 0.1), transparent);
  transition: left 0.6s;
}

.coin-display:hover::before {
  left: 100%;
}

.coin-display:hover {
  background: linear-gradient(135deg, rgba(255, 215, 0, 0.2), rgba(255, 215, 0, 0.15));
  border-color: rgba(255, 215, 0, 0.6);
  transform: translateY(-2px);
  box-shadow: 0 6px 25px rgba(255, 215, 0, 0.3);
}

/* Dark mode coin display */
[data-theme="dark"] .coin-display {
  background: linear-gradient(135deg, rgba(255, 215, 0, 0.3), rgba(255, 215, 0, 0.25));
  border: 2px solid rgba(255, 215, 0, 0.6);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
}

[data-theme="dark"] .coin-display:hover {
  background: linear-gradient(135deg, rgba(255, 215, 0, 0.4), rgba(255, 215, 0, 0.35));
  border-color: rgba(255, 215, 0, 0.8);
  box-shadow: 0 6px 25px rgba(255, 215, 0, 0.5);
}

.coin-amount {
  font-size: 18px;
  font-weight: 700;
  color: #ffd700;
  text-shadow: 0 0 10px rgba(255, 215, 0, 0.5);
}

.coin-loading {
  color: rgba(255, 215, 0, 0.7);
  font-style: italic;
  font-size: 14px;
}

.coin-error {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
}

.error-icon {
  font-size: 18px;
}

.error-text {
  color: var(--error);
  font-size: 12px;
  flex: 1;
}

/* Theme Toggle */
.theme-toggle-container {
  background: rgba(255, 255, 255, 0.5);
  border-radius: 12px;
  padding: 12px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  transition: all 0.3s ease;
  flex-shrink: 0;
}

.theme-toggle-container:hover {
  background: rgba(255, 255, 255, 0.7);
  transform: translateY(-2px);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

/* Dark mode theme toggle */
[data-theme="dark"] .theme-toggle-container {
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.3);
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.3);
}

[data-theme="dark"] .theme-toggle-container:hover {
  background: rgba(255, 255, 255, 0.3);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
}

/* Enhanced Vuetify List Items */
:deep(.v-list-item) {
  border: 2px solid rgba(255, 255, 255, 0.2) !important;
  margin-bottom: 8px !important;
  border-radius: 12px !important;
  transition: all 0.3s ease !important;
  position: relative !important;
  overflow: hidden !important;
  min-height: 48px !important;
  max-height: 60px !important;
}

:deep(.v-list-item::before) {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: left 0.5s;
  z-index: 1;
}

:deep(.v-list-item:hover::before) {
  left: 100%;
}

:deep(.v-list-item:hover) {
  background: rgba(255, 255, 255, 0.8) !important;
  transform: translateX(8px) !important;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15) !important;
  border-color: rgba(106, 122, 90, 0.3) !important;
}

:deep(.v-list-item:hover .v-list-item__content) {
  color: var(--text-primary) !important;
}

:deep(.v-list-item:hover .v-icon) {
  color: var(--text-primary) !important;
}

:deep(.v-list-item--active) {
  background: linear-gradient(135deg, var(--primary), var(--secondary)) !important;
  color: white !important;
  border-color: var(--primary) !important;
  box-shadow: 0 6px 25px rgba(106, 122, 90, 0.3) !important;
}

:deep(.v-list-item--active:hover) {
  background: linear-gradient(135deg, var(--primary), var(--secondary)) !important;
  color: white !important;
  transform: translateX(8px) scale(1.02) !important;
  box-shadow: 0 8px 30px rgba(106, 122, 90, 0.4) !important;
}

:deep(.v-list-item--active:hover .v-list-item__content) {
  color: white !important;
}

:deep(.v-list-item--active:hover .v-icon) {
  color: white !important;
}

:deep(.v-list-item__prepend) {
  margin-right: 16px !important;
}

:deep(.v-list-item__content) {
  font-weight: 600 !important;
  font-size: 15px !important;
}

:deep(.v-list-item--active .v-list-item__content) {
  color: white !important;
}

:deep(.v-list-item--active .v-icon) {
  color: white !important;
}

/* Dark mode styles for Vuetify list items */
[data-theme="dark"] :deep(.v-list-item) {
  background: #000000 !important;
  border: 2px solid rgba(255, 255, 255, 0.25) !important;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.4) !important;
  backdrop-filter: blur(10px) !important;
}

[data-theme="dark"] :deep(.v-list-item:hover) {
  background: rgba(255, 255, 255, 0.25) !important;
  box-shadow: 0 6px 24px rgba(0, 0, 0, 0.6) !important;
  border-color: rgba(106, 122, 90, 0.6) !important;
  transform: translateY(-1px) !important;
}

[data-theme="dark"] :deep(.v-list-item:hover .v-list-item__content) {
  color: white !important;
}

[data-theme="dark"] :deep(.v-list-item:hover .v-icon) {
  color: white !important;
}

[data-theme="dark"] :deep(.v-list-item .v-list-item__content) {
  color: white !important;
  font-weight: 600 !important;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.5) !important;
}

[data-theme="dark"] :deep(.v-list-item .v-icon) {
  color: white !important;
  filter: drop-shadow(0 1px 2px rgba(0, 0, 0, 0.5)) !important;
}

[data-theme="dark"] :deep(.v-list-item--active) {
  background: linear-gradient(135deg, var(--primary), var(--secondary)) !important;
  border-color: var(--primary) !important;
  box-shadow: 0 6px 25px rgba(106, 122, 90, 0.5) !important;
}

[data-theme="dark"] :deep(.v-list-item--active:hover) {
  background: linear-gradient(135deg, var(--primary), var(--secondary)) !important;
  color: white !important;
  box-shadow: 0 8px 30px rgba(106, 122, 90, 0.6) !important;
}

[data-theme="dark"] :deep(.v-list-item--active:hover .v-list-item__content) {
  color: white !important;
}

[data-theme="dark"] :deep(.v-list-item--active:hover .v-icon) {
  color: white !important;
}

/* Height responsive adjustments */
@media (max-height: 800px) {
  .sidebar-container {
    padding: 16px;
  }
  
  .profile-header {
    margin-bottom: 20px;
  }
  
  .profile-avatar-container {
    padding: 16px;
  }
  
  .profile-avatar {
    width: 48px;
    height: 48px;
    font-size: 20px;
  }
  
  .profile-name {
    font-size: 16px;
  }
  
  .nav-container {
    margin-bottom: 12px;
  }
  
  :deep(.v-list-item) {
    margin-bottom: 6px !important;
    min-height: 44px !important;
    max-height: 56px !important;
  }
  
  .coin-display {
    padding: 12px 16px;
    margin-bottom: 16px;
  }
  
  .coin-amount {
    font-size: 16px;
  }
  
  .theme-toggle-container {
    padding: 10px;
  }
}

@media (max-height: 600px) {
  .sidebar-container {
    padding: 12px;
  }
  
  .profile-header {
    margin-bottom: 16px;
  }
  
  .profile-avatar-container {
    padding: 12px;
    gap: 12px;
  }
  
  .profile-avatar {
    width: 44px;
    height: 44px;
    font-size: 18px;
  }
  
  .profile-name {
    font-size: 15px;
  }
  
  .nav-container {
    margin-bottom: 8px;
  }
  
  :deep(.v-list-item) {
    margin-bottom: 4px !important;
    min-height: 40px !important;
    max-height: 52px !important;
  }
  
  .coin-display {
    padding: 10px 14px;
    margin-bottom: 12px;
  }
  
  .coin-amount {
    font-size: 15px;
  }
  
  .theme-toggle-container {
    padding: 8px;
  }
}

/* Very small heights */
@media (max-height: 500px) {
  .sidebar-container {
    padding: 8px;
  }
  
  .profile-header {
    margin-bottom: 12px;
  }
  
  .profile-avatar-container {
    padding: 10px;
    gap: 10px;
  }
  
  .profile-avatar {
    width: 40px;
    height: 40px;
    font-size: 16px;
  }
  
  .profile-name {
    font-size: 14px;
  }
  
  .nav-container {
    margin-bottom: 6px;
  }
  
  :deep(.v-list-item) {
    margin-bottom: 3px !important;
    min-height: 36px !important;
    max-height: 48px !important;
  }
  
  .coin-display {
    padding: 8px 12px;
    margin-bottom: 8px;
  }
  
  .coin-amount {
    font-size: 14px;
  }
  
  .theme-toggle-container {
    padding: 6px;
  }
}
</style>