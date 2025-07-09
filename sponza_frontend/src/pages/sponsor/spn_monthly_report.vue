<script setup>
  import "../../static/common/styles/common_main.css";
  import "../../static/common/scripts/common_main.js"; 
  import "../../static/sponsor/styles/sponsor_monthly_report.css"
  import axios from "axios";
  import { ref, onMounted } from "vue";
  import { useRoute } from 'vue-router';

  const route = useRoute();
  const id = ref("");
  const month = ref("");
  const year = ref("");

  const isLoading = ref(false);
  const campaigns = ref([]);

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

  const fetchCampaigns = async () => {
  try {
  let link = `http://127.0.0.1:5000/sponsor/monthly-report-data/${id.value}/${month.value}/${year.value}`
  const response = await axios.get(link);
  const data = response.data;

  campaigns.value = data.campaigns || [];
  } catch (error) {
  console.error('Error fetching campaigns data:', error);
  }
  };

  function hideContainer(container) {
    container.style.display = "none";
  }

  function isDataEmpty(data) {
    return Object.keys(data).length === 0;
  }

  const fetchGraphData = async () => {
    try {
      isLoading.value = true;
      const response = await axios.get(`http://127.0.0.1:5000/sponsor/get-monthly-report-graph-data/${id.value}/${month.value}/${year.value}`); 
      const data = response.data;
      console.log(data)
      
      if (isDataEmpty(data)) {
        hideContainer(document.querySelector('.col-xl-8.col-lg-7'));
        return;
      }
      isLoading.value = false;

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
      isLoading.value = false;
      console.error(error);
      hideContainer(document.querySelector('.col-xl-8.col-lg-7'));
    }
  };

  onMounted(() => {
    id.value = route.query.id; 
    month.value = route.query.month;
    year.value = route.query.year;
    fetchCampaigns();
    fetchGraphData();
  });
</script>


<template>
    <div v-if="isLoading" class="loading-overlay">
        <div class="spinner"></div>
    </div>
    <div v-if="campaigns.length">
      <h2><b>Campaign Details</b></h2>
      <div class="table-container">
          <table>
              <thead>
                  <tr>
                      <th>Campaign Name</th>
                      <th>Description</th>
                      <th>Start Date</th>
                      <th>End Date</th>
                      <th>Budget</th>
                      <th>Visibility</th>
                      <th>Goals</th>
                  </tr>
              </thead>
              <tbody>
                  <tr v-for="(campaign, index) in campaigns" :key="index">
                      <td>{{ campaign.title }}</td>
                      <td>{{ campaign.desc }}</td>
                      <td>{{ campaign.start_date }}</td>
                      <td>{{ campaign.end_date }}</td>
                      <td>{{ campaign.budget }}</td>
                      <td>{{ campaign.visiblity }}</td>
                      <td>{{ campaign.goals }}</td>
                  </tr>
              </tbody>
          </table>
      </div>
    </div>
    <div class="expired" v-else>
        <p class="expired-icon">📄❌</p>
        <p class="expired-title">Report Unavailable</p>
        <p class="expired-description">
            The report you are trying to access is no longer available. Please contact support or try again later.
        </p>
    </div>
    <div class="col-xl-8 col-lg-7 chart-container">
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
</template>
