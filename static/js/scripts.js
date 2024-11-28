const uploadArea = document.getElementById('upload-area');
const fileInput = document.getElementById('file-input');

// Prevent default behavior for dragover and drop events
uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.classList.add('dragging');
});

uploadArea.addEventListener('dragleave', () => {
    uploadArea.classList.remove('dragging');
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.classList.remove('dragging');

    const files = e.dataTransfer.files; // Get all files dropped
    uploadFiles(files); // Upload all files
});

// Trigger file input click when the user clicks the upload area
uploadArea.addEventListener('click', () => {
    fileInput.click();
});

// Handle file selection via file input
fileInput.addEventListener('change', (e) => {
    const files = e.target.files; // Get selected files
    uploadFiles(files); // Upload all selected files
});

// Function to upload multiple files using Fetch API
function uploadFiles(files) {
    if (files.length === 0) {
        return;
    }

    const formData = new FormData();

    // Append each file to FormData
    Array.from(files).forEach(file => {
        formData.append('files[]', file); // 'files[]' is the key that Flask will expect
    });

    fetch('/upload', {
        method: 'POST',
        body: formData, // This sends the file data as form-data
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message || data.error);
    })
    .catch(error => {
        alert('Error uploading files!');
        console.error(error);
    });
}
