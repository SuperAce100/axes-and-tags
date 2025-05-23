function render(container, content) {
  const imgElement = document.createElement("img");
  imgElement.src = `data:image/png;base64,${content}`;
  imgElement.className = "w-full h-full object-contain";

  container.appendChild(imgElement);
}
