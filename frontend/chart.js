// Function to fetch and render the chart data
function fetchChartData(query) {
  fetch(http://127.0.0.1:3000/chart/${query})
    .then(response => response.json())
    .then(data => {
      renderChart(data);  // Pass the data to renderChart function
    })
    .catch(error => console.error("Error fetching data:", error));
}

// Function to render the chart
function renderChart(data) {
  const ctx = document.getElementById('chartCanvas').getContext('2d');
  const chart = new Chart(ctx, {
    type: 'bar',  // Change to 'line', 'pie', etc. depending on your needs
    data: {
      labels: data.labels,  // The x-axis labels (e.g., months, regions, products)
      datasets: [{
        label: 'Sales Data',
        data: data.values,  // The values corresponding to the labels
        backgroundColor: 'rgba(54, 162, 235, 0.2)',  // Customize as needed
        borderColor: 'rgba(54, 162, 235, 1)',
        borderWidth: 1
      }]
    },
    options: {
      responsive: true,
      animation: {
        duration: 2000,
        easing: "easeInOutBounce"
      },
      plugins: {
        legend: {
          display: true,
          position: "top",
          labels: {
            color: "#333",
            font: { size: 14 },
          }
        }
      },
      scales: {
        y: {
          beginAtZero: true  // Ensures that the y-axis starts at 0
        }
      }
    }
  });
}

// Event listener for query selection
function setupQuerySelection() {
  const querySelector = document.getElementById("querySelect");
  querySelector.addEventListener("change", function() {
    const queryName = querySelector.value;
    fetchChartData(queryName);  // Fetch and render chart based on selected query
  });
}

// Set up the dropdown and initial chart load
window.onload = function() {
  setupQuerySelection();
  fetchChartData("Monthly Sales");  // Initial chart load with "Monthly Sales"
}