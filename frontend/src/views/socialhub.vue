<script setup>
import { ref } from 'vue'

/* Tabs */
const tab = ref(0)

/* Feed */
const composer = ref('')
const feed = ref([
  { id: 1, name: 'Sarah Kim', initials: 'SK', time: '2 hours ago', tag: 'Study Streak: 18 days', text: 'Just completed a 4-hour study session! Feeling productive 💪', likes: 12, comments: 3 },
  { id: 2, name: 'Alex Chen', initials: 'AC', time: '5 hours ago', text: 'Finally finished my challenging math assignment. The Pomodoro technique really helped!', likes: 9, comments: 1 },
  { id: 3, name: 'Mike John', initials: 'MJ', time: 'Yesterday', text: 'Walked 6k steps between study blocks. Feeling refreshed.', likes: 4, comments: 0 },
])
function sharePost() {
  const msg = composer.value.trim()
  if (!msg) return
  feed.value.unshift({ id: crypto.randomUUID(), name: 'You', initials: 'Y', time: 'Just now', text: msg, likes: 0, comments: 0 })
  composer.value = ''
}

/* Friends */
const friends = ref([
  { id: 1, name: 'Alex Chen', initials: 'AC', status: 'Studying Math', online: true, level: 15, study: '12d', checkin: '8d', week: '4h' },
  { id: 2, name: 'Sarah Kim', initials: 'SK', status: 'Taking a break', online: true, level: 22, study: '18d', checkin: '15d', week: '5h' },
  { id: 3, name: 'Mike Johnson', initials: 'MJ', status: 'Offline', online: false, level: 8, study: '5d', checkin: '3d', week: '3h' },
])

/* Challenges */
const challenges = ref([
  { id: 1, title: 'Study Sprint Challenge', subtitle: 'Study for 25 hours this week', progress: 18, goal: 25, participants: 47, reward: '150 XP + Special Badge', time: '3 days' },
  { id: 2, title: 'Wellness Warrior', subtitle: 'Complete daily check-ins for 14 days straight', progress: 9, goal: 14, participants: 23, reward: '200 XP + Wellness Badge', time: '5 days' },
])

/* Leaderboard */
const leaders = ref([
  { rank: 1, name: 'Emma Wilson', initials: 'EW', level: 28, xp: 15420, medal: '🥇' },
  { rank: 2, name: 'David Lee', initials: 'DL', level: 25, xp: 14890, medal: '🥈' },
  { rank: 3, name: 'Lisa Zhang', initials: 'LZ', level: 24, xp: 14230, medal: '🥉' },
  { rank: 4, name: 'You', initials: 'Y', level: 1, xp: 0, medal: '' },
  { rank: 5, name: 'James Brown', initials: 'JB', level: 20, xp: 12100, medal: '' },
])
</script>

