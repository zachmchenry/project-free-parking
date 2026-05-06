// Lobby guard and timer startup.

(function () {
  if (!window.ProjectFreeParking.getName()) {
    window.location.href = "/";
    return;
  }
  window.ProjectFreeParking.ensureTimerStarted();
  window.ProjectFreeParking.renderTimer();

  const logoutBtn = document.getElementById("logout");
  const summaryEl = document.getElementById("logout-summary");
  const summaryTitleEl = document.getElementById("logout-summary-title");
  const summaryTextEl = document.getElementById("logout-summary-text");
  const personaTimesEl = document.getElementById("logout-persona-times");
  const startOverBtn = document.getElementById("start-over");
  const personaGrid = document.querySelector(".persona-grid");

  function renderPersonaTimes(items) {
    personaTimesEl.innerHTML = "";
    (items || []).forEach((item) => {
      const row = document.createElement("div");
      row.className = "persona-time-row";
      const name = document.createElement("span");
      name.textContent = item.persona_name || item.persona_key;
      const duration = document.createElement("strong");
      duration.textContent = item.formatted || window.ProjectFreeParking.formatSeconds(item.seconds);
      row.append(name, duration);
      personaTimesEl.appendChild(row);
    });
  }

  async function logout() {
    const userName = window.ProjectFreeParking.getName();
    logoutBtn.disabled = true;
    logoutBtn.textContent = "Ending...";

    try {
      const res = await fetch("/api/user/end", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_name: userName,
          session_ids: window.ProjectFreeParking.getSessionIds(),
          total_elapsed_seconds: window.ProjectFreeParking.getElapsedSeconds(),
          persona_durations: window.ProjectFreeParking.getPersonaDurations(),
        }),
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        throw new Error(data.error || res.statusText);
      }
      summaryTitleEl.textContent = `Session complete for ${data.user_name}`;
      summaryTextEl.textContent = data.summary;
      renderPersonaTimes(data.persona_durations);
      summaryEl.classList.remove("hidden");
      if (personaGrid) personaGrid.classList.add("hidden");
      window.ProjectFreeParking.clearUserSession();
      summaryEl.scrollIntoView({ behavior: "smooth", block: "start" });
    } catch (err) {
      logoutBtn.disabled = false;
      logoutBtn.textContent = "Log Out";
      summaryTitleEl.textContent = "Could not end session";
      summaryTextEl.textContent = err.message;
      personaTimesEl.innerHTML = "";
      summaryEl.classList.remove("hidden");
    }
  }

  logoutBtn.addEventListener("click", logout);
  startOverBtn.addEventListener("click", function () {
    window.ProjectFreeParking.clearUserSession();
    window.location.href = "/";
  });
})();
