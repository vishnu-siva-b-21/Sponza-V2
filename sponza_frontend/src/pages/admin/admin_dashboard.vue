<script setup>
    import "../../static/admin/styles/admin_dashboard.css";
    import { onMounted,computed,ref } from 'vue';
    import Base from "./admin_base.vue";
    import API from "@/router/axios";
    import Swal from "sweetalert2";

    const isLoading = ref(false);
    const total_infs = ref();
    const total_spns= ref();
    const total_users= ref();
    const total_expense= ref();
    const searchQuery = ref('');
    const sponsors = ref([]);
    const influencers = ref([]);
    const campaigns = ref([]);
    const unapprovedSponsors = ref([]);
     const filteredCampaigns = computed(() => {
      return campaigns.value.filter((camp) => camp.campaign_title.toLowerCase().includes(searchQuery.value.toLowerCase()));
    });

    const filteredSponsors = computed(() => {
      return sponsors.value.filter((spn) => spn.sponsor_company_name.toLowerCase().includes(searchQuery.value.toLowerCase()));
    });

    const filteredInfluencers = computed(() => {
      return influencers.value.filter((inf) => inf.influencer_user_name.toLowerCase().includes(searchQuery.value.toLowerCase()));
    });


    const approveSponsor = async (id, role) => {
      const result = await Swal.fire({
        title: "Are you sure?",
        text: "You want to approve this sponsor?",
        icon: "question",
        showCancelButton: true,
        confirmButtonColor: "#28a745",
        cancelButtonColor: "#d33",
        confirmButtonText: "Yes, approve it!"
      });

      if (result.isConfirmed) {
        isLoading.value = true;

        try {
          const response = await API.put("/admin/approve", { id, role });
          if (response.data.message) {
            Swal.fire({
              title: "Approved!",
              text: response.data.message,
              icon: "success",
              confirmButtonText: "OK",
            });
            fetchDashboardData();
          } else {
            Swal.fire({
              title: "Error",
              text: response.data.error || "An error occurred.",
              icon: "error"
            });
          }
        } catch (error) {
          console.error("Error:", error);
        } finally {
          isLoading.value = false; 
        }
      }
    };

    const rejectSponsor = async (id,role) => {
      
      console.log({ id, role })
      const result = await Swal.fire({
        title: "Are you sure?",
        text: "You want to reject this sponsor?",
        icon: "warning",
        showCancelButton: true,
        confirmButtonColor: "#d33",
        cancelButtonColor: "#28a745",
        confirmButtonText: "Yes, reject it!"
      });

      if (result.isConfirmed) {
        isLoading.value = true;

        try {
          const response = await API.delete("/admin/reject", {
        headers: {
          "Content-Type": "application/json",
        },
        data: { id, role },
      });
          if (response.data.message) {
            Swal.fire({
                  title: "Rejected!",
                  text: response.data.message,
                  icon: "success",
                  confirmButtonText: "OK",
            });
            fetchDashboardData();
          } else {
            Swal.fire({
              title: "Error",
              text: response.data.error || "An error occurred.",
              icon: "error"
            });
          }
        } catch (error) {
          console.error("Error:", error);
        } finally {
          isLoading.value = false; 
        }
      }
    };

    const unflag = async (id,role) => {
      const result = await Swal.fire({
        title: "Are you sure?",
      text: "Do you really want to leave the campaign?",
      icon: "warning",
      showCancelButton: true,
      confirmButtonText: "Yes, unflag it!",
      cancelButtonText: "No, cancel!",
      confirmButtonColor: "#3085d6",
      cancelButtonColor: "#d33",
      reverseButtons: true
      });

      if (result.isConfirmed) {
        isLoading.value = true;

        try {
          const response = await API.put("/admin/unflag", { id, role });
          if (response.data.message) {
            Swal.fire({
                title: "Success",
                text: response.data.message,
                icon: "success",
                  confirmButtonText: "OK",
            });
            fetchDashboardData();
          } else {
            Swal.fire({
              title: "Error",
              text: response.data.error || "An error occurred.",
              icon: "error"
            });
          }
        } catch (error) {
          console.error("Error:", error);
        } finally {
          isLoading.value = false; 
        }
      }
    };
    
    const showCampaignDetails = (camp) => {
      Swal.fire({
        title: "Campaign Details",
        html: `
          <div style="text-align:left;">
            <p><strong>Sponsor Name:</strong> ${camp.sponsor_name}</p>
            <p><strong>Duration:</strong> ${camp.total_camp_days} Days</p>
            <p><strong>Completed Days:</strong> ${camp.completed_camp_days}</p>
            <p><strong>Completed progress:</strong> ${camp.progress}%</p>
            <p><strong>Influencers:</strong> 
              ${camp.all_influencers.length > 0 ? camp.all_influencers.join(", ") : "No Influencers"}</p>
          </div>
        `,
        icon: "info"
      });
    };


    const showSponsorDetails = (spn) => {
      Swal.fire({
        title: "Sponsor Details",
        html: `
          <div style="text-align:left;">
            <p><strong>Sponsor Name:</strong> ${spn.sponsor_name}</p>
            <p><strong>Ongoing Campaigns:</strong> 
              ${spn.campaign_titles.length > 0 ? spn.campaign_titles.join(", ") : "No Influencers"}</p>
          </div>
        `,
        icon: "info"
      });
    };

    const showInfluencerDetails = (inf) => {

      Swal.fire({
        title: "Campaign Details",
        html: `
          <div style="text-align:left;">
            <p><strong>Sponsor Name:</strong> ${inf.influencer_user_name}</p>
          <p><strong>Niche:</strong> ${inf.influencer_niche}</p>
          <p><strong>Social Media Platform:</strong> <a href="${inf.influencer_social_media_link}">${inf.influencer_social_media_platform}</a></p>
            <p><strong>Influencers:</strong> 
              ${inf.campaign_titles.length > 0 ? inf.campaign_titles.join(", ") : "No Influencers"}</p>
          </div>
        `,
        icon: "info"
      });
    };

    Chart.defaults.global.defaultFontFamily = "Nunito";
    Chart.defaults.global.defaultFontColor = "#858796";

    function number_format(number, decimals, dec_point, thousands_sep) {
      number = (number + "").replace(",", "").replace(" ", "");
      var n = !isFinite(+number) ? 0 : +number,
        prec = !isFinite(+decimals) ? 0 : Math.abs(decimals),
        sep = typeof thousands_sep === "undefined" ? "," : thousands_sep,
        dec = typeof dec_point === "undefined" ? "." : dec_point,
        s = "",
        toFixedFix = function (n, prec) {
          var k = Math.pow(10, prec);
          return "" + Math.round(n * k) / k;
        };
      s = (prec ? toFixedFix(n, prec) : "" + Math.round(n)).split(".");
      if (s[0].length > 3) {
        s[0] = s[0].replace(/\B(?=(?:\d{3})+(?!\d))/g, sep);
      }
      if ((s[1] || "").length < prec) {
        s[1] = s[1] || "";
        s[1] += new Array(prec - s[1].length + 1).join("0");
      }
      return s.join(dec);
    }

    function hideContainer(container) {
      container.style.display = "none";
    }

    function isDataEmpty(data) {
      return Object.keys(data).length === 0;
    }

    function isPieDataEmpty(object1) {
  const arr = Object.values(object1);
  const isAllZeros = arr.every(item => item === 0);
  return isAllZeros;
}

    const fetchGraphData = async () => {
      try {
        const response = await API.get('/admin/get-graph-data');
        const data = response.data;

        if (isDataEmpty(data)) {
          hideContainer(document.querySelector('.col-xl-8.col-lg-7'));
          return;
        }

        const labels = [];
        const dataPoints = [];

        for (const key in data) {
          if (data.hasOwnProperty(key)) {
            labels.push(key);
            dataPoints.push(data[key]);
          }
        }

        var ctx = document.getElementById('myAreaChart');
        var myLineChart = new Chart(ctx, {
          type: 'line',
          data: {
            labels: labels,
            datasets: [
              {
                label: 'Expenses',
                lineTension: 0.3,
                backgroundColor: 'rgba(78, 115, 223, 0.05)',
                borderColor: 'rgba(78, 115, 223, 1)',
                pointRadius: 3,
                pointBackgroundColor: 'rgba(78, 115, 223, 1)',
                pointBorderColor: 'rgba(78, 115, 223, 1)',
                pointHoverRadius: 3,
                pointHoverBackgroundColor: 'rgba(78, 115, 223, 1)',
                pointHoverBorderColor: 'rgba(78, 115, 223, 1)',
                pointHitRadius: 10,
                pointBorderWidth: 2,
                data: dataPoints,
              },
            ],
          },
          options: {
            maintainAspectRatio: false,
            layout: {
              padding: {
                left: 10,
                right: 25,
                top: 25,
                bottom: 0,
              },
            },
            scales: {
              xAxes: [
                {
                  scaleLabel: {
                    display: true,
                    labelString: 'Campaigns',
                    fontSize: 16,
                    fontColor: '#4e73df',
                    fontFamily:
                      'Nunito, -apple-system,system-ui,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif',
                    fontStyle: 'bold',
                  },
                  ticks: {
                    display: false,
                  },
                  gridLines: {
                    display: false,
                    drawBorder: false,
                  },
                },
              ],
              yAxes: [
                {
                  scaleLabel: {
                    display: true,
                    labelString: 'Expenses',
                    fontSize: 16,
                    fontColor: '#4e73df',
                    fontFamily:
                      'Nunito, -apple-system,system-ui,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif',
                    fontStyle: 'bold',
                  },
                  ticks: {
                    display: false,
                    callback: function (value, index, values) {
                      return '₹' + number_format(value);
                    },
                  },
                  gridLines: {
                    color: 'rgb(234, 236, 244)',
                    zeroLineColor: 'rgb(234, 236, 244)',
                    drawBorder: false,
                    borderDash: [2],
                    zeroLineBorderDash: [2],
                  },
                },
              ],
            },
            legend: {
              display: false,
            },
            tooltips: {
              backgroundColor: 'rgb(255,255,255)',
              bodyFontColor: '#858796',
              titleMarginBottom: 10,
              titleFontColor: '#6e707e',
              titleFontSize: 14,
              borderColor: '#dddfeb',
              borderWidth: 1,
              xPadding: 15,
              yPadding: 15,
              displayColors: false,
              intersect: false,
              mode: 'index',
              caretPadding: 10,
              callbacks: {
                label: function (tooltipItem, chart) {
                  var datasetLabel =
                    chart.datasets[tooltipItem.datasetIndex].label || '';
                  return datasetLabel + ': ₹' + number_format(tooltipItem.yLabel);
                },
              },
            },
          },
        });
      } catch (error) {
        console.error('Error fetching data:', error);
        hideContainer(document.querySelector('.col-xl-8.col-lg-7'));
      }
    };


    const fetchPieData = async () => {
    try {
      const response = await API.get('/admin/get-pie-data');
      const data = response.data;

      if (isPieDataEmpty(data)) {
        hideContainer(document.querySelector('.col-xl-4.col-lg-5'));
        return;
      }

      const dynamicData = {
        values: [data.influencer, data.campaign],
        labels: ['Influencer', 'Campaigns'],
      };

      const chartContainer = document.getElementById('chartPie');
      chartContainer.setAttribute('data-values', JSON.stringify(dynamicData.values));
      chartContainer.setAttribute('data-labels', JSON.stringify(dynamicData.labels));

      const values = JSON.parse(chartContainer.getAttribute('data-values'));
      const labels = JSON.parse(chartContainer.getAttribute('data-labels'));

      const chartData = {
        labels: labels,
        datasets: [
          {
            data: values,
            backgroundColor: ['#4e73df', '#1cc88a'],
            hoverBackgroundColor: ['#2e59d9', '#17a673'],
            hoverBorderColor: 'rgba(234, 236, 244, 1)',
          },
        ],
      };

      const valuePlugin = {
        id: 'valuePlugin',
        afterDatasetsDraw(chart) {
          const { ctx, data } = chart;
          chart.data.datasets.forEach((dataset, i) => {
            const meta = chart.getDatasetMeta(i);
            meta.data.forEach((element, index) => {
              ctx.fillStyle = 'white';
              const fontSize = 16;
              const fontStyle = 'normal';
              const fontFamily = 'Helvetica Neue';
              ctx.font = Chart.helpers.fontString(fontSize, fontStyle, fontFamily);
              ctx.textAlign = 'center';
              ctx.textBaseline = 'middle';

              const padding = 5;
              const position = element.tooltipPosition();
              const total = dataset.data.reduce((a, b) => a + b, 0);
              const value = dataset.data[index];
              const text = `${((value / total) * 100).toFixed(1)}%`;

              ctx.fillText(text, position.x, position.y - fontSize / 2 - padding);
            });
          });
        },
      };

      const config = {
        type: 'pie',
        data: chartData,
        options: {
          responsive: true,
          plugins: {
            legend: {
              display: false,
            },
          },
        },
        plugins: [valuePlugin],
      };

      const myPieChart = new Chart(document.getElementById('myPieChart'), config);
    } catch (error) {
      console.error('Error fetching pie data:', error);
      hideContainer(document.querySelector('.col-xl-4.col-lg-5'));
    }
    };

    const fetchDashboardData =async () => {
    try {
      const response = await API.get('/admin/api/dashboard');
      const data = response.data;
      total_infs.value= data.total_infs;
      total_spns.value= data.total_spns;
      total_users.value= data.total_users;
      total_expense.value= data.total_expense;
      sponsors.value = data.sponsors;
      influencers.value = data.influencers;
      campaigns.value = data.campaigns;
      unapprovedSponsors.value = data.unapproved_sponsors;
    }catch (error) {
        console.error('Error fetching data', error);
      }}

    onMounted(fetchGraphData);
    onMounted(fetchPieData);
    onMounted(fetchDashboardData);

