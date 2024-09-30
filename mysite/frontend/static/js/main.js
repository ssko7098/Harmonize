// main.js
import { attachEventListeners } from './eventHandlers.js';
import { restoreAudioState, persistAudioState } from './audioControl.js';

document.addEventListener('DOMContentLoaded', function () {
    attachEventListeners();
    restoreAudioState();

    window.addEventListener('beforeunload', persistAudioState);
});
