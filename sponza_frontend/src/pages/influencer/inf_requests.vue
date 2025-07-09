<script setup>
    import Base from "./inf_base.vue";
    import "../../static/influencer/styles/inf_requests.css"
    
    import API from "@/router/axios";
    import { onMounted, ref } from 'vue';
    import Swal from "sweetalert2";

    const isLoading = ref(false);
    const influencerId = ref(null);
    const campSentPending = ref([]);
    const infSentPending = ref([]);
    const requestedSearchQuery = ref('');
    const acceptSearchQuery = ref('');
    const noMatchesRequested = ref(false);
    const noMatchesAccepted = ref(false);
    
    const fetchrequestesData = async () => {
      try {
        const response = await API.get('/influencer/api/requests');
        const data = response.data;
        campSentPending.value = data.camp_sent_pending;
        infSentPending.value = data.inf_sent_pending;
        influencerId.value = data.influencer_id;

      } catch (error) {
        console.error('Error fetching dashboard data:', error);
      }
    };

    const filterRequests = (query, list) =>
      list.filter(item => item.title.toLowerCase().includes(query.toLowerCase()));

    const handleSearchRequested = () => {
      noMatchesRequested.value =
        filterRequests(requestedSearchQuery.value, infSentPending.value).length === 0;
    };

    const handleSearchAccepted = () => {
      noMatchesAccepted.value =
        filterRequests(acceptSearchQuery.value, campSentPending.value).length === 0;
    };

  const removeRequest = (inf_id, camp_id) => {
  Swal.fire({
    title: "Are you sure?",
    text: "Do you want to proceed with this Reject?",
    icon: "warning",
    showCancelButton: true,
    confirmButtonColor: "#3085d6",
    cancelButtonColor: "#d33",
    confirmButtonText: "Yes"
  }).then((result) => {
    if (result.isConfirmed) {
      API.delete("/influencer/rm-ad-req", {
        data: { inf_id, camp_id }, // Pass data inside a `data` object
        headers: { "Content-Type": "application/json" }, // Explicitly set the content type
      })
        .then((response) => {
          const { message, error } = response.data;

          if (message) {
            Swal.fire({
              title: "Success",
              text: message,
              icon: "success",
              confirmButtonText: "OK"
            }).then(() => {
              window.location.reload(); // Optionally reload the page
            });
          } else {
            Swal.fire({
              title: "Error",
              text: error || "An unknown error occurred.",
              icon: "error",
              confirmButtonText: "OK"
            });
          }
        })
        .catch((error) => {
          console.error("Error:", error);
          Swal.fire({
            title: "Error",
            text: "There was an error sending the reject request.",
            icon: "error",
            confirmButtonText: "OK"
          });
        });
    }
  });
};


    const editSalary = (index) => {
      const form = document.getElementById(`change-salary-form-${index}`)
      const span = document.getElementById(`salary-span-${index}`)
      const editIcon =  document.getElementById(`edit-salary-${index}`)
      const saveIcon = document.getElementById(`save-salary-${index}`)
      const cancelIcon = document.getElementById(`cancel-salary-${index}`)
      const salaryInput = document.getElementById(`product-salary-input-${index}`)
      span.classList.add("hidden");
      editIcon.classList.add("hidden");

      
      salaryInput.dataset.initialValue = salaryInput.value.trim();
      salaryInput.focus();

      form.classList.remove("hidden"); 
      saveIcon.classList.remove("hidden"); 
      cancelIcon.classList.remove("hidden"); 
    }

    const cancelSalary = (index) => {
    const form = document.getElementById(`change-salary-form-${index}`);
    const span = document.getElementById(`salary-span-${index}`);
    const editIcon = document.getElementById(`edit-salary-${index}`);
    const saveIcon = document.getElementById(`save-salary-${index}`);
    const cancelIcon = document.getElementById(`cancel-salary-${index}`);
    const salaryInput = document.getElementById(`product-salary-input-${index}`);

    // Reset salary input to its initial value
    salaryInput.value = salaryInput.dataset.initialValue;

    // Toggle visibility
    span.classList.remove("hidden");
    editIcon.classList.remove("hidden");
    form.classList.add("hidden");
    saveIcon.classList.add("hidden");
    cancelIcon.classList.add("hidden");
    };

    const saveSalary = (index, camp_id) => {
        const salaryInput = document.getElementById(`product-salary-input-${index}`);
        const salaryErrorMessage = document.getElementById(`salary-error-message-${index}`);
        const span = document.getElementById(`salary-span-${index}`);
        const editIcon = document.getElementById(`edit-salary-${index}`);
        const saveIcon = document.getElementById(`save-salary-${index}`);
        const cancelIcon = document.getElementById(`cancel-salary-${index}`);
        const form = document.getElementById(`change-salary-form-${index}`);
        const initialValue = salaryInput.dataset.initialValue;

        // Validate input
        if (!salaryInput.value.trim()) {
            salaryErrorMessage.textContent = "Amount is required";
            salaryErrorMessage.classList.remove("hidden");
            return;
        }
        if (salaryInput.value.trim() === initialValue) {
            salaryErrorMessage.textContent = "No changes detected";
            salaryErrorMessage.classList.remove("hidden");
            return;
        }

        const amount = parseFloat(salaryInput.value.trim());
        if (isNaN(amount) || amount <= 0) {
            salaryErrorMessage.textContent = "Amount must be a positive number";
            salaryErrorMessage.classList.remove("hidden");
            return;
        }

        // Clear error messages
        salaryErrorMessage.classList.add("hidden");

        // Send updated salary to backend
        API.put(`/influencer/change-salary/${camp_id}`, { salary: salaryInput.value.trim() })
            .then((response) => {
                const { message, status } = response.data;

                if (status === "success") {
                    // Update UI to reflect changes
                    span.textContent = `₹${salaryInput.value.trim()}`;
                    salaryInput.dataset.initialValue = salaryInput.value.trim(); // Update initial value

                    Swal.fire({
                        title: "Success",
                        text: message,
                        icon: "success",
                        confirmButtonText: "OK",
                    });

                    // Toggle visibility
                    span.classList.remove("hidden");
                    editIcon.classList.remove("hidden");
                    form.classList.add("hidden");
                    saveIcon.classList.add("hidden");
                    cancelIcon.classList.add("hidden");
                } else {
                    Swal.fire({
                        title: "Error",
                        text: message || "An unknown error occurred.",
                        icon: "error",
                        confirmButtonText: "OK",
                    });
                }
            })
            .catch((error) => {
                console.error("Error:", error);
                Swal.fire({
                    title: "Error",
                    text: "Failed to update salary. Please try again later.",
                    icon: "error",
                    confirmButtonText: "OK",
                });
            });
    };

    const editNegotiateSalary = (index) => {
      const form = document.getElementById(`negotiate-change-salary-form-${index}`)
      const span = document.getElementById(`negotiate-salary-span-${index}`)
      const editIcon =  document.getElementById(`negotiate-edit-salary-${index}`)
      const saveIcon = document.getElementById(`negotiate-save-salary-${index}`)
      const cancelIcon = document.getElementById(`negotiate-cancel-salary-${index}`)
      const salaryInput = document.getElementById(`negotiate-product-salary-input-${index}`)
      span.classList.add("hidden");
      editIcon.classList.add("hidden");

      
      salaryInput.dataset.initialValue = salaryInput.value.trim();
      salaryInput.focus();

      form.classList.remove("hidden"); 
      saveIcon.classList.remove("hidden"); 
      cancelIcon.classList.remove("hidden"); 
    }

    const cancelNegotiateSalary = (index) => {
    const form = document.getElementById(`negotiate-change-salary-form-${index}`);
    const span = document.getElementById(`negotiate-salary-span-${index}`);
    const editIcon = document.getElementById(`negotiate-edit-salary-${index}`);
    const saveIcon = document.getElementById(`negotiate-save-salary-${index}`);
    const cancelIcon = document.getElementById(`negotiate-cancel-salary-${index}`);
    const salaryInput = document.getElementById(`negotiate-product-salary-input-${index}`);

    // Reset salary input to its initial value
    salaryInput.value = salaryInput.dataset.initialValue;

    // Toggle visibility
    span.classList.remove("hidden");
    editIcon.classList.remove("hidden");
    form.classList.add("hidden");
    saveIcon.classList.add("hidden");
    cancelIcon.classList.add("hidden");
    };

    const saveNegotiateSalary = (index, camp_id) => {
        const salaryInput = document.getElementById(`negotiate-product-salary-input-${index}`);
        const salaryErrorMessage = document.getElementById(`negotiate-salary-error-message-${index}`);
        const span = document.getElementById(`negotiate-salary-span-${index}`);
        const editIcon = document.getElementById(`negotiate-edit-salary-${index}`);
        const saveIcon = document.getElementById(`negotiate-save-salary-${index}`);
        const cancelIcon = document.getElementById(`negotiate-cancel-salary-${index}`);
        const form = document.getElementById(`negotiate-change-salary-form-${index}`);
        const initialValue = salaryInput.dataset.initialValue;

        // Validate input
        if (!salaryInput.value.trim()) {
            salaryErrorMessage.textContent = "Amount is required";
            salaryErrorMessage.classList.remove("hidden");
            return;
        }
        if (salaryInput.value.trim() === initialValue) {
            salaryErrorMessage.textContent = "No changes detected";
            salaryErrorMessage.classList.remove("hidden");
            return;
        }

        const amount = parseFloat(salaryInput.value.trim());
        if (isNaN(amount) || amount <= 0) {
            salaryErrorMessage.textContent = "Amount must be a positive number";
            salaryErrorMessage.classList.remove("hidden");
            return;
        }

        // Clear error messages
        salaryErrorMessage.classList.add("hidden");
        isLoading.value = true;
        // Send updated salary to backend
        API.post(`/influencer/negotiate/${camp_id}`, { "negotiate-amt": salaryInput.value.trim() })
            .then((response) => {
                const { message, status } = response.data;

                if (status === "success") {
                    // Update UI to reflect changes
                    span.textContent = `₹${salaryInput.value.trim()}`;
                    salaryInput.dataset.initialValue = salaryInput.value.trim(); // Update initial value

                    Swal.fire({
                        title: "Success",
                        text: message,
                        icon: "success",
                        confirmButtonText: "OK",
                        willClose: () => {
                          fetchrequestesData();
                }
                    });

                    // Toggle visibility
                    span.classList.remove("hidden");
                    editIcon.classList.remove("hidden");
                    form.classList.add("hidden");
                    saveIcon.classList.add("hidden");
                    cancelIcon.classList.add("hidden");
                } else {
                    Swal.fire({
                        title: "Error",
                        text: message || "An unknown error occurred.",
                        icon: "error",
                        confirmButtonText: "OK",
                    });
                }
            })
            .catch((error) => {
                console.error("Error:", error);
                Swal.fire({
                    title: "Error",
                    text: "Failed to update salary. Please try again later.",
                    icon: "error",
                    confirmButtonText: "OK",
                });
            })
            .finally(()=>{
              isLoading.value = false;
            })
    };

    const viewDetails = async (camp) => {
  const inf_id = influencerId.value;
  const camp_id = camp.id;
  const sponsorName = camp.sponsor_company_name;
  const campDesc = camp.desc;
  const endDate = camp.end_date;

  const confirmSwal = (title, text) => {
    return Swal.fire({
      title,
      text,
      icon: "warning",
      showCancelButton: true,
      confirmButtonColor: "#3085d6",
      cancelButtonColor: "#d33",
      confirmButtonText: "Yes",
    });
  };

  const data = { inf_id, camp_id };

  Swal.fire({
    title: "Campaign Details",
    html: `
      <div style="text-align: left;">
        <p><strong>Company Name:</strong> ${sponsorName}</p>
        <p><strong>Description:</strong> ${campDesc}</p>
        <p><strong>End Date:</strong> ${endDate}</p>
      </div>
    `,
    icon: "info",
    showCancelButton: true,
    cancelButtonText: "Close",
    showDenyButton: true,
    showConfirmButton: true,
    confirmButtonText: "Accept",
    denyButtonText: "Reject",
  }).then(async (result) => {
    if (result.isConfirmed) {
      const confirmResult = await confirmSwal(
        "Are you sure?",
        "Do you want to proceed with this Accept?"
      );
      if (confirmResult.isConfirmed) {
        try {
          const response = await API.put("/influencer/accept-ad-req", data);
          const { message, error } = response.data;

          if (message) {
            Swal.fire({
              title: "Success",
              text: message,
              icon: "success",
              confirmButtonText: "OK",
              willClose: fetchrequestesData,
            });
          } else {
            Swal.fire({
              title: "Error",
              text: error || "An error occurred.",
              icon: "error",
            });
          }
        } catch (error) {
          console.error("Error:", error);
          Swal.fire({
            title: "Error",
            text: "There was an error sending the ad request.",
            icon: "error",
          });
        }
      }
    } else if (result.isDenied) {
      const confirmResult = await confirmSwal(
        "Are you sure?",
        "Do you want to proceed with this Reject?"
      );
      if (confirmResult.isConfirmed) {
        try {

          const response = await API.delete("/influencer/rm-ad-req", {
        data: data, // Pass data in the `data` field
        headers: { "Content-Type": "application/json" } // Ensure content type is JSON
      });
          const { message, error } = response.data;

          if (message) {
            Swal.fire({
              title: "Success",
              text: message,
              icon: "success",
              confirmButtonText: "OK",
              willClose: fetchrequestesData,
            });
          } else {
            Swal.fire({
              title: "Error",
              text: error || "An error occurred.",
              icon: "error",
              confirmButtonText: "OK",
            });
          }
        } catch (error) {
          console.error("Error:", error);
          Swal.fire({
            title: "Error",
            text: "There was an error sending the ad request.",
            icon: "error",
            confirmButtonText: "OK",
          });
        }
      }
    }
  });
    };

    onMounted(fetchrequestesData)
