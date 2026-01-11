<script lang="ts">
  import {
    getAvailableVoices,
    getSelectedVoice,
    setSelectedVoice,
    speakWord,
    getVoiceDisplayName,
    isEnglishVoice
  } from '../lib/textToSpeech';

  let {
    isOpen,
    onClose
  }: {
    isOpen: boolean;
    onClose: () => void;
  } = $props();

  let voices = $derived(getAvailableVoices());
  let selectedVoiceName = $state<string | null>(null);

  // Initialize selected voice name when modal opens
  $effect(() => {
    if (isOpen) {
      const current = getSelectedVoice();
      selectedVoiceName = current?.name ?? null;
    }
  });

  // Filter to English voices only, then sort by name
  let sortedVoices = $derived(
    [...voices]
      .filter(v => isEnglishVoice(v))
      .sort((a, b) => getVoiceDisplayName(a).localeCompare(getVoiceDisplayName(b)))
  );

  function handleVoiceSelect(voice: SpeechSynthesisVoice) {
    setSelectedVoice(voice);
    selectedVoiceName = voice.name;
  }

  function handlePreview(voice: SpeechSynthesisVoice, event: MouseEvent) {
    event.stopPropagation();
    speakWord('Hello!', voice);
  }

  function handleBackdropClick(event: MouseEvent) {
    if (event.target === event.currentTarget) {
      onClose();
    }
  }
</script>

{#if isOpen}
  <div class="modal-backdrop" onclick={handleBackdropClick}>
    <div class="modal">
      <h2 class="modal-title">Choose a Voice!</h2>

      <div class="voice-list">
        {#each sortedVoices as voice}
          <div
            class="voice-item"
            class:selected={selectedVoiceName === voice.name}
            onclick={() => handleVoiceSelect(voice)}
            role="button"
            tabindex="0"
          >
            <span class="voice-check">
              {#if selectedVoiceName === voice.name}
                <span class="checkmark">&#10003;</span>
              {/if}
            </span>
            <span class="voice-name">
              {getVoiceDisplayName(voice)}
            </span>
            <button
              class="preview-button"
              onclick={(e) => handlePreview(voice, e)}
              aria-label="Preview voice"
            >
              &#9654;
            </button>
          </div>
        {/each}
      </div>

      <button class="done-button" onclick={onClose}>
        Done
      </button>
    </div>
  </div>
{/if}

<style>
  .modal-backdrop {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
    padding: 20px;
  }

  .modal {
    background: white;
    border-radius: 24px;
    border: 4px solid #333;
    box-shadow: 8px 8px 0 #333;
    max-width: 400px;
    width: 100%;
    max-height: 80vh;
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }

  .modal-title {
    font-family: 'Comic Sans MS', 'Chalkboard', sans-serif;
    font-size: 1.75rem;
    color: #333;
    text-align: center;
    margin: 0;
    padding: 20px;
    border-bottom: 3px solid #333;
    background: #FFFFBA;
  }

  .voice-list {
    flex: 1;
    overflow-y: auto;
    padding: 12px;
  }

  .voice-item {
    display: flex;
    align-items: center;
    gap: 12px;
    width: 100%;
    padding: 12px 16px;
    margin-bottom: 8px;
    border: 3px solid #333;
    border-radius: 12px;
    background: #f8f8f8;
    cursor: pointer;
    transition: transform 0.15s, background 0.15s;
    font-family: 'Comic Sans MS', 'Chalkboard', sans-serif;
    user-select: none;
    -webkit-user-select: none;
  }

  .voice-item:hover {
    background: #e8e8e8;
    transform: scale(1.02);
  }

  .voice-item.selected {
    background: #BAFFC9;
    border-color: #4CAF50;
  }

  .voice-check {
    width: 24px;
    height: 24px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 18px;
    color: #4CAF50;
  }

  .checkmark {
    font-weight: bold;
  }

  .voice-name {
    flex: 1;
    font-size: 16px;
    color: #333;
    text-align: left;
  }

  .preview-button {
    width: 40px;
    height: 40px;
    border: 2px solid #333;
    border-radius: 50%;
    background: #42A5F5;
    color: white;
    font-size: 14px;
    cursor: pointer;
    transition: transform 0.15s, background 0.15s;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .preview-button:hover {
    background: #1E88E5;
    transform: scale(1.1);
  }

  .preview-button:active {
    transform: scale(0.9);
  }

  .done-button {
    margin: 16px;
    padding: 16px 32px;
    border: 4px solid #333;
    border-radius: 16px;
    background: #4CAF50;
    color: white;
    font-family: 'Comic Sans MS', 'Chalkboard', sans-serif;
    font-size: 1.25rem;
    font-weight: bold;
    cursor: pointer;
    transition: transform 0.15s;
    box-shadow: 4px 4px 0 #333;
  }

  .done-button:hover {
    transform: scale(1.05);
  }

  .done-button:active {
    transform: scale(0.95);
    box-shadow: 2px 2px 0 #333;
  }
</style>
