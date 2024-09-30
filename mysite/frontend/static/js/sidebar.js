function toggleSidebar() {
    var sidebar = document.getElementById("sidebar");
    var hamburgerIcon = document.querySelector(".hamburger-icon");

    if (sidebar.classList.contains('open')) {
        // Close the sidebar with curtain effect
        sidebar.classList.remove('open');
        sidebar.classList.add('closed');
        setTimeout(function() {
            hamburgerIcon.style.display = "block";
        }, 500); // Wait for the transition to complete (500ms)
    } else {
        // Open the sidebar with curtain effect
        sidebar.classList.remove('closed');
        sidebar.classList.add('open');
        hamburgerIcon.style.display = "none";
    }
}

// Function to handle page navigation and load content dynamically
function navigateAndClose(element) {
    // Close the sidebar
    toggleSidebar();

    // Delay navigation until after the sidebar animation (e.g., 300ms)
    setTimeout(function() {
        var url = element.getAttribute('data-href');

        // Fetch the new page content dynamically
        fetch(url)
            .then(response => response.text())
            .then(data => {
                // Create a temporary container to parse the new content
                var newContent = document.createElement('div');
                newContent.innerHTML = data;

                // Extract the specific section to update (e.g., #content-container)
                var newContentBlock = newContent.querySelector('#content-container');
                if (newContentBlock) {
                    document.getElementById('content-container').innerHTML = newContentBlock.innerHTML;
                }

                // Optionally, reinitialize any event listeners or scripts for the new content if needed
            })
            .catch(error => console.log('Error loading page:', error));
    }, 300); // Adjust this delay to match your sidebar close animation
}
