const STORAGE_KEY = 'rhymes-selected-voice';

let voices: SpeechSynthesisVoice[] = [];
let selectedVoice: SpeechSynthesisVoice | null = null;
let voicesLoaded = false;

export function initVoices(): Promise<SpeechSynthesisVoice[]> {
  return new Promise((resolve) => {
    if (!('speechSynthesis' in window)) {
      resolve([]);
      return;
    }

    const loadVoices = () => {
      voices = window.speechSynthesis.getVoices();
      voicesLoaded = true;

      // Restore saved voice preference
      const savedVoiceName = localStorage.getItem(STORAGE_KEY);
      if (savedVoiceName) {
        const savedVoice = voices.find(v => v.name === savedVoiceName);
        if (savedVoice) {
          selectedVoice = savedVoice;
        }
      }

      // Default to first English voice if no selection
      if (!selectedVoice && voices.length > 0) {
        const englishVoice = voices.find(v => v.lang.startsWith('en'));
        selectedVoice = englishVoice || voices[0];
      }

      resolve(voices);
    };

    // Some browsers load voices synchronously
    const initialVoices = window.speechSynthesis.getVoices();
    if (initialVoices.length > 0) {
      voices = initialVoices;
      loadVoices();
    } else {
      // Others load asynchronously
      window.speechSynthesis.onvoiceschanged = loadVoices;
    }
  });
}

export function getAvailableVoices(): SpeechSynthesisVoice[] {
  return voices;
}

export function getSelectedVoice(): SpeechSynthesisVoice | null {
  return selectedVoice;
}

export function setSelectedVoice(voice: SpeechSynthesisVoice): void {
  selectedVoice = voice;
  localStorage.setItem(STORAGE_KEY, voice.name);
}

export function speakWord(word: string, voice?: SpeechSynthesisVoice): void {
  if (!('speechSynthesis' in window)) {
    return;
  }

  // Cancel any currently speaking text
  window.speechSynthesis.cancel();

  // Keep only ASCII characters (removes emojis and other Unicode symbols)
  // Lowercase to prevent TTS from spelling out "words" like DAT as D-A-T
  const textToSpeak = word.replace(/[^\x20-\x7E]/g, '').trim().toLowerCase();

  // Only speak if there's text remaining after filtering
  if (textToSpeak) {
    const utterance = new SpeechSynthesisUtterance(textToSpeak);
    utterance.rate = 0.65;
    utterance.pitch = 1.4;
    utterance.volume = 1.0;

    // Use provided voice, selected voice, or default
    const voiceToUse = voice || selectedVoice;
    if (voiceToUse) {
      utterance.voice = voiceToUse;
    }

    window.speechSynthesis.speak(utterance);
  }
}

export function getVoiceDisplayName(voice: SpeechSynthesisVoice): string {
  // Clean up voice names for kid-friendly display
  let name = voice.name;

  // Remove common prefixes/suffixes
  name = name.replace(/^Microsoft /, '');
  name = name.replace(/^Google /, '');
  name = name.replace(/ Online \(Natural\)$/, '');
  name = name.replace(/ \(Enhanced\)$/, '');
  name = name.replace(/ \(Premium\)$/, '');

  return name;
}

export function isEnglishVoice(voice: SpeechSynthesisVoice): boolean {
  return voice.lang.startsWith('en');
}
