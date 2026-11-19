/**
 * Explainable NLP-Based Industrial Equipment Failure Prediction
 * Frontend Application Controller (Vanilla JS + Chart.js)
 */

document.addEventListener('DOMContentLoaded', () => {
  // Application State
  const state = {
    currentView: 'dashboard',
    dashboardData: null,
    performanceData: null,
    lastAnalysisResult: null,
    datasetFilters: {
      page: 1,
      page_size: 20,
      split: 'ALL',
      category: 'ALL',
      search: '',
    },
    charts: {},
  };

  // Realistic sample maintenance observations for testing
  const PRESETS = {
    noise_vib: {
      machine_id: 'MCH-101',
      machine_name: 'Centrifugal Slurry Pump #1',
      equipment_type: 'Centrifugal Pump',
      observation: 'Machine 1 produces extreme noise during operation. Temperature is higher than normal, vibration is increasing and the belt appears loose.',
      technician: 'Tech Alex Morgan (ID: TM-410)',
      label: 'Acoustic & Vibration Anomaly',
    },
    leak: {
      machine_id: 'PMP-204',
      machine_name: 'Acid Transfer Pump B',
      equipment_type: 'Positive Displacement Pump',
      observation: 'Fluid is leaking from the mechanical shaft seal, spraying slurry across the floor and dripping continuously.',
      technician: 'Tech Sarah Jenkins (ID: TM-228)',
      label: 'Seal Leakage Spillage',
    },
    elec: {
      machine_id: 'MTR-305',
      machine_name: 'Main Feed Drive Motor #4',
      equipment_type: 'Electric Induction Motor',
      observation: 'Motor keeps tripping on start up and has power issue. Static earth resistance is abnormal and will not trip properly.',
      technician: 'Tech David Chen (ID: TM-512)',
      label: 'Electrical Tripping Fault',
    },
    overheat: {
      machine_id: 'CMP-409',
      machine_name: 'Rotary Screw Compressor A',
      equipment_type: 'Air Compressor',
      observation: 'Motor casing is smoking hot, over heating rapidly after 30 minutes of load, and smells burnt.',
      technician: 'Tech Marcus Vance (ID: TM-104)',
      label: 'Thermal Overheating Anomaly',
    },
    plugged: {
      machine_id: 'PIP-512',
      machine_name: 'Tailings Slurry Discharge Line',
      equipment_type: 'Piping & Valve System',
      observation: 'Pipe line is bogged and plugged with heavy solids, choked suction, resulting in no pressure output.',
      technician: 'Tech Liam O\'Connor (ID: TM-619)',
      label: 'Choked / Blocked Line',
    },
    structural: {
      machine_id: 'CNV-618',
      machine_name: 'Overland Conveyor Gantry #3',
      equipment_type: 'Belt Conveyor Structure',
      observation: 'Support frame shows severe corrosion, shredded mounting bracket and structural damage requiring immediate repair.',
      technician: 'Tech Elena Rostova (ID: TM-307)',
      label: 'Structural Corrosion Defect',
    },
  };

  // Initialize Modules
  initNavigation();
  initPredictForm();
  initDatasetView();
  initPerformanceView();

  // Load initial view
  const initialHash = window.location.hash.replace('#', '') || 'dashboard';
  navigateTo(initialHash);

  // =========================================================================
  // Navigation & SPA Router
  // =========================================================================
  function initNavigation() {
    document.querySelectorAll('.nav-link').forEach((link) => {
      link.addEventListener('click', (e) => {
        e.preventDefault();
        const targetView = link.getAttribute('data-view');
        navigateTo(targetView);
      });
    });

    window.addEventListener('hashchange', () => {
      const hashView = window.location.hash.replace('#', '') || 'dashboard';
      navigateTo(hashView);
    });

    document.querySelectorAll('[data-goto]').forEach((btn) => {
      btn.addEventListener('click', () => {
        const targetView = btn.getAttribute('data-goto');
        if (targetView) {
          navigateTo(targetView);
        }
      });
    });
  }

  function navigateTo(viewId) {
    const validViews = ['dashboard', 'predict', 'dataset', 'performance', 'about'];
    if (!validViews.includes(viewId)) {
      viewId = 'dashboard';
    }

    state.currentView = viewId;
    window.location.hash = viewId;

    document.querySelectorAll('.nav-link').forEach((link) => {
      if (link.getAttribute('data-view') === viewId) {
        link.classList.add('active');
      } else {
        link.classList.remove('active');
      }
    });

    document.querySelectorAll('.view-section').forEach((section) => {
      if (section.id === `view-${viewId}`) {
        section.classList.add('active');
      } else {
        section.classList.remove('active');
      }
    });

    if (viewId === 'dashboard') {
      loadDashboard();
    } else if (viewId === 'dataset') {
      fetchDatasetRecords();
    } else if (viewId === 'performance') {
      loadPerformance();
    }
  }

  // =========================================================================
  // Dashboard Analytics & Visualizations
  // =========================================================================
  async function loadDashboard() {
    // The Dashboard now functions as an informative, professional industrial
    // software homepage. Dataset statistics and Machine Learning evaluation metrics
    // are strictly preserved on the dedicated Dataset and Model Performance pages.
  }

  function renderDashboardMetrics(summary, performance) {
    const elTotal = document.getElementById('metric-total-records');
    if (!elTotal) return;
    elTotal.textContent = summary.total_records.toLocaleString();
    const elCat = document.getElementById('metric-categories-count');
    if (elCat) elCat.textContent = summary.num_categories;
    const elTrain = document.getElementById('metric-train-records');
    if (elTrain) elTrain.textContent = summary.train_records.toLocaleString();

    const testAcc = (performance.test_metrics.accuracy * 100).toFixed(1);
    const macroF1 = (performance.test_metrics.macro_f1 * 100).toFixed(1);
    const elAcc = document.getElementById('metric-model-accuracy');
    if (elAcc) elAcc.textContent = `${testAcc}%`;
    const elAccSub = document.getElementById('metric-accuracy-sub');
    if (elAccSub) elAccSub.textContent = `Test Accuracy (${testAcc}%) | Macro F1 (${macroF1}%)`;
  }

  function renderDashboardCharts(summary, performance) {
    if (typeof Chart === 'undefined') {
      console.warn('Chart.js not available');
      return;
    }

    // Chart A: Failure Category Distribution
    const ctxA = document.getElementById('chart-failure-types');
    if (ctxA) {
      if (state.charts.failureTypes) state.charts.failureTypes.destroy();
      const dist = summary.all_distribution;
      const sortedEntries = Object.entries(dist).sort((a, b) => b[1] - a[1]);
      const labels = sortedEntries.map(e => e[0]);
      const values = sortedEntries.map(e => e[1]);

      state.charts.failureTypes = new Chart(ctxA, {
        type: 'bar',
        data: {
          labels: labels,
          datasets: [{
            label: 'Total Observations',
            data: values,
            backgroundColor: '#2563eb',
            borderRadius: 5,
          }],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { display: false },
            tooltip: {
              callbacks: {
                label: (ctx) => ` ${ctx.raw} observations (${summary.dataset_name})`,
              },
            },
          },
          scales: {
            y: { beginAtZero: true, grid: { color: '#f1f5f9' } },
            x: {
              grid: { display: false },
              ticks: { maxRotation: 45, minRotation: 20, font: { size: 10 } },
            },
          },
        },
      });
    }

    // Chart B: Dataset Partition Breakdown
    const ctxB = document.getElementById('chart-partition-breakdown');
    if (ctxB) {
      if (state.charts.partitions) state.charts.partitions.destroy();
      state.charts.partitions = new Chart(ctxB, {
        type: 'doughnut',
        data: {
          labels: [
            `Train Split (${summary.train_records} obs)`,
            `Dev / Validation (${summary.dev_records} obs)`,
            `Holdout Test (${summary.test_records} obs)`,
          ],
          datasets: [{
            data: [summary.train_records, summary.dev_records, summary.test_records],
            backgroundColor: ['#2563eb', '#38bdf8', '#10b981'],
            borderWidth: 2,
            borderColor: '#ffffff',
          }],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { position: 'bottom', labels: { boxWidth: 12, font: { size: 11 } } },
          },
        },
      });
    }

    // Chart C: Top 8 Failure Modes in Training Set
    const ctxC = document.getElementById('chart-top-categories');
    if (ctxC) {
      if (state.charts.topCategories) state.charts.topCategories.destroy();
      const trainDist = summary.train_distribution;
      const top8 = Object.entries(trainDist).sort((a, b) => b[1] - a[1]).slice(0, 8);

      state.charts.topCategories = new Chart(ctxC, {
        type: 'bar',
        data: {
          labels: top8.map(e => e[0]),
          datasets: [{
            label: 'Train Samples',
            data: top8.map(e => e[1]),
            backgroundColor: [
              '#3b82f6', '#60a5fa', '#93c5fd', '#bfdbfe',
              '#10b981', '#f59e0b', '#ef4444', '#8b5cf6',
            ],
            borderRadius: 5,
          }],
        },
        options: {
          indexAxis: 'y',
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { display: false },
          },
          scales: {
            x: { beginAtZero: true, grid: { color: '#f1f5f9' } },
            y: { grid: { display: false }, ticks: { font: { size: 11 } } },
          },
        },
      });
    }

    // Chart D: Model Evaluation Holdout Metrics
    const ctxD = document.getElementById('chart-model-metrics');
    if (ctxD) {
      if (state.charts.modelMetrics) state.charts.modelMetrics.destroy();
      const tm = performance.test_metrics;

      state.charts.modelMetrics = new Chart(ctxD, {
        type: 'bar',
        data: {
          labels: ['Test Accuracy', 'Weighted F1', 'Macro F1', 'Macro Precision', 'Macro Recall', 'Dev Validation'],
          datasets: [{
            label: 'Metric Score (%)',
            data: [
              tm.accuracy * 100,
              tm.weighted_f1 * 100,
              tm.macro_f1 * 100,
              tm.macro_precision * 100,
              tm.macro_recall * 100,
              tm.dev_accuracy * 100,
            ],
            backgroundColor: ['#2563eb', '#1d4ed8', '#3b82f6', '#60a5fa', '#93c5fd', '#10b981'],
            borderRadius: 6,
          }],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { display: false } },
          scales: {
            y: {
              beginAtZero: true,
              max: 100,
              ticks: { callback: v => `${v}%` },
              grid: { color: '#f1f5f9' },
            },
            x: { grid: { display: false }, ticks: { font: { size: 10 } } },
          },
        },
      });
    }
  }

  // =========================================================================
  // Maintenance Report Prediction & PDF Generation
  // =========================================================================
  function initPredictForm() {
    const form = document.getElementById('predict-form');
    const clearBtn = document.getElementById('btn-clear-predict');

    // Preset sample observation buttons
    document.querySelectorAll('.preset-btn').forEach((btn) => {
      btn.addEventListener('click', () => {
        const key = btn.getAttribute('data-preset');
        if (PRESETS[key]) {
          applyPreset(PRESETS[key]);
        }
      });
    });

    clearBtn.addEventListener('click', () => {
      form.reset();
      document.getElementById('input-inspection-date').value = new Date().toISOString().split('T')[0];
      state.lastAnalysisResult = null;
      document.getElementById('result-container').innerHTML = `
        <div class="result-empty-state">
          <div class="result-empty-icon">
            <svg width="32" height="32" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <h3>Awaiting Maintenance Report</h3>
          <p>Enter the machine inspection observation on the left or select an evaluation preset, then click <strong>Analyse Report</strong>.</p>
        </div>
      `;
    });

    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      await handleReportAnalysis();
    });

    // Default inspection date
    const dateInput = document.getElementById('input-inspection-date');
    if (dateInput && !dateInput.value) {
      dateInput.value = new Date().toISOString().split('T')[0];
    }
  }

  function applyPreset(preset) {
    document.getElementById('input-machine-id').value = preset.machine_id;
    document.getElementById('input-machine-name').value = preset.machine_name;
    document.getElementById('input-equipment-type').value = preset.equipment_type;
    document.getElementById('input-technician').value = preset.technician;
    document.getElementById('input-observation').value = preset.observation;
    document.getElementById('input-inspection-date').value = new Date().toISOString().split('T')[0];

    showToast(`Loaded preset: ${preset.label}`, 'info');
  }

  async function handleReportAnalysis() {
    const submitBtn = document.getElementById('btn-run-predict');
    const originalText = submitBtn.innerHTML;

    try {
      const observation = document.getElementById('input-observation').value.trim();
      if (!observation) {
        showToast('Please enter an inspection observation in English.', 'warning');
        return;
      }

      submitBtn.disabled = true;
      submitBtn.innerHTML = `
        <svg class="spinner" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" style="animation: spin 1s linear infinite;">
          <circle cx="12" cy="12" r="10" stroke-width="4" stroke="currentColor" stroke-dasharray="32" stroke-linecap="round"></circle>
        </svg>
        Analyzing Observation...
      `;

      const payload = {
        machine_id: document.getElementById('input-machine-id').value.trim() || 'MCH-101',
        machine_name: document.getElementById('input-machine-name').value.trim() || 'Primary Operating Unit',
        equipment_type: document.getElementById('input-equipment-type').value.trim() || 'General Equipment',
        inspection_date: document.getElementById('input-inspection-date').value || new Date().toISOString().split('T')[0],
        technician_name: document.getElementById('input-technician').value.trim() || 'Plant Technician',
        observation: observation,
      };

      const res = await fetch('/api/analyse', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      const json = await res.json();
      if (!res.ok) throw new Error(json.detail || 'Analysis failed');

      state.lastAnalysisResult = json.data;
      renderAnalysisResult(json.data);
    } catch (err) {
      console.error('Analysis error:', err);
      showToast(err.message, 'danger');
    } finally {
      submitBtn.disabled = false;
      submitBtn.innerHTML = originalText;
    }
  }

  function renderAnalysisResult(data) {
    const container = document.getElementById('result-container');
    const cat = data.predicted_category;
    const conf = data.confidence_percentage;
    const recs = data.maintenance_recommendations;

    // Low confidence warning banner
    let warnHtml = '';
    if (data.is_low_confidence && data.low_confidence_warning) {
      warnHtml = `
        <div class="alert-warning-banner">
          <svg width="20" height="20" fill="none" viewBox="0 0 24 24" stroke="currentColor" style="flex-shrink: 0; margin-top: 1px;">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          <div>
            <strong>Notice:</strong> ${data.low_confidence_warning}
          </div>
        </div>
      `;
    }

    // Secondary categories
    let altHtml = '';
    if (data.alternative_categories && data.alternative_categories.length > 0) {
      altHtml = `
        <div class="alternatives-box">
          <div class="alternatives-title">Secondary Probable Categories</div>
          ${data.alternative_categories.map(a => `
            <div class="alternative-item">
              <span>${a.category}</span>
              <strong>${a.percentage}%</strong>
            </div>
          `).join('')}
        </div>
      `;
    }

    // Extracted symptoms tags
    let symptomsHtml = '';
    if (data.detected_symptoms && data.detected_symptoms.length > 0) {
      const tagList = data.detected_symptoms.map(s => `
        <div class="symptom-tag">
          <strong>${s.symptom_category}:</strong>
          <span>${s.matched_terms.join(', ')}</span>
        </div>
      `).join('');
      symptomsHtml = `
        <div class="card symptoms-card">
          <div class="card-title">
            <svg width="18" height="18" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
            </svg>
            Extracted Maintenance Symptoms
          </div>
          <div class="symptoms-tag-list">
            ${tagList}
          </div>
        </div>
      `;
    }

    // Explainability top words
    let explainRowsHtml = '';
    const topWords = data.explainability.top_words || [];
    topWords.forEach(w => {
      const isPos = w.is_positive;
      const borderClass = isPos ? 'positive' : 'negative';
      const dirColor = isPos ? 'var(--danger)' : 'var(--primary)';
      const dirLabel = isPos ? 'Supports Prediction' : 'Reduces Score';

      explainRowsHtml += `
        <div class="explain-param-item ${borderClass}">
          <div class="param-name-block">
            <strong>"${w.term}"</strong>
            <span>${w.contribution_level} &bull; TF-IDF: ${w.tfidf_weight} &bull; Model Coef: ${w.coefficient > 0 ? '+' : ''}${w.coefficient}</span>
          </div>
          <div class="param-score-block">
            <span class="score" style="color: ${dirColor};">${w.contribution > 0 ? '+' : ''}${w.contribution}</span>
            <span class="direction" style="color: ${dirColor};">${dirLabel}</span>
          </div>
        </div>
      `;
    });

    // Maintenance recommendations checklist
    const checklistHtml = recs.suggestions.map(s => `
      <li>
        <svg width="18" height="18" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <span>${s}</span>
      </li>
    `).join('');

    container.innerHTML = `
      ${warnHtml}

      <!-- Primary Diagnostic Hero -->
      <div class="prediction-hero-card">
        <div class="prediction-hero-header">
          <span class="badge badge-primary">Predicted Failure Mode</span>
          <span class="badge badge-neutral">${recs.code}</span>
        </div>
        <div class="prediction-title">${cat}</div>

        <div class="prediction-confidence-bar-wrap">
          <div class="confidence-label-row">
            <span>Model Prediction Confidence</span>
            <span>${conf}%</span>
          </div>
          <div class="confidence-bar-bg">
            <div class="confidence-bar-fill" style="width: ${conf}%;"></div>
          </div>
        </div>

        ${altHtml}
      </div>

      <!-- Symptoms Card -->
      ${symptomsHtml}

      <!-- Explainable Words Card -->
      <div class="card explain-card">
        <div class="card-title">
          <svg width="20" height="20" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
          Influential Words & Features (Explainable NLP)
        </div>
        <p class="card-subtitle">Contribution scores computed via Logistic Regression class coefficients & TF-IDF term weights.</p>

        <div class="explain-param-list">
          ${explainRowsHtml || '<p style="color: var(--text-muted); font-size: 0.88rem;">No single dominant terms detected.</p>'}
        </div>

        <div class="explain-narrative">
          ${data.explainability.narrative_explanation}
        </div>
      </div>

      <!-- Maintenance Decision Support Card -->
      <div class="card maintenance-card">
        <div class="card-header">
          <div class="card-title">
            <svg width="20" height="20" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
            Maintenance Decision Support
          </div>
          <span class="badge badge-warning">${recs.suggested_priority}</span>
        </div>

        <div class="maintenance-subsystem">Targeted Assembly: <strong>${recs.targeted_subsystem}</strong></div>
        <ul class="maintenance-checklist">
          ${checklistHtml}
        </ul>

        <div class="maintenance-disclaimer">
          ${recs.disclaimer}
        </div>
      </div>

      <!-- PDF Report Download Card -->
      <div class="pdf-download-card">
        <div class="pdf-download-info">
          <h4>Download Official Maintenance PDF Report</h4>
          <p>Generate a formalized, formatted engineering report suitable for management review.</p>
        </div>
        <button type="button" id="btn-download-pdf" class="btn btn-success">
          <svg width="18" height="18" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
          </svg>
          Download PDF Report
        </button>
      </div>
    `;

    // Hook PDF download event
    document.getElementById('btn-download-pdf').addEventListener('click', handlePdfDownload);
  }

  async function handlePdfDownload() {
    if (!state.lastAnalysisResult) {
      showToast('No active analysis result to export.', 'warning');
      return;
    }

    const btn = document.getElementById('btn-download-pdf');
    const origText = btn.innerHTML;

    try {
      btn.disabled = true;
      btn.innerHTML = 'Compiling PDF...';

      const payload = {
        machine_id: state.lastAnalysisResult.machine_id,
        machine_name: state.lastAnalysisResult.machine_name,
        equipment_type: state.lastAnalysisResult.equipment_type,
        inspection_date: state.lastAnalysisResult.inspection_date,
        technician_name: state.lastAnalysisResult.technician_name,
        observation: state.lastAnalysisResult.original_text,
      };

      const res = await fetch('/api/report', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      const json = await res.json();
      if (!res.ok) throw new Error(json.detail || 'PDF compilation failed');

      // Trigger automatic file download
      const downloadLink = document.createElement('a');
      downloadLink.href = json.download_url;
      downloadLink.download = json.filename;
      document.body.appendChild(downloadLink);
      downloadLink.click();
      downloadLink.remove();

      showToast(`Report downloaded: ${json.filename}`, 'success');
    } catch (err) {
      console.error('PDF error:', err);
      showToast(err.message, 'danger');
    } finally {
      btn.disabled = false;
      btn.innerHTML = origText;
    }
  }

  // =========================================================================
  // Dataset Explorer View (FMC-MWO2KG)
  // =========================================================================
  function initDatasetView() {
    const searchInput = document.getElementById('dataset-search');
    const filterSplit = document.getElementById('filter-split');
    const filterCategory = document.getElementById('filter-category');
    const filterPageSize = document.getElementById('filter-page-size');
    const btnReset = document.getElementById('btn-reset-filters');
    const btnPrev = document.getElementById('btn-prev-page');
    const btnNext = document.getElementById('btn-next-page');

    let debounceTimer = null;
    searchInput.addEventListener('input', () => {
      clearTimeout(debounceTimer);
      debounceTimer = setTimeout(() => {
        state.datasetFilters.search = searchInput.value;
        state.datasetFilters.page = 1;
        fetchDatasetRecords();
      }, 300);
    });

    filterSplit.addEventListener('change', () => {
      state.datasetFilters.split = filterSplit.value;
      state.datasetFilters.page = 1;
      fetchDatasetRecords();
    });

    filterCategory.addEventListener('change', () => {
      state.datasetFilters.category = filterCategory.value;
      state.datasetFilters.page = 1;
      fetchDatasetRecords();
    });

    filterPageSize.addEventListener('change', () => {
      state.datasetFilters.page_size = parseInt(filterPageSize.value, 10);
      state.datasetFilters.page = 1;
      fetchDatasetRecords();
    });

    btnReset.addEventListener('click', () => {
      searchInput.value = '';
      filterSplit.value = 'ALL';
      filterCategory.value = 'ALL';
      filterPageSize.value = '20';

      state.datasetFilters = {
        page: 1,
        page_size: 20,
        split: 'ALL',
        category: 'ALL',
        search: '',
      };
      fetchDatasetRecords();
    });

    btnPrev.addEventListener('click', () => {
      if (state.datasetFilters.page > 1) {
        state.datasetFilters.page -= 1;
        fetchDatasetRecords();
      }
    });

    btnNext.addEventListener('click', () => {
      if (state.datasetFilters.page < state.totalDatasetPages) {
        state.datasetFilters.page += 1;
        fetchDatasetRecords();
      }
    });
  }

  async function fetchDatasetRecords() {
    const tbody = document.getElementById('dataset-table-body');
    tbody.innerHTML = `<tr><td colspan="4" style="text-align: center; padding: 2rem;">Loading FMC-MWO2KG benchmark observations...</td></tr>`;

    try {
      const q = state.datasetFilters;
      const url = `/api/dataset?page=${q.page}&page_size=${q.page_size}&split=${encodeURIComponent(q.split)}&category=${encodeURIComponent(q.category)}&search=${encodeURIComponent(q.search)}`;

      const res = await fetch(url);
      if (!res.ok) throw new Error('Failed to load dataset records');
      const json = await res.json();
      const data = json.data;

      state.totalDatasetPages = data.total_pages;
      renderDatasetTable(data);
    } catch (err) {
      console.error('Dataset query error:', err);
      tbody.innerHTML = `<tr><td colspan="4" style="text-align: center; color: var(--danger); padding: 2rem;">${err.message}</td></tr>`;
    }
  }

  function renderDatasetTable(data) {
    const tbody = document.getElementById('dataset-table-body');
    if (!data.records || data.records.length === 0) {
      tbody.innerHTML = `<tr><td colspan="4" style="text-align: center; padding: 2rem; color: var(--text-muted);">No observations match your selected filter criteria.</td></tr>`;
      document.getElementById('pagination-summary').textContent = 'Showing 0 records';
      return;
    }

    const startRow = (data.page - 1) * data.page_size + 1;
    const endRow = Math.min(startRow + data.records.length - 1, data.total_records);
    document.getElementById('pagination-summary').textContent = `Showing ${startRow.toLocaleString()} - ${endRow.toLocaleString()} of ${data.total_records.toLocaleString()} observations`;

    document.getElementById('current-page-label').textContent = `Page ${data.page} of ${data.total_pages}`;
    document.getElementById('btn-prev-page').disabled = data.page <= 1;
    document.getElementById('btn-next-page').disabled = data.page >= data.total_pages;

    let rowsHtml = '';
    data.records.forEach(row => {
      let splitBadge = '<span class="badge badge-primary">Train</span>';
      if (row.split === 'Dev') {
        splitBadge = '<span class="badge badge-info">Dev</span>';
      } else if (row.split === 'Test') {
        splitBadge = '<span class="badge badge-success">Test</span>';
      }

      rowsHtml += `
        <tr>
          <td><code>${row.id}</code></td>
          <td>${splitBadge}</td>
          <td><strong>${row.text}</strong></td>
          <td><span class="badge badge-neutral">${row.label}</span></td>
        </tr>
      `;
    });

    tbody.innerHTML = rowsHtml;
  }

  // =========================================================================
  // Model Performance View
  // =========================================================================
  function initPerformanceView() {
    const btnRetrain = document.getElementById('btn-retrain-models');
    if (btnRetrain) {
      btnRetrain.addEventListener('click', async () => {
        if (!confirm('Retrain the TF-IDF + Logistic Regression model using train.txt and re-evaluate on test.txt?')) {
          return;
        }

        const origText = btnRetrain.innerHTML;
        try {
          btnRetrain.disabled = true;
          btnRetrain.innerHTML = 'Retraining Pipeline...';

          const res = await fetch('/api/retrain', { method: 'POST' });
          const json = await res.json();
          if (!res.ok) throw new Error(json.detail || 'Retraining failed');

          showToast('NLP Model retrained and re-evaluated successfully!', 'success');
          loadPerformance();
        } catch (err) {
          console.error('Retrain error:', err);
          showToast(err.message, 'danger');
        } finally {
          btnRetrain.disabled = false;
          btnRetrain.innerHTML = origText;
        }
      });
    }
  }

  async function loadPerformance() {
    try {
      const res = await fetch('/api/performance');
      if (!res.ok) throw new Error('Failed to load performance metrics');
      const json = await res.json();
      const perf = json.data;
      state.performanceData = perf;

      renderPerformanceDetails(perf);
    } catch (err) {
      console.error('Performance error:', err);
      showToast(err.message, 'danger');
    }
  }

  function renderPerformanceDetails(perf) {
    const tm = perf.test_metrics;

    document.getElementById('perf-accuracy').textContent = `${(tm.accuracy * 100).toFixed(2)}%`;
    document.getElementById('perf-macro-f1').textContent = tm.macro_f1.toFixed(4);
    document.getElementById('perf-weighted-f1').textContent = tm.weighted_f1.toFixed(4);
    document.getElementById('perf-macro-prec').textContent = tm.macro_precision.toFixed(4);
    document.getElementById('perf-macro-rec').textContent = tm.macro_recall.toFixed(4);
    document.getElementById('perf-dev-acc').textContent = `${(tm.dev_accuracy * 100).toFixed(2)}%`;

    // Classification report table
    const tbody = document.getElementById('perf-report-tbody');
    let rowsHtml = '';
    perf.classes.forEach(cls => {
      const c = perf.classification_report[cls] || {};
      const p = c.precision !== undefined ? c.precision.toFixed(3) : '-';
      const r = c.recall !== undefined ? c.recall.toFixed(3) : '-';
      const f = c['f1-score'] !== undefined ? c['f1-score'].toFixed(3) : '-';
      const s = c.support !== undefined ? c.support : 0;

      rowsHtml += `
        <tr>
          <td><strong>${cls}</strong></td>
          <td>${p}</td>
          <td>${r}</td>
          <td><strong>${f}</strong></td>
          <td><span class="badge badge-neutral">${s}</span></td>
        </tr>
      `;
    });
    tbody.innerHTML = rowsHtml;

    // Multi-Class Confusion Matrix Table
    renderConfusionMatrixTable(perf);
  }

  function renderConfusionMatrixTable(perf) {
    const table = document.getElementById('perf-cm-table');
    const classes = perf.classes;
    const matrix = perf.confusion_matrix.matrix;

    let headerHtml = '<tr><th style="min-width: 140px;">Actual \\ Pred</th>';
    classes.forEach(c => {
      const short = c.length > 10 ? c.substring(0, 8) + '..' : c;
      headerHtml += `<th title="${c}">${short}</th>`;
    });
    headerHtml += '</tr>';

    let bodyHtml = '';
    classes.forEach((actualClass, rowIdx) => {
      const short = actualClass.length > 16 ? actualClass.substring(0, 14) + '..' : actualClass;
      bodyHtml += `<tr><th style="text-align: left;" title="${actualClass}">${short}</th>`;
      classes.forEach((predClass, colIdx) => {
        const val = matrix[rowIdx][colIdx];
        const isDiag = rowIdx === colIdx;
        const cellClass = isDiag && val > 0 ? 'matrix-cell-highlight' : '';
        bodyHtml += `<td class="${cellClass}">${val}</td>`;
      });
      bodyHtml += '</tr>';
    });

    table.innerHTML = `<thead>${headerHtml}</thead><tbody>${bodyHtml}</tbody>`;
  }

  // =========================================================================
  // Toast Notifications
  // =========================================================================
  function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.style.cssText = `
      background-color: #ffffff;
      color: var(--text-primary);
      border: 1px solid var(--border-color);
      border-left: 5px solid ${type === 'danger' ? 'var(--danger)' : type === 'success' ? 'var(--success)' : type === 'warning' ? 'var(--warning)' : 'var(--primary)'};
      padding: 0.85rem 1.25rem;
      border-radius: var(--radius-md);
      box-shadow: var(--shadow-lg);
      margin-bottom: 0.75rem;
      font-size: 0.9rem;
      font-weight: 500;
      display: flex;
      align-items: center;
      gap: 0.75rem;
    `;

    toast.innerHTML = `<span>${message}</span>`;
    container.appendChild(toast);
    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transition = 'opacity 0.3s ease';
      setTimeout(() => toast.remove(), 300);
    }, 4500);
  }
});