<template>
  <div class="social-hub-container">
    <!-- Main Content -->
    <div class="main-content">
      <!-- Header -->
      <div class="content-header">
        <h1 class="page-title">Social Hub</h1>
        <p class="page-subtitle">Connect with fellow students and stay motivated</p>
      </div>

      <!-- Tab Navigation -->
      <div class="tab-navigation">
        <div 
          class="tab-item" 
          :class="{ active: tab === 0 }"
          @click="tab = 0"
        >
          Feed
        </div>
        <div 
          class="tab-item" 
          :class="{ active: tab === 1 }"
          @click="tab = 1"
        >
          Friends
        </div>
        <div 
          class="tab-item" 
          :class="{ active: tab === 2 }"
          @click="tab = 2"
        >
          Challenges
        </div>
        <div 
          class="tab-item" 
          :class="{ active: tab === 3 }"
          @click="tab = 3"
        >
          Leaderboard
        </div>
      </div>

      <!-- Tab Content -->
      <div class="tab-content">

    <v-window v-model="tab" :transition="false" :touch="false">
      <!-- FEED -->
      <v-window-item :value="0">
        <v-card rounded="xl" class="soft-card pa-4 mb-4">
          <div class="text-subtitle-1 font-weight-medium">Share Your Progress</div>
          <div class="text-caption mb-3">Let your friends know how you're doing</div>
          <div class="d-flex ga-3">
            <v-avatar size="40" class="bg-muted text-on-muted">Y</v-avatar>
            <v-textarea
              v-model="composer"
              rows="3"
              auto-grow
              rounded="lg"
              variant="outlined"
              class="composer-area"
              placeholder="Share your achievements, struggles, or motivation..."
            />
          </div>
          <div class="d-flex justify-end mt-2">
            <v-btn class="btn-dark" @click="sharePost">
              <v-icon start>mdi-share-variant</v-icon>Share Post
            </v-btn>
          </div>
        </v-card>

        <v-card v-for="p in feed" :key="p.id" rounded="xl" class="soft-card pa-4 mb-4">
          <div class="d-flex flex-wrap ga-3 align-start">
            <v-avatar size="40" class="bg-muted text-on-muted">{{ p.initials }}</v-avatar>
            <div class="flex-1 min-w-0">
              <div class="d-flex align-center flex-wrap ga-2">
                <div class="font-weight-medium mr-auto">{{ p.name }}</div>
                <v-chip v-if="p.tag" size="small" class="chip-tonal">{{ p.tag }}</v-chip>
                <div class="text-caption text-muted">{{ p.time }}</div>
              </div>
              <div class="mt-2 text-body-2">{{ p.text }}</div>
              <div class="d-flex ga-3 mt-2">
                <v-btn size="small" variant="text"><v-icon start>mdi-thumb-up-outline</v-icon>{{ p.likes }}</v-btn>
                <v-btn size="small" variant="text"><v-icon start>mdi-chat-outline</v-icon>{{ p.comments }}</v-btn>
              </div>
            </div>
          </div>
        </v-card>
      </v-window-item>

      <!-- FRIENDS -->
      <v-window-item :value="1">
        <div class="d-flex align-center justify-space-between mb-3 flex-wrap ga-2">
          <div>
            <div class="text-subtitle-1 font-weight-medium">Your Study Buddies ({{ friends.length }})</div>
            <div class="text-caption">Stay connected and motivated together</div>
          </div>
          <v-btn class="btn-dark" prepend-icon="mdi-account-plus">Add Friend</v-btn>
        </div>

        <v-row dense>
          <v-col v-for="f in friends" :key="f.id" cols="12" md="6">
            <v-card rounded="xl" class="soft-card pa-4">
              <div class="d-flex flex-wrap ga-3">
                <v-avatar size="44" class="bg-muted text-on-muted">{{ f.initials }}</v-avatar>
                <div class="flex-1 min-w-0">
                  <div class="d-flex align-center flex-wrap ga-2">
                    <div class="text-subtitle-1 font-weight-medium">{{ f.name }}</div>
                    <v-chip size="small" class="chip-outline">Level {{ f.level }}</v-chip>
                    <div class="d-flex align-center ga-1 ms-auto">
                      <span class="status-dot" :class="f.online ? 'online' : ''"></span>
                      <span class="text-caption">{{ f.status }}</span>
                    </div>
                  </div>
                  <v-row class="mt-3" dense>
                    <v-col cols="4">
                      <div class="text-overline text-muted">STUDY</div>
                      <div class="text-h6">{{ f.study }}</div>
                    </v-col>
                    <v-col cols="4">
                      <div class="text-overline text-muted">CHECK-IN</div>
                      <div class="text-h6">{{ f.checkin }}</div>
                    </v-col>
                    <v-col cols="4">
                      <div class="text-overline text-muted">THIS WEEK</div>
                      <div class="text-h6">{{ f.week }}</div>
                    </v-col>
                  </v-row>
                </div>
              </div>
            </v-card>
          </v-col>
        </v-row>
      </v-window-item>

      <!-- CHALLENGES -->
      <v-window-item :value="2">
        <div class="text-subtitle-1 font-weight-medium">Active Challenges</div>
        <div class="text-caption mb-3">Join challenges to stay motivated and earn rewards</div>

        <v-card v-for="c in challenges" :key="c.id" rounded="xl" class="soft-card pa-4 mb-4">
          <div class="d-flex align-center flex-wrap ga-2 mb-1">
            <div class="text-subtitle-1 font-weight-bold mr-auto">{{ c.title }}</div>
            <v-chip size="small" class="chip-tonal">{{ c.participants }} participants</v-chip>
          </div>
          <div class="text-body-2 text-muted mb-3">{{ c.subtitle }}</div>
          <div class="mb-1 text-caption">Progress</div>
          <v-progress-linear
            :model-value="Math.round((c.progress / c.goal) * 100)"
            height="10"
            rounded
            color="var(--primary)"
            bg-color="var(--surface-light)"
          />
          <div class="text-caption text-right mt-1">{{ c.progress }}/{{ c.goal }}</div>
          <v-row class="mt-3" align="center">
            <v-col cols="12" md="8">
              <div class="text-caption">
                <strong>Reward:</strong> {{ c.reward }}<br />
                <span class="text-muted">Time left: {{ c.time }}</span>
              </div>
            </v-col>
            <v-col cols="12" md="4" class="d-flex justify-end">
              <v-btn class="btn-dark w-100 w-md-auto" prepend-icon="mdi-target-variant">Join Challenge</v-btn>
            </v-col>
          </v-row>
        </v-card>
      </v-window-item>

      <!-- LEADERBOARD -->
      <v-window-item :value="3">
        <v-card rounded="xl" class="soft-card pa-4">
          <div class="d-flex align-center ga-2 mb-1">
            <v-icon>mdi-trophy-outline</v-icon>
            <div class="text-subtitle-1 font-weight-medium">Weekly Leaderboard</div>
          </div>
          <div class="text-caption mb-3">Top performers this week</div>
          <v-list>
            <v-list-item
              v-for="l in leaders"
              :key="l.rank"
              class="leader-row"
              :class="{ you: l.name === 'You' }"
            >
              <template #prepend><div class="rank-pill">{{ l.rank }}</div></template>
              <v-avatar class="bg-muted text-on-muted me-3">{{ l.initials }}</v-avatar>
              <v-list-item-title class="font-weight-medium">{{ l.name }}</v-list-item-title>
              <v-list-item-subtitle>Level {{ l.level }} • {{ l.xp.toLocaleString() }} XP</v-list-item-subtitle>
              <template #append><v-chip v-if="l.medal" class="medal-chip">{{ l.medal }}</v-chip></template>
            </v-list-item>
          </v-list>
        </v-card>
      </v-window-item>
    </v-window>
      </div>
    </div>
  </div>
