let jsFiles = [];
let selectedJs = null;
let feedbackData = {};
let isClosing = false;
let selectedIndex = -1;
let isTyping = false;
let scenes = {};
let cameras = {};
let renderers = {};
let controls = {};
let objects = {};

// Fetch JavaScript files from the server
async function fetchJsFiles() {
    try {
        const response = await fetch('/api/js');
        jsFiles = await response.json();
        renderJsFiles();
    } catch (error) {
        showStatus('Error loading JavaScript files: ' + error.message, 'error');
    }
}

// Render JavaScript files in the grid
function renderJsFiles() {
    const grid = document.getElementById('threejsGrid');
    grid.innerHTML = '';
    
    jsFiles.forEach((jsData, index) => {
        const jsName = jsData.name;
        const jsContent = jsData.content;
        
        const item = document.createElement('div');
        item.className = 'threejs-item';
        if (selectedJs === jsName) {
            item.classList.add('selected');
            selectedIndex = index;
        }
        
        // Add feedback badge if there's feedback
        const hasFeedback = feedbackData[jsName] && feedbackData[jsName].length > 0;
        
        item.innerHTML = `
            <div class="js-number">${index + 1}</div>
            ${hasFeedback ? `<div class="feedback-badge">${feedbackData[jsName].length}</div>` : ''}
            <div class="threejs-preview" id="preview-${index}"></div>
        `;
        
        item.addEventListener('click', () => {
            selectJs(jsName);
        });

        item.addEventListener('dblclick', () => {
            saveSelected();
        });
        
        grid.appendChild(item);
        
        // Initialize Three.js scene for this preview
        initThreeJsScene(index, jsContent);
    });
}

// Initialize Three.js scene for a preview
async function initThreeJsScene(index, jsContent) {
    const container = document.getElementById(`preview-${index}`);
    if (!container) return;

    const width = container.clientWidth;
    const height = container.clientHeight;
    
    // Create scene
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0xf0f0f0);
    scenes[index] = scene;
    
    // Create camera
    const camera = new THREE.PerspectiveCamera(50, width / height, 0.1, 1000);
    cameras[index] = camera;
    camera.position.set(5, 5, 5);
    camera.lookAt(0, 0, 0);
    
    // Create renderer
    const renderer = new THREE.WebGLRenderer({ 
        antialias: true,
        alpha: true
    });
    renderer.setPixelRatio(window.devicePixelRatio);
    renderer.setSize(width, height);
    renderer.shadowMap.enabled = true;
    renderers[index] = renderer;
    container.appendChild(renderer.domElement);
    
    // Add lights
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
    scene.add(ambientLight);
    
    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
    directionalLight.position.set(5, 5, 5);
    directionalLight.castShadow = true;
    scene.add(directionalLight);

    const fillLight = new THREE.DirectionalLight(0xffffff, 0.4);
    fillLight.position.set(-5, 0, -5);
    scene.add(fillLight);
    
    // Add orbit controls
    const orbitControls = new THREE.OrbitControls(camera, renderer.domElement);
    orbitControls.enableDamping = false;
    // orbitControls.dampingFactor = 0.05;
    orbitControls.enableZoom = true;
    orbitControls.enablePan = true;
    orbitControls.autoRotate = true;
    orbitControls.autoRotateSpeed = 1.3;
    controls[index] = orbitControls;
    
    try {
        // Create a blob URL from the JavaScript content
        const blob = new Blob([jsContent], { type: 'application/javascript' });
        const blobUrl = URL.createObjectURL(blob);
        
        // Load the script
        const script = document.createElement('script');
        script.src = blobUrl;
        
        // Wait for script to load
        await new Promise((resolve, reject) => {
            script.onload = resolve;
            script.onerror = reject;
            document.head.appendChild(script);
        });
        
        // Clean up
        URL.revokeObjectURL(blobUrl);
        document.head.removeChild(script);
        
        // Get the createObject function
        const createObject = window.createObject;
        
        if (typeof createObject === 'function') {
            const object = createObject(container);
            if (object) {
                scene.add(object);
                objects[index] = object;
                
                // Center and scale the object
                const box = new THREE.Box3().setFromObject(object);
                const center = box.getCenter(new THREE.Vector3());
                const size = box.getSize(new THREE.Vector3());
                
                // Center the object
                object.position.sub(center);
                
                // Scale the object to fit the view
                const maxDim = Math.max(size.x, size.y, size.z);
                const scale = 4 / maxDim;
                object.scale.multiplyScalar(scale);
            }
        }
    } catch (error) {
        console.error('Error creating 3D object:', error);
        showStatus('Error creating 3D object: ' + error.message, 'error');
    }
    
    // Animate
    function animate() {
        requestAnimationFrame(animate);
        controls[index].update();
        renderer.render(scene, camera);
    }
    animate();
}

