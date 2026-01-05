<script>
  let { onPlay } = $props();

  function handlePlayClick() {
    onPlay();
  }

  function handleKidModeClick() {
    onPlay(true);
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
  <h3><i>Now with Kid Mode for ages 4+!</i></h3>
  <button class="play-button" onclick={handlePlayClick}>Play</button>
  <button class="kid-mode-button" onclick={handleKidModeClick}>Kid Mode</button>
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
    padding: 0.75rem 1rem;
    border: none;
    border-radius: 32px;
    cursor: pointer;
    transition: all 0.2s;
    width: 200px;
  }

  .play-button:hover {
    background-color: #333;
    transform: scale(1.05);
  }

  .play-button:active {
    transform: scale(0.95);
  }

  .kid-mode-button {
    background: linear-gradient(90deg, 
      #ffb3ba 0%, 
      #ffcc99 16.67%, 
      #ffffba 33.33%, 
      #baffc9 50%, 
      #bae1ff 66.67%, 
      #d5b3ff 83.33%, 
      #ffb3ff 100%);
    color: #333;
    font-size: 1.5rem;
    font-weight: bold;
    padding: 0.75rem 1rem;
    border: 2px solid black;
    border-radius: 32px;
    cursor: pointer;
    transition: all 0.2s;
    width: 200px;
  }

  .kid-mode-button:hover {
    transform: scale(1.05);
    filter: brightness(1.1);
  }

  .kid-mode-button:active {
    transform: scale(0.95);
  }
</style>
