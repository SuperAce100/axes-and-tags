/**
 * Renders a p5.js sketch in the DOM element with the specified ID using a string of JavaScript code
 * @param {string} id - The ID of the DOM element where the sketch should be rendered
 * @param {string} content - A string containing valid p5.js code in global mode
 * @returns {Object} - The p5 instance
 */
/**
 * Renders a p5.js sketch in the DOM element with the specified ID using a string of JavaScript code
 * @param {string} id - The ID of the DOM element where the sketch should be rendered
 * @param {string} content - A string containing valid p5.js code in global mode
 * @returns {Object} - The p5 instance
 */
function render(id, content, fileName) {
  container = document.getElementById(id);
  const script = document.createElement('script');
  script.textContent = content.data;
  container.appendChild(script);
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