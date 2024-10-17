// contentLoader.js
import { attachEventListeners } from './eventHandlers.js'; 

import { attachEventListeners } from './eventHandlers.js';

export function loadPageContent(url) {
    fetch(url)
        .then(response => response.text())
        .then(data => {
            const parser = new DOMParser();
            const doc = parser.parseFromString(data, 'text/html');
            const newContent = doc.querySelector('#content-container').innerHTML;
            document.getElementById('content-container').innerHTML = newContent;

            // Reattach event listeners after the content is loaded
            if (typeof attachEventListeners === 'function') {
                attachEventListeners();
            } else {
                console.error("attachEventListeners is not defined");
            }

        })
        .catch(error => console.log('Error loading content:', error));
}
