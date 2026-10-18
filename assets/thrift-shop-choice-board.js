/* Local picture communication board. A selection never submits an order. */
(() => {
  'use strict';
  const cards = Array.from(document.querySelectorAll('[data-choice]'));
  const shopCards = Array.from(document.querySelectorAll('.shop-card'));
  const selectionLabel = document.getElementById('selection-label');
  const speakButton = document.getElementById('speak-choice');
  const clearButton = document.getElementById('clear-choice');
  const speechNote = document.getElementById('speech-note');
  const noShopNote = document.getElementById('no-shop-note');
  const speechSupported = Boolean(window.speechSynthesis) && typeof window.SpeechSynthesisUtterance === 'function';
  let selectedChoice = '';
  let selectedLabel = '';
  let utterance = null;
  let speechTimeout = null;

  const defaultSpeechNote = speechSupported
    ? 'Sound is optional. Tap “Say it” to speak the selected words.'
    : 'Speech is not available in this browser. You can show or point to the selected words.';
  speechNote.textContent = defaultSpeechNote;

  function stopSpeech() {
    if (speechTimeout) window.clearTimeout(speechTimeout);
    speechTimeout = null;
    if (speechSupported && utterance) {
      // Ignore cancellation callbacks from a previous choice.
      utterance.onend = null;
      utterance.onerror = null;
      utterance.onstart = null;
      window.speechSynthesis.cancel();
    }
    utterance = null;
    speakButton.textContent = 'Say it';
  }

  function choose(key, label) {
    stopSpeech();
    selectedChoice = key;
    selectedLabel = label;
    cards.forEach(card => card.setAttribute('aria-pressed', String(card.dataset.choice === key && Boolean(key))));
    selectionLabel.textContent = label || 'Tap a card below';
    clearButton.disabled = !key;
    speakButton.disabled = !key || !speechSupported;
    speechNote.textContent = defaultSpeechNote;
  }

  cards.forEach(card => card.addEventListener('click', () => choose(card.dataset.choice, card.dataset.label)));

  clearButton.addEventListener('click', () => {
    choose('', '');
    // The visible status stays in view after Clear disables itself.
    selectionLabel.focus({preventScroll: true});
  });

  document.querySelectorAll('[data-show-choice]').forEach(input => {
    input.addEventListener('change', () => {
      const card = shopCards.find(item => item.dataset.choice === input.dataset.showChoice);
      if (!card) return;
      card.hidden = !input.checked;
      if (card.hidden && selectedChoice === card.dataset.choice) choose('', '');
      noShopNote.hidden = shopCards.some(item => !item.hidden);
    });
  });

  speakButton.addEventListener('click', () => {
    if (!selectedLabel || !speechSupported) return;
    stopSpeech();
    const message = new window.SpeechSynthesisUtterance(selectedLabel);
    utterance = message;
    message.lang = 'en-US';
    message.rate = 0.9;
    // Prefer a local English voice, when the browser exposes one.
    const voices = window.speechSynthesis.getVoices();
    const localVoice = voices.find(voice => voice.localService && /^en[-_]/i.test(voice.lang));
    if (localVoice) message.voice = localVoice;
    message.onstart = () => { if (utterance === message) speakButton.textContent = 'Speaking'; };
    message.onend = () => {
      if (utterance !== message) return;
      stopSpeech();
      speechNote.textContent = defaultSpeechNote;
    };
    message.onerror = () => {
      if (utterance !== message) return;
      stopSpeech();
      speechNote.textContent = 'The voice could not play. Your selected words are still shown above.';
    };
    try {
      window.speechSynthesis.speak(message);
      speechTimeout = window.setTimeout(() => {
        if (utterance !== message) return;
        stopSpeech();
        speechNote.textContent = 'If you did not hear the voice, show or point to the selected words.';
      }, 12000);
    } catch (_) {
      stopSpeech();
      speechNote.textContent = 'The voice could not play. Your selected words are still shown above.';
    }
  });

  document.querySelector('.selection-panel').hidden = false;
  document.getElementById('availability-settings').hidden = false;
  document.querySelector('.mobile-words').hidden = false;

  window.addEventListener('pagehide', stopSpeech);
})();
