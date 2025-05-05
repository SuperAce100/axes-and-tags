function render(id, content) {
  const container = document.getElementById(id);
  container.style.position = 'relative';
  
  // Create image element
  const imgElement = document.createElement('img');
  imgElement.src = `data:image/png;base64,${content.data}`;
  imgElement.style.width = '100%';
  imgElement.style.height = '100%';
  imgElement.style.objectFit = 'contain';
  
  // Create prompt overlay with gradient
  const promptOverlay = document.createElement('div');
  promptOverlay.style.position = 'absolute';
  promptOverlay.style.top = '0';
  promptOverlay.style.left = '0';
  promptOverlay.style.width = '100%';
  promptOverlay.style.height = '100%';
  promptOverlay.style.padding = '12px';
  promptOverlay.style.background = 'linear-gradient(to bottom, rgba(0, 0, 0, 0.85) 0%, rgba(0, 0, 0, 0.6) 70%, transparent 100%)';
  promptOverlay.style.boxSizing = 'border-box';
  promptOverlay.style.display = 'flex';
  promptOverlay.style.flexDirection = 'column';
  promptOverlay.style.justifyContent = 'space-between';
  
  // Create prompt text element
  const promptElement = document.createElement('div');
  promptElement.textContent = content.prompt;
  promptElement.style.color = 'white';
  promptElement.style.fontSize = '12px';
  promptElement.style.fontFamily = 'Inter, sans-serif';
  promptElement.style.maxWidth = '100%';
  promptElement.style.overflow = 'hidden';
  promptElement.style.lineHeight = '1.2em';
  promptElement.style.maxHeight = '2.4em';
  promptElement.style.display = '-webkit-box';
  promptElement.style.webkitLineClamp = '2';
  promptElement.style.webkitBoxOrient = 'vertical';
  
  // Create tags container
  const tagsContainer = document.createElement('div');
  tagsContainer.style.display = 'flex';
  tagsContainer.style.gap = '4px';
  tagsContainer.style.flexWrap = 'wrap';
  tagsContainer.style.marginTop = 'auto';

  // Add each tag
  if (content.tags && Array.isArray(content.tags)) {
    content.tags.forEach(tag => {
      const tagElement = document.createElement('span');
      tagElement.textContent = tag;
      tagElement.style.background = 'rgba(255, 255, 255, 0.2)';
      tagElement.style.padding = '2px 6px';
      tagElement.style.borderRadius = 'calc(infinity * 1px)';
      tagElement.style.fontSize = '10px';
      tagElement.style.fontFamily = 'Inter, sans-serif';
      tagElement.style.color = 'white';
      tagElement.style.transition = 'var(--transition)';
      tagElement.addEventListener('mouseenter', () => {
        tagElement.style.background = 'rgba(255, 255, 255, 0.3)';
        tagElement.style.transform = 'scale(1.05)';
      });
      tagElement.addEventListener('mouseleave', () => {
        tagElement.style.background = 'rgba(255, 255, 255, 0.2)';
        tagElement.style.transform = 'scale(1)';
      });
      tagsContainer.appendChild(tagElement);
    });
  }
  // Append elements
  promptOverlay.appendChild(promptElement);
  promptOverlay.appendChild(tagsContainer);
  container.appendChild(imgElement);
  container.appendChild(promptOverlay);
  
  return imgElement;
}
