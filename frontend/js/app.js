const API_BASE = '/api';

const DASHBOARD_STORAGE_KEY = 'silverGoldActiveDashboard';

function toggleSidebar(open) {
  const sidebar = document.getElementById('sidebar');
  const overlay = document.getElementById('sidebarOverlay');
  if (!sidebar || !overlay) return;
  if (open) {
    sidebar.classList.add('open');
    overlay.classList.add('active');
  } else {
    sidebar.classList.remove('open');
    overlay.classList.remove('active');
  }
}

document.querySelectorAll('.sidebar .nav-item').forEach((link) => {
  link.addEventListener('click', () => {
    if (window.innerWidth <= 768) toggleSidebar(false);
  });
});

function updateNav(element) {
  document.querySelectorAll('.nav-item').forEach((el) => el.classList.remove('active'));
  element.classList.add('active');
  const title = element.innerText.trim();
  document.getElementById('current-view-title').innerText = title + ' Overview';
}

window.addEventListener('scroll', () => {
  const sections = document.querySelectorAll('.content-section');
  const navItems = document.querySelectorAll('.nav-item');

  let current = '';
  sections.forEach((section) => {
    const sectionTop = section.offsetTop;
    if (pageYOffset >= sectionTop - 200) {
      current = section.getAttribute('id');
    }
  });

  navItems.forEach((item) => {
    item.classList.remove('active');
    if (item.getAttribute('href').includes(current)) {
      item.classList.add('active');
      document.getElementById('current-view-title').innerText = item.innerText.trim() + ' Overview';
    }
  });
});

const formatter = new Intl.NumberFormat('en-US', {
  style: 'currency',
  currency: 'USD',
});

let activeDashboard = sessionStorage.getItem(DASHBOARD_STORAGE_KEY) || 'silver';

function setActiveDashboard(asset, btn) {
  activeDashboard = asset;
  sessionStorage.setItem(DASHBOARD_STORAGE_KEY, asset);

  document.querySelectorAll('.dashboard-switch-btn').forEach((b) => {
    const on = b.getAttribute('data-asset') === asset;
    b.classList.toggle('active', on);
    b.setAttribute('aria-selected', on ? 'true' : 'false');
  });

  const silverPanel = document.getElementById('dashboard-panel-silver');
  const goldPanel = document.getElementById('dashboard-panel-gold');
  if (silverPanel && goldPanel) {
    silverPanel.classList.toggle('hidden', asset !== 'silver');
    goldPanel.classList.toggle('hidden', asset !== 'gold');
  }

  const predSilver = document.getElementById('predictions-panel-silver');
  const predGold = document.getElementById('predictions-panel-gold');
  if (predSilver && predGold) {
    predSilver.classList.toggle('hidden', asset !== 'silver');
    predGold.classList.toggle('hidden', asset !== 'gold');
  }

  const calc = document.getElementById('calcAsset');
  if (calc) calc.value = asset;

  loadDashboardForAsset(asset);
}

function loadDashboardForAsset(asset) {
  const color = asset === 'silver' ? 'rgba(99, 102, 241, 1)' : 'rgba(245, 158, 11, 1)';
  const canvasId = asset === 'silver' ? 'silverChart' : 'goldChart';

  fetch(`${API_BASE}/prices/${asset}/latest`)
    .then((r) => r.json())
    .then((payload) => {
      const elId = asset === 'silver' ? 'silverPrice' : 'goldPrice';
      const metaId = asset === 'silver' ? 'silverPriceMeta' : 'goldPriceMeta';
      const node = document.getElementById(elId);
      const meta = document.getElementById(metaId);
      if (payload.data && payload.data.close != null && node) {
        node.innerText = formatter.format(payload.data.close);
        if (meta && payload.data.date) {
          meta.innerText = `As of ${payload.data.date}`;
          meta.className = 'stat-change positive';
        }
      } else if (node) {
        node.innerText = '—';
        if (meta) {
          meta.innerText = 'No data (check API / MongoDB)';
          meta.className = 'stat-change negative';
        }
      }
    })
    .catch(() => {
      const elId = asset === 'silver' ? 'silverPrice' : 'goldPrice';
      const node = document.getElementById(elId);
      if (node) node.innerText = 'Error';
    });

  const rangeBtn = document.querySelector(`#dashboard-panel-${asset} .chart-actions .btn.active`);
  const label = rangeBtn ? rangeBtn.textContent.trim() : 'All';
  const range = label === '24h' ? 'daily' : mapRangeLabel(label);
  fetchAndRender(asset, range, canvasId, color);
}

