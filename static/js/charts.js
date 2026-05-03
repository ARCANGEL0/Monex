// chart.js theme + helpers - tuned for the deus ex panels

function monexTheme() {
  Chart.defaults.color = "#7a7466";
  Chart.defaults.borderColor = "rgba(110, 86, 20, 0.18)";
  Chart.defaults.font.family = "'Rajdhani', 'Inter', sans-serif";
  Chart.defaults.font.size = 11;
  Chart.defaults.font.weight = 500;
  Chart.defaults.plugins.legend.labels.usePointStyle = true;
  Chart.defaults.plugins.legend.labels.padding = 12;
  Chart.defaults.plugins.legend.labels.color = "#7a7466";
  Chart.defaults.plugins.tooltip.backgroundColor = "rgba(20, 20, 20, 0.96)";
  Chart.defaults.plugins.tooltip.borderColor = "#6e5614";
  Chart.defaults.plugins.tooltip.borderWidth = 1;
  Chart.defaults.plugins.tooltip.titleColor = "#e8b923";
  Chart.defaults.plugins.tooltip.bodyColor = "#e8e3d3";
  Chart.defaults.plugins.tooltip.padding = 10;
  Chart.defaults.plugins.tooltip.titleFont = { family: "Rajdhani", size: 12, weight: 700 };
  Chart.defaults.plugins.tooltip.bodyFont = { family: "JetBrains Mono", size: 11 };
}

