<script setup>
  import Base from "./inf_base.vue";
  import "../../static/influencer/styles/inf_campaigns.css"
  import Swal from "sweetalert2";
  
  import API from "@/router/axios";
  import { onMounted, ref, watch } from 'vue';
  import { useRoute, useRouter } from 'vue-router';

  const isLoading = ref(false);
  const campaigns = ref([]);
  const sponsorName = ref("");
  const influencerId = ref(null);
  const router = useRouter();

  const route = useRoute();

  const fetchCampaigns = async () => {
      try {
          const sponsorId = route.params.id; 
          let response;

          if (sponsorId) {
              response = await API.get("/influencer/api/campaigns", {
                  params: { id: sponsorId },
              });
          } else {
              response = await API.get("/influencer/api/campaigns");
          }

          // Extract data from the API response
          campaigns.value = response.data.all_camp;
          sponsorName.value = response.data.sponsor_name;
          influencerId.value = response.data.influencer_id;
      } catch (error) {
          console.error("Error fetching campaigns:", error);
      }
  };

  const viewDetails = (camp,inf_id) => {
    const sponsorName = camp.sponser_name;
    const campaignId = camp.campaign_id;
    const influencerId = inf_id;
    const campaignTitle = camp.campaign_title;
    const description = camp.camp_desc;
    const endDate = camp.campaign_end_date;

    Swal.fire({
      title: "Campaign Details",
      html: `
        <div style="text-align:left;">
          <p><strong>Sponsor Company Name:</strong> ${sponsorName}</p>
          <p><strong>Campaign Name:</strong> ${campaignTitle}</p>
          <p><strong>Description:</strong> ${description}</p>
          <p><strong>End Date:</strong> ${endDate}</p>
          <p><strong>Payment:</strong> ₹<input id="payment-amount" class="swal2-input" style="display: inline-block; width: auto; padding: 2px 4px;" placeholder="Enter amount"></p>
          <div id="error-message" style="color: red; display: none;">Please enter a valid payment amount.</div>
        </div>
      `,
      icon: "info",
      confirmButtonText: "Request",
      showCancelButton: true,
      cancelButtonText: "Close",
      preConfirm: () => {
        const paymentAmount = document.getElementById("payment-amount").value;
        if (!paymentAmount) {
          document.getElementById("error-message").style.display = "block";
          return false;
        }
        return {
          adCampaignId: campaignId,
          adInfluencerid: influencerId,
          adPayment: paymentAmount
        };
      }
    }).then((result) => {
      if (result.isConfirmed) {
        const adData = result.value;

        // Use Axios to send the ad request
        API.post(`/influencer/send-ad-request/${campaignId}`, adData)
          .then((response) => {
            const data = response.data;
            if (data.message) {
              Swal.fire({
                title: "Success",
                text: data.message,
                icon: "success",
                confirmButtonText: "OK",
                willClose: () => {
                  location.reload();
                }
              });
            } else {
              Swal.fire({
                title: "Error",
                text: data.error,
                icon: "error",
                confirmButtonText: "OK",
                willClose: () => {
                  location.reload();
                }
              });
            }
          })
          .catch((error) => {
            console.error("Error:", error);
            Swal.fire({
              title: "Error",
              text: "There was an error sending the ad request",
              icon: "error",
              confirmButtonText: "OK",
              willClose: () => {
                location.reload();
              }
            });
          });
      }
    });
  };


  const goToSponsorPage = (sponsorId) => {
    router.push({ path: `/inf/campaigns/${sponsorId}` });  // Programmatically navigate to the sponsor page
  };

  onMounted(fetchCampaigns);
  watch(() => route.params.id, (newId) => {
    fetchCampaigns();
  });
</script>

<template>
  <Base>
        <div v-if="isLoading" class="loading-overlay">
          <div class="spinner"></div>
        </div>
        <div>
          <div class="details" v-if="campaigns.length > 0">
            <h1 class="h3 mb-4 text-gray-800">
              All
              <span v-if="sponsorName">{{ sponsorName }}</span>
              Non Requested Campaigns
            </h1>

            <div class="detail-box">
              <div class="campaigns-box" v-for="camp in campaigns" :key="camp.campaign_id">
                <img class="profile-img" :src="camp.campaign_profile_image" alt="Profile Image">
                <h5>{{ camp.campaign_title }}</h5>
                <h5>
                  <span class="spn-name-link" @click="goToSponsorPage(camp.sponsor_id)">{{ camp.sponser_name }}</span>
                </h5>
                <button
                  class="view view1"
                  type="button"
                  @click="viewDetails(camp,influencerId)"
                >
                  View
                </button>
              </div>
            </div>
          </div>

          <div v-else>
            <h1 class="h3 mb-0 text-gray-800">No campaigns found</h1>
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
