const API_BASE = window.location.origin;

let currentEvidence = [];
let currentReport = null;

// DOM Elements
const evidenceListEl = document.getElementById('evidence-list');
const evidenceCountEl = document.getElementById('evidence-count');
const contradictionsContainerEl = document.getElementById('contradictions-container');
const timelineContainerEl = document.getElementById('timeline-container');
const entityContainerEl = document.getElementById('entity-container');
const dossierViewEl = document.getElementById('dossier-view');
const analysisSummaryEl = document.getElementById('analysis-summary');
const contraPillEl = document.getElementById('contra-pill');
const timelinePillEl = document.getElementById('timeline-pill');
const entityPillEl = document.getElementById('entity-pill');
const airgapTextEl = document.getElementById('airgap-text');
const modelTextEl = document.getElementById('model-text');
const btnAnalyze = document.getElementById('btn-analyze');
const btnReset = document.getElementById('btn-reset');
const btnPrint = document.getElementById('btn-print');

// File Upload Elements
const dropzone = document.getElementById('dropzone');
const fileInput = document.getElementById('file-input');

// Modal Elements
const modalBackdrop = document.getElementById('modal-backdrop');
const modalFilename = document.getElementById('modal-filename');
const modalMeta = document.getElementById('modal-meta');
const modalContent = document.getElementById('modal-content');
const modalClose = document.getElementById('modal-close');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
  setupTabs();
  setupUpload();
  setupModal();
  fetchStatus();
  fetchEvidence();

  btnAnalyze.addEventListener('click', runAnalysis);
  btnReset.addEventListener('click', resetDemoCase);
  btnPrint.addEventListener('click', () => window.print());
});

// Setup Tabs Navigation
function setupTabs() {
  const tabs = document.querySelectorAll('.tab-btn');
  tabs.forEach(btn => {
    btn.addEventListener('click', () => {
      tabs.forEach(t => t.classList.remove('active'));
      document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));
      btn.classList.add('active');
      const targetPane = document.getElementById(btn.dataset.tab);
      if (targetPane) targetPane.classList.add('active');
    });
  });
}

// Fetch System & Air-Gap Telemetry
async function fetchStatus() {
  try {
    const res = await fetch(`${API_BASE}/api/status`);
    if (!res.ok) return;
    const data = await res.json();
    
    if (data.airgap_audit) {
      if (data.airgap_audit.is_airgapped) {
        airgapTextEl.textContent = "AIR-GAP CERTIFIED (0 EGRESS)";
      } else {
        airgapTextEl.textContent = `ALERT: ${data.airgap_audit.active_outbound_connections} ACTIVE SOCKETS`;
      }
    }

    if (data.available_models && data.available_models.length > 0) {
      modelTextEl.textContent = `OLLAMA: ${data.available_models[0].toUpperCase()}`;
    } else {
      modelTextEl.textContent = "LOCAL HYBRID SLM + HEURISTICS";
    }
  } catch (err) {
    console.warn("Status fetch error:", err);
  }
}

// Fetch Evidence Locker
async function fetchEvidence() {
  try {
    const res = await fetch(`${API_BASE}/api/evidence`);
    if (!res.ok) return;
    currentEvidence = await res.json();
    renderEvidenceList();
  } catch (err) {
    console.error("Evidence fetch error:", err);
  }
}

// Render Evidence Cards
function renderEvidenceList() {
  evidenceListEl.innerHTML = '';
  evidenceCountEl.textContent = `${currentEvidence.length} Items`;

  currentEvidence.forEach(ev => {
    const card = document.createElement('div');
    card.className = 'evidence-card';
    const isAudio = ev.evidence_type === 'audio';

    card.innerHTML = `
      <div class="ev-header">
        <span class="ev-tag ${isAudio ? 'ev-audio' : 'ev-doc'}">${ev.evidence_type.toUpperCase()}</span>
        <span class="ev-id">${ev.id}</span>
      </div>
      <div class="ev-filename" title="${ev.filename}">${ev.filename}</div>
      <div class="ev-hash">SHA: ${ev.sha256_hash.substring(0, 16)}...</div>
    `;

    card.addEventListener('click', () => openEvidenceModal(ev));
    evidenceListEl.appendChild(card);
  });
}

