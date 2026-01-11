<script lang="ts">
  import { SOUNDS, RAINBOW_COLORS } from '../lib/wordData';

  let {
    onSoundClick,
    lastClickedSound = null
  }: {
    onSoundClick: (sound: string) => void;
    lastClickedSound?: string | null;
  } = $props();

  let animatingSound = $state<string | null>(null);

  function getSoundColor(index: number): string {
    return RAINBOW_COLORS[index % RAINBOW_COLORS.length];
  }

  function handleClick(sound: string) {
    animatingSound = sound;
    onSoundClick(sound);

    setTimeout(() => {
      animatingSound = null;
    }, 300);
  }

  function isDigraph(sound: string): boolean {
    return sound.length > 1;
  }
</script>

<div class="sound-grid">
  {#each SOUNDS as sound, index}
    <button
      class="sound-button"
      class:animating={animatingSound === sound}
      class:last-clicked={lastClickedSound === sound}
      class:digraph={isDigraph(sound)}
      style="--sound-color: {getSoundColor(index)};"
      onclick={() => handleClick(sound)}
    >
      {sound}
    </button>
  {/each}
</div>

<style>
  .sound-grid {
    display: grid;
    grid-template-columns: repeat(7, 48px);
    gap: 8px;
    padding: 16px;
    justify-content: center;
  }

  .sound-button {
    width: 48px;
    height: 48px;
    border: 3px solid #333;
    border-radius: 12px;
    background: var(--sound-color);
    font-size: 22px;
    font-weight: bold;
    font-family: 'Comic Sans MS', 'Chalkboard', sans-serif;
    color: #333;
    cursor: pointer;
    transition: transform 0.15s, box-shadow 0.15s;
    box-shadow: 3px 3px 0 #333;
    padding: 0;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .sound-button.digraph {
    font-size: 16px;
  }

  .sound-button:hover {
    transform: scale(1.1);
  }

  .sound-button:active,
  .sound-button.animating {
    transform: scale(0.9);
    box-shadow: 1px 1px 0 #333;
  }

  .sound-button.last-clicked {
    border-color: #FF6B6B;
    border-width: 4px;
  }

  @media (max-width: 400px) {
    .sound-grid {
      grid-template-columns: repeat(6, 44px);
      gap: 6px;
      padding: 12px;
    }

    .sound-button {
      width: 44px;
      height: 44px;
      font-size: 18px;
    }

    .sound-button.digraph {
      font-size: 14px;
    }
  }
</style>
