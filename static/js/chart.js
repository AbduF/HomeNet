// HomeNet Traffic Monitoring with Chart.js
let trafficChart = null;
let trafficData = {
    labels: [],
    datasets: [
        {
            label: 'Bytes Sent',
            data: [],
            borderColor: '#2563EB',
            backgroundColor: 'rgba(37, 99, 235, 0.1)',
            tension: 0.1
        },
        {
            label: 'Bytes Received',
            data: [],
            borderColor: '#10B981',
            backgroundColor: 'rgba(16, 185, 129, 0.1)',
            tension: 0.1
        }
    ]
};

function initTrafficChart() {
    const ctx = document.getElementById('trafficChart');
    if (!ctx) return;

    if (trafficChart) {
        trafficChart.destroy();
    }

    trafficChart = new Chart(ctx, {
        type: 'line',
        data: trafficData,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Bytes'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Time'
                    }
                }
            },
            plugins: {
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `${context.dataset.label}: ${formatBytes(context.raw)}`;
                        }
                    }
                }
            }
        }
    });
}

function formatBytes(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function updateTrafficChart() {
    fetch('/api/traffic?limit=20', {
        headers: { 'Authorization': 'Basic ' + btoa('admin:123456') }
    })
    .then(response => response.json())
    .then(data => {
        trafficData.labels = data.map(item => new Date(item.timestamp).toLocaleTimeString());
        trafficData.datasets[0].data = data.map(item => item.bytes_sent);
        trafficData.datasets[1].data = data.map(item => item.bytes_received);

        if (trafficChart) {
            trafficChart.update();
        } else {
            initTrafficChart();
        }
    })
    .catch(error => {
        console.error('Error fetching traffic data:', error);
    });
}

// Initialize chart when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initTrafficChart();
    updateTrafficChart();
    setInterval(updateTrafficChart, 10000); // Update every 10 seconds
});