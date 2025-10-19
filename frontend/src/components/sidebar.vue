<template>
  <div class="pa-4 d-flex flex-column h-100">
    <!-- Profile header -->
    <div class="d-flex align-center mb-4 ga-3">
      <v-avatar size="44" color="secondary" variant="tonal">🐱</v-avatar>
      <div>
        <div class="text-body-1 font-weight-semibold">qw</div>
        <v-chip size="x-small" color="primary" variant="tonal">Level 1</v-chip>
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

    <!-- Bottom theme toggle -->
    <div class="mt-4 pt-2 border-top">
      <ThemeToggle compact />
    </div>
  </div>
</template>

<script setup>
import ThemeToggle from '@/components/ThemeToggle.vue'
</script>

<style scoped>
.border-top {
  border-top: 1px solid var(--surface-lighter);
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
</style>