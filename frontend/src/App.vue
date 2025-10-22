<template>
  <v-app>
    <!-- Login route renders only the view (no navbar, no sidebar) -->
    <router-view v-if="isLogin" />

    <!-- Authenticated layout: permanent sidebar, scrollable main -->
    <template v-else>
      <!-- Header - always visible except in fullscreen mode -->
      <Header v-if="!isFullscreen" v-model="sidebarOpen" />

      <!-- Sidebar only shows when NOT in fullscreen mode -->
      <Sidebar
        v-if="!isFullscreen"
        v-model="sidebarOpen"
      />

      <v-main :class="['sb-main', { 'fullscreen-main': isFullscreen }]">
        <!-- Listen for the toggle-fullscreen event from timer page -->
        <router-view @toggle-fullscreen="handleFullscreen" />
      </v-main>

      <!-- NEW: Global floating pet - Always visible on all pages -->
      <GlobalDesktopPet />
    </template>
  </v-app>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import Sidebar from '@/components/sidebar.vue'
import Header from '@/components/header.vue'
import GlobalDesktopPet from '@/components/GlobalDesktopPet.vue'

const route = useRoute()
const isLogin = computed(() => route.name === 'Login')

// Sidebar state - starts open
const sidebarOpen = ref(true)

// Fullscreen mode state
const isFullscreen = ref(false)

function handleFullscreen(value) {
  isFullscreen.value = value
}
</script>

<style scoped>
.sb-main {
  min-height: 100vh;
  background: var(--background);
}

.fullscreen-main {
  padding: 0 !important;
  margin: 0 !important;
}
</style>