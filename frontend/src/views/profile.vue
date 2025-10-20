<template>
  <div class="profile-container">
    <!-- Main Content -->
    <div class="main-content">
      <!-- Header -->
      <div class="content-header">
        <h1 class="page-title">Profile</h1>
        <p class="page-subtitle">Manage your account and preferences</p>
      </div>

      <!-- Tab Navigation -->
      <div class="tab-navigation">
        <div
          class="tab-item"
          :class="{ active: activeTab === 'overview' }"
          @click="activeTab = 'overview'"
        >
          Overview
        </div>
        <div
          class="tab-item"
          :class="{ active: activeTab === 'pet' }"
          @click="activeTab = 'pet'"
        >
          Pet
        </div>
        <div
          class="tab-item"
          :class="{ active: activeTab === 'achievements' }"
          @click="activeTab = 'achievements'"
        >
          Achievements
        </div>
        <div
          class="tab-item"
          :class="{ active: activeTab === 'settings' }"
          @click="activeTab = 'settings'"
        >
          Settings
        </div>
      </div>

      <!-- Tab Content -->
      <div class="tab-content">
        <!-- Overview Tab -->
        <div v-if="activeTab === 'overview'" class="overview-content">
          <!-- Profile Summary Card -->
          <div class="profile-card">
            <div class="profile-avatar-section">
              <div class="avatar-container">
                <div class="profile-avatar">
                  <img
                    v-if="user.avatar"
                    :src="user.avatar"
                    alt="Profile Avatar"
                    class="avatar-image"
                  />
                  <span v-else class="avatar-text">{{
                    user.name?.charAt(0)?.toUpperCase() || "S"
                  }}</span>
                  <div class="camera-icon" @click="triggerAvatarUpload">
                    <svg
                      width="12"
                      height="12"
                      viewBox="0 0 24 24"
                      fill="currentColor"
                    >
                      <path
                        d="M12 15.5A3.5 3.5 0 0 1 8.5 12A3.5 3.5 0 0 1 12 8.5a3.5 3.5 0 0 1 3.5 3.5a3.5 3.5 0 0 1-3.5 3.5m7.43-2.53c.04-.32.07-.64.07-.97c0-.33-.03-.66-.07-1l2.11-1.63c.19-.15.24-.42.12-.64l-2-3.46c-.12-.22-.39-.31-.61-.22l-2.49 1c-.52-.4-1.08-.73-1.69-.98l-.37-2.65A.506.506 0 0 0 14 2h-4c-.25 0-.46.18-.5.42l-.37 2.65c-.61.25-1.17.59-1.69.98l-2.49-1c-.22-.09-.49 0-.61.22l-2 3.46c-.13.22-.07.49.12.64L4.57 11c-.04.34-.07.67-.07 1c0 .33.03.65.07.97l-2.11 1.66c-.19.15-.25.42-.12.64l2 3.46c.12.22.39.3.61.22l2.49-1.01c.52.4 1.08.74 1.69.99l.37 2.65c.04.24.25.42.5.42h4c.25 0 .46-.18.5-.42l.37-2.65c.61-.25 1.17-.59 1.69-.99l2.49 1.01c.22.08.49 0 .61-.22l2-3.46c.12-.22.07-.49-.12-.64l-2.11-1.66Z"
                      />
                    </svg>
                  </div>
                </div>
                <input
                  ref="avatarInput"
                  type="file"
                  accept="image/*"
                  style="display: none"
                  @change="handleAvatarChange"
                />
                <div class="level-badge">Level 1</div>
              </div>
              <div class="profile-info">
                <h2 class="profile-name">{{ user.name || "User" }}</h2>
                <p class="profile-email">
                  {{ user.email || "user@example.com" }}
                </p>
                <p class="profile-member-since">Member since October 2025</p>
                <div class="experience-section">
                  <div class="xp-header">
                    <span class="xp-title">Experience Points</span>
                    <span class="xp-counter">{{ stats.xp }} / 1000 XP</span>
                  </div>
                  <div class="xp-progress">
                    <div class="progress-bar">
                      <div
                        class="progress-fill"
                        :style="{ width: `${(stats.xp / 1000) * 100}%` }"
                      ></div>
                    </div>
                    <div class="xp-until-next">
                      {{ 1000 - stats.xp }} XP until next level
                    </div>
                  </div>
                </div>
              </div>
              <button class="edit-profile-btn" @click="openEditModal">
                <span class="btn-icon">✏️</span>
                Edit Profile
              </button>
            </div>
          </div>

          <!-- Statistics Cards -->
          <div class="stats-grid">
            <div class="stat-card">
              <div class="stat-icon blue">🕐</div>
              <div class="stat-value">{{ stats.studyHours }}</div>
              <div class="stat-label">Study Hours</div>
            </div>
            <div class="stat-card">
              <div class="stat-icon green">🎯</div>
              <div class="stat-value">{{ stats.studyStreak }}</div>
              <div class="stat-label">Study Streak</div>
            </div>
            <div class="stat-card">
              <div class="stat-icon red">❤️</div>
              <div class="stat-value">{{ stats.checkinStreak }}</div>
              <div class="stat-label">Check-in Streak</div>
            </div>
            <div class="stat-card">
              <div class="stat-icon purple">🏆</div>
              <div class="stat-value">{{ stats.achievements }}</div>
              <div class="stat-label">Achievements</div>
            </div>
          </div>

          <!-- Recent Activity -->
          <div class="recent-activity">
            <h3 class="section-title">Recent Activity</h3>
            <div class="activity-list">
              <div class="activity-item">
                <div class="activity-icon blue">🕐</div>
                <div class="activity-content">
                  <div class="activity-title">Completed study session</div>
                  <div class="activity-time">2 hours ago</div>
                </div>
              </div>
              <div class="activity-item">
                <div class="activity-icon green">❤️</div>
                <div class="activity-content">
                  <div class="activity-title">Daily wellness check-in</div>
                  <div class="activity-time">1 day ago</div>
                </div>
              </div>
              <div class="activity-item">
                <div class="activity-icon purple">🏆</div>
                <div class="activity-content">
                  <div class="activity-title">
                    Unlocked "Early Bird" achievement
                  </div>
                  <div class="activity-time">3 days ago</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Pet Tab -->
        <div v-if="activeTab === 'pet'" class="pet-content">
          <div class="pet-card">
            <h3 class="pet-title">Your Virtual Pet - Buddy</h3>
            <p class="pet-subtitle">Take care of your study companion</p>
            <div class="pet-display">
              <div class="pet-avatar">
                <div class="pet-icon">🐱</div>
                <div class="pet-level">Level 1</div>
              </div>
              <div class="pet-stats">
                <div class="pet-stats-row">
                  <div class="pet-stat">
                    <div class="stat-label">Health</div>
                    <div class="stat-bar">
                      <div class="stat-fill" style="width: 80%"></div>
                    </div>
                    <div class="stat-value">80%</div>
                  </div>
                  <div class="pet-stat">
                    <div class="stat-label">Happiness</div>
                    <div class="stat-bar">
                      <div class="stat-fill" style="width: 70%"></div>
                    </div>
                    <div class="stat-value">70%</div>
                  </div>
                </div>
                <div class="pet-details">
                  <div class="pet-detail">
                    <span class="detail-label">Pet Name:</span>
                    <span class="detail-value">Buddy</span>
                  </div>
                  <div class="pet-detail">
                    <span class="detail-label">Pet Type:</span>
                    <span class="detail-value">Cat</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="pet-tips-card">
            <h3 class="tips-title">Pet Care Tips</h3>
            <ul class="tips-list">
              <li>Study regularly to keep your pet healthy</li>
              <li>Complete daily check-ins to boost happiness</li>
              <li>Feed your pet by clicking the feed button</li>
              <li>Your pet's well-being reflects your own!</li>
            </ul>
          </div>
        </div>

        <!-- Achievements Tab -->
        <div v-if="activeTab === 'achievements'" class="achievements-content">
          <div class="achievements-header">
            <div class="achievements-title-section">
              <div class="crown-icon">👑</div>
              <h3 class="achievements-title">Achievements (1/8)</h3>
            </div>
            <p class="achievements-subtitle">
              Track your progress and unlock rewards
            </p>
          </div>
          <div class="achievements-grid">
            <div class="achievement-card unlocked">
              <div class="achievement-icon unlocked-icon">⭐</div>
              <div class="achievement-info">
                <h4 class="achievement-title">Early Bird</h4>
                <p class="achievement-desc">Joined StudyBuddy</p>
              </div>
              <div class="achievement-status unlocked-badge">
                <span class="status-icon">⭐</span>
                <span class="status-text">Unlocked</span>
              </div>
            </div>
            <div class="achievement-card locked">
              <div class="achievement-icon locked-icon">👣</div>
              <div class="achievement-info">
                <h4 class="achievement-title">First Steps</h4>
                <p class="achievement-desc">Completed first study session</p>
              </div>
            </div>
            <div class="achievement-card locked">
              <div class="achievement-icon locked-icon">📚</div>
              <div class="achievement-info">
                <h4 class="achievement-title">Dedicated Learner</h4>
                <p class="achievement-desc">Studied for 10 hours total</p>
              </div>
            </div>
            <div class="achievement-card locked">
              <div class="achievement-icon locked-icon">🔥</div>
              <div class="achievement-info">
                <h4 class="achievement-title">Streak Master</h4>
                <p class="achievement-desc">Maintain a 7-day study streak</p>
              </div>
            </div>
            <div class="achievement-card locked">
              <div class="achievement-icon locked-icon">❤️</div>
              <div class="achievement-info">
                <h4 class="achievement-title">Wellness Warrior</h4>
                <p class="achievement-desc">Complete 5 wellness activities</p>
              </div>
            </div>
            <div class="achievement-card locked">
              <div class="achievement-icon locked-icon">🦋</div>
              <div class="achievement-info">
                <h4 class="achievement-title">Social Butterfly</h4>
                <p class="achievement-desc">Connect with 5 study buddies</p>
              </div>
            </div>
            <div class="achievement-card locked">
              <div class="achievement-icon locked-icon">🏆</div>
              <div class="achievement-info">
                <h4 class="achievement-title">Challenge Champion</h4>
                <p class="achievement-desc">Complete 10 study challenges</p>
              </div>
            </div>
            <div class="achievement-card locked">
              <div class="achievement-icon locked-icon">🐾</div>
              <div class="achievement-info">
                <h4 class="achievement-title">Pet Lover</h4>
                <p class="achievement-desc">
                  Take care of your pet for 30 days
                </p>
              </div>
            </div>
          </div>
        </div>

        <!-- Settings Tab -->
        <div v-if="activeTab === 'settings'" class="settings-content">
          <div class="settings-section">
            <h3 class="section-title">
              <span class="section-icon">🔔</span>
              Notifications
            </h3>
            <p class="section-subtitle">
              Manage your notification preferences.
            </p>
            <div class="settings-list">
              <div class="setting-item">
                <div class="setting-info">
                  <div class="setting-title">Notifications</div>
                  <div class="setting-desc">
                    Manage your notification preferences.
                  </div>
                </div>
                <div
                  class="toggle-switch"
                  :class="{ active: notificationSettings.notifications }"
                  @click="toggleNotification('notifications')"
                ></div>
              </div>
              <div class="setting-item">
                <div class="setting-info">
                  <div class="setting-title">Study Reminders</div>
                  <div class="setting-desc">
                    Get reminded to start your study sessions.
                  </div>
                </div>
                <div
                  class="toggle-switch"
                  :class="{ active: notificationSettings.studyReminders }"
                  @click="toggleNotification('studyReminders')"
                ></div>
              </div>
              <div class="setting-item">
                <div class="setting-info">
                  <div class="setting-title">Daily Check-in</div>
                  <div class="setting-desc">
                    Reminder for daily wellness check-in.
                  </div>
                </div>
                <div
                  class="toggle-switch"
                  :class="{ active: notificationSettings.dailyCheckin }"
                  @click="toggleNotification('dailyCheckin')"
                ></div>
              </div>
              <div class="setting-item">
                <div class="setting-info">
                  <div class="setting-title">Achievement Notifications</div>
                  <div class="setting-desc">
                    Get notified when you unlock achievements.
                  </div>
                </div>
                <div
                  class="toggle-switch"
                  :class="{
                    active: notificationSettings.achievementNotifications,
                  }"
                  @click="toggleNotification('achievementNotifications')"
                ></div>
              </div>
              <div class="setting-item">
                <div class="setting-info">
                  <div class="setting-title">Social Updates</div>
                  <div class="setting-desc">
                    Notifications from friends and challenges.
                  </div>
                </div>
                <div
                  class="toggle-switch"
                  :class="{ active: notificationSettings.socialUpdates }"
                  @click="toggleNotification('socialUpdates')"
                ></div>
              </div>
            </div>
          </div>

          <div class="settings-section">
            <h3 class="section-title">
              <span class="section-icon">⚙️</span>
              Preferences
            </h3>
            <div class="preference-item">
              <label class="preference-label">Daily Study Goal (minutes)</label>
              <input
                type="number"
                class="preference-input"
                v-model="preferences.dailyStudyGoal"
                placeholder="120"
                min="1"
                max="1440"
              />
            </div>
            <div class="preference-item">
              <label class="preference-label">Theme</label>
              <select class="preference-select" v-model="preferences.theme">
                <option value="system">System</option>
                <option value="light">Light</option>
                <option value="dark">Dark</option>
              </select>
            </div>
          </div>

          <div class="settings-section">
            <h3 class="section-title">Account</h3>
            <div class="account-actions">
              <button class="signout-btn" @click="confirmLogout">
                <span class="btn-icon"></span>
                Sign Out
              </button>
              <button class="delete-btn" @click="confirmDeleteAccount">
                <span class="btn-icon"></span>
                Delete Account
              </button>
            </div>
          </div>

          <!-- Save Settings Button -->
          <div class="settings-save-section">
            <button class="save-settings-btn" @click="saveSettings">
              <span class="btn-icon"></span>
              Save Settings
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Edit Profile Modal -->
    <div v-if="showEditModal" class="modal-overlay" @click="closeEditModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3 class="modal-title">Edit Profile</h3>
          <button class="modal-close" @click="closeEditModal">×</button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="saveProfile">
            <div class="form-group">
              <label for="edit-name" class="form-label">Name</label>
              <input
                id="edit-name"
                v-model="editForm.name"
                type="text"
                class="form-input"
                placeholder="Enter your name"
                required
              />
            </div>
            <div class="form-group">
              <label for="edit-email" class="form-label">Email</label>
              <input
                id="edit-email"
                v-model="editForm.email"
                type="email"
                class="form-input"
                placeholder="Enter your email"
                required
              />
            </div>
            <div class="modal-actions">
              <button type="submit" class="btn-save">Save Changes</button>
              <button type="button" class="btn-cancel" @click="closeEditModal">
                Cancel
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- Avatar Upload Modal -->
    <div v-if="showAvatarModal" class="modal-overlay" @click="closeAvatarModal">
      <div class="modal-content avatar-modal" @click.stop>
        <div class="modal-header">
          <h3 class="modal-title">Change Profile Picture</h3>
          <button class="modal-close" @click="closeAvatarModal">×</button>
        </div>
        <div class="modal-body">
          <div class="avatar-preview">
            <div class="preview-avatar">
              <img
                v-if="previewAvatar"
                :src="previewAvatar"
                alt="Preview"
                class="preview-image"
              />
              <span v-else class="preview-initials">{{
                user.name?.charAt(0)?.toUpperCase() || "S"
              }}</span>
            </div>
          </div>
          <div class="avatar-options">
            <button class="option-btn upload-btn" @click="triggerFileUpload">
              <span class="btn-icon">📁</span>
              Upload Photo
            </button>
            <button class="option-btn default-btn" @click="useDefaultAvatar">
              <span class="btn-icon">👤</span>
              Use Initials
            </button>
          </div>
          <input
            ref="avatarInput"
            type="file"
            accept="image/*"
            style="display: none"
            @change="handleAvatarChange"
          />
        </div>
      </div>
    </div>

    <!-- Success Toast Notification -->
    <div v-if="showSuccessToast" class="success-toast">
      <div class="toast-icon">✓</div>
      <div class="toast-message">Profile updated successfully!</div>
    </div>

    <!-- Sign Out Confirmation Modal -->
    <div v-if="showLogoutModal" class="modal-overlay" @click="closeLogoutModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3 class="modal-title">Sign Out</h3>
          <button class="modal-close" @click="closeLogoutModal">×</button>
        </div>
        <div class="modal-body">
          <p style="margin: 0 0 16px 0; color: var(--text-primary)">
            Are you sure you want to sign out?
          </p>
          <div class="modal-actions">
            <button type="button" class="btn-cancel" @click="closeLogoutModal">
              Cancel
            </button>
            <button type="button" class="btn-danger" @click="confirmLogoutProceed">
              Sign Out
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Delete Account Confirmation Modal -->
    <div v-if="showDeleteModal" class="modal-overlay" @click="closeDeleteModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3 class="modal-title">Delete Account</h3>
          <button class="modal-close" @click="closeDeleteModal">×</button>
        </div>
        <div class="modal-body">
          <p style="margin: 0 0 16px 0; color: var(--text-primary)">
            This action is permanent. Are you sure you want to delete your account?
          </p>

          <div style="margin: 12px 0 8px 0; color: var(--text-primary)">
            To continue, solve the equation:
          </div>
          <div style="display:flex; align-items:center; gap:12px; margin-bottom:16px">
            <div style="font-weight:600; font-size:16px; color: var(--text-primary)">{{ deleteChallenge.a }} {{ deleteChallenge.op }} {{ deleteChallenge.b }} = ?</div>
            <input
              type="number"
              class="form-input"
              style="max-width:140px"
              v-model="deleteChallenge.userInput"
              placeholder="Your answer"
            />
          </div>

          <div class="modal-actions">
            <button type="button" class="btn-cancel" @click="closeDeleteModal">
              Cancel
            </button>
            <button type="button" class="btn-danger" :disabled="!isDeleteAnswerCorrect" @click="confirmDeleteProceed">
              Delete Account
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref, watch } from "vue";
import { useRouter } from "vue-router";

