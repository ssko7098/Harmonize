// audioControl.js

export function playAudio(url) {
    const audioPlayer = document.getElementById('audio-player');
    const audioSource = document.getElementById('audio-source');

    if (!audioPlayer || !audioSource) {
        console.warn('Audio player or source not found. Cannot play audio.');
        return;
    }

    if (audioSource.src === url) {
        audioPlayer.currentTime = 0;
        audioPlayer.play();
    } else {
        audioSource.src = url;
        audioPlayer.load();
        audioPlayer.play();
    }
}

window.playAudio = playAudio;

export function restoreAudioState() {
    const audioPlayer = document.getElementById('audio-player');
    const audioSource = document.getElementById('audio-source');
    const userDataElement = document.getElementById('user-data');
    const username = userDataElement ? userDataElement.getAttribute('data-username') : 'guest';

    if (!audioPlayer || !audioSource) {
        console.warn('Audio player or source not found. Cannot restore audio state.');
        return;
    }
    
    const timeKey = `${username}_currentTrackTime`;
    const srcKey = `${username}_currentTrackSrc`;

    const savedTime = localStorage.getItem(timeKey);
    const savedTrackSrc = localStorage.getItem(srcKey);

    if (savedTrackSrc) {
        audioSource.src = savedTrackSrc;
        audioPlayer.load();
        if (savedTime) {
            audioPlayer.currentTime = parseFloat(savedTime);
        }

        // Wait for user interaction before playing the audio
        const playButton = document.getElementById('play-button');
        if (playButton) {
            playButton.style.display = 'block'; // Show play button
            playButton.addEventListener('click', () => {
                audioPlayer.play().catch(error => {
                    console.error('Error trying to play audio:', error);
                });
                playButton.style.display = 'none'; // Hide play button after interaction
            });
        }
    }
}

export function persistAudioState() {
    const audioPlayer = document.getElementById('audio-player');
    const audioSource = document.getElementById('audio-source');
    const userDataElement = document.getElementById('user-data');
    const username = userDataElement ? userDataElement.getAttribute('data-username') : 'guest';

    if (!audioPlayer || !audioSource) {
        console.warn('Audio player or source not found. Cannot persist audio state.');
        return;
    }

    const timeKey = `${username}_currentTrackTime`;
    const srcKey = `${username}_currentTrackSrc`;

    const currentTime = audioPlayer.currentTime;
    const trackSrc = audioSource.src;

    localStorage.setItem(timeKey, currentTime);
    localStorage.setItem(srcKey, trackSrc);
}
