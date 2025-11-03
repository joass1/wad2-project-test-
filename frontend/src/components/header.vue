<template>
  <v-app-bar elevation="0" class="app-header" app>
    <v-btn
      icon
      variant="text"
      class="hamburger-btn ml-2"
      @click="$emit('update:modelValue', !modelValue)"
    >
      <v-icon class="hamburger-icon">mdi-menu</v-icon>
      <div class="shimmer-overlay"></div>
    </v-btn>

    <v-toolbar-title class="text-h6 font-weight-bold ml-2 title-shimmer">
      Pomogotchi
    </v-toolbar-title>

    <v-spacer />


  </v-app-bar>
</template>

<script setup>
defineProps({
  modelValue: Boolean
})

defineEmits(['update:modelValue'])
</script>

<style scoped>
.app-header {
  border-bottom: 1px solid rgba(0, 0, 0, 0.12);
  background: white;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.hamburger-btn {
  position: relative;
  overflow: hidden;
  transition: all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.hamburger-btn:hover {
  transform: scale(1.1);
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(168, 85, 247, 0.1) 100%);
}

.hamburger-btn:active {
  transform: scale(0.95);
}

.hamburger-icon {
  transition: transform 0.6s cubic-bezier(0.68, -0.55, 0.265, 1.55);
  position: relative;
  z-index: 2;
}

.hamburger-btn:hover .hamburger-icon {
  transform: rotate(180deg);
  filter: drop-shadow(0 0 8px rgba(99, 102, 241, 0.5));
}

/* Shimmer effect on hamburger button */
.shimmer-overlay {
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: linear-gradient(
    45deg,
    transparent 30%,
    rgba(255, 255, 255, 0.3) 50%,
    transparent 70%
  );
  transform: translateX(-100%) translateY(-100%) rotate(45deg);
  transition: transform 0.6s;
}

.hamburger-btn:hover .shimmer-overlay {
  transform: translateX(100%) translateY(100%) rotate(45deg);
}

/* Title shimmer effect */
.title-shimmer {
  background: linear-gradient(
    90deg,
    #333 0%,
    #666 25%,
    #999 50%,
    #666 75%,
    #333 100%
  );
  background-size: 200% 100%;
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  animation: shimmer 3s linear infinite;
}

@keyframes shimmer {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}

/* Avatar glow effect */
.avatar-glow {
  transition: all 0.4s ease;
  animation: pulse-glow 2s ease-in-out infinite;
}

.avatar-glow:hover {
  transform: scale(1.1);
  box-shadow: 0 0 20px rgba(99, 102, 241, 0.6);
}

@keyframes pulse-glow {
  0%, 100% {
    box-shadow: 0 0 10px rgba(99, 102, 241, 0.3);
  }
  50% {
    box-shadow: 0 0 20px rgba(168, 85, 247, 0.5);
  }
}
</style>