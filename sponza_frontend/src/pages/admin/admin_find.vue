<script setup>
import "../../static/admin/styles/admin_find.css";
import Base from "./admin_base.vue";
import { ref, computed, onMounted } from 'vue';
import Swal from 'sweetalert2';
import API from "@/router/axios";

    const isLoading = ref(false);
    const campaigns = ref([]);
    const sponsors = ref([]);
    const influencers = ref([]);

    const campaignSearchQuery = ref('');
    const sponsorSearchQuery = ref('');
    const influencerSearchQuery = ref('');

    const filteredCampaigns = computed(() => {
      return campaigns.value.filter((camp) =>
        camp.campaign_title.toLowerCase().includes(campaignSearchQuery.value.toLowerCase())
      );
    });

    const filteredSponsors = computed(() => {
      return sponsors.value.filter((spn) =>
        spn.sponsor_company_name.toLowerCase().includes(sponsorSearchQuery.value.toLowerCase())
      );
    });

    const filteredInfluencers = computed(() => {
      return influencers.value.filter((inf) =>
        inf.influencer_user_name.toLowerCase().includes(influencerSearchQuery.value.toLowerCase())
      );
    });

    const fetchData = async () => {
      isLoading.value = true;
      try {
        const response = await API.get('/admin/api/find');
        const data = response.data; 
        campaigns.value = data.campaigns;
        sponsors.value = data.sponsors;
        influencers.value = data.influencers;
      } catch (error) {
        console.error('Error fetching data', error);
      } finally {
        isLoading.value = false;
      }
    };

    const showDetails = (item, type) => {
      const title = `${type.charAt(0).toUpperCase() + type.slice(1)} Details`;
      let content = '';

      if (type === 'campaign') {
        content = `
          <p><strong>Sponsor Name:</strong> ${item.sponsor_name}</p>
          <p><strong>Duration:</strong> ${item.total_camp_days} days</p>
          <p><strong>Completed Days:</strong> ${item.completed_camp_days} days</p>
          <p><strong>Completed Progress:</strong> ${item.progress}%</p>
          <p><strong>Influencers:</strong> ${item.all_influencers.length ? item.all_influencers.join(', ') : 'No Influencers'}</p>
        `;
      } else if (type === 'sponsor') {
        content = `
          <p><strong>Sponsor Name:</strong> ${item.sponsor_company_name}</p>
          <p><strong>Ongoing Campaigns:</strong> ${item.campaign_titles.length ? item.campaign_titles.join(', ') : 'No ongoing campaigns'}</p>
        `;
      } else if (type === 'influencer') {
        content = `
          <p><strong>Influencer Name:</strong> ${item.influencer_user_name}</p>
          <p><strong>Niche:</strong> ${item.influencer_niche}</p>
          <p><strong>Social Media Platform:</strong> <a href="${item.influencer_social_media_link}">${item.influencer_social_media_platform}</a></p>
          <p><strong>Ongoing Campaigns:</strong> ${item.campaign_titles.length ? item.campaign_titles.join(', ') : 'No ongoing campaigns'}</p>
        `;
      }

      Swal.fire({
        title: title,
        html: content,
        icon: 'info',
        confirmButtonText: 'OK'
      });
    };

    const flag = async (id, role) => {
  const result = await Swal.fire({
    title: "Are you sure?",
    text: "You are about to flag this item.",
    icon: "warning",
    showCancelButton: true,
    confirmButtonText: "Yes, flag it!",
    cancelButtonText: "No, cancel!",
    reverseButtons: true,
  });

  if (result.isConfirmed) {
    try {
      isLoading.value = true; // Assuming `isLoading` is a reactive state
      const response = await API.put("/admin/flag", { id, role });
      
      if (response.data.message) {
        Swal.fire("Success", response.data.message, "success");
        fetchData();
      } else {
        Swal.fire("Error", response.data.error || "Unknown error", "error");
      }
    } catch (error) {
      console.error("Error flagging:", error);
      Swal.fire("Error", "There was an error sending the flag request", "error");
    } finally {
      isLoading.value = false;
    }
  }
};

    onMounted(fetchData);