function mapRangeLabel(label) {
  if (label === '1M') return 'monthly';
  if (label === '1W') return 'weekly';
  if (label === '24h') return 'daily';
  if (label === 'All') return 'all';
  return 'all';
}

async function loadDashboard() {
  try {
    await Promise.all([
      fetch(`${API_BASE}/prices/silver/latest`).then((r) => r.json()).then(updatePriceCard('silver')),
      fetch(`${API_BASE}/prices/gold/latest`).then((r) => r.json()).then(updatePriceCard('gold')),
    ]);
  } catch (err) {
    console.error('Failed to load prices:', err);
  }

  const initial = activeDashboard;
  const switchBtn = document.querySelector(`.dashboard-switch-btn[data-asset="${initial}"]`);
  setActiveDashboard(initial, switchBtn || document.querySelector('.dashboard-switch-btn[data-asset="silver"]'));
  
  // Auto-trigger predictions
  generatePrediction('silver');
  generatePrediction('gold');
}

function updatePriceCard(asset) {
  return (payload) => {
    const elId = asset === 'silver' ? 'silverPrice' : 'goldPrice';
    const metaId = asset === 'silver' ? 'silverPriceMeta' : 'goldPriceMeta';
    const node = document.getElementById(elId);
    const meta = document.getElementById(metaId);
    if (payload.data && payload.data.close != null && node) {
      node.innerText = formatter.format(payload.data.close);
      if (meta && payload.data.date) {
        meta.innerText = `As of ${payload.data.date}`;
        meta.className = 'stat-change positive';
      }
    } else if (node) {
      node.innerText = '—';
      if (meta) {
        meta.innerText = 'No data';
        meta.className = 'stat-change negative';
      }
    }
  };
}

async function fetchAndRender(asset, range, canvasId, color) {
  const res = await fetch(`${API_BASE}/prices/${asset}?range=${range}`);
  const result = await res.json();
  if (result.detail) {
    console.error(result.detail);
    return;
  }
  if (result.data && result.data.length) {
    renderChart(canvasId, result.data, `${asset.charAt(0).toUpperCase() + asset.slice(1)} price`, color);
  } else {
    renderChart(canvasId, [], `${asset.charAt(0).toUpperCase() + asset.slice(1)} price`, color);
  }
}

async function changeRange(asset, range, element) {
  const container = element.parentElement;
  container.querySelectorAll('.btn').forEach((btn) => btn.classList.remove('active'));
  element.classList.add('active');

  const canvasId = asset === 'silver' ? 'silverChart' : 'goldChart';
  const color = asset === 'silver' ? 'rgba(99, 102, 241, 1)' : 'rgba(245, 158, 11, 1)';

  await fetchAndRender(asset, range, canvasId, color);
}

const charts = {};

