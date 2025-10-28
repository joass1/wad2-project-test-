// frontend/src/composables/useBackgrounds.js

import { ref, watch, onMounted } from 'vue'
// NOTE: Assuming api.js exports an object with .get and .put methods
// that correctly handle authentication headers and errors.
import { api } from '@/lib/api.js' 
import { useAuth } from './useAuth'

// Available background options (Cleaned list with 4 custom GIFs + None)
export const BACKGROUNDS = [
    { id: 'castle', name: 'Animated Castle', thumbnail: '/background/gifs/castle.gif', path: '/background/gifs/castle.gif' },
    { id: 'lilypads', name: 'Lilypads Pond', thumbnail: '/background/gifs/lilypads.gif', path: '/background/gifs/lilypads.gif' },
    { id: 'cityskyline', name: 'City Skyline', thumbnail: '/background/gifs/cityskyline.gif', path: '/background/gifs/cityskyline.gif' },
    { id: 'winterpond', name: 'Winter Pond', thumbnail: '/background/gifs/winterpond.gif', path: '/background/gifs/winterpond.gif' },
    { id: 'sunsets', name: 'Sunsets', thumbnail: '/background/gifs/sunsets.gif', path: '/background/gifs/sunsets.gif' },
    { id: 'winterforest', name: 'Winter Forest', thumbnail: '/background/gifs/winterforest.gif', path: '/background/gifs/winterforest.gif' },
    { id: 'wintermountains', name: 'Winter Mountains', thumbnail: '/background/gifs/wintermountains.gif', path: '/background/gifs/wintermountains.gif' },
    { id: 'springmountains', name: 'Spring Mountains', thumbnail: '/background/gifs/springmountains.gif', path: '/background/gifs/springmountains.gif' },
    { id: 'rainymountains', name: 'Rainy Mountains', thumbnail: '/background/gifs/rainymountains.gif', path: '/background/gifs/rainymountains.gif' },
    { id: 'boating', name: 'Boating', thumbnail: '/background/gifs/boating.gif', path: '/background/gifs/boating.gif' },
    { id: 'japaninautumn', name: 'Japan in Autumn', thumbnail: '/background/gifs/japaninautumn.gif', path: '/background/gifs/japaninautumn.gif' },
    { id: 'wintertrain', name: 'Winter Train', thumbnail: '/background/gifs/wintertrain.gif', path: '/background/gifs/wintertrain.gif' },
    { id: 'japanesehouse', name: 'Japanese House', thumbnail: '/background/gifs/japanesehouse.gif', path: '/background/gifs/japanesehouse.gif' },
    { id: 'purpleforest', name: 'Purple Forest', thumbnail: '/background/gifs/purpleforest.gif', path: '/background/gifs/purpleforest.gif' },
    { id: 'none', name: 'None (Falling Leaves)', thumbnail: null, path: null } 
]

export function useBackground() {
    const { user } = useAuth()
    const selectedBackgroundId = ref('none') 
    const loading = ref(false)

    // Load background preference from the new endpoint
    async function loadPreferences() {
        if (!user.value) return

        loading.value = true
        try {
            // FIX: Explicitly prepended '/api/' to form the correct route: /api/study-sessions/backgrounds
            const response = await api.get('/api/study-sessions/backgrounds')
            
            if (response && response.background_id) {
                 selectedBackgroundId.value = response.background_id
            } else {
                 selectedBackgroundId.value = 'none'
            }
        } catch (error) {
            // Log 404s but don't crash the app
            console.error('Error loading background preference:', error)
        } finally {
            loading.value = false
        }
    }

    // Save background preference via the new endpoint
    async function saveBackground(backgroundId) {
        if (!user.value) return

        loading.value = true
        try {
            const payload = { background_id: backgroundId }
            // FIX: Explicitly prepended '/api/'
            await api.put('/api/study-sessions/backgrounds', payload)
            selectedBackgroundId.value = backgroundId 

        } catch (error) {
            console.error('Error saving background:', error)
            throw error
        } finally {
            loading.value = false
        }
    }

    function getCurrentBackground() {
        return BACKGROUNDS.find(bg => bg.id === selectedBackgroundId.value) || BACKGROUNDS[BACKGROUNDS.length - 1]
    }

    watch(user, (newUser) => {
        if (newUser) {
            loadPreferences()
        } else {
            selectedBackgroundId.value = 'none'
        }
    }, { immediate: true })

    onMounted(loadPreferences)

    return {
        selectedBackgroundId,
        loading,
        saveBackground,
        getCurrentBackground,
        BACKGROUNDS
    }
}