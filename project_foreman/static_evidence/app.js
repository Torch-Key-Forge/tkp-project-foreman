let fixture = null;
let recovery = null;
let activityStartedAt = null;
let activityTimer = null;
let activityRunning = false;

const statusEl = document.getElementById("status");
const statusState = document.getElementById("statusState");
const statusOperation = document.getElementById("statusOperation");
const statusElapsed = document.getElementById("statusElapsed");
const statusMessage = document.getElementById("statusMessage");
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

function beginActivity(operation, message) {
  activityRunning = true;
  activityStartedAt = performance.now();
  statusElapsed.textContent = "00:00";
  setStatus("RUNNING", operation, message);
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

async function runActivity({ operation, startMessage, task, successMessage }) {
  beginActivity(operation, startMessage);
  try {
    const result = await task();
    finishActivity("PASS", operation, successMessage(result));
    return result;
  } catch (error) {
    finishActivity("FAIL", operation, `${operation} failed: ${describeError(error)}. Review the message and retry.`);
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
    await runActivity({
      operation: "RECOVER PROJECT",
      startMessage: "Recovering project structure, authority, continuation state, source traces, and evidence boundary…",
      task: async () => {
        if (!fixture) fixture = await fetchJson("/api/fixture");
        recovery = await fetchJson("/api/recover");
        setMetrics(recovery.metrics);
        renderSpine();
        renderAuthority();
        renderContinuation();
        renderEvidenceBoundary();
        return recovery;
      },
      successMessage: recovered => `Recovery complete · ${recovered.metrics.spine_events} spine events · ${recovered.metrics.authority_entries} authority entries · ${recovered.metrics.traceable_claims} traceable claims.`,
    });
  } catch (error) {
    console.error(error);
  }
});

exportBtn.addEventListener("click", async () => {
  exportStatus.textContent = "";
  try {
    const result = await runActivity({
      operation: "EXPORT PACKAGE",
      startMessage: "Creating and validating the evidence-bound project package…",
      task: () => fetchJson("/api/export"),
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
syncActionAvailability();
