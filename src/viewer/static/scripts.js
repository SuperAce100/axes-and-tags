// Global variables
let files = [];
let selectedFile = null;
let selectedIndex = -1;
let feedbackData = {};
let isClosing = false;
let usedExamples = {};
let isFirstRender = true;
let designSpace = {};
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

async function saveDesignSpace() {
    const response = await fetch('/api/save-designspace', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({designSpace})
    });

    if (response.ok) {
        showStatus('Design space saved', 'success');
    } else {
        showStatus('Error saving design space', 'error');
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

if(typeof renderTags === 'undefined') {
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
        
        const previewDiv = document.createElement('div');
        previewDiv.className = 'main-preview w-full h-full max-h-full flex flex-col items-center justify-center';
        previewDiv.id = `preview-${index}`;
        item.appendChild(previewDiv);
        
        item.className = item.className + ' bg-white rounded-lg shadow-md transition-all relative overflow-hidden aspect-square hover:-translate-y-0.5 hover:shadow-lg';
        if (isFirstRender) {
            item.className = item.className + ' opacity-0 translate-y-4 scale-80 duration-500 filter blur-md';
        }
        grid.appendChild(item);

        render("preview-" + index, fileContent, fileName);
        renderTags(fileData, previewDiv);

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
            usedExamplesList.appendChild(item);
            
            renderExample(item, fileContent, feedback);

            if (isFirstRender) {
                setTimeout(() => {
                    item.classList.remove('opacity-0', 'translate-y-4', 'scale-80', 'filter', 'blur-md');
                    item.classList.add('opacity-100', 'translate-y-0', 'scale-100');
                }, index * 100);
            }
        });
    }
}

async function fetchDesignSpace() {
    const response = await fetch('/api/design-space');
    const data = await response.json();
    designSpace = data.design_space;
    console.log("designSpace", data);
}
let icons = {};
async function fetchDesignSpaceIcons() {
    const iconUrls = {
        exploring: 'https://unpkg.com/lucide-static@latest/icons/telescope.svg',
        unconstrained: 'https://unpkg.com/lucide-static@latest/icons/dices.svg',
        constrained: 'https://unpkg.com/lucide-static@latest/icons/lock.svg',
        new: 'https://unpkg.com/lucide-static@latest/icons/plus.svg'
    };

    await Promise.all(
        Object.entries(iconUrls).map(async ([key, url]) => {
            const response = await fetch(url);
            icons[key] = await response.text();
        })
    );
}

function createDesignAxisControls(axis, status, value) {
    const container = document.createElement('div');
    container.className = 'absolute right-0 top-0 w-24 h-full flex gap-1 justify-end items-center p-2 hover:w-fit hover:min-w-24 transition-all z-10 group';
    const exploreButton = document.createElement('button');
    const unconstrainedButton = document.createElement('button');
    const constrainedButton = document.createElement('button');
    const baseButtonClassName = 'bg-transparent rounded-md group-hover:opacity-100 group-hover:w-8 w-0 group-hover:h-8 h-0 opacity-0 top-0 transition-all flex items-center justify-center';
    exploreButton.className = baseButtonClassName + ' hover:bg-green-500/10 text-green-500';
    unconstrainedButton.className = baseButtonClassName + ' hover:bg-red-500/10 text-red-500';
    constrainedButton.className = baseButtonClassName + ' hover:bg-blue-500/10 text-blue-500';

    exploreButton.innerHTML = icons["exploring"];
    unconstrainedButton.innerHTML = icons["unconstrained"];
    constrainedButton.innerHTML = icons["constrained"];

    if (status === "exploring") {
        exploreButton.classList.remove('bg-transparent', 'hover:bg-green-500/10');
        exploreButton.classList.add('bg-green-500/30', 'hover:bg-green-500/50');
    } else if (status === "unconstrained") {
        unconstrainedButton.classList.remove('bg-transparent', 'hover:bg-red-500/10');
        unconstrainedButton.classList.add('bg-red-500/30', 'hover:bg-red-500/50');
    } else if (status === "constrained") {
        constrainedButton.classList.remove('bg-transparent', 'hover:bg-blue-500/10');
        constrainedButton.classList.add('bg-blue-500/30', 'hover:bg-blue-500/50');
    }

    exploreButton.addEventListener('click', async () => {
        designSpace[axis] = ["exploring", value];
        await saveDesignSpace();
        renderDesignSpace();
    });

    unconstrainedButton.addEventListener('click', async () => {
        designSpace[axis] = ["unconstrained", value];
        await saveDesignSpace();
        renderDesignSpace();
    });

    constrainedButton.addEventListener('click', async () => {
        designSpace[axis] = ["constrained", value];
        await saveDesignSpace();
        renderDesignSpace();
    });

    container.appendChild(constrainedButton);
    container.appendChild(unconstrainedButton);
    container.appendChild(exploreButton);
    return container;
}

