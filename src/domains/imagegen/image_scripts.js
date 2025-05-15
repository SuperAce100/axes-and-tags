let isPromptVisible = false;

function togglePrompt() {
  isPromptVisible = !isPromptVisible;
  const promptOverlays = document.querySelectorAll('.prompt-overlay');
  promptOverlays.forEach(overlay => {
    overlay.style.opacity = isPromptVisible ? 1 : 0;
  });
}

// cmd + i
document.addEventListener('keydown', (event) => {
  if (event.metaKey && event.key === 'i') {
    togglePrompt();
  }
});

let isTagOverlayVisible = false;

function toggleTagOverlay() {
  isTagOverlayVisible = !isTagOverlayVisible;
  const tagOverlays = document.querySelectorAll('.tag-overlay');
  tagOverlays.forEach(overlay => {
    overlay.style.opacity = isTagOverlayVisible ? 1 : 0;
  });
}

// cmd + u
document.addEventListener('keydown', (event) => {
  if (event.metaKey && event.key === 'u') {
    toggleTagOverlay();
  }
});

function render(id, content, fileName) {
  const container = document.getElementById(id);
  container.className = 'relative';
  
  // Create image element
  const imgElement = document.createElement('img');
  imgElement.src = `data:image/png;base64,${content.data}`;
  imgElement.className = 'w-full h-full object-contain';
  
  // Create prompt overlay with gradient
  const promptOverlay = document.createElement('div');
  promptOverlay.className = 'absolute top-0 left-0 w-full p-3 bg-gradient-to-b from-black/85 via-black/60 to-transparent prompt-overlay transition-all';
  
  // Create prompt text element
  const promptElement = document.createElement('div');
  promptElement.textContent = content.prompt;
  promptElement.className = 'text-white text-xs max-w-full overflow-hidden leading-tight font-sans max-h-[2.5em] hover:max-h-[200px] transition-all mask-b-from-0% mask-b-to-20%';
  
  promptOverlay.appendChild(promptElement);
  promptOverlay.addEventListener('click', togglePrompt);
  promptOverlay.style.opacity = isPromptVisible ? 1 : 0;
  container.appendChild(imgElement);
  container.appendChild(promptOverlay);
  
  return imgElement;
}

function renderTags(fileData, container) {
    // Create tags container
    const tagsContainer = document.createElement('div');
    tagsContainer.className = 'flex gap-1 flex-wrap mt-1';

    // Add each tag
    if (fileData.content.tags && Array.isArray(fileData.content.tags)) {
        fileData.content.tags.forEach(tag => {
            const tagElement = document.createElement('span');
            tagElement.textContent = tag;
            tagElement.className = 'tag bg-white/20 px-1.5 py-0.5 rounded-full text-[10px] text-white hover:bg-white/30 hover:scale-105 cursor-pointer font-sans active:scale-95 transition-all';

            if (feedbackData[fileData.name]) {
                if (feedbackData[fileData.name].includes(tag)) {
                tagElement.className = tagElement.className.replace('bg-white/20', 'bg-green-300/30')
                    .replace('text-white', 'text-green-500')
                    .replace('hover:bg-white/30', 'hover:bg-green-300/50');
                }
            }
            
            tagElement.addEventListener('click', async () => {
                if (fileData.name) {
                    await selectFile(fileData.name);
                    saveFeedback(tag);
                }
            });
            tagsContainer.appendChild(tagElement);
        });
    }

    const tagOverlay = document.createElement('div');
    tagOverlay.className = 'bg-gradient-to-t from-black/85 via-black/60 to-transparent p-3 absolute bottom-0 left-0 w-full z-12 tag-overlay transition-all';
    tagOverlay.id = "tag-overlay";
    // Append elements
    tagOverlay.appendChild(tagsContainer);
    container.appendChild(tagOverlay);
}

function renderExample(container, content, feedback) {
  const imgElement = document.createElement('img');
  imgElement.src = `data:image/png;base64,${content.data}`;
  imgElement.className = 'w-full h-full object-contain';
  container.appendChild(imgElement);

  const feedbackContainer = document.createElement('div');
  feedbackContainer.className = 'absolute top-0 left-0 w-full p-2 z-10 bg-gradient-to-b from-black/85 via-black/60 to-transparent';
  
  const feedbackElement = document.createElement('div');
  feedbackElement.textContent = feedback;
  feedbackElement.className = 'text-white font-tight';
  feedbackContainer.appendChild(feedbackElement);
  
  container.appendChild(feedbackContainer);
}