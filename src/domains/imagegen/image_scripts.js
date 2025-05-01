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
  promptOverlay.style.bottom = '0';
  promptOverlay.style.left = '0';
  promptOverlay.style.width = '100%';
  promptOverlay.style.padding = '12px';
  promptOverlay.style.background = 'linear-gradient(to top, rgba(0, 0, 0, 0.85) 0%, rgba(0, 0, 0, 0.6) 70%, transparent 100%)';
  promptOverlay.style.boxSizing = 'border-box';
  
  // Create prompt text element
  const promptElement = document.createElement('div');
  promptElement.textContent = content.prompt;
  promptElement.style.color = 'white';
  promptElement.style.fontFamily = 'system-ui, -apple-system, sans-serif';
  promptElement.style.fontSize = '14px';
  promptElement.style.maxWidth = '100%';
  promptElement.style.overflow = 'hidden';
  promptElement.style.textOverflow = 'ellipsis';
  promptElement.style.whiteSpace = 'nowrap';
  promptElement.style.textShadow = '0 1px 2px rgba(0, 0, 0, 0.5)';
  
  // Create tooltip for full prompt on hover
  const tooltip = document.createElement('div');
  tooltip.textContent = content.prompt;
  tooltip.style.position = 'absolute';
  tooltip.style.top = 'calc(100% + 5px)';
  tooltip.style.left = '0';
  tooltip.style.backgroundColor = 'rgba(0, 0, 0, 0.9)';
  tooltip.style.color = 'white';
  tooltip.style.padding = '10px';
  tooltip.style.borderRadius = '4px';
  tooltip.style.maxWidth = '400px';
  tooltip.style.wordWrap = 'break-word';
  tooltip.style.whiteSpace = 'normal';
  tooltip.style.boxShadow = '0 2px 10px rgba(0, 0, 0, 0.3)';
  tooltip.style.zIndex = '1000';
  tooltip.style.opacity = '0';
  tooltip.style.visibility = 'hidden';
  tooltip.style.transition = 'opacity 0.2s, visibility 0.2s';
  tooltip.style.fontSize = '13px';
  tooltip.style.lineHeight = '1.4';
  
  // Only show tooltip if prompt is truncated
  promptOverlay.addEventListener('mouseenter', () => {
    tooltip.style.opacity = '1';
    tooltip.style.visibility = 'visible';
  });
  
  promptOverlay.addEventListener('mouseleave', () => {
    tooltip.style.opacity = '0';
    tooltip.style.visibility = 'hidden';
  });
  
  // Append elements
  promptOverlay.appendChild(promptElement);
  container.appendChild(imgElement);
  container.appendChild(promptOverlay);
  container.appendChild(tooltip);
  
  return imgElement;
}
