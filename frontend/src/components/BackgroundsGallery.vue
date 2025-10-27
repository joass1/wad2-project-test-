<script setup>
import { ref } from 'vue'
// FIX: Use the correct function name 'useBackground'
import { useBackground } from '@/composables/useBackgrounds'

// Destructure the needed properties and functions
const { selectedBackgroundId, saveBackground, getCurrentBackground, BACKGROUNDS } = useBackground()

const dialog = ref(false)

function selectBackground(backgroundId) {
  saveBackground(backgroundId)
  dialog.value = false
}

function getCardStyle(background) {
    if (background.path) {
        return {
            backgroundImage: `url(${background.path})`,
            backgroundSize: 'cover',
            backgroundPosition: 'center',
            // FIX: Removed filter: 'blur(3px) brightness(0.9)', 
            // and opacity: '0.8', to show the image clearly.
            transition: 'all 0.3s ease'
        }
    }
    // Style for the 'none' option
    return {
        backgroundColor: '#e0e0e0', // Light grey or a default color
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        transition: 'all 0.3s ease'
    }
}
</script>

<template>
  <div>
    <v-card
      rounded="xl" 
      elevation="0" 
      class="pa-6 cursor-pointer d-flex align-center justify-center text-center background-select-card"
      @click="dialog = true"
    >
      <div class="text-caption text-medium-emphasis">
        <v-icon size="small" start>mdi-image-multiple</v-icon>
        Change Background
      </div>
    </v-card>

    <v-dialog v-model="dialog" max-width="800">
      <v-card rounded="xl" class="pa-4">
        <v-card-title class="text-h6 font-weight-medium pa-4 pb-2">
          Choose Your Study Background
        </v-card-title>
        <v-card-subtitle class="px-4">
          Selected: 
          <span class="font-weight-bold text-primary">
            {{ getCurrentBackground().name }}
          </span>
        </v-card-subtitle>

        <v-card-text class="pt-4">
          <v-row>
            <v-col
              v-for="bg in BACKGROUNDS"
              :key="bg.id"
              cols="6"
              sm="4"
              md="3"
            >
              <v-card
                :class="['pa-2 h-100 bg-card', { 'bg-selected': selectedBackgroundId === bg.id }]"
                @click="selectBackground(bg.id)"
                :style="getCardStyle(bg)"
                rounded="lg"
                height="120"
                variant="outlined"
              >
                <div class="bg-overlay">
                    <span class="font-weight-bold text-white text-shadow">{{ bg.name }}</span>
                    <v-icon v-if="selectedBackgroundId === bg.id" color="success" size="large">
                        mdi-check-circle
                    </v-icon>
                    <span v-if="bg.id === 'none'" class="text-h6 text-medium-emphasis text-white text-shadow">🚫</span>
                </div>
              </v-card>
            </v-col>
          </v-row>
        </v-card-text>
        
        <v-card-actions class="pa-4 pt-0">
          <v-spacer></v-spacer>
          <v-btn color="primary" variant="text" @click="dialog = false">Close</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<style scoped>
.background-select-card {
  height: 100%;
  border: 1px dashed var(--surface-lighter);
  background: var(--surface) !important; 
  min-height: 80px; 
}

.bg-card {
  position: relative;
  cursor: pointer;
  overflow: hidden;
  transition: all 0.2s ease;
  background-size: cover !important; 
  background-position: center !important; 
  
  /* FIX 1: Remove potentially conflicting box-sizing or border properties */
  padding: 0 !important;
}

.bg-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
}

.bg-selected {
  border: 4px solid var(--primary) !important;
  box-shadow: 0 0 0 2px var(--primary);
}

.bg-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  
  /* FIX 2: Ensure the internal thumbnail image is NOT blurred by overriding any global filter */
  filter: none !important;
  
  /* Use a subtle overlay for text readability */
  background-color: rgba(0, 0, 0, 0.15); 
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  transition: background-color 0.2s;
  z-index: 2; 
}

.bg-card:not(.bg-selected) .bg-overlay:hover {
    background-color: rgba(0, 0, 0, 0.05);
}

.text-shadow {
    text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.8);
}
</style>