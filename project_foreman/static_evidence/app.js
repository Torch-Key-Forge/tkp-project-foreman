let fixture = null;
let recovery = null;
let activityStartedAt = null;
let activityTimer = null;
let activityRunning = false;
let stagePlan = [];
let stageStates = new Map();

const statusEl = document.getElementById("status");
const statusState = document.getElementById("statusState");
const statusOperation = document.getElementById("statusOperation");
const statusElapsed = document.getElementById("statusElapsed");
const statusMessage = document.getElementById("statusMessage");
const activityTrack = document.getElementById("activityTrack");
const stageProgress = document.getElementById("stageProgress");
const stageProgressFill = document.getElementById("stageProgressFill");
const stagePercent = document.getElementById("stagePercent");
const statusStages = document.getElementById("statusStages");
const statusLog = document.getElementById("statusLog");
const loadBtn = document.getElementById("loadBtn");
const recoverBtn = document.getElementById("recoverBtn");
const exportBtn = document.getElementById("exportBtn");
const sourceView = document.getElementById("sourceView");
const sourceBadge = document.getElementById("sourceBadge");
const exportStatus = document.getElementById("exportStatus");

async function fetchJson(url) {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`Request failed: ${res.status}`);
  return res.json();
}

async function streamJsonLines(url, onEvent) {
  const res = await fetch(url, {
    headers: { Accept: "application/x-ndjson" },
    cache: "no-store",
  });
  if (!res.ok) throw new Error(`Request failed: ${res.status}`);
  if (!res.body) throw new Error("Streaming response body is unavailable.");

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { value, done } = await reader.read();
    buffer += decoder.decode(value || new Uint8Array(), { stream: !done });

    let newlineIndex = buffer.indexOf("\n");
    while (newlineIndex >= 0) {
      const line = buffer.slice(0, newlineIndex).trim();
      buffer = buffer.slice(newlineIndex + 1);
      if (line) onEvent(JSON.parse(line));
      newlineIndex = buffer.indexOf("\n");
    }

    if (done) break;
  }

  const finalLine = buffer.trim();
  if (finalLine) onEvent(JSON.parse(finalLine));
}

function formatElapsed(milliseconds) {
  const totalSeconds = Math.max(0, Math.floor(milliseconds / 1000));
  const hours = Math.floor(totalSeconds / 3600);
  const minutes = Math.floor((totalSeconds % 3600) / 60);
  const seconds = totalSeconds % 60;
  const clock = [minutes, seconds].map(value => String(value).padStart(2, "0")).join(":");
  return hours > 0 ? `${String(hours).padStart(2, "0")}:${clock}` : clock;
}

function syncActionAvailability() {
  loadBtn.disabled = activityRunning;
  recoverBtn.disabled = activityRunning;
  exportBtn.disabled = activityRunning || !recovery;
}

function setStatus(state, operation, message) {
  statusEl.dataset.state = state;
  statusEl.className = `status status-${state.toLowerCase()}`;
  statusEl.setAttribute("aria-busy", state === "RUNNING" ? "true" : "false");
  statusState.textContent = state;
  statusOperation.textContent = operation;
  statusMessage.textContent = message;
}

function updateElapsed() {
  if (activityStartedAt === null) return;
  statusElapsed.textContent = formatElapsed(performance.now() - activityStartedAt);
}

function setProgressMode(mode) {
  const staged = mode === "staged";
  activityTrack.classList.toggle("hidden", staged);
  stageProgress.classList.toggle("hidden", !staged);
  statusStages.classList.toggle("hidden", !staged);
}

function resetStagedProgress() {
  stagePlan = [];
  stageStates = new Map();
  statusStages.innerHTML = "";
  statusLog.textContent = "";
  setStageCompletion(0, 0);
}

