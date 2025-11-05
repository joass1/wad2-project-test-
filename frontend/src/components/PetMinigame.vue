<script setup>
import { ref, onMounted, onUnmounted, computed, watch } from 'vue'
import { useCoins } from '@/composables/useCoins.js'
import { useGlobalPet } from '@/composables/useGlobalPet.js'
import { useMinigameProgress } from '@/composables/useMinigameProgress.js'
import { PET_CATALOG } from '@/data/petCatalog.js'
import AnimatedCoin from '@/components/AnimatedCoin.vue'

const props = defineProps({
  petSpriteUrl: {
    type: String,
    required: true
  },
  petSlice: {
    type: Number,
    required: true
  },
  petScale: {
    type: Number,
    default: 2
  },
  petAnimations: {
    type: Object,
    required: true
  }
})

// Game constants
const CANVAS_WIDTH = 800
const CANVAS_HEIGHT = 600
const WORLD_WIDTH = 1600
const WORLD_HEIGHT = 1200
const FPS = 60
const GAME_DURATION = 2.5 * 60 * 1000 // 2.5 minutes
const WAVE_DURATION = 30 * 1000 // 0.5 minute per wave
const BASE_ENEMY_SPAWN_INTERVAL = 4000 // Base spawn interval (4 seconds for wave 1)
const GOLD_DROP_CHANCE = 1 // 15% chance to drop gold

// Game state
const canvas = ref(null)
const ctx = ref(null)
const gameActive = ref(false)
const gamePaused = ref(false)
const gameOver = ref(false)
const gameWon = ref(false)
const showStartButton = ref(true)
const showLevelUp = ref(false)
const levelUpOptions = ref([])

// Daily play restriction - check if player has played for 2.5 minutes today
const remainingTimeToday = ref(GAME_DURATION) // Track remaining play time for today
const diedToday = ref(false) // Track if player died today
const deathStateLoading = ref(true) // Loading state for death check
const canPlayToday = computed(() => remainingTimeToday.value > 0 && !diedToday.value)

// Load today's remaining time from progress
async function loadDailyPlayTime() {
  console.log('=== LOAD DAILY PLAY TIME ===')
  deathStateLoading.value = true

  const savedProgress = await loadProgress()
  console.log('Loaded progress:', JSON.stringify(savedProgress, null, 2))

  if (savedProgress && savedProgress.last_played) {
    const lastPlayed = new Date(savedProgress.last_played)
    const today = new Date()

    console.log('Last played:', lastPlayed.toDateString())
    console.log('Today:', today.toDateString())

    // Check if last played was today
    if (lastPlayed.toDateString() === today.toDateString()) {
      // Calculate time already played today
      const timePlayedToday = savedProgress.time_played_today || 0
      remainingTimeToday.value = Math.max(0, GAME_DURATION - timePlayedToday)

      // Check if player died today
      diedToday.value = savedProgress.died_today || false

      console.log('Same day - Time played today:', timePlayedToday)
      console.log('Remaining time:', remainingTimeToday.value)
      console.log('Died today:', diedToday.value)
    } else {
      // New day, reset remaining time and death state
      remainingTimeToday.value = GAME_DURATION
      diedToday.value = false

      console.log('New day - Reset remaining time and death state')
    }
  } else {
    remainingTimeToday.value = GAME_DURATION
    diedToday.value = false

    console.log('No saved progress - Using defaults')
  }

  deathStateLoading.value = false
  console.log('=== LOAD DAILY PLAY TIME COMPLETE ===')
}

// Track time played in current session
const sessionStartTimeMs = ref(0)
const totalTimePlayed = ref(0)

// Game entities
const player = ref({
  x: CANVAS_WIDTH / 2,
  y: CANVAS_HEIGHT / 2,
  width: 32 * 2,
  height: 32 * 2,
  health: 100,
  maxHealth: 100,
  speed: 3,
  level: 1,
  exp: 0,
  nextLevelExp: 10,
  direction: 'down',
  moving: false,
  currentFrame: 0,
  frameTimer: 0,
  weapons: []
})

const enemies = ref([])
const projectiles = ref([])
const enemyProjectiles = ref([])
const gems = ref([])
const goldCoins = ref([])

// Game stats
const currentWave = ref(1)
const enemiesKilled = ref(0)
const gameTime = ref(0)
const startTime = ref(0)
const coinsEarned = ref(0) // Track coins earned during this game session

// Input state
const keys = ref({
  w: false,
  a: false,
  s: false,
  d: false,
  ArrowUp: false,
  ArrowLeft: false,
  ArrowDown: false,
  ArrowRight: false
})

// Coin integration
const { coins, updateCoins } = useCoins()
const startingCoins = ref(0) // Track coins at start of game

// Backend progress integration
const { progress, loadProgress, saveProgress, clearProgress } = useMinigameProgress()

// Images
const images = ref({
  petSprite: null,
  monster: null,
  shuriken: null,
  greenGem: null,
  goldCoin: null,
  // Flying monster sprites
  flyingMonsterFlying: null,
  flyingMonsterAttack: null,
  flyingMonsterHurt: null,
  flyingMonsterDeath: null,
  enemyProjectile: null
})

let gameLoopId = null
let enemySpawnId = null
let nextEnemyId = 0

// Load images
onMounted(async () => {
  loadImages()
  await loadDailyPlayTime()
})

function loadImages() {
  const petImg = new Image()
  petImg.src = props.petSpriteUrl
  petImg.onload = () => {
    images.value.petSprite = petImg
    console.log('Pet sprite loaded:', petImg.width, 'x', petImg.height)
  }

  const monsterImg = new Image()
  monsterImg.src = '/minigame/PunchMonster.png'
  monsterImg.onload = () => {
    images.value.monster = monsterImg
    console.log('Monster sprite loaded:', monsterImg.width, 'x', monsterImg.height)
    console.log('Calculated sprite frame size: width=' + (monsterImg.width / 8) + ', height=' + (monsterImg.height / 7))
  }
  monsterImg.onerror = (e) => {
    console.error('Failed to load Monster sprite:', e)
    console.log('Attempted path:', monsterImg.src)
  }

  const shurikenImg = new Image()
  shurikenImg.src = '/minigame/Shuriken.png'
  shurikenImg.onload = () => {
    images.value.shuriken = shurikenImg
    console.log('Shuriken sprite loaded:', shurikenImg.width, 'x', shurikenImg.height)
  }

  const gemImg = new Image()
  gemImg.src = '/minigame/greengem.png'
  gemImg.onload = () => {
    images.value.greenGem = gemImg
    console.log('Green gem sprite loaded:', gemImg.width, 'x', gemImg.height)
  }

  // Load animated gold coin sprite (01PixelCoinGold.png)
  // Sprite sheet: 16x16 pixel sprites, 6 frames total
  // First row has 4 frames, second row has 2 frames
  const goldImg = new Image()
  goldImg.src = '/01PixelCoinGold.png'
  goldImg.onload = () => {
    images.value.goldCoin = goldImg
    console.log('Gold coin sprite loaded:', goldImg.width, 'x', goldImg.height)
  }

  // Load flying monster sprites (64x64 px each frame)
  const flyingImg = new Image()
  flyingImg.src = '/minigame/flying monster/Flying.png'
  flyingImg.onload = () => {
    images.value.flyingMonsterFlying = flyingImg
    console.log('Flying monster (Flying) sprite loaded:', flyingImg.width, 'x', flyingImg.height)
  }

  const attackImg = new Image()
  attackImg.src = '/minigame/flying monster/Attack.png'
  attackImg.onload = () => {
    images.value.flyingMonsterAttack = attackImg
    console.log('Flying monster (Attack) sprite loaded:', attackImg.width, 'x', attackImg.height)
  }

  const hurtImg = new Image()
  hurtImg.src = '/minigame/flying monster/Hurt.png'
  hurtImg.onload = () => {
    images.value.flyingMonsterHurt = hurtImg
    console.log('Flying monster (Hurt) sprite loaded:', hurtImg.width, 'x', hurtImg.height)
  }

  const deathImg = new Image()
  deathImg.src = '/minigame/flying monster/Death.png'
  deathImg.onload = () => {
    images.value.flyingMonsterDeath = deathImg
    console.log('Flying monster (Death) sprite loaded:', deathImg.width, 'x', deathImg.height)
  }

  const enemyProjectileImg = new Image()
  enemyProjectileImg.src = '/minigame/flying monster/projectile.png'
  enemyProjectileImg.onload = () => {
    images.value.enemyProjectile = enemyProjectileImg
    console.log('Enemy projectile sprite loaded:', enemyProjectileImg.width, 'x', enemyProjectileImg.height)
  }
}

