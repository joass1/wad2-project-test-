import { createRouter, createWebHistory } from "vue-router";
import LoginPage from "@/views/loginpage.vue";
import Dashboard from "@/views/dashboard.vue";
import Timer from "@/views/timer.vue";
import TaskTracker from "@/views/tasktracker.vue";
import Profile from "@/views/profile.vue";
import Progress from "@/views/progress.vue";
import Checkin from "@/views/checkin.vue";
import SocialHub from '@/views/socialhub.vue'
import PetPage from '@/views/petpage.vue'
import PetSelection from '@/views/PetSelection.vue'
import { onAuthStateChanged } from "firebase/auth";
import { auth } from "../lib/firebase";


const routes = [
  { path: "/", redirect: { name: "Dashboard" } },
  {
    path: "/login",
    name: "Login",
    component: LoginPage,
    meta: { requiresUnauth: true },
  },
  {
    path: "/dashboard",
    name: "Dashboard",
    component: Dashboard,
    meta: { requiresAuth: true },
  },
  {
    path: "/timer",
    name: "Timer",
    component: Timer,
    meta: { requiresAuth: true },
  },
  {
    path: "/task-tracker",
    name: "TaskTracker",
    component: TaskTracker,
    meta: { requiresAuth: true },
  },
  {
    path: "/profile",
    name: "Profile",
    component: Profile,
    meta: { requiresAuth: true },
  },
  {
    path: "/progress",
    name: "Progress",
    component: Progress,
    meta: { requiresAuth: true },
  },
  {
    path: "/checkin",
    name: "Checkin",
    component: Checkin,
    meta: { requiresAuth: true },
  },
  { path: '/social-hub',
    name: 'SocialHub', 
    component: SocialHub,
    meta: { requiresAuth: true }, 
  },
  {
    path: '/pet',
    name: 'PetPage',
    component: PetPage,
    meta: { requiresAuth: true },
  },
  {
    path: '/pet-selection',
    name: 'PetSelection',
    component: PetSelection,
    meta: { requiresAuth: true },
  },
];

const router = createRouter({ history: createWebHistory(), routes });

const getCurrentUser = () => {
  return new Promise((resolve, reject) => {
    const unsubscribe = onAuthStateChanged(
      auth,
      (user) => {
        unsubscribe();
        resolve(user);
      },
      reject
    );
  });
};

router.beforeEach(async (to, from, next) => {
  const currentUser = await getCurrentUser();

  // Redirect to login if route requires auth and user is not logged in
  if (to.meta.requiresAuth && !currentUser) {
    next({ name: "Login" });
    return;
  }

  // Redirect to login page if logged in user tries to access login
  if (to.meta.requiresUnauth && currentUser) {
    next({ name: "Dashboard" });
    return;
  }

  // Check if user has selected a pet (for logged-in users only)
  if (currentUser && to.meta.requiresAuth) {
    try {
      const token = await currentUser.getIdToken();
      const response = await fetch(`${process.env.VUE_APP_API_URL}/api/profile/pet-selection-status`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();

        if (!data.has_selected_pet && to.name !== 'PetSelection') {
          // Redirect to pet selection if they haven't selected a pet yet
          next({ name: "PetSelection" });
          return;
        }

        if (data.has_selected_pet && to.name === 'PetSelection') {
          // Redirect to dashboard if they've already selected a pet and try to access PetSelection
          next({ name: "Dashboard" });
          return;
        }
      }
    } catch (error) {
      console.error('Error checking pet selection status:', error);
      // Continue to the requested route if there's an error
    }
  }

  next();
});

export default router;