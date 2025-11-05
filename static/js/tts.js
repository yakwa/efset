class TextToSpeech {
  constructor() {
    this.synth = window.speechSynthesis;
    this.utterance = null;
    this.currentButton = null;
    this.audioContext = null;
    this.analyser = null;
    this.isPlaying = false;
    this.initialize();
  }

  initialize() {
    // Vérifier la compatibilité du navigateur
    if (!('speechSynthesis' in window)) {
      console.warn('La synthèse vocale n\'est pas supportée par votre navigateur');
      return;
    }

    // Initialiser les écouteurs d'événements
    document.addEventListener('click', (e) => {
      const button = e.target.closest('[data-tts-text]');
      if (button) {
        e.preventDefault();
        this.toggleSpeech(button);
      }
    });

    // Mettre à jour l'interface utilisateur lorsque la synthèse vocale change d'état
    this.synth.onvoiceschanged = () => {
      this.updateVoices();
    };
  }

  toggleSpeech(button) {
    const text = button.getAttribute('data-tts-text');
    const isPlaying = button.classList.contains('playing');

    // Arrêter la lecture en cours si nécessaire
    if (this.isPlaying) {
      this.stopSpeech();
      
      // Si c'est le même bouton, on arrête simplement
      if (this.currentButton === button) {
        return;
      }
    }

    // Démarrer une nouvelle lecture
    this.currentButton = button;
    this.speak(text);
  }

  speak(text) {
    if (!text) {
      console.warn('Aucun texte à lire');
      return;
    }

    // Créer une nouvelle instance de SpeechSynthesisUtterance
    this.utterance = new SpeechSynthesisUtterance(text);
    
    // S'assurer que les voix sont chargées
    const voices = this.synth.getVoices();
    if (voices.length === 0) {
      // Attendre que les voix soient chargées
      console.log('Chargement des voix...');
      setTimeout(() => this.speak(text), 100);
      return;
    }
    
    // Configurer les paramètres de la voix
    this.configureVoice(this.utterance);
    
    console.log('Lecture du texte:', text.substring(0, 50) + '...');
    console.log('Voix utilisée:', this.utterance.voice?.name || 'Voix par défaut');
    
    // Gérer les événements
    this.utterance.onstart = () => {
      console.log('Lecture démarrée');
      this.isPlaying = true;
      this.currentButton.classList.add('playing');
      this.currentButton.classList.add('loading');
      this.currentButton.setAttribute('aria-label', 'Arrêter la lecture');
      
      // Initialiser la visualisation audio si disponible
      this.initAudioVisualization();
    };

    this.utterance.onend = () => {
      console.log('Lecture terminée');
      this.stopSpeech();
    };
    
    this.utterance.onerror = (event) => {
      console.error('Erreur de lecture:', event.error);
      this.stopSpeech();
    };

    // Lancer la lecture
    this.synth.speak(this.utterance);
  }

  stopSpeech() {
    if (this.synth.speaking) {
      this.synth.cancel();
    }
    
    if (this.currentButton) {
      this.currentButton.classList.remove('playing', 'loading');
      this.currentButton.setAttribute('aria-label', 'Écouter le texte');
      this.currentButton = null;
    }
    
    this.isPlaying = false;
    
    // Arrêter la visualisation audio
    if (this.audioContext && this.audioContext.state !== 'closed') {
      this.audioContext.close();
      this.audioContext = null;
    }
  }

  configureVoice(utterance) {
    // Essayer de trouver une voix anglaise pour les questions de listening
    const voices = this.synth.getVoices();
    
    // Détecter si le texte est en anglais (simple heuristique)
    const text = utterance.text.toLowerCase();
    const isEnglish = text.includes('the ') || text.includes(' is ') || text.includes(' are ') || 
                      text.includes('i am ') || text.includes('welcome ') || text.includes('please ');
    
    let selectedVoice = null;
    
    if (isEnglish) {
      // Chercher une voix anglaise
      const englishVoices = voices.filter(voice => 
        voice.lang.startsWith('en-') || voice.lang === 'en'
      );
      
      if (englishVoices.length > 0) {
        // Préférer les voix US ou UK
        const preferredVoices = englishVoices.filter(v => 
          v.lang === 'en-US' || v.lang === 'en-GB'
        );
        selectedVoice = preferredVoices.length > 0 ? preferredVoices[0] : englishVoices[0];
      }
    } else {
      // Chercher une voix française
      const frenchVoices = voices.filter(voice => 
        voice.lang.startsWith('fr') || voice.lang.startsWith('fr-')
      );
      
      if (frenchVoices.length > 0) {
        const preferredVoices = frenchVoices.filter(v => v.localService);
        selectedVoice = preferredVoices.length > 0 ? preferredVoices[0] : frenchVoices[0];
      }
    }
    
    // Utiliser la voix sélectionnée ou la première disponible
    utterance.voice = selectedVoice || voices[0];
    
    // Configurer les paramètres de la voix
    utterance.rate = 0.9;  // Légèrement plus lent pour une meilleure compréhension
    utterance.pitch = 1.0;
    utterance.volume = 1.0;
    utterance.lang = isEnglish ? 'en-US' : 'fr-FR';
  }

  updateVoices() {
    // Mettre à jour les voix disponibles si nécessaire
    if (this.utterance) {
      this.configureVoice(this.utterance);
    }
  }

  initAudioVisualization() {
    // Créer un contexte audio pour la visualisation
    if (!this.audioContext) {
      this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
      this.analyser = this.audioContext.createAnalyser();
      this.analyser.fftSize = 256;
      
      // Créer un nœud de destination audio
      const destination = this.audioContext.createMediaStreamDestination();
      
      // Connecter l'analyseur à la destination
      this.analyser.connect(destination);
      
      // Mettre à jour la visualisation
      this.updateVisualization();
    }
  }

  updateVisualization() {
    if (!this.analyser) return;
    
    const bufferLength = this.analyser.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);
    
    const draw = () => {
      if (!this.analyser) return;
      
      this.analyser.getByteFrequencyData(dataArray);
      
      // Mettre à jour la barre de progression ou l'effet visuel
      if (this.currentButton) {
        const progressBar = this.currentButton.querySelector('.audio-progress-bar');
        if (progressBar) {
          // Calculer le niveau moyen de fréquence
          let sum = 0;
          for (let i = 0; i < bufferLength; i++) {
            sum += dataArray[i];
          }
          const average = sum / bufferLength;
          
          // Mettre à jour la largeur de la barre de progression
          progressBar.style.width = `${average}%`;
        }
      }
      
      // Continuer l'animation si nécessaire
      if (this.isPlaying) {
        requestAnimationFrame(draw);
      }
    };
    
    draw();
  }
}

