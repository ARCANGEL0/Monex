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

function withAlpha(hex, aHex) {
  if (typeof hex !== "string" || hex[0] !== "#" || hex.length !== 7) return hex;
  return hex + aHex;
}

function eurAxis() {
  return { color: "#7a7466", callback: (v) => "€" + v };
}

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
        tooltip: { callbacks: { label: (ctx) => ctx.label + ": " + fmtEuro(ctx.parsed) } },
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
          backgroundColor: "rgba(122, 154, 71, 0.08)",
          borderColor: "#9bb84d",
          borderWidth: 2.5,
          borderRadius: 1,
          hoverBackgroundColor: "rgba(122, 154, 71, 0.18)",
        },
        {
          label: "out",
          data: items.map(d => d.expense),
          backgroundColor: "rgba(220, 38, 38, 0.08)",
          borderColor: "#dc2626",
          borderWidth: 2.5,
          borderRadius: 1,
          hoverBackgroundColor: "rgba(220, 38, 38, 0.20)",
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
        tooltip: { callbacks: { label: (ctx) => ctx.dataset.label + ": " + fmtEuro(ctx.parsed.y) } },
      },
    },
  });
}

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
        tooltip: { callbacks: { label: (ctx) => ctx.dataset.label + ": " + fmtEuro(ctx.parsed.y) } },
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
        backgroundColor: "rgba(252, 211, 77, 0.08)",
        borderColor: "#fcd34d",
        borderWidth: 2.5,
        borderRadius: 1,
        hoverBackgroundColor: "rgba(252, 211, 77, 0.20)",
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
  if (!data || !data.datasets || !data.datasets.length) return emptyState(canvas, "no category data yet");
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
        tooltip: { callbacks: { label: (ctx) => ctx.dataset.label + ": " + fmtEuro(ctx.parsed.y) } },
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
        backgroundColor: data.colors.map(c => withAlpha(c, "1a")),
        borderColor: data.colors,
        borderWidth: 2.5,
        borderRadius: 1,
        hoverBackgroundColor: data.colors.map(c => withAlpha(c, "44")),
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

