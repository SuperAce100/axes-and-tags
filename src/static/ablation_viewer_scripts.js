// Ablation viewer script – allows replaying historical generations
// Depends on scripts.js for rendering utilities. We patch the initial
// fetch that scripts.js performs so that it returns the first history
// entry instead of hitting the network.


const { id: ablationId } = window.__ABLATION_VIEWER__ || {};


// Global state shared with scripts.js
window.sessionId = ablationId;

let historyData = [];
let currentIndex = 0;

// Fetch history once on initial load and cache it.
async function loadHistory() {
  if (historyData.length > 0) return historyData;
  const res = await originalFetch(`/api/ablation/${ablationId}/history`);
  if (!res.ok) {
    throw new Error("Failed to fetch ablation history");
  }
  historyData = await res.json();
  return historyData;
} 

// Keep reference to original fetch *after* binding.
const originalFetch = window.fetch.bind(window);

// ------------------------------------------------------------------
// Intercept scripts.js API calls so they always reflect the *current* entry.
// Every interception triggers a fresh DB fetch via getCurrentEntry().
// ------------------------------------------------------------------
window.fetch = async function (resource, init) {
  if (typeof resource === "string" && resource.startsWith("/api/generation/")) {
    // Ensure history is loaded before first intercept
    if (historyData.length === 0) {
      await loadHistory();
    }
    const entry = historyData[currentIndex];
    const responseBody = JSON.stringify({
      design_space: entry.design_space,
      generations: entry.generations,
    });
    return new Response(responseBody, {
      status: 200,
      headers: { "Content-Type": "application/json" },
    });
  }
  return originalFetch(resource, init);
};

function updateHeader(entry) {
  const conceptEl = document.getElementById("concept");
  const detailEl = document.getElementById("detailText");
  if (conceptEl) {
    conceptEl.textContent = entry.design_space.concept;
  }
  if (detailEl) {
    detailEl.textContent = `Entry ${currentIndex + 1} / ${historyData.length} — Variant ${
      entry.variant_index + 1
    }, Prompt ${entry.prompt_index + 1}`;
  }
}

async function renderCurrent() {
  if (historyData.length === 0) await loadHistory();
  const entry = historyData[currentIndex];
  console.log("entry", entry);

  // scripts.js expects these globals
  window.designSpace = entry.design_space;
  window.generations = entry.generations;
  designSpace = entry.design_space;
  generations = entry.generations;

  if (typeof window.renderDesignSpace === "function") {
    window.renderDesignSpace();
  }
  if (typeof window.renderGrid === "function") {
    window.renderGrid();
  }
  updateHeader(entry);
}

function attachNavHandlers() {
  const prevBtn = document.getElementById("prevButton");
  const nextBtn = document.getElementById("nextButton");

  if (prevBtn) {
    prevBtn.addEventListener("click", () => {
      currentIndex -= 1;
      if (currentIndex < 0) currentIndex = 0;
      renderCurrent();
    });
  }

  if (nextBtn) {
    nextBtn.addEventListener("click", () => {
      currentIndex += 1;
      if (currentIndex >= historyData.length) currentIndex = historyData.length - 1;
      renderCurrent();
    });
  }
}

// Wait until DOM & scripts.js have loaded
document.addEventListener("DOMContentLoaded", async () => {
  try {
    await loadHistory();
    renderCurrent();
    attachNavHandlers();
  } catch (err) {
    console.error("Error loading ablation history:", err);
    alert("Unable to load ablation history – see console for details.");
  }
});