// Start game
async function startGame() {
  console.log('=== START GAME ===')

  if (!canPlayToday.value) {
    if (diedToday.value) {
      alert('You died today! Come back tomorrow to try again.')
    } else {
      alert('You have reached your 2.5 minute daily play limit! Come back tomorrow.')
    }
    return
  }

  // Load saved progress from backend
  const savedProgress = await loadProgress()
  console.log('Loaded progress when starting game:', JSON.stringify(savedProgress, null, 2))

  // Initialize player with saved progress or defaults
  const startingWave = savedProgress?.wave || 1
  const startingLevel = savedProgress?.level || 1
  const startingWeapons = savedProgress?.weapons || [{
    type: 'shuriken',
    damage: 1,
    fireRate: 1000,
    lastFired: 0,
    projectileSpeed: 5,
    range: 400
  }]
  const startingMaxHealth = savedProgress?.max_health || 100
  const startingSpeed = savedProgress?.speed || 3

  console.log('Starting values:')
  console.log('  - Wave:', startingWave)
  console.log('  - Level:', startingLevel)
  console.log('  - Max Health:', startingMaxHealth)
  console.log('  - Speed:', startingSpeed)
  console.log('  - Weapons:', startingWeapons)

  // Reset game state with saved progress - ALWAYS START WITH FULL HEALTH
  player.value = {
    x: CANVAS_WIDTH / 2,
    y: CANVAS_HEIGHT / 2,
    width: 32 * 2,
    height: 32 * 2,
    health: startingMaxHealth, // FULL HEALTH on start
    maxHealth: startingMaxHealth,
    speed: startingSpeed,
    level: startingLevel,
    exp: 0,
    nextLevelExp: 10 * Math.pow(1.5, startingLevel - 1), // Scale exp requirement
    direction: 'down',
    moving: false,
    currentFrame: 0,
    frameTimer: 0,
    weapons: startingWeapons.map(w => ({ ...w, lastFired: 0 }))
  }

  enemies.value = []
  projectiles.value = []
  enemyProjectiles.value = []
  gems.value = []
  goldCoins.value = []
  currentWave.value = startingWave
  enemiesKilled.value = 0
  // Adjust startTime to account for starting wave so gameTime calculation is correct
  // gameTime = Date.now() - startTime, so to start at wave N, startTime must be in the past
  const now = Date.now()
  startTime.value = now - ((startingWave - 1) * WAVE_DURATION)
  sessionStartTimeMs.value = now
  gameTime.value = 0 // Will be calculated from startTime in gameLoop
  totalTimePlayed.value = 0
  gameActive.value = true
  gamePaused.value = false
  gameOver.value = false
  gameWon.value = false
  showStartButton.value = false
  showLevelUp.value = false

  // Track starting coins and reset coins earned
  startingCoins.value = coins.value || 0
  coinsEarned.value = 0

  console.log(`Starting game at Wave ${startingWave}, Level ${startingLevel} with FULL HEALTH (${startingMaxHealth})`)

  // Set canvas context
  ctx.value = canvas.value.getContext('2d')
  ctx.value.imageSmoothingEnabled = false

  // Start game loop
  gameLoopId = setInterval(gameLoop, 1000 / FPS)

  // Start enemy spawning with dynamic interval
  startEnemySpawning()
}

// Reset daily timer (for testing)
async function resetDailyTimer() {
  console.log('=== RESET DAILY TIMER ===')
  // Clear backend progress so it starts fresh
  await clearProgress()
  // Reset local state
  remainingTimeToday.value = GAME_DURATION
  diedToday.value = false
  console.log('Daily timer reset - you have full time available!')
}

// Reset death state (for testing)
async function resetDeathState() {
  console.log('=== RESET DEATH STATE START ===')

  // Load current progress
  const savedProgress = await loadProgress()
  console.log('1. Loaded progress:', JSON.stringify(savedProgress, null, 2))

  if (!savedProgress) {
    console.error('No saved progress found!')
    diedToday.value = false
    await loadDailyPlayTime()
    return
  }

  // Re-save the same progress but with died_today=false
  // Note: Backend returns snake_case, we need to use camelCase for saveProgress
  const progressData = {
    wave: savedProgress.wave || 1,
    level: savedProgress.level || 1,
    weapons: savedProgress.weapons || [{
      type: 'shuriken',
      damage: 1,
      fireRate: 1000,
      projectileSpeed: 5,
      range: 400
    }],
    maxHealth: savedProgress.max_health || 100,
    speed: savedProgress.speed || 3
  }

  console.log('2. Prepared data to save:', JSON.stringify(progressData, null, 2))

  // Save with died_today=false to allow playing again (keep existing time played)
  const result = await saveProgress(progressData, savedProgress.time_played_today || 0, false)
  console.log('3. Save result:', result)

  if (!result.success) {
    console.error('Failed to save progress:', result.error)
    alert('Failed to reset death state. Check console for details.')
    return
  }

  // IMPORTANT: Reload progress from backend to verify it was saved correctly
  const reloadedProgress = await loadProgress()
  console.log('4. Reloaded progress after save:', JSON.stringify(reloadedProgress, null, 2))
  console.log('   - Wave:', reloadedProgress?.wave)
  console.log('   - Level:', reloadedProgress?.level)
  console.log('   - Max Health:', reloadedProgress?.max_health)
  console.log('   - Died Today:', reloadedProgress?.died_today)

  // Reset local state
  diedToday.value = false
  await loadDailyPlayTime()

  console.log('=== RESET DEATH STATE COMPLETE ===')
  console.log('Death state reset - you can play again with your saved progress!')
}

