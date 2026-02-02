import { initializeApp } from "https://www.gstatic.com/firebasejs/10.12.2/firebase-app.js";
import {
  getAuth,
  createUserWithEmailAndPassword,
  signInWithEmailAndPassword,
  signOut,
  onAuthStateChanged,
} from "https://www.gstatic.com/firebasejs/10.12.2/firebase-auth.js";

const statusText = document.getElementById("auth-status-text");
const loginForm = document.getElementById("login-form");
const signupForm = document.getElementById("signup-form");

function setStatus(message) {
  if (statusText) {
    statusText.textContent = message;
  }
}

if (!window.__FIREBASE_READY__) {
  setStatus("Firebase Auth not configured. Set web config env vars to enable.");
} else {
  const app = initializeApp(window.__FIREBASE_CONFIG__);
  const auth = getAuth(app);

  onAuthStateChanged(auth, (user) => {
    if (user) {
      setStatus(`Signed in as ${user.email}`);
    } else {
      setStatus("Signed out");
    }
  });

  if (loginForm) {
    loginForm.addEventListener("submit", async (event) => {
      event.preventDefault();
      const email = loginForm.querySelector("input[name='email']").value;
      const password = loginForm.querySelector("input[name='password']").value;
      try {
        await signInWithEmailAndPassword(auth, email, password);
      } catch (err) {
        setStatus(`Login failed: ${err.message}`);
      }
    });
  }

  if (signupForm) {
    signupForm.addEventListener("submit", async (event) => {
      event.preventDefault();
      const email = signupForm.querySelector("input[name='email']").value;
      const password = signupForm.querySelector("input[name='password']").value;
      try {
        await createUserWithEmailAndPassword(auth, email, password);
      } catch (err) {
        setStatus(`Signup failed: ${err.message}`);
      }
    });
  }

  const logoutBtn = document.getElementById("logout-btn");
  if (logoutBtn) {
    logoutBtn.addEventListener("click", async () => {
      await signOut(auth);
    });
  }
}