// Setup Drag & Drop Upload
function setupUpload() {
  dropzone.addEventListener('click', () => fileInput.click());
  
  dropzone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropzone.classList.add('drag-active');
  });

  dropzone.addEventListener('dragleave', () => dropzone.classList.remove('drag-active'));

  dropzone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropzone.classList.remove('drag-active');
    if (e.dataTransfer.files.length) {
      uploadFiles(e.dataTransfer.files);
    }
  });

  fileInput.addEventListener('change', () => {
    if (fileInput.files.length) {
      uploadFiles(fileInput.files);
    }
  });
}

async function uploadFiles(files) {
  for (let file of files) {
    const formData = new FormData();
    formData.append('file', file);
    try {
      const res = await fetch(`${API_BASE}/api/upload`, {
        method: 'POST',
        body: formData
      });
      if (res.ok) {
        const item = await res.json();
        currentEvidence.push(item);
      }
    } catch (e) {
      console.error("Upload error:", e);
    }
  }
  renderEvidenceList();
}

// Run Analysis
async function runAnalysis() {
  btnAnalyze.disabled = true;
  btnAnalyze.innerHTML = `
    <svg class="spinner" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <circle cx="12" cy="12" r="10"></circle>
      <path d="M12 6v6l4 2"></path>
    </svg>
    Analyzing Evidence...
  `;

  try {
    const res = await fetch(`${API_BASE}/api/analyze`, { method: 'POST' });
    if (!res.ok) {
      alert("Failed to run analysis. Check console.");
      return;
    }
    currentReport = await res.json();
    renderAnalysisResults(currentReport);
  } catch (err) {
    console.error("Analysis execution error:", err);
    alert("Analysis failed. Is backend running?");
  } finally {
    btnAnalyze.disabled = false;
    btnAnalyze.innerHTML = `
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <polygon points="5 3 19 12 5 21 5 3"></polygon>
      </svg>
      Run Forensic Analysis
    `;
  }
}

// Render Results
function renderAnalysisResults(report) {
  analysisSummaryEl.textContent = report.summary;
  contraPillEl.textContent = report.contradiction_count;
  timelinePillEl.textContent = report.timeline_count;
  entityPillEl.textContent = report.entity_count;

  // Render Contradictions
  contradictionsContainerEl.innerHTML = '';
  if (report.contradictions.length === 0) {
    contradictionsContainerEl.innerHTML = '<div class="quote-box">No direct contradictions flagged among current evidence.</div>';
  } else {
    report.contradictions.forEach(c => {
      const card = document.createElement('div');
      card.className = 'contra-card';
      card.innerHTML = `
        <div class="contra-header">
          <div class="contra-title">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
              <line x1="12" y1="9" x2="12" y2="13"></line>
              <line x1="12" y1="17" x2="12.01" y2="17"></line>
            </svg>
            ${c.title}
          </div>
          <span class="contra-badge">${c.severity} RISK · ${c.category}</span>
        </div>
        <div class="contra-body">
          <div class="contra-comparison">
            <div class="quote-box">
              <div class="quote-label">
                <span>[SOURCE A]</span> ${c.source_a_name}
              </div>
              <div class="quote-text">"${c.source_a_quote}"</div>
            </div>
            <div class="quote-box">
              <div class="quote-label">
                <span>[SOURCE B]</span> ${c.source_b_name}
              </div>
              <div class="quote-text">"${c.source_b_quote}"</div>
            </div>
          </div>
          <div class="contra-reasoning">
            <strong>FORENSIC REASONING:</strong> ${c.analysis_reasoning || c.description}
          </div>
        </div>
      `;
      contradictionsContainerEl.appendChild(card);
    });
  }

  // Render Timeline
  timelineContainerEl.innerHTML = '';
  report.timeline.forEach(t => {
    const node = document.createElement('div');
    node.className = 'timeline-node';
    node.innerHTML = `
      <div class="timeline-dot"></div>
      <div class="timeline-card">
        <div class="timeline-time">${t.timestamp_raw}</div>
        <div class="timeline-desc">${t.event_description}</div>
        <div class="timeline-meta">
          <span>SOURCE: <strong>${t.source_name}</strong></span>
          ${t.entities.length ? `<span>ENTITIES: ${t.entities.join(', ')}</span>` : ''}
        </div>
      </div>
    `;
    timelineContainerEl.appendChild(node);
  });

  // Render Entities
  entityContainerEl.innerHTML = '';
  report.entities.forEach(ent => {
    const card = document.createElement('div');
    card.className = 'entity-card';
    card.innerHTML = `
      <div>
        <div class="entity-name">${ent.name}</div>
        <div class="entity-type">${ent.entity_type}</div>
      </div>
      <div class="entity-count">${ent.mentions} mention${ent.mentions > 1 ? 's' : ''}</div>
    `;
    entityContainerEl.appendChild(card);
  });

  // Render Court Dossier
  renderDossierView(report);
}

