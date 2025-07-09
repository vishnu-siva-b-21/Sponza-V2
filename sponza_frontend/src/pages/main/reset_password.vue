<script setup>
import "../../static/main/styles/reset_password.css"; 
import axios from "axios";
import { ref, onMounted } from "vue";
import Swal from "sweetalert2";

const isLoading = ref(false);
const password = ref("");
const confirmPassword = ref("");
const passwordError = ref("");
const confirmPasswordError = ref("");
const role = ref("");
const token = ref("");

const minLengthRegex = /.{8,}/;
const uppercaseRegex = /[A-Z]/;
const lowercaseRegex = /[a-z]/;
const digitRegex = /\d/;
const symbolRegex = /[@$!%*?&]/;

onMounted(() => {
  const urlParams = new URLSearchParams(window.location.search);
  role.value = urlParams.get("role");
  token.value = urlParams.get("token");

  const newUrl = window.location.origin + window.location.pathname;
  window.history.replaceState({}, document.title, newUrl); 
});

const validatePassword = (value) => {
  if (!minLengthRegex.test(value)) {
    passwordError.value = "Password must be at least 8 characters long."
    return false;
  }
  if (!uppercaseRegex.test(value)) {
    passwordError.value = "Password must contain at least 1 uppercase letter."
    return false;
  }
  if (!lowercaseRegex.test(value)) {
    passwordError.value = "Password must contain at least 1 lowercase letter."
    return false;
  }
  if (!digitRegex.test(value)) {
    passwordError.value = "Password must contain at least 1 digit."
    return false;
  }
  if (!symbolRegex.test(value)) {
    passwordError.value = "Password must contain at least 1 symbol."
    return false;
  }
  return true;
};

const resetPassword = async () => {
  if (password.value.trim() === "") {
    document.getElementById("password").classList.add('error');
    passwordError.value = "Password cannot be empty"
    return;
  }

  if (!validatePassword(password.value)) {
    document.getElementById("password").classList.add('error');
    return; 
  }


  document.getElementById("password").classList.remove('error');
  passwordError.value = ""

  if (confirmPassword.value.trim() === ""){
    document.getElementById("confirm_password").classList.add('error');
    confirmPasswordError.value = "Confirm Password cannot be empty"
    return;
  } 

  if (password.value !== confirmPassword.value) {
    document.getElementById("password").classList.remove('error');
    document.getElementById("confirm_password").classList.add('error');
    confirmPasswordError.value = "Passwords do not match!"
    return;
  }

  document.getElementById("confirm_password").classList.remove('error');
  confirmPasswordError.value = ""
  isLoading.value = true;
  try {
    const response = await axios.post(`http://127.0.0.1:5000/user-reset-password/${role.value}/${token.value}`, {
      password: password.value.trim(),
    });

    if (response.data.success) {
      Swal.fire("Success", "Your Password updated successfully, you can now login with your new password", "success").then(() => {
        window.location.href = "/"; // Redirect to home
      });
    } else {
      Swal.fire("Error", response.data.message || "Failed to update password", "error");
    }
  } catch (error) {
    console.error("Error resetting password:", error);
    Swal.fire("Error", "An error occurred while resetting the password.", "error");
  } finally {
    isLoading.value = false;
  }
};

const togglePasswordVisibility = (inputId, event) => {
  const passwordInput = document.getElementById(inputId);
  const eyeIcon = event.target;

  if (passwordInput.type === "password") {
    passwordInput.type = "text";
    eyeIcon.classList.remove("fa-eye-slash");
    eyeIcon.classList.add("fa-eye");
  } else {
    passwordInput.type = "password";
    eyeIcon.classList.remove("fa-eye");
    eyeIcon.classList.add("fa-eye-slash");
  }
};
</script>

<template>
  <div class="container profile-container">
    <div v-if="isLoading" class="loading-overlay">
      <div class="spinner"></div>
    </div>

    <form class="profile-form" @submit.prevent="resetPassword">
      <h3>
        Reset Password
        <hr />
      </h3>
      <label for="password">New Password</label>
      <div class="input-container">
        <input
          type="password"
          v-model="password"
          id="password"
          placeholder="Enter new password"
        />
        <i @click="togglePasswordVisibility('password', $event)" class="fas fa-eye-slash toggle-password" id="togglePassword"></i>
        <div v-if="passwordError" class="error-message">{{ passwordError }}</div>
      </div>
      

      <label for="confirm_password">Confirm New Password</label>
      <div class="input-container">
        <input
          type="password"
          v-model="confirmPassword"
          id="confirm_password"
          placeholder="Confirm new password"
        />
        <i @click="togglePasswordVisibility('confirm_password', $event)" class="fas fa-eye-slash toggle-password" id="toggleConfirmPassword"></i>
        <div v-if="confirmPasswordError" class="error-message">{{ confirmPasswordError }}</div>
      </div>
      <button class="reset" type="submit">Reset</button>
    </form>
  </div>
</template>

<style scoped>
.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5); 
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9999; 
}

.spinner {
  border: 8px solid rgba(255, 255, 255, 0.3); 
  border-top: 8px solid #ffffff;
  border-radius: 50%;
  width: 60px;
  height: 60px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}
</style>