</script>


<template>
<Base>
  <div v-if="isLoading" class="loading-overlay">
      <div class="spinner"></div>
    </div>
    <div class="container-fluid">
        <div class="d-sm-flex align-items-center justify-content-between mb-4">
            <h1 class="h3 mb-0 text-gray-800 heading">Dashboard</h1>
        </div>

<div class="row">
    <div class="col-xl-3 col-md-6 mb-4">
        <div class="card border-left-primary shadow h-100 py-2">
            <div class="card-body">
                <div class="row no-gutters align-items-center">
                    <div class="col mr-2">
                        <div class="text-xs font-weight-bold text-primary text-uppercase mb-1">
                            Total Users</div>
                        <div class="h5 mb-0 font-weight-bold text-gray-800">{{ total_users }}</div>
                    </div>
                    <div class="col-auto">
                        <i class="fas fa-calendar fa-2x text-gray-300"></i>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <div class="col-xl-3 col-md-6 mb-4">
        <div class="card border-left-success shadow h-100 py-2">
            <div class="card-body">
                <div class="row no-gutters align-items-center">
                    <div class="col mr-2">
                        <div class="text-xs font-weight-bold text-success text-uppercase mb-1">
                            Expenses</div>
                        <div class="h5 mb-0 font-weight-bold text-gray-800">{{ total_expense }}</div>
                    </div>
                    <div class="col-auto">
                        <i class="fa-solid fa-indian-rupee-sign fa-2x text-gray-300"></i>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <div class="col-xl-3 col-md-6 mb-4">
        <div class="card border-left-info shadow h-100 py-2">
            <div class="card-body">
                <div class="row no-gutters align-items-center">
                    <div class="col mr-2">
                        <div class="text-xs font-weight-bold text-info text-uppercase mb-1">Total
                            Influencer
                        </div>
                        <div class="row no-gutters align-items-center">
                            <div class="col-auto">
                                <div class="h5 mb-0 mr-3 font-weight-bold text-gray-800">{{ total_infs }}</div>
                            </div>
                        </div>
                    </div>
                    <div class="col-auto">
                        <i class="fas fa-clipboard-list fa-2x text-gray-300"></i>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <div class="col-xl-3 col-md-6 mb-4">
        <div class="card border-left-warning shadow h-100 py-2">
            <div class="card-body">
                <div class="row no-gutters align-items-center">
                    <div class="col mr-2">
                        <div class="text-xs font-weight-bold text-warning text-uppercase mb-1">
                            Total Sponsors</div>
                        <div class="h5 mb-0 font-weight-bold text-gray-800">{{ total_spns }}</div>
                    </div>
                    <div class="col-auto">
                        <i class="fas fa-comments fa-2x text-gray-300"></i>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>


