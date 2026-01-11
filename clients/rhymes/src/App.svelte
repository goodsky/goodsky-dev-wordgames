<script lang="ts">
  import { onMount } from 'svelte';
  import EmojiButton from './components/EmojiButton.svelte';
  import SoundGrid from './components/SoundGrid.svelte';
  import VoiceSelector from './components/VoiceSelector.svelte';
  import { WORD_ENTRIES, makeRhyme } from './lib/wordData';
  import { initVoices, speakWord } from './lib/textToSpeech';

  let selectedWordIndex = $state(0);
  let lastClickedSound = $state<string | null>(null);
  let displayWord = $state<string | null>(null);
  let showRhyme = $state(false);
  let showVoiceSelector = $state(false);
  let voicesReady = $state(false);

  onMount(async () => {
    await initVoices();
    voicesReady = true;
  });

  function handleEmojiClick(index: number) {
    selectedWordIndex = index;
    displayWord = null;
    showRhyme = false;
    lastClickedSound = null;
  }

  function handleSoundClick(sound: string) {
    const currentEntry = WORD_ENTRIES[selectedWordIndex];
    const newWord = makeRhyme(sound, currentEntry.rhymeSuffix);

    displayWord = newWord;
    showRhyme = true;
    lastClickedSound = sound;

    speakWord(newWord);
  }

  function getCurrentDisplayWord(): string {
    if (displayWord) {
      return displayWord;
    }
    return WORD_ENTRIES[selectedWordIndex].word;
  }
</script>

<main>
  <div class="container">
    <header class="header">
      <h1 class="title">Fun with Rhymes!</h1>
      <button
        class="settings-button"
        onclick={() => showVoiceSelector = true}
        aria-label="Settings"
      >
        <svg viewBox="0 0 24 24" fill="currentColor" width="24" height="24">
          <path d="M19.14,12.94c0.04-0.3,0.06-0.61,0.06-0.94c0-0.32-0.02-0.64-0.07-0.94l2.03-1.58c0.18-0.14,0.23-0.41,0.12-0.61 l-1.92-3.32c-0.12-0.22-0.37-0.29-0.59-0.22l-2.39,0.96c-0.5-0.38-1.03-0.7-1.62-0.94L14.4,2.81c-0.04-0.24-0.24-0.41-0.48-0.41 h-3.84c-0.24,0-0.43,0.17-0.47,0.41L9.25,5.35C8.66,5.59,8.12,5.92,7.63,6.29L5.24,5.33c-0.22-0.08-0.47,0-0.59,0.22L2.74,8.87 C2.62,9.08,2.66,9.34,2.86,9.48l2.03,1.58C4.84,11.36,4.8,11.69,4.8,12s0.02,0.64,0.07,0.94l-2.03,1.58 c-0.18,0.14-0.23,0.41-0.12,0.61l1.92,3.32c0.12,0.22,0.37,0.29,0.59,0.22l2.39-0.96c0.5,0.38,1.03,0.7,1.62,0.94l0.36,2.54 c0.05,0.24,0.24,0.41,0.48,0.41h3.84c0.24,0,0.44-0.17,0.47-0.41l0.36-2.54c0.59-0.24,1.13-0.56,1.62-0.94l2.39,0.96 c0.22,0.08,0.47,0,0.59-0.22l1.92-3.32c0.12-0.22,0.07-0.47-0.12-0.61L19.14,12.94z M12,15.6c-1.98,0-3.6-1.62-3.6-3.6 s1.62-3.6,3.6-3.6s3.6,1.62,3.6,3.6S13.98,15.6,12,15.6z"/>
        </svg>
      </button>
    </header>

    <div class="display-area" class:show-rhyme={showRhyme}>
      <span class="current-emoji">{WORD_ENTRIES[selectedWordIndex].emoji}</span>
      <span class="current-word">{getCurrentDisplayWord()}</span>
    </div>

    <div class="emoji-row">
      {#each WORD_ENTRIES as entry, index}
        <EmojiButton
          {entry}
          isSelected={selectedWordIndex === index}
          onclick={() => handleEmojiClick(index)}
        />
      {/each}
    </div>

    <p class="instruction">
      {#if showRhyme}
        Tap another sound to make more rhymes!
      {:else}
        Tap a sound to change the first sound!
      {/if}
    </p>

    <SoundGrid
      onSoundClick={handleSoundClick}
      {lastClickedSound}
    />
  </div>

  <VoiceSelector
    isOpen={showVoiceSelector}
    onClose={() => showVoiceSelector = false}
  />
</main>

<style>
  :global(body) {
    margin: 0;
    padding: 0;
    font-family: 'Comic Sans MS', 'Chalkboard', 'Marker Felt', sans-serif;
    background: linear-gradient(180deg, #87CEEB 0%, #E0F6FF 100%);
    min-height: 100vh;
  }

  :global(*) {
    box-sizing: border-box;
  }

  main {
    display: flex;
    justify-content: center;
    align-items: flex-start;
    min-height: 100vh;
    padding: 20px;
  }

  .container {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 20px;
    max-width: 600px;
    width: 100%;
  }

  .header {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 100%;
    position: relative;
  }

  .title {
    font-size: 2.5rem;
    color: #333;
    text-shadow: 3px 3px 0 #FFD700;
    margin: 0;
    text-align: center;
  }

  .settings-button {
    position: absolute;
    right: 0;
    background: white;
    border: 3px solid #333;
    border-radius: 50%;
    width: 44px;
    height: 44px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: transform 0.15s;
    box-shadow: 3px 3px 0 #333;
    color: #333;
  }

  .settings-button:hover {
    transform: scale(1.1);
  }

  .settings-button:active {
    transform: scale(0.95);
    box-shadow: 1px 1px 0 #333;
  }

  .display-area {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 8px;
    padding: 20px 40px;
    background: white;
    border: 4px solid #333;
    border-radius: 24px;
    box-shadow: 6px 6px 0 #333;
    transition: background-color 0.3s, transform 0.3s;
  }

  .display-area.show-rhyme {
    background: #FFFFBA;
    transform: scale(1.05);
  }

  .current-emoji {
    font-size: 64px;
    line-height: 1;
  }

  .current-word {
    font-size: 48px;
    font-weight: bold;
    color: #333;
    letter-spacing: 4px;
  }

  .emoji-row {
    display: flex;
    flex-wrap: nowrap;
    overflow-x: auto;
    gap: 12px;
    width: 100%;
    padding: 8px 4px;
    -webkit-overflow-scrolling: touch;
  }

  .instruction {
    font-size: 1.25rem;
    color: #555;
    margin: 0;
    text-align: center;
    background: rgba(255, 255, 255, 0.8);
    padding: 12px 24px;
    border-radius: 16px;
  }

  @media (max-width: 480px) {
    .title {
      font-size: 1.75rem;
    }

    .current-emoji {
      font-size: 48px;
    }

    .current-word {
      font-size: 36px;
      letter-spacing: 2px;
    }

    .instruction {
      font-size: 1rem;
    }
  }
</style>