import { useAuth } from "@/composables/useAuth.js";
import { api } from "@/lib/api.js";

const { userProfile, user: authUser, logout: baseLogout } = useAuth();

const router = useRouter();
const activeTab = ref("overview");
const showEditModal = ref(false);
const showSuccessToast = ref(false);
const showAvatarModal = ref(false);
const showLogoutModal = ref(false);
const showDeleteModal = ref(false);
const deleteChallenge = reactive({ a: 0, b: 0, op: '+', userInput: '' });
const isDeleteAnswerCorrect = ref(false);
const avatarInput = ref(null);
const previewAvatar = ref(null);

const user = reactive({
  name: "",
  email: "",
  avatar: null,
});

const editForm = reactive({
  name: "",
  email: "",
});

const stats = reactive({
  studyHours: 0,
  studyStreak: 0,
  checkinStreak: 0,
  wellnessStreak: 0,
  achievements: 1,
  xp: 0,
});

const defaultNotificationSettings = {
  notifications: true,
  studyReminders: true,
  dailyCheckin: true,
  achievementNotifications: false,
  socialUpdates: false,
};

const defaultPreferences = {
  dailyStudyGoal: 120,
  theme: "system",
  timezone: "UTC+8",
  timer: {
    focusDuration: 25,
    breakDuration: 5,
    longBreakDuration: 15,
  },
};

