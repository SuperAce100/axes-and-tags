let svgs = [];
let selectedSvg = null;
let feedbackData = {};
let isClosing = false;
let selectedIndex = -1;
let isTyping = false;

// Fetch SVGs from the server
async function fetchSvgs() {
    try {
        const response = await fetch('/api/svgs');
        svgs = await response.json();
        renderSvgs();
    } catch (error) {
        showStatus('Error loading SVGs: ' + error.message, 'error');
    }
}

// Render SVGs in the grid
function renderSvgs() {
    const grid = document.getElementById('svgGrid');
    grid.innerHTML = '';
    
    svgs.forEach((svgData, index) => {
        const svgName = svgData.name;
        const svgContent = svgData.content;
        
        const item = document.createElement('div');
        item.className = 'svg-item';
        if (selectedSvg === svgName) {
            item.classList.add('selected');
            selectedIndex = index;
        }
        
        // Add feedback badge if there's feedback
        const hasFeedback = feedbackData[svgName] && feedbackData[svgName].length > 0;
        
        item.innerHTML = `
            <div class="svg-number">${index + 1}</div>
            ${hasFeedback ? `<div class="feedback-badge">${feedbackData[svgName].length}</div>` : ''}
            <div class="svg-preview">
                ${svgContent}
            </div>
        `;
        
        item.addEventListener('click', () => {
            selectSvg(svgName);
        });

        item.addEventListener('dblclick', () => {
            saveSelected();
        });
        
        grid.appendChild(item);
    });
}

// Select an SVG (only one at a time)
async function selectSvg(svg) {
    try {
        const response = await fetch('/api/select', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ svg })
        });
        
        if (response.ok) {
            selectedSvg = svg;
            renderSvgs();
            loadFeedback(svg);
        } else {
            showStatus('Error selecting SVG', 'error');
        }
    } catch (error) {
        showStatus('Error selecting SVG: ' + error.message, 'error');
    }
}

// Load feedback for a specific SVG
async function loadFeedback(svg) {
    try {
        const response = await fetch(`/api/feedback/${svg}`);
        const data = await response.json();
        
        feedbackData[svg] = data.feedback;
        renderFeedbackList();
    } catch (error) {
        console.error('Error loading feedback:', error);
    }
}

// Render feedback list
function renderFeedbackList() {
    const list = document.getElementById('feedbackList');
    list.innerHTML = '';
    
    if (!selectedSvg || !feedbackData[selectedSvg] || feedbackData[selectedSvg].length === 0) {
        list.innerHTML = '<div class="feedback-empty-state">No feedback yet</div>';
        return;
    }
    
    feedbackData[selectedSvg].forEach((feedback, index) => {
        const feedbackItem = document.createElement('div');
        feedbackItem.className = 'feedback-item';
        feedbackItem.textContent = feedback;
        list.appendChild(feedbackItem);
    });
}

// Save feedback for selected SVG
async function saveFeedback() {
    const feedback = document.getElementById('feedbackInput').value.trim();
    
    if (!feedback) {
        showStatus('Please enter feedback', 'error');
        return;
    }
    
    if (!selectedSvg) {
        showStatus('Please select an SVG first', 'error');
        return;
    }
    
    try {
        const response = await fetch('/api/feedback', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ svg: selectedSvg, feedback })
        });
        
        if (response.ok) {
            showStatus(`Feedback saved for ${selectedSvg}`, 'success');
            document.getElementById('feedbackInput').value = '';
            
            // Reload feedback for the selected SVG
            await loadFeedback(selectedSvg);
        } else {
            showStatus('Error saving feedback', 'error');
        }
    } catch (error) {
        showStatus('Error saving feedback: ' + error.message, 'error');
    }
}

// Save selected SVG
async function saveSelected() {
    if (!selectedSvg) {
        showStatus('No SVG selected', 'error');
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
            showStatus(`SVG ${selectedSvg} saved to ${data.path}`, 'success');
        } else {
            showStatus('Error saving SVG', 'error');
        }
    } catch (error) {
        showStatus('Error saving SVG: ' + error.message, 'error');
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
function showStatus(message, type) {
    const status = document.getElementById('status');
    status.textContent = message;
    status.className = 'status ' + type;
    status.style.display = 'block';
    
    setTimeout(() => {
        status.style.display = 'none';
    }, 3000);
}

// Navigate to previous SVG
function navigatePrevious() {
    if (svgs.length === 0) return;
    
    let newIndex = selectedIndex - 1;
    if (newIndex < 0) newIndex = svgs.length - 1;
    
    selectSvg(svgs[newIndex].name);
}

// Navigate to next SVG
function navigateNext() {
    if (svgs.length === 0) return;
    
    let newIndex = selectedIndex + 1;
    if (newIndex >= svgs.length) newIndex = 0;
    
    selectSvg(svgs[newIndex].name);
}

// Handle keyboard shortcuts
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
            e.preventDefault();
            navigateNext();
            break;
        case 'Enter':
            e.preventDefault();
            if (selectedSvg) {
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

// Event listeners
document.getElementById('saveFeedbackBtn').addEventListener('click', saveFeedback);
document.addEventListener('keydown', handleKeyDown);

// Add beforeunload event handler
window.addEventListener('beforeunload', function(e) {
    if (!isClosing) {
        // Use sendBeacon for more reliable delivery during page unload
        navigator.sendBeacon('/api/close');
    }
});

// Initialize
fetchSvgs();