function render(id, content, fileName) {
  // Get the container element
  const container = document.getElementById(id);
  if (!container) {
    console.error(`Container with ID "${id}" not found`);
    return;
  }

  // Create a canvas element
  const canvas = document.createElement('canvas');
  container.appendChild(canvas);

  // Set canvas to fill the container
  canvas.width = container.clientWidth;
  canvas.height = container.clientHeight;
  canvas.style.display = 'block';

  // Create resize observer to handle container size changes
  const resizeObserver = new ResizeObserver(entries => {
    for (const entry of entries) {
      canvas.width = entry.contentRect.width;
      canvas.height = entry.contentRect.height;
      gl.viewport(0, 0, canvas.width, canvas.height);
    }
  });
  resizeObserver.observe(container);

  // Initialize WebGL
  const gl = canvas.getContext('webgl');
  if (!gl) {
    container.innerHTML = 'WebGL is not supported in your browser';
    return;
  }

  // Vertex shader always stays the same - just a simple fullscreen quad
  const vertexShaderSource = `
    attribute vec2 a_position;
    void main() {
      gl_Position = vec4(a_position, 0.0, 1.0);
    }
  `;

  // Fragment shader - prepend necessary uniforms and mainImage wrapper
  const fragmentShaderPrefix = `
    precision highp float;
    uniform vec2 iResolution;
    uniform float iTime;
    uniform vec4 iMouse;
    uniform float iFrame;
  `;

  const fragmentShaderSuffix = `
    void main() {
      vec4 fragColor;
      mainImage(fragColor, gl_FragCoord.xy);
      gl_FragColor = fragColor;
    }
  `;

  const fragmentShaderSource = fragmentShaderPrefix + content.data + fragmentShaderSuffix;

  // Create and compile shaders
  const vertexShader = createShader(gl, gl.VERTEX_SHADER, vertexShaderSource);
  const fragmentShader = createShader(gl, gl.FRAGMENT_SHADER, fragmentShaderSource);

  if (!vertexShader || !fragmentShader) {
    container.innerHTML = 'Failed to compile shaders';
    container.parentElement.remove();
    return;
  }

  // Create shader program
  const program = createProgram(gl, vertexShader, fragmentShader);
  if (!program) {
    container.innerHTML = 'Failed to create shader program';
    return;
  }

  // Look up vertex data location
  const positionAttributeLocation = gl.getAttribLocation(program, 'a_position');

  // Create a buffer and put a fullscreen quad in it (2 triangles)
  const positionBuffer = gl.createBuffer();
  gl.bindBuffer(gl.ARRAY_BUFFER, positionBuffer);
  const positions = [
    -1, -1,
     1, -1,
    -1,  1,
    -1,  1,
     1, -1,
     1,  1,
  ];
  gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(positions), gl.STATIC_DRAW);

  // Look up uniforms
  const resolutionUniformLocation = gl.getUniformLocation(program, 'iResolution');
  const timeUniformLocation = gl.getUniformLocation(program, 'iTime');
  const mouseUniformLocation = gl.getUniformLocation(program, 'iMouse');
  const frameUniformLocation = gl.getUniformLocation(program, 'iFrame');

  // Mouse tracking
  const mouse = { x: 0, y: 0, z: 0, w: 0 };
  let mouseDown = false;

  canvas.addEventListener('mousemove', e => {
    const rect = canvas.getBoundingClientRect();
    mouse.x = e.clientX - rect.left;
    mouse.y = rect.height - (e.clientY - rect.top); // Flip Y to match GLSL convention
  });

  canvas.addEventListener('mousedown', () => {
    mouseDown = true;
    mouse.z = mouse.x;
    mouse.w = mouse.y;
  });

  canvas.addEventListener('mouseup', () => {
    mouseDown = false;
    mouse.z = 0;
    mouse.w = 0;
  });

  // Touch support for mobile
  canvas.addEventListener('touchstart', e => {
    if (e.touches.length > 0) {
      const rect = canvas.getBoundingClientRect();
      mouse.x = e.touches[0].clientX - rect.left;
      mouse.y = rect.height - (e.touches[0].clientY - rect.top);
      mouse.z = mouse.x;
      mouse.w = mouse.y;
    }
  });

  canvas.addEventListener('touchmove', e => {
    if (e.touches.length > 0) {
      const rect = canvas.getBoundingClientRect();
      mouse.x = e.touches[0].clientX - rect.left;
      mouse.y = rect.height - (e.touches[0].clientY - rect.top);
    }
  });

  canvas.addEventListener('touchend', () => {
    mouse.z = 0;
    mouse.w = 0;
  });

  // Animation state
  let startTime = performance.now();
  let frameCount = 0;

  // Draw the scene
  function render() {
    frameCount++;
    const currentTime = (performance.now() - startTime) / 1000; // time in seconds

    // Update canvas dimensions if needed
    if (canvas.width !== container.clientWidth || canvas.height !== container.clientHeight) {
      canvas.width = container.clientWidth;
      canvas.height = container.clientHeight;
      gl.viewport(0, 0, canvas.width, canvas.height);
    }

    gl.clearColor(0, 0, 0, 1);
    gl.clear(gl.COLOR_BUFFER_BIT);

    // Tell WebGL how to convert clip space to pixels
    gl.viewport(0, 0, canvas.width, canvas.height);

    // Use our shader program
    gl.useProgram(program);

    // Setup the position attribute
    gl.enableVertexAttribArray(positionAttributeLocation);
    gl.bindBuffer(gl.ARRAY_BUFFER, positionBuffer);
    gl.vertexAttribPointer(positionAttributeLocation, 2, gl.FLOAT, false, 0, 0);

    // Set uniforms
    gl.uniform2f(resolutionUniformLocation, canvas.width, canvas.height);
    gl.uniform1f(timeUniformLocation, currentTime);
    gl.uniform4f(mouseUniformLocation, mouse.x, mouse.y, mouse.z, mouse.w);
    gl.uniform1f(frameUniformLocation, frameCount);

    // Draw the fullscreen quad
    gl.drawArrays(gl.TRIANGLES, 0, 6);

    // Request the next frame
    requestAnimationFrame(render);
  }

  // Start rendering
  requestAnimationFrame(render);

  // Utility function to create a shader
  function createShader(gl, type, source) {
    const shader = gl.createShader(type);
    gl.shaderSource(shader, source);
    gl.compileShader(shader);
    
    // Check if compilation was successful
    const success = gl.getShaderParameter(shader, gl.COMPILE_STATUS);
    if (success) {
      return shader;
    }
    
    // If there was an error, log it and delete the shader
    console.error(gl.getShaderInfoLog(shader));
    gl.deleteShader(shader);
    
    // Display error on canvas
    const shaderType = type === gl.VERTEX_SHADER ? 'Vertex' : 'Fragment';
    container.innerHTML = `<div style="color: red; white-space: pre-wrap; font-family: monospace; padding: 10px;">
      ${shaderType} Shader Error:
      ${gl.getShaderInfoLog(shader)}
    </div>`;
    return null;
  }

  // Utility function to create a shader program
  function createProgram(gl, vertexShader, fragmentShader) {
    const program = gl.createProgram();
    gl.attachShader(program, vertexShader);
    gl.attachShader(program, fragmentShader);
    gl.linkProgram(program);
    
    // Check if linking was successful
    const success = gl.getProgramParameter(program, gl.LINK_STATUS);
    if (success) {
      return program;
    }
    
    // If there was an error, log it and delete the program
    console.error(gl.getProgramInfoLog(program));
    gl.deleteProgram(program);
    
    // Display error on canvas
    container.innerHTML = `<div style="color: red; white-space: pre-wrap; font-family: monospace; padding: 10px;">
      Shader Program Error:
      ${gl.getProgramInfoLog(program)}
    </div>`;
    return null;
  }

  // Return cleanup function
  return function cleanup() {
    resizeObserver.disconnect();
    cancelAnimationFrame(render);
    gl.deleteProgram(program);
    gl.deleteShader(vertexShader);
    gl.deleteShader(fragmentShader);
    gl.deleteBuffer(positionBuffer);
    container.removeChild(canvas);
  };
}

