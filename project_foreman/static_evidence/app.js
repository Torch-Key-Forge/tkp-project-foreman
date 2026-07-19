let fixture = null;
let recovery = null;

const statusEl = document.getElementById("status");
const exportBtn = document.getElementById("exportBtn");
const sourceView = document.getElementById("sourceView");
const sourceBadge = document.getElementById("sourceBadge");

async function fetchJson(url) {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`Request failed: ${res.status}`);
  return res.json();
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

document.getElementById("loadBtn").addEventListener("click", async () => {
  statusEl.textContent = "Loading sanitized Atlas Workshop fixture…";
  fixture = await fetchJson("/api/fixture");
  statusEl.textContent = `Loaded ${fixture.conversation_identity.title} · ${fixture.turns.length} turns`;
});

document.getElementById("recoverBtn").addEventListener("click", async () => {
  if (!fixture) {
    fixture = await fetchJson("/api/fixture");
  }
  statusEl.textContent = "Recovering project spine, authority, continuation state, source traces, and evidence boundary…";
  recovery = await fetchJson("/api/recover");
  setMetrics(recovery.metrics);
  renderSpine();
  renderAuthority();
  renderContinuation();
  renderEvidenceBoundary();
  exportBtn.disabled = false;
  statusEl.textContent = "Recovery complete. Canonical evidence remains separate from provisional review and unavailable sources.";
});

document.getElementById("exportBtn").addEventListener("click", async () => {
  const out = document.getElementById("exportStatus");
  out.textContent = "Exporting and validating ZIP…";
  try {
    const result = await fetchJson("/api/export");
    out.textContent = `Validated export: ${result.filename} · ${result.file_count} files · Downloads\\Project_Foreman_Exports`;
  } catch (error) {
    out.textContent = `EXPORT FAILED: ${error.message}`;
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