function renderChart(canvasId, dataList, label, color) {
  const canvas = document.getElementById(canvasId);
  if (!canvas) return;
  const ctx = canvas.getContext('2d');

  const gradient = ctx.createLinearGradient(0, 0, 0, 400);
  gradient.addColorStop(0, color.replace('1)', '0.2)'));
  gradient.addColorStop(1, color.replace('1)', '0)'));

  const labels = (dataList || []).map((d) => {
    const raw = d.date || d.Date;
    const date = new Date(raw);
    if (raw && String(raw).includes(' ')) {
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }
    return Number.isFinite(date.getTime()) ? date.toLocaleDateString() : String(raw);
  });
  const values = (dataList || []).map((d) => d.close ?? d.predicted_price);

  if (charts[canvasId]) {
    charts[canvasId].destroy();
  }

  charts[canvasId] = new Chart(ctx, {
    type: 'line',
    data: {
      labels,
      datasets: [
        {
          label,
          data: values,
          borderColor: color,
          backgroundColor: gradient,
          borderWidth: 2,
          tension: 0.4,
          pointRadius: 0,
          pointHoverRadius: 6,
          fill: true,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: {
        intersect: false,
        mode: 'index',
      },
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: 'rgba(15, 17, 23, 0.9)',
          titleColor: '#fff',
          bodyColor: '#94a3b8',
          borderColor: 'rgba(255, 255, 255, 0.1)',
          borderWidth: 1,
          padding: 12,
          displayColors: false,
          callbacks: {
            label(ctx) {
              const v = ctx.parsed.y;
              if (v == null || Number.isNaN(v)) return '';
              return formatter.format(v);
            },
          },
        },
      },
      scales: {
        x: {
          ticks: { color: '#94a3b8', maxRotation: 45, autoSkip: true, maxTicksLimit: 12 },
          grid: { display: false },
        },
        y: {
          ticks: {
            color: '#94a3b8',
            callback: (value) => formatter.format(value),
          },
          grid: { color: 'rgba(255,255,255,0.05)' },
        },
      },
    },
  });
}

function apiErrorMessage(data) {
  if (!data) return 'Unknown error';
  if (typeof data.detail === 'string') return data.detail;
  if (Array.isArray(data.detail)) {
    return data.detail.map((e) => e.msg || JSON.stringify(e)).join('; ');
  }
  return data.error || JSON.stringify(data);
}

let lastGeneratedPredictions = { silver: null, gold: null };

