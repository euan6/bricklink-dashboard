// script for theme breakdown ring chart
const themeData = JSON.parse(document.getElementById('chart-data').textContent);

new Chart(document.getElementById('themeChart'), {
    type: 'doughnut',
    data: {
        labels: Object.keys(themeData),
        datasets: [{
            data: Object.values(themeData),
            backgroundColor: [
                '#f0c040', '#4a9eff', '#5dcaa5', '#c084fc',
                '#f97316', '#ec4899', '#14b8a6', '#a3e635',
                '#1c72d3', '#c6e635', '#ff520e', '#852ae1',
                '#1fe12c', '#cc0088'
            ],
            borderWidth: 0,
            hoverOffset: 4
        }]
    },
    options: {
        plugins: {
            legend: {
                position: 'bottom',
                labels: {
                    padding: 12,
                    boxWidth: 10,
                    boxHeight: 10,
                    color: '#aaa',
                    font: {
                        size: 11,
                        family: "'Inter', sans-serif"
                    }
                }
            }
        },
        cutout: '65%',
        responsive: true,
        maintainAspectRatio: false,
        animation: { duration: 600 }
    }
});

// script for yearly distribution bar chart
const yearData = JSON.parse(document.getElementById('year-data').textContent);

new Chart(document.getElementById('yearChart'), {
    type: 'bar',
    data: {
        labels: Object.keys(yearData),
        datasets: [{
            data: Object.values(yearData),
            backgroundColor: '#f0c040',
            borderRadius: 4,
            borderSkipped: false
        }]
    },
    options: {
        plugins: {
            legend: { display: false }
        },
        scales: {
            x: {
                grid: { display: false },
                ticks: {
                    color: '#888',
                    font: { size: 11, family: "'Inter', sans-serif" }
                },
                border: { display: false }
            },
            y: {
                grid: { color: '#1f1f2e' },
                ticks: {
                    color: '#888',
                    stepSize: 1,
                    font: { size: 11, family: "'Inter', sans-serif" }
                },
                border: { display: false }
            }
        },
        responsive: true,
        maintainAspectRatio: false,
        animation: { duration: 600 }
    }
});
