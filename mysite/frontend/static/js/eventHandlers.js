// eventHandlers.js
import { loadPageContent } from './contentLoader.js';

export function attachEventListeners() {
    document.querySelectorAll('a.nav-link').forEach(link => {
        link.removeEventListener('click', handleLinkClick);
        link.addEventListener('click', handleLinkClick);
    });

    const searchForm = document.getElementById('search-form');
    if (searchForm) {
        searchForm.removeEventListener('submit', handleSearchSubmit);
        searchForm.addEventListener('submit', handleSearchSubmit);
    }

    const uploadForm = document.getElementById('profile-settings-form');
    if (uploadForm) {
        uploadForm.removeEventListener('submit', handleProfileSubmit);
        uploadForm.addEventListener('submit', handleProfileSubmit);
    }
}

function handleLinkClick(e) {
    e.preventDefault();
    const url = this.href;
    loadPageContent(url);
    window.history.pushState({}, '', url);
}

function handleSearchSubmit(e) {
    e.preventDefault();
    const formData = new FormData(this);
    const query = formData.get('query');
    const url = this.action + '?query=' + encodeURIComponent(query);

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