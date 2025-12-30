<script>
  let { onPlay } = $props();

  function handlePlayClick() {
    onPlay();
  }
</script>

<div class="splash-screen">
  <img src="/idea.svg" alt="Connections Lightbulb" class="splash-icon" />
  <h1 class="splash-title"><b>Connections</b></h1>
  <h3>Create four groups of four categories!</h3>
  <h3><i>Now with Kid Mode for ages 4+!</i></h3>
  <button class="play-button" onclick={handlePlayClick}>Play</button>
</div>

<style>
  .splash-screen {
    position: fixed;
    inset: 0;
    background-color: #ba81c5;
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
    width: 100px;
    height: 100px;
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
