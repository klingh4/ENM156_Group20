// Function to auto-grow/shrink a textarea to fit content
const autoGrow = (el: HTMLElement) => {
    // Reset height to its minimum to allow shrinking
    const baseHeight = '28px'
    el.style.height = baseHeight;
    el.style.height = (el.scrollHeight) + 'px';
};

// Growing and shrinking of remark input fields
export function activateRemarkResizing() {
    // Find all remark textareas
    const textareas = document.querySelectorAll('.remark-input');

    textareas.forEach(textarea => {
        // Add event listener for 'input' event (typing, deleting)
        textarea.addEventListener("input", (e) => {
            autoGrow(textarea as HTMLElement);
        });
    });
}