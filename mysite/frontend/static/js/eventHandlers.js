// eventHandlers.js
import { loadPageContent } from './contentLoader.js';

import { playAudio, playFromQueue, setCurrentIndex, getCurrentIndex, queue, currentIndex } from './audioControl.js';

export function attachEventListeners() {
    document.querySelectorAll('a.nav-link').forEach(link => {
        link.removeEventListener('click', handleLinkClick);
        link.addEventListener('click', handleLinkClick);
    });

    document.querySelectorAll('a#button').forEach(link => {
        link.removeEventListener('click', handleLinkClick);
        link.addEventListener('click', handleLinkClick);
    });

    const addToQueueButtons = document.querySelectorAll('.add-to-queue'); // Select all buttons with the class "add-to-queue"
    addToQueueButtons.forEach(button => {
        button.addEventListener('click', function() {
            const url = this.dataset.url; // Retrieve the URL from the data-url attribute of the clicked button
            addToQueue(url);
        });
    });
    
    const nextButton = document.getElementById('next-button');
    if (nextButton) {
        nextButton.removeEventListener('click', handleNextClick);
        nextButton.addEventListener('click', handleNextClick);
    }

    const previousButton = document.getElementById('prev-button');
    if (previousButton) {
        previousButton.removeEventListener('click', handlePreviousClick);
        previousButton.addEventListener('click', handlePreviousClick);
    }

    const searchForm = document.getElementById('search-form');
    if (searchForm) {
        searchForm.removeEventListener('submit', handleSearchSubmit);
        searchForm.addEventListener('submit', handleSearchSubmit);
    }

    // For the registration form
    const registerForm = document.getElementById('register-form');
    if (registerForm) {
        registerForm.removeEventListener('submit', handleRegisterSubmit);
        registerForm.addEventListener('submit', handleRegisterSubmit);
    }

    const uploadForm = document.getElementById('profile-settings-form');
    if (uploadForm) {
        uploadForm.removeEventListener('submit', handleProfileSubmit);
        uploadForm.addEventListener('submit', handleProfileSubmit);
    }

    // For the song cover
    const coverInput = document.getElementById('cover_image_file');
    if (coverInput) {
        coverInput.removeEventListener('change', previewCover);
        coverInput.addEventListener('change', previewCover);
    }

    // For the profile picture
    const avatarInput = document.getElementById('avatar_file');
    if (avatarInput) {
        avatarInput.removeEventListener('change', previewAvatar);
        avatarInput.addEventListener('change', previewAvatar);
    }

    document.querySelectorAll('#custom-form').forEach(form => {
        form.removeEventListener('submit', handleFormSubmit);
        form.addEventListener('submit', handleFormSubmit);
    });

    document.querySelectorAll('select#filter').forEach(filter => {
        filter.removeEventListener('change', handleFilter);
        filter.addEventListener('change', handleFilter);
    });

    document.querySelectorAll('#search-bar').forEach(form => {
        form.removeEventListener('submit', handleSearchFilterSubmit);
        form.addEventListener('submit', handleSearchFilterSubmit);
    });

    attachNavLinkActiveState();
}

function handleSearchFilterSubmit(e) {
    e.preventDefault();  // Prevent the default form submission

    const form = e.target;  // Get the form element that triggered the event
    const formData = new FormData(form);  // Collect the form data

    const url = new URL(form.action || window.location.href);  // Build URL with form action or current page
    formData.forEach((value, key) => {
        url.searchParams.set(key, value);  // Add form data as query parameters
    });

    // Send AJAX request for the search results
    fetch(url, {
        method: 'GET',  // Use GET for search queries
        headers: {
            'X-Requested-With': 'XMLHttpRequest',  // Indicate that this is an AJAX request
        },
    })
    .then(response => response.text())
    .then(data => {
        // Update the content-container with the new filtered data
        const parser = new DOMParser();
        const doc = parser.parseFromString(data, 'text/html');
        const newContent = doc.querySelector('#content-container').innerHTML;
        document.getElementById('content-container').innerHTML = newContent;

        // Reattach event listeners to the new content if necessary
        attachEventListeners();
    })
    .catch(error => {
        console.error('Error during AJAX request:', error);
    });
}