// Game loop
function gameLoop() {
  if (!gameActive.value || gamePaused.value || gameOver.value) return

  // Update game time
  gameTime.value = Date.now() - startTime.value
  totalTimePlayed.value = Date.now() - sessionStartTimeMs.value

  // Check if daily time limit reached
  if (totalTimePlayed.value >= remainingTimeToday.value) {
    endGame(true, 'timeLimit')
    return
  }

  // Update wave - NO CAP, infinite progression
  const newWave = Math.floor(gameTime.value / WAVE_DURATION) + 1
  if (newWave !== currentWave.value) {
    currentWave.value = newWave
    // Restart spawning with new wave interval
    startEnemySpawning()
    console.log(`Wave ${currentWave.value} started!`)
  }

  // Update player
  updatePlayer()

  // Update enemies
  updateEnemies()

  // Update projectiles
  updateProjectiles()

  // Update enemy projectiles
  updateEnemyProjectiles()

  // Update gems
  updateGems()

  // Update gold coins
  updateGoldCoins()

  // Fire weapons
  fireWeapons()

  // Check collisions
  checkCollisions()

  // Draw everything
  draw()

  // Check if player is dead
  if (player.value.health <= 0) {
    endGame(false)
  }
}

// Update player
function updatePlayer() {
  let dx = 0
  let dy = 0

  if (keys.value.w || keys.value.ArrowUp) dy -= 1
  if (keys.value.s || keys.value.ArrowDown) dy += 1
  if (keys.value.a || keys.value.ArrowLeft) dx -= 1
  if (keys.value.d || keys.value.ArrowRight) dx += 1

  // Normalize diagonal movement
  if (dx !== 0 && dy !== 0) {
    dx *= 0.707
    dy *= 0.707
  }

  player.value.moving = dx !== 0 || dy !== 0

  if (player.value.moving) {
    player.value.x += dx * player.value.speed
    player.value.y += dy * player.value.speed

    // Clamp to canvas
    player.value.x = Math.max(player.value.width / 2, Math.min(CANVAS_WIDTH - player.value.width / 2, player.value.x))
    player.value.y = Math.max(player.value.height / 2, Math.min(CANVAS_HEIGHT - player.value.height / 2, player.value.y))

    // Set direction
    if (dy < 0) player.value.direction = 'up'
    else if (dy > 0) player.value.direction = 'down'
    else if (dx < 0) player.value.direction = 'left'
    else if (dx > 0) player.value.direction = 'right'

    // Animate
    player.value.frameTimer++
    if (player.value.frameTimer > 10) {
      player.value.currentFrame = (player.value.currentFrame + 1) % 4
      player.value.frameTimer = 0
    }
  } else {
    player.value.currentFrame = 0
  }
}

// Start enemy spawning with dynamic interval based on wave
function startEnemySpawning() {
  if (enemySpawnId) {
    clearInterval(enemySpawnId)
  }

  // Spawn interval decreases as waves progress (faster spawning)
  const spawnInterval = Math.max(1500, BASE_ENEMY_SPAWN_INTERVAL - (currentWave.value - 1) * 500)

  enemySpawnId = setInterval(spawnEnemyWave, spawnInterval)
}

// Spawn enemy wave
function spawnEnemyWave() {
  if (!gameActive.value || gamePaused.value || gameOver.value) return

  // Fewer enemies per spawn, but more frequent spawning
  const enemyCount = 1 + Math.floor(currentWave.value / 2) // Wave 1: 1, Wave 2: 1, Wave 3: 2, etc.

  for (let i = 0; i < enemyCount; i++) {
    spawnEnemy()
  }
}

// Spawn single enemy
function spawnEnemy() {
  // Spawn off screen
  const side = Math.floor(Math.random() * 4)
  let x, y

  switch (side) {
    case 0: // Top
      x = Math.random() * CANVAS_WIDTH
      y = -50
      break
    case 1: // Right
      x = CANVAS_WIDTH + 50
      y = Math.random() * CANVAS_HEIGHT
      break
    case 2: // Bottom
      x = Math.random() * CANVAS_WIDTH
      y = CANVAS_HEIGHT + 50
      break
    case 3: // Left
      x = -50
      y = Math.random() * CANVAS_HEIGHT
      break
  }

  // Randomly spawn either ground or flying monster (50% chance for flying from wave 2+)
  const spawnFlying = currentWave.value >= 2 && Math.random() < 0.5

  if (spawnFlying) {
    // Spawn flying monster
    enemies.value.push({
      id: nextEnemyId++,
      type: 'flying',
      x,
      y,
      width: 96,  // Display size (1.5x the sprite size)
      height: 96,
      health: 3 + Math.floor(currentWave.value / 2), // Slightly more health than ground
      maxHealth: 3 + Math.floor(currentWave.value / 2),
      speed: 1.0 + currentWave.value * 0.1,
      damage: 8 + currentWave.value * 2, // More damage
      currentFrame: 0,
      frameTimer: 0,
      attackCooldown: 0,
      attackRange: 400, // Stop 400px away from player
      state: 'flying', // flying, attacking, hurt, dying, dead
      stateTimer: 0,
      animationComplete: false,
      projectileTimer: 0,
      fadeOpacity: 1.0,
      facingLeft: true // Flying monster sprite faces left by default
    })
  } else {
    // Spawn ground (punch) monster
    enemies.value.push({
      id: nextEnemyId++,
      type: 'ground',
      x,
      y,
      width: 96,  // Display size (4x the sprite size for visibility)
      height: 96,
      health: 2 + Math.floor(currentWave.value / 2), // 2-3 hits to kill
      maxHealth: 2 + Math.floor(currentWave.value / 2),
      speed: 0.8 + currentWave.value * 0.1,
      damage: 5 + currentWave.value * 2,
      currentFrame: 0,
      frameTimer: 0,
      attackCooldown: 0,
      dying: false,
      fadeOpacity: 1.0
    })
  }
}


// Update enemies
function updateEnemies() {
  for (let i = enemies.value.length - 1; i >= 0; i--) {
    const enemy = enemies.value[i]

    if (enemy.type === 'flying') {
      updateFlyingEnemy(enemy, i)
    } else {
      // Default to ground enemy behavior
      updateGroundEnemy(enemy, i)
    }
  }
}

// Update ground (punch) enemy
function updateGroundEnemy(enemy, index) {
  if (enemy.dying) {
    // Fade out death animation
    enemy.fadeOpacity -= 0.05
    if (enemy.fadeOpacity <= 0) {
      // Remove enemy and drop gem
      dropGem(enemy.x, enemy.y)

      // Chance to drop gold
      if (Math.random() < GOLD_DROP_CHANCE) {
        dropGold(enemy.x, enemy.y)
      }

      enemies.value.splice(index, 1)
      enemiesKilled.value++
    }
    return
  }

  // Move towards player
  const dx = player.value.x - enemy.x
  const dy = player.value.y - enemy.y
  const dist = Math.sqrt(dx * dx + dy * dy)

  if (dist > 0) {
    enemy.x += (dx / dist) * enemy.speed
    enemy.y += (dy / dist) * enemy.speed
  }

  // Animate (4 frames in row 0 for movement)
  enemy.frameTimer++
  if (enemy.frameTimer > 10) {
    enemy.currentFrame = (enemy.currentFrame + 1) % 4
    enemy.frameTimer = 0
  }

  // Attack player on touch
  if (enemy.attackCooldown > 0) {
    enemy.attackCooldown--
  } else {
    const playerDist = Math.sqrt(
      Math.pow(player.value.x - enemy.x, 2) +
      Math.pow(player.value.y - enemy.y, 2)
    )
    if (playerDist < 40) {
      player.value.health -= enemy.damage
      enemy.attackCooldown = 60 // 1 second cooldown
    }
  }
}

