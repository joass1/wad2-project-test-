<template>
  <div class="pa-4 d-flex flex-column h-100">
    <!-- Profile header -->
    <div class="d-flex align-center mb-4 ga-3">
      <v-avatar size="44" color="secondary" variant="tonal">
        <img v-if="displayAvatar" :src="displayAvatar" alt="Profile Avatar" class="avatar-image" />
        <span v-else>{{ displayName.charAt(0).toUpperCase() }}</span>
      </v-avatar>
      <div>
        <div class="text-body-1 font-weight-semibold">{{ displayName }}</div>
        <v-chip size="x-small" color="primary" variant="tonal">Level {{ level }}</v-chip>
      </div>
    </div>

    <!-- Nav -->
    <v-list nav density="comfortable">
      <v-list-item to="/dashboard" prepend-icon="mdi-home-outline" title="Dashboard" rounded="lg" />
      <v-list-item to="/timer" prepend-icon="mdi-timer-outline" title="Study Timer" rounded="lg" />
      <v-list-item to="/task-tracker" prepend-icon="mdi-checkbox-marked-outline" title="Task Tracker" rounded="lg" />
      <v-list-item to="/progress" prepend-icon="mdi-chart-line" title="Progress" rounded="lg" />
      <v-list-item to="/checkin" prepend-icon="mdi-heart-outline" title="Wellness Check-in" rounded="lg" />
      <v-list-item to="/social-hub" prepend-icon="mdi-account-group-outline" title="Social" rounded="lg" />
      <v-list-item to="/pet" prepend-icon="mdi-paw" title="Pet" rounded="lg" />
      <v-list-item to="/profile" prepend-icon="mdi-account-outline" title="Profile" rounded="lg" />
    </v-list>

    <v-spacer />

    <!-- Coin display -->
    <div class="coin-display mb-3 pa-3 d-flex align-center ga-2">
      <template v-if="coinsLoading">
        <div class="coin-loading text-body-2">Loading coins...</div>
      </template>
      <template v-else-if="coinsError">
        <div class="coin-error">
          <div class="error-icon">⚠️</div>
          <div class="error-text text-caption">{{ coinsError }}</div>
        </div>
      </template>
      <template v-else>
        <AnimatedCoin :scale="2" :speed="8" />
        <div class="coin-amount text-h6 font-weight-bold">{{ coins }}</div>
      </template>
    </div>

    <!-- Bottom theme toggle -->
    <div class="mt-2 pt-2 border-top">
      <ThemeToggle compact />
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import ThemeToggle from '@/components/ThemeToggle.vue'
import AnimatedCoin from '@/components/AnimatedCoin.vue'
import { useCoins } from '@/composables/useCoins.js'
import { useUserProfile } from '@/composables/useUserProfile.js'

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
.border-top {
  border-top: 1px solid var(--surface-lighter);
}

.coin-display {
  background: rgba(255, 215, 0, 0.1);
  border: 2px solid rgba(255, 215, 0, 0.3);
  border-radius: 12px;
  transition: all 0.3s ease;
}

.coin-display:hover {
  background: rgba(255, 215, 0, 0.15);
  border-color: rgba(255, 215, 0, 0.5);
}

.coin-amount {
  color: #ffd700;
  text-shadow: 0 0 10px rgba(255, 215, 0, 0.3);
}

.coin-loading {
  color: rgba(255, 215, 0, 0.7);
  font-style: italic;
}

.coin-error {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
}

.error-icon {
  font-size: 20px;
}

.error-text {
  color: #ff6b6b;
  line-height: 1.2;
  flex: 1;
}

:deep(.v-list-item) {
  border: 1px solid var(--surface-lighter);
  margin-bottom: 8px;
  transition: background 0.2s ease;
}

:deep(.v-list-item:hover) {
  background: var(--surface-light);
}

:deep(.v-list-item--active) {
  background: #0b0b15 !important;
  color: #fff !important;
}

.avatar-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 50%;
}
</style>