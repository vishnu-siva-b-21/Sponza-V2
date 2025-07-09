<script setup>
import '../../static/main/styles/home.css';
import Swal from 'sweetalert2';
import { onMounted, ref } from 'vue';

import API from "@/router/axios";

import SignIn from '../../components/main/home/signin.vue';
import SignUp from '../../components/main/home/signup.vue';

const loading = ref(false);
const main_active_tab = ref("signin");

onMounted(() => {
  const urlParams = new URLSearchParams(window.location.search);
  if (urlParams.get("logout") === "success") {
    Swal.fire({
      title: "Logout Successful!",
      text: "You have been successfully logged out.",
      icon: "success",
      confirmButtonText: "OK",
    });

    const newUrl = window.location.origin + window.location.pathname;
    window.history.replaceState({}, document.title, newUrl);
  }
});

onMounted(async () => {
  const token = localStorage.getItem("accessToken"); 
  if (token) {
    try {
      const response = await API.get("http://127.0.0.1:5000/check-auth", {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      const data = response.data;

      if (data.status === "authenticated") {
        window.location.href = data.redirect_url + "/?authenticated=success";
      } else if (data.status === "unauthenticated") {
        console.log("User not authenticated. Staying on the home page.");
      } else if (data.status === "warning") {
        Swal.fire({
          icon: 'warning',
          title: 'Warning',
          text: data.message,
          confirmButtonText: 'Okay',
        });
      }
    } catch (error) {
      Swal.fire({
        icon: 'error',
        title: 'Oops...',
        text:
          error.response?.data?.message ||
          'An error occurred while checking authentication. Please try again.',
        confirmButtonText: 'Okay',
      });
    }
  } else {
    console.log("No access token found. User is not logged in.");
  }
});

</script>


<template>
  <div class="home">
    <div v-show="loading" class="loading-screen" id="loadingScreen">
      Sending the Mail...
    </div>
    <div class="page-content">
      <div class="form-left"></div>
      <div class="form-right">
        <div class="tab">
          <button
            class="tablink signin"
            :class="{ active: main_active_tab === 'signin' }"
            @click="main_active_tab = 'signin'"
          >
            Sign In
          </button>
          <button
            class="tablink register"
            :class="{ active: main_active_tab === 'signup' }"
            @click="main_active_tab = 'signup'"
          >
            Sign Up
          </button>
        </div>
        <SignIn v-if="main_active_tab === 'signin'" />
        <SignUp v-if="main_active_tab === 'signup'" />
      </div>
    </div>
  </div>
</template>