// Update flying enemy with state machine
function updateFlyingEnemy(enemy, index) {
  const dx = player.value.x - enemy.x
  const dy = player.value.y - enemy.y
  const dist = Math.sqrt(dx * dx + dy * dy)

  // State machine
  switch (enemy.state) {
    case 'flying':
      // Move towards player until in attack range
      if (dist > enemy.attackRange) {
        enemy.x += (dx / dist) * enemy.speed
        enemy.y += (dy / dist) * enemy.speed

        // Update facing direction based on movement
        // Sprite faces left by default, so flip when moving right
        enemy.facingLeft = dx < 0

        // Animate flying (4 frames, cycle continuously)
        enemy.frameTimer++
        if (enemy.frameTimer > 10) {
          enemy.currentFrame = (enemy.currentFrame + 1) % 4
          enemy.frameTimer = 0
        }
      } else {
        // In range, switch to attacking
        if (enemy.attackCooldown <= 0) {
          enemy.state = 'attacking'
          enemy.currentFrame = 0
          enemy.frameTimer = 0
          enemy.animationComplete = false
        }
      }
      break

    case 'attacking':
      // Stay in position and play attack animation
      enemy.frameTimer++
      if (enemy.frameTimer > 6) {
        enemy.currentFrame++
        enemy.frameTimer = 0

        // Shoot projectile at frame 4
        if (enemy.currentFrame === 4) {
          shootEnemyProjectile(enemy)
        }

        if (enemy.currentFrame >= 8) {
          // Attack animation complete, return to flying
          enemy.state = 'flying'
          enemy.currentFrame = 0
          enemy.frameTimer = 0
          enemy.attackCooldown = 120 // 2 second cooldown before next attack
        }
      }
      break

    case 'hurt':
      // Play hurt animation (4 frames once)
      enemy.frameTimer++
      if (enemy.frameTimer > 8) {
        enemy.currentFrame++
        enemy.frameTimer = 0

        if (enemy.currentFrame >= 4) {
          // Hurt animation complete
          if (enemy.health <= 0) {
            enemy.state = 'dying'
            enemy.currentFrame = 0
            enemy.frameTimer = 0
          } else {
            enemy.state = 'flying'
            enemy.currentFrame = 0
            enemy.frameTimer = 0
          }
        }
      }
      break

    case 'dying':
      // Play death animation (7 frames once)
      enemy.frameTimer++
      if (enemy.frameTimer > 8) {
        enemy.currentFrame++
        enemy.frameTimer = 0

        if (enemy.currentFrame >= 7) {
          // Death animation complete
          enemy.state = 'dead'
          enemy.currentFrame = 6 // Keep last frame
        }
      }
      break

    case 'dead':
      // Fade out
      enemy.fadeOpacity -= 0.05
      if (enemy.fadeOpacity <= 0) {
        // Remove enemy and drop gem
        dropGem(enemy.x, enemy.y)

        // Chance to drop gold
        if (Math.random() < GOLD_DROP_CHANCE) {
          dropGold(enemy.x, enemy.y)
        }

        enemies.value.splice(index, 1)
        enemiesKilled.value++
      }
      break
  }

  // Decrement attack cooldown
  if (enemy.attackCooldown > 0) {
    enemy.attackCooldown--
  }
}

// Shoot enemy projectile
function shootEnemyProjectile(enemy) {
  const dx = player.value.x - enemy.x
  const dy = player.value.y - enemy.y
  const dist = Math.sqrt(dx * dx + dy * dy)

  if (dist > 0) {
    enemyProjectiles.value.push({
      x: enemy.x,
      y: enemy.y,
      vx: (dx / dist) * 4, // Projectile speed
      vy: (dy / dist) * 4,
      damage: enemy.damage,
      rotation: Math.atan2(dy, dx)
    })
  }
}

// Fire weapons
function fireWeapons() {
  const currentTime = Date.now()

  for (const weapon of player.value.weapons) {
    if (currentTime - weapon.lastFired > weapon.fireRate) {
      // Find nearest enemy
      let nearestEnemy = null
      let nearestDist = Infinity

      for (const enemy of enemies.value) {
        if (enemy.dying) continue
        const dist = Math.sqrt(
          Math.pow(player.value.x - enemy.x, 2) +
          Math.pow(player.value.y - enemy.y, 2)
        )
        if (dist < nearestDist) {
          nearestDist = dist
          nearestEnemy = enemy
        }
      }

      // Fire at nearest enemy
      if (nearestEnemy && nearestDist < weapon.range) {
        const dx = nearestEnemy.x - player.value.x
        const dy = nearestEnemy.y - player.value.y
        const dist = Math.sqrt(dx * dx + dy * dy)

        projectiles.value.push({
          x: player.value.x,
          y: player.value.y,
          vx: (dx / dist) * weapon.projectileSpeed,
          vy: (dy / dist) * weapon.projectileSpeed,
          damage: weapon.damage,
          rotation: Math.atan2(dy, dx)
        })

        weapon.lastFired = currentTime
      }
    }
  }
}

// Update projectiles
function updateProjectiles() {
  for (let i = projectiles.value.length - 1; i >= 0; i--) {
    const proj = projectiles.value[i]
    proj.x += proj.vx
    proj.y += proj.vy
    proj.rotation += 0.2

    // Remove if off screen
    if (proj.x < -50 || proj.x > CANVAS_WIDTH + 50 ||
        proj.y < -50 || proj.y > CANVAS_HEIGHT + 50) {
      projectiles.value.splice(i, 1)
    }
  }
}

// Check collisions
function checkCollisions() {
  // Projectile vs enemy
  for (let i = projectiles.value.length - 1; i >= 0; i--) {
    const proj = projectiles.value[i]

    for (const enemy of enemies.value) {
      if (enemy.dying) continue

      const dist = Math.sqrt(
        Math.pow(proj.x - enemy.x, 2) +
        Math.pow(proj.y - enemy.y, 2)
      )

      if (dist < 30) {
        enemy.health -= proj.damage
        projectiles.value.splice(i, 1)

        if (enemy.type === 'flying') {
          // Flying enemies go to hurt state
          if (enemy.state !== 'hurt' && enemy.state !== 'dying' && enemy.state !== 'dead') {
            enemy.state = 'hurt'
            enemy.currentFrame = 0
            enemy.frameTimer = 0
          }
        } else {
          // Ground enemies use dying flag
          if (enemy.health <= 0) {
            enemy.dying = true
            enemy.deathFrame = 0
            enemy.deathTimer = 0
          }
        }
        break
      }
    }
  }
}

