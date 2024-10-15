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
    attachNavLinkActiveState();
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