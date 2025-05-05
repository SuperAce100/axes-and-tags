// Global variables
let files = [];
let selectedFile = null;
let selectedIndex = -1;
let feedbackData = {};
let isClosing = false;

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
        renderFeedbackList();
    } catch (error) {
        console.error('Error loading feedback:', error);
    }
}

async function getFeedbackData() {
    files.forEach(async (file) => {
        await loadFeedback(file.name);
    });
}

// Render feedback list
function renderFeedbackList() {
    const list = document.getElementById('feedbackList');
    list.innerHTML = '';
    
    if (!selectedFile || !feedbackData[selectedFile] || feedbackData[selectedFile].length === 0) {
        list.innerHTML = '<div class="text-gray-400 text-center py-8 text-sm">No feedback yet</div>';
        return;
    }
    
    feedbackData[selectedFile].forEach((feedback, index) => {
        const feedbackItem = document.createElement('div');
        feedbackItem.className = 'p-3 border-b border-gray-100 last:border-b-0 hover:bg-gray-50 transition-colors';
        feedbackItem.textContent = feedback;
        list.appendChild(feedbackItem);
    });
}

// Save feedback for selected file
async function saveFeedback() {
    const feedback = document.getElementById('feedbackInput').value.trim();
    
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
        
        if (response.ok) {
            showStatus(`Feedback saved for ${selectedFile}`, 'success');
            document.getElementById('feedbackInput').value = '';
            
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
                document.getElementById('feedbackInput').focus();
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
        if (selectedFile === fileName) {
            item.className = item.className + ' border-2 border-green-500';
        }

        grid.appendChild(item);
        render("preview-" + index, fileContent, fileName);
        
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
    console.log("used examples", data);
    return data.used_examples;
}


// Initialize
document.addEventListener('DOMContentLoaded', async () => {
    // Set up keyboard event listener
    document.addEventListener('keydown', handleKeyDown);
    
    // Set up window resize event listener
    window.addEventListener('resize', handleResize);
    
    // Set up feedback button click event listener
    document.getElementById('saveFeedbackBtn').addEventListener('click', saveFeedback);
    
    await fetchFiles();
    console.log(files);
    await getFeedbackData();
    console.log(feedbackData);
    await fetchUsedExamples();
    // console.log(usedExamples);
    if (files.length > 0) {
        selectFile(files[3].name);
    }
    
    renderGrid();
    renderFeedbackList();
}); 