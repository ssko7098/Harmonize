// audioControl.js

export let queue = [];
export let currentIndex = 0;

export function playAudio(url) {
    const audioPlayer = document.getElementById('audio-player');
    const audioSource = document.getElementById('audio-source');

    currentIndex = 0;
    queue.length = 0;
    queue.push(url);
    console.log("Current song index:", currentIndex);
    console.log('Queue:', queue);

    // Check if the audio player elements exist
    if (!audioPlayer || !audioSource) {
        console.warn('Audio player or source not found. Cannot play audio.');
        return;
    }

    // Play the selected song
    if (audioSource.src !== url) {
        audioSource.src = url;  // Set the new song URL
        audioPlayer.load();  // Reload the audio player with the new song
    }

    audioPlayer.play().catch(error => {
        console.error('Error trying to play audio:', error);
    });
}

window.playAudio = playAudio;

export function playFromPlaylist(url) {
    const audioPlayer = document.getElementById('audio-player');
    const audioSource = document.getElementById('audio-source');
    const songElements = document.querySelectorAll('.song-table tbody tr a');  // Get all song links in the playlist

    const songUrls = Array.from(songElements).map(songElement => songElement.getAttribute('onclick').match(/'(.*?)'/)[1]);
    
    const clickedSongIndex = songUrls.indexOf(url);
    // Extract clicked song and create the queue
    const clickedSong = songUrls.splice(clickedSongIndex, 1);  // Remove the clicked song from the array
    const shuffledSongs = shuffle(songUrls);  // Shuffle the remaining songs
    queue = clickedSong.concat(shuffledSongs); 

    currentIndex = 0;

    //currentIndex = index;  // Set the current index to the clicked song
    console.log("Current song index:", currentIndex);
    console.log('Queue:', queue);

    // Check if the audio player elements exist
    if (!audioPlayer || !audioSource) {
        console.warn('Audio player or source not found. Cannot play audio.');
        return;
    }

    // Play the selected song
    if (audioSource.src !== url) {
        audioSource.src = url;  // Set the new song URL
        audioPlayer.load();  // Reload the audio player with the new song
    }

    audioPlayer.play().catch(error => {
        console.error('Error trying to play audio:', error);
    });
}

window.playFromPlaylist = playFromPlaylist;

export function playFromQueue(url){
    const audioPlayer = document.getElementById('audio-player');
    const audioSource = document.getElementById('audio-source');

    //currentIndex = index;  // Set the current index to the clicked song
    console.log("Current song index:", currentIndex);
    console.log('Queue:', queue);

    // Check if the audio player elements exist
    if (!audioPlayer || !audioSource) {
        console.warn('Audio player or source not found. Cannot play audio.');
        return;
    }

    // Play the selected song
    if (audioSource.src !== url) {
        audioSource.src = url;  // Set the new song URL
        audioPlayer.load();  // Reload the audio player with the new song
    }

    audioPlayer.play().catch(error => {
        console.error('Error trying to play audio:', error);
    });
}

function shuffle(array) {
    for (let i = array.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [array[i], array[j]] = [array[j], array[i]];  // Swap elements
    }
    return array;
}

export function setCurrentIndex(index) {
    currentIndex = index;
}

export function getCurrentIndex() {
    return currentIndex;
}

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
