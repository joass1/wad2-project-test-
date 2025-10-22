<template>
  <v-navigation-drawer
    :model-value="modelValue"
    @update:model-value="$emit('update:modelValue', $event)"
    :rail="!modelValue"
    app
    permanent
    :width="260"
    class="sb-drawer"
  >
    <div class="pa-4 d-flex flex-column h-100">
      <!-- Profile header -->
      <div class="d-flex align-center mb-4 ga-3 profile-section">
        <v-avatar size="44" color="secondary" variant="tonal" class="avatar-bounce">🐱</v-avatar>
        <transition name="slide-fade">
          <div v-show="modelValue" class="profile-info">
            <div class="text-body-1 font-weight-semibold">qw</div>
            <v-chip size="x-small" color="primary" variant="tonal">Level 1</v-chip>
          </div>
        </transition>
      </div>

      <!-- Nav -->
      <v-list nav density="comfortable">
        <transition-group name="stagger-fade">
          <v-list-item 
            v-for="(item, index) in navItems" 
            :key="item.to"
            :to="item.to" 
            :prepend-icon="item.icon" 
            :title="modelValue ? item.title : ''"
            rounded="lg"
            class="nav-item"
            :style="{ transitionDelay: `${index * 50}ms` }"
          >
            <v-tooltip v-if="!modelValue" activator="parent" location="end">
              {{ item.title }}
            </v-tooltip>
          </v-list-item>
        </transition-group>
      </v-list>

      <v-spacer />

      <!-- Bottom theme toggle -->
      <div class="mt-4 pt-2 border-top">
        <ThemeToggle compact />
      </div>
    </div>
  </v-navigation-drawer>
</template>

<script setup>
import ThemeToggle from '@/components/ThemeToggle.vue'

defineProps({
  modelValue: Boolean
})

defineEmits(['update:modelValue'])

const navItems = [
  { to: '/dashboard', icon: 'mdi-home-outline', title: 'Dashboard' },
  { to: '/timer', icon: 'mdi-timer-outline', title: 'Study Timer' },
  { to: '/task-tracker', icon: 'mdi-checkbox-marked-outline', title: 'Task Tracker' },
  { to: '/progress', icon: 'mdi-chart-line', title: 'Progress' },
  { to: '/checkin', icon: 'mdi-heart-outline', title: 'Wellness Check-in' },
  { to: '/social-hub', icon: 'mdi-account-group-outline', title: 'Social' },
  { to: '/pet', icon: 'mdi-paw', title: 'Pet' },
  { to: '/profile', icon: 'mdi-account-outline', title: 'Profile' }
]
</script>

<style scoped>
.sb-drawer {
  border-right: 1px solid var(--surface-lighter);
  background: linear-gradient(180deg, #ffffff 0%, #fafafa 100%);
  transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

.profile-section {
  overflow: hidden;
}

.avatar-bounce {
  transition: transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.avatar-bounce:hover {
  transform: scale(1.15) rotate(5deg);
}

/* Slide fade transition for profile info */
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

/* Stagger fade for nav items */
.stagger-fade-enter-active,
.stagger-fade-leave-active {
  transition: all 0.3s ease;
}

.stagger-fade-enter-from,
.stagger-fade-leave-to {
  opacity: 0;
  transform: translateX(-10px);
}

.border-top {
  border-top: 1px solid var(--surface-lighter);
}

.nav-item {
  position: relative;
  overflow: hidden;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.nav-item::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(
    90deg,
    transparent,
    rgba(99, 102, 241, 0.1),
    transparent
  );
  transition: left 0.5s;
}

.nav-item:hover::before {
  left: 100%;
}

:deep(.v-list-item) {
  border: 1px solid var(--surface-lighter);
  margin-bottom: 8px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  backdrop-filter: blur(10px);
}

:deep(.v-list-item:hover) {
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.05) 0%, rgba(168, 85, 247, 0.05) 100%);
  transform: translateX(5px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

:deep(.v-list-item--active) {
  background: linear-gradient(135deg, #0b0b15 0%, #1a1a2e 100%) !important;
  color: #fff !important;
  box-shadow: 0 4px 20px rgba(11, 11, 21, 0.4);
  transform: translateX(8px);
}

:deep(.v-list-item--active::after) {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 4px;
  height: 60%;
  background: linear-gradient(180deg, #6366f1 0%, #a855f7 100%);
  border-radius: 0 4px 4px 0;
  animation: pulse-line 2s ease-in-out infinite;
}

@keyframes pulse-line {
  0%, 100% {
    opacity: 1;
    box-shadow: 0 0 10px rgba(99, 102, 241, 0.5);
  }
  50% {
    opacity: 0.7;
    box-shadow: 0 0 20px rgba(168, 85, 247, 0.8);
  }
}
</style>