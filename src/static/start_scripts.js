var selectedDomain = null;
var domains = [];

function renderDomains() {
  const domainContainer = document.getElementById("domains");
  domainContainer.innerHTML = "";
  domainContainer.classList.add("flex", "flex-row", "gap-4", "bg-gray-100", "p-4", "rounded-full");
  domains.forEach((domain) => {
    const domainElement = document.createElement("div");
    domainElement.textContent = domain.display_name;
    domainElement.classList.add(
      "px-4",
      "py-2",
      "rounded-full",
      "cursor-pointer",
      "transition-all",
      "duration-200",
      "font-medium"
    );

    if (selectedDomain === domain.name) {
      domainElement.classList.add("bg-blue-500", "text-white", "scale-105", "hover:bg-blue-400");
    } else {
      domainElement.classList.add("bg-gray-200", "hover:bg-gray-300");
    }

    domainElement.addEventListener("click", (e) => {
      selectedDomain = domain.name;
      renderDomains();
    });
    domainContainer.appendChild(domainElement);
  });
}

document.addEventListener("DOMContentLoaded", () => {
  fetch("/api/domains")
    .then((res) => res.json())
    .then((data) => {
      data.forEach((domain) => {
        domains = [...domains, domain];
      });
      renderDomains();
    });

  const input = document.querySelector("input");
  const button = document.getElementById("generateButton");
  button.addEventListener("click", (e) => {
    const concept = input.value;
    if (concept.length > 0 && selectedDomain) {
      window.location.href = `/generated/${selectedDomain}/${concept}`;
    } else {
      alert("Please enter a concept and select a domain");
    }
  });
});
