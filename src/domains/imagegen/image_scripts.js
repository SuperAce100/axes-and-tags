function render(id, content, fileName) {
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
  promptElement.className = 'text-white text-xs max-w-full overflow-hidden leading-tight font-sans max-h-[2.5em] hover:max-h-[200px] transition-all mask-b-from-0% mask-b-to-20%';
  
  // Create tags container
  const tagsContainer = document.createElement('div');
  tagsContainer.className = 'flex gap-1 flex-wrap mt-1';

  // Add each tag
  if (content.tags && Array.isArray(content.tags)) {
    content.tags.forEach(tag => {
      const tagElement = document.createElement('span');
      tagElement.textContent = tag;
      tagElement.className = 'bg-white/20 px-1.5 py-0.5 rounded-full text-[10px] text-white hover:bg-white/30 hover:scale-105 cursor-pointer font-sans active:scale-95 transition-all';

      if (feedbackData[fileName]) {
        if (feedbackData[fileName].includes(tag)) {
          tagElement.classList.remove('bg-white/20');
          tagElement.classList.add('bg-green-500/20');
          tagElement.classList.remove('text-white');
          tagElement.classList.add('text-green-500');
          tagElement.classList.add('hover:bg-green-500/30');
          tagElement.classList.remove('hover:bg-white/30');
        }
      }
      
      tagElement.addEventListener('click', async () => {
        const feedbackInput = document.getElementById('feedbackInput');
        if (feedbackInput) {
            if (fileName) {
              await selectFile(fileName);
              feedbackInput.value = `${tag}`;
              saveFeedback();
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
