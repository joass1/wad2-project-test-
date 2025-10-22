<template>
  <v-navigation-drawer
    :model-value="modelValue"
    @update:model-value="$emit('update:modelValue', $event)"
    :rail="!modelValue"
    app
    permanent
    :width="287"
    class="sb-drawer"
  >
    <div class="sidebar-container">
      <!-- Profile header -->
      <div class="profile-header">
        <div class="profile-avatar-container">
          <div class="profile-avatar">
            <img v-if="displayAvatar" :src="displayAvatar" alt="Profile Avatar" class="avatar-image" />
            <span v-else class="avatar-text">{{ displayName.charAt(0).toUpperCase() }}</span>
          </div>
          <transition name="slide-fade">
            <div v-show="modelValue" class="profile-info">
              <div class="profile-name">{{ displayName }}</div>
              <div class="level-badge">Level {{ level }}</div>
            </div>
          </transition>
        </div>
      </div>

      <!-- Nav -->
      <v-list nav density="comfortable">
        <v-list-item to="/dashboard" :prepend-icon="modelValue ? 'mdi-home-outline' : ''" :title="modelValue ? 'Dashboard' : ''" rounded="lg">
          <v-icon v-if="!modelValue">mdi-home-outline</v-icon>
          <v-tooltip v-if="!modelValue" activator="parent" location="end">Dashboard</v-tooltip>
        </v-list-item>
        
        <v-list-item to="/timer" :prepend-icon="modelValue ? 'mdi-timer-outline' : ''" :title="modelValue ? 'Study Timer' : ''" rounded="lg">
          <v-icon v-if="!modelValue">mdi-timer-outline</v-icon>
          <v-tooltip v-if="!modelValue" activator="parent" location="end">Study Timer</v-tooltip>
        </v-list-item>
        
        <v-list-item to="/task-tracker" :prepend-icon="modelValue ? 'mdi-checkbox-marked-outline' : ''" :title="modelValue ? 'Task Tracker' : ''" rounded="lg">
          <v-icon v-if="!modelValue">mdi-checkbox-marked-outline</v-icon>
          <v-tooltip v-if="!modelValue" activator="parent" location="end">Task Tracker</v-tooltip>
        </v-list-item>
        
        <v-list-item to="/progress" :prepend-icon="modelValue ? 'mdi-chart-line' : ''" :title="modelValue ? 'Progress' : ''" rounded="lg">
          <v-icon v-if="!modelValue">mdi-chart-line</v-icon>
          <v-tooltip v-if="!modelValue" activator="parent" location="end">Progress</v-tooltip>
        </v-list-item>
        
        <v-list-item to="/checkin" :prepend-icon="modelValue ? 'mdi-heart-outline' : ''" :title="modelValue ? 'Wellness Check-in' : ''" rounded="lg">
          <v-icon v-if="!modelValue">mdi-heart-outline</v-icon>
          <v-tooltip v-if="!modelValue" activator="parent" location="end">Wellness Check-in</v-tooltip>
        </v-list-item>
        
        <v-list-item to="/social-hub" :prepend-icon="modelValue ? 'mdi-account-group-outline' : ''" :title="modelValue ? 'Social' : ''" rounded="lg">
          <v-icon v-if="!modelValue">mdi-account-group-outline</v-icon>
          <v-tooltip v-if="!modelValue" activator="parent" location="end">Social</v-tooltip>
        </v-list-item>
        
        <v-list-item to="/pet" :prepend-icon="modelValue ? 'mdi-paw' : ''" :title="modelValue ? 'Pet' : ''" rounded="lg">
          <v-icon v-if="!modelValue">mdi-paw</v-icon>
          <v-tooltip v-if="!modelValue" activator="parent" location="end">Pet</v-tooltip>
        </v-list-item>
        
        <v-list-item to="/profile" :prepend-icon="modelValue ? 'mdi-account-outline' : ''" :title="modelValue ? 'Profile' : ''" rounded="lg">
          <v-icon v-if="!modelValue">mdi-account-outline</v-icon>
          <v-tooltip v-if="!modelValue" activator="parent" location="end">Profile</v-tooltip>
        </v-list-item>
      </v-list>

      <div class="spacer"></div>

      <!-- Coin display -->
      <transition name="slide-fade">
        <div v-show="modelValue" class="coin-display">
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
import { onMounted } from 'vue'
import ThemeToggle from '@/components/ThemeToggle.vue'
import AnimatedCoin from '@/components/AnimatedCoin.vue'
import { useCoins } from '@/composables/useCoins.js'
import { useUserProfile } from '@/composables/useUserProfile.js'

defineProps({
  modelValue: Boolean
})

defineEmits(['update:modelValue'])

// Use shared coin state
const { coins, coinsLoading, coinsError, fetchCoins } = useCoins()

// Use shared profile state
const { displayName, displayAvatar, level } = useUserProfile()

onMounted(() => {
  // Only fetch if coins haven't been loaded yet
  if (coins.value === null && !coinsLoading.value) {
    fetchCoins()
  }
})
</script>

<style scoped>
.sb-drawer {
  border-right: 1px solid rgba(0, 0, 0, 0.12);
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
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
}

.profile-avatar-container {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  background: rgba(255, 255, 255, 0.6);
  border-radius: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.profile-avatar-container:hover {
  background: rgba(255, 255, 255, 0.8);
  transform: translateY(-2px);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.15);
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
  color: white;
  box-shadow: 0 4px 15px rgba(106, 122, 90, 0.3);
  border: 3px solid rgba(255, 255, 255, 0.8);
  transition: all 0.3s ease;
  flex-shrink: 0;
}

.profile-avatar:hover {
  transform: scale(1.05) rotate(5deg);
  box-shadow: 0 6px 25px rgba(106, 122, 90, 0.4);
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
  color: white;
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

.level-badge {
  background: linear-gradient(135deg, var(--primary), var(--secondary));
  color: white;
  padding: 6px 12px;
  border-radius: 16px;
  font-size: 12px;
  font-weight: 600;
  display: inline-block;
  box-shadow: 0 2px 12px rgba(106, 122, 90, 0.3);
  border: 2px solid rgba(255, 255, 255, 0.2);
  transition: all 0.3s ease;
}

.level-badge:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 20px rgba(106, 122, 90, 0.4);
}

/* Spacer */
.spacer {
  flex: 1;
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
  color: #ff6b6b;
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
</style>