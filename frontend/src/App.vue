<template>
  <v-app>
    <!-- Login route renders only the view (no navbar, no sidebar) -->
    <router-view v-if="isLogin" />

    <!-- Authenticated layout: permanent sidebar, scrollable main -->
    <template v-else>
      <!-- Sidebar only shows when NOT in fullscreen mode -->
      <v-navigation-drawer
        v-if="!isFullscreen"
        app
        permanent
        width="287"
        class="sb-drawer"
      >
        <Sidebar />
      </v-navigation-drawer>

      <v-main :class="['sb-main', { 'fullscreen-main': isFullscreen }]">
        <!-- Listen for the toggle-fullscreen event from timer page -->
        <router-view @toggle-fullscreen="handleFullscreen" />
      </v-main>
    </template>
       <!-- NEW: Global floating pet - Hidden on login and petpage -->
    <GlobalDesktopPet v-if="!isLogin && !isPetPage" />
  </v-app>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import Sidebar from '@/components/sidebar.vue'
import GlobalDesktopPet from '@/components/GlobalDesktopPet.vue'


const route = useRoute()
const isLogin = computed(() => route.name === 'Login')
const isPetPage = computed(() => route.name === 'PetPage' || route.path === '/pet')

// Fullscreen mode state
const isFullscreen = ref(false)

function handleFullscreen(value) {
  isFullscreen.value = value
}
</script>

<style scoped>
.sb-drawer {
  border-right: 1px solid var(--surface-lighter);
  background: #fff;
}

.sb-main {
  min-height: 100vh;
  background: var(--background);
}

.fullscreen-main {
  padding: 0 !important;
  margin: 0 !important;
}
</style>