function handleFilter(e) {
    e.preventDefault();  // Prevent default form submission

    const form = e.target.form;  // Get the form related to the select element
    const formData = new FormData(form);  // Collect the form data

    const url = new URL(form.action || window.location.href);  // Build URL with form action or current page
    formData.forEach((value, key) => {
        url.searchParams.set(key, value);  // Add form data as query parameters
    });

    // Send AJAX request to filter results
    fetch(url, {
        method: 'GET',  // GET request for filtering
        headers: {
            'X-Requested-With': 'XMLHttpRequest',  // Indicate that this is an AJAX request
        },
    })
    .then(response => response.text())
    .then(data => {
        // Update the content-container with the new filtered data
        const parser = new DOMParser();
        const doc = parser.parseFromString(data, 'text/html');
        const newContent = doc.querySelector('#content-container').innerHTML;
        document.getElementById('content-container').innerHTML = newContent;

        // Reattach event listeners to the new content if necessary
        attachEventListeners();
    })
    .catch(error => {
        console.error('Error during AJAX request:', error);
    });
}

function handleLinkClick(e) {
    e.preventDefault();
    const url = this.href;
    
    // Load content via AJAX and only update #content-container
    loadPageContent(url)
        .then(data => {
            // Update the #content-container without affecting other elements
            document.getElementById('content-container').innerHTML = data;
            attachEventListeners(); // Reattach event listeners to new content
        });

    // Push new URL to the browser history without reloading the page
    window.history.pushState({}, '', url);
}

function addToQueue(url) {
    let currentIndex = getCurrentIndex();

    queue.splice(currentIndex+1, 0, url); // Add the URL in front of the current song
    console.log("Song added to queue:", queue);
}

function handleNextClick(e) {
    e.preventDefault();
    
    let currentIndex = getCurrentIndex(); // Get the current index

    if (currentIndex < queue.length - 1) {  // Check if there is a next song
        setCurrentIndex(currentIndex + 1);  // Use the setter to update the current index
        const nextUrl = queue[getCurrentIndex()];  // Get the next song URL
        console.log("Playing next song, index:", getCurrentIndex());
        playFromQueue(nextUrl);  // Call playAudio for the next song
    } else {
        console.log("You are at the last song in the queue.");
    }
}

function handlePreviousClick(e) {
    e.preventDefault();
    console.log("Playing previous song");
    let currentIndex = getCurrentIndex();  // Get the current index

    if (currentIndex > 0) {  // Check if there is a previous song
        setCurrentIndex(currentIndex - 1);  // Use the setter to update the current index
        const previousUrl = queue[getCurrentIndex()];  // Get the previous song URL
        console.log("Playing previous song, index:", getCurrentIndex());
        playFromQueue(previousUrl);  // Call playAudio for the previous song
    } else {
        console.log("You are at the first song in the queue.");
    }
}

// Function to handle form submission via AJAX
function handleFormSubmit(e) {
    e.preventDefault();  // Prevent the default form submission

    const form = this;
    const url = form.action;  // Form action URL
    const formData = new FormData(form);  // Collect form data

    fetch(url, {
        method: 'POST',  // Use POST for form submissions
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest',  // Indicate this is an AJAX request
        },
    })
    .then(response => response.text())  // Assuming the server returns HTML
    .then(data => {
        // Update the #content-container with the response data
        const parser = new DOMParser();
        const doc = parser.parseFromString(data, 'text/html');
        const newContent = doc.querySelector('#content-container').innerHTML;
        document.getElementById('content-container').innerHTML = newContent;

        // Reattach event listeners for the new content
        attachEventListeners();
    })
    .catch(error => {
        console.error('Error submitting form:', error);
    });
}

function handleSearchSubmit(e) {
    e.preventDefault();
    const formData = new FormData(this);
    const query = formData.get('query');
    const url = this.action + '?query=' + encodeURIComponent(query);

    // Deselect any active nav links/buttons when search form is submitted
    clearActiveNavLinks();

    fetch(url)
        .then(response => response.text())
        .then(data => {
            const parser = new DOMParser();
            const doc = parser.parseFromString(data, 'text/html');
            const newContent = doc.querySelector('#content-container').innerHTML;
            document.getElementById('content-container').innerHTML = newContent;

            attachEventListeners();
        })
        .catch(error => console.error('Error during search:', error));
}