</template>

<style scoped>
.text-muted { color: var(--text-muted); }

/* Ensure container doesn't clip content */
:deep(.v-container) {
  overflow: visible !important;
}

:deep(.v-main) {
  overflow: visible !important;
}

.soft-card {
  background: var(--surface);
  border: 1px solid var(--surface-lighter);
}

/* ===== Social Hub Container ===== */
.social-hub-container {
  min-height: 100vh;
  background-color: var(--background);
}

/* Main Content Styles */
.main-content {
  padding: 32px;
  background-color: var(--background);
  max-width: 1200px;
  margin: 0 auto;
}

.content-header {
  margin-bottom: 24px;
}

.page-title {
  font-size: 32px;
  font-weight: bold;
  color: var(--text-primary);
  margin: 0 0 8px 0;
}

.page-subtitle {
  font-size: 16px;
  color: var(--text-muted);
  margin: 0;
}

.tab-navigation {
  display: flex;
  gap: 0;
  margin-bottom: 24px;
  background-color: var(--surface-lighter);
  border-radius: 12px;
  padding: 4px;
  position: relative;
}

.tab-item {
  padding: 12px 24px;
  cursor: pointer;
  border-radius: 8px;
  transition: all 0.3s ease;
  color: var(--text-muted);
  font-weight: 500;
  position: relative;
  flex: 1;
  text-align: center;
  background: transparent;
}

.tab-item:hover {
  background-color: rgba(255, 255, 255, 0.5);
  color: var(--text-primary);
}

.tab-item.active {
  background-color: var(--surface);
  color: var(--text-primary);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  font-weight: 600;
}

.tab-item.active::after {
  content: '';
  position: absolute;
  bottom: -4px;
  left: 50%;
  transform: translateX(-50%);
  width: 20px;
  height: 3px;
  background-color: var(--primary);
  border-radius: 2px;
}

.tab-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
}
/* Mobile responsiveness */
@media (max-width: 768px) {
  .main-content {
    padding: 16px;
  }
  
  .page-title {
    font-size: 24px;
  }
  
  .tab-item {
    padding: 10px 16px;
    font-size: 14px;
  }
}

/* === Composer & Buttons === */
.composer-area :deep(.v-field){
  background: var(--surface) !important;
  border-radius: 12px;
}
.v-theme--dark .composer-area :deep(.v-field){
  background: var(--surface) !important;
}
.btn-dark{
  background: var(--primary) !important;
  color: #fff !important;
  border-radius: 12px;
  padding-inline: 18px;
  min-width: 160px;
  box-shadow: 0 2px 6px rgba(0,0,0,.25);
}
.btn-dark:hover{ filter: brightness(0.95); }



/* === Helpers === */
.status-dot{ width:8px;height:8px;border-radius:50%;background:var(--surface-lighter);}
.status-dot.online{ background:var(--secondary); }
.rank-pill{ width:34px;height:34px;border-radius:10px;background:var(--surface);display:grid;place-items:center;font-weight:600;margin-right:10px; }
</style>