function renderTags(fileData, container) {
    // Create tags container
    const tagsContainer = document.createElement('div');
    tagsContainer.className = 'flex gap-1 flex-wrap mt-1';

    // Add each tag
    if (fileData.content.tags && Array.isArray(fileData.content.tags)) {
        fileData.content.tags.forEach((tag, index) => {
            const tagElement = document.createElement('span');
            tagElement.textContent = tag;
            tagElement.className = `tag bg-white/20 px-1.5 py-0.5 rounded-full text-[10px] text-white hover:bg-white/30 hover:scale-105 cursor-pointer font-sans active:scale-95 transition-all z-[${10+index}]`;

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
    tagOverlay.className = 'bg-gradient-to-t from-black/85 via-black/60 to-transparent p-3 absolute bottom-0 left-0 w-full z-10';
    tagOverlay.id = "tag-overlay";
    // Append elements
    tagOverlay.appendChild(tagsContainer);
    container.appendChild(tagOverlay);
}
function renderExample(container, content, feedback) {
  const uiElement = document.createElement('div');
  let cleanedFeedback = "shader-container-" + feedback.replace(/<[^>]*>?/g, '').replace(/\s+/g, '-');
  uiElement.id = cleanedFeedback;
  uiElement.className = 'w-full h-full';
  container.appendChild(uiElement);
  
  render(cleanedFeedback, content, "temp");
  uiElement.style.zoom = "0.1";

  const feedbackContainer = document.createElement('div');
  feedbackContainer.className = 'absolute top-0 left-0 w-full p-2 z-10 bg-gradient-to-b from-black/85 via-black/60 to-transparent';
  
  const feedbackElement = document.createElement('div');
  feedbackElement.textContent = feedback;
  feedbackElement.className = 'text-white font-tight';
  feedbackContainer.appendChild(feedbackElement);
  
  container.appendChild(feedbackContainer);
}