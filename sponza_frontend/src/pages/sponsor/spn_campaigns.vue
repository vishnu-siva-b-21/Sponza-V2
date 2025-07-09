<script setup>
    import Base from "./spn_base.vue";
    import "../../static/sponsor/styles/sponsor_campaigns.css";
    import add_logo from "../../static/sponsor/images/add.png";

    import API from "@/router/axios";
    import { onMounted, ref, computed } from 'vue';
    import Swal from "sweetalert2";

    const isLoading = ref(false);
    const campaigns = ref([]);
    const sponsorName = ref('');
    const campaignSearchQuery = ref('');

    const fetchCampaigns = async () => {
      try {
        const response = await API.get('/sponsor/campaigns');
        const data = response.data;

        campaigns.value = data.campaigns || [];
        sponsorName.value = data.sponsor_name;
      } catch (error) {
        console.error('Error fetching campaigns data:', error);
      }
    };

    const filteredCampaigns = computed(() => {
      return campaigns.value.filter((camp) =>
        camp.title.toLowerCase().includes(campaignSearchQuery.value.toLowerCase())
      );
    });

const addCampaign = () => {
  const currentDate = new Date();
  const tomorrow = new Date(currentDate);
  tomorrow.setDate(currentDate.getDate() + 1);
  const minDate = tomorrow.toISOString().split("T")[0];

  Swal.fire({
    title: "Create New Campaign",
    html: `
      <div style="text-align:left;">
        <form id="campaign-form" style="display: flex; flex-direction: column; gap: 0.6em;">
          <div style="display: flex; align-items: center; gap: 1em;">
            <label for="title" style="flex: 1; min-width: 100px;">Title:</label>
            <input type="text" id="title" name='title' class="swal2-input" placeholder="Enter title" style="flex: 2;">
          </div>
          <div style="display: flex; align-items: center; gap: 1em;">
            <label for="description" style="flex: 1; min-width: 100px;">Description:</label>
            <textarea id="description" name='desc' class="swal2-textarea" placeholder="Enter description" style="flex: 2;"></textarea>
          </div>
          <div style="display: flex; align-items: center; gap: 1em;">
            <label for="image" style="flex: 1; min-width: 100px;">Profile Picture:</label>
            <input type="file" id="image" name='profile_pic' class="swal2-file" style="flex: 2;">
          </div>
          <div style="display: flex; align-items: center; gap: 1em;">
            <label for="end-date" style="flex: 1; min-width: 100px;">End Date:</label>
            <input type="date" id="end-date" name='end_date' class="swal2-input" style="flex: 2;" min="${minDate}">
          </div>
          <div style="display: flex; align-items: center; gap: 1em;">
            <label for="visibility" style="flex: 1; min-width: 100px;">Visibility:</label>
            <select id="visibility" class="input-text select" name="campaign_visibility">
              <option value="public" selected>Public</option>
              <option value="private">Private</option>
            </select>
          </div>
          <div style="display: flex; align-items: center; gap: 1em;">
            <label for="goals" style="flex: 1; min-width: 100px;">Goals:</label>
            <textarea id="goals" name='campaign_goals' class="swal2-textarea" placeholder="Enter goals" style="flex: 2;"></textarea>
          </div>
        </form>
      </div>
    `,
    showCancelButton: true,
    confirmButtonText: "Add",
    preConfirm: () => {
      const title = document.getElementById("title").value;
      const description = document.getElementById("description").value;
      const goals = document.getElementById("goals").value;
      const visibility = document.getElementById("visibility").value;
      const endDate = document.getElementById("end-date").value;

      if (!title || !description || !endDate || !goals) {
        Swal.showValidationMessage("Please fill out all fields");
        return false;
      }

      if (endDate < minDate) {
        Swal.showValidationMessage("End date must be tomorrow or a future date");
        return false;
      }

      return { title, description, endDate, visibility, goals };
    }
  }).then(async (result) => {
    if (result.isConfirmed) {
      const { title, description, endDate, visibility, goals } = result.value;

      const formData = new FormData();
      formData.append('title', title);
      formData.append('desc', description);
      formData.append('end_date', endDate);
      formData.append('campaign_visibility', visibility);
      formData.append('campaign_goals', goals);
      const image = document.getElementById("image").files[0];
      if (image) {
        formData.append('profile_pic', image);
      }

      try {
        const response = await API.post('/sponsor/add-campaign', formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });

        if (response.data.status === 'success') {
          Swal.fire({
            icon: 'success',
            title: 'Campaign Added Successfully',
            confirmButtonText: 'OK',            
            willClose: () => {
              fetchCampaigns();
              }
          });
        }
      } catch (error) {
        Swal.fire({
          icon: 'error',
          title: 'Failed to Add Campaign',
          text: 'An error occurred while adding the campaign.',
          confirmButtonText: 'OK'
        });
      }
    }
  });
};

    onMounted(fetchCampaigns);
</script>

<template>
    <Base>
        <div v-if="isLoading" class="loading-overlay">
            <div class="spinner"></div>
        </div>
        <div class="container-fluid">
            <h1 class="h3 mb-4 text-gray-800">Ongoing Campaigns</h1>
            <form @submit.prevent="performCampaignSearch">
                <input v-model="campaignSearchQuery" type="search" class="search-text" placeholder="Search the Campaign" autocomplete="off" />
            </form>

            <div v-if="filteredCampaigns.length">
                <div class="ongoing-cp">
                    <div v-for="camp in filteredCampaigns" :key="camp.campaign_id" class="ongoing-cp-inner">
                      <router-link 
                            :to="{ name: 'CampaignDetails', params: { id: camp.id } }" 
                            style="text-decoration: none; color: grey;">
                            <div class="box">
                                <img :src="camp.image" alt="Campaign Profile Image" style="width: 100px; height: 100px; border-radius: 100%;" />
                                <h4><b>{{ camp.title }}</b></h4>
                                <p>{{ camp.desc }}</p>
                                <p class="date-range-paragraph">Start Date: {{ camp.start_date }}</p>
                                <p class="date-range-paragraph">End Date: {{ camp.end_date }}</p>
                            </div>
                        </router-link>
                    </div>
                </div>
            </div>
            <div v-else>
                <h1 class="h3 mb-4 text-gray-800">No campaigns Created</h1>
            </div>
            <div class="add-campaigns">
                <h1 class="h3 mb-4 text-gray-800">Add Campaigns</h1>
                <img :src="add_logo" alt="Add Campaign" style="width: 120px; height: 120px; border-radius: 100%;" @click="addCampaign" class="add-campaigns-image" />
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
