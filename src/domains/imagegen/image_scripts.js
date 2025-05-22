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

function render(id, content, prompt) {
  const container = document.getElementById(id);
  container.className = "relative";

  // Create image element
  const imgElement = document.createElement("img");
  imgElement.src = `data:image/png;base64,${content}`;
  imgElement.className = "w-full h-full object-contain";

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
  container.appendChild(imgElement);
  container.appendChild(promptOverlay);

  return imgElement;
}

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

function renderExample(container, content, feedback) {
  const imgElement = document.createElement("img");
  imgElement.src = `data:image/png;base64,${content.data}`;
  imgElement.className = "w-full h-full object-contain";
  container.appendChild(imgElement);

  const feedbackContainer = document.createElement("div");
  feedbackContainer.className =
    "absolute top-0 left-0 w-full p-2 z-10 bg-gradient-to-b from-black/85 via-black/60 to-transparent";

  const feedbackElement = document.createElement("div");
  feedbackElement.textContent = feedback;
  feedbackElement.className = "text-white font-tight";
  feedbackContainer.appendChild(feedbackElement);

  container.appendChild(feedbackContainer);
}