// Notification settings
const notificationSettings = reactive({ ...defaultNotificationSettings });

// Preferences settings
const preferences = reactive({
  dailyStudyGoal: defaultPreferences.dailyStudyGoal,
  theme: defaultPreferences.theme,
  timezone: defaultPreferences.timezone,
  timer: { ...defaultPreferences.timer },
});

const isLoadingSettings = ref(false);
let shouldRehydrate = false;

onMounted(() => {
  try {
    const data = JSON.parse(localStorage.getItem("demo_user") || "{}");
    if (data?.email) user.email = data.email;
    if (data?.name) user.name = data.name;
    if (data?.avatar) user.avatar = data.avatar;
  } catch {}
});

function openEditModal() {
  editForm.name = user.name;
  editForm.email = user.email;
  showEditModal.value = true;
}

function closeEditModal() {
  showEditModal.value = false;
  editForm.name = "";
  editForm.email = "";
}

function saveProfile() {
  user.name = editForm.name;
  user.email = editForm.email;

  // Save to localStorage
  const userData = {
    name: user.name,
    email: user.email,
  };
  localStorage.setItem("demo_user", JSON.stringify(userData));

  closeEditModal();
  showSuccessNotification();
}

function showSuccessNotification() {
  showSuccessToast.value = true;
  setTimeout(() => {
    showSuccessToast.value = false;
  }, 3000); // Hide after 3 seconds
}