function beginActivity(operation, message, mode = "indeterminate") {
  activityRunning = true;
  activityStartedAt = performance.now();
  statusElapsed.textContent = "00:00";
  setStatus("RUNNING", operation, message);
  setProgressMode(mode);
  if (mode === "staged") resetStagedProgress();
  syncActionAvailability();
  window.clearInterval(activityTimer);
  activityTimer = window.setInterval(updateElapsed, 250);
}

function finishActivity(state, operation, message) {
  updateElapsed();
  window.clearInterval(activityTimer);
  activityTimer = null;
  activityStartedAt = null;
  activityRunning = false;
  setStatus(state, operation, message);
  syncActionAvailability();
}

function describeError(error) {
  return error instanceof Error ? error.message : String(error);
}

function appendStatusLog(message) {
  const timestamp = statusElapsed.textContent || "00:00";
  statusLog.textContent += `${statusLog.textContent ? "\n" : ""}[${timestamp}] ${message}`;
}

async function runActivity({ operation, startMessage, task, successMessage }) {
  beginActivity(operation, startMessage, "indeterminate");
  try {
    const result = await task();
    finishActivity("PASS", operation, successMessage(result));
    return result;
  } catch (error) {
    finishActivity("FAIL", operation, `${operation} failed: ${describeError(error)}. Review the message and retry.`);
    throw error;
  }
}

function stageMarker(status) {
  if (status === "PASS") return "✓";
  if (status === "RUNNING") return "→";
  if (status === "FAIL") return "!";
  return "○";
}

function setStageCompletion(completed, total) {
  const percentage = total > 0 ? Math.round((completed / total) * 100) : 0;
  stageProgressFill.style.width = `${percentage}%`;
  stagePercent.textContent = `${percentage}%`;
  stageProgress.setAttribute("aria-valuenow", String(percentage));
  stageProgress.setAttribute(
    "aria-valuetext",
    total > 0 ? `${completed} of ${total} stages complete` : "No staged operation active"
  );
}

function renderStagePlan(stages) {
  stagePlan = stages;
  stageStates = new Map(stages.map(stage => [stage.id, "PENDING"]));
  statusStages.innerHTML = "";

  stages.forEach(stage => {
    const item = document.createElement("li");
    item.dataset.stageId = stage.id;
    item.dataset.status = "PENDING";
    item.innerHTML = `
      <span class="stage-marker" aria-hidden="true">○</span>
      <span class="stage-label">${stage.label}</span>
      <span class="stage-state">Pending</span>
    `;
    statusStages.appendChild(item);
  });

  setStageCompletion(0, stages.length);
  appendStatusLog(`Plan received: ${stages.length} real execution stages.`);
}

function applyStageEvent(event) {
  const item = statusStages.querySelector(`[data-stage-id="${event.stage_id}"]`);
  if (!item) return;

  stageStates.set(event.stage_id, event.status);
  item.dataset.status = event.status;
  item.querySelector(".stage-marker").textContent = stageMarker(event.status);
  item.querySelector(".stage-state").textContent =
    event.status === "RUNNING" ? "Running" :
    event.status === "PASS" ? "Complete" :
    event.status === "FAIL" ? "Failed" : "Pending";

  const completed = [...stageStates.values()].filter(status => status === "PASS").length;
  setStageCompletion(completed, stagePlan.length);
  statusMessage.textContent = event.message;
  appendStatusLog(`${event.label}: ${event.status} — ${event.message}`);
}

async function runStagedActivity({ operation, startMessage, url, successMessage }) {
  beginActivity(operation, startMessage, "staged");
  let finalResult = null;
  let streamError = null;

  try {
    await streamJsonLines(url, event => {
      if (event.type === "plan") {
        renderStagePlan(event.stages);
        return;
      }
      if (event.type === "stage") {
        applyStageEvent(event);
        return;
      }
      if (event.type === "result") {
        finalResult = event.result;
        return;
      }
      if (event.type === "error") {
        streamError = new Error(event.error || `${operation} failed.`);
      }
    });

    if (streamError) throw streamError;
    if (!finalResult) throw new Error("Operation ended without a final result.");

    finishActivity("PASS", operation, successMessage(finalResult));
    appendStatusLog(`${operation}: PASS`);
    return finalResult;
  } catch (error) {
    finishActivity("FAIL", operation, `${operation} failed: ${describeError(error)}. Review the failed stage and retry.`);
    appendStatusLog(`${operation}: FAIL — ${describeError(error)}`);
    throw error;
  }
}