// Update enemy projectiles
function updateEnemyProjectiles() {
  for (let i = enemyProjectiles.value.length - 1; i >= 0; i--) {
    const proj = enemyProjectiles.value[i]

    proj.x += proj.vx
    proj.y += proj.vy

    // Remove if off screen
    if (proj.x < -50 || proj.x > CANVAS_WIDTH + 50 ||
        proj.y < -50 || proj.y > CANVAS_HEIGHT + 50) {
      enemyProjectiles.value.splice(i, 1)
      continue
    }

    // Check collision with player
    const dist = Math.sqrt(
      Math.pow(proj.x - player.value.x, 2) +
      Math.pow(proj.y - player.value.y, 2)
    )

    if (dist < 30) {
      player.value.health -= proj.damage
      enemyProjectiles.value.splice(i, 1)
    }
  }
}

// Drop gem
function dropGem(x, y) {
  gems.value.push({
    x,
    y,
    expValue: 1,
    rotation: 0,
    collected: false
  })
}

// Drop gold
function dropGold(x, y) {
  const goldValue = Math.floor(Math.random() * 5) + 1 // 1-5 gold coins

  // Drop multiple individual coins (each worth 1 gold)
  for (let i = 0; i < goldValue; i++) {
    // Scatter coins slightly around the drop point
    const offsetX = (Math.random() - 0.5) * 30
    const offsetY = (Math.random() - 0.5) * 30

    goldCoins.value.push({
      x: x + offsetX,
      y: y + offsetY,
      value: 1, // Each coin is worth 1 gold
      collected: false,
      currentFrame: Math.floor(Math.random() * 6), // Random starting frame for variety
      frameTimer: 0
    })
  }
}

// Update gems
function updateGems() {
  for (let i = gems.value.length - 1; i >= 0; i--) {
    const gem = gems.value[i]

    // Rotate gem
    gem.rotation += 0.05

    // Check if player picks up gem
    const dist = Math.sqrt(
      Math.pow(player.value.x - gem.x, 2) +
      Math.pow(player.value.y - gem.y, 2)
    )

    if (dist < 40 && !gem.collected) {
      gem.collected = true
      player.value.exp += gem.expValue

      // Level up
      if (player.value.exp >= player.value.nextLevelExp) {
        levelUp()
      }

      gems.value.splice(i, 1)
    } else if (dist < 150) {
      // Attract towards player
      const dx = player.value.x - gem.x
      const dy = player.value.y - gem.y
      gem.x += dx * 0.05
      gem.y += dy * 0.05
    }
  }
}

// Update gold coins
function updateGoldCoins() {
  for (let i = goldCoins.value.length - 1; i >= 0; i--) {
    const gold = goldCoins.value[i]

    // Animate gold coin frames (6 frames total, cycle through them)
    gold.frameTimer++
    if (gold.frameTimer > 8) {  // Change frame every ~8 game ticks (similar to AnimatedCoin fps: 8)
      gold.currentFrame = (gold.currentFrame + 1) % 6
      gold.frameTimer = 0
    }

    // Check if player picks up gold
    const dist = Math.sqrt(
      Math.pow(player.value.x - gold.x, 2) +
      Math.pow(player.value.y - gold.y, 2)
    )

    if (dist < 40 && !gold.collected) {
      gold.collected = true

      // Add coins to player's account
      const newCoinAmount = (coins.value || 0) + gold.value
      updateCoins(newCoinAmount)

      // Track coins earned this session
      coinsEarned.value += gold.value

      goldCoins.value.splice(i, 1)
    } else if (dist < 150) {
      // Attract towards player
      const dx = player.value.x - gold.x
      const dy = player.value.y - gold.y
      gold.x += dx * 0.05
      gold.y += dy * 0.05
    }
  }
}

// Level up
function levelUp() {
  player.value.level++
  player.value.exp = 0
  player.value.nextLevelExp = Math.floor(player.value.nextLevelExp * 1.5)

  // Pause game and show level up options
  gamePaused.value = true
  showLevelUp.value = true

  // Generate level up options (placeholder for now)
  levelUpOptions.value = [
    { name: 'Increase Attack Speed', description: 'Fire weapons 30% faster' },
    { name: 'Increase Damage', description: 'Deal 1 more damage' },
    { name: 'Heal', description: 'Restore 30 health' }
  ]
}

// Select level up option
function selectLevelUpOption(option) {
  if (option.name === 'Increase Attack Speed') {
    for (const weapon of player.value.weapons) {
      weapon.fireRate *= 1.3
    }
  } else if (option.name === 'Increase Damage') {
    for (const weapon of player.value.weapons) {
      weapon.damage += 1
    }
  } else if (option.name === 'Heal') {
    player.value.health = Math.min(player.value.maxHealth, player.value.health + 30)
  }

  showLevelUp.value = false
  gamePaused.value = false
}

// End game
async function endGame(won, reason = 'death') {
  gameActive.value = false
  gameOver.value = true
  gameWon.value = won

  if (gameLoopId) {
    clearInterval(gameLoopId)
    gameLoopId = null
  }

  if (enemySpawnId) {
    clearInterval(enemySpawnId)
    enemySpawnId = null
  }

  // Save progress to backend (whether died or time limit reached)
  const progressData = {
    wave: currentWave.value,
    level: player.value.level,
    weapons: player.value.weapons.map(w => ({
      type: w.type,
      damage: w.damage,
      fireRate: w.fireRate,
      projectileSpeed: w.projectileSpeed,
      range: w.range
    })),
    maxHealth: player.value.maxHealth,
    speed: player.value.speed
  }

  // Calculate total time played today (existing + this session)
  const savedProgress = await loadProgress()
  const existingTimeToday = savedProgress?.time_played_today || 0
  const todayCheck = savedProgress?.last_played ? new Date(savedProgress.last_played).toDateString() : null
  const isToday = todayCheck === new Date().toDateString()

  // If last played was today, add to existing time; otherwise, reset to just this session
  const totalTimePlayedToday = isToday ? existingTimeToday + totalTimePlayed.value : totalTimePlayed.value

  console.log(`Game ended (${reason}). Saving progress:`, progressData)
  console.log(`Time played this session: ${totalTimePlayed.value}ms, Total today: ${totalTimePlayedToday}ms`)

  // Pass died_today flag if player died
  const playerDied = reason === 'death'
  const saveResult = await saveProgress(progressData, totalTimePlayedToday, playerDied)

  // Verify the save was successful (especially important for death state)
  if (saveResult && saveResult.success) {
    console.log('Progress saved successfully')
  } else {
    console.error('Failed to save progress:', saveResult?.error)
  }

  // IMPORTANT: If player died, verify the death state was saved by reloading
  if (playerDied) {
    console.log('Player died - verifying death state was saved...')
    const verifyProgress = await loadProgress()
    console.log('Verified saved progress:', verifyProgress)

    if (verifyProgress && verifyProgress.died_today) {
      console.log('✓ Death state confirmed saved in backend')
      diedToday.value = true
    } else {
      console.error('✗ Death state NOT saved in backend! Retrying...')
      // Retry save once more
      await saveProgress(progressData, totalTimePlayedToday, true)
      diedToday.value = true
    }

    remainingTimeToday.value = Math.max(0, remainingTimeToday.value - totalTimePlayed.value)
  } else if (reason === 'timeLimit') {
    remainingTimeToday.value = 0
  } else {
    // Other reasons (if any)
    remainingTimeToday.value = Math.max(0, remainingTimeToday.value - totalTimePlayed.value)
  }

  console.log(`Remaining play time today: ${Math.floor(remainingTimeToday.value / 1000)}s`)
  console.log(`Died today: ${diedToday.value}`)
}

