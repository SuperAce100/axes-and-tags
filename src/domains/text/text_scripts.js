function render(id, content, prompt) {
  const container = document.getElementById(id);
  container.className = "relative";

  // Create image element
  const textElement = document.createElement("div");
  textElement.textContent = content;
  textElement.className = "p-4 text-sm w-full overflow-y-auto aspect-square font-serif pb-24";

  container.appendChild(textElement);

  return textElement;
}
