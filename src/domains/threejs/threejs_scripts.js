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
