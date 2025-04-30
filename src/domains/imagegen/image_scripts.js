function render(id, content) {
  const container = document.getElementById(id);
  const imgElement = document.createElement('img');;
  imgElement.src = `data:image/png;base64,${content.data}`;
  imgElement.style.width = '100%';
  imgElement.style.height = '100%';
  imgElement.style.objectFit = 'contain';
  container.appendChild(imgElement);
  return imgElement;
}
