<script>
  let { onPlay } = $props();

  function handlePlayClick() {
    onPlay();
  }
</script>

<div class="splash-screen">
  <div class="splash-icon">
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" fill="currentColor">
      <rect x="5" y="5" width="25" height="25" rx="2"/>
      <rect x="35" y="5" width="25" height="25" rx="2"/>
      <rect x="65" y="5" width="25" height="25" rx="2"/>
      <rect x="5" y="35" width="25" height="25" rx="2"/>
      <rect x="35" y="35" width="25" height="25" rx="2"/>
      <rect x="65" y="35" width="25" height="25" rx="2"/>
      <rect x="5" y="65" width="25" height="25" rx="2"/>
      <rect x="35" y="65" width="25" height="25" rx="2"/>
      <rect x="65" y="65" width="25" height="25" rx="2"/>
    </svg>
  </div>
  <h1 class="splash-title"><b>Crossword</b></h1>
  <h3>Fill the grid with words from the clues!</h3>
  <button class="play-button" onclick={handlePlayClick}>Play</button>
</div>

<style>
  .splash-screen {
    position: fixed;
    inset: 0;
    background-color: #e3f2fd;
    color: black;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    gap: 1.5rem;
    z-index: 1000;
    font-family: Georgia, serif;
    text-align: center;
    padding-bottom: 20vh;
  }

  .splash-title {
    font-size: 3rem;
    margin: 0 2rem;
    font-family: Baskerville, 'Libre Baskerville', serif;
    font-weight: 1000;
  }

  .splash-screen h3 {
    margin: 0 3rem;
  }

  .splash-icon {
    width: 128px;
    height: 128px;
    color: #333;
  }

  .splash-icon svg {
    width: 100%;
    height: 100%;
  }

  .play-button {
    background-color: black;
    color: white;
    font-size: 1.5rem;
    padding: 0.75rem 5rem;
    border: none;
    border-radius: 32px;
    cursor: pointer;
    transition: all 0.2s;
  }

  .play-button:hover {
    background-color: #333;
    transform: scale(1.05);
  }

  .play-button:active {
    transform: scale(0.95);
  }
</style>
