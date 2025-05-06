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
  
  promptOverlay.appendChild(promptElement);
  container.appendChild(imgElement);
  container.appendChild(promptOverlay);
  
  return imgElement;
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