</script>


<template>
    <Base>
      <div v-if="isLoading" class="loading-overlay">
      <div class="spinner"></div>
    </div>
    <div class="all-details">

    <div v-if="infSentPending.length" class="details details1">
      <div class="top-details">
        <h1 class="h3 mb-4 text-gray-800" style="margin-bottom: -3vh !important; margin-top: 3vh;">Request Sent</h1>
        <form @submit.prevent="handleSearchRequested" class="search-form">
          <input
            type="search"
            v-model="requestedSearchQuery"
            placeholder="Search the Influencer"
            class="search-text"
            autocomplete="off"
          />
          <input type="submit" value="" class="search-submit" />
        </form>
      </div>
      <div v-if="noMatchesRequested" class="no-matches">No matched data</div>

      <div v-for="(camp, index) in filterRequests(requestedSearchQuery, infSentPending)" :key="camp.id" class="influencer-box flex-box">
  <img class="profile-img" :src="camp.image" alt="Profile Image" />
  <h5>{{ camp.title }}</h5>
  <h5>{{ camp.sponsor }}</h5>
  <div>
    <span class="salary" :id="`salary-span-${index}`">₹{{ camp.camp_pay }}</span>
    <i
      :id="`edit-salary-${index}`"
      @click="editSalary(index)"
      class="edit-icon fa-regular fa-pen-to-square"
      data-target="salary"
    ></i>
    <form
      :id="`change-salary-form-${index}`"
      class="hidden"
    >
      <input
        type="text"
        name="salary"
        :id="`product-salary-input-${index}`"
        :value="camp.camp_pay"
        required
      />
      <i
        :id="`save-salary-${index}`"
        @click.prevent="saveSalary(index,camp.main_id)"
        class="save-icon fa-solid fa-check hidden"
      ></i>
      <i
        :id="`cancel-salary-${index}`"
        @click.prevent="cancelSalary(index)"
        class="cancel-icon fa-solid fa-xmark hidden"
      ></i>
      <div :id="`salary-error-message-${index}`" class="error-message hidden"></div>
    </form>
  </div>

  <button
    @click="removeRequest(influencerId, camp.id)"
    class="reject"
  >
    Remove
  </button>
