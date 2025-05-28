function render(container, content) {
  container.classList.add("relative", "group", "parent");

  const uiElement = document.createElement("div");
  uiElement.innerHTML = content;
  uiElement.className = "w-full h-full transition-all hover:z-30 z-0 overflow-y-auto";
  uiElement.style.zoom = "0.3";

  container.appendChild(uiElement);
}
