// Global variables
let files = [];
let selectedFile = null;
let selectedIndex = -1;
let feedbackData = {};
let isClosing = false;
let usedExamples = {};
let isFirstRender = true;
// Select a file
async function selectFile(file) {
    try {
        const response = await fetch('/api/select', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ file })
        });
        
        if (response.ok) {
            selectedFile = file;
            
            selectedIndex = files.findIndex(f => f.name === file);
            await loadFeedback(file);
            renderGrid();
        } else {
            showStatus('Error selecting file', 'error');
        }
    } catch (error) {
        showStatus('Error selecting file: ' + error.message, 'error');
    }
}

// Load feedback for a specific file
async function loadFeedback(file) {
    try {
        const response = await fetch(`/api/feedback/${file}`);
        const data = await response.json();
        
        feedbackData[file] = data.feedback;
    } catch (error) {
        console.error('Error loading feedback:', error);
    }
}

async function getFeedbackData() {
    const response = await fetch('/api/all-feedback');
    const data = await response.json();
    feedbackData = data;
    console.log("feedbackData", feedbackData);
}


// Save feedback for selected file
async function saveFeedback(feedback) {
    // if (!feedback) {
    //     feedback = document.getElementById('feedbackInput').value.trim();
    // }

    if (!feedback) {
        showStatus('Please enter feedback', 'error');
        return;
    }
    
    if (!selectedFile) {
        showStatus('Please select an object first', 'error');
        return;
    }
    
    try {
        const response = await fetch('/api/feedback', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ file: selectedFile, feedback })
        });

        console.log({file: selectedFile, feedback});
        
        if (response.ok) {
            showStatus(`Feedback saved for ${selectedFile}`, 'success');
            // document.getElementById('feedbackInput').value = '';
            
            // Reload feedback for the selected file
            await loadFeedback(selectedFile);
            
            renderGrid();
        } else {
            showStatus('Error saving feedback', 'error');
        }
    } catch (error) {
        showStatus('Error saving feedback: ' + error.message, 'error');
    }
}

// Save selected file
async function saveSelected() {
    if (!selectedFile) {
        showStatus('No object selected', 'error');
        return;
    }
    
    try {
        const response = await fetch('/api/save-selected', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({})
        });
        
        if (response.ok) {
            const data = await response.json();
            showStatus(`Object ${selectedFile} saved to ${data.path}`, 'success');
        } else {
            showStatus('Error saving object', 'error');
        }
    } catch (error) {
        showStatus('Error saving object: ' + error.message, 'error');
    }
}

// Close the viewer
async function closeViewer() {
    if (isClosing) return;
    
    isClosing = true;
    try {
        const response = await fetch('/api/close', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        if (response.ok) {
            window.close();
        } else {
            showStatus('Error closing viewer', 'error');
            isClosing = false;
        }
    } catch (error) {
        showStatus('Error closing viewer: ' + error.message, 'error');
        isClosing = false;
    }
}

// Show status message
function showStatus(message, type = 'info') {
    const status = document.getElementById('status');
    status.textContent = message;
    status.className = `status ${type}`;
    status.style.display = 'block';
    
    setTimeout(() => {
        status.style.display = 'none';
    }, 3000);
}

async function fetchFiles() {
    try {
        const response = await fetch('/api/files');
        files = await response.json();
        // renderGrid();
    } catch (error) {
        showStatus('Error loading files: ' + error.message, 'error');
    }
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
            tagElement.className = 'bg-white/20 px-1.5 py-0.5 rounded-full text-[10px] text-white hover:bg-white/30 hover:scale-105 cursor-pointer font-sans active:scale-95 transition-all';

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
    tagOverlay.className = 'bg-gradient-to-t from-black/85 via-black/60 to-transparent p-3 absolute bottom-0 left-0 w-full z-12';
    // Append elements
    tagOverlay.appendChild(tagsContainer);
    container.appendChild(tagOverlay);
}

// Render files in the grid
function renderGrid() {
    console.log("Rendering files");
    const grid = document.getElementById('mainGrid');
    grid.innerHTML = '';
    
    files.forEach((fileData, index) => {
        const item = document.createElement('div');
        
        const fileName = fileData.name;
        const fileContent = fileData.content;
        
        item.innerHTML = `
        <div class="main-preview" id="preview-${index}">
        </div>
        `;
        
        item.className = item.className + ' bg-white rounded-lg shadow-md transition-all relative overflow-hidden aspect-square hover:-translate-y-0.5 hover:shadow-lg';
        if (isFirstRender) {
            item.className = item.className + ' opacity-0 translate-y-4 scale-80 duration-500 filter blur-md';
        }
        grid.appendChild(item);

        render("preview-" + index, fileContent, fileName);
        renderTags(fileData, item);

        // Animate in with a delay based on index
        if (isFirstRender) {
            setTimeout(() => {
                item.classList.remove('opacity-0', 'translate-y-4', 'scale-80', 'filter', 'blur-md');
                item.classList.add('opacity-100', 'translate-y-0', 'scale-100');
            }, index * 100);
        }

        item.addEventListener('click', () => {
            selectFile(fileName);
        });

        item.addEventListener('dblclick', () => {
            saveSelected();
        });
        
    });
}

async function fetchUsedExamples() {
    const response = await fetch('/api/used-examples');
    const data = await response.json();
    usedExamples = data.used_examples;
    console.log("used examples", data);
}

function renderUsedExamples() {
    usedExamplesContainer = document.getElementById('usedExamples');

    console.log("usedExamples", usedExamples);

    if(Object.keys(usedExamples).length === 0) {
        console.log("No used examples");
        usedExamplesContainer.classList.add('hidden');
        return;
    } else {
        usedExamplesContainer.classList.remove('hidden');
    }

    const usedExamplesList = document.getElementById('usedExamplesList');
    usedExamplesList.innerHTML = '';

    for (const [file, feedbacks] of Object.entries(usedExamples)) {
        const fileContent = feedbacks.content;
        const newFeedbacks = feedbacks.feedback;
        newFeedbacks.forEach((feedback, index) => {
            const item = document.createElement('div');
            item.id = "used-example-" + file;
            item.className = 'aspect-square bg-white rounded-lg shadow-md transition-all relative overflow-hidden hover:-translate-y-0.5';
            if (isFirstRender) {
                item.className = item.className + ' opacity-0 translate-y-4 scale-80 duration-500 filter blur-md';
            }
            renderExample(item, fileContent, feedback);
            usedExamplesList.appendChild(item);

            if (isFirstRender) {
                setTimeout(() => {
                    item.classList.remove('opacity-0', 'translate-y-4', 'scale-80', 'filter', 'blur-md');
                    item.classList.add('opacity-100', 'translate-y-0', 'scale-100');
                }, index * 100);
            }
        });
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', async () => {
    isFirstRender = true;

    document.addEventListener('keydown', (event) => {
        if (event.key === 'Escape') {
            closeViewer();
        }
    });
    
    await fetchFiles();
    console.log(files);
    await getFeedbackData();
    console.log(feedbackData);
    await fetchUsedExamples();

    renderUsedExamples();
    
    renderGrid();

    setTimeout(() => {
        isFirstRender = false;
    }, 1000);
}); 