// Initialiser la synthèse vocale lorsque le DOM est chargé
document.addEventListener('DOMContentLoaded', () => {
  window.textToSpeech = new TextToSpeech();
  
  // Ajouter des boutons de lecture à côté de chaque élément avec la classe 'text-to-speech'
  document.querySelectorAll('.text-to-speech').forEach(element => {
    const text = element.textContent.trim();
    const container = document.createElement('span');
    container.className = 'text-with-audio';
    
    // Créer le bouton de lecture
    const button = document.createElement('button');
    button.className = 'tts-button';
    button.setAttribute('data-tts-text', text);
    button.setAttribute('aria-label', 'Écouter le texte');
    button.setAttribute('title', 'Écouter le texte');
    button.innerHTML = '\
      <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">\
        <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon>\
        <path d="M15.54 8.46a5 5 0 0 1 0 7.07"></path>\
        <path d="M19.07 4.93a10 10 0 0 1 0 14.14"></path>\
      </svg>\
      <span class="audio-progress">\
        <span class="audio-progress-bar"></span>\
      </span>\
    ';
    
    // Remplacer le contenu de l'élément par la nouvelle structure
    container.innerHTML = element.innerHTML;
    container.appendChild(button);
    
    // Remplacer l'élément d'origine par le nouveau contenu
    element.replaceWith(container);
  });
});