function triggerAvatarUpload() {
  showAvatarModal.value = true;
  previewAvatar.value = user.avatar;
}

function triggerFileUpload() {
  avatarInput.value.click();
}

function closeAvatarModal() {
  showAvatarModal.value = false;
  previewAvatar.value = null;
}

function useDefaultAvatar() {
  user.avatar = null;
  previewAvatar.value = null;
  // Save to localStorage
  const userData = {
    name: user.name,
    email: user.email,
    avatar: user.avatar,
  };
  localStorage.setItem("demo_user", JSON.stringify(userData));
  closeAvatarModal();
  showSuccessNotification();
}

function handleAvatarChange(event) {
  const file = event.target.files[0];
  if (file) {
    // Validate file type
    if (!file.type.startsWith("image/")) {
      alert("Please select a valid image file");
      return;
    }

    // Validate file size (max 5MB)
    if (file.size > 5 * 1024 * 1024) {
      alert("Image size should be less than 5MB");
      return;
    }

    // Create a preview URL
    const reader = new FileReader();
    reader.onload = (e) => {
      previewAvatar.value = e.target.result;
      user.avatar = e.target.result;
      // Save to localStorage
      const userData = {
        name: user.name,
        email: user.email,
        avatar: user.avatar,
      };
      localStorage.setItem("demo_user", JSON.stringify(userData));
      closeAvatarModal();
      showSuccessNotification();
    };
    reader.readAsDataURL(file);
  }
}

function toggleNotification(setting) {
  notificationSettings[setting] = !notificationSettings[setting];
  // Note: Individual toggles no longer auto-save, user must click Save Settings
}

// Recompute whether the math challenge answer is correct whenever user input changes
watch(
  () => deleteChallenge.userInput,
  (val) => {
    const parsed = Number(val);
    const correct =
      deleteChallenge.op === '+'
        ? deleteChallenge.a + deleteChallenge.b
        : deleteChallenge.a - deleteChallenge.b;
    isDeleteAnswerCorrect.value = Number.isFinite(parsed) && parsed === correct;
  }
);

function logout() {
  baseLogout();
  router.push("/login");
}

function confirmLogout() {
  showLogoutModal.value = true;
}

