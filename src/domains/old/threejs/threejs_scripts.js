let scenes = [];
let cameras = [];
let renderers = [];
let controls = [];
let objects = [];

// Initialize Three.js scene for a preview
async function initThreeJsScene(id, container, jsContent) {
    const width = container.clientWidth;
    const height = width;
    console.log("width", width, "height", height);

    index = id.split('-')[1];
    
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
    orbitControls.enableDamping = true;
    orbitControls.dampingFactor = 0.05;
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
                console.log(object);
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
        if (controls[index].enabled) {
            controls[index].update();
        }
        renderer.render(scene, camera);
    }
    animate();

    // Handle window resize
    window.addEventListener('resize', () => {
        const width = container.clientWidth;
        const rect = container.getBoundingClientRect();
        const height = rect.height;
        
        camera.aspect = width / height;
        camera.updateProjectionMatrix();
        renderer.setSize(width, height);
    });
}



function render(id, content) {
    const item = document.getElementById(id);
    const container = document.createElement("div");
    container.className = "bg-white rounded-lg flex flex-col items-center justify-center group w-full h-full";
    item.appendChild(container);
    
    try {
        initThreeJsScene(id, container, content.model);
    } catch (e) {
        console.error(e);
        container.innerHTML = "Error loading model";
    }
}

function renderExample(container, content, feedback) {
    const example = document.createElement('div');
    container.className = 'relative w-full h-full bg-white rounded-lg flex flex-col items-center justify-center group';
    const id = container.id;
    
    const titleOverlay = document.createElement('div');
    titleOverlay.className = 'p-2 pb-0 w-full text-left z-12 absolute top-0 left-0';
    
    const titleElement = document.createElement('div');
    titleElement.textContent = feedback;
    titleElement.className = 'font-tight';
    
    titleOverlay.appendChild(titleElement);

    const exampleContainer = document.createElement('div');
    exampleContainer.className = 'w-full h-full overflow-hidden rounded-lg';
    exampleContainer.appendChild(example);

    container.appendChild(titleOverlay);
    container.appendChild(exampleContainer);

    initThreeJsScene(id, exampleContainer, content.model);
}

function renderTags(fileData, container) {
    // Create tags container
    const tagsContainer = document.createElement('div');
    tagsContainer.className = 'flex gap-1 flex-wrap-reverse mt-1 ';

    // Add each tag
    if (fileData.content.tags && Array.isArray(fileData.content.tags)) {
        fileData.content.tags.forEach(tag => {
            const tagElement = document.createElement('span');
            tagElement.textContent = tag;
            tagElement.className = 'tag bg-gray-100/10 px-1.5 py-0.5 rounded-full text-[10px] text-gray-600 hover:bg-gray-200/50 hover:scale-105 cursor-pointer font-sans active:scale-95 transition-all border';

            if (feedbackData[fileData.name]) {
                if (feedbackData[fileData.name].includes(tag)) {
                    tagElement.className = tagElement.className.replace('bg-gray-100/50', 'bg-green-100/50')
                        .replace('text-gray-600', 'text-green-600')
                        .replace('hover:bg-gray-200/50', 'hover:bg-green-200/50');
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
    tagOverlay.className = 'p-2 pt-0 w-full z-12 absolute bottom-0 left-0';
    tagOverlay.id = "tag-overlay";
    // Append elements
    tagOverlay.appendChild(tagsContainer);
    container.appendChild(tagOverlay);
}