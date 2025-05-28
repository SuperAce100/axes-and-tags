let isFirstRender = true;

let concept = null;
let designSpace = null;
let generations = [];
let sessionId = null;

let highlightedAxis = null;

function showStatus(message, type = "info") {
  const status = document.getElementById("status");
  status.textContent = message;
  status.className = `status ${type}`;
  status.style.display = "block";

  setTimeout(() => {
    status.style.display = "none";
  }, 3000);
}

let isPromptVisible = false;

function togglePrompt() {
  isPromptVisible = !isPromptVisible;
  const promptOverlays = document.querySelectorAll(".prompt-overlay");
  promptOverlays.forEach((overlay) => {
    overlay.style.opacity = isPromptVisible ? 1 : 0;
  });
}

// cmd + i
document.addEventListener("keydown", (event) => {
  if (event.metaKey && event.key === "i") {
    togglePrompt();
  }
});

let isTagOverlayVisible = false;

function toggleTagOverlay() {
  isTagOverlayVisible = !isTagOverlayVisible;
  const tagOverlays = document.querySelectorAll(".tag-overlay");
  tagOverlays.forEach((overlay) => {
    overlay.style.opacity = isTagOverlayVisible ? 1 : 0;
  });
}

// cmd + u
document.addEventListener("keydown", (event) => {
  if (event.metaKey && event.key === "u") {
    toggleTagOverlay();
  }
});

function renderTags(tags, container) {
  console.log("tags", tags);
  // Create tags container
  const tagsContainer = document.createElement("div");
  tagsContainer.className = "flex gap-1 flex-wrap mt-1";

  // Add each tag
  if (tags && Array.isArray(tags)) {
    tags.forEach((tag) => {
      const tagElement = document.createElement("span");
      tagElement.textContent = tag.value;
      tagElement.className =
        "tag bg-white/20 px-1.5 py-0.5 rounded-full text-[10px] text-white hover:bg-white/30 hover:scale-105 cursor-pointer font-sans active:scale-95 transition-all";

      if (
        designSpace.axes.find((axis) => axis.name === tag.dimension).value === tag.value &&
        designSpace.axes.find((axis) => axis.name === tag.dimension).status === "constrained"
      ) {
        tagElement.className = tagElement.className
          .replace("bg-white/20", "bg-green-300/30")
          .replace("text-white", "text-green-500")
          .replace("hover:bg-white/30", "hover:bg-green-300/50");
      }

      tagElement.addEventListener("click", async () => {
        tagElement.className = tagElement.className
          .replace("bg-white/20", "bg-green-300/30")
          .replace("text-white", "text-green-500")
          .replace("hover:bg-white/30", "hover:bg-green-300/50");

        await updateDesignSpace(tag.dimension, tag.value, "constrained");
        renderTags(tags, container);
      });

      tagElement.addEventListener("mouseenter", () => {
        highlightedAxis = tag.dimension;
        document
          .getElementById("design-space-container-" + tag.dimension)
          .classList.add("scale-105", "shadow-md", "ring-2", "ring-green-500", "ring");
      });

      tagElement.addEventListener("mouseleave", () => {
        highlightedAxis = null;
        document
          .getElementById("design-space-container-" + tag.dimension)
          .classList.remove("scale-105", "shadow-md", "ring-2", "ring-green-500", "ring");
      });

      tagsContainer.appendChild(tagElement);
    });
  }

  const tagOverlay = document.createElement("div");
  tagOverlay.className =
    "bg-gradient-to-t from-black/85 via-black/60 to-transparent p-3 absolute bottom-0 left-0 w-full z-12 tag-overlay transition-all";
  tagOverlay.id = "tag-overlay";
  // Append elements
  tagOverlay.appendChild(tagsContainer);
  container.appendChild(tagOverlay);
}