// Handle profile settings form submission (for profile picture and bio updates)
function handleProfileSubmit(e) {
    e.preventDefault();

    const form = this;
    const formData = new FormData(form);
    const url = form.action;
    const messageContainer = document.getElementById('message-container');

    // Clear previous messages
    messageContainer.innerHTML = '';

    // Disable the submit button to prevent multiple submissions
    const submitButton = form.querySelector('button[type="submit"]');
    if (submitButton) {
        submitButton.disabled = true;
    }

    fetch(url, {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest',  // Indicate this is an AJAX request
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            // Display success message
            messageContainer.innerHTML = `<div class="alert alert-success">${data.message}</div>`;
        } else {
            // Display error message
            messageContainer.innerHTML = `<div class="alert alert-danger">Error: ${data.message}</div>`;
            
            if (data.errors) {
                console.log('Form errors:', data.errors);  // Display form validation errors in the console
            }
        }
    })
    .catch(error => {
        console.error('Error during profile update:', error);
        messageContainer.innerHTML = `<div class="alert alert-danger">There was an error updating the profile.</div>`;
    })
    .finally(() => {
        // Re-enable the submit button
        if (submitButton) {
            submitButton.disabled = false;
        }
    });
}

function previewCover() {
    const fileInput = document.getElementById('cover_image_file');
    const preview = document.getElementById('cover-preview');

    if (fileInput.files && fileInput.files[0]) {
        const reader = new FileReader();
        reader.onload = function(e) {
            preview.src = e.target.result;
        };
        reader.readAsDataURL(fileInput.files[0]);
    }
}

function previewAvatar() {
    const fileInput = document.getElementById('avatar_file');
    const preview = document.getElementById('avatar-preview');

    if (fileInput.files && fileInput.files[0]) {
        const reader = new FileReader();
        reader.onload = function(e) {
            preview.src = e.target.result;
        };
        reader.readAsDataURL(fileInput.files[0]);
    }
}

function handleRegisterSubmit(e) {
    e.preventDefault();

    const form = this;
    const formData = new FormData(form);
    const url = form.action;
    const messageContainer = document.getElementById('message-container');

    // Clear previous messages
    messageContainer.innerHTML = '';

    // Disable the submit button to prevent multiple submissions
    const submitButton = form.querySelector('button[type="submit"]');
    if (submitButton) {
        submitButton.disabled = true;
    }

    // Submit the form via AJAX
    fetch(url, {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest',  // Indicate this is an AJAX request
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            // Display success message
            messageContainer.innerHTML = `<div class="alert alert-success">${data.message}</div>`;
        } else if (data.status === 'error') {
            // Display error message and handle form validation errors
            let errorMessages = '';
            for (const [field, errors] of Object.entries(data.errors)) {
                errorMessages += `<p class="alert alert-danger">${errors.join(', ')}</p>`;
            }
            messageContainer.innerHTML = errorMessages;
        }
    })
    .catch(error => {
        console.error('Error during registration:', error);
        messageContainer.innerHTML = `<p class="alert alert-danger">An error occurred. Please try again later.</p>`;
    })
    .finally(() => {
        // Re-enable the submit button
        if (submitButton) {
            submitButton.disabled = false;
        }
    });
}
// New function to manage "active" state of nav links
function attachNavLinkActiveState() {
    const navItems = document.querySelectorAll('.nav-link-btn, .nav-link');

    navItems.forEach(navItem => {
        // Add click event listener to each nav item
        navItem.addEventListener('click', function () {
            // Remove 'active' class from all nav items
            navItems.forEach(item => item.classList.remove('active'));

            // Add 'active' class to the clicked item
            this.classList.add('active');
        });
    });
}

// Function to clear "active" class from nav links and buttons
function clearActiveNavLinks() {
    const navItems = document.querySelectorAll('.nav-link-btn, .nav-link');
    navItems.forEach(item => {
        item.classList.remove('active');
    });
}
