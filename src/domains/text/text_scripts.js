function render(container, content) {
  container.className = "relative";

  // Create image element
  const textElement = document.createElement("div");
  textElement.innerHTML = content.replace("\n", " <br> <br>");
  textElement.className = "p-4 text-sm w-full overflow-y-auto aspect-square font-serif pb-24";

  container.appendChild(textElement);
}