// Generate Printable Court Dossier
function renderDossierView(report) {
  let doc = `========================================================================================\n`;
  doc += `                AEGISDESK CERTIFIED FORENSIC INVESTIGATION REPORT                      \n`;
  doc += `========================================================================================\n`;
  doc += `CASE ID:        ${report.case_id}\n`;
  doc += `CASE TITLE:     ${report.case_name}\n`;
  doc += `ANALYZED AT:    ${report.analyzed_at}\n`;
  doc += `AIR-GAP AUDIT:  ${report.airgap_audit.verification_message}\n`;
  doc += `INFERENCE MODEL: ${report.model_used} (Offline Execution)\n`;
  doc += `----------------------------------------------------------------------------------------\n\n`;

  doc += `[1. CHAIN OF CUSTODY EVIDENCE INTEGRITY TABLE]\n`;
  doc += `ID       | FILENAME                          | TYPE     | SHA-256 HASH\n`;
  doc += `---------+-----------------------------------+----------+-----------------------------------------------------------------\n`;
  currentEvidence.forEach(e => {
    const fn = e.filename.padEnd(33, ' ').substring(0, 33);
    const typ = e.evidence_type.padEnd(8, ' ');
    doc += `${e.id.padEnd(8, ' ')} | ${fn} | ${typ} | ${e.sha256_hash}\n`;
  });

  doc += `\n[2. EXECUTIVE INTELLIGENCE SUMMARY]\n`;
  doc += `${report.summary}\n\n`;

  doc += `[3. CONTRADICTION & PERJURY MATRIX (${report.contradiction_count} FLAGGED)]\n`;
  report.contradictions.forEach((c, idx) => {
    doc += `\n--- DISCREPANCY #${idx + 1}: ${c.title} [SEVERITY: ${c.severity}] ---\n`;
    doc += `SOURCE A [${c.source_a_name}]: "${c.source_a_quote}"\n`;
    doc += `SOURCE B [${c.source_b_name}]: "${c.source_b_quote}"\n`;
    doc += `ANALYSIS: ${c.analysis_reasoning}\n`;
  });

  doc += `\n[4. RECONSTRUCTED CHRONOLOGICAL TIMELINE (${report.timeline_count} EVENTS)]\n`;
  report.timeline.forEach((t, idx) => {
    doc += `[${t.timestamp_raw.padEnd(24, ' ')}] : ${t.event_description} (Source: ${t.source_name})\n`;
  });

  doc += `\n========================================================================================\n`;
  doc += `CERTIFICATION: Generated in a verified air-gapped cryptographic sandbox.\n`;
  doc += `========================================================================================\n`;

  dossierViewEl.textContent = doc;
}

// Reset Demo Case
async function resetDemoCase() {
  try {
    const res = await fetch(`${API_BASE}/api/reset-sample`, { method: 'POST' });
    if (res.ok) {
      currentEvidence = await res.json();
      renderEvidenceList();
      runAnalysis();
    }
  } catch (err) {
    console.error("Reset demo error:", err);
  }
}

// Modal
function setupModal() {
  modalClose.addEventListener('click', closeModal);
  modalBackdrop.addEventListener('click', (e) => {
    if (e.target === modalBackdrop) closeModal();
  });
}

function openEvidenceModal(item) {
  modalFilename.textContent = item.filename;
  modalMeta.textContent = `ID: ${item.id} | TYPE: ${item.evidence_type.toUpperCase()} | SHA-256: ${item.sha256_hash}`;
  modalContent.textContent = item.extracted_text;
  modalBackdrop.style.display = 'flex';
}

function closeModal() {
  modalBackdrop.style.display = 'none';
}