function renderPrompt(prompt, container) {
  // Create prompt overlay with gradient
  const promptOverlay = document.createElement("div");
  promptOverlay.className =
    "absolute top-0 left-0 w-full p-3 bg-gradient-to-b from-black/85 via-black/60 to-transparent prompt-overlay transition-all";

  // Create prompt text element
  const promptElement = document.createElement("div");
  promptElement.textContent = prompt;
  promptElement.className =
    "text-white text-xs max-w-full overflow-hidden leading-tight font-sans max-h-[2.5em] hover:max-h-[200px] transition-all mask-b-from-0% mask-b-to-20%";

  promptOverlay.appendChild(promptElement);
  promptOverlay.addEventListener("click", togglePrompt);
  promptOverlay.style.opacity = isPromptVisible ? 1 : 0;
  container.appendChild(promptOverlay);
}

function renderGrid() {
  console.log("Rendering files");
  const grid = document.getElementById("mainGrid");
  grid.innerHTML = "";

  if (generations.length === 0) {
    grid.innerHTML = `
      <div class="flex flex-col items-center gap-4">
        <div class="animate-spin text-gray-500"><svg xmlns="http://www.w3.org/2000/svg" class="lucide lucide-loader-circle stroke-gray-500" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M21 12a9 9 0 1 1-6.219-8.56"/>
        </svg></div>
        <div class="text-gray-500">Generating designs...</div>
      </div>
    `;
    grid.className = "col-span-3 flex flex-col items-center justify-center py-48";
    return;
  } else {
    grid.className = "col-span-3 grid grid-cols-3 gap-4 items-start";
  }

  generations.forEach((generation, index) => {
    const item = document.createElement("div");

    const content = generation.content;

    const previewDiv = document.createElement("div");
    previewDiv.className =
      "main-preview w-full h-full max-h-full flex flex-col items-center justify-center relative";
    previewDiv.id = `preview-${index}`;
    item.appendChild(previewDiv);

    item.className =
      item.className +
      " bg-white rounded-lg shadow-md transition-all relative overflow-hidden aspect-square hover:-translate-y-0.5 hover:shadow-lg";
    if (isFirstRender) {
      item.className =
        item.className + " opacity-0 translate-y-4 scale-80 duration-500 filter blur-md";
    }
    grid.appendChild(item);

    render(previewDiv, content);
    renderPrompt(generation.prompt, previewDiv);
    renderTags(generation.tags, previewDiv);

    // Animate in with a delay based on index
    if (isFirstRender) {
      setTimeout(() => {
        item.classList.remove("opacity-0", "translate-y-4", "scale-80", "filter", "blur-md");
        item.classList.add("opacity-100", "translate-y-0", "scale-100");
      }, index * 100);
    }
  });
}

async function updateDesignSpace(dimension, value, status) {
  const axis = designSpace.axes.find((axis) => axis.name === dimension);
  if (axis) {
    axis.value = value;
    axis.status = status;
  }

  renderDesignSpace();
}

let icons = {};
async function fetchDesignSpaceIcons() {
  const iconUrls = {
    exploring: "https://unpkg.com/lucide-static@latest/icons/telescope.svg",
    unconstrained: "https://unpkg.com/lucide-static@latest/icons/dices.svg",
    constrained: "https://unpkg.com/lucide-static@latest/icons/lock.svg",
    new: "https://unpkg.com/lucide-static@latest/icons/plus.svg",
    delete: "https://unpkg.com/lucide-static@latest/icons/trash-2.svg",
    loading: "https://unpkg.com/lucide-static@0.511.0/icons/loader-circle.svg",
  };

  await Promise.all(
    Object.entries(iconUrls).map(async ([key, url]) => {
      const response = await fetch(url);
      icons[key] = await response.text();
    })
  );
}
fetchDesignSpaceIcons();