// Select a JavaScript file
async function selectJs(js) {
    try {
        const response = await fetch('/api/select', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ js })
        });
        
        if (response.ok) {
            selectedJs = js;
            renderJsFiles();
            loadFeedback(js);
        } else {
            showStatus('Error selecting JavaScript file', 'error');
        }
    } catch (error) {
        showStatus('Error selecting JavaScript file: ' + error.message, 'error');
    }
}

// Load feedback for a specific JavaScript file
async function loadFeedback(js) {
    try {
        const response = await fetch(`/api/feedback/${js}`);
        const data = await response.json();
        
        feedbackData[js] = data.feedback;
        renderFeedbackList();
    } catch (error) {
        console.error('Error loading feedback:', error);
    }
}

// Render feedback list
function renderFeedbackList() {
    const list = document.getElementById('feedbackList');
    list.innerHTML = '';
    
    if (!selectedJs || !feedbackData[selectedJs] || feedbackData[selectedJs].length === 0) {
        list.innerHTML = '<div class="feedback-empty-state">No feedback yet</div>';
        return;
    }
    
    feedbackData[selectedJs].forEach((feedback, index) => {
        const feedbackItem = document.createElement('div');
        feedbackItem.className = 'feedback-item';
        feedbackItem.textContent = feedback;
        list.appendChild(feedbackItem);
    });
}

// Save feedback for selected JavaScript file
async function saveFeedback() {
    const feedback = document.getElementById('feedbackInput').value.trim();
    
    if (!feedback) {
        showStatus('Please enter feedback', 'error');
        return;
    }
    
    if (!selectedJs) {
        showStatus('Please select an object first', 'error');
        return;
    }
    
    try {
        const response = await fetch('/api/feedback', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ js: selectedJs, feedback })
        });
        
        if (response.ok) {
            showStatus(`Feedback saved for ${selectedJs}`, 'success');
            document.getElementById('feedbackInput').value = '';
            
            // Reload feedback for the selected JavaScript file
            await loadFeedback(selectedJs);
        } else {
            showStatus('Error saving feedback', 'error');
        }
    } catch (error) {
        showStatus('Error saving feedback: ' + error.message, 'error');
    }
}

// Save selected JavaScript file
async function saveSelected() {
    if (!selectedJs) {
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
            showStatus(`Object ${selectedJs} saved to ${data.path}`, 'success');
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

// Navigate to previous JavaScript file
function navigatePrevious() {
    if (jsFiles.length === 0) return;
    
    let newIndex = selectedIndex - 1;
    if (newIndex < 0) newIndex = jsFiles.length - 1;
    
    selectJs(jsFiles[newIndex].name);
}

// Navigate to next JavaScript file
function navigateNext() {
    if (jsFiles.length === 0) return;
    
    let newIndex = selectedIndex + 1;
    if (newIndex >= jsFiles.length) newIndex = 0;
    
    selectJs(jsFiles[newIndex].name);
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
            if (selectedJs) {
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
    jsFiles.forEach((_, index) => {
        const container = document.getElementById(`preview-${index}`);
        if (container && renderers[index] && cameras[index]) {
            const width = container.clientWidth;
            const height = container.clientHeight;
            
            cameras[index].aspect = width / height;
            cameras[index].updateProjectionMatrix();
            
            renderers[index].setSize(width, height, true);
        }
    });
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    fetchJsFiles();
    document.addEventListener('keydown', handleKeyDown);
    window.addEventListener('resize', handleResize);
    
    document.getElementById('saveFeedbackBtn').addEventListener('click', saveFeedback);
}); 