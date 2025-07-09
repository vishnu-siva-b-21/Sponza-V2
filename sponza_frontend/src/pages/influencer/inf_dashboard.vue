<script setup>
    import Base from "./inf_base.vue";
    import "../../static/influencer/styles/inf_dashboard.css"
    
    import API from "@/router/axios";
    import { onMounted,ref } from 'vue';
    import Swal from "sweetalert2";

    const isLoading = ref(false);
    const campaigns = ref([]);
    const influencer = ref({});
    const numTotalCamp = ref(0);
    const pendingRequestsCount = ref(0);

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
    
    const fetchDashboardData = async () => {
      try {
        const response = await API.get('/influencer/api/dashboard');
        const data = response.data;

        campaigns.value = data.campaigns || [];
        influencer.value = {
          id: data.influencer.id,
          name: data.influencer.name,
          income: data.influencer.income,
        };
        numTotalCamp.value = data.num_total_camp;
        pendingRequestsCount.value = data.pending_requests_count;

        fetchGraphData();
        fetchPieData();
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
      }
    };

    const leave = async (inf_id, camp_id) => {
    const result = await Swal.fire({
      title: "Are you sure?",
      text: "Do you really want to leave the campaign?",
      icon: "warning",
      showCancelButton: true,
      confirmButtonText: "Yes",
      cancelButtonText: "No, cancel!",
      reverseButtons: true
    });

  if (result.isConfirmed) {
    isLoading.value = true;

    try {
      const response = await API.delete("/influencer/rm-ad-req", {
        data: { inf_id, camp_id }, // Pass data in the `data` field
        headers: { "Content-Type": "application/json" } // Ensure content type is JSON
      });

      if (response.data.message) {
        Swal.fire({
          title: "Success",
          text: response.data.message,
          icon: "success",
          confirmButtonText: "OK"
        });
        fetchDashboardData(); // Optionally refresh the dashboard or update the UI
      } else {
        Swal.fire({
          title: "Error",
          text: response.data.error || "An error occurred.",
          icon: "error"
        });
      }
    } catch (error) {
      console.error("Error:", error);
      Swal.fire({
        title: "Error",
        text: "There was an error processing your request.",
        icon: "error"
      });
    } finally {
      isLoading.value = false;
    }
  }
};

    
    const viewDetails = (camp) => {
      Swal.fire({
        title: "Campaign Details",
        html: `
          <div style="text-align:left;">
            <p><strong>Sponsor Name:</strong> ${camp.sponsor}</p>
            <p><strong>Description:</strong> ${camp.desc}</p>
            <p><strong>End Date</strong> ${camp.end_date}</p>
            <p><strong>Campaign Amount:</strong> ${camp.camp_amt}%</p>
            <p><strong>Goals:</strong> ${camp.goals}</p>

          </div>
        `,
        icon: "info"
      });
    };


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
        const response = await API.get('/influencer/get-graph-data'); 
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
                label: 'Earnings',
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
                    labelString: 'Income',
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
        console.error(error);
        hideContainer(document.querySelector('.col-xl-8.col-lg-7'));
      }
    };


    const fetchPieData = async () => {
    try {
      const response = await API.get('/influencer/get-pie-data'); 
      const data = response.data;

      if (isPieDataEmpty(data)) {
        hideContainer(document.querySelector('.col-xl-4.col-lg-5'));
        return;
      }

      const dynamicData = {
        values: [data.your_camp, data.not_your_camp],
        labels: ['Your Campaigns', 'Rest All Campaigns'],
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
                <div class="col-xl-3 col-md-6 mb-4 content-box">
                    <div class="card border-left-primary shadow h-100 py-2">
                        <div class="card-body">
                            <div class="row no-gutters align-items-center">
                                <div class="col mr-2">
                                    <div class="text-xs font-weight-bold text-primary text-uppercase mb-1">
                                        Total Number of Campaigns</div>
                                    <div class="h5 mb-0 font-weight-bold text-gray-800">{{numTotalCamp}}</div>
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
                                        Current Income</div>
                                    <div class="h5 mb-0 font-weight-bold text-gray-800">{{influencer.income}}</div>
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
                                    <div class="text-xs font-weight-bold text-info text-uppercase mb-1">
                                        My Campaigns
                                    </div>
                                    <div class="row no-gutters align-items-center">
                                        <div class="col-auto">
                                            <div class="h5 mb-0 mr-3 font-weight-bold text-gray-800">{{ campaigns.length }}</div>
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
                                        Pending Request</div>
                                    <div class="h5 mb-0 font-weight-bold text-gray-800">{{pendingRequestsCount}}</div>
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
                        <div class="card-body">
                            <div class="chart-pie pt-4 pb-2" id="chartPie" data-labels='["Influencer", "Sponsor"]'>
                                <canvas id="myPieChart"></canvas>
                            </div>
                        </div>
                    </div>
                </div>
                </div>
        </div>

        <div>
          <div v-if="campaigns.length > 0" class="details">
            <div class="ongoing-cp">
              <h1 class="h3 mb-0 text-gray-800 heading" style="width: 47vh;">Ongoing Campaigns:</h1>
            </div>
            <div v-for="camp in campaigns" :key="camp.id" class="campaigns-details">
              <div class="campaigns-details-1">
                <img class="profile-img ongoing-campaign-profile" :src="camp.image" alt="Profile Image" />
                <div class="item-2 item">
                  {{ camp.title }}
                  <span v-if="camp.flag === 'True'" style="color: red;">- Flagged</span>
                </div>
                <div class="item-3 item">
                  <div class="progress pg-1">
                    <div
                      class="progress-bar bg-success progress-bar-striped progress-bar-animated"
                      :style="{ width: camp.progress + '%' }"
                    ></div>
                  </div>
                </div>
                <button class="views" type="button" 
                  @click = "viewDetails(camp)"
                >
                  View
                </button>
                <button id="leave" class="leave" type="button" 
                  :data-inf-id="influencer.id" 
                  :data-camp-id="camp.id"
                  @click="leave(influencer.id,camp.id)"
                >
                  Leave
                </button>
              </div>
            </div>
          </div>
          <div v-else>
            <h1 class="h3 mb-0 text-gray-800" style="width: 47vh; padding-left: 1vh;">No Ongoing Campaigns</h1>
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
