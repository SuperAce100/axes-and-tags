function render(id, content) {
  const container = document.getElementById(id);
  container.className = 'relative';
  
  // Create image element
  const imgElement = document.createElement('img');
  imgElement.src = `data:image/png;base64,${content.data}`;
  imgElement.className = 'w-full h-full object-contain';
  
  // Create prompt overlay with gradient
  const promptOverlay = document.createElement('div');
  promptOverlay.className = 'absolute top-0 left-0 w-full p-3 bg-gradient-to-b from-black/85 via-black/60 to-transparent';
  
  // Create prompt text element
  const promptElement = document.createElement('div');
  promptElement.textContent = content.prompt;
  promptElement.className = 'text-white text-xs max-w-full overflow-hidden leading-tight max-h-[3.6em]';
  
  // Create tags container
  const tagsContainer = document.createElement('div');
  tagsContainer.className = 'flex gap-1 flex-wrap mt-1';

  // Add each tag
  if (content.tags && Array.isArray(content.tags)) {
    content.tags.forEach(tag => {
      const tagElement = document.createElement('span');
      tagElement.textContent = tag;
      tagElement.className = 'bg-white/20 px-1.5 py-0.5 rounded-full text-[10px] text-white transition-all hover:bg-white/30 hover:scale-105 cursor-pointer';
      
      tagElement.addEventListener('click', async () => {
        const feedbackInput = document.getElementById('feedbackInput');
        if (feedbackInput) {
          // Get the file name from the container's parent
          const fileContainer = container.closest('.main-item');
          if (fileContainer) {
            const fileNumber = fileContainer.querySelector('.main-number').textContent;
            const fileIndex = parseInt(fileNumber) - 1;
            const file = files[fileIndex];
            
            if (file) {
              await selectFile(file.name);
              feedbackInput.value = `${tag}`;
              feedbackInput.focus();
              saveFeedback();
            }
          }
        }
      });
      tagsContainer.appendChild(tagElement);
    });
  }

  const tagOverlay = document.createElement('div');
  tagOverlay.className = 'bg-gradient-to-t from-black/85 via-black/60 to-transparent p-3 absolute bottom-0 left-0 w-full';
  // Append elements
  promptOverlay.appendChild(promptElement);
  tagOverlay.appendChild(tagsContainer);
  container.appendChild(imgElement);
  container.appendChild(promptOverlay);
  container.appendChild(tagOverlay);
  
  return imgElement;
}
