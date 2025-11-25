// Growing and shrinking of remark input fields
document.addEventListener('DOMContentLoaded', (event) => {
    // Find all remark textareas
    const textareas = document.querySelectorAll('.remark-input');

    // Function to auto-grow/shrink a textarea to fit content
    const autoGrow = (el) => {
        // Reset height to its minimum to allow shrinking
        const baseHeight = '28px'
        el.style.height = baseHeight;
        el.style.height = (el.scrollHeight) + 'px';
    };

    textareas.forEach(textarea => {
        // Add event listener for 'input' event (typing, deleting)
        textarea.addEventListener("input", (e) => {
            autoGrow(textarea);
        });
    });
});

var map = L.map('map-view').setView([60, 15], 4)
L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
}).addTo(map);