<div class="row">

    <div class="col-xl-8 col-lg-7">
        <div class="card shadow mb-4">
            <div class="card-header py-3 d-flex flex-row align-items-center justify-content-between">
                <h6 class="m-0 font-weight-bold text-primary">Campaigns Growth</h6>
            </div>
            <div class="card-body">
                <div class="chart-area">
                    <canvas id="myAreaChart"></canvas>
                </div>
            </div>
        </div>
    </div>

    <div class="col-xl-4 col-lg-5">
        <div class="card shadow mb-4 pie">
            <div class="card-header py-3 d-flex flex-row align-items-center justify-content-between">
                <h6 class="m-0 font-weight-bold text-primary">User Type Split</h6>
            </div>
            <div class="card-body pie-body">
                <div class="chart-pie pt-4 pb-2" id="chartPie" data-labels='["Influencer", "Sponsor"]'>
                    <canvas id="myPieChart"></canvas>
                </div>

            </div>
        </div>
    </div>
</div>
</div>
<div>
    <div v-if="unapprovedSponsors.length">
      <div class="details">
        <div class="top-details">
          <h1 class="h3 mb-4 text-gray-800 heading">Sponsor Requests:</h1>
        </div>
        <div class="detail-box">
          <div v-for="spn in unapprovedSponsors" :key="spn.sponsor_id" class="sponsors-box">
            <h5>{{ spn.sponsor_company_name }}</h5>
            <h5>{{ spn.industry }}</h5>
            <button
              class="approve"
              :data-id="spn.sponsor_id"
              data-role="sponsor"
              style="background-color: #28a745; color: white;"
              type="button"
              @click="approveSponsor(spn.sponsor_id, spn.role)"
            >
              Approve
            </button>
            <button
              class="reject"
              :data-id="spn.sponsor_id"
              data-role="sponsor"
              type="button"
              style="background-color: #e59696;"
              @click="rejectSponsor(spn.sponsor_id, spn.role)"
            >
              Reject
            </button>
          </div>
        </div>
      </div>
    </div>

    <div v-if="campaigns.length">
      <div class="details">
        <div class="top-details">
          <h1 class="h3 mb-4 text-gray-800 heading">Flagged Campaigns:</h1>
          <form id="flagged-campaigns-search-form" class="search-form">
            <input
              type="search"
              id="flagged-campaigns-search-input"
              name="q"
              class="search-text"
              placeholder="Search the Campaign"
              autocomplete="off"
              v-model="searchQuery"
            />
            <input type="submit" id="flagged-campaigns-search-button" value="" class="search-submit" />
          </form>
        </div>
        <div v-if="filteredCampaigns.length" class="detail-box">
          <div v-for="camp in filteredCampaigns" :key="camp.campaign_id" class="campaigns-box">
            <img class="profile-img" :src="camp.campaign_profile_image" alt="Profile Image" />
            <h5>{{ camp.campaign_title }}</h5>
            <button
              class="view view-campaign"
              type="button"
              @click="showCampaignDetails(camp)"
            >
              View
            </button>
            <button
              class="unflag"
              type="button"
              :data-id="camp.campaign_id"
              @click="unflag(camp.campaign_id, camp.role)"
            >
              Unflag
            </button>
          </div>
        </div>
        <div v-else>
          <div id="flagged-campaigns-no-matches" class="no-matches">
            No matched data
          </div>
        </div>
      </div>
    </div>
    <div v-else>
      <h1 class="h3 mb-4 text-gray-800 heading" style="margin-left: 3rem;">No Flagged Campaigns</h1>
    </div>

    <div v-if="sponsors.length">
      <div class="details">
        <div class="top-details">
          <h1 class="h3 mb-4 text-gray-800">Flagged Sponsors:</h1>
          <form id="flagged-sponsors-search-form" class="search-form">
            <input
              type="search"
              id="flagged-sponsors-search-input"
              name="q"
              class="search-text"
              placeholder="Search the Sponsor"
              autocomplete="off"
              v-model="searchQuery"
            />
            <input type="submit" id="flagged-sponsors-search-button" value="" class="search-submit" />
          </form>
        </div>
        <div v-if="filteredSponsors.length" class="detail-box">
          <div v-for="spn in filteredSponsors" :key="spn.sponsor_id" class="sponsors-box">
            <img class="profile-img" :src="spn.sponsor_profile_image" alt="Profile Image" />
            <h5>{{ spn.sponsor_company_name }}</h5>
            <button
              class="view view-sponsor"
              type="button"
              @click="showSponsorDetails(spn)"
            >
              View
            </button>
            <button
              class="unflag"
              type="button"
              :data-id="spn.sponsor_id"
              data-role="spn"
              @click="unflag(spn.sponsor_id, spn.role)"
            >
              Unflag
            </button>
          </div>
        </div>
        <div v-else>
          <div id="flagged-sponsors-no-matches" class="no-matches">
            No matched data
          </div>
        </div>
      </div>
    </div>
    <div v-else>
      <h1 class="h3 mb-4 text-gray-800" style="margin-left: 3rem;">No Flagged Sponsors</h1>
    </div>

    <div v-if="influencers.length">
      <div class="details">
        <div class="top-details">
          <h1 class="h3 mb-4 text-gray-800">Flagged Influencers:</h1>
          <form id="flagged-influencers-search-form" class="search-form">
            <input
              type="search"
              id="flagged-influencers-search-input"
              name="q"
              class="search-text"
              placeholder="Search the Influencer"
              autocomplete="off"
              v-model="searchQuery"
            />
            <input type="submit" id="flagged-influencers-search-button" value="" class="search-submit" />
          </form>
        </div>
        <div v-if="filteredInfluencers.length" class="detail-box">
          <div v-for="inf in filteredInfluencers" :key="inf.influencer_id" class="influencer-box">
            <img class="profile-img" :src="inf.influencer_profile_image" alt="Profile Image" />
            <h5>{{ inf.influencer_user_name }}</h5>
            <button
              class="view view-influencer"
              type="button"
              @click="showInfluencerDetails(inf)"
            >
              View
            </button>
            <button
              class="unflag"
              type="button"
              :data-id="inf.influencer_id"
              data-role="inf"
              @click="unflag(inf.influencer_id,inf.role)"
            >
              Unflag
            </button>
          </div>
        </div>
        <div v-else>
          <div id="flagged-influencers-no-matches" class="no-matches">
            No matched data
          </div>
        </div>
      </div>
    </div>
    <div v-else>
      <h1 class="h3 mb-4 text-gray-800" style="margin-left: 3rem;">No Flagged Influencers</h1>
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