function monthlyDonut(canvas, data) {
  if (!data || !data.labels || !data.labels.length) return emptyState(canvas, "no expenses this month");
  return new Chart(canvas, {
    type: "doughnut",
    data: {
      labels: data.labels,
      datasets: [{
        data: data.values,
        backgroundColor: data.colors.map(c => withAlpha(c, "55")),
        borderColor: data.colors,
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
        tooltip: { callbacks: { label: (ctx) => ctx.label + ": " + fmtEuro(ctx.parsed) } },
      },
    },
  });
}

function catComparison(canvas, data) {
  if (!data || !data.labels || !data.labels.length) return emptyState(canvas, "no data yet");
  return new Chart(canvas, {
    type: "bar",
    data: {
      labels: data.labels,
      datasets: [
        {
          label: "last month",
          data: data.last_month,
          backgroundColor: "rgba(122, 116, 102, 0.15)",
          borderColor: "#7a7466",
          borderWidth: 2,
          borderRadius: 1,
        },
        {
          label: "this month",
          data: data.this_month,
          backgroundColor: "rgba(252, 211, 77, 0.15)",
          borderColor: "#fcd34d",
          borderWidth: 2,
          borderRadius: 1,
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
        datasetGlow: { enabled: true, blur: 12 },
        legend: { position: "top", align: "end" },
        tooltip: { callbacks: { label: (ctx) => ctx.dataset.label + ": " + fmtEuro(ctx.parsed.y) } },
      },
    },
  });
}

function dailyBars(canvas, data) {
  if (!data || !data.labels || !data.labels.length) return emptyState(canvas, "no daily data");
  return new Chart(canvas, {
    type: "bar",
    data: {
      labels: data.labels,
      datasets: [{
        data: data.values,
        backgroundColor: "rgba(252, 211, 77, 0.10)",
        borderColor: "#fcd34d",
        borderWidth: 2,
        borderRadius: 1,
        hoverBackgroundColor: "rgba(252, 211, 77, 0.25)",
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: { grid: { color: GRID_X }, ticks: { color: "#7a7466", maxRotation: 0, maxTicksLimit: 15 } },
        y: { grid: { color: GRID_Y }, ticks: eurAxis() },
      },
      plugins: {
        datasetGlow: { enabled: true, blur: 14, color: "rgba(252, 211, 77, 0.5)" },
        legend: { display: false },
        tooltip: { callbacks: { label: (ctx) => "Day " + ctx.label + ": " + fmtEuro(ctx.parsed.y) } },
      },
    },
  });
}

function weeklyBars(canvas, data) {
  if (!data || !data.labels || !data.labels.length) return emptyState(canvas, "no weekly data");
  return new Chart(canvas, {
    type: "bar",
    data: {
      labels: data.labels,
      datasets: [{
        data: data.values,
        backgroundColor: "rgba(252, 211, 77, 0.12)",
        borderColor: "#fcd34d",
        borderWidth: 2,
        borderRadius: 2,
        hoverBackgroundColor: "rgba(252, 211, 77, 0.28)",
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
        datasetGlow: { enabled: true, blur: 16, color: "rgba(252, 211, 77, 0.5)" },
        legend: { display: false },
        tooltip: { callbacks: { label: (ctx) => ctx.label + ": " + fmtEuro(ctx.parsed.y) } },
      },
    },
  });
}

function burnRate(canvas, data) {
  if (!data || !data.labels || !data.labels.length) return emptyState(canvas, "no burn data");
  return new Chart(canvas, {
    type: "line",
    data: {
      labels: data.labels,
      datasets: [
        {
          label: "actual",
          data: data.cumulative,
          borderColor: "#fcd34d",
          backgroundColor: "rgba(252, 211, 77, 0.08)",
          tension: 0.2,
          fill: true,
          borderWidth: 2.5,
          pointRadius: 3,
          pointHoverRadius: 6,
          pointBackgroundColor: "#fcd34d",
          pointBorderColor: "#0a0a0a",
          pointBorderWidth: 1,
        },
        {
          label: "projected",
          data: data.projected,
          borderColor: "rgba(122, 116, 102, 0.45)",
          borderDash: [5, 4],
          tension: 0,
          fill: false,
          borderWidth: 1.5,
          pointRadius: 0,
          pointHoverRadius: 4,
          pointBackgroundColor: "#7a7466",
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: { grid: { color: GRID_X }, ticks: { color: "#7a7466", maxTicksLimit: 10 } },
        y: { grid: { color: GRID_Y }, ticks: eurAxis() },
      },
      plugins: {
        datasetGlow: { enabled: true, blur: 16, color: "rgba(252, 211, 77, 0.5)" },
        legend: { position: "top", align: "end" },
        tooltip: { callbacks: { label: (ctx) => ctx.dataset.label + ": " + fmtEuro(ctx.parsed.y) } },
      },
    },
  });
}

function categoryMovers(canvas, data) {
  if (!data || !data.labels || !data.labels.length) return emptyState(canvas, "no mover data");
  return new Chart(canvas, {
    type: "bar",
    data: {
      labels: data.labels,
      datasets: [{
        label: "change",
        data: data.deltas,
        backgroundColor: data.deltas.map(d => d >= 0 ? "rgba(220, 38, 38, 0.18)" : "rgba(122, 154, 71, 0.18)"),
        borderColor: data.deltas.map(d => d >= 0 ? "#dc2626" : "#9bb84d"),
        borderWidth: 2,
        borderRadius: 2,
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: { grid: { color: GRID_X }, ticks: { color: "#7a7466" } },
        y: { grid: { color: GRID_Y }, ticks: Object.assign(eurAxis(), { callback: v => (v >= 0 ? "+" : "") + fmtEuro(v) } ) },
      },
      plugins: {
        datasetGlow: { enabled: true, blur: 14 },
        legend: { display: false },
        tooltip: { callbacks: { label: (ctx) => (ctx.parsed.y >= 0 ? "+" : "") + fmtEuro(ctx.parsed.y) } },
      },
    },
  });
}

const __charts = {};

function killOld() {
  Object.keys(__charts).forEach(id => {
    if (__charts[id]) __charts[id].destroy();
    delete __charts[id];
  });
}

function track(id, c) { if (c) __charts[id] = c; }

var _themeSet = false;

function initCharts() {
  if (typeof Chart === "undefined") {
    console.error("Chart.js not loaded");
    return;
  }
  try {
    if (!_themeSet) { 
      Chart.register(datasetGlow);
      monexTheme(); 
      _themeSet = true;
    }
    killOld();

    var data = window.__chartData;
    if (!data) {
      console.error("No chart data");
      return;
    }

    // Create charts with error handling
    var chartIds = [
      { id: "chart-trend", fn: trendLine, chartData: data.trend },
      { id: "chart-evolution", fn: evolutionStack, chartData: data.evolution },
      { id: "chart-top", fn: topHorizontalBar, chartData: data.top },
      { id: "chart-cat-comparison", fn: catComparison, chartData: data.cat_comparison },
      { id: "chart-burn-rate", fn: burnRate, chartData: data.burn_rate },
      { id: "chart-weekly", fn: weeklyBars, chartData: data.weekly },
      { id: "chart-movers", fn: categoryMovers, chartData: data.movers },
    ];

    chartIds.forEach(function(cfg) {
      var canvas = document.getElementById(cfg.id);
      if (!canvas) {
        return;
      }
      try {
        if (cfg.chartData && ((cfg.chartData.labels && cfg.chartData.labels.length) || (cfg.chartData.values && cfg.chartData.values.length) || (cfg.chartData.datasets && cfg.chartData.datasets.length))) {
          var chart = cfg.fn(canvas, cfg.chartData);
          track(cfg.id, chart);
          if (chart) {
            console.log("Chart created: " + cfg.id);
          }
        } else {
          emptyState(canvas, "no data");
        }
      } catch(e) {
        console.error("Error creating chart " + cfg.id + ":", e);
      }
    });
  } catch(e) {
    console.error("initCharts error:", e);
  }
}

// Charts are initialized by inline scripts in fragments after chart data is set