function fmtEuro(v) {
  if (typeof v !== "number") v = Number(v) || 0;
  return "€" + v.toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

function emptyState(canvas, msg) {
  const wrap = canvas.parentElement;
  wrap.replaceChildren();
  const empty = document.createElement("div");
  empty.className = "empty";
  const icon = document.createElement("div");
  icon.className = "empty__icon";
  icon.textContent = "○";
  const p = document.createElement("p");
  p.className = "dim";
  p.textContent = msg;
  empty.appendChild(icon);
  empty.appendChild(p);
  wrap.appendChild(empty);
}

const GRID_X = "rgba(110, 86, 20, 0.06)";
const GRID_Y = "rgba(110, 86, 20, 0.12)";

function eurAxis() {
  return { color: "#7a7466", callback: (v) => "€" + v };
}

// dashboard ----------------------------------------------------------

function categoryDonut(canvas, items) {
  if (!items || !items.length) return emptyState(canvas, "no expenses logged");
  return new Chart(canvas, {
    type: "doughnut",
    data: {
      labels: items.map(d => d.label),
      datasets: [{
        data: items.map(d => d.value),
        backgroundColor: items.map(d => d.color),
        borderColor: "#0a0a0a",
        borderWidth: 2,
        hoverOffset: 8,
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      cutout: "62%",
      plugins: {
        legend: { position: "right", labels: { boxWidth: 8, boxHeight: 8 } },
        tooltip: {
          callbacks: { label: (ctx) => ctx.label + ": " + fmtEuro(ctx.parsed) },
        },
      },
    },
  });
}

function bankBar(canvas, items) {
  if (!items || !items.length) return emptyState(canvas, "no bank movement");
  return new Chart(canvas, {
    type: "bar",
    data: {
      labels: items.map(d => d.label),
      datasets: [
        {
          label: "in",
          data: items.map(d => d.income),
          backgroundColor: "rgba(122, 154, 71, 0.7)",
          borderColor: "#9bb84d",
          borderWidth: 1,
        },
        {
          label: "out",
          data: items.map(d => d.expense),
          backgroundColor: "rgba(185, 28, 28, 0.6)",
          borderColor: "#dc2626",
          borderWidth: 1,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: { grid: { color: GRID_X }, ticks: { color: "#7a7466" } },
        y: { grid: { color: GRID_Y }, ticks: eurAxis() },
      },
      plugins: {
        legend: { position: "top", align: "end" },
        tooltip: {
          callbacks: { label: (ctx) => ctx.dataset.label + ": " + fmtEuro(ctx.parsed.y) },
        },
      },
    },
  });
}

// analytics ----------------------------------------------------------

function trendLine(canvas, data) {
  if (!data || !data.labels || !data.labels.length) return emptyState(canvas, "no trend data");
  return new Chart(canvas, {
    type: "line",
    data: {
      labels: data.labels,
      datasets: [
        {
          label: "income",
          data: data.income,
          borderColor: "#9bb84d",
          backgroundColor: "rgba(122, 154, 71, 0.15)",
          tension: 0.32,
          fill: true,
          borderWidth: 2,
          pointRadius: 3,
          pointBackgroundColor: "#9bb84d",
        },
        {
          label: "expense",
          data: data.expense,
          borderColor: "#dc2626",
          backgroundColor: "rgba(185, 28, 28, 0.12)",
          tension: 0.32,
          fill: true,
          borderWidth: 2,
          pointRadius: 3,
          pointBackgroundColor: "#dc2626",
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: { grid: { color: GRID_X }, ticks: { color: "#7a7466" } },
        y: { grid: { color: GRID_Y }, ticks: eurAxis() },
      },
      plugins: {
        legend: { position: "top", align: "end" },
        tooltip: {
          callbacks: { label: (ctx) => ctx.dataset.label + ": " + fmtEuro(ctx.parsed.y) },
        },
      },
    },
  });
}

function dowBar(canvas, data) {
  const has = data && data.values && data.values.some(v => v > 0);
  if (!has) return emptyState(canvas, "no expenses tracked yet");
  return new Chart(canvas, {
    type: "bar",
    data: {
      labels: data.labels,
      datasets: [{
        label: "spending",
        data: data.values,
        backgroundColor: "rgba(232, 185, 35, 0.55)",
        borderColor: "#c9a227",
        borderWidth: 1,
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: { grid: { color: GRID_X }, ticks: { color: "#7a7466" } },
        y: { grid: { color: GRID_Y }, ticks: eurAxis() },
      },
      plugins: {
        legend: { display: false },
        tooltip: { callbacks: { label: (ctx) => fmtEuro(ctx.parsed.y) } },
      },
    },
  });
}

function evolutionStack(canvas, data) {
  if (!data || !data.datasets || !data.datasets.length) {
    return emptyState(canvas, "no category data yet");
  }
  return new Chart(canvas, {
    type: "line",
    data: {
      labels: data.labels,
      datasets: data.datasets.map(ds => ({
        label: ds.label,
        data: ds.values,
        borderColor: ds.color,
        backgroundColor: ds.color + "55",
        fill: true,
        tension: 0.3,
        borderWidth: 1.5,
        pointRadius: 2,
      })),
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { mode: "index", intersect: false },
      scales: {
        x: { stacked: true, grid: { color: GRID_X }, ticks: { color: "#7a7466" } },
        y: { stacked: true, grid: { color: GRID_Y }, ticks: eurAxis() },
      },
      plugins: {
        legend: { position: "top", align: "end" },
        tooltip: {
          callbacks: { label: (ctx) => ctx.dataset.label + ": " + fmtEuro(ctx.parsed.y) },
        },
      },
    },
  });
}

function topHorizontalBar(canvas, data) {
  if (!data || !data.labels || !data.labels.length) return emptyState(canvas, "no entries");
  return new Chart(canvas, {
    type: "bar",
    data: {
      labels: data.labels,
      datasets: [{
        data: data.values,
        backgroundColor: data.colors,
        borderColor: "#0a0a0a",
        borderWidth: 1,
      }],
    },
    options: {
      indexAxis: "y",
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: { grid: { color: GRID_X }, ticks: eurAxis() },
        y: { grid: { display: false }, ticks: { color: "#7a7466" } },
      },
      plugins: {
        legend: { display: false },
        tooltip: { callbacks: { label: (ctx) => fmtEuro(ctx.parsed.x) } },
      },
    },
  });
}

// init ---------------------------------------------------------------

function initCharts() {
  if (typeof Chart === "undefined") return;
  monexTheme();

  const dataEl = document.getElementById("chart-data");
  if (!dataEl) return;
  const data = JSON.parse(dataEl.textContent);

  // dashboard
  const cat = document.getElementById("chart-category");
  if (cat) categoryDonut(cat, data.by_category || []);
  const bank = document.getElementById("chart-bank");
  if (bank) bankBar(bank, data.by_bank || []);

  // analytics
  const trend = document.getElementById("chart-trend");
  if (trend) trendLine(trend, data.trend || {});
  const dow = document.getElementById("chart-dow");
  if (dow) dowBar(dow, data.dow || {});
  const evo = document.getElementById("chart-evolution");
  if (evo) evolutionStack(evo, data.evolution || {});
  const top = document.getElementById("chart-top");
  if (top) topHorizontalBar(top, data.top || {});
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initCharts);
} else {
  initCharts();
}