// Restart game
function restartGame() {
  showStartButton.value = true
  gameOver.value = false
  gameWon.value = false
}

// Draw flying enemy
function drawFlyingEnemy(enemy, drawX, drawY) {
  let spriteImage = null
  let maxFrames = 0
  let spriteWidth = 0
  let spriteHeight = 0

  // Select sprite based on state and set max frames and dimensions
  switch (enemy.state) {
    case 'flying':
      spriteImage = images.value.flyingMonsterFlying
      maxFrames = 4
      // If image is 64x64 overall with 4 frames left-to-right: each frame is 16x64
      spriteWidth = spriteImage ? spriteImage.width / maxFrames : 16
      spriteHeight = spriteImage ? spriteImage.height : 64
      break
    case 'attacking':
      spriteImage = images.value.flyingMonsterAttack
      maxFrames = 8
      spriteWidth = spriteImage ? spriteImage.width / maxFrames : 8
      spriteHeight = spriteImage ? spriteImage.height : 64
      break
    case 'hurt':
      spriteImage = images.value.flyingMonsterHurt
      maxFrames = 4
      spriteWidth = spriteImage ? spriteImage.width / maxFrames : 16
      spriteHeight = spriteImage ? spriteImage.height : 64
      break
    case 'dying':
    case 'dead':
      spriteImage = images.value.flyingMonsterDeath
      maxFrames = 7
      spriteWidth = spriteImage ? spriteImage.width / maxFrames : 9
      spriteHeight = spriteImage ? spriteImage.height : 64
      break
  }

  if (spriteImage) {
    // Clamp frame to valid range for current animation
    const frame = Math.min(Math.max(0, Math.floor(enemy.currentFrame)), maxFrames - 1)

    // Save context for transformations
    ctx.value.save()

    // Apply fade opacity if dead
    if (enemy.state === 'dead') {
      ctx.value.globalAlpha = enemy.fadeOpacity
    }

    // Translate to enemy center
    ctx.value.translate(enemy.x, enemy.y)

    // Flip horizontally if not facing left (sprite default is facing left)
    if (!enemy.facingLeft) {
      ctx.value.scale(-1, 1)
    }

    // Draw sprite centered at origin (horizontal sprite sheet)
    // Extract the specific frame from the sprite sheet
    ctx.value.drawImage(
      spriteImage,
      frame * spriteWidth, 0, spriteWidth, spriteHeight,  // Source: extract one frame
      -enemy.width / 2, -enemy.height / 2, enemy.width, enemy.height  // Dest: centered
    )

    // Restore context
    ctx.value.restore()

    // Health bar (drawn without transformations)
    if (enemy.state !== 'dying' && enemy.state !== 'dead' && enemy.health < enemy.maxHealth) {
      const barWidth = 70
      const barHeight = 6
      const healthPercent = enemy.health / enemy.maxHealth

      ctx.value.fillStyle = '#000000'
      ctx.value.fillRect(enemy.x - barWidth / 2 - 1, drawY - 12, barWidth + 2, barHeight + 2)
      ctx.value.fillStyle = '#ff0000'
      ctx.value.fillRect(enemy.x - barWidth / 2, drawY - 11, barWidth, barHeight)
      ctx.value.fillStyle = '#00ff00'
      ctx.value.fillRect(enemy.x - barWidth / 2, drawY - 11, barWidth * healthPercent, barHeight)
    }
  } else {
    // Placeholder if sprite not loaded
    ctx.value.fillStyle = '#800080'
    ctx.value.fillRect(drawX, drawY, enemy.width, enemy.height)
    ctx.value.fillStyle = '#ffffff'
    ctx.value.font = '12px monospace'
    ctx.value.fillText('F', enemy.x - 5, enemy.y + 5)
  }
}