</script>


<template>
    <Base>
      <div v-if="isLoading" class="loading-overlay">
      <div class="spinner"></div>
    </div>
      <div class="details" v-if="campaigns.length">
        <div class="top-details campaigns-search">
          <h1 class="h3 mb-4 text-gray-800 head-camp heading">Unflagged Campaigns:</h1>
          <form @submit.prevent="performCampaignSearch">
            <input v-model="campaignSearchQuery" type="search" class="search-text" placeholder="Search the Campaign" autocomplete="off" />
          </form>
        </div>
        <div v-if="filteredCampaigns.length">
          <div class="detail-box" id="campaigns-detail-box">
            <div v-for="camp in filteredCampaigns" :key="camp.campaign_id" class="campaigns-box">
              <img :src="camp.campaign_profile_image" alt="Profile Image" class="profile-img" />
              <h5>{{ camp.campaign_title }}</h5>
              <button @click="showDetails(camp, 'campaign')" class="view view-campaign">View</button>
              <button @click="flag(camp.campaign_id, 'camp')" class="flag">Flag</button>
            </div>
          </div>
        </div>
        <div v-else class="no-matches">No matched data</div>
      </div>
      <div class="details" v-else>
        <h1 class="h3 mb-4 text-gray-800">No Unflagged Campaigns</h1>
      </div>
  
      <div class="details" v-if="sponsors.length">
        <div class="top-details sponsors-search">
          <h1 class="h3 mb-4 text-gray-800">Unflagged Sponsors:</h1>
          <form @submit.prevent="performSponsorSearch">
            <input v-model="sponsorSearchQuery" type="search" class="search-text" placeholder="Search the Sponsor" autocomplete="off" />
          </form>
        </div>
        <div v-if="filteredSponsors.length">
          <div class="detail-box" id="sponsors-detail-box">
            <div v-for="spn in filteredSponsors" :key="spn.sponsor_id" class="sponsors-box">
              <img :src="spn.sponsor_profile_image" alt="Profile Image" class="profile-img" />
              <h5>{{ spn.sponsor_company_name }}</h5>
              <button @click="showDetails(spn, 'sponsor')" class="view view-sponsor">View</button>
              <button @click="flag(spn.sponsor_id, 'spn')" class="flag">Flag</button>
            </div>
          </div>
        </div>
        <div v-else class="no-matches">No matched data</div>
      </div>
      <div class="details" v-else>
        <h1 class="h3 mb-4 text-gray-800">No Unflagged Sponsors</h1>
      </div>
  
      <div class="details" v-if="influencers.length">
        <div class="top-details influencers-search">
          <h1 class="h3 mb-4 text-gray-800">Unflagged Influencers:</h1>
          <form @submit.prevent="performInfluencerSearch">
            <input v-model="influencerSearchQuery" type="search" class="search-text" placeholder="Search the Influencer" autocomplete="off" />
          </form>
        </div>
        <div v-if="filteredInfluencers.length">
          <div class="detail-box" id="influencers-detail-box">
            <div v-for="inf in filteredInfluencers" :key="inf.influencer_id" class="influencer-box">
              <img :src="inf.influencer_profile_image" alt="Profile Image" class="profile-img" />
              <h5>{{ inf.influencer_user_name }}</h5>
              <button @click="showDetails(inf, 'influencer')" class="view view-influencer">View</button>
              <button @click="flag(inf.influencer_id, 'inf')" class="flag">Flag</button>
            </div>
          </div>
        </div>
        <div v-else class="no-matches">No matched data</div>
      </div>
      <div class="details" v-else>
        <h1 class="h3 mb-4 text-gray-800">No Unflagged Influencers</h1>
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
  