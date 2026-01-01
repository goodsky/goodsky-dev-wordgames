export function speakWord(word) {
    if ('speechSynthesis' in window) {
        // Cancel any currently speaking text
        window.speechSynthesis.cancel();
        
        // Keep only ASCII characters (removes emojis and other Unicode symbols)
        const textToSpeak = word.replace(/[^\x20-\x7E]/g, '').trim();
        
        // Only speak if there's text remaining after filtering
        if (textToSpeak) {
            const utterance = new SpeechSynthesisUtterance(textToSpeak);
            utterance.rate = 0.75;  // Slightly slower for kids
            utterance.pitch = 1.5; // Slightly higher pitch
            utterance.volume = 1.0;
            
            window.speechSynthesis.speak(utterance);
        }
    }
    }