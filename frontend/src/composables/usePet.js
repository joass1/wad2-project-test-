import { ref, onMounted, onUnmounted } from 'vue';
import { io } from 'socket.io-client';

export function usePet() {
    const socket = ref(null);
    const petState = ref({
        x: 100,
        y: 100,
        animation: 'idle',
        frame: 0,
        is_grabbed: false
    });
    const petConfig = ref(null);
    const isConnected = ref(false);

    // Initialize socket connection
    const connect = () => {
        socket.value = io('http://localhost:8000', {
            transports: ['websocket'],
            reconnection: true
        });

        socket.value.on('connect', () => {
            console.log('Connected to pet backend');
            isConnected.value = true;
        });

        socket.value.on('disconnect', () => {
            console.log('Disconnected from pet backend');
            isConnected.value = false;
        });

        // CRITICAL: Listen for backend pet updates
        socket.value.on('pet_update', (data) => {
            console.log('📡 Received pet_update from backend:', data)

            // CRITICAL: Only update from backend if NOT currently dragging
            // Check if this component is dragging by seeing if local state says grabbed
            if (!petState.value.is_grabbed) {
                petState.value.x = data.x
                petState.value.y = data.y
            }

            // Always update animation and grab state
            petState.value.animation = data.animation
            petState.value.is_grabbed = data.is_grabbed
        })

        socket.value.on('pet_state', (data) => {
            console.log('📡 Received initial pet_state:', data);
            petState.value.x = data.x;
            petState.value.y = data.y;
            petState.value.animation = data.animation;
            petState.value.is_grabbed = data.is_grabbed;
        });
    };

    // Fetch pet configuration
    const loadConfig = async () => {
        try {
            const response = await fetch('http://localhost:8000/pet/config');
            petConfig.value = await response.json();
            console.log('✅ Loaded pet config:', petConfig.value);
        } catch (error) {
            console.error('Failed to load pet config:', error);
        }
    };

    // Move pet to position

    const movePet = (x, y) => {
        // Update local state immediately for smooth dragging
        petState.value.x = x
        petState.value.y = y

        // Always send to backend so it knows the latest position
        if (socket.value && isConnected.value) {
            socket.value.emit('move_pet', { x, y })
        }
    }
    // Grab/release pet
    const grabPet = (grabbed) => {
        console.log(`Sending grab_pet to backend: ${grabbed}`);
        if (socket.value && isConnected.value) {
            socket.value.emit('grab_pet', { grabbed });
        } else {
            console.error('❌ Socket not connected, cannot grab pet');
        }
    };

    // Initialize pet with canvas dimensions
    const initializePet = async (width, height) => {
        try {
            console.log(`🎮 Initializing pet with canvas: ${width}x${height}`);
            await fetch('http://localhost:8000/pet/init', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ canvas_width: width, canvas_height: height })
            });
        } catch (error) {
            console.error('Failed to initialize pet:', error);
        }
    };

    onMounted(() => {
        connect();
        loadConfig();
    });

    onUnmounted(() => {
        if (socket.value) {
            socket.value.disconnect();
        }
    });

    return {
        petState,
        petConfig,
        isConnected,
        movePet,
        grabPet,
        initializePet
    };
}
