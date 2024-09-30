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
