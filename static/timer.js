// Shared trainee name and elapsed-time display for Project Free Parking.

(function () {
  const NAME_KEY = "pfp:userName";
  const START_KEY = "pfp:timerStartedAt";
  const SESSION_IDS_KEY = "pfp:sessionIds";
  const PERSONA_DURATIONS_KEY = "pfp:personaDurations";

  function readJson(key, fallback) {
    try {
      return JSON.parse(localStorage.getItem(key) || "");
    } catch (err) {
      return fallback;
    }
  }

  function writeJson(key, value) {
    localStorage.setItem(key, JSON.stringify(value));
  }

  function getName() {
    return localStorage.getItem(NAME_KEY) || "";
  }

  function setName(name) {
    const cleanName = (name || "").trim().replace(/\s+/g, " ").slice(0, 80);
    const previousName = getName();
    localStorage.setItem(NAME_KEY, cleanName);
    if (!localStorage.getItem(START_KEY) || previousName !== cleanName) {
      localStorage.setItem(START_KEY, String(Date.now()));
      writeJson(SESSION_IDS_KEY, []);
      writeJson(PERSONA_DURATIONS_KEY, {});
    }
    render();
  }

  function ensureTimerStarted() {
    if (!localStorage.getItem(START_KEY)) {
      localStorage.setItem(START_KEY, String(Date.now()));
    }
  }

  function formatElapsed(ms) {
    const totalSeconds = Math.max(0, Math.floor(ms / 1000));
    const hours = Math.floor(totalSeconds / 3600);
    const minutes = Math.floor((totalSeconds % 3600) / 60);
    const seconds = totalSeconds % 60;
    const mm = String(minutes).padStart(2, "0");
    const ss = String(seconds).padStart(2, "0");
    if (hours > 0) {
      return `${hours}:${mm}:${ss}`;
    }
    return `${mm}:${ss}`;
  }

  function formatSeconds(seconds) {
    return formatElapsed(Number(seconds || 0) * 1000);
  }

  function getElapsedSeconds() {
    const start = Number(localStorage.getItem(START_KEY) || Date.now());
    return Math.max(0, Math.floor((Date.now() - start) / 1000));
  }

  function addSession(sessionId) {
    if (!sessionId) return;
    const ids = readJson(SESSION_IDS_KEY, []);
    if (!ids.includes(sessionId)) {
      ids.push(sessionId);
      writeJson(SESSION_IDS_KEY, ids);
    }
  }

  function getSessionIds() {
    return readJson(SESSION_IDS_KEY, []);
  }

  function addPersonaSeconds(personaKey, seconds) {
    if (!personaKey || !seconds) return;
    const durations = readJson(PERSONA_DURATIONS_KEY, {});
    durations[personaKey] = Math.max(
      0,
      Number(durations[personaKey] || 0) + Math.max(0, Number(seconds || 0))
    );
    writeJson(PERSONA_DURATIONS_KEY, durations);
  }

  function getPersonaDurations() {
    return readJson(PERSONA_DURATIONS_KEY, {});
  }

  function clearUserSession() {
    localStorage.removeItem(NAME_KEY);
    localStorage.removeItem(START_KEY);
    localStorage.removeItem(SESSION_IDS_KEY);
    localStorage.removeItem(PERSONA_DURATIONS_KEY);
  }

  function render() {
    const name = getName();
    const start = Number(localStorage.getItem(START_KEY) || Date.now());
    document.querySelectorAll(".js-trainee-name").forEach((el) => {
      el.textContent = name;
    });
    document.querySelectorAll(".js-session-timer").forEach((el) => {
      el.textContent = formatElapsed(Date.now() - start);
    });
  }

  window.ProjectFreeParking = {
    NAME_KEY,
    START_KEY,
    SESSION_IDS_KEY,
    PERSONA_DURATIONS_KEY,
    getName,
    setName,
    ensureTimerStarted,
    getElapsedSeconds,
    addSession,
    getSessionIds,
    addPersonaSeconds,
    getPersonaDurations,
    clearUserSession,
    formatSeconds,
    renderTimer: render,
  };

  document.addEventListener("DOMContentLoaded", function () {
    render();
    setInterval(render, 1000);
  });
})();
