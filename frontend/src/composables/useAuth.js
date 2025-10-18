import { onAuthStateChanged, signOut } from "firebase/auth";
import { doc, onSnapshot } from "firebase/firestore";
import { computed, ref } from "vue";
import { auth, db } from "@/lib/firebase";

const _user = ref(null);
const _userProfile = ref(null);
const _loading = ref(true);

// listen to auth state changes
let unsubscribe = null;
let unsubscribeProfile = null;

async function loadUserProfile(firebaseUser) {
  if (unsubscribeProfile) {
    unsubscribeProfile();
    unsubscribeProfile = null;
  }

  try {
    const docRef = doc(db, "users", firebaseUser.uid);

    unsubscribeProfile = onSnapshot(
      docRef,
      (snapshot) => {
        _userProfile.value = snapshot.exists() ? snapshot.data() : null;
      },
      (error) => {
        console.log("error fetching user profile: ", error);
        _userProfile.value = null;
      }
    );
  } catch (error) {
    console.log("error setting up user profile listener: ", error);
    _userProfile.value = null;
  }
}

if (!unsubscribe) {
  unsubscribe = onAuthStateChanged(auth, async (firebaseUser) => {
    _loading.value = true;

    if (firebaseUser) {
      // store firebase auth details
      _user.value = firebaseUser;
      // fetch firestore user details
      await loadUserProfile(firebaseUser);
    } else {
      _user.value = null;
      _userProfile.value = null;
      if (unsubscribeProfile) {
        unsubscribeProfile();
        unsubscribeProfile = null;
      }
    }

    _loading.value = false;
  });
}

export function useAuth() {
  const user = computed(() => _user.value);
  const userProfile = computed(() => _userProfile.value);
  const loading = computed(() => _loading.value);
  const isAuthed = computed(() => !!_user.value);

  async function logout() {
    try {
      await signOut(auth);
    } catch (error) {
      console.error("error signing out:", error);
    }
  }

  return { user, userProfile, loading, isAuthed, logout };
}