</div>

    </div>
    <div v-else>
      <h1 class="h3 mb-4 text-gray-800" style="margin-bottom: -3vh !important; margin-top: 3vh;">
        No Request Sent
      </h1>
    </div>



    <div v-if="campSentPending.length" class="details details1">
      <div class="top-details">
        <h1 class="h3 mb-4 text-gray-800" style="margin-bottom: -3vh !important; margin-top: 3vh;">
          Request Received
        </h1>
        <form @submit.prevent="handleSearchAccepted" class="search-form">
          <input
            type="search"
            v-model="acceptSearchQuery"
            placeholder="Search the Influencer"
            class="search-text"
            autocomplete="off"
          />
          <input type="submit" value="" class="search-submit" />
        </form>
      </div>
      <div v-if="noMatchesAccepted" class="no-matches">No matched data</div>
      <div
        v-for="(camp,index) in filterRequests(acceptSearchQuery, campSentPending)"
        :key="camp.id"
        class="influencer-box flex-box"
      >
        <img class="profile-img" :src="camp.image" alt="Profile Image" />
        <h5>{{ camp.title }}</h5>
        <div>
    <span class="salary" :id="`negotiate-salary-span-${index}`">₹{{ camp.camp_pay }}</span>
    <i :id="`negotiate-edit-salary-${index}`" @click="editNegotiateSalary(index)" class="edit-icon fa-regular fa-pen-to-square" data-target="salary"></i>
    <form :id="`negotiate-change-salary-form-${index}`" class="hidden">
      <input type="text" :id="`negotiate-product-salary-input-${index}`" :value="camp.camp_pay"/>
      <i :id="`negotiate-save-salary-${index}`" @click.prevent="saveNegotiateSalary(index,camp.main_id)" class="save-icon fa-solid fa-check "></i>
      <i :id="`negotiate-cancel-salary-${index}`" @click.prevent="cancelNegotiateSalary(index)" class="cancel-icon fa-solid fa-xmark hidden"></i>
      <div :id="`negotiate-salary-error-message-${index}`" class="error-message hidden"></div>
    </form>
  </div>
        <button
          class="views"
          @click="viewDetails(camp)"
        >
          View
        </button>
      </div>
    </div>
    <div v-else>
      <h1 class="h3 mb-0 text-gray-800" style="margin-top: 3vh;">No Request Received</h1>
    </div>
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
