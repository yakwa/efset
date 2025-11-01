(function(){
  // Timer logic
  const body = document.body;
  const enabled = body.dataset.timerEnabled === 'true';
  let remaining = parseInt(body.dataset.timerSeconds || '0', 10);
  const timerEl = document.getElementById('timer');
  if (enabled && remaining > 0 && timerEl) {
    const form = document.getElementById('question-form');
    const render = () => {
      const m = Math.floor(remaining / 60);
      const s = remaining % 60;
      timerEl.textContent = `Temps restant: ${m}:${s.toString().padStart(2,'0')}`;
    };
    render();
    const iv = setInterval(() => {
      remaining -= 1;
      if (remaining <= 0) {
        clearInterval(iv);
        // Auto submit when time is up
        if (form) form.submit();
      } else {
        render();
      }
    }, 1000);
  }

  // Audio play once restriction
  const audio = document.getElementById('audio-q');
  if (audio) {
    let playedOnce = false;
    audio.addEventListener('ended', () => {
      playedOnce = true;
      audio.controls = false;
    });
    audio.addEventListener('seeking', (e) => {
      if (playedOnce) {
        e.preventDefault();
        audio.currentTime = audio.duration; // jump to end
        audio.pause();
      }
    });
    audio.addEventListener('play', () => {
      if (playedOnce) {
        audio.pause();
      }
    });
  }
})();