async function generatePrediction(asset) {
  const tfEl = document.getElementById(asset === 'silver' ? 'predTimeframeSilver' : 'predTimeframeGold');
  const timeframe = tfEl ? tfEl.value : 'daily';
  const panel = document.getElementById(`predictions-panel-${asset}`);

  const summaryEl = document.getElementById(asset === 'silver' ? 'predictionSummarySilver' : 'predictionSummaryGold');
  const resultEl = document.getElementById(asset === 'silver' ? 'predictionResultSilver' : 'predictionResultGold');
  const titleEl = document.getElementById(asset === 'silver' ? 'predChartTitleSilver' : 'predChartTitleGold');
  const canvasId = asset === 'silver' ? 'predChartSilver' : 'predChartGold';
  const tableBody = document.getElementById(asset === 'silver' ? 'predTableBodySilver' : 'predTableBodyGold');

  if (summaryEl) {
    summaryEl.classList.remove('hidden');
    summaryEl.innerHTML = '<div class="loading-pulse">Calculating forecast paths...</div>';
  }
  if (resultEl) resultEl.classList.remove('hidden');
  if (tableBody) tableBody.innerHTML = '<tr><td colspan="3" style="text-align: center;">Loading...</td></tr>';

  try {
    const res = await fetch(`${API_BASE}/predict/${asset}?timeframe=${timeframe}`);
    const data = await res.json();

    if (!res.ok) {
      alert(apiErrorMessage(data));
      return;
    }

    if (data.predictions && data.predictions.length) {
      lastGeneratedPredictions[asset] = {
          timeframe: timeframe,
          data: data.predictions
      };
      
      if (resultEl) resultEl.classList.remove('hidden');
      if (titleEl) titleEl.innerText = `${asset} forecast (${timeframe})`;

      const lastClose = data.last_close;
      const firstPred = data.predictions[0].predicted_price;
      const lastPred = data.predictions[data.predictions.length - 1].predicted_price;
      const maeTrain = data.mean_absolute_error_train;
      const maeTest = data.mean_absolute_error_test;
      const maeGoal = data.mae_goal_usd;

      if (summaryEl && lastClose != null) {
        const horizonChange = ((lastPred - lastClose) / lastClose) * 100;
        const stepOne = ((firstPred - lastClose) / lastClose) * 100;
        const pos = horizonChange >= 0;
        const maeWarn =
          typeof maeTest === 'number' && typeof maeGoal === 'number' && maeTest > maeGoal
            ? `<div class="mae-warning-box animate-pulse">
                <i class="fas fa-exclamation-triangle"></i>
                <span><strong>High Typical Error:</strong> Current model error (${formatter.format(maeTest)}) exceeds target (${formatter.format(maeGoal)}). Accuracy may be compromised.</span>
               </div>`
            : '';
        summaryEl.classList.remove('hidden');
        summaryEl.className = `prediction-summary animate-fade-in ${pos ? 'gain' : 'loss'}`;
        summaryEl.innerHTML = `
          <div class="prediction-summary-inner">
            <div>
              <span class="prediction-summary-label">Last close</span>
              <strong>${formatter.format(lastClose)}</strong>
            </div>
            <div>
              <span class="prediction-summary-label">Mean abs. error (train)</span>
              <strong>${maeTrain != null ? formatter.format(maeTrain) : '—'}</strong>
            </div>
            <div>
              <span class="prediction-summary-label">Mean abs. error (test hold-out)</span>
              <strong>${maeTest != null ? formatter.format(maeTest) : '—'}</strong>
            </div>
            <div>
              <span class="prediction-summary-label">Goal (typical error)</span>
              <strong>≤ ${maeGoal != null ? formatter.format(maeGoal) : '—'}</strong>
            </div>
            <div>
              <span class="prediction-summary-label">First step vs close</span>
              <strong class="${stepOne >= 0 ? 'text-gain' : 'text-loss'}">${stepOne >= 0 ? '+' : ''}${stepOne.toFixed(2)}%</strong>
            </div>
            <div>
              <span class="prediction-summary-label">Full horizon vs close</span>
              <strong class="${horizonChange >= 0 ? 'text-gain' : 'text-loss'}">${horizonChange >= 0 ? '+' : ''}${horizonChange.toFixed(2)}%</strong>
            </div>
          </div>
          ${maeWarn}
          <p class="prediction-disclaimer">MAE is the average dollar gap between predicted and actual next prices on the hold-out period. Forecast path uses that plus volatility caps — not investment advice.</p>
        `;
      } else if (summaryEl) {
        summaryEl.classList.add('hidden');
        summaryEl.innerHTML = '';
      }

      const hist = await fetch(`${API_BASE}/prices/${asset}?range=all`).then((r) => r.json());
      const recent = (hist.data || []).slice(-45).map((d) => ({ date: d.date, close: d.close }));
      renderForecastChart(recent, data.predictions, lastClose, asset, canvasId);

      // Populate Table
      const tableBody = document.getElementById(asset === 'silver' ? 'predTableBodySilver' : 'predTableBodyGold');
      if (tableBody) {
        tableBody.innerHTML = data.predictions.map(p => `
          <tr>
            <td>${p.date}</td>
            <td style="font-weight: 600;">${formatter.format(p.predicted_price)}</td>
            <td style="color: var(--text-muted); font-size: 0.8rem;">
              ${formatter.format(p.ci_lower)} - ${formatter.format(p.ci_upper)}
            </td>
          </tr>
        `).join('');
      }
    } else {
      alert('Error: ' + apiErrorMessage(data));
    }
  } catch (err) {
    console.error('Failed to generate prediction:', err);
  }
}

