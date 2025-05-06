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
    files.forEach(async (file) => {
        await loadFeedback(file.name);
    });
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

function navigatePrevious() {
    if (files.length === 0) return;
    
    let newIndex = selectedIndex - 1;
    if (newIndex < 0) newIndex = files.length - 1;
    
    selectFile(files[newIndex].name);
}

function navigateNext() {
    console.log(files);
    if (files.length === 0) return;
    
    let newIndex = selectedIndex + 1;
    if (newIndex >= files.length) newIndex = 0;
    console.log('navigateNext', newIndex, files[newIndex].name);
    
    selectFile(files[newIndex].name);
}

function handleKeyDown(e) {
    // If user is typing in the feedback input, don't handle navigation keys
    if (e.target.id === 'feedbackInput') {
        if (e.key === 'Enter') {
            e.preventDefault();
            saveFeedback();
        }
        return;
    }
    
    switch (e.key) {
        case 'ArrowLeft':
            e.preventDefault();
            navigatePrevious();
            break;
        case 'ArrowRight':
            console.log('ArrowRight');
            e.preventDefault();
            navigateNext();
            break;
        case 'Enter':
            e.preventDefault();
            if (selectedFile) {
                // document.getElementById('feedbackInput').focus();
            }
            break;
        case 'Escape':
            e.preventDefault();
            closeViewer();
            break;
        case 's':
        case 'S':
            e.preventDefault();
            saveSelected();
            break;
    }
}

// Handle window resize
function handleResize() {
    console.log('Window resized');
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


// Render files in the grid
function renderGrid() {
    console.log("Rendering files");
    const grid = document.getElementById('mainGrid');
    grid.innerHTML = '';
    
    files.forEach((fileData, index) => {
        const item = document.createElement('div');
        
        const fileName = fileData.name;
        const fileContent = fileData.content;
        
        // Add feedback badge if there's feedback
        const hasFeedback = feedbackData[fileName] && feedbackData[fileName].length > 0;
        
        if (selectedFile === fileName) {
            item.classList.add('selected');
        }
        
        item.innerHTML = `
        <div class="main-number">${index + 1}</div>
        ${false ? `<div class="feedback-badge">${feedbackData[fileName].length}</div>` : ''}
        <div class="main-preview" id="preview-${index}">
        </div>
        `;
        
        item.className = item.className + ' bg-white rounded-lg shadow-md transition-all relative cursor-pointer overflow-hidden aspect-square hover:-translate-y-0.5 active:translate-y-0 hover:shadow-lg';
        if (isFirstRender) {
            item.className = item.className + ' opacity-0 translate-y-4 scale-80 duration-300 ';
        }
        if (selectedFile === fileName) {
            item.className = item.className + ' border-2 border-green-500';
        }

        grid.appendChild(item);
        render("preview-" + index, fileContent, fileName);
        
        // Animate in with a delay based on index
        if (isFirstRender) {
            setTimeout(() => {
                item.classList.remove('opacity-0', 'translate-y-4', 'scale-80');
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
        usedExamplesContainer.innerHTML = `
        <h3 class="text-lg font-medium text-gray-900 font-tight">Used Examples</h3>
        <div id="usedExamplesList"></div>
        `;
        usedExamplesContainer.classList.remove('hidden');
    }

    const usedExamplesList = document.getElementById('usedExamplesList');
    usedExamplesList.innerHTML = '';
    usedExamplesList.className = 'mt-4 grid gap-4 grid-flow-col auto-cols-max';

    for (const [file, feedbacks] of Object.entries(usedExamples)) {
        const fileContent = feedbacks.content;
        const newFeedbacks = feedbacks.feedback;
        newFeedbacks.forEach(feedback => {
            const item = document.createElement('div');
            item.id = "used-example-" + file;
            item.className = 'aspect-square bg-white rounded-lg shadow-md transition-all relative overflow-hidden max-w-[200px]';
            renderExample(item, fileContent, feedback);
            usedExamplesList.appendChild(item);
        });
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', async () => {
    isFirstRender = true;
    // Set up keyboard event listener
    document.addEventListener('keydown', handleKeyDown);
    
    // Set up window resize event listener
    window.addEventListener('resize', handleResize);
    
    
    await fetchFiles();
    console.log(files);
    await getFeedbackData();
    console.log(feedbackData);
    await fetchUsedExamples();
    renderUsedExamples();
    // console.log(usedExamples);
    if (files.length > 0) {
        selectFile(files[3].name);
    }
    
    renderGrid();
    setTimeout(() => {
        isFirstRender = false;
    }, 2000);
}); 