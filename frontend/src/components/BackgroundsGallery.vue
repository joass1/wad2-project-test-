<script setup>
import { ref } from 'vue'
import { useBackground } from '@/composables/useBackgrounds'

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
            transition: 'all 0.3s ease'
        }
    }
    return {
        backgroundColor: '#e0e0e0',
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

    <v-dialog v-model="dialog" max-width="900" scrollable>
      <v-card rounded="xl" class="pa-4">
        <v-card-title class="text-h6 font-weight-medium pa-4 pb-2">
          Choose Your Study Background
        </v-card-title>
        <v-card-subtitle class="px-4 pb-4">
          Selected: 
          <span class="font-weight-bold text-primary">
            {{ getCurrentBackground().name }}
          </span>
        </v-card-subtitle>

        <v-card-text class="pt-0">
          <v-row dense>
            <v-col
              v-for="bg in BACKGROUNDS"
              :key="bg.id"
              cols="6"
              sm="4"
            >
              <v-card
                :class="['pa-2 bg-card', { 'bg-selected': selectedBackgroundId === bg.id }]"
                @click="selectBackground(bg.id)"
                rounded="lg"
                height="160"
                variant="outlined"
              >
                <div v-if="bg.path" class="bg-preview" :style="{ backgroundImage: `url(${bg.path})` }"></div>
                <div v-else class="bg-preview-none">
                  <span class="text-h5">🍂</span>
                </div>
                <div class="bg-overlay">
                  <span class="font-weight-bold text-white text-shadow text-body-2">{{ bg.name }}</span>
                  <v-icon v-if="selectedBackgroundId === bg.id" color="success" size="large" class="mt-2">
                    mdi-check-circle
                  </v-icon>
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
  background: rgba(255, 255, 255, 0.95) !important; 
  border: 1px solid var(--surface-lighter);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  min-height: 80px;
  transition: all 0.2s ease;
}

.background-select-card:hover {
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  transform: translateY(-1px);
}

[data-theme="dark"] .background-select-card {
  background: rgba(30, 30, 30, 0.95) !important;
}

.bg-card {
  position: relative;
  cursor: pointer;
  overflow: hidden;
  transition: all 0.2s ease;
  background-size: cover !important; 
  background-position: center !important; 
  padding: 0 !important;
}

.bg-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
}

.bg-selected {
  border: 4px solid var(--v-theme-primary) !important;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3), 0 0 0 3px var(--v-theme-primary);
}

.bg-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  filter: none !important;
  background-color: rgba(0, 0, 0, 0.15); 
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  transition: background-color 0.2s;
  z-index: 2; 
}

.bg-card:not(.bg-selected) .bg-overlay:hover {
    background-color: rgba(0, 0, 0, 0.3);
}
.bg-preview {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-size: cover;
  background-position: center;
  z-index: 1;
}

.bg-preview-none {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #e0e0e0 0%, #f5f5f5 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1;
}

.text-shadow {
    text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.9);
}
</style>