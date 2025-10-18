<template>
  <v-container class="fill-height d-flex align-center justify-center" fluid>
    <v-card width="460" elevation="8" class="pa-6 rounded-xxl text-center">
      <v-avatar size="56" class="mb-2" color="secondary" variant="tonal"
        >🐱</v-avatar
      >
      <h2 class="text-h5 font-weight-bold mb-1 text-primary">StudyBuddy</h2>
      <p class="text-body-2 mb-6" style="color: var(--text-secondary)">
        Your wellness companion for academic success
      </p>

      <!-- Segmented control (pill) -->
      <div class="segmented mb-4" role="tablist" aria-label="Auth tabs">
        <div class="thumb" :class="tab"></div>
        <button
          class="seg-btn"
          :class="{ active: tab === 'login' }"
          role="tab"
          aria-selected="tab === 'login'"
          @click="tab = 'login'"
        >
          Login
        </button>
        <button
          class="seg-btn"
          :class="{ active: tab === 'signup' }"
          role="tab"
          aria-selected="tab === 'signup'"
          @click="tab = 'signup'"
        >
          Sign Up
        </button>
      </div>

      <v-window v-model="tab">
        <!-- LOGIN -->
        <v-window-item value="login">
          <v-form @submit.prevent="submit('login')">
            <v-text-field
              v-model="email"
              label="Email"
              variant="outlined"
              density="comfortable"
              class="mb-3"
              hide-details
            />
            <v-text-field
              v-model="password"
              label="Password"
              type="password"
              variant="outlined"
              density="comfortable"
              class="mb-4"
              hide-details
            />
            <v-btn
              type="submit"
              block
              color="primary"
              size="large"
              class="text-white"
            >
              Sign In
            </v-btn>
          </v-form>
        </v-window-item>

        <!-- SIGN UP -->
        <v-window-item value="signup">
          <v-form @submit.prevent="submit('signup')">
            <v-text-field
              v-model="fullName"
              label="Full Name"
              variant="outlined"
              density="comfortable"
              class="mb-3"
              hide-details
            />
            <v-text-field
              v-model="email"
              label="Email"
              variant="outlined"
              density="comfortable"
              class="mb-3"
              hide-details
            />
            <v-text-field
              v-model="password"
              label="Password"
              type="password"
              variant="outlined"
              density="comfortable"
              class="mb-3"
              hide-details
            />
            <v-text-field
              v-model="confirm"
              label="Confirm Password"
              type="password"
              variant="outlined"
              density="comfortable"
              class="mb-4"
              hide-details
            />
            <v-btn
              type="submit"
              block
              color="primary"
              size="large"
              class="text-white"
            >
              Create Account
            </v-btn>
          </v-form>
        </v-window-item>
      </v-window>

      <!-- Error message display -->
      <v-alert
        v-if="errorMsg"
        type="error"
        variant="tonal"
        class="mt-4"
        closable
        @click:close="errorMsg = ''"
      >
        {{ errorMsg }}
      </v-alert>

      <p class="text-caption mt-4 text-disabled">
        Demo App — Use any email/password combination
      </p>
    </v-card>
  </v-container>
</template>

<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import { auth } from "@/lib/firebase";
import { api } from "@/lib/api";
import {
  createUserWithEmailAndPassword,
  signInWithEmailAndPassword,
} from "firebase/auth";

const router = useRouter();
const tab = ref("login");
const email = ref("");
const password = ref("");
const fullName = ref("");
const confirm = ref("");
const errorMsg = ref("");

// firebase errors
function getFirebaseErrorMessage(error) {
  switch (error.code) {
    // sign up errors
    case "auth/email-already-in-use":
      return "This email is already registered. Please try logging in instead.";
    case "auth/invalid-email":
      return "Please enter a valid email address.";
    case "auth/weak-password":
      return "Password should be at least 6 characters long.";
    case "auth/operation-not-allowed":
      return "Email/password accounts are not enabled.";

    // sign in errors
    case "auth/user-not-found":
      return "No account found with this email address.";
    case "auth/wrong-password":
      return "Incorrect password. Please try again.";
    case "auth/invalid-credential":
      return "Invalid email or password. Please check your credentials.";
    case "auth/user-disabled":
      return "This account has been disabled.";
    case "auth/too-many-requests":
      return "Too many failed attempts. Please try again later.";

    // general
    case "auth/network-request-failed":
      return "Network error. Please check your connection.";
    default:
      return error.message || "An unexpected error occurred. Please try again.";
  }
}

async function submit(mode) {
  // clear previous error messages
  errorMsg.value = "";

  try {
    // https://firebase.google.com/docs/auth/web/manage-users
    if (mode === "signup") {
      // check if password and confirm password are the same
      if (password.value !== confirm.value) {
        errorMsg.value = "Passwords do not match";
        return;
      }

      await createUserWithEmailAndPassword(auth, email.value, password.value);

      await api.post("/api/profile", {
        name: fullName.value,
        email: email.value,
      });
    } else {
      if (!email.value || !password.value) {
        errorMsg.value = "Please enter both email and password";
        return;
      }

      await signInWithEmailAndPassword(auth, email.value, password.value);

      await api.post("/api/auth/login");
    }

    // clear form
    email.value = "";
    password.value = "";
    fullName.value = "";
    confirm.value = "";
    errorMsg.value = "";

    router.push("/dashboard");
  } catch (err) {
    console.error("Authentication error:", err);

    // handle firebase auth errors
    if (err?.code?.startsWith("auth/")) {
      errorMsg.value = getFirebaseErrorMessage(err);
    }
    // handle api errors
    else if (err?.message) {
      errorMsg.value = err.message;
    }
    // handle other errors
    else {
      errorMsg.value = "An unexpected error occurred. Please try again.";
    }
  }
}
</script>

<style scoped>
/* page bg like the figma */
.v-container {
  background: linear-gradient(
    180deg,
    rgba(170, 196, 188, 0.22),
    rgba(215, 203, 178, 0.16)
  );
}
.v-card {
  backdrop-filter: blur(10px);
  background: #fff !important;
}

/* Segmented control (pill) */
.segmented {
  position: relative;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0;
  border-radius: 999px;
  padding: 4px;
  background: var(--surface-light);
  border: 1px solid var(--surface-lighter);
  overflow: hidden;
}
.segmented .thumb {
  position: absolute;
  top: 4px;
  left: 4px;
  width: calc(50% - 4px);
  height: calc(100% - 8px);
  border-radius: 999px;
  background: #fff;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08);
  transition: transform 0.2s ease;
}
.segmented .thumb.signup {
  transform: translateX(100%);
}

.seg-btn {
  position: relative;
  z-index: 1;
  border: 0;
  background: transparent;
  padding: 10px 0;
  font-weight: 600;
  color: var(--text-muted);
  cursor: pointer;
}
.seg-btn.active {
  color: var(--text-primary);
}
</style>