function createDesignAxisControls(axis, status) {
  const container = document.createElement("div");
  container.className =
    "absolute right-0 top-0 w-24 h-full flex gap-1 justify-end items-center p-2 hover:w-fit hover:min-w-24 transition-all z-10 group";
  const exploreButton = document.createElement("button");
  const unconstrainedButton = document.createElement("button");
  const constrainedButton = document.createElement("button");
  const deleteButton = document.createElement("button");
  const baseButtonClassName =
    "bg-transparent rounded-md group-hover:opacity-100 group-hover:w-8 w-0 group-hover:h-8 h-0 opacity-0 top-0 transition-all flex items-center justify-center";
  exploreButton.className = baseButtonClassName + " hover:bg-green-500/10 text-green-500";
  unconstrainedButton.className = baseButtonClassName + " hover:bg-purple-500/10 text-purple-500";
  constrainedButton.className = baseButtonClassName + " hover:bg-blue-500/10 text-blue-500";
  deleteButton.className = baseButtonClassName + " hover:bg-red-500/10 text-red-500";

  exploreButton.innerHTML = icons["exploring"];
  unconstrainedButton.innerHTML = icons["unconstrained"];
  constrainedButton.innerHTML = icons["constrained"];
  deleteButton.innerHTML = icons["delete"];

  if (status === "exploring") {
    exploreButton.classList.remove("bg-transparent", "hover:bg-green-500/10");
    exploreButton.classList.add("bg-green-500/30", "hover:bg-green-500/50");
  } else if (status === "unconstrained") {
    unconstrainedButton.classList.remove("bg-transparent", "hover:bg-purple-500/10");
    unconstrainedButton.classList.add("bg-purple-500/30", "hover:bg-purple-500/50");
  } else if (status === "constrained") {
    constrainedButton.classList.remove("bg-transparent", "hover:bg-blue-500/10");
    constrainedButton.classList.add("bg-blue-500/30", "hover:bg-blue-500/50");
  }

  exploreButton.addEventListener("click", async () => {
    designSpace.axes.forEach(axis => {
      if (axis.status === "exploring") {
        axis.status = "unconstrained";
      }
    });
    updateDesignSpace(axis.name, axis.value, "exploring");
  });

  unconstrainedButton.addEventListener("click", async () => {
    updateDesignSpace(axis.name, axis.value, "unconstrained");
  });

  constrainedButton.addEventListener("click", async () => {
    updateDesignSpace(axis.name, axis.value, "constrained");
  });

  deleteButton.addEventListener("click", async () => {
    designSpace.axes = designSpace.axes.filter((a) => axis.name !== a.name);
    renderDesignSpace();
  });

  container.appendChild(deleteButton);
  container.appendChild(constrainedButton);
  container.appendChild(unconstrainedButton);
  container.appendChild(exploreButton);
  return container;
}

