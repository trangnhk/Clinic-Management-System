const stats = window.__STATS__;
const type = window.__REPORT_TYPE__;

function drawLine(id, labels, dataset, color) {
    const c = document.getElementById(id);
    new Chart(c, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: dataset.label,
                data: dataset.data,
                borderColor: color,
                fill: false,
                tension: 0.3
            }]
        }
    });
}

function drawBar(id, labels, dataset, color) {
    const c = document.getElementById(id);
    new Chart(c, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: dataset.label,
                data: dataset.data,
                borderColor: color,
                backgroundColor: color
            }]
        }
    });
}



if ( type === "overview"){
    drawLine("chartApp", stats.labels, stats.datasets[0], '#6c757d');
    drawLine("chartRev", stats.labels, stats.datasets[1], '#e83e8c');
    drawLine("chartMed", stats.labels, stats.datasets[2], '#444');
}
else if (type === "revenue"){
    drawLine("mainChart", stats.labels, stats.datasets[0], '#e83e8c')
}
else{
    drawBar("mainChart", stats.labels, stats.datasets[0], '#e83e8c')
}





