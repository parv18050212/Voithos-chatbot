document.getElementById('fileUploadForm').addEventListener('submit', function (event) {
    event.preventDefault();

    // Get the file input and the user query
    const fileInput = document.getElementById('fileInput');
    const queryInput = document.getElementById('queryInput');
    const formData = new FormData();
    
    formData.append('file', fileInput.files[0]);
    formData.append('query', queryInput.value);

    // Send the form data to the backend (Flask API)
    fetch('/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            console.error('Error:', data.error);
            alert('Failed to upload or process the file.');
        } else {
            console.log('Success:', data);
            alert('File processed successfully!');
        }
    })
    .catch((error) => {
        console.error('Error:', error);
        alert('An error occurred during the file upload.');
    });
});
