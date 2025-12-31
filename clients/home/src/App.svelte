<script>
  
</script>

<main class="main-container">
  <div class="main-header">
    <h1>Word Games <span style="font-family: Comic Sans MS, cursive, sans-serif; white-space: nowrap; color: #555;">with Kids</span></h1>
  </div>
  <div class="game-buttons-container">
    <a href="/spellingbee" class="game-button play-spellingbee">
      <div class="game-button-text">
        <div class="header-spellingbee">Spelling Bee</div>
        <div class="game-button-description">Spell as many words as you can!</div>
        <div class="game-button-callout"><i>Try Kid Mode for ages 4+!</i></div>
      </div>
      <img src="/bee-128.png" alt="Bee" class="play-spellingbee-icon" />
    </a>

    <a href="/connections" class="game-button play-connections">
      <div class="game-button-text">
        <div class="header-connections">Connections</div>
        <div class="game-button-description">Find the categories!</div>
        <div class="game-button-callout"><i>Try Kid Mode for ages 4+!</i></div>
      </div>
      <div class="play-connections-icon"></div>
    </a>
  </div>
  <footer>
      <p>Created by <a href="mailto:goodsky@outlook.com">Skyler Goodell</a></p>
  </footer>
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

.game-button:hover {
  transform: scale(1.03);
}

.game-button:active {
  transform: scale(0.98);
}

.game-button-text {
  flex: 1;
}

.game-button-description {
  margin-top: 0.5rem;
}

.game-button-callout {
  margin-top: 0.5rem;
  font-style: italic;
  color: #333;
  background: rgb(46, 236, 29);
  padding: 0.2rem 0.4rem;
  border-radius: 8px;
  width: fit-content;
}

.play-spellingbee {
  background-color: #ffd700;
  color: black;
  transition: transform 0.15s ease;
}

.play-spellingbee:hover {
  background-color: #fcda19;
  size: larger;
}

.header-spellingbee {
  font-size: 1.5rem;
  font-weight: bold;
  font-family: 'Gill Sans', 'Gill Sans MT', Calibri, 'Trebuchet MS', sans-serif
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

.header-connections {
  font-size: 1.5rem;
  font-weight: bold;
  font-family:'Courier New', Courier, monospace
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

footer {
  position: absolute;
  bottom: 10px;
  font-size: 0.8rem;
  font-family: Arial, Helvetica, sans-serif;
  color: #333;
}

</style>
