function render(id, content, fileName) {
  const container = document.getElementById(id);
  container.classList.add('relative', 'group', 'parent');

  const uiElement = document.createElement('div');
  uiElement.innerHTML = content.data;
  uiElement.className = 'w-full h-full transition-all hover:z-30 z-0 overflow-y-auto';
  
  // scale down if content is too large
  uiElement.style.zoom = "0.3";



  // prompt overlay with gradient
  const promptOverlay = document.createElement('div');
  promptOverlay.className = 'absolute top-0 left-0 w-full p-3 bg-gradient-to-b from-black/85 via-black/60 to-transparent z-10 transition-all';
  
  const promptElement = document.createElement('div');
  promptElement.textContent = content.prompt;
  promptElement.className = 'text-white text-xs max-w-full overflow-hidden leading-tight font-sans max-h-[2.5em] hover:max-h-[200px] transition-all mask-b-from-0% mask-b-to-20%';
  
  promptOverlay.appendChild(promptElement);
  container.appendChild(uiElement);
  container.appendChild(promptOverlay);
  
  return uiElement;
}

function renderTags(fileData, container) {
    // Create tags container
    const tagsContainer = document.createElement('div');
    tagsContainer.className = 'flex gap-1 flex-wrap mt-1';

    // Add each tag
    if (fileData.content.tags && Array.isArray(fileData.content.tags)) {
        fileData.content.tags.forEach((tag, index) => {
            const tagElement = document.createElement('span');
            tagElement.textContent = tag;
            tagElement.className = `tag bg-white/20 px-1.5 py-0.5 rounded-full text-[10px] text-white hover:bg-white/30 hover:scale-105 cursor-pointer font-sans active:scale-95 transition-all z-[${10+index}]`;

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
    tagOverlay.className = 'bg-gradient-to-t from-black/85 via-black/60 to-transparent p-3 absolute bottom-0 left-0 w-full z-10';
    tagOverlay.id = "tag-overlay";
    // Append elements
    tagOverlay.appendChild(tagsContainer);
    container.appendChild(tagOverlay);
}
function renderExample(container, content, feedback) {
  const uiElement = document.createElement('div');
  uiElement.innerHTML = content.data;
  uiElement.className = 'w-full h-full';
  container.appendChild(uiElement);
  
  uiElement.style.zoom = "0.1";

  const feedbackContainer = document.createElement('div');
  feedbackContainer.className = 'absolute top-0 left-0 w-full p-2 z-10 bg-gradient-to-b from-black/85 via-black/60 to-transparent';
  
  const feedbackElement = document.createElement('div');
  feedbackElement.textContent = feedback;
  feedbackElement.className = 'text-white font-tight';
  feedbackContainer.appendChild(feedbackElement);
  
  container.appendChild(feedbackContainer);
}