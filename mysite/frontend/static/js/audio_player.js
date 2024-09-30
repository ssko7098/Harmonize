// Function to play audio
function playAudio(url) {
    const audioPlayer = document.getElementById('audio-player');
    const audioSource = document.getElementById('audio-source');

    // Check if the song clicked is already playing
    if (audioSource.src === url) {
        // If it's the same song, restart it from the beginning
        audioPlayer.currentTime = 0;
        audioPlayer.play();
    } else {
        // If it's a new song, set the new URL and play the audio
        audioSource.src = url;
        audioPlayer.load();
        audioPlayer.play();
    }
}

// Function to load content dynamically without affecting the audio player
function loadPageContent(url) {
    fetch(url)
        .then(response => response.text())
        .then(data => {
            const parser = new DOMParser();
            const doc = parser.parseFromString(data, 'text/html');
            const newContent = doc.querySelector('#content-container').innerHTML;

            // Replace only the content inside #content-container
            document.getElementById('content-container').innerHTML = newContent;

            // Attach event listeners for any dynamic content if necessary
            attachEventListeners();
        })
        .catch(error => console.log('Error loading content:', error));
}

// Attach dynamic content loading to navigation links (with the class nav-link)
function attachEventListeners() {
    document.querySelectorAll('a.nav-link').forEach(link => {
        link.removeEventListener('click', handleLinkClick); // Remove existing listeners to avoid duplication
        link.addEventListener('click', handleLinkClick);    // Add new event listener
    });

    // If the search form exists, attach its event listener
    const searchForm = document.getElementById('search-form');
    if (searchForm) {
        searchForm.removeEventListener('submit', handleSearchSubmit); // Avoid duplication
        searchForm.addEventListener('submit', handleSearchSubmit);
    }
}

// Handle link click to load new page dynamically
function handleLinkClick(e) {
    e.preventDefault();  // Prevent default navigation
    const url = this.href;  // Get the target URL
    loadPageContent(url);  // Load the content dynamically
    window.history.pushState({}, '', url);  // Update browser URL without full page reload
}

// Handle search form submission
function handleSearchSubmit(e) {
    e.preventDefault(); // Prevent the default form submission

    // Get the search query from the form
    const formData = new FormData(this);
    const query = formData.get('query');
    const url = this.action + '?query=' + encodeURIComponent(query);

    // Fetch the search results via AJAX
    fetch(url)
        .then(response => response.text())
        .then(data => {
            const parser = new DOMParser();
            const doc = parser.parseFromString(data, 'text/html');
            const newContent = doc.querySelector('#content-container').innerHTML;

            // Replace only the content inside #content-container
            document.getElementById('content-container').innerHTML = newContent;

            // Optionally, reinitialize any event listeners to the new content
            attachEventListeners();
        })
        .catch(error => console.error('Error during search:', error));
}

// Initialize everything when the DOM is ready
document.addEventListener('DOMContentLoaded', function () {
    // Attach event listeners for navigation links and search form
    attachEventListeners();

    const audioPlayer = document.getElementById('audio-player');
    const audioSource = document.getElementById('audio-source');

    // Get the logged-in user's username from the data- attribute
    const userDataElement = document.getElementById('user-data');
    const username = userDataElement ? userDataElement.getAttribute('data-username') : 'guest';

    // Unique storage keys for the current user
    const timeKey = `${username}_currentTrackTime`;
    const srcKey = `${username}_currentTrackSrc`;

    // Restore the audio player state on page load
    const savedTime = localStorage.getItem(timeKey);
    const savedTrackSrc = localStorage.getItem(srcKey);

    if (savedTrackSrc) {
        audioSource.src = savedTrackSrc;
        audioPlayer.load();
        if (savedTime) {
            audioPlayer.currentTime = parseFloat(savedTime);
        }
        audioPlayer.play();
    }

    // Persist the audio player state when leaving the page
    window.addEventListener('beforeunload', function () {
        const currentTime = audioPlayer.currentTime;
        const trackSrc = audioSource.src;

        // Save the current track and time to localStorage, specific to the current user
        localStorage.setItem(timeKey, currentTime);
        localStorage.setItem(srcKey, trackSrc);
    });
});
