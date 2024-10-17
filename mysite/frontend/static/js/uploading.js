
function previewCover() {
    var fileInput = document.getElementById('cover_image_file');
    var preview = document.getElementById('cover-preview');
    
    // Check if a file has been selected
    if (fileInput.files && fileInput.files[0]) {
        var reader = new FileReader();
        
        // When the image is fully loaded, set it as the source of the preview
        reader.onload = function(e) {
            preview.src = e.target.result;
        }
        
        // Read the image file as a data URL
        reader.readAsDataURL(fileInput.files[0]);
    }
}

document.addEventListener('DOMContentLoaded', function() {
    // Get all buttons with the class 'upload-btn'
    const buttons = document.querySelectorAll('#upload-page .upload-btn');
    console.log("hello")
    buttons.forEach(button => {
        // Add click event listener to each button
        button.addEventListener('click', function() {
            // Remove 'active' class from all buttons
            buttons.forEach(btn => btn.classList.remove('active'));

            // Add 'active' class to the clicked button
            this.classList.add('active');
        });
    });
});