function closeLogoutModal() {
  showLogoutModal.value = false;
}

function confirmLogoutProceed() {
  showLogoutModal.value = false;
  logout();
}

function confirmDeleteAccount() {
  // generate easy math challenge: numbers 1-9, random + or - with non-negative result
  const a = Math.floor(Math.random() * 9) + 1;
  const b = Math.floor(Math.random() * 9) + 1;
  const useAddition = Math.random() < 0.5;
  if (useAddition) {
    deleteChallenge.a = a;
    deleteChallenge.b = b;
    deleteChallenge.op = '+';
  } else {
    const maxVal = Math.max(a, b);
    const minVal = Math.min(a, b);
    deleteChallenge.a = maxVal;
    deleteChallenge.b = minVal;
    deleteChallenge.op = '-';
  }
  deleteChallenge.userInput = '';
  isDeleteAnswerCorrect.value = false;
  showDeleteModal.value = true;
}

function closeDeleteModal() {
  showDeleteModal.value = false;
}

function confirmDeleteProceed() {
  showDeleteModal.value = false;
  // Implement deletion here (API call). For demo, sign out afterward.
  logout();
}

function resetNotificationSettings() {
  Object.assign(notificationSettings, { ...defaultNotificationSettings });
}

function resetPreferences() {
  Object.assign(preferences, {
    dailyStudyGoal: defaultPreferences.dailyStudyGoal,
    theme: defaultPreferences.theme,
    timezone: defaultPreferences.timezone,
  });
  Object.assign(preferences.timer, { ...defaultPreferences.timer });
}

function toNumber(value, fallback) {
  if (value === null || value === undefined || value === "") {
    return fallback;
  }
  const num = Number(value);
  return Number.isFinite(num) ? num : fallback;
}

watch(
  [() => userProfile.value, () => authUser.value],
  ([profile, firebaseUser]) => {
    if (profile) {
      const fallbackName =
        firebaseUser?.displayName || firebaseUser?.email || "";
      user.name = profile.full_name || profile.name || fallbackName || "";
      user.email = profile.email || firebaseUser?.email || "";
      user.avatar =
        profile.avatar ||
        profile.avatar_url ||
        firebaseUser?.photoURL ||
        null;
    } else if (firebaseUser) {
      user.name = firebaseUser.displayName || firebaseUser.email || "";
      user.email = firebaseUser.email || "";
      user.avatar = firebaseUser.photoURL || null;
    } else {
      user.name = "";
      user.email = "";
      user.avatar = null;
    }
  },
  { immediate: true }
);

watch(
  () => authUser.value,
  (firebaseUser) => {
    if (firebaseUser) {
      hydrateSettings();
    } else {
      resetNotificationSettings();
      resetPreferences();
    }
  },
  { immediate: true }
);

async function hydrateSettings() {
  if (isLoadingSettings.value) {
    shouldRehydrate = true;
    return;
  }
  isLoadingSettings.value = true;
  try {
    await Promise.all([loadNotificationSettings(), loadUserPreferences()]);
  } finally {
    isLoadingSettings.value = false;
    if (shouldRehydrate) {
      shouldRehydrate = false;
      hydrateSettings();
    }
  }
}

async function loadNotificationSettings() {
  try {
    const settings = await api.get("/api/notifications/settings");
    const mappedSettings = {
      notifications:
        settings.notifications ?? defaultNotificationSettings.notifications,
      studyReminders:
        settings.study_reminders ?? defaultNotificationSettings.studyReminders,
      dailyCheckin:
        settings.daily_checkin ?? defaultNotificationSettings.dailyCheckin,
      achievementNotifications:
        settings.achievement_notifications ??
        defaultNotificationSettings.achievementNotifications,
      socialUpdates:
        settings.social_updates ?? defaultNotificationSettings.socialUpdates,
    };

    Object.assign(notificationSettings, mappedSettings);
  } catch (error) {
    console.log("Failed to load notification settings:", error);
    resetNotificationSettings();
  }
}

async function loadUserPreferences() {
  try {
    const prefs = await api.get("/api/profile/preferences");
    Object.assign(preferences, {
      dailyStudyGoal:
        prefs.daily_study_goal ?? defaultPreferences.dailyStudyGoal,
      theme: prefs.theme ?? defaultPreferences.theme,
      timezone: prefs.timezone ?? defaultPreferences.timezone,
    });
    const timerSettings = prefs.timer_settings || {};
    Object.assign(preferences.timer, {
      focusDuration:
        timerSettings.focus_duration ??
        defaultPreferences.timer.focusDuration,
      breakDuration:
        timerSettings.break_duration ?? defaultPreferences.timer.breakDuration,
      longBreakDuration:
        timerSettings.long_break_duration ??
        defaultPreferences.timer.longBreakDuration,
    });
  } catch (error) {
    console.log("Failed to load user preferences:", error);
    resetPreferences();
  }
}

async function saveSettings() {
  try {
    const notificationPayload = {
      notifications: notificationSettings.notifications,
      study_reminders: notificationSettings.studyReminders,
      daily_checkin: notificationSettings.dailyCheckin,
      achievement_notifications: notificationSettings.achievementNotifications,
      social_updates: notificationSettings.socialUpdates,
    };

    const preferencesPayload = {
      daily_study_goal: toNumber(
        preferences.dailyStudyGoal,
        defaultPreferences.dailyStudyGoal
      ),
      theme: preferences.theme,
      timezone: preferences.timezone,
      timer_settings: {
        focus_duration: toNumber(
          preferences.timer.focusDuration,
          defaultPreferences.timer.focusDuration
        ),
        break_duration: toNumber(
          preferences.timer.breakDuration,
          defaultPreferences.timer.breakDuration
        ),
        long_break_duration: toNumber(
          preferences.timer.longBreakDuration,
          defaultPreferences.timer.longBreakDuration
        ),
      },
    };

    await Promise.all([
      api.put("/api/notifications/settings", notificationPayload),
      api.put("/api/profile/preferences", preferencesPayload),
    ]);

    await hydrateSettings();

    showSuccessNotification();
  } catch (error) {
    console.log(error);
    alert("Failed to save settings: " + error.message);
  }
}
</script>

