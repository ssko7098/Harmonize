// eventHandlers.js
import { loadPageContent } from './contentLoader.js';

export function attachEventListeners() {
    document.querySelectorAll('a.nav-link').forEach(link => {
        link.removeEventListener('click', handleLinkClick);
        link.addEventListener('click', handleLinkClick);
    });

    const button = document.getElementById('button');
    if (button) {
        button.removeEventListener('click', handleLinkClick);
        button.addEventListener('click', handleLinkClick);
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

    attachNavLinkActiveState();
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