function createNewDesignAxis() {
  const wrapper = document.createElement("div");
  wrapper.className = "relative";

  const newAxisTriggerButton = document.createElement("button");
  newAxisTriggerButton.className =
    "bg-transparent rounded-md w-8 h-8 opacity-100 transition-all duration-300 flex items-center justify-center z-10 absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 rotate-180";
  newAxisTriggerButton.innerHTML = icons["new"];
  wrapper.appendChild(newAxisTriggerButton);

  const container = document.createElement("div");
  container.className = "w-0 h-9 opacity-0 transition-all duration-300";
  wrapper.appendChild(container);

  const label = document.createElement("label");
  label.className =
    "text-xs text-gray-500 absolute top-2 left-2 flex items-start justify-center gap-1";
  const itemIcon = document.createElement("div");

  itemIcon.className = `text-gray-500 scale-50 -translate-y-0.5 -translate-x-0.5 w-4 h-4`;
  label.appendChild(itemIcon);
  const itemLabel = document.createElement("span");
  itemLabel.innerHTML = "add new axis";
  label.appendChild(itemLabel);
  container.appendChild(label);

  const item = document.createElement("input");
  item.className =
    "w-full pt-6 pb-2 px-2 bg-gray-200 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-gray-400";
  container.appendChild(item);

  wrapper.addEventListener("mouseenter", (event) => {
    event.stopPropagation();
    newAxisTriggerButton.classList.remove(
      "w-8",
      "opacity-100",
      "top-1/2",
      "left-1/2",
      "-translate-x-1/2",
      "-translate-y-1/2",
      "rotate-180"
    );
    newAxisTriggerButton.classList.add("top-1", "left-1", "scale-50", "-translate-y-1", "rotate-0");
    container.classList.remove("w-0", "opacity-0");
    container.classList.add("w-full", "opacity-100");
    setTimeout(() => item.focus(), 50);
  });

  wrapper.addEventListener("mouseleave", (event) => {
    newAxisTriggerButton.classList.remove(
      "top-1",
      "left-1",
      "scale-50",
      "-translate-y-1",
      "rotate-0"
    );
    newAxisTriggerButton.classList.add(
      "w-8",
      "opacity-100",
      "top-1/2",
      "left-1/2",
      "-translate-x-1/2",
      "-translate-y-1/2",
      "rotate-180"
    );
    container.classList.remove("w-full", "opacity-100");
    container.classList.add("w-0", "opacity-0");
  });

  const handleSubmit = async () => {
    if (item.value.trim()) {
      designSpace.axes.push({ name: item.value.trim(), status: "exploring", value: "" });
      renderDesignSpace();

      item.value = "";
      container.classList.remove("w-64", "opacity-100");
      container.classList.add("w-0", "opacity-0");
    }
  };

  item.addEventListener("change", handleSubmit);

  return wrapper;
}

async function renderDesignSpace() {
  const designSpaceContainer = document.getElementById("designSpaceList");
  designSpaceContainer.innerHTML = "";
  designSpaceContainer.className = "p-0 space-y-3 mt-4";

  console.log("designSpaceList", designSpace);

  if (designSpace === null) {
    designSpaceContainer.innerHTML = `
      <div class="flex flex-col items-center gap-4">
        <div class="animate-spin"><svg xmlns="http://www.w3.org/2000/svg" class="lucide lucide-loader-circle" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M21 12a9 9 0 1 1-6.219-8.56"/>
        </svg></div>
        <div class="text-gray-500">Generating designs...</div>
      </div>
    `;
    designSpaceContainer.className =
      "flex flex-col items-center justify-center py-60 text-gray-500";
    return;
  } else {
    designSpaceContainer.className = "p-0 space-y-3 mt-4";
  }

  if (isFirstRender) {
    await fetchDesignSpaceIcons();
  }

  const grouped = {
    exploring: [],
    constrained: [],
    unconstrained: [],
  };

  designSpace.axes.forEach((axis) => {
    grouped[axis.status].push(axis);
  });

  let index = 0;

  // Render each status group
  for (const status of ["constrained", "exploring", "unconstrained"]) {
    if (grouped[status].length > 0) {
      // Add section header
      const header = document.createElement("div");
      header.className =
        "text-lg font-medium tracking-tight text-gray-700 mb-2 mt-4 first:mt-0 opacity-0 translate-y-4 scale-80 duration-500 filter blur-md";
      header.textContent =
        status === "constrained"
          ? "Filtered"
          : status === "exploring"
          ? "Exploring"
          : "Suggestions for Exploration";

      setTimeout(() => {
        header.classList.remove("opacity-0", "translate-y-4", "scale-80", "filter", "blur-md");
        header.classList.add("opacity-100", "translate-y-0", "scale-100");
      }, index * 100);
      designSpaceContainer.appendChild(header);

      for (const axis of grouped[status]) {
        const container = document.createElement("div");
        container.id = "design-space-container-" + axis.name;
        container.className = "relative rounded-lg overflow-hidden";
        const item = document.createElement("input");
        const label = document.createElement("label");
        label.className =
          "text-xs text-gray-500 absolute top-2 left-2 flex items-start justify-center gap-1";
        const itemIcon = document.createElement("div");
        itemIcon.innerHTML = icons[axis.status];
        const currentColor =
          axis.status === "exploring"
            ? "green-500"
            : axis.status === "unconstrained"
            ? "purple-500"
            : "blue-500";
        itemIcon.className = `text-${currentColor} scale-50 -translate-y-0.5 -translate-x-0.5 w-4 h-4`;
        label.appendChild(itemIcon);
        const itemLabel = document.createElement("span");
        itemLabel.innerHTML = axis.name;
        label.appendChild(itemLabel);
        item.id = "design-space-" + axis.name;
        item.className =
          "transition-all relative overflow-hidden hover:bg-gray-300 bg-gray-200 p-2 rounded-lg shadow-sm pt-6 w-full focus:outline-none focus:ring-2 focus:ring-gray-400";
        if (axis.status === "unconstrained") {
          item.placeholder = axis.value;
          item.value = "";
        } else if (axis.status === "exploring") {
          item.value = "";
          item.placeholder = "exploring";
        } else if (axis.status === "constrained") {
          item.value = axis.value;
        }

        if (isFirstRender) {
          container.className =
            container.className + " opacity-0 translate-y-4 scale-80 duration-500 filter blur-md";
          setTimeout(() => {
            container.classList.remove(
              "opacity-0",
              "translate-y-4",
              "scale-80",
              "filter",
              "blur-md"
            );
            container.classList.add("opacity-100", "translate-y-0", "scale-100");
          }, index * 100);
        }

        container.appendChild(item);
        container.appendChild(label);
        item.addEventListener("change", async (event) => {
          axis.value = event.target.value;
          axis.status = "constrained";
          await updateDesignSpace(axis.name, axis.value, axis.status);
          renderDesignSpace();
          console.log("designSpace updated", designSpace);
        });
        container.appendChild(createDesignAxisControls(axis, status));
        designSpaceContainer.appendChild(container);
        index++;
      }
    }
  }

  designSpaceContainer.appendChild(createNewDesignAxis());
}

