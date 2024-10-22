// contentLoader.js
import { attachEventListeners } from './eventHandlers.js'; 

export function loadPageContent(url) {
    return fetch(url)
        .then(response => response.text())
        .then(data => {
            const parser = new DOMParser();
            const doc = parser.parseFromString(data, 'text/html');
            const newContent = doc.querySelector('#content-container').innerHTML;
            document.getElementById('content-container').innerHTML = newContent;
            
            if (typeof attachEventListeners === 'function') {
                attachEventListeners();
            } else {
                console.error('attachEventListeners is not defined');
            }

            return newContent; // Ensure this is returned
        })
        .catch(error => {
            console.error('Error loading content:', error);
            throw error;
        });
}

