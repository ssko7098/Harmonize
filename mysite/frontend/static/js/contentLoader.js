// contentLoader.js
import { attachEventListeners } from './eventHandlers.js'; 

export function loadPageContent(url) {
    fetch(url)
        .then(response => response.text())
        .then(data => {
            const parser = new DOMParser();
            const doc = parser.parseFromString(data, 'text/html');
            const newContent = doc.querySelector('#content-container').innerHTML;
            document.getElementById('content-container').innerHTML = newContent;

            // Reattach event listeners for dynamic content
            attachEventListeners();
        })
        .catch(error => console.log('Error loading content:', error));
}