async function regenerate() {
  const exploringAxes = designSpace.axes.filter(axis => axis.status === "exploring");
  if (exploringAxes.length === 0) {
    showStatus("Please select an axis to explore", "error");
    return;
  }

  
  generations = [];
  renderGrid();


  try {
    const response = await fetch(`/api/generation/${sessionId}/regenerate`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        design_space: designSpace?.model_dump?.() || designSpace,
      }),
    });

    if (!response.ok) {
      if (response.status === 422) {
        console.error("Invalid design space:", designSpace);
        throw new Error("Invalid design space format - please check the console for details");
      }
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    console.log("regenerated", data);
    isFirstRender = true;
    generations = data.generations;
    if (data.design_space !== designSpace) {
      designSpace = data.design_space;
      renderDesignSpace();
    }
    renderGrid();
  } catch (error) {
    console.error("Error:", error);
    showStatus(error.message || "Failed to regenerate designs", "error");
  }

  setTimeout(() => {
    isFirstRender = false;
  }, 1000);
}

// Initialize
document.addEventListener("DOMContentLoaded", async () => {
  isFirstRender = true;

  // Get session ID from URL
  sessionId = window.location.pathname.split("/").pop();
  concept = document.getElementById("concept").textContent;

  console.log("sessionId", sessionId);
  console.log("concept", concept);

  renderDesignSpace();
  renderGrid();

  try {
    const response = await fetch(`/api/generation/${sessionId}`, {
      method: "GET",
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    designSpace = data.design_space;
    generations = data.generations;
    console.log("generations", generations);
    renderGrid();
    renderDesignSpace();
  } catch (error) {
    console.error("Error:", error);
    showStatus("Failed to load generation", "error");
  }

  const regenerateButton = document.getElementById("regenerateButton");
  regenerateButton.addEventListener("click", regenerate);

  setTimeout(() => {
    isFirstRender = false;
  }, 1000);
});
