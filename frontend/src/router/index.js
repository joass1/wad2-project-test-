import { createRouter, createWebHistory } from "vue-router";
import LoginPage from "@/views/LoginPage.vue";
import Dashboard from "@/views/Dashboard.vue";
import Timer from "@/views/Timer.vue";
import TaskTracker from "@/views/TaskTracker.vue";
import Profile from "@/views/Profile.vue";
import Progress from "@/views/Progress.vue";
import Checkin from "@/views/Checkin.vue";
import SocialHub from '@/views/SocialHub.vue'
import { onAuthStateChanged } from "firebase/auth";
import { auth } from "../lib/firebase";


const routes = [
  { path: "/", redirect: { name: "Login" } },
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

  if (to.meta.requiresAuth && !currentUser) {
    next({ name: "Login" }); 
  } else {
    next();
  }
});

export default router;