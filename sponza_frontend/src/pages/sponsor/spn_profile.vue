<script setup>
    import Base from "./spn_base.vue";
    import "../../static/sponsor/styles/sponsor_profile.css"

    import API from "@/router/axios";
    import { onMounted,ref, reactive } from 'vue';
    import Swal from "sweetalert2";

    const isLoading = ref(false);

    const userDetails = reactive({
      sponsor_id: "", 
      sponsor_name: "", 
      email: "", 
      industry: "", 
      email: "", 
      image: "",
      profile_pic: "" 
      })

    const formErrors = reactive({
      sponsor_name: "",
      industry: "",
      email: "",
      profile_pic: "",
    });
    
    const hasChanges = ref(false);

    const fetchDetails = async () => {
      try {
        const response = await API.get('/sponsor/profile');
        const data = response.data;
        Object.assign(userDetails, data);
      } catch (error) {
        console.error('Error fetching campaigns data:', error);
      }
    };

    const handleInputChange = () => {
      hasChanges.value = true;
    };

    const handleFileChange = (event) => {
      hasChanges.value = true;
      userDetails.profile_pic = event.target.files[0];
    };

    const validateForm = () => {
      let isValid = true;
      formErrors.sponsor_name = "";
      formErrors.industry = "";
      formErrors.email = "";
      formErrors.profile_pic = "";

      if (!userDetails.sponsor_name.trim()) {
        formErrors.sponsor_name = "Company name cannot be empty.";
        isValid = false;
      } else if (/\s/.test(userDetails.sponsor_name)) {
        formErrors.sponsor_name = "Company name cannot contain spaces.";
        isValid = false;
      }

      if (!userDetails.industry.trim()) {
        formErrors.industry = "Industry cannot be empty.";
        isValid = false;
      }

      const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!userDetails.email.trim()) {
        formErrors.email = "Email cannot be empty.";
        isValid = false;
      } else if (!emailPattern.test(userDetails.email)) {
        formErrors.email = "Please enter a valid email address.";
        isValid = false;
      }

      if (userDetails.profile_pic) {
        const allowedExtensions = /(\.jpg|\.jpeg|\.png)$/i;
        if (!allowedExtensions.exec(userDetails.profile_pic.name)) {
          formErrors.profile_pic =
            "Only .jpg, .jpeg, .png formats are allowed.";
          isValid = false;
        }
      }

      return isValid;
    };

    const handleSubmit = async () => {
      if (!hasChanges.value) {
        Swal.fire({
          icon: "info",
          title: "No Changes Made",
          text: "Please make some changes before submitting.",
          confirmButtonText: "OK",
        });
        return;
      }

      if (validateForm()) {
        const formData = new FormData();
        formData.append("company_name", userDetails.sponsor_name);
        formData.append("industry", userDetails.industry);
        formData.append("email", userDetails.email);
        if (userDetails.profile_pic) {
          formData.append("profile_pic", userDetails.profile_pic);
        }

        try {
          const response = await API.put("/sponsor/update-profile", formData, {
            headers: {
              "Content-Type": "multipart/form-data",
            },
          });
          if (response.data.success) {
            Swal.fire({
            icon: "success",
            title: "Profile Updated!",
            text: "",
            willClose: () => {
              window.location.reload();
            },
          });
          }
        } catch (error) {
          console.error("Error updating profile:", error);
          Swal.fire("Error", "Something went wrong.", "error");
        }

      }
    };

    const deleteProfile = async (sponsor_id) => {
      Swal.fire({
        title: "Are you sure?",
        text: "You won't be able to revert this!",
        icon: "warning",
        showCancelButton: true,
        confirmButtonColor: "#3085d6",
        cancelButtonColor: "#d33",
        confirmButtonText: "Yes"
      }).then(async (result) => {
        if (result.isConfirmed) {
          try {
            const response = await API.delete("/sponsor/delete-sponsor", {
              sponsor_id
            });

            if (response.data.message) {
              Swal.fire({
                title: "Success",
                text: response.data.message,
                icon: "success",
                confirmButtonText: "OK",
                willClose: () => {
                  localStorage.removeItem("accessToken");
                  localStorage.removeItem("refreshToken");
                  localStorage.removeItem("userRole");
                  window.location.href = "/";
                }
              });
            } else {
              Swal.fire({
                title: "Error",
                text: response.data.error || "Unknown error occurred",
                icon: "error"
              });
            }
          } catch (error) {
            console.error("Error:", error);
            Swal.fire({
              title: "Error",
              text: "There was an error sending the profile delete request",
              icon: "error"
            });
          }
        }
      });
    };

    onMounted(fetchDetails)
</script>


<template>
    <Base>
        <div v-if="isLoading" class="loading-overlay">
            <div class="spinner"></div>
        </div>

        <div class="container profile-container">
        <div class="profile-header">
          <div class="profile-img">
            <img :src="userDetails.image" />
          </div>
          <div class="profile-info">
            <h2 id="display-username">{{ userDetails.sponsor_name }}</h2>
            <p id="display-email">{{ userDetails.email }}</p>
          </div>
        </div>

        <form
          class="profile-form"
          @submit.prevent="handleSubmit"
          enctype="multipart/form-data"
          id="profile-form"
        >
          <h3>Account Info
            <hr />
          </h3>
          <label for="username">Company Name</label>
          <input
            v-model="userDetails.sponsor_name"
            type="text"
            id="username"
                    @change="handleInputChange"
          />
          <div v-if="formErrors.sponsor_name" class="error-message">
            {{ formErrors.sponsor_name }}
          </div>

          <label for="industry">Industry</label>
          <input
            v-model="userDetails.industry"
            type="text"
            id="industry"
                    @change="handleInputChange"
          />
          <div v-if="formErrors.industry" class="error-message">
            {{ formErrors.industry }}
          </div>

          <label for="email">Email</label>
          <input
            v-model="userDetails.email"
            type="email"
            id="email"
            readonly
          />
          <div v-if="formErrors.email" class="error-message">
            {{ formErrors.email }}
          </div>

          <label for="profile-pic">Update Profile Picture</label>
          <input
            type="file"
            id="profile-pic"
            @change="handleFileChange"
          />
          <div v-if="formErrors.profile_pic" class="error-message">
            {{ formErrors.profile_pic }}
          </div>

          <button type="submit">Update</button>
          <button
            type="button"
            class="delete"
            @click="deleteProfile(userDetails.sponsor_id)"
          >
            Delete
          </button>
        </form>
      </div>
    </Base>
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
