<script lang="ts">
  import type { WordEntry } from '../lib/wordData';
  import { speakWord } from '../lib/textToSpeech';

  let {
    entry,
    isSelected = false,
    onclick
  }: {
    entry: WordEntry;
    isSelected?: boolean;
    onclick: () => void;
  } = $props();

  let isAnimating = $state(false);

  function handleClick() {
    isAnimating = true;
    speakWord(entry.word);
    onclick();

    setTimeout(() => {
      isAnimating = false;
    }, 300);
  }
</script>

<button
  class="emoji-button"
  class:selected={isSelected}
  class:animating={isAnimating}
  style="--button-color: {entry.color};"
  onclick={handleClick}
>
  <span class="emoji">{entry.emoji}</span>
  <span class="word">{entry.word}</span>
</button>

<style>
  .emoji-button {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 8px;
    width: 100px;
    height: 120px;
    border: 4px solid #333;
    border-radius: 20px;
    background: var(--button-color);
    cursor: pointer;
    transition: transform 0.2s, box-shadow 0.2s;
    box-shadow: 4px 4px 0 #333;
    flex-shrink: 0;
  }

  .emoji-button:hover {
    transform: scale(1.05);
  }

  .emoji-button:active,
  .emoji-button.animating {
    transform: scale(0.95);
    box-shadow: 2px 2px 0 #333;
  }

  .emoji-button.selected {
    border-color: #FF6B6B;
    border-width: 6px;
    box-shadow: 6px 6px 0 #FF6B6B;
  }

  .emoji {
    font-size: 48px;
    line-height: 1;
  }

  .word {
    font-size: 18px;
    font-weight: bold;
    font-family: 'Comic Sans MS', 'Chalkboard', sans-serif;
    color: #333;
  }
</style>
