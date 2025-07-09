<script setup>
import axios from "axios";
import Swal from "sweetalert2";
import { reactive ,ref} from "vue";
import { useRouter } from "vue-router";


const router = useRouter();
const isLoading = ref(false);

const signin = reactive({
  email: "",
  password: "",
  role: "",
});

const signin_error = reactive({
  role: "",
  email: "",
  password: "",
});

const validateForm = () => {
  let isValid = true;
  signin_error.role = "";
  signin_error.email = "";
  signin_error.password = "";

  if (!signin.role) {
    signin_error.role = "Role is required";
    isValid = false;
  }

  if (!signin.email) {
    signin_error.email = "Email cannot be empty.";
    isValid = false;
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(signin.email)) {
    signin_error.email = "Please enter a valid email address.";
    isValid = false;
  }

  if (!signin.password) {
    signin_error.password = "Password is required";
    isValid = false;
  }

  return isValid;
};

const signIn = async () => {
  if (!validateForm()) return;

  try {
    const response = await axios.post("http://127.0.0.1:5000/login", signin);
    const data = response.data;
    if (data.status === "success") {
      localStorage.setItem("accessToken", data.tokens.access_token);
      localStorage.setItem("refreshToken", data.tokens.refresh_token);
      localStorage.setItem("userRole", signin.role);

        switch (signin.role) {
          case "admin":
            window.location.href = "/admin/dashboard/?login=success";
            break;
          case "influencer":
            window.location.href = "/inf/dashboard/?login=success";
            break;
          case "sponsor":
            window.location.href = "/spn/dashboard/?login=success";
            break;
        }
    } else {
      Swal.fire({
        icon: "error",
        title: "Login Failed",
        text: data.message,
        confirmButtonText: "Okay",
      });
    }
  } catch (error) {
    Swal.fire({
      icon: "error",
      title: "Oops...",
      text:
        error.response?.data?.message ||
        "An error occurred during login. Please try again.",
      confirmButtonText: "Okay",
    });
  }
};

function showForgotPasswordPopup() {
  const signin_email = signin.email;
  Swal.fire({
    title: "Forgot Password",
    html: `
      <p>Please enter your email address to reset your password.</p>
      <input type="email" id="email" class="swal2-input" placeholder="Enter your email address" aria-label="Enter your email address" value=${signin_email || ""}>
      <br>
    `,
    icon: "info",
    showCancelButton: true,
    confirmButtonText: "Submit",
    customClass: {
      popup: "animated fadeInDown"
    },
    preConfirm: () => {
      const role = signin.role;
      const email = Swal.getPopup().querySelector("#email").value;

      if (!email) {
        Swal.showValidationMessage("Please enter your email address");
      } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
        Swal.showValidationMessage("Please enter a valid email address");
      } else if (!role) {
        Swal.showValidationMessage("Please select a role");
      }
      return {
        email: email,
        role: role
      };
    }
  }).then((result) => {
    if (result.isConfirmed) {
      isLoading.value = true;
      const data = result.value;
      
      axios.post("http://127.0.0.1:5000/user-reset-request", data)
        .then((response) => {
          isLoading.value = false;
          if (response.data.message) {
            Swal.fire({
              title: "Success",
              text: response.data.message,
              icon: "success",
              confirmButtonText: "OK",
              willClose: () => {
                location.reload();
              }
            });
          } else {
            Swal.fire({
              title: "Error",
              text: response.data.error || "Unexpected error occurred",
              icon: "error"
            });
          }
        })
        .catch((error) => {
          isLoading.value = false;
          console.error("Error:", error);
          Swal.fire({
            title: "Error",
            text: "There was an error sending the password reset request",
            icon: "error"
          });
        });
    }
  });
}

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
        <div v-if="isLoading" class="loading-overlay">
      <div class="spinner"></div>
    </div>
  <section class="signin-section">
    <form @submit.prevent="signIn" id="signin">
      <div class="form-row">
        <select
          id="role"
          class="input-text select"
          v-model="signin.role"
          :class="{ error: signin_error.role }"
        >
          <option value="">Select Role</option>
          <option value="admin">Admin</option>
          <option value="influencer">Influencer</option>
          <option value="sponsor">Sponsor</option>
        </select>
        <span
          id="role-error"
          class="error-message"
          v-if="signin_error.role"
          >{{ signin_error.role }}</span
        >
      </div>
      <div class="form-row">
        <input
          type="email"
          v-model="signin.email"
          id="signin-email"
          class="input-text"
          :class="{ error: signin_error.email }"
          placeholder="Email"
        />
        <span
          id="signin-email-error"
          class="error-message"
          v-if="signin_error.email"
          >{{ signin_error.email }}</span
        >
      </div>
      <div class="form-row">
        <div class="input-container">
          <input
            type="password"
            v-model="signin.password"
            id="signin-password"
            class="input-text"
            :class="{ error: signin_error.password }"
            placeholder="Password"
          />
          <span
            class="eye-toggle"
            @click="togglePasswordVisibility('signin-password', $event)"
          >
            <i id="eye-icon" class="fas fa-eye-slash"></i>
          </span>
        </div>
        <span
          id="signin-password-error"
          class="error-message"
          v-if="signin_error.password"
          >{{ signin_error.password }}</span
        >
      </div>
      <div class="form-row">
        <a style="text-decoration: underline; cursor: pointer;"  v-if="signin.role == 'influencer' || signin.role =='sponsor'" id="forget-password" class="forget-password" @click="showForgotPasswordPopup"
        >Forget Password?</a>
      </div>

      <div class="form-row submit">
        <input type="submit" class="signin" value="Sign In" />
      </div>
    </form>
  </section>
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