function setMetrics(values) {
  const cards = document.querySelectorAll(".metric strong");
  const ordered = [
    values.turns,
    values.spine_events,
    values.authority_entries,
    values.open_items,
    values.traceable_claims,
  ];
  cards.forEach((card, i) => card.textContent = ordered[i] ?? "—");
}

function sourceByRef(sourceRef) {
  return recovery.source_trace_index.source_turns.find(x => x.source_ref === sourceRef);
}

function showSource(sourceRef) {
  const source = sourceByRef(sourceRef);
  if (!source) {
    sourceView.textContent = "Source turn not found.";
    return;
  }

  sourceBadge.textContent = source.source_ref;
  sourceView.classList.remove("empty");
  sourceView.innerHTML = `
    <div class="role">${source.role}</div>
    <div class="meta">
      Conversation: ${source.conversation_id}<br>
      Turn: ${source.ordinal} · ${source.turn_id}<br>
      SHA-256: ${source.text_sha256.slice(0, 20)}…
    </div>
    <div class="text"></div>
  `;
  sourceView.querySelector(".text").textContent = source.text;
}

function renderSpine() {
  const list = document.getElementById("spineList");
  const items = recovery.project_spine.spine_events;
  document.getElementById("spineCount").textContent = items.length;
  list.classList.remove("empty");
  list.innerHTML = "";

  items.forEach(item => {
    const btn = document.createElement("button");
    btn.className = "list-item";
    btn.innerHTML = `
      <strong>${item.sequence}. ${item.title}</strong>
      <div class="item-meta">${item.event_type} · ${item.status}</div>
    `;
    btn.addEventListener("click", () => {
      document.querySelectorAll(".list-item").forEach(x => x.classList.remove("active"));
      btn.classList.add("active");
      showSource(item.source_refs[0]);
    });
    list.appendChild(btn);
  });
}

function renderAuthority() {
  const view = document.getElementById("authorityView");
  view.innerHTML = "";

  recovery.authority_ledger.entries.forEach(entry => {
    const card = document.createElement("div");
    card.className = "authority-card";
    const button = document.createElement("button");
    button.innerHTML = `
      <div class="badge">${entry.decision_class}</div>
      <div class="authority-statement">${entry.statement}</div>
      <div class="item-meta authority-meta">
        ${entry.authority_status} · ${entry.execution_status}
      </div>
    `;
    button.addEventListener("click", () => showSource(entry.source_refs[0]));
    card.appendChild(button);
    view.appendChild(card);
  });
}

function renderContinuation() {
  const c = recovery.continuation_brief;
  const view = document.getElementById("continuationView");
  view.innerHTML = `
    <div class="continuation-block">
      <div class="badge">Last trustworthy state</div>
      <div>${c.last_trustworthy_state}</div>
    </div>
    <div class="continuation-block">
      <div class="badge">Completed</div>
      <ul>${c.completed.map(x => `<li>${x}</li>`).join("")}</ul>
    </div>
    <div class="continuation-block">
      <div class="badge">Unresolved</div>
      <ul>${c.unresolved.map(x => `<li>${x}</li>`).join("")}</ul>
    </div>
    <div class="continuation-block boundary" id="productionBoundary">
      <div class="badge">Explicit boundaries</div>
      <ul>${c.boundaries.map(x => `<li>${x}</li>`).join("")}</ul>
    </div>
    <div class="continuation-block">
      <div class="badge">Recommended next action</div>
      <div>${c.recommended_next_action}</div>
    </div>
  `;
  document.getElementById("productionBoundary").addEventListener("click", () => showSource(c.source_refs[1]));
}

