function render(id, content) {
    const item = document.getElementById(id);
    const container = document.createElement("div");
    container.className = "bg-grey/10 rounded-lg m-4 flex flex-col items-center justify-center flex-1 group min-h-0";
    container.innerHTML = content.svg;
    
    // Scale SVG to fit container
    const svg = container.querySelector('svg');
    if (svg) {
        svg.setAttribute('width', '100%');

        svg.setAttribute('height', '100%');
        // svg.setAttribute('preserveAspectRatio', 'xMidYMid meet');
        svg.classList.add('transition-transform', 'duration-200', 'group-hover:scale-110');

    }

    item.appendChild(container);
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
            tagElement.className = 'tag bg-gray-100 px-1.5 py-0.5 rounded-full text-[10px] text-gray-600 hover:bg-gray-200 hover:scale-105 cursor-pointer font-sans active:scale-95 transition-all';

            if (feedbackData[fileData.name]) {
                if (feedbackData[fileData.name].includes(tag)) {
                tagElement.className = tagElement.className.replace('bg-gray-100', 'bg-green-100')
                    .replace('text-gray-600', 'text-green-600')
                    .replace('hover:bg-gray-200', 'hover:bg-green-200');
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
    tagOverlay.className = 'bg-white/80 backdrop-blur-sm p-3 pt-0 w-full z-12';
    tagOverlay.id = "tag-overlay";
    // Append elements
    tagOverlay.appendChild(tagsContainer);
    container.appendChild(tagOverlay);
}


function renderExample(container, content, feedback) {
    const example = document.createElement('div');
    container.classList.add('flex', 'flex-col', 'items-center', 'justify-center');
    example.className = 'w-full flex-1 p-4';
    example.innerHTML = content.svg;

    const svg = example.querySelector('svg');
    if (svg) {
        svg.setAttribute('width', '100%');
        svg.setAttribute('height', '100%');
        svg.setAttribute('preserveAspectRatio', 'xMidYMid meet');
    }

    const titleOverlay = document.createElement('div');
    titleOverlay.className = 'p-4 pb-0 w-full text-left';
    
    const titleElement = document.createElement('div');
    titleElement.textContent = feedback;
    titleElement.className = 'font-tight';
    
    titleOverlay.appendChild(titleElement);
    container.appendChild(titleOverlay);
    container.appendChild(example);
}
