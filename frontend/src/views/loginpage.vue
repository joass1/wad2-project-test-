<template>
  <v-container class="fill-height d-flex align-center justify-center" fluid>
    <v-card width="460" elevation="8" class="pa-6 rounded-xxl text-center">
      <v-avatar size="56" class="mb-2" color="primary" variant="tonal"
        >🐱</v-avatar
      >
      <h2 class="text-h5 font-weight-bold mb-1 text-primary">StudyBuddy</h2>
      <p class="text-body-2 mb-6" style="color: var(--text-muted)">
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
              {{ tab === "login" ? "Sign In" : "Create Account" }}
            </v-btn>
          </v-form>
          <!-- google login button -->
          <div class="my-4 d-flex align-center justify-center">
            <v-divider class="mx-2" vertical></v-divider>
            <span class="mx-2 text-caption font-weight-bold">or</span>
            <v-divider class="mx-2" vertical></v-divider>
          </div>
          <v-btn
            block
            color="white"
            class="mb-2 google-signin text-primary font-weight-bold"
            @click="onGoogleLogin"
            style="
              border: 1px solid var(--surface-lighter);
              align-items: center;
            "
          >
            <span
              style="
                display: inline-flex;
                align-items: center;
                margin-right: 10px;
              "
            >
              <!-- Google 2025 Favicon SVG logo -->
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="24"
                height="24"
                viewBox="0 0 48 48"
              >
                <circle cx="24" cy="24" r="20" fill="#fff" />
                <path
                  fill="#4285F4"
                  d="M25.15 16.37V21.42H35.61Q35.8 22.39 35.8 24Q35.8 28.06 33.11 30.39Q31.01 32.24 27.31 32.24Q23.5 32.24 20.88 29.65Q18.26 27.06 18.26 23.21Q18.26 19.11 20.86 16.58Q23.37 14.18 27 14.18Q29.68 14.18 31.29 15.34L35.61 11.46Q32.98 9.39 27 9.39Q20.43 9.39 16.49 13.68Q12.2 18.13 12.2 24Q12.2 29.85 16.67 34.27T27 39.19Q33.24 39.19 37.09 35.61Q40.8 32.03 40.8 24Q40.8 22.91 40.67 21.92Z"
                />
              </svg>
            </span>
            Sign in with Google
          </v-btn>
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
      <!-- <p class="text-caption mt-4 text-disabled">
        Demo App — Use any email/password combination
      </p> -->
    </v-card>
  </v-container>
</template>

<script setup>
import {
  createUserWithEmailAndPassword,
  signInWithEmailAndPassword,
} from "firebase/auth";
import { ref } from "vue";
import { useRouter } from "vue-router";
import { signInWithGoogle } from "@/composables/useGoogleSignIn";
import { api } from "@/lib/api";
import { auth } from "@/lib/firebase";

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

      // await api.post("/api/auth/login");
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

async function onGoogleLogin() {
  errorMsg.value = "";
  try {
    const result = await signInWithGoogle();
    const firebaseUser = result.user || auth.currentUser;
    if (firebaseUser) {
      try {
        await api.get("/api/profile");
        router.push("/dashboard");
      } catch (err) {
        // If 404, create a new profile
        if (err.response && err.response.status === 404) {
          try {
            await api.post("/api/profile", {
              name: firebaseUser.displayName,
              email: firebaseUser.email,
            });

            router.push("/dashboard");
          } catch (err) {
            console.error("Failed to create profile after Google login", err);
            errorMsg.value =
              err?.message || "Profile creation failed. Please try again.";
          }
        }
      }
    }
  } catch (e) {
    console.error("Google sign-in failed", e);
    errorMsg.value = e?.message || "Google sign-in failed. Please try again.";
  }
}
</script>

<style scoped>
/* page bg using app color scheme */
.v-container {
  background: var(--background);
  min-height: 100vh;
}
.v-card {
  backdrop-filter: blur(10px);
  background: var(--surface) !important;
  border: 1px solid var(--surface-lighter);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
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
  background: var(--primary);
  box-shadow: 0 2px 6px rgba(106, 122, 90, 0.2);
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
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
  transition: color 0.2s ease;
}
.seg-btn.active {
  color: white;
}

/* Fix input field styling issues */
.v-text-field {
  --v-field-border-opacity: 0.3;
}

.v-text-field .v-field {
  background: var(--surface-light) !important;
  border: 1px solid var(--surface-lighter) !important;
  border-radius: 8px !important;
}

.v-text-field .v-field--focused {
  border-color: var(--primary) !important;
  box-shadow: 0 0 0 2px rgba(106, 122, 90, 0.1) !important;
}

.v-text-field .v-label {
  color: var(--text-muted) !important;
  background: var(--surface) !important;
  padding: 0 4px !important;
}

.v-text-field .v-field__input {
  color: var(--text-primary) !important;
}
</style>
