let isPromptVisible = false;

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
  const textElement = document.createElement('div');
  textElement.textContent = content.text;
  textElement.className = 'p-4 text-sm w-full overflow-y-auto aspect-square';
  
  container.appendChild(textElement);
  
  return textElement;
}

function renderTags(fileData, container) {
    // Create tags container
    const tagsContainer = document.createElement('div');
    tagsContainer.className = 'flex gap-1 flex-wrap mt-1';

    // Add each tag
    if (fileData.content.tags && Array.isArray(fileData.content.tags)) {
        fileData.content.tags.forEach(([dimension, tag]) => {
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

                tagElement.className = tagElement.className.replace('bg-white/20', 'bg-green-300/30')
                    .replace('text-white', 'text-green-500')
                    .replace('hover:bg-white/30', 'hover:bg-green-300/50');

                updateDesignSpace(dimension, tag);
                renderTags(fileData, container);
                
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
  const textElement = document.createElement('div');
  textElement.textContent = content.text;
  textElement.className = 'p-2 text-xs max-w-full overflow-y-auto';
  container.appendChild(textElement);

  const feedbackContainer = document.createElement('div');
  feedbackContainer.className = 'absolute top-0 left-0 w-full p-2 z-10 bg-gradient-to-b from-black/85 via-black/60 to-transparent';
  
  const feedbackElement = document.createElement('div');
  feedbackElement.textContent = feedback;
  feedbackElement.className = 'text-white font-tight';
  feedbackContainer.appendChild(feedbackElement);
  
  container.appendChild(feedbackContainer);
}