<style scoped>
.profile-container {
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
  content: "";
  position: absolute;
  bottom: -4px;
  left: 50%;
  transform: translateX(-50%);
  width: 20px;
  height: 3px;
  background-color: var(--primary);
  border-radius: 2px;
}

/* Overview Content */
.overview-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.profile-card {
  background: var(--surface);
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border: 1px solid var(--surface-lighter);
}

.profile-avatar-section {
  display: flex;
  align-items: flex-start;
  gap: 24px;
  position: relative;
  margin-bottom: 20px;
}

.avatar-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.profile-avatar {
  width: 80px;
  height: 80px;
  background-color: var(--surface-light);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32px;
  font-weight: bold;
  color: var(--text-muted);
  position: relative;
  overflow: hidden;
}

.avatar-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 50%;
}

.camera-icon {
  position: absolute;
  bottom: 4px;
  right: 4px;
  background: var(--surface);
  border-radius: 50%;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
  border: 2px solid var(--surface);
  z-index: 10;
  cursor: pointer;
  transition: all 0.2s;
}

.camera-icon:hover {
  background: var(--surface-light);
  transform: scale(1.1);
}

.level-badge {
  background-color: var(--surface-lighter);
  color: var(--text-primary);
  padding: 4px 12px;
  border-radius: 12px;
  border: 1px solid var(--border);
  font-size: 12px;
  font-weight: 500;
  margin-top: 8px;
  align-self: center;
}

.profile-info {
  flex: 1;
}

.profile-name {
  font-size: 24px;
  font-weight: bold;
  margin: 0 0 8px 0;
  color: var(--text-primary);
}

.profile-email {
  font-size: 16px;
  color: var(--text-muted);
  margin: 0 0 4px 0;
}

.profile-member-since {
  font-size: 14px;
  color: var(--text-disabled);
  margin: 0 0 16px 0;
}

.experience-section {
  margin-top: 16px;
}

.xp-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.xp-title {
  font-size: 16px;
  font-weight: 500;
  color: var(--text-primary);
}

.xp-counter {
  font-size: 14px;
  color: var(--text-muted);
}

