<script>
  
</script>

<main class="main-container">
  <div class="main-header">
    <h1>Word Games</h1>
  </div>
  <div class="game-buttons-container">

    <a href="/spellingbee" class="game-button play-spellingbee">
      <div>
        <h1>Spelling Bee</h1>
        <p>How many words can you spell?</p>
        <p><i>Now with Kid Mode!</i></p>
      </div>
      <img src="/bee-128.png" alt="Bee" class="play-spellingbee-icon" />
    </a>

    <a href="/connections" class="game-button play-connections">
      <div>
        <h1>Connections</h1>
        <p>Create four groups of four categories!</p>
        <p><i>Now with Kid Mode for ages 4+!</i></p>
      </div>
      <div class="play-connections-icon"></div>
    </a>

  </div>
</main>

<style>
.main-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin: 0 auto;
  padding: 1rem;
  max-width: 400px;
}

.main-header {
  position: sticky;
  top: 0;
  background-color: white;
  text-align: center;
  font-family: Georgia, Times, 'Times New Roman', serif;
  margin-bottom: 2rem;
}

.game-buttons-container {
  display: flex;
  flex-direction: column;
  width: 100%;
}

.game-button {
  display: flex;
  flex-direction: row;
  padding: 1rem;
  margin: 1rem 0;
  text-decoration: none;
  border-radius: 16px;
  cursor: pointer;
}

.play-spellingbee {
  background-color: #ffd700;
  color: black;
}

.play-spellingbee-icon {
    width: 100px;
    height: 100px;
    align-self: center;
    justify-self: center;
  }

.play-connections {
  background-color: #ba81c5;
  color: black;
}

.play-connections-icon {
    width: 100px;
    height: 100px;
    align-self: center;
    justify-self: center;
    background-color: #651476;
    mask: url('idea.svg') no-repeat center;
    -webkit-mask: url('idea.svg') no-repeat center;
    mask-size: contain;
    -webkit-mask-size: contain;
  }

</style>
