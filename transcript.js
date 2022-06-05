window.onload = () => {
    const playbackSpeedSection = document.querySelector('.playback-speed-section');
    playbackSpeedSection.style.display = 'inline-block';

    const audio = document.querySelector('audio');
    const playbackSpeedLinks = document.querySelectorAll('.play-audio');
    for (const link of playbackSpeedLinks) {

        link.addEventListener('click', (e) => {
            e.preventDefault();
            audio.playbackRate = link.dataset.playbackSpeed;
            audio.play();
        });
    }
}