async function renderForecastChart(histRows, predictions, lastClose, asset, canvasId) {
  const canvas = document.getElementById(canvasId);
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  const colorHist = asset === 'silver' ? 'rgba(99, 102, 241, 1)' : 'rgba(245, 158, 11, 1)';
  const colorPred = 'rgba(139, 92, 246, 1)';

  const h = histRows || [];
  const pred = predictions || [];
  const n = h.length;
  const labels = [
    ...h.map((d) => {
      const date = new Date(d.date);
      return Number.isFinite(date.getTime()) ? date.toLocaleDateString() : String(d.date);
    }),
    ...pred.map((p) => {
      const date = new Date(p.date);
      return Number.isFinite(date.getTime()) ? date.toLocaleDateString() : String(p.date);
    }),
  ];

  const histVals = [...h.map((d) => d.close), ...Array(pred.length).fill(null)];
  const bridge = n > 0 ? Number(h[n - 1].close) : lastClose;
  const predVals =
    n === 0
      ? [bridge, ...pred.map((p) => p.predicted_price)]
      : [...Array(n - 1).fill(null), bridge, ...pred.map((p) => p.predicted_price)];

  if (charts[canvasId]) charts[canvasId].destroy();

  const datasets = [
    {
      label: 'Historical close',
      data: histVals,
      borderColor: colorHist,
      backgroundColor: 'transparent',
      borderWidth: 2,
      tension: 0.3,
      pointRadius: 0,
      spanGaps: false,
    },
    {
      label: 'Forecast',
      data: predVals,
      borderColor: colorPred,
      backgroundColor: 'transparent',
      borderWidth: 2,
      borderDash: [6, 4],
      tension: 0.3,
      pointRadius: 0,
      spanGaps: false,
    },
  ];

  if (lastClose != null && labels.length) {
    datasets.push({
      label: 'Last close (baseline)',
      data: labels.map(() => lastClose),
      borderColor: 'rgba(148, 163, 184, 0.45)',
      borderWidth: 1,
      borderDash: [4, 6],
      pointRadius: 0,
      tension: 0,
    });
  }

  charts[canvasId] = new Chart(ctx, {
    type: 'line',
    data: { labels, datasets },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { mode: 'index', intersect: false },
      plugins: {
        legend: { display: true, labels: { color: '#94a3b8' } },
        tooltip: {
          callbacks: {
            label(ctx) {
              const v = ctx.parsed.y;
              if (v == null || Number.isNaN(v)) return ctx.dataset.label + ': —';
              return ctx.dataset.label + ': ' + formatter.format(v);
            },
          },
        },
      },
      scales: {
        x: { ticks: { color: '#94a3b8', maxRotation: 45, maxTicksLimit: 16 }, grid: { color: 'rgba(255,255,255,0.05)' } },
        y: {
          ticks: { color: '#94a3b8', callback: (v) => formatter.format(v) },
          grid: { color: 'rgba(255,255,255,0.05)' },
        },
      },
    },
  });
}
async function savePrediction(asset) {
    const saved = lastGeneratedPredictions[asset];
    if (!saved || !saved.data) {
        alert("Please generate a forecast first.");
        return;
    }

    const btnId = asset === 'silver' ? 'saveSilverBtn' : 'saveGoldBtn';
    const btn = document.getElementById(btnId);
    btn.disabled = true;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Saving...';

    try {
        const res = await fetch(`${API_BASE}/predictions/save`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                asset: asset,
                timeframe: saved.timeframe,
                predictions: saved.data.map(p => ({
                    date: p.date,
                    predicted_price: p.predicted_price
                }))
            })
        });

        const data = await res.json();
        if (res.ok) {
            alert(`Successfully saved ${data.saved_count} prediction points to Reality Check!`);
            loadRealityHistory();
        } else {
            alert("Error: " + (data.detail || "Failed to save"));
        }
    } catch (err) {
        console.error(err);
        alert("Failed to save prediction to database.");
    } finally {
        btn.disabled = false;
        btn.innerHTML = '<i class="fas fa-save"></i> Save Path to Reality Check';
    }
}

