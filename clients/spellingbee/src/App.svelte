<script>
  import ReportWord from './ReportWord.svelte';
  import Help from './Help.svelte';
  import SplashScreen from './SplashScreen.svelte';

  // Parse URL parameters for puzzle configuration
  const urlParams = new URLSearchParams(window.location.search);
  const lettersParam = urlParams.get('letters');
  const centerLetterParam = urlParams.get('centerLetter');
  const minWordLengthParam = urlParams.get('minWordLength');

  // Ensure center letter is at index 3 (middle of second row)
  const ensureCenterAtIndex3 = (lettersArray, center) => {
    const filtered = lettersArray.filter(l => l !== center);
    return [...filtered.slice(0, 3), center, ...filtered.slice(3)];
  };

  const calculateMaxPossibleScore = (words, minLength) => {
    return words.reduce((total, word) => {
      if (word.length >= minLength) {
        return total + (word.length === minLength ? 1 : word.length);
      }
      return total;
    }, 0);
  };

  // Game state
  let currentWord = $state('');
  let minWordLength = $state(minWordLengthParam ? parseInt(minWordLengthParam) : 4);
  let foundWords = $state([]);
  let score = $state(0);
  let validWords = $state([]);
  let scoringWords = $derived(
    validWords.filter(word => word.includes(centerLetter))
  );
  let maxPossibleScore = $derived(
    calculateMaxPossibleScore(scoringWords, minWordLength)
  );
  let isLoadingDictionary = $state(true);
  let menuOpen = $state(false);
  let howToPlayOpen = $state(false);
  let kidAssistMode = $state(false);
  let hintMode = $state(false);
  let wordsListExpanded = $state(false);
  let reportModalOpen = $state(false);
  let lastSubmittedWord = $state('');
  let lastWordWasValid = $state(false);
  let showSplashScreen = $state(true);
  
  // Get a random unfound scoring word for Kid Assist mode
  let hintWord = $derived(
    kidAssistMode 
      ? getKidAssistWord()
      : ''
  );  
  
  // Game completion states
  let allWordsFound = $derived(
    scoringWords.length > 0 && foundWords.length === scoringWords.length
  );
  let noPossibleWords = $derived(scoringWords.length === 0 && !isLoadingDictionary);
  
  // Notification system
  let notification = $state({ show: false, message: 'Blank', type: 'error' });
  let notificationTimeout;

  // Puzzle letters - configurable via URL parameters or fetched from server
  // Example: ?letters=ABCDEFG&centerLetter=A
  let centerLetter = $state('');
  let letters = $state([]);

  // Fetch new game from server
  async function fetchNewGame() {
    try {
      const response = await fetch(`/api/newgame?minLength=${minWordLength}`);
      const data = await response.json();
      
      centerLetter = data.centerLetter;
      letters = ensureCenterAtIndex3(data.letters, data.centerLetter);
      validWords = data.validWords;
      isLoadingDictionary = false;
      
      console.log(`New game generated with ${data.stats.wordCount} scoring words`);
      console.log(`Total possible score: ${data.stats.totalScore}`);
      console.log(`Heuristic score: ${data.stats.heuristicScore.toFixed(1)}`);
    } catch (error) {
      console.error('Error fetching new game:', error);
      showNotification('Error loading new game', 'error');
      isLoadingDictionary = false;
    }
  }

  // Fetch valid words from API
  async function fetchDictionary() {
    try {
      const response = await fetch('/api/dictionary', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ letters, minLength: minWordLength })
      });
      const data = await response.json();
      validWords = data.validWords;
      isLoadingDictionary = false;
      console.log(`Loaded ${validWords.length} valid words`);
      console.log(`${scoringWords.length} contain the center letter "${centerLetter}"`);
    } catch (error) {
      console.error('Error fetching dictionary:', error);
      showNotification('Error loading dictionary', 'error');
      isLoadingDictionary = false;
    }
  }

  function getKidAssistWord() {
    return scoringWords.find(word => word.startsWith(currentWord) && !foundWords.includes(word)) || '';
  }

  // Initialize game on mount
  if (lettersParam && centerLetterParam) {
    // Use URL parameters
    const initialLetters = lettersParam.toUpperCase().split('');
    const initialCenter = centerLetterParam.toUpperCase();
    centerLetter = initialCenter;
    letters = ensureCenterAtIndex3(initialLetters, initialCenter);
    fetchDictionary();
  } else {
    // Fetch smart random game from server
    fetchNewGame();
  }

  // Helper function to show notifications
  function showNotification(message, type = 'error', duration = 2000) {
    clearTimeout(notificationTimeout);
    notification = { show: true, message, type };
    notificationTimeout = setTimeout(() => {
      notification = { ...notification, show: false };
    }, duration);
  }

  // Button handlers
  function handleLetterClick(letter) {
    currentWord += letter;
  }

  function handleDelete() {
    currentWord = currentWord.slice(0, -1);
  }

  function handleCycle() {
    // Shuffle the outer letters (keep center fixed at index 3)
    const outer = letters.filter(l => l !== centerLetter);
    const shuffled = outer.sort(() => Math.random() - 0.5);
    letters = [...shuffled.slice(0, 3), centerLetter, ...shuffled.slice(3)];
  }

  function handleHint() {
    const currentUpper = currentWord.toUpperCase();
    
    // Find all scoring words that start with current word
    const matchingWords = scoringWords.filter(word => 
      word.startsWith(currentUpper) && !foundWords.includes(word)
    );
    
    if (matchingWords.length === 0) {
      showNotification('No valid words start with those letters!', 'error');
      return;
    }

    // Get the next letter from a random matching word
    const randomWord = matchingWords[Math.floor(Math.random() * matchingWords.length)];

    if (randomWord === currentUpper) {
      return;
    }
    
    const nextLetter = randomWord[currentWord.length];
    currentWord += nextLetter;
  }

  function handleEnter() {
    const proposedWord = currentWord.trim().toUpperCase();
    currentWord = '';

    if (proposedWord.length < minWordLength) {
      showNotification(`Too short! Words must be at least ${minWordLength} letters.`, 'error');
      return;
    }

    // Check if word already found
    if (foundWords.some(w => w.toUpperCase() === proposedWord)) {
      showNotification('Already found!', 'info');
      return;
    }

    // Check if word is in valid dictionary
    if (!validWords.includes(proposedWord)) {
      lastSubmittedWord = proposedWord;
      lastWordWasValid = false;
      showNotification('Not in word list!', 'error');
      return;
    }

    // Check if word is missing center letter
    if (!proposedWord.includes(centerLetter)) {
      lastSubmittedWord = proposedWord;
      lastWordWasValid = false;
      showNotification(`Must include letter "${centerLetter}"!`, 'error');
      return;
    }

    // Valid word!
    lastSubmittedWord = proposedWord;
    lastWordWasValid = true;
    foundWords = [...foundWords, proposedWord];
    if (proposedWord.length === minWordLength) {
      score += 1;
      showNotification(`Good! +1`, 'success', 800);
    } else {
      score += proposedWord.length;
      showNotification(`Great! +${proposedWord.length}`, 'success', 800);
    }
  }

  function toggleMenu(event) {
    event.stopPropagation();
    menuOpen = !menuOpen;
  }

  function toggleKidAssist() {
    kidAssistMode = !kidAssistMode;
  }

  function toggleHintMode() {
    hintMode = !hintMode;
  }

  function toggleWordsList() {
    wordsListExpanded = !wordsListExpanded;
  }

  function closeMenu() {
    if (menuOpen) {
      menuOpen = false;
    }
  }

  function openHowToPlay() {
    howToPlayOpen = true;
  }

  function closeHowToPlay() {
    howToPlayOpen = false;
  }

  function openReportModal() {
    reportModalOpen = true;
    menuOpen = false;
  }

  function closeReportModal() {
    reportModalOpen = false;
  }

  function handleReportSuccess({ success, message, type }) {
    showNotification(message, type);
  }

  async function shareGame() {
    const lettersParam = letters.filter(l => l !== centerLetter).join('') + centerLetter;
    let url = `${window.location.origin}${window.location.pathname}?letters=${lettersParam}&centerLetter=${centerLetter}`;
    
    // Only add minWordLength if it's not the default
    if (minWordLength !== 4) {
      url += `&minWordLength=${minWordLength}`;
    }
    
    try {
      await navigator.clipboard.writeText(url);
      showNotification('Link copied to clipboard!', 'success', 1500);
    } catch (error) {
      console.error('Failed to copy to clipboard:', error);
      showNotification('Failed to copy link', 'error');
    }
    
    menuOpen = false;
  }

  async function resetPuzzle() {
    // Reset game state
    currentWord = '';
    foundWords = [];
    score = 0;
    menuOpen = false;
    isLoadingDictionary = true;
    
    // Fetch new game from server
    await fetchNewGame();
    
    showNotification('New puzzle!', 'info', 1000);
  }

  function handlePlayClick() {
    showSplashScreen = false;
  }
