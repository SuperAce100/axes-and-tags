// This script adapts the generic generation interactions to ablation mode
// It relies on the existing scripts.js that powers normal sessions, but rewrites
// API endpoints and adds support for the "Done" button to advance through
// the prompts.

(function () {
  const ablationId = window.__ABLATION__?.id;
  if (!ablationId) return;

  // Patch global variable that scripts.js expects
  window.sessionId = ablationId;

  // Intercept fetch calls that are hard-coded to the /api/generation/* endpoints
  const originalFetch = window.fetch;
  window.fetch = function (resource, init) {
    if (typeof resource === "string" && resource.startsWith("/api/generation/")) {
      resource = resource.replace("/api/generation/", "/api/ablation/");
    }
    return originalFetch(resource, init);
  };

  // Attach Done button handler
  document.addEventListener("DOMContentLoaded", () => {
    const doneButton = document.getElementById("doneButton");
    if (!doneButton) return;
    doneButton.addEventListener("click", async () => {
      doneButton.disabled = true;
      doneButton.classList.add("opacity-50", "cursor-not-allowed");
      try {
        const res = await fetch(`/api/ablation/${ablationId}/next`, {
          method: "POST",
        });
        if (!res.ok) {
          alert("Failed to advance ablation – please try again.");
          doneButton.disabled = false;
          return;
        }
        // Reload page to fetch next prompt / variant
        window.location.reload();
      } catch (err) {
        console.error(err);
        alert("Unexpected error – check console.");
        doneButton.disabled = false;
      }
    });
  });
})(); 