async function loadRealityHistory() {
    const body = document.getElementById('realityBody');
    if (!body) return;

    try {
        const res = await fetch(`${API_BASE}/predictions/history`);
        const result = await res.json();
        const data = result.data || [];

        if (data.length === 0) {
            body.innerHTML = `<tr><td colspan="8" style="text-align: center; padding: 2rem; color: var(--color-text-muted);">No saved predictions found.</td></tr>`;
            return;
        }

        body.innerHTML = data.map(item => {
            const hasActual = item.actual_price != null;
            const errorAbs = item.error_abs != null ? formatter.format(item.error_abs) : '—';
            const errorPct = item.error_pct != null ? item.error_pct.toFixed(2) + '%' : '—';
            const actualStr = hasActual ? formatter.format(item.actual_price) : 'Waiting...';
            const statusClass = item.status === 'completed' ? 'completed' : 'pending';
            
            return `
                <tr>
                    <td style="text-transform: capitalize; font-weight: 600;">${item.asset}</td>
                    <td><small>${item.made_at}</small></td>
                    <td>${item.predicted_for_date}</td>
                    <td><strong>${formatter.format(item.predicted_price)}</strong></td>
                    <td style="${hasActual ? 'color: var(--text-primary)' : 'color: var(--text-muted)'}">${actualStr}</td>
                    <td>${errorAbs}</td>
                    <td class="${item.error_pct != null ? (item.error_pct < 1.0 ? 'text-gain' : 'text-loss') : ''}">${errorPct}</td>
                    <td><span class="status-badge ${statusClass}">${item.status}</span></td>
                </tr>
            `;
        }).join('');
    } catch (err) {
        console.error("Failed to load reality history:", err);
    }
}

async function calculatePL() {
  const asset = document.getElementById('calcAsset').value;
  const buyDate = document.getElementById('calcBuyDate').value;
  const sellDate = document.getElementById('calcSellDate').value;
  const qty = parseFloat(document.getElementById('calcQty').value);

  if (!buyDate || !sellDate || !qty) {
    alert('Please fill all fields');
    return;
  }

  try {
    const res = await fetch(`${API_BASE}/profit-loss`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ asset, buy_date: buyDate, sell_date: sellDate, quantity: qty }),
    });

    const data = await res.json();
    if (!res.ok) {
      alert(apiErrorMessage(data));
      return;
    }

    const isProfit = data.profit_loss >= 0;
    const cardClass = isProfit ? 'green' : 'red';
    const sign = data.profit_loss >= 0 ? '+' : '';
    const roi = typeof data.roi_percent === 'number' ? data.roi_percent : 0;
    const icon = isProfit ? 'fa-arrow-trend-up' : 'fa-arrow-trend-down';

    const html = `
      <div class="stat-card ${cardClass} animate-fade-in">
        <div class="stat-icon ${cardClass}"><i class="fas fa-scale-balanced"></i></div>
        <div class="stat-info">
          <div class="stat-label">Total P/L (${data.quantity} oz)</div>
          <div class="stat-value">${sign}${formatter.format(data.profit_loss)}</div>
          <div class="stat-change ${isProfit ? 'positive' : 'negative'}">
            <i class="fas ${icon}"></i> ${sign}${roi.toFixed(2)}% ROI &middot;
            Buy ${formatter.format(data.buy_price)} → Sell ${formatter.format(data.sell_price)}
          </div>
          ${data.data_range ? `<div class="stat-meta">History: ${data.data_range.start} — ${data.data_range.end}</div>` : ''}
        </div>
      </div>
    `;

    const resDiv = document.getElementById('calcResult');
    resDiv.innerHTML = html;
    resDiv.classList.remove('hidden');
  } catch (err) {
    alert('Failed to calculate.');
  }
}

window.onload = () => {
  loadDashboard();
  loadRealityHistory();
};

window.setActiveDashboard = setActiveDashboard;
window.toggleSidebar = toggleSidebar;
window.changeRange = changeRange;
window.generatePrediction = generatePrediction;
window.savePrediction = savePrediction;
window.loadRealityHistory = loadRealityHistory;
window.calculatePL = calculatePL;
window.updateNav = updateNav;
