function chartColors() {
    const dark = document.documentElement.getAttribute("data-theme") === "dark";
    return {
        text: dark ? "#eef3fb" : "#0f172a",
        grid: dark ? "rgba(255,255,255,0.08)" : "rgba(15,23,42,0.08)",
        line: "#4f46e5",
        fill: "rgba(79,70,229,0.18)",
    };
}

function drawLineChart(id, labels, data, label) {
    const el = document.getElementById(id);
    if (!el || typeof Chart === "undefined") return;
    const c = chartColors();
    new Chart(el, {
        type: "line",
        data: {
            labels: labels,
            datasets: [{
                label: label,
                data: data,
                borderColor: c.line,
                backgroundColor: c.fill,
                fill: true,
                tension: 0.35,
                pointRadius: 4,
            }],
        },
        options: {
            plugins: { legend: { display: false } },
            scales: {
                y: { min: 0, max: 100, ticks: { color: c.text }, grid: { color: c.grid } },
                x: { ticks: { color: c.text }, grid: { display: false } },
            },
        },
    });
}

function drawBarChart(id, labels, data) {
    const el = document.getElementById(id);
    if (!el || typeof Chart === "undefined") return;
    const c = chartColors();
    new Chart(el, {
        type: "bar",
        data: {
            labels: labels,
            datasets: [{ data: data, backgroundColor: "#4f46e5", borderRadius: 8 }],
        },
        options: {
            plugins: { legend: { display: false } },
            scales: {
                y: { min: 0, max: 100, ticks: { color: c.text }, grid: { color: c.grid } },
                x: { ticks: { color: c.text }, grid: { display: false } },
            },
        },
    });
}

function drawRadarChart(id, labels, data) {
    const el = document.getElementById(id);
    if (!el || typeof Chart === "undefined") return;
    const c = chartColors();
    new Chart(el, {
        type: "radar",
        data: {
            labels: labels,
            datasets: [{
                data: data,
                borderColor: c.line,
                backgroundColor: c.fill,
            }],
        },
        options: {
            plugins: { legend: { display: false } },
            scales: {
                r: {
                    min: 0,
                    max: 100,
                    ticks: { display: false },
                    grid: { color: c.grid },
                    pointLabels: { color: c.text },
                },
            },
        },
    });
}
