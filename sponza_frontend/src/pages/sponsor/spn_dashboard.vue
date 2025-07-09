<script setup>
    import Base from "./spn_base.vue";
    import "../../static/sponsor/styles/sponsor_dashboard.css"
    import API from "@/router/axios";
    import { onMounted,ref, reactive } from 'vue';
    import Swal from "sweetalert2";
    import * as XLSX from "xlsx";

    const dashboardData = reactive({
      sponsor_name: "",
      user_num_camp: 0,
      num_camp: 0,
      total_expenses: 0,
      num_pending_requests: 0,
      campaigns: [],
    });
    const campaigns = ref([]);
    const isLoading = ref(false);

    
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

    function isPieDataEmpty(object) {
      const arr = Object.values(object);
      const isAllZeros = arr.every(item => item === 0);
      return isAllZeros;
    }

    const fetchGraphData = async () => {
      try {
        const response = await API.get('/sponsor/get-graph-data'); // No need for headers
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
      const response = await API.get('/sponsor/get-pie-data'); // No need for headers
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

    const fetchDashboardData = async () => {
      try {
        const response = await API.get("/sponsor/api/dashboard");
        Object.assign(dashboardData, response.data);
      } catch (error) {
        console.error("Error fetching dashboard data:", error);
      }
    };

    const generateReport = async () => {
      isLoading.value = true;
      const createExcelFile = () => {
        const worksheet = XLSX.utils.json_to_sheet(dashboardData.campaigns);
        const workbook = XLSX.utils.book_new();
        XLSX.utils.book_append_sheet(workbook, worksheet, "Campaigns");
        const excelData = XLSX.write(workbook, { bookType: "xlsx", type: "array" });
        const blob = new Blob([excelData], { type: "application/octet-stream" });
        const url = URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = url;
        link.download = "Report.xlsx";
        link.click();
        URL.revokeObjectURL(url);
      };
      isLoading.value = false;
      Swal.fire({
        title: "Report Generated Successfully",
        icon: "success",
        showCancelButton: true,
        confirmButtonText: "Download Report",
      }).then((result) => {
        if (result.isConfirmed) {
          createExcelFile();
        }
      });
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
                <div class="col-xl-3 col-md-6 mb-4">
                    <div class="card border-left-primary shadow h-100 py-2">
                        <div class="card-body">
                            <div class="row no-gutters align-items-center">
                                <div class="col mr-2">
                                    <div class="text-xs font-weight-bold text-primary text-uppercase mb-1">
                                        Total Campaigns</div>
                                    <div class="h5 mb-0 font-weight-bold text-gray-800">{{dashboardData.num_camp}}</div>
                                </div>
                                <div class="col-auto">
                                    <i class="fas fa-calendar fa-2x text-gray-300"></i>
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
                                    <div class="text-xs font-weight-bold text-info text-uppercase mb-1">Total Ad
                                        Spend
                                    </div>
                                    <div class="row no-gutters align-items-center">
                                        <div class="col-auto">
                                            <div class="h5 mb-0 mr-3 font-weight-bold text-gray-800">{{dashboardData.total_expenses}}</div>
                                        </div>

                                    </div>
                                </div>
                                <div class="col-auto">
                                    <i class="fa-solid fa-indian-rupee-sign fa-2x text-gray-300"></i>
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
                                        My Campaigns</div>
                                    <div class="h5 mb-0 font-weight-bold text-gray-800">{{dashboardData.user_num_camp}}</div>
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
                                        Pending Requests</div>
                                    <div class="h5 mb-0 font-weight-bold text-gray-800">
                                        {{dashboardData.num_pending_requests}}
                                    </div>
                                </div>
                                <div class="col-auto">
                                    <i class="fas fa-comments fa-2x text-gray-300"></i>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="row">
                    <div class="col-xl-8 col-lg-7">
                        <div class="card shadow mb-4 card-box">

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
                        <div class="card shadow mb-4 pie card-box">

                            <div class="card-header py-3 d-flex flex-row align-items-center justify-content-between">
                                <h6 class="m-0 font-weight-bold text-primary">User Type Split</h6>
                            </div>

                            <div class="card-body pie-body">
                                <div class="chart-pie pt-4 pb-2" id="chartPie">
                                    <canvas id="myPieChart"></canvas>
                                </div>
                            </div>
                        </div>
                    </div>

                </div>
            </div>
        </div>

      <div v-if="dashboardData.campaigns.length > 0" class="details">
        <div class="ongoing-cp">
          <h1 class="h3 mb-0 text-gray-800 heading">Ongoing Campaigns:</h1>
          <button id="export-campaign" @click="generateReport" class="export-button">Generate report as CSV</button>
        </div>
        <div v-for="camp in dashboardData.campaigns" :key="camp.id" class="campaigns-details">
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
          </div>
        </div>
      </div>
      <div v-else>
        <h1 class="h3 mb-0 text-gray-800" style="width: 47vh; padding-left: 1vh;">No Ongoing Campaigns</h1>
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