function createNewDesignAxis() {
    // Create the wrapper first
    const wrapper = document.createElement('div');
    wrapper.className = 'relative';
    
    // Create the button
    const newAxisTriggerButton = document.createElement('button');
    newAxisTriggerButton.className = 'bg-transparent rounded-md w-8 h-8 opacity-100 transition-all flex items-center justify-center z-10 absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2';
    newAxisTriggerButton.innerHTML = icons["new"];
    wrapper.appendChild(newAxisTriggerButton);
    
    // Create the input container
    const container = document.createElement('div');
    container.className = 'w-0 h-9 opacity-0 transition-all duration-300';
    wrapper.appendChild(container);
    
    const label = document.createElement('label');
    label.className = 'text-xs text-gray-500 absolute top-2 left-2 flex items-start justify-center gap-1';
    const itemIcon = document.createElement('div');
    // itemIcon.innerHTML = icons["new"];
    itemIcon.className = `text-gray-500 scale-50 -translate-y-0.5 -translate-x-0.5 w-4 h-4`;
    label.appendChild(itemIcon);
    const itemLabel = document.createElement('span');
    itemLabel.innerHTML = "add new axis";
    label.appendChild(itemLabel);
    container.appendChild(label);
    // Create the input
    const item = document.createElement('input');
    item.className = 'w-full pt-6 pb-2 px-2 bg-gray-200 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-gray-400';
    container.appendChild(item);
    
    // Handle button click to show input
    wrapper.addEventListener('mouseenter', (event) => {
        event.stopPropagation(); // Prevent document click from immediately closing it
        newAxisTriggerButton.classList.remove('w-8', 'opacity-100', 'top-1/2', 'left-1/2', '-translate-x-1/2', '-translate-y-1/2');
        newAxisTriggerButton.classList.add('top-1', 'left-1', 'scale-50', '-translate-y-1');
        container.classList.remove('w-0', 'opacity-0');
        container.classList.add('w-full', 'opacity-100');
        setTimeout(() => item.focus(), 50); // Small delay to ensure transition completes
    });
    
    wrapper.addEventListener('mouseleave', (event) => {
        newAxisTriggerButton.classList.remove('top-1', 'left-1', 'scale-50', '-translate-y-1');
        newAxisTriggerButton.classList.add('w-8', 'opacity-100', 'top-1/2', 'left-1/2', '-translate-x-1/2', '-translate-y-1/2');
        container.classList.remove('w-full', 'opacity-100');
        container.classList.add('w-0', 'opacity-0');
    });

    // Handle Enter key or blur to submit
    const handleSubmit = async () => {
        if (item.value.trim()) {
            designSpace[item.value.trim()] = ["exploring", ""];
            await saveDesignSpace();
            renderDesignSpace();
            
            // Reset and collapse input after submission
            item.value = '';
            container.classList.remove('w-64', 'opacity-100');
            container.classList.add('w-0', 'opacity-0');
        }
    };
    
    // Handle input submission with Enter key
    item.addEventListener('change', handleSubmit);
    
    return wrapper;
}

async function renderDesignSpace() {
    const designSpaceContainer = document.getElementById('designSpaceList');
    designSpaceContainer.innerHTML = '';
    designSpaceContainer.className = 'p-0 space-y-3 mt-4';

    console.log("designSpaceList", designSpace);
    if (isFirstRender) {
        await fetchDesignSpaceIcons();
    }

    for (const [index, [axis, [status, value]]] of Object.entries(Object.entries(designSpace))) {
        console.log("axis", axis, "value", value);
        const container = document.createElement('div');
        container.className = 'relative';
        const item = document.createElement('input');
        const label = document.createElement('label');
        label.className = 'text-xs text-gray-500 absolute top-2 left-2 flex items-start justify-center gap-1';
        const itemIcon = document.createElement('div');
        itemIcon.innerHTML = icons[status];
        const currentColor = status === "exploring" ? "green-500" : status === "unconstrained" ? "red-500" : "blue-500";
        itemIcon.className = `text-${currentColor} scale-50 -translate-y-0.5 -translate-x-0.5 w-4 h-4`;
        label.appendChild(itemIcon);
        const itemLabel = document.createElement('span');
        itemLabel.innerHTML = axis;
        label.appendChild(itemLabel);
        item.id = "design-space-" + axis;
        item.className = 'transition-all relative overflow-hidden hover:bg-gray-300 bg-gray-200 p-2 rounded-lg shadow-sm pt-6 w-full focus:outline-none focus:ring-2 focus:ring-gray-400';
        item.value = value;
        if (status === "unconstrained") {
            item.placeholder = value;
            item.value = "";
        } else if (status === "exploring") {
            item.value = "";
            item.placeholder = "exploring";
        } else if (status === "constrained") {
            item.value = value;
        }
        if (isFirstRender) {
            container.className = container.className + ' opacity-0 translate-y-4 scale-80 duration-500 filter blur-md';
            setTimeout(() => {
                container.classList.remove('opacity-0', 'translate-y-4', 'scale-80', 'filter', 'blur-md');
                container.classList.add('opacity-100', 'translate-y-0', 'scale-100');
            }, index * 100);
        }
        container.appendChild(item);
        container.appendChild(label);
        item.addEventListener('change', async (event) => {
            designSpace[axis] = ["constrained", event.target.value];
            await saveDesignSpace();
            renderDesignSpace();
            console.log("designSpace updated", designSpace);
        });
        container.appendChild(createDesignAxisControls(axis, status, value));
        designSpaceContainer.appendChild(container);
    }
    designSpaceContainer.appendChild(createNewDesignAxis());
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
    await fetchDesignSpace();
    
    renderUsedExamples();
    renderDesignSpace();
    renderGrid();

    setTimeout(() => {
        isFirstRender = false;
    }, 1000);
}); 