function renderEvidenceBoundary() {
  const policy = recovery.evidence_boundary;
  const demo = policy.demo_case;
  const view = document.getElementById("evidenceView");

  view.innerHTML = `
    <div class="evidence-hero">
      <div class="badge">${policy.mode}</div>
      <h3>${policy.public_rule}</h3>
      <p>${policy.purpose}</p>
    </div>

    <div class="state-grid">
      ${policy.sifting_states.map(item => `
        <div class="state-card">
          <strong>${item.state}</strong>
          <span>${item.meaning}</span>
        </div>
      `).join("")}
    </div>

    <div class="evidence-demo">
      <div class="badge">Unsupported claim test</div>
      <div class="demo-question">Question: ${demo.question}</div>
      <div class="demo-result">${demo.result}</div>
      <p>${policy.fail_closed_response.message}</p>
      <small>${demo.explanation}</small>
    </div>

    <div class="evidence-rules">
      <div><strong>Assistant authority promotion:</strong> ${policy.candidate_handling.assistant_authority_promotion}</div>
      <div><strong>Command completion without evidence:</strong> ${policy.execution_handling.command_without_completion_evidence}</div>
      <div><strong>Candidate disposition:</strong> ${policy.candidate_handling.disposition}</div>
      <div><strong>Promotion:</strong> ${policy.candidate_handling.promotion_rule}</div>
    </div>
  `;
}

loadBtn.addEventListener("click", async () => {
  try {
    await runActivity({
      operation: "LOAD FIXTURE",
      startMessage: "Loading the sanitized Atlas Workshop fixture…",
      task: async () => {
        fixture = await fetchJson("/api/fixture");
        return fixture;
      },
      successMessage: loaded => `Loaded ${loaded.conversation_identity.title} · ${loaded.turns.length} turns.`,
    });
  } catch (error) {
    console.error(error);
  }
});

recoverBtn.addEventListener("click", async () => {
  try {
    recovery = await runStagedActivity({
      operation: "RECOVER PROJECT",
      startMessage: "Beginning governed project recovery…",
      url: "/api/recover/stream",
      successMessage: recovered => `Recovery complete · ${recovered.metrics.spine_events} spine events · ${recovered.metrics.authority_entries} authority entries · ${recovered.metrics.traceable_claims} traceable claims.`,
    });
    fixture = recovery.fixture;
    setMetrics(recovery.metrics);
    renderSpine();
    renderAuthority();
    renderContinuation();
    renderEvidenceBoundary();
    syncActionAvailability();
  } catch (error) {
    console.error(error);
  }
});

exportBtn.addEventListener("click", async () => {
  exportStatus.textContent = "";
  try {
    const result = await runStagedActivity({
      operation: "EXPORT PACKAGE",
      startMessage: "Beginning governed package export…",
      url: "/api/export/stream",
      successMessage: exported => `Validated ${exported.filename} · ${exported.file_count} files · SHA-256 ${exported.sha256.slice(0, 12)}…`,
    });
    exportStatus.textContent = `Saved to Downloads\\Project_Foreman_Exports · ${result.file_count} files`;
  } catch (error) {
    exportStatus.textContent = `EXPORT FAILED: ${describeError(error)}`;
    console.error(error);
  }
});

document.querySelectorAll(".tab").forEach(btn => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".tab").forEach(x => x.classList.remove("active"));
    btn.classList.add("active");
    const tab = btn.dataset.tab;
    document.getElementById("authorityView").classList.toggle("hidden", tab !== "authority");
    document.getElementById("continuationView").classList.toggle("hidden", tab !== "continuation");
    document.getElementById("evidenceView").classList.toggle("hidden", tab !== "evidence");
  });
});

setStatus("IDLE", "READY", "Load the fixture or recover the project to begin.");
setProgressMode("indeterminate");
syncActionAvailability();
