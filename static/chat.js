// Project Free Parking — chat frontend.
// Handles message send/receive, off-topic warning UI, typing indicator,
// and session lifecycle.

(function () {
  const chatEl = document.getElementById("chat");
  const inputEl = document.getElementById("input");
  const sendBtn = document.getElementById("send");
  const warningEl = document.getElementById("warning");
  const statusDot = document.getElementById("status-dot");
  const statusText = document.getElementById("status-text");
  const sessionTagEl = document.getElementById("session-tag");
  const appEl = document.querySelector(".chat-app");
  const endBtn = document.getElementById("end-session");
  const backLink = document.querySelector(".back-link");
  const summaryEl = document.getElementById("end-summary");
  const summaryTitleEl = document.getElementById("summary-title");
  const summaryTextEl = document.getElementById("summary-text");

  let sessionId = null;
  let sessionEnded = false;
  let sessionClosed = false;
  let sessionStartAt = Date.now();
  let personaTimeRecorded = false;
  const personaKey = appEl ? appEl.dataset.personaKey : "";
  const traineeName = window.ProjectFreeParking.getName();

  if (!traineeName) {
    window.location.href = "/";
    return;
  }
  window.ProjectFreeParking.ensureTimerStarted();

  // ---------- Helpers ----------

  function appendMessage(role, text) {
    const div = document.createElement("div");
    div.className = "msg " + (
      role === "user" ? "msg-user" :
      role === "system" ? "msg-system" :
      "msg-persona"
    );
    div.textContent = text;
    chatEl.appendChild(div);
    chatEl.scrollTop = chatEl.scrollHeight;
    return div;
  }

  function showTyping() {
    const div = document.createElement("div");
    div.className = "msg msg-persona typing";
    div.id = "typing-indicator";
    div.innerHTML = "<span></span><span></span><span></span>";
    chatEl.appendChild(div);
    chatEl.scrollTop = chatEl.scrollHeight;
  }

  function hideTyping() {
    const t = document.getElementById("typing-indicator");
    if (t) t.remove();
  }

  function setStatus(state) {
    statusDot.classList.remove("dot-active", "dot-warning", "dot-ended");
    if (state === "active") {
      statusDot.classList.add("dot-active");
      statusText.textContent = "Active";
    } else if (state === "warning") {
      statusDot.classList.add("dot-warning");
      statusText.textContent = "Off-topic warnings";
    } else if (state === "ended") {
      statusDot.classList.add("dot-ended");
      statusText.textContent = "Session ended";
    } else {
      statusDot.classList.add("dot-active");
      statusText.textContent = "Ready";
    }
  }

  function showWarning(text, isError) {
    warningEl.textContent = text;
    warningEl.classList.remove("hidden", "error");
    if (isError) warningEl.classList.add("error");
  }

  function clearWarning() {
    warningEl.classList.add("hidden");
    warningEl.classList.remove("error");
    warningEl.textContent = "";
  }

  function setComposerEnabled(enabled) {
    inputEl.disabled = !enabled;
    sendBtn.disabled = !enabled;
  }

  function autoResizeInput() {
    inputEl.style.height = "auto";
    inputEl.style.height = Math.min(inputEl.scrollHeight, 160) + "px";
  }

  function elapsedForThisChat() {
    return Math.max(0, Math.floor((Date.now() - sessionStartAt) / 1000));
  }

  function recordPersonaTime(elapsedSeconds) {
    if (personaTimeRecorded) return 0;
    const elapsed = Math.max(0, Number(elapsedSeconds || elapsedForThisChat()));
    window.ProjectFreeParking.addPersonaSeconds(personaKey, elapsed);
    personaTimeRecorded = true;
    return elapsed;
  }

  function showSummary(data) {
    summaryTitleEl.textContent = `${data.persona_name || "Chat"} ended`;
    summaryTextEl.textContent = data.summary || "This chat session has ended.";
    summaryEl.classList.remove("hidden");
    summaryEl.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }

  async function endCurrentSession(reason, showSummaryCard) {
    if (!sessionId || sessionClosed) return true;
    sessionClosed = true;
    sessionEnded = true;
    const elapsed = elapsedForThisChat();
    setStatus("ended");
    setComposerEnabled(false);
    endBtn.disabled = true;

    try {
      const res = await fetch("/api/session/end", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          session_id: sessionId,
          elapsed_seconds: elapsed,
          reason: reason || "ended_by_user",
        }),
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        throw new Error(data.error || res.statusText);
      }
      recordPersonaTime(elapsed);
      appendMessage("system", "This chat session has ended.");
      if (showSummaryCard) showSummary(data);
      return true;
    } catch (err) {
      sessionClosed = false;
      sessionEnded = false;
      setStatus("active");
      setComposerEnabled(true);
      endBtn.disabled = false;
      showWarning("Could not end session: " + err.message, true);
      return false;
    }
  }

  function sendEndBeacon(reason) {
    if (!sessionId || sessionClosed) return;
    sessionClosed = true;
    const elapsed = recordPersonaTime(elapsedForThisChat());
    const payload = JSON.stringify({
      session_id: sessionId,
      elapsed_seconds: elapsed,
      reason: reason || "navigation",
    });
    navigator.sendBeacon(
      "/api/session/end",
      new Blob([payload], { type: "application/json" })
    );
  }

  // ---------- API calls ----------

  async function startSession() {
    try {
      const res = await fetch("/api/session", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          persona: personaKey,
          user_name: traineeName,
        }),
      });
      if (!res.ok) throw new Error("Failed to start session");
      const data = await res.json();
      sessionId = data.session_id;
      sessionStartAt = Date.now();
      window.ProjectFreeParking.addSession(sessionId);
      sessionTagEl.textContent = "Session: " + sessionId.slice(0, 8);
      appendMessage("persona", data.opening_message);
      setStatus("active");
      setComposerEnabled(true);
    } catch (err) {
      showWarning("Failed to start session: " + err.message, true);
    }
  }

  async function sendMessage(text) {
    if (sessionEnded) {
      showWarning(
        "This session has ended. Return to the lobby to start a new conversation.",
        false
      );
      return;
    }
    appendMessage("user", text);
    showTyping();
    setComposerEnabled(false);

    try {
      const res = await fetch("/api/message", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: sessionId, message: text }),
      });
      hideTyping();

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        showWarning(
          "Error from server: " + (errData.error || res.statusText),
          true
        );
        setComposerEnabled(true);
        return;
      }

      const data = await res.json();
      appendMessage("persona", data.reply);

      // Update status / warnings based on cut-off state
      if (data.cut_off || data.state === "ended") {
        setStatus("ended");
        sessionEnded = true;
        sessionClosed = true;
        recordPersonaTime();
        endBtn.disabled = true;
        appendMessage(
          "system",
          "The stakeholder has stepped away. Return to the lobby to start a new session."
        );
        setComposerEnabled(false);
        return;
      }

      if (data.off_topic_count >= 1) {
        setStatus("warning");
        const remaining = (data.off_topic_count >= 3)
          ? "One more off-topic message will end this session."
          : "Try to keep the conversation focused on the redesign.";
        showWarning(
          `Off-topic count: ${data.off_topic_count}. ${remaining}`,
          false
        );
      } else {
        clearWarning();
        setStatus("active");
      }

      setComposerEnabled(true);
      inputEl.focus();
    } catch (err) {
      hideTyping();
      showWarning("Network error: " + err.message, true);
      setComposerEnabled(true);
    }
  }

  // ---------- Event wiring ----------

  function trySend() {
    const text = inputEl.value.trim();
    if (!text) return;
    inputEl.value = "";
    autoResizeInput();
    sendMessage(text);
  }

  sendBtn.addEventListener("click", trySend);
  endBtn.addEventListener("click", function () {
    endCurrentSession("ended_by_user", true);
  });

  backLink.addEventListener("click", async function (event) {
    if (!sessionId || sessionClosed) return;
    event.preventDefault();
    const href = backLink.href;
    await endCurrentSession("navigation", false);
    window.location.href = href;
  });

  inputEl.addEventListener("keydown", function (e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      trySend();
    }
  });

  inputEl.addEventListener("input", autoResizeInput);
  window.addEventListener("pagehide", function () {
    sendEndBeacon("navigation");
  });

  // ---------- Init ----------
  setComposerEnabled(false);
  startSession();
  inputEl.focus();
})();
