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

// per-dataset neon glow plugin
// configure via options.plugins.datasetGlow = { enabled, blur, color }
// if color is omitted, uses the dataset's borderColor (single-color datasets only)
const datasetGlow = {
  id: "datasetGlow",
  beforeDatasetDraw(chart, args) {
    const cfg = chart.options.plugins && chart.options.plugins.datasetGlow;
    if (!cfg || !cfg.enabled) return;
    let color = cfg.color;
    if (!color) {
      const ds = chart.data.datasets[args.index];
      const bc = ds.borderColor;
      color = (typeof bc === "string") ? bc : "#fcd34d";
    }
    chart.ctx.save();
    chart.ctx.shadowBlur = cfg.blur != null ? cfg.blur : 14;
    chart.ctx.shadowColor = color;
  },
  afterDatasetDraw(chart) {
    const cfg = chart.options.plugins && chart.options.plugins.datasetGlow;
    if (cfg && cfg.enabled) chart.ctx.restore();
  },
};

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

// alpha helper: appends 8-bit hex alpha to a #rrggbb color
function withAlpha(hex, aHex) {
  if (typeof hex !== "string" || hex[0] !== "#" || hex.length !== 7) return hex;
  return hex + aHex;
}

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
        backgroundColor: items.map(d => withAlpha(d.color, "55")),
        borderColor: items.map(d => d.color),
        borderWidth: 2.5,
        hoverOffset: 14,
        hoverBorderWidth: 3,
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      cutout: "62%",
      plugins: {
        datasetGlow: { enabled: true, blur: 20, color: "rgba(232, 185, 35, 0.65)" },
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
          backgroundColor: "rgba(122, 154, 71, 0.22)",
          borderColor: "#9bb84d",
          borderWidth: 2,
          borderRadius: 2,
        },
        {
          label: "out",
          data: items.map(d => d.expense),
          backgroundColor: "rgba(220, 38, 38, 0.20)",
          borderColor: "#dc2626",
          borderWidth: 2,
          borderRadius: 2,
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
        datasetGlow: { enabled: true, blur: 14 },
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
          backgroundColor: "rgba(122, 154, 71, 0.10)",
          tension: 0.32,
          fill: true,
          borderWidth: 2.5,
          pointRadius: 4,
          pointHoverRadius: 7,
          pointBackgroundColor: "#9bb84d",
          pointBorderColor: "#0a0a0a",
          pointBorderWidth: 1.5,
        },
        {
          label: "expense",
          data: data.expense,
          borderColor: "#dc2626",
          backgroundColor: "rgba(220, 38, 38, 0.08)",
          tension: 0.32,
          fill: true,
          borderWidth: 2.5,
          pointRadius: 4,
          pointHoverRadius: 7,
          pointBackgroundColor: "#dc2626",
          pointBorderColor: "#0a0a0a",
          pointBorderWidth: 1.5,
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
        datasetGlow: { enabled: true, blur: 16 },
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
        backgroundColor: "rgba(252, 211, 77, 0.18)",
        borderColor: "#fcd34d",
        borderWidth: 2,
        borderRadius: 2,
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
        datasetGlow: { enabled: true, blur: 18, color: "rgba(252, 211, 77, 0.7)" },
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
        backgroundColor: withAlpha(ds.color, "33"),
        fill: true,
        tension: 0.3,
        borderWidth: 2,
        pointRadius: 3,
        pointHoverRadius: 6,
        pointBackgroundColor: ds.color,
        pointBorderColor: "#0a0a0a",
        pointBorderWidth: 1,
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
        datasetGlow: { enabled: true, blur: 12 },
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
        backgroundColor: data.colors.map(c => withAlpha(c, "33")),
        borderColor: data.colors,
        borderWidth: 2,
        borderRadius: 2,
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
        datasetGlow: { enabled: true, blur: 18, color: "rgba(232, 185, 35, 0.55)" },
        legend: { display: false },
        tooltip: { callbacks: { label: (ctx) => fmtEuro(ctx.parsed.x) } },
      },
    },
  });
}

// init ---------------------------------------------------------------

function initCharts() {
  if (typeof Chart === "undefined") return;
  Chart.register(datasetGlow);
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