// Draw everything
function draw() {
  if (!ctx.value) return

  // Clear canvas
  ctx.value.fillStyle = '#2a1810'
  ctx.value.fillRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT)

  // Draw grid pattern
  ctx.value.strokeStyle = '#3a2820'
  ctx.value.lineWidth = 1
  for (let x = 0; x < CANVAS_WIDTH; x += 40) {
    ctx.value.beginPath()
    ctx.value.moveTo(x, 0)
    ctx.value.lineTo(x, CANVAS_HEIGHT)
    ctx.value.stroke()
  }
  for (let y = 0; y < CANVAS_HEIGHT; y += 40) {
    ctx.value.beginPath()
    ctx.value.moveTo(0, y)
    ctx.value.lineTo(CANVAS_WIDTH, y)
    ctx.value.stroke()
  }

  // Draw gold coins
  for (const gold of goldCoins.value) {
    if (images.value.goldCoin) {
      // 01PixelCoinGold.png sprite sheet info:
      // 16x16 pixel sprites, 6 frames total
      // First row has 4 frames (0-3), second row has 2 frames (4-5)
      const coinSpriteSize = 16
      const frame = gold.currentFrame
      let sx, sy

      // Calculate source position based on frame
      if (frame < 4) {
        // First row (frames 0-3)
        sx = frame * coinSpriteSize
        sy = 0
      } else {
        // Second row (frames 4-5)
        sx = (frame - 4) * coinSpriteSize
        sy = coinSpriteSize
      }

      // Draw the animated coin at original size (16px)
      const coinDisplaySize = 16
      ctx.value.drawImage(
        images.value.goldCoin,
        sx, sy, coinSpriteSize, coinSpriteSize,
        gold.x - coinDisplaySize / 2,
        gold.y - coinDisplaySize / 2,
        coinDisplaySize,
        coinDisplaySize
      )
    }
  }

  // Draw gems
  for (const gem of gems.value) {
    if (images.value.greenGem) {
      ctx.value.save()
      ctx.value.translate(gem.x, gem.y)
      ctx.value.rotate(gem.rotation)
      // Assume gem sprite is 16x16, use first frame
      ctx.value.drawImage(
        images.value.greenGem,
        0, 0, 16, 16,
        -16, -16, 32, 32
      )
      ctx.value.restore()
    }
  }

  // Draw projectiles
  for (const proj of projectiles.value) {
    if (images.value.shuriken) {
      ctx.value.save()
      ctx.value.translate(proj.x, proj.y)
      ctx.value.rotate(proj.rotation)
      // Assume shuriken sprite is 16x16
      ctx.value.drawImage(
        images.value.shuriken,
        0, 0, 16, 16,
        -12, -12, 24, 24
      )
      ctx.value.restore()
    }
  }

  // Draw enemy projectiles
  for (const proj of enemyProjectiles.value) {
    if (images.value.enemyProjectile) {
      ctx.value.save()
      ctx.value.translate(proj.x, proj.y)
      // Rotate 180 degrees (PI radians) more to flip the fireball
      ctx.value.rotate(proj.rotation + Math.PI)
      // Draw enemy projectile (get actual sprite dimensions)
      const projWidth = images.value.enemyProjectile.width
      const projHeight = images.value.enemyProjectile.height
      ctx.value.drawImage(
        images.value.enemyProjectile,
        0, 0, projWidth, projHeight,  // Source rectangle
        -12, -12, 24, 24  // Destination rectangle
      )
      ctx.value.restore()
    } else {
      // Fallback: draw red circle
      ctx.value.fillStyle = '#ff0000'
      ctx.value.beginPath()
      ctx.value.arc(proj.x, proj.y, 8, 0, Math.PI * 2)
      ctx.value.fill()
    }
  }

  // Draw enemies
  for (const enemy of enemies.value) {
    const drawX = enemy.x - enemy.width / 2
    const drawY = enemy.y - enemy.height / 2

    if (enemy.type === 'flying') {
      // Draw flying monster
      drawFlyingEnemy(enemy, drawX, drawY)
    } else {
      // Draw ground (punch) monster
      if (images.value.monster) {
        // PunchMonster sprite sheet info:
        // Total: 96x24 pixels (4 frames x 1 row)
        // Each frame is 24x24 pixels
        // Row 0: Movement animation (4 frames)
        const spriteWidth = 24
        const spriteHeight = 24
        const movementRow = 0

        const frame = enemy.currentFrame % 4

        // Apply fade opacity if dying
        if (enemy.dying) {
          ctx.value.globalAlpha = enemy.fadeOpacity
        }

        ctx.value.drawImage(
          images.value.monster,
          frame * spriteWidth, movementRow * spriteHeight, spriteWidth, spriteHeight,
          drawX, drawY, enemy.width, enemy.height
        )

        // Reset opacity
        if (enemy.dying) {
          ctx.value.globalAlpha = 1.0
        }

        // Health bar
        if (!enemy.dying && enemy.health < enemy.maxHealth) {
          const barWidth = 70
          const barHeight = 6
          const healthPercent = enemy.health / enemy.maxHealth

          ctx.value.fillStyle = '#000000'
          ctx.value.fillRect(enemy.x - barWidth / 2 - 1, drawY - 12, barWidth + 2, barHeight + 2)
          ctx.value.fillStyle = '#ff0000'
          ctx.value.fillRect(enemy.x - barWidth / 2, drawY - 11, barWidth, barHeight)
          ctx.value.fillStyle = '#00ff00'
          ctx.value.fillRect(enemy.x - barWidth / 2, drawY - 11, barWidth * healthPercent, barHeight)
        }
      } else {
        // Draw placeholder if image not loaded yet
        ctx.value.fillStyle = '#ff0000'
        ctx.value.fillRect(drawX, drawY, enemy.width, enemy.height)
        ctx.value.fillStyle = '#ffffff'
        ctx.value.font = '12px monospace'
        ctx.value.fillText('E', enemy.x - 5, enemy.y + 5)
      }
    }
  }

  // Draw player
  if (images.value.petSprite) {
    const rowMap = {
      down: 0,
      right: 1,
      up: 2,
      left: 3
    }
    const row = rowMap[player.value.direction] || 0
    const frame = player.value.currentFrame

    ctx.value.drawImage(
      images.value.petSprite,
      frame * props.petSlice, row * props.petSlice, props.petSlice, props.petSlice,
      player.value.x - player.value.width / 2, player.value.y - player.value.height / 2,
      player.value.width, player.value.height
    )
  }

  // Draw UI
  drawUI()
}

// Draw UI
function drawUI() {
  // Health bar
  const healthBarWidth = 200
  const healthBarHeight = 20
  const healthPercent = player.value.health / player.value.maxHealth

  ctx.value.fillStyle = '#000000'
  ctx.value.fillRect(10, 10, healthBarWidth + 4, healthBarHeight + 4)
  ctx.value.fillStyle = '#ff0000'
  ctx.value.fillRect(12, 12, healthBarWidth, healthBarHeight)
  ctx.value.fillStyle = '#00ff00'
  ctx.value.fillRect(12, 12, healthBarWidth * healthPercent, healthBarHeight)

  ctx.value.fillStyle = '#ffffff'
  ctx.value.font = 'bold 12px monospace'
  ctx.value.fillText(`${Math.floor(player.value.health)}/${player.value.maxHealth}`, 15, 26)

  // Experience bar
  const expPercent = player.value.exp / player.value.nextLevelExp
  ctx.value.fillStyle = '#000000'
  ctx.value.fillRect(10, 40, healthBarWidth + 4, 14)
  ctx.value.fillStyle = '#4444ff'
  ctx.value.fillRect(12, 42, healthBarWidth * expPercent, 10)

  // Level
  ctx.value.fillStyle = '#ffffff'
  ctx.value.font = 'bold 14px monospace'
  ctx.value.fillText(`Level ${player.value.level}`, 220, 26)

  // Wave
  ctx.value.fillText(`Wave ${currentWave.value}`, 220, 50)

  // Timer
  const minutes = Math.floor(gameTime.value / 60000)
  const seconds = Math.floor((gameTime.value % 60000) / 1000)
  ctx.value.fillText(`${minutes}:${seconds.toString().padStart(2, '0')}`, CANVAS_WIDTH - 80, 26)

  // Kills
  ctx.value.fillText(`Kills: ${enemiesKilled.value}`, CANVAS_WIDTH - 120, 50)
}

// Keyboard events
function handleKeyDown(e) {
  const key = e.key.toLowerCase()
  if (key in keys.value || e.key in keys.value) {
    keys.value[key] = true
    keys.value[e.key] = true
    e.preventDefault()
  }
}

function handleKeyUp(e) {
  const key = e.key.toLowerCase()
  if (key in keys.value || e.key in keys.value) {
    keys.value[key] = false
    keys.value[e.key] = false
    e.preventDefault()
  }
}

onMounted(() => {
  window.addEventListener('keydown', handleKeyDown)
  window.addEventListener('keyup', handleKeyUp)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeyDown)
  window.removeEventListener('keyup', handleKeyUp)

  if (gameLoopId) {
    clearInterval(gameLoopId)
  }
  if (enemySpawnId) {
    clearInterval(enemySpawnId)
  }
})

// Format time
function formatTime(ms) {
  const minutes = Math.floor(ms / 60000)
  const seconds = Math.floor((ms % 60000) / 1000)
  return `${minutes}:${seconds.toString().padStart(2, '0')}`
}
</script>

