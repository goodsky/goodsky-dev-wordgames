<script>
  let { onPlay } = $props();

  function handlePlayClick() {
    onPlay();
  }
</script>

<div class="splash-screen">
  <img src="/bee-128.png" alt="Bee" class="splash-bee" />
  <h1 class="splash-title"><b>Spelling Bee</b></h1>
  <h3>How many words can you make with 7 letters?</h3>
  <h3><i>Now with Kid Assist mode for ages 4+!</i></h3>
  <button class="play-button" onclick={handlePlayClick}>Play</button>
</div>

<style>
  .splash-screen {
    position: fixed;
    inset: 0;
    background-color: #ffd700;
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

  .splash-bee {
    width: 128px;
    height: 128px;
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
