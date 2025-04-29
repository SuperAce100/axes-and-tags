

// Fetch files from the server
async function fetchFiles() {
    try {
        const response = await fetch('/api/files');
        files = await response.json();
        render();
    } catch (error) {
        showStatus('Error loading files: ' + error.message, 'error');
    }
}

// Render SVGs in the grid
function render() {
    console.log("Rendering files");
    const grid = document.getElementById('mainGrid');
    grid.innerHTML = '';
    
    files.forEach((fileData, index) => {
        const item = document.createElement('div');
        item.className = 'main-item';
        item.id = `preview-${index}`;
        
        const fileName = fileData.name;
        const fileContent = fileData.content;
        
        // Add feedback badge if there's feedback
        const hasFeedback = feedbackData[fileName] && feedbackData[fileName].length > 0;

        if (selectedFile === fileName) {
            item.classList.add('selected');
        }
        
        item.innerHTML = `
            <div class="main-number">${index + 1}</div>
            ${hasFeedback ? `<div class="feedback-badge">${feedbackData[fileName].length}</div>` : ''}
            <div class="main-preview">
                ${fileContent}
            </div>
        `;
        
        item.addEventListener('click', () => {
            selectFile(fileName);
        });

        item.addEventListener('dblclick', () => {
            saveSelected();
        });
        
        grid.appendChild(item);
    });
}



// Load files when the page loads
document.addEventListener('DOMContentLoaded', () => {
    fetchFiles();
});

// Override the handleResize function for SVG-specific resizing
function handleResize() {
    console.log('SVG viewer resized');
    // Add any SVG-specific resize handling here if needed
}