.xp-progress {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.progress-bar {
  width: 100%;
  height: 8px;
  background-color: var(--surface-lighter);
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background-color: var(--surface-lighter);
  transition: width 0.3s;
}

.xp-until-next {
  font-size: 12px;
  color: var(--text-muted);
}

.edit-profile-btn {
  position: absolute;
  top: 0;
  right: 0;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: var(--surface);
  border: 1px solid var(--surface-lighter);
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  color: var(--text-primary);
  transition: all 0.2s;
}

.edit-profile-btn:hover {
  background: var(--surface-light);
}

.btn-icon {
  font-size: 12px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.stat-card {
  background: var(--surface);
  border-radius: 12px;
  padding: 24px;
  text-align: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border: 1px solid var(--surface-lighter);
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  margin: 0 auto 12px;
}

.stat-icon.blue {
  background-color: #e3f2fd;
}
.stat-icon.green {
  background-color: #e8f5e8;
}
.stat-icon.red {
  background-color: #ffebee;
}
.stat-icon.purple {
  background-color: #f3e5f5;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.stat-label {
  font-size: 14px;
  color: var(--text-muted);
}

.recent-activity {
  background: var(--surface);
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border: 1px solid var(--surface-lighter);
}

.section-title {
  font-size: 20px;
  font-weight: bold;
  color: var(--text-primary);
  margin: 0 0 16px 0;
}

.activity-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.activity-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background-color: var(--surface-light);
  border-radius: 8px;
}

.activity-icon {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
}

.activity-icon.blue {
  background-color: #e3f2fd;
}
.activity-icon.green {
  background-color: #e8f5e8;
}
.activity-icon.purple {
  background-color: #f3e5f5;
}

.activity-content {
  flex: 1;
}

.activity-title {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
  margin-bottom: 2px;
}

.activity-time {
  font-size: 12px;
  color: var(--text-muted);
}

/* Pet Content */
.pet-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.pet-card {
  background: var(--surface);
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border: 1px solid var(--surface-lighter);
}

.pet-title {
  font-size: 20px;
  font-weight: bold;
  color: var(--text-primary);
  margin: 0 0 8px 0;
}

.pet-subtitle {
  font-size: 14px;
  color: var(--text-muted);
  margin: 0 0 24px 0;
}

.pet-display {
  display: flex;
  align-items: center;
  gap: 24px;
}

.pet-avatar {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.pet-icon {
  width: 80px;
  height: 80px;
  background-color: #e1bee7;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32px;
}

.pet-level {
  font-size: 14px;
  font-weight: bold;
  color: var(--text-primary);
  background-color: var(--surface-lighter);
  padding: 4px 12px;
  border-radius: 12px;
  border: 1px solid var(--border);
}

.pet-stats {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.pet-stats-row {
  display: flex;
  gap: 32px;
  align-items: center;
  justify-content: space-between;
  width: 100%;
}

.pet-stat {
  display: flex;
  flex-direction: column;
  gap: 4px;
  flex: 1;
  min-width: 0;
}

.stat-label {
  font-size: 14px;
  color: var(--text-muted);
  font-weight: 500;
}

.stat-bar {
  width: 100%;
  height: 8px;
  background-color: var(--surface-lighter);
  border-radius: 4px;
  overflow: hidden;
}

.stat-fill {
  height: 100%;
  background-color: var(--primary);
  border-radius: 4px;
}

.stat-value {
  font-size: 12px;
  color: var(--text-muted);
  font-weight: 500;
}

.pet-details {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.pet-detail {
  display: flex;
  gap: 8px;
}

.detail-label {
  font-size: 14px;
  color: var(--text-muted);
  min-width: 80px;
}

.detail-value {
  font-size: 14px;
  color: var(--text-primary);
  font-weight: 500;
}

.pet-tips-card {
  background: var(--surface);
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border: 1px solid var(--surface-lighter);
}

.tips-title {
  font-size: 18px;
  font-weight: bold;
  color: var(--text-primary);
  margin: 0 0 16px 0;
}

.tips-list {
  margin: 0;
  padding-left: 20px;
  color: var(--text-muted);
}

.tips-list li {
  margin-bottom: 8px;
}

/* Achievements Content */
.achievements-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.achievements-header {
  margin-bottom: 24px;
}

.achievements-title-section {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.crown-icon {
  font-size: 20px;
}

.achievements-title {
  font-size: 24px;
  font-weight: bold;
  color: var(--text-primary);
  margin: 0;
}

.achievements-subtitle {
  font-size: 14px;
  color: var(--text-muted);
  margin: 0;
}

.achievements-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.achievement-card {
  background-color: var(--surface);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 16px;
  display: flex;
  align-items: center;
  gap: 12px;
  transition: all 0.2s ease;
  position: relative;
}

.achievement-card:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.achievement-card.unlocked {
  border-color: var(--primary);
  background-color: var(--surface-light);
}

.achievement-card.locked {
  opacity: 0.6;
  filter: grayscale(0.3);
}

.achievement-icon {
  font-size: 24px;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
}

.achievement-icon.unlocked-icon {
  background-color: #fbbf24;
  color: white;
}

.achievement-icon.locked-icon {
  background-color: var(--surface-lighter);
  color: var(--text-muted);
}

.achievement-info {
  flex: 1;
}

.achievement-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 4px 0;
}

.achievement-card.locked .achievement-title {
  color: var(--text-muted);
}

.achievement-desc {
  font-size: 14px;
  color: var(--text-muted);
  margin: 0;
}

.achievement-card.locked .achievement-desc {
  color: var(--text-muted);
  opacity: 0.7;
}

.achievement-status {
  display: flex;
  align-items: center;
  gap: 4px;
}

.unlocked-badge {
  background-color: var(--surface-lighter);
  color: var(--text-primary);
  padding: 4px 8px;
  border-radius: 12px;
  border: 1px solid var(--border);
  font-size: 12px;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 4px;
}

.status-icon {
  font-size: 12px;
}

.status-text {
  font-size: 12px;
}

/* Settings Content */
.settings-content {
  display: flex;
  flex-direction: column;
  gap: 32px;
}

.settings-section {
  background: var(--surface);
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border: 1px solid var(--surface-lighter);
}

.section-title {
  font-size: 20px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 16px 0;
  display: flex;
  align-items: center;
  gap: 10px;
}

.section-icon {
  font-size: 18px;
  color: var(--primary);
}

.section-subtitle {
  font-size: 14px;
  color: var(--text-muted);
  margin: 0 0 16px 0;
}

.settings-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.setting-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid var(--surface-lighter);
}

.setting-item:last-child {
  border-bottom: none;
}

.setting-info {
  flex: 1;
}

.setting-title {
  font-size: 16px;
  font-weight: 500;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.setting-desc {
  font-size: 14px;
  color: var(--text-muted);
}

.toggle-switch {
  width: 48px;
  height: 24px;
  background-color: var(--surface-lighter);
  border-radius: 12px;
  position: relative;
  cursor: pointer;
  transition: background-color 0.2s;
}

.toggle-switch.active {
  background-color: var(--primary);
}

.toggle-switch::after {
  content: "";
  position: absolute;
  top: 2px;
  left: 2px;
  width: 20px;
  height: 20px;
  background-color: var(--surface);
  border-radius: 50%;
  transition: transform 0.2s;
}

.toggle-switch.active::after {
  transform: translateX(24px);
}

.preference-item {
  margin-bottom: 24px;
}

.preference-item:last-child {
  margin-bottom: 0;
}

.preference-label {
  display: block;
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 12px;
}

.preference-input,
.preference-select {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid #e0e0e0;
  border-radius: 12px;
  font-size: 16px;
  background-color: #f8f9fa;
  color: var(--text-primary);
  transition: all 0.2s ease;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.preference-input:focus,
.preference-select:focus {
  outline: none;
  border-color: var(--primary);
  background-color: var(--surface);
  box-shadow: 0 0 0 3px rgba(106, 122, 90, 0.1);
}

.preference-input:hover,
.preference-select:hover {
  border-color: #ccc;
  background-color: var(--surface);
}

.preference-select {
  cursor: pointer;
  appearance: none;
  background-image: url("data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3e%3cpolyline points='6,9 12,15 18,9'%3e%3c/polyline%3e%3c/svg%3e");
  background-repeat: no-repeat;
  background-position: right 12px center;
  background-size: 16px;
  padding-right: 40px;
}

/* Style dropdown options with rounded corners */
.preference-select option {
  padding: 12px 16px;
  border-radius: 8px;
  margin: 2px;
  background-color: var(--surface);
  color: var(--text-primary);
}

/* Style the dropdown list container */
.preference-select:focus {
  border-radius: 12px 12px 0 0;
}

/* Custom dropdown styling for better appearance */
.preference-select option:checked {
  background-color: var(--primary);
  color: white;
  border-radius: 8px;
}

/* Dark mode adjustments */
[data-theme="dark"] .preference-input,
[data-theme="dark"] .preference-select {
  background-color: var(--surface-light);
  border-color: var(--border);
  color: var(--text-primary);
}

[data-theme="dark"] .preference-input:focus,
[data-theme="dark"] .preference-select:focus {
  background-color: var(--surface);
  box-shadow: 0 0 0 3px rgba(141, 175, 155, 0.2);
}

[data-theme="dark"] .preference-input:hover,
[data-theme="dark"] .preference-select:hover {
  background-color: var(--surface);
}

.privacy-actions {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.account-actions {
  display: flex;
  gap: 12px;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
}

.account-actions .signout-btn,
.account-actions .delete-btn {
  flex: 1 1 240px;
}

.export-btn,
.delete-btn,
.signout-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  border: 1px solid var(--surface-lighter);
  border-radius: 6px;
  background: var(--surface);
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
  color: var(--text-primary);
}

.delete-btn {
  background-color: var(--error);
  color: white;
  border-color: var(--error);
  justify-content: center;
}

.delete-btn:hover {
  background-color: #c82333;
}

.signout-btn {
  justify-content: center;
}

.export-btn:hover,
.signout-btn:hover {
  background-color: var(--surface-light);
}

.btn-icon {
  font-size: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* Save Settings Section */
.settings-save-section {
  margin-top: 32px;
  padding-top: 24px;
  border-top: 1px solid var(--surface-lighter);
}

.save-settings-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 16px 32px;
  border: none;
  border-radius: 12px;
  background: var(--primary);
  color: white;
  cursor: pointer;
  font-size: 16px;
  font-weight: 600;
  transition: all 0.2s ease;
  box-shadow: 0 2px 8px rgba(106, 122, 90, 0.3);
  width: 100%;
}

.save-settings-btn:hover {
  background: var(--secondary);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(106, 122, 90, 0.4);
}

.save-settings-btn:active {
  transform: translateY(0);
  box-shadow: 0 2px 6px rgba(106, 122, 90, 0.3);
}

@media (max-width: 768px) {
  .main-content {
    padding: 16px;
  }

  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .achievements-grid {
    grid-template-columns: 1fr;
  }
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: var(--surface);
  border-radius: 12px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
  border: 1px solid var(--surface-lighter);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px 24px 0 24px;
  border-bottom: 1px solid var(--surface-lighter);
  margin-bottom: 24px;
}

.modal-title {
  font-size: 20px;
  font-weight: bold;
  color: var(--text-primary);
  margin: 0;
}

.modal-close {
  background: none;
  border: none;
  font-size: 24px;
  color: var(--text-muted);
  cursor: pointer;
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: all 0.2s;
}

.modal-close:hover {
  background-color: var(--surface-light);
  color: var(--text-primary);
}

.modal-body {
  padding: 0 24px 24px 24px;
}

.form-group {
  margin-bottom: 20px;
}

.form-label {
  display: block;
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.form-input {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid var(--surface-lighter);
  border-radius: 8px;
  font-size: 14px;
  background-color: var(--surface);
  color: var(--text-primary);
  transition: border-color 0.2s;
}

.form-input:focus {
  outline: none;
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgba(106, 122, 90, 0.1);
}

.modal-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid var(--surface-lighter);
}

.btn-save {
  background-color: var(--primary);
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-save:hover {
  background-color: var(--secondary);
}

.btn-cancel {
  background-color: var(--surface);
  color: var(--text-primary);
  border: 1px solid var(--surface-lighter);
  padding: 12px 24px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-cancel:hover {
  background-color: var(--surface-light);
}

/* Danger (destructive action) button */
.btn-danger {
  background-color: var(--error);
  color: #fff;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-danger:hover {
  background-color: #c82333;
}

.btn-danger:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Dark mode adjustments for modal */
[data-theme="dark"] .modal-overlay {
  background-color: rgba(0, 0, 0, 0.7);
}

[data-theme="dark"] .form-input:focus {
  box-shadow: 0 0 0 3px rgba(141, 175, 155, 0.2);
}

/* Avatar Modal Styles */
.avatar-modal {
  max-width: 400px;
}

.avatar-preview {
  display: flex;
  justify-content: center;
  margin-bottom: 24px;
}

.preview-avatar {
  width: 120px;
  height: 120px;
  background-color: var(--surface-light);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 48px;
  font-weight: bold;
  color: var(--text-muted);
  position: relative;
  overflow: hidden;
}

.preview-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 50%;
}

.preview-initials {
  font-size: 48px;
  font-weight: bold;
  color: var(--text-muted);
}

.avatar-options {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.option-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 16px 24px;
  border: 2px solid var(--surface-lighter);
  border-radius: 8px;
  background: var(--surface);
  color: var(--text-primary);
  cursor: pointer;
  font-size: 16px;
  font-weight: 500;
  transition: all 0.2s;
}

.option-btn:hover {
  background: var(--surface-light);
  border-color: var(--primary);
}

.upload-btn {
  border-color: var(--primary);
  background: var(--surface);
}

.upload-btn:hover {
  background: var(--primary);
  color: white;
}

.default-btn {
  border-color: var(--surface-lighter);
  background: var(--surface);
}

.default-btn:hover {
  background: var(--surface-light);
  border-color: var(--text-muted);
}

.btn-icon {
  font-size: 18px;
}

/* Success Toast Notification */
.success-toast {
  position: fixed;
  bottom: 24px;
  right: 24px;
  background-color: var(--surface);
  color: var(--text-primary);
  padding: 16px 20px;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
  display: flex;
  align-items: center;
  gap: 12px;
  z-index: 1001;
  animation: slideInRight 0.3s ease-out;
  max-width: 300px;
  border: 1px solid var(--surface-lighter);
}

.toast-icon {
  background-color: var(--success);
  color: white;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: bold;
  flex-shrink: 0;
}

.toast-message {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
}

@keyframes slideInRight {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

/* Dark mode adjustments for toast shadow */
[data-theme="dark"] .success-toast {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.5);
}

/* Mobile responsiveness */
@media (max-width: 768px) {
  .success-toast {
    bottom: 16px;
    right: 16px;
    left: 16px;
    max-width: none;
  }
}
</style>
