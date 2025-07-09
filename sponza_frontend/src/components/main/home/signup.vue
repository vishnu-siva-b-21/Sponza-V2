<script setup>
	import axios from 'axios';
	import Swal from 'sweetalert2';
	import { ref,reactive } from 'vue';

	const signup_active_tab = ref("Influencer");

	const spn_signup = reactive({
  role:"sponsor",
	spn_company:"",
	spn_email: "",
  spn_industry: "",
	spn_password: "",
	spn_con_password: "",
	});

	const spn_signup_error = reactive({
		spn_company: "",
		spn_email: "",
    spn_industry: "",
		spn_password: "",
		spn_con_password: "",
	});

	const inf_signup = reactive({
  role:"influencer",
	inf_uname: "",
	inf_email: "",
	inf_niche: "",
	inf_password: "",
	inf_con_password: "",
	inf_platform: "",
	inf_platform_link: "",
	});

	const inf_signup_error = reactive({
	inf_uname: "",
	inf_email: "",
	inf_niche: "",
	inf_password: "",
	inf_con_password: "",
	inf_platform: "",
	inf_platform_link: "",
	});

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
  }

  // const spnValidateForm = () => {
  // let isValid = true;

  // // Reset errors
  // spn_signup_error.spn_company = "";
  // spn_signup_error.spn_email = "";
  // spn_signup_error.spn_password = "";

  // // Role validation
  // if (!spn_signup.spn_company) {
  //     spn_signup_error.spn_company = "Company Name is required";
  //     isValid = false;
  // }

  // // Spn_email validation
  // if (!spn_signup.spn_email) {
  //     spn_signup_error.spn_email = "Email cannot be empty.";
  //     isValid = false;
  // } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(spn_signup.spn_email)) {
  //     spn_signup_error.spn_email = "Please enter a valid email address.";
  //     isValid = false;
  // }

  // if (!spn_signup.spn_industry) {
  //     spn_signup_error.spn_industry = "Industry is required";
  //     isValid = false;
  // }

  // // Spn_password validation
  // if (!spn_signup.spn_password) {
  //     spn_signup_error.spn_password = "Password is required";
  //     isValid = false;
  // }

  // if (!spn_signup.spn_con_password) {
  //     spn_signup_error.spn_con_password = "Confirm Password is required";
  //     isValid = false;
  // }

  // return isValid;
  // };

  const spnValidateForm = async () => {
  let isValid = true;

  // Reset errors
  spn_signup_error.spn_company = "";
  spn_signup_error.spn_email = "";
  spn_signup_error.spn_industry = "";
  spn_signup_error.spn_password = "";
  spn_signup_error.spn_con_password = "";

  // Role validation (if needed)
  if (!spn_signup.spn_company) {
    spn_signup_error.spn_company = "Company Name is required";
    isValid = false;
  }

  // Spn_email validation
  if (!spn_signup.spn_email) {
    spn_signup_error.spn_email = "Email cannot be empty.";
    isValid = false;
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(spn_signup.spn_email)) {
    spn_signup_error.spn_email = "Please enter a valid email address.";
    isValid = false;
  } else {
    try {
      const response = await fetch("http://127.0.0.1:5000/get-all-users/sponsor", {
        method: "GET",
      });
      const data = await response.json();
      if (data.includes(spn_signup.spn_email)) {
        spn_signup_error.spn_email = "Email address already taken.";
        isValid = false;
      }
    } catch (error) {
      console.error("Error fetching users:", error);
      isValid = false;
    }
  }

  // Spn_industry validation
  if (!spn_signup.spn_industry) {
    spn_signup_error.spn_industry = "Industry is required";
    isValid = false;
  }

  // Spn_password validation
  if (!spn_signup.spn_password) {
    spn_signup_error.spn_password = "Password is required";
    isValid = false;
  } else if (spn_signup.spn_password.length < 8) {
    spn_signup_error.spn_password = "Password must be at least 8 characters long.";
    isValid = false;
  } else if (!/[A-Z]/.test(spn_signup.spn_password)) {
    spn_signup_error.spn_password = "Password must contain at least one uppercase letter.";
    isValid = false;
  } else if (!/[a-z]/.test(spn_signup.spn_password)) {
    spn_signup_error.spn_password = "Password must contain at least one lowercase letter.";
    isValid = false;
  } else if (!/\d/.test(spn_signup.spn_password)) {
    spn_signup_error.spn_password = "Password must contain at least one digit.";
    isValid = false;
  } else if (!/[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(spn_signup.spn_password)) {
    spn_signup_error.spn_password = "Password must contain at least one special character.";
    isValid = false;
  }

  // Spn_con_password validation
  if (!spn_signup.spn_con_password) {
    spn_signup_error.spn_con_password = "Confirm Password is required";
    isValid = false;
  } else if (spn_signup.spn_password !== spn_signup.spn_con_password) {
    spn_signup_error.spn_con_password = "Passwords do not match";
    isValid = false;
  }

  return isValid;
};
  const spnSignUp = async () => {
    let valid = await spnValidateForm();
    if (!valid) return;

  try {
      const response = await axios.post("http://127.0.0.1:5000/register", spn_signup);
      const data = response.data;
      if (data.status === "success") {
      Swal.fire({
          icon: 'success',
          title: 'Success',
          text: data.message,
          confirmButtonText: 'Okay'
      }).then(() => {
      window.location.reload();;
    });} else {
      Swal.fire({
          icon: 'error',
          title: 'Error',
          text: data.message,
          confirmButtonText: 'Okay'
      });
      }
  } catch (error) {
      Swal.fire({
      icon: 'error',
      title: 'Oops...',
      text: error.response?.data?.message || 'An error occurred during registration. Please try again.',
      confirmButtonText: 'Okay'
      });
  }
  };


  const infValidateForm = async () => {
    let isValid = true;


    inf_signup_error.inf_uname = "";
    inf_signup_error.inf_email = "";
    inf_signup_error.inf_niche = "";
    inf_signup_error.inf_password = "";
    inf_signup_error.inf_platform= "";
    inf_signup_error.inf_con_password = "";
    inf_signup_error.inf_platform_link = "";

    if (!inf_signup.inf_uname) {
      inf_signup_error.inf_uname = "Username is required";
      isValid = false;
    } else if (!/^[A-Za-z]{4,20}$/.test(inf_signup.inf_uname)) {
      inf_signup_error.inf_uname = "Enter a valid Username";
      isValid = false;
    }
    if (!inf_signup.inf_email) {
      inf_signup_error.inf_email = "Email is required.";
      isValid = false;
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(inf_signup.inf_email)) {
      inf_signup_error.inf_email = "Enter a valid email address.";
      isValid = false;
    } else {
      try {
        const response = await fetch("http://127.0.0.1:5000/get-all-users/influencer", { method: "GET" });
        const data = await response.json();
        if (data.includes(inf_signup.inf_email)) {
          inf_signup_error.inf_email = "Email address already taken.";
          isValid = false;
        }
      } catch (error) {
        console.error("Error fetching users:", error);
        isValid = false;
      }
    }
    if (!inf_signup.inf_niche) {
      inf_signup_error.inf_niche = "Niche is required";
      isValid = false;
    } else if (!/^[A-Za-z]{4,30}$/.test(inf_signup.inf_niche)) {
      inf_signup_error.inf_niche = "Enter a valid Niche";
      isValid = false;
    }
    if (!inf_signup.inf_password) {
      inf_signup_error.inf_password = "Password is required";
      isValid = false;
    } else if (inf_signup.inf_password.length < 8) {
      inf_signup_error.inf_password = "Password must be at least 8 characters long.";
      isValid = false;
    } else if (!/[A-Z]/.test(inf_signup.inf_password)) {
      inf_signup_error.inf_password = "Password must contain at least one uppercase letter.";
      isValid = false;
    } else if (!/[a-z]/.test(inf_signup.inf_password)) {
      inf_signup_error.inf_password = "Password must contain at least one lowercase letter.";
      isValid = false;
    } else if (!/\d/.test(inf_signup.inf_password)) {
      inf_signup_error.inf_password = "Password must contain at least one digit.";
      isValid = false;
    } else if (!/[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(inf_signup.inf_password)) {
      inf_signup_error.inf_password = "Password must contain at least one special character.";
      isValid = false;
    }

    if (!inf_signup.inf_con_password) {
      inf_signup_error.inf_con_password = "Confirm password is required";
      isValid = false;
    } else if (inf_signup.inf_password !== inf_signup.inf_con_password) {
      inf_signup_error.inf_con_password = "Passwords do not match";
      isValid = false;
    }

    if (!inf_signup.inf_platform) {
      inf_signup_error.inf_platform_link = "Select any one";
      isValid = false;
    } else {
      if (!inf_signup.inf_platform_link) {
        inf_signup_error.inf_platform_link = `${inf_signup.inf_platform.charAt(0).toUpperCase() + inf_signup.inf_platform.slice(1)} Link is required`;
        isValid = false;
      }
    }
    return isValid;

  };
  
  const infSignUp = async () => {
  let valid = await infValidateForm();
  if (!valid) return;

  try {
      const response = await axios.post("http://127.0.0.1:5000/register", inf_signup);
      const data = response.data;
      if (data.status === "success") {
      Swal.fire({
          icon: 'success',
          title: 'Success',
          text: data.message,
          confirmButtonText: 'Okay'
      }).then(() => {
      window.location.reload();;
    });} else {
      Swal.fire({
          icon: 'error',
          title: 'Error',
          text: data.message,
          confirmButtonText: 'Okay'
      });
      }
  } catch (error) {
      Swal.fire({
      icon: 'error',
      title: 'Oops...',
      text: error.response?.data?.message || 'An error occurred during registration. Please try again.',
      confirmButtonText: 'Okay'
      });
  }
  };
</script>

<template>
    <section class="signup-section">
        <div class="tab">
			<button
			class="tablink influencer"
			:class="{ active: signup_active_tab === 'Influencer' }"
			@click="signup_active_tab = 'Influencer'">Influencer</button>

			<button
			class="tablink sponsor"
			:class="{ active: signup_active_tab === 'Sponsor' }"
			@click="signup_active_tab = 'Sponsor'">Sponsor</button>
		</div>

	<form v-if="signup_active_tab === 'Influencer'" @submit.prevent="infSignUp" id="InfluencerForm">
		<div class="form-row">
			<input type="text" id="influencer-username" class="input-text" 
			v-model="inf_signup.inf_uname"
			placeholder="Username"
			:class="{ error: inf_signup_error.inf_uname }">
			<span id="influencer-username-error" class="error-message" v-if="inf_signup_error.inf_uname">{{ inf_signup_error.inf_uname }}</span>
		</div>
		<div class="form-row">
			<input type="email" id="influencer-email" 
			v-model="inf_signup.inf_email"
			class="input-text" placeholder="Email"
			:class="{ error: inf_signup_error.inf_email }">
			<span id="influencer-email-error" class="error-message" v-if="inf_signup_error.inf_email">{{ inf_signup_error.inf_email }}</span>
		</div>
		<div class="form-row">
			<input type="text" id="influencer-niche" 
			v-model="inf_signup.inf_niche"
			class="input-text" placeholder="Niche"
			:class="{ error: inf_signup_error.inf_niche }">
			<span id="influencer-niche-error" class="error-message" v-if="inf_signup_error.inf_niche">{{ inf_signup_error.inf_niche }}</span>
		</div>
		<div class="form-row">
			<div class="input-container">
				<input type="password" id="influencer-password" 
				v-model="inf_signup.inf_password"
				class="input-text"
					placeholder="Password"
					:class="{ error: inf_signup_error.inf_password }">
				<span class="eye-toggle" 
				@click="togglePasswordVisibility('influencer-password', $event)">
					<i id="eye-icon-password" class="fas fa-eye-slash"></i>
				</span>
			</div>
			<span id="influencer-password-error" class="error-message" v-if="inf_signup_error.inf_password">{{ inf_signup_error.inf_password }}</span>
		</div>
		<div class="form-row">
			<div class="input-container">
				<input type="password" id="influencer-confirm-password" class="input-text"
					v-model="inf_signup.inf_con_password"
					placeholder="Confirm Password"
					:class="{ error: inf_signup_error.inf_con_password }">
				<span class="eye-toggle"
				@click="togglePasswordVisibility('influencer-confirm-password', $event)">
					<i id="eye-icon-confirm-password" class="fas fa-eye-slash"></i>
				</span>
			</div>
			<span id="influencer-confirm-password-error" class="error-message" v-if="inf_signup_error.inf_con_password">{{ inf_signup_error.inf_con_password }}</span>
		</div>
		<div class="form-row">
    <div class="platform-icons" id="platform-icons">
      <!-- YouTube Platform -->
      <div class="platform-row">
        <input
          type="radio"
          class="checkbox"
          id="youtube-checkbox"
          name="platform"
          v-model="inf_signup.inf_platform"
          value="youtube"
        />
        <i class="fab fa-youtube"></i>
        <input
          v-if="inf_signup.inf_platform === 'youtube'"
          type="text"
          placeholder="Enter your YouTube URL"
          class="url-input"
          name="inf_social_media_link"
          v-model="inf_signup.inf_platform_link"
          :class="{ error: inf_signup_error.inf_platform_link }"
        />
      </div>

      <!-- Twitter Platform -->
      <div class="platform-row">
        <input
          type="radio"
          class="checkbox"
          id="twitter-checkbox"
          name="platform"
          v-model="inf_signup.inf_platform"
          value="twitter"
        />
        <i class="fa-brands fa-twitter"></i>
        <input
          v-if="inf_signup.inf_platform === 'twitter'"
          type="text"
          placeholder="Enter your Twitter profile link"
          class="url-input"
          name="inf_social_media_link"
          v-model="inf_signup.inf_platform_link"
		  :class="{ error: inf_signup_error.inf_platform_link }"
        />
      </div>

      <!-- Instagram Platform -->
      <div class="platform-row">
        <input
          type="radio"
          class="checkbox"
          id="instagram-checkbox"
          name="platform"
          v-model="inf_signup.inf_platform"
          value="instagram"
        />
        <i class="fab fa-instagram"></i>
        <input
          v-if="inf_signup.inf_platform === 'instagram'"
          type="text"
          placeholder="Enter your Instagram profile link"
          class="url-input"
          name="inf_social_media_link"
          v-model="inf_signup.inf_platform_link"
		  :class="{ error: inf_signup_error.inf_platform_link }"
        />
      </div>
    </div>

    <!-- Error Message -->
    <span
      id="influencer-platform-error"
      class="error-message"
      v-if="inf_signup_error.inf_platform_link"
    >
      {{ inf_signup_error.inf_platform_link }}
    </span>
  </div>
		<div class="form-row-last">
			<input type="submit" class="register" value="Register">
		</div>

	</form>

	<form v-if="signup_active_tab === 'Sponsor'" @submit.prevent="spnSignUp" id="SponsorForm">
		<div class="form-row">
			<input type="text" id="sponsor-companyname" class="input-text" v-model="spn_signup.spn_company"
			placeholder="Company Name"
			:class="{ error: spn_signup_error.spn_company }">
			<span id="sponsor-companyname-error" class="error-message" v-if="spn_signup_error.spn_company">{{ spn_signup_error.spn_company }}</span>
		</div>
    <div class="form-row">
			<input type="text" id="sponsor-industry" class="input-text" v-model="spn_signup.spn_industry"
			placeholder="Industry"
			:class="{ error: spn_signup_error.spn_industry }">
			<span id="sponsor-industry-error" class="error-message" v-if="spn_signup_error.spn_industry">{{ spn_signup_error.spn_industry }}</span>
		</div>
		<div class="form-row">
			<input type="email" id="sponsor-email" class="input-text" 
			v-model="spn_signup.spn_email"
			placeholder="Email" :class="{ error: spn_signup_error.spn_email }">
			<span id="sponsor-email-error" class="error-message" v-if="spn_signup_error.spn_email"> {{ spn_signup_error.spn_email }}</span>
		</div>
		<div class="form-row">
			<div class="input-container">
				<input type="password" id="sponsor-password" class="input-text"
				v-model="spn_signup.spn_password" 
				placeholder="Password"
				:class="{ error: spn_signup_error.spn_password }">
				<span class="eye-toggle" @click="togglePasswordVisibility('sponsor-password', $event)">
					<i id="eye-icon-password" class="fas fa-eye-slash"></i>
				</span>
			</div>
			<span id="sponsor-password-error" class="error-message" v-if="spn_signup_error.spn_password">{{ spn_signup_error.spn_password }}</span>
		</div>
		<div class="form-row">
			<div class="input-container">
				<input type="password" id="sponsor-confirm-password" class="input-text" 
				v-model="spn_signup.spn_con_password"
				placeholder="Confirm Password"
				:class="{ error: spn_signup_error.spn_con_password }">
				<span class="eye-toggle"
				@click="togglePasswordVisibility('sponsor-confirm-password', $event)">
					<i id="eye-icon-confirm-password" class="fas fa-eye-slash"></i>
				</span>
			</div>
			<span id="sponsor-confirm-password-error" class="error-message" v-if="spn_signup_error.spn_con_password">{{ spn_signup_error.spn_con_password }}</span>
		</div>
		<div class="form-row-last">
			<input type="submit" class="register" value="Register">
		</div>

	</form>
</section>
</template>

