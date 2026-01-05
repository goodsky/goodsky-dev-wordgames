<script>
  
</script>

<main class="main-container">
  <div class="main-header">
    <h1>Word Games <span style="font-family: Comic Sans MS, cursive, sans-serif; white-space: nowrap; color: #555;">with Kids</span></h1>
  </div>
  <div class="game-buttons-container">
    <a href="/crossword" class="game-button play-crossword">
      <div class="game-button-text">
        <div class="header-crossword">Crossword</div>
        <div class="game-button-description">Fill in the crossword puzzle!</div>
        <div class="game-button-callout"><i>Try Kid Mode for ages 4+!</i></div>
      </div>
      <div class="play-crossword-icon"></div>
    </a>
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
  transition: transform 0.15s ease;
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
  background: linear-gradient(90deg, 
    #ffb3ba 0%, 
    #ffcc99 16.67%, 
    #ffffba 33.33%, 
    #baffc9 50%, 
    #bae1ff 66.67%, 
    #d5b3ff 83.33%, 
    #ffb3ff 100%);
  padding: 0.3rem 0.5rem;
  border-radius: 8px;
  width: fit-content;
  font-weight: bold;
}

.play-crossword {
  background-color: white;
  color: #333;
  border: 2px solid #333;
}

.play-crossword:hover {
  background-color: #9b9b9b;
  size: larger;
}

.header-crossword {
  font-size: 1.5rem;
  font-weight: bold;
  font-family: 'Times New Roman', Times, serif;
}

.play-crossword-icon {
    width: 100px;
    height: 100px;
    align-self: center;
    justify-self: center;
    background-color: #333;
    mask: url('/grid.svg') no-repeat center;
    -webkit-mask: url('/grid.svg') no-repeat center;
    mask-size: contain;
    -webkit-mask-size: contain;
}

.play-spellingbee {
  background-color: #ffd700;
  color: black;
  border: 2px solid #333;
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
  border: 2px solid #333;
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
    mask: url('/idea.svg') no-repeat center;
    -webkit-mask: url('/idea.svg') no-repeat center;
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
