/* SecureScan progressive enhancement.
 * - Scan detail: poll data-progress-url every 2s while status is not DONE/FAILED.
 * - Configure: live cost/duration hint from the estimate inputs (purely cosmetic).
 * No framework, no network calls except the JSON progress endpoint.
 */
(function () {
  "use strict";

  function pollProgress() {
    var box = document.querySelector("[data-progress-url]");
    if (!box) return;
    var bar = box.querySelector(".progress > span");
    var label = box.querySelector("[data-progress-label]");
    var statusChip = box.querySelector("[data-scan-status]");
    var terminal = ["DONE", "FAILED"];
    function tick() {
      fetch(box.getAttribute("data-progress-url"), { headers: { Accept: "application/json" } })
        .then(function (r) { return r.ok ? r.json() : null; })
        .then(function (data) {
          if (!data) return;
          if (bar) bar.style.width = Math.max(0, Math.min(100, data.progress || 0)) + "%";
          if (label) label.textContent = (data.progress || 0) + "%";
          if (statusChip && data.status) {
            statusChip.textContent = data.status;
            statusChip.className = "status-chip status-" + String(data.status).toLowerCase();
          }
          if (terminal.indexOf(data.status) === -1) {
            setTimeout(tick, 2000);
          } else if (String(data.status) === "DONE" && !box.getAttribute("data-reloaded")) {
            box.setAttribute("data-reloaded", "1");
            setTimeout(function () { window.location.reload(); }, 800);
          }
        })
        .catch(function () { /* stay on last known state */ });
    }
    setTimeout(tick, 1200);
  }

  document.addEventListener("DOMContentLoaded", pollProgress);
})();