</script>

<!-- Splash Screen -->
{#if showSplashScreen}
  <SplashScreen onPlay={handlePlayClick} />
{/if}

<!-- Backdrop to close menu when clicking outside -->
{#if menuOpen}
  <div class="menu-backdrop" onclick={closeMenu} onkeydown={closeMenu} role="button" tabindex="-1"></div>
{/if}

<!-- How to Play Modal -->
<Help isOpen={howToPlayOpen} onClose={closeHowToPlay} />

<!-- Report Word Modal -->
<ReportWord 
  isOpen={reportModalOpen} 
  onClose={closeReportModal}
  onSuccess={handleReportSuccess}
  initialWord={lastSubmittedWord}
  initialType={lastWordWasValid ? 'remove' : 'add'}
/>

<main>
  <div class="game-container">
    <!-- Menu bar at top -->
    <div class="header">
      <button 
        class="kid-assist-button" 
        class:active={kidAssistMode}
        onclick={toggleKidAssist}
      >
        Kid Assist
        <span class="status-box">{kidAssistMode ? 'ON' : 'OFF'}</span>
      </button>
      <div class="header-buttons">
        <button class="help-button" onclick={openHowToPlay} title="How to Play">ⓘ</button>
        <button class="menu-button" onclick={toggleMenu}>☰</button>
      </div>
      {#if menuOpen}
        <div class="menu-dropdown">
          <button class="menu-item" onclick={resetPuzzle}>New Puzzle</button>
          <button class="menu-item" onclick={shareGame}>Share Game</button>
          <button class="menu-item" onclick={openReportModal}>Report Word</button>
          <button class="menu-item" class:active={hintMode} onclick={toggleHintMode}>
            Hint Mode: <span class="status-box">{hintMode ? 'ON' : 'OFF'}</span>
          </button>
        </div>
      {/if}
    </div>

    <!-- Found words section -->
    <div class="found-words">
      <div class="found-words-header">
      </div>
      <div class="words-list-container">
        <div class="words-list" class:expanded={wordsListExpanded}>
          {#each foundWords.toReversed() as word}
            <span class="word-chip">{word}</span>
          {/each}
        </div>
        {#if foundWords.length > 0}
          <button class="expand-button" onclick={toggleWordsList}>
            {wordsListExpanded ? '▼' : '▶'}
          </button>
        {/if}
      </div>
      <div class="score-progress">
        <div class="progress-bar">
          <div class="progress-line"></div>
          <div 
            class="progress-marker" 
            style="left: calc(30px + {maxPossibleScore > 0 ? (score / maxPossibleScore) : 0} * (100% - 60px))"
          >{score}</div>
        </div>
      </div>
    </div>

    <!-- Spacer to push game elements to bottom -->
    <div style="flex-grow: 1; min-height: 0;"></div>

    <!-- Game elements wrapper -->
    <div class="game-elements">
      <!-- Notification message -->
      <div 
      class="notification" 
      class:visible={notification.show || allWordsFound}
      class:error={notification.type === 'error'}
      class:success={notification.type === 'success' || allWordsFound}
      class:info={notification.type === 'info'}
    >
      {allWordsFound ? 'Puzzle Complete!' : notification.message}
    </div>

    <!-- Current word display -->
    <div class="current-word" class:complete={kidAssistMode && hintWord && currentWord.length === hintWord.length}>
      {#if allWordsFound}
        <span class="congrats">🎉 Congratulations! 🎉</span>
      {:else if noPossibleWords}
        <span class="apology">😕 Sorry, no valid words for these letters. Please start a new puzzle.</span>
      {:else if kidAssistMode && hintWord}
        {#each hintWord.split('') as letter, i}
          <span class:ghost={i >= currentWord.length} class:center-letter={letter === centerLetter}>
            {i < currentWord.length ? currentWord[i] : letter}
          </span>
        {/each}
      {:else if currentWord}
        {#each currentWord.split('') as letter}
          <span class:center-letter={letter === centerLetter}>{letter}</span>
        {/each}
      {:else}
        <span class="cursor">_</span>
      {/if}
    </div>

    <!-- Hexagon buttons (placeholder - we'll make these actual hexagons) -->
    <div class="hexagons">
      <div class="hex-grid">
        {#each letters as letter, i}
          <button
            class="hex-button {letter === centerLetter ? 'center' : ''}"
            onclick={() => handleLetterClick(letter)}
            disabled={allWordsFound || noPossibleWords}
          >
            {letter}
          </button>
        {/each}
      </div>
    </div>

    <!-- Control buttons -->
    <div class="controls">
      <button class="delete" onclick={handleDelete} disabled={allWordsFound || noPossibleWords}>Delete</button>
      <button onclick={handleCycle} disabled={allWordsFound || noPossibleWords}><img src="/cycle.svg" alt="Cycle" /></button>
      {#if hintMode}
        <button class="hint" onclick={handleHint} disabled={allWordsFound || noPossibleWords}>💡</button>
      {/if}
      <button class="enter" onclick={handleEnter} disabled={allWordsFound || noPossibleWords}>Enter</button>
    </div>
    </div>

    <!-- Spacer to push game elements to bottom -->
    <div style="flex-grow: 1.0; min-height: 0;"></div>
  </div>
</main>

<style>
  main {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100vh;
    height: 100dvh; /* Dynamic viewport height for mobile browsers */
    background-color: #f5f5f5;
    overflow: hidden;
  }

  .menu-backdrop {
    position: fixed;
    inset: 0;
    z-index: 50;
  }

  .game-container {
    max-width: 600px;
    width: 100%;
    height: 100%;
    padding: 1rem;
    display: flex;
    flex-direction: column;
    overflow-y: auto;
  }

  .header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
    position: relative;
    flex-shrink: 0;
  }

  .kid-assist-button {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    background: white;
    border: 2px solid #ddd;
    border-radius: 8px;
    padding: 0.5rem 0.75rem;
    cursor: pointer;
    transition: all 0.2s;
    font-size: 0.9rem;
  }

  .kid-assist-button:hover {
    background: #f0f0f0;
  }

  .kid-assist-button.active {
    background: #ffd43b;
    color: #333;
    border-color: #fcc419;
  }

  .status-box {
    background: rgba(0, 0, 0, 0.1);
    padding: 0.2rem 0.5rem;
    border-radius: 4px;
    font-size: 0.75rem;
    font-weight: bold;
    min-width: 32px;
    text-align: center;
  }

  .kid-assist-button.active .status-box {
    background: rgba(255, 255, 255, 0.3);
  }

  .header-buttons {
    display: flex;
    gap: 0.5rem;
    align-items: center;
  }

  .help-button {
    background: white;
    border: 2px solid #ddd;
    border-radius: 8px;
    font-size: 1.5rem;
    width: 48px;
    height: 48px;
    cursor: pointer;
    transition: all 0.2s;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #333;
  }

  .help-button:hover {
    background: #f0f0f0;
    transform: scale(1.05);
  }

  .menu-button {
    background: white;
    border: 2px solid #ddd;
    border-radius: 8px;
    font-size: 1.5rem;
    width: 48px;
    height: 48px;
    cursor: pointer;
    transition: all 0.2s;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .menu-button:hover {
    background: #f0f0f0;
    transform: scale(1.05);
  }

  .menu-dropdown {
    position: absolute;
    top: 56px;
    right: 0;
    background: white;
    border: 2px solid #ddd;
    border-radius: 8px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    min-width: 150px;
    z-index: 100;
  }

  .menu-item {
    display: block;
    width: 100%;
    padding: 0.75rem 1rem;
    border: none;
    background: white;
    text-align: left;
    cursor: pointer;
    font-size: 1rem;
    transition: background 0.2s;
  }

  .menu-item:hover {
    background: #f0f0f0;
  }

  .menu-item.active {
    background: #ffd43b;
    color: #333;
  }

  .menu-item.active:hover {
    background: #fcc419;
  }

  .menu-item:first-child {
    border-radius: 6px 6px 0 0;
  }

  .menu-item:last-child {
    border-radius: 0 0 6px 6px;
  }

  .found-words {
    background: white;
    padding: 1rem;
    border-radius: 8px;
    margin-bottom: 0.5rem;
    flex-shrink: 0;
  }

  .game-elements {
    flex-shrink: 0;
  }

  .found-words-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .words-list-container {
    position: relative;
    margin: 0.25rem 0 1rem 0;
  }

  .expand-button {
    position: absolute;
    top: 50%;
    right: 0;
    transform: translateY(-50%);
    background: white;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 1rem;
    cursor: pointer;
    padding: 0.5rem;
    color: #666;
    transition: all 0.2s;
    z-index: 10;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  }

  .expand-button:hover {
    color: #333;
  }

  .words-list {
    display: flex;
    flex-wrap: nowrap;
    gap: 0.5rem;
    min-height: 40px;
    max-height: 40px;
    overflow-x: auto;
    overflow-y: hidden;
    align-items: center;
    line-height: 1;
    transition: max-height 0.3s ease-out;
    scrollbar-width: none; /* Firefox */
    -ms-overflow-style: none; /* IE/Edge */
  }

  .words-list::-webkit-scrollbar {
    display: none; /* Chrome/Safari */
  }

  .words-list.expanded {
    flex-wrap: wrap;
    max-height: 500px;
    overflow-y: auto;
    overflow-x: hidden;
  }

  .word-chip {
    background: #e0e0e0;
    padding: 0.25rem 0.75rem;
    border-radius: 12px;
    font-size: 0.9rem;
    line-height: 1.4;
  }

  .score-progress {
    margin-top: 1rem;
  }

  .progress-bar {
    position: relative;
    height: 40px;
    display: flex;
    align-items: center;
    padding: 0 10px;
  }

  .progress-line {
    position: absolute;
    left: 10px;
    right: 10px;
    height: 2px;
    background: #ddd;
  }

  .progress-marker {
    position: absolute;
    left: 0;
    width: 36px;
    height: 36px;
    border-radius: 50%;
    background: #ffd43b;
    border: 3px solid white;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
    transform: translateX(-18px);
    transition: left 0.3s ease-out;
    z-index: 2;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: bold;
    font-size: 0.9rem;
    color: black;
  }

  .current-word {
    background: white;
    padding: 1rem;
    text-align: center;
    font-size: 2rem;
    font-weight: bold;
    border-radius: 8px;
    margin-bottom: 1.5rem;
    min-height: 50px;
    color: #333;
    user-select: none;
    cursor: default;
    flex-shrink: 0;
  }

  .current-word.complete {
    color: #51cf66;
  }

  .current-word .ghost {
    opacity: 0.25;
  }

  .current-word .ghost.center-letter {
    color: inherit;
  }

  .current-word .center-letter {
    color: #ffd43b;
  }

  .current-word.complete .center-letter {
    color: #51cf66;
  }

  .current-word .cursor {
    animation: blink 1s step-end infinite;
  }

  .current-word .congrats,
  .current-word .apology {
    font-size: clamp(1rem, 4vw, 1.2rem);
  }

  .current-word .congrats {
    color: #51cf66;
  }

  .current-word .apology {
    color: #ff6b6b;
  }

  .current-word .congrats,
  .current-word .apology {
    font-size: clamp(1rem, 4vw, 1.2rem);
  }

  .current-word .congrats {
    color: #51cf66;
  }

  .current-word .apology {
    color: #ff6b6b;
  }

  @keyframes blink {
    0%, 50% {
      opacity: 1;
    }
    50.01%, 100% {
      opacity: 0;
    }
  }

  .notification {
    color: white;
    padding: 1rem;
    text-align: center;
    font-size: 1.2rem;
    font-weight: bold;
    border-radius: 8px;
    margin-bottom: 1rem;
    opacity: 0;
    transition: opacity 0.3s ease-out;
    pointer-events: none;
    flex-shrink: 0;
  }

  .notification.visible {
    opacity: 1;
  }

  .notification.error {
    background: #ff6b6b;
  }

  .notification.success {
    background: #51cf66;
  }

  .notification.info {
    background: #4dabf7;
  }

  .hexagons {
    margin-bottom: 1.5rem;
    flex-shrink: 0;
  }

  .hex-grid {
    display: grid;
    grid-template-columns: repeat(3, min(100px, 20vw));
    grid-template-rows: repeat(3, min(100px, 20vw));
    gap: 0.75rem;
    max-width: 350px;
    margin: 0 auto;
    justify-content: center;
    align-items: center;
  }

  /* Honeycomb pattern - centered rows */
  /* Top row - 2 buttons offset to center */
  .hex-button:nth-child(1) { 
    grid-column: 1;
    grid-row: 1;
    transform: translateX(50%);
  }
  .hex-button:nth-child(2) { 
    grid-column: 2;
    grid-row: 1;
    transform: translateX(50%);
  }
  
  /* Middle row - 3 buttons fill all columns */
  .hex-button:nth-child(3) { grid-column: 1; grid-row: 2; }
  .hex-button:nth-child(4) { grid-column: 2; grid-row: 2; }
  .hex-button:nth-child(5) { grid-column: 3; grid-row: 2; }
  
  /* Bottom row - 2 buttons offset to center */
  .hex-button:nth-child(6) { 
    grid-column: 1;
    grid-row: 3;
    transform: translateX(50%);
  }
  .hex-button:nth-child(7) { 
    grid-column: 2;
    grid-row: 3;
    transform: translateX(50%);
  }

  .hex-button {
    width: 100%;
    height: 100%;
    font-size: 2rem;
    font-weight: bold;
    border: 2px solid #ddd;
    border-radius: 8px;
    background: white;
    cursor: pointer;
    transition: all 0.2s;
  }

  .hex-button:hover {
    background: #f0f0f0;
  }
  
  .hex-button:active {
    background: #e0e0e0;
  }

  .hex-button.center {
    background: #ffd700;
    border-color: #ffb700;
  }

  .hex-button:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .hex-button:disabled:hover {
    background: white;
  }

  .hex-button.center:disabled:hover {
    background: #ffd700;
  }

  .controls {
    display: flex;
    gap: 1rem;
    justify-content: center;
    flex-shrink: 0;
  }

  .controls button {
    padding: 0.75rem 1.25rem;
    font-size: 1rem;
    border: 2px solid #ddd;
    border-radius: 32px;
    background: white;
    cursor: pointer;
    transition: all 0.2s;
  }

  .controls button:hover {
    background: #f0f0f0;
  }

  .controls button.delete {
    background: #ff6b6b;
    border-color: #fa5252;
    color: black;

  }

  .controls button.delete:hover {
    background: #fa5252;
  }

  .controls button.enter {
    background: #51cf66;
    border-color: #40c057;
    color: black;
  }

  .controls button.enter:hover {
    background: #40c057;
  }

  .controls button.hint {
    font-size: 1.5rem;
    padding: 0.75rem 1rem;
  }

  .controls button.hint:hover {
    background: #fcc419;
  }

  .controls button:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .controls button.delete:disabled:hover {
    background: #ff6b6b;
  }

  .controls button.enter:disabled:hover {
    background: #51cf66;
  }

  /* Responsive adjustments for small screens */
  @media (max-height: 750px) {
    .game-container {
      padding: 0.25rem;
    }

    .header {
      margin-bottom: 0.25rem;
    }

    .found-words {
      padding: 0.5rem;
      margin-bottom: 0.25rem;
    }

    .current-word {
      padding: 0.5rem;
      margin-bottom: 0.5rem;
      min-height: 40px;
      font-size: clamp(1.5rem, 10vw, 2.0rem);
    }

    .notification {
      padding: 0.5rem;
      margin-bottom: 0.25rem;
    }

    .hexagons {
      margin-bottom: 0.5rem;
    }

    .hex-grid {
      gap: 0.35rem;
      max-width: 250px;
      grid-template-columns: repeat(3, min(70px, 18vw));
      grid-template-rows: repeat(3, min(70px, 18vw));
    }
  }

  @media (max-width: 360px) {
    .game-container {
      padding: 0.25rem;
    }

    .hex-grid {
      max-width: 220px;
      grid-template-columns: repeat(3, min(60px, 30vw));
      grid-template-rows: repeat(3, min(60px, 30vw));
    }
  }

</style>