<template>
  <div class="minigame-container">
    <!-- Start screen -->
    <div v-if="showStartButton" class="start-screen">
      <h2>Pet Survival Challenge</h2>
      <p>Survive endless waves of enemies! Your progress is saved.</p>
      <p class="controls-hint">Use WASD or Arrow Keys to move</p>
      <p class="controls-hint">Your pet will automatically attack nearby enemies</p>
      <p class="controls-hint">2.5 minutes of play time per day - Continue from where you left off!</p>

      <!-- Loading death state -->
      <div v-if="deathStateLoading" class="loading-state">
        <p>⏳ Checking game status...</p>
      </div>

      <!-- Show death message if player died today -->
      <div v-else-if="diedToday" class="daily-restriction death-restriction">
        <p class="warning">💀 You died today!</p>
        <p>Come back tomorrow to try again</p>
        <button class="reset-button" @click="resetDeathState">
          Reset Death State (Testing)
        </button>
      </div>

      <!-- Show time limit message if time ran out -->
      <div v-else-if="!canPlayToday" class="daily-restriction">
        <p class="warning">⏱️ You've used your 2.5 minutes today!</p>
        <p>Come back tomorrow to continue your adventure</p>
        <button class="reset-button" @click="resetDailyTimer">
          Reset Timer (Testing)
        </button>
      </div>

      <!-- Show remaining time if player can play -->
      <div v-else class="remaining-time-display">
        <p>⏱️ Remaining play time today: {{ Math.floor(remainingTimeToday / 1000) }}s</p>
      </div>

      <button
        class="start-button"
        @click="startGame"
        :disabled="deathStateLoading || !canPlayToday"
      >
        <template v-if="deathStateLoading">⏳ Loading...</template>
        <template v-else-if="diedToday">💀 Died Today - Try Tomorrow</template>
        <template v-else-if="!canPlayToday">⏱️ Time's Up - Try Tomorrow</template>
        <template v-else>Start Game</template>
      </button>
    </div>

    <!-- Game canvas -->
    <div v-show="!showStartButton && !gameOver" class="game-canvas-container">
      <canvas
        ref="canvas"
        :width="CANVAS_WIDTH"
        :height="CANVAS_HEIGHT"
        class="game-canvas"
      />
    </div>

    <!-- Level up screen -->
    <div v-if="showLevelUp" class="level-up-screen">
      <h2>Level Up!</h2>
      <p>Choose an upgrade:</p>
      <div class="level-up-options">
        <button
          v-for="(option, index) in levelUpOptions"
          :key="index"
          class="level-up-option"
          @click="selectLevelUpOption(option)"
        >
          <div class="option-name">{{ option.name }}</div>
          <div class="option-description">{{ option.description }}</div>
        </button>
      </div>
    </div>

    <!-- Game over screen -->
    <div v-if="gameOver" class="game-over-screen">
      <h2 v-if="gameWon" class="victory">Victory!</h2>
      <h2 v-else class="defeat">Game Over</h2>

      <div class="stats">
        <p><strong>Time Survived:</strong> {{ formatTime(gameTime) }}</p>
        <p><strong>Enemies Killed:</strong> {{ enemiesKilled }}</p>
        <p><strong>Level Reached:</strong> {{ player.level }}</p>
        <p><strong>Final Wave:</strong> {{ currentWave }}</p>

        <!-- Coins Earned Display -->
        <div class="coins-earned">
          <AnimatedCoin :scale="2" :speed="8" />
          <span class="coins-earned-text">
            <strong>Coins Earned:</strong> {{ coinsEarned }}
          </span>
        </div>
      </div>

      <button class="restart-button" @click="restartGame">
        Back to Menu
      </button>
    </div>
  </div>
</template>

<style scoped>
.minigame-container {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #1a1a1a;
  position: relative;
  overflow: hidden;
}

.start-screen,
.game-over-screen,
.level-up-screen {
  text-align: center;
  color: white;
  padding: 40px;
  background: rgba(0, 0, 0, 0.8);
  border-radius: 12px;
  max-width: 500px;
}

.start-screen h2,
.game-over-screen h2,
.level-up-screen h2 {
  font-size: 32px;
  margin-bottom: 20px;
}

.victory {
  color: #4ade80;
}

.defeat {
  color: #f87171;
}

.controls-hint {
  color: #9ca3af;
  font-size: 14px;
  margin: 8px 0;
}

.start-button,
.restart-button,
.reset-button {
  padding: 12px 32px;
  font-size: 18px;
  font-weight: bold;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  margin-top: 20px;
  transition: all 0.3s ease;
}

.start-button {
  background: #4ade80;
  color: white;
}

.start-button:hover:not(:disabled) {
  background: #22c55e;
  transform: translateY(-2px);
}

.start-button:disabled {
  background: #6b7280;
  cursor: not-allowed;
}

.restart-button {
  background: #3b82f6;
  color: white;
}

.restart-button:hover {
  background: #2563eb;
  transform: translateY(-2px);
}

.reset-button {
  background: #ef4444;
  color: white;
  padding: 8px 16px;
  font-size: 14px;
}

.reset-button:hover {
  background: #dc2626;
}

.daily-restriction {
  background: rgba(239, 68, 68, 0.2);
  border: 2px solid #ef4444;
  border-radius: 8px;
  padding: 16px;
  margin: 20px 0;
}

.death-restriction {
  background: rgba(139, 92, 246, 0.2);
  border: 2px solid #8b5cf6;
}

.death-restriction .warning {
  color: #c4b5fd;
}

.warning {
  color: #fca5a5;
  font-weight: bold;
  font-size: 18px;
  margin-bottom: 8px;
}

.remaining-time-display {
  background: rgba(74, 222, 128, 0.2);
  border: 2px solid #4ade80;
  border-radius: 8px;
  padding: 16px;
  margin: 20px 0;
}

.remaining-time-display p {
  color: #86efac;
  font-weight: bold;
  font-size: 16px;
  margin: 0;
}

.loading-state {
  background: rgba(59, 130, 246, 0.2);
  border: 2px solid #3b82f6;
  border-radius: 8px;
  padding: 16px;
  margin: 20px 0;
  text-align: center;
}

.loading-state p {
  color: #93c5fd;
  font-weight: bold;
  font-size: 16px;
  margin: 0;
  animation: pulse 1.5s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

.game-canvas-container {
  position: relative;
}

.game-canvas {
  border: 4px solid #3b82f6;
  border-radius: 8px;
  image-rendering: pixelated;
  image-rendering: crisp-edges;
}

.stats {
  margin: 20px 0;
  text-align: left;
}

.coins-earned {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  margin-top: 16px;
  padding: 16px;
  background: linear-gradient(135deg, rgba(255, 215, 0, 0.2), rgba(255, 215, 0, 0.1));
  border: 2px solid rgba(255, 215, 0, 0.5);
  border-radius: 12px;
}

.coins-earned-text {
  font-size: 18px;
  color: #FFD700;
  text-shadow: 0 0 10px rgba(255, 215, 0, 0.5);
}

.stats p {
  margin: 8px 0;
  font-size: 16px;
}

.level-up-screen {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  z-index: 1000;
  border: 4px solid #fbbf24;
}

.level-up-options {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 20px;
}

.level-up-option {
  padding: 16px;
  background: #374151;
  border: 2px solid #6b7280;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  text-align: left;
}

.level-up-option:hover {
  background: #4b5563;
  border-color: #fbbf24;
  transform: translateY(-2px);
}

.option-name {
  font-size: 18px;
  font-weight: bold;
  color: #fbbf24;
  margin-bottom: 8px;
}

.option-description {
  font-size: 14px;
  color: #d1d5db;
}
</style>
