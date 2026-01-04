<script>
  import { onMount } from "svelte";
  import MenuBar from "./MenuBar.svelte";
  import SplashScreen from "./SplashScreen.svelte";
  import ReportIssue from "./ReportIssue.svelte";

  let isLoading = $state(true);
  let gameId = $state(null);
  let rawGrid = $state([]); // 2D array from API: -1 = blocked, 0 = empty, N = clue index
  let clues = $state([]); // Array of clue objects
  let grid = $state([]); // 2D array of cell objects for display
  let userAnswers = $state([]); // 2D array of user input letters
  let currentClueIndex = $state(0); // Index in clues array
  let currentClueVariantIndex = $state([]); // Array tracking clue variant index for each clue
  let lastFocusedCell = $state(null); // Track last focused cell: {row, col}
  let showModal = $state(false);
  let isCorrect = $state(false);
  let showHowToPlay = $state(false);
  let showShareModal = $state(false);
  let shareUrl = $state('');
  let copiedToClipboard = $state(false);
  let showSplashScreen = $state(true);
  let showReportIssue = $state(false);
  let incorrectCells = $state(new Set()); // Cells marked as incorrect from check
  
  // MenuBar state
  let kidMode = $state(false);
  let soundOn = $state(false);

  onMount(() => {
    const params = new URLSearchParams(window.location.search);
    const urlGameId = params.get('id');

    loadGame(urlGameId);

    // Keep focus on grid for mobile keyboard
    const handleVisibilityChange = () => {
      if (!document.hidden && !showModal) {
        setTimeout(focusNextBlank, 100);
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);

    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
    };
  });

  async function loadGame(id) {
    isLoading = true;
    const url = `/api/crossword/newgame${id ? `?id=${id}` : ''}`;

    try {
      const response = await fetch(url);
      if (!response.ok) {
        throw new Error('Failed to load game');
      }

      const data = await response.json();

      gameId = data.id;
      rawGrid = data.grid;
      
      // Sort clues: across first, then by row, then by column
      clues = data.clues.sort((a, b) => {
        // First sort by direction (across before down)
        if (a.direction !== b.direction) {
          return a.direction === 'across' ? -1 : 1;
        }
        // Then by row
        if (a.row !== b.row) {
          return a.row - b.row;
        }
        // Then by column
        return a.col - b.col;
      });
      
      // Initialize clue variant index array (0 for each clue)
      currentClueVariantIndex = new Array(clues.length).fill(0);
      
      buildDisplayGrid(rawGrid);
    } catch (error) {
      console.error('Error loading game:', error);
    } finally {
      isLoading = false;
    }
  }

  function buildDisplayGrid(rawGrid) {
    const rows = rawGrid.length;
    const cols = rawGrid[0]?.length || 0;
    
    const newGrid = [];
    const newAnswers = [];
    
    for (let row = 0; row < rows; row++) {
      newGrid[row] = [];
      newAnswers[row] = [];
      for (let col = 0; col < cols; col++) {
        const cellValue = rawGrid[row][col];
        newGrid[row][col] = {
          blocked: cellValue === -1,
          clueIndex: cellValue > 0 ? cellValue : null,
          letter: ''
        };
        newAnswers[row][col] = '';
      }
    }
    
    grid = newGrid;
    userAnswers = newAnswers;

    setTimeout(focusNextBlank, 0);
  }

  // Get all cells in the current clue for highlighting
  function getHighlightedCells() {
    if (!clues[currentClueIndex]) return new Set();
    
    const clue = clues[currentClueIndex];
    const cells = new Set();
    
    if (clue.direction === 'across') {
      for (let i = 0; i < clue.answer.length; i++) {
        cells.add(`${clue.row}-${clue.col + i}`);
      }
    } else {
      for (let i = 0; i < clue.answer.length; i++) {
        cells.add(`${clue.row + i}-${clue.col}`);
      }
    }
    
    return cells;
  }

  // Check if a cell is highlighted
  function isHighlighted(row, col) {
    const highlightedCells = getHighlightedCells();
    return highlightedCells.has(`${row}-${col}`);
  }

  // Check if all cells are filled
  function isPuzzleFilled() {
    for (let row = 0; row < grid.length; row++) {
      for (let col = 0; col < grid[row].length; col++) {
        if (!grid[row][col].blocked && !userAnswers[row][col]) {
          return false;
        }
      }
    }
    return true;
  }

  // Check if all answers are correct
  function isPuzzleCorrect() {
    for (const clue of clues) {
      const { row, col, direction, answer } = clue;
      for (let i = 0; i < answer.length; i++) {
        const r = direction === 'across' ? row : row + i;
        const c = direction === 'across' ? col + i : col;
        if (userAnswers[r][c] !== answer[i]) {
          return false;
        }
      }
    }
    return true;
  }

  // Check puzzle when it's filled
  function checkPuzzle() {
    if (isPuzzleFilled()) {
      isCorrect = isPuzzleCorrect();
      showModal = true;
    }
  }

  // Find all clues that contain a specific cell
  function findCluesForCell(row, col) {
    return clues.filter((clue, index) => {
      if (clue.direction === 'across') {
        return clue.row === row && col >= clue.col && col < clue.col + clue.answer.length;
      } else {
        return clue.col === col && row >= clue.row && row < clue.row + clue.answer.length;
      }
    });
  }

  // Update the active clue for a given cell
  function updateClueForCell(row, col) {
    const cellClues = findCluesForCell(row, col);
    if (cellClues.length > 0) {
      const currentClue = clues[currentClueIndex];
      
      // If current clue contains this cell, keep it
      const currentContainsCell = cellClues.some(c => c === currentClue);
      if (currentContainsCell) {
        return; // Keep current clue
      }
      
      // Otherwise, prefer the current direction, then across, then any clue
      const currentDirection = currentClue?.direction;
      const sameDirectionClue = cellClues.find(c => c.direction === currentDirection);
      const acrossClue = cellClues.find(c => c.direction === 'across');
      const targetClue = sameDirectionClue || acrossClue || cellClues[0];
      const targetIndex = clues.indexOf(targetClue);
      if (targetIndex !== -1 && targetIndex !== currentClueIndex) {
        currentClueIndex = targetIndex;
      }
    }
  }

  // Get cells in the current clue word
  function getCurrentClueCells() {
    if (!clues[currentClueIndex]) return [];
    
    const clue = clues[currentClueIndex];
    const cells = [];
    
    if (clue.direction === 'across') {
      for (let i = 0; i < clue.answer.length; i++) {
        cells.push({ row: clue.row, col: clue.col + i });
      }
    } else {
      for (let i = 0; i < clue.answer.length; i++) {
        cells.push({ row: clue.row + i, col: clue.col });
      }
    }
    
    return cells;
  }

  // Get the ghost letter for a cell in kid mode
  function getGhostLetter(row, col) {
    if (!kidMode || !clues[currentClueIndex]) return '';
    
    const clue = clues[currentClueIndex];
    const { row: clueRow, col: clueCol, direction, answer } = clue;
    
    // Check if this cell is part of the current clue
    if (direction === 'across') {
      if (row === clueRow && col >= clueCol && col < clueCol + answer.length) {
        const index = col - clueCol;
        return answer[index];
      }
    } else {
      if (col === clueCol && row >= clueRow && row < clueRow + answer.length) {
        const index = row - clueRow;
        return answer[index];
      }
    }
    
    return '';
  }

  // Check if a cell has a wrong answer in kid mode
  function hasWrongAnswer(row, col) {
    if (!kidMode) return false;
    
    const userLetter = userAnswers[row][col];
    if (!userLetter) return false; // No user input, not wrong
    
    // Check all clues to find the correct answer for this cell
    for (const clue of clues) {
      const { row: clueRow, col: clueCol, direction, answer } = clue;
      
      if (direction === 'across') {
        if (row === clueRow && col >= clueCol && col < clueCol + answer.length) {
          const index = col - clueCol;
          return userLetter !== answer[index];
        }
      } else {
        if (col === clueCol && row >= clueRow && row < clueRow + answer.length) {
          const index = row - clueRow;
          return userLetter !== answer[index];
        }
      }
    }
    
    return false;
  }

  // Check if cell is marked as incorrect from check puzzle
  function isIncorrectCell(row, col) {
    return incorrectCells.has(`${row}-${col}`);
  }

  // Check if the current word is completely filled
  function isCurrentWordComplete() {
    if (!lastFocusedCell) return false;
    
    const cells = getCurrentClueCells();
    
    // Check all cells are filled
    for (const cell of cells) {
      if (!userAnswers[cell.row][cell.col]) {
        return false;
      }
    }
    
    // Check that focus is on the last cell of the word
    if (cells.length === 0) return false;
    const lastCell = cells[cells.length - 1];
    const isOnLastCell = lastFocusedCell.row === lastCell.row && lastFocusedCell.col === lastCell.col;
    
    return isOnLastCell;
  }

  // Find next blank cell in the current clue word
  function findNextBlankInWord() {
    const cells = getCurrentClueCells();
    for (const cell of cells) {
      if (!userAnswers[cell.row][cell.col]) {
        return cell;
      }
    }
    return null;
  }

  // Focus the next blank cell in the current word
  function focusNextBlank() {
    const nextBlank = findNextBlankInWord();
    if (nextBlank) {
      focusCell(nextBlank.row, nextBlank.col);
    }
  }

  // Focus on the next cell in the word (assumes the word is not complete)
  function focusNextCell() {
    if (!lastFocusedCell) return;
    
    const cells = getCurrentClueCells();
    const currentIndex = cells.findIndex(
      cell => cell.row === lastFocusedCell.row && cell.col === lastFocusedCell.col
    );
    
    // If current cell is in the word and not the last cell, move to next
    if (currentIndex !== -1 && currentIndex < cells.length - 1) {
      const nextCell = cells[currentIndex + 1];
      focusCell(nextCell.row, nextCell.col);
    }
  }

  function findPreviousCell(row, col) {
    // Try previous column first
    if (col - 1 >= 0 && !grid[row][col - 1].blocked) {
      return { row, col: col - 1 };
    }
    // Try previous row
    for (let r = row - 1; r >= 0; r--) {
      for (let c = grid[r].length - 1; c >= 0; c--) {
        if (!grid[r][c].blocked) {
          return { row: r, col: c };
        }
      }
    }
    return null;
  }

  function cycleClue() {
    // Cycle through available clues for the current clue object
    const currentClue = clues[currentClueIndex];
    if (currentClue?.clues && currentClue.clues.length > 0) {
      currentClueVariantIndex[currentClueIndex] = (currentClueVariantIndex[currentClueIndex] + 1) % currentClue.clues.length;
      // Trigger reactivity
      currentClueVariantIndex = [...currentClueVariantIndex];
    }
  }

  function previousClue() {
    if (currentClueIndex > 0) {
      currentClueIndex--;
    } else {
      currentClueIndex = clues.length - 1;
    }
    // Focus first blank cell in the new clue
    setTimeout(focusNextBlank, 0);
  }

  function nextClue() {
    if (currentClueIndex < clues.length - 1) {
      currentClueIndex++;
    } else {
      currentClueIndex = 0;
    }
    // Focus first blank cell in the new clue
    setTimeout(focusNextBlank, 0);
  }

  function toggleClueDirection() {
    // Toggle between across and down clues for the last focused cell
    if (!lastFocusedCell) return;
    
    const { row, col } = lastFocusedCell;
    const cellClues = findCluesForCell(row, col);
    const currentClue = clues[currentClueIndex];
    
    // Find the other direction's clue
    const otherClue = cellClues.find(clue => clue.direction !== currentClue.direction);
    
    if (otherClue) {
      // Switch to the other clue
      const otherIndex = clues.indexOf(otherClue);
      if (otherIndex !== -1) {
        currentClueIndex = otherIndex;
      }
    }
    
    // Refocus the cell to maintain input focus
    setTimeout(() => focusCell(row, col), 0);
  }

  function focusCell(row, col) {
    const cell = document.querySelector(`[data-row="${row}"][data-col="${col}"]`);
    if (cell instanceof HTMLElement) {
      cell.focus();
      lastFocusedCell = { row, col };
    }

    if (cell instanceof HTMLInputElement) {
      cell.select();
    }
  }

  function handleCellFocus(row, col, event) {
    // In kid mode, clear wrong answers when focusing
    if (hasWrongAnswer(row, col)) {
      userAnswers[row][col] = '';
      grid[row][col].letter = '';
      event.target.value = '';
      // Trigger reactivity
      userAnswers = userAnswers;
      grid = grid;
    }
    
    // Select the text in the input
    /** @type {HTMLInputElement} */ (event.target).select();
  }

  function refocusGrid() {
    // Refocus on last focused cell or next blank
    if (lastFocusedCell) {
      focusCell(lastFocusedCell.row, lastFocusedCell.col);
    } else {
      focusNextBlank();
    }
  }

  function closeModal() {
    showModal = false;
    // Refocus on grid after closing modal
    setTimeout(focusNextBlank, 100);
  }

  function newGame() {
    showModal = false;
    loadGame(null);
  }

  function handleShareGame() {
    const baseUrl = `${window.location.origin}${window.location.pathname}`;
    shareUrl = `${baseUrl}?id=${gameId}`;
    copiedToClipboard = false;
    showShareModal = true;
    // Refocus grid after modal opens
    setTimeout(refocusGrid, 100);
  }

  function copyShareUrl() {
    navigator.clipboard.writeText(shareUrl).then(() => {
      copiedToClipboard = true;
      setTimeout(() => {
        copiedToClipboard = false;
      }, 2000);
    });
  }

  function closeShareModal() {
    showShareModal = false;
    setTimeout(refocusGrid, 100);
  }

  function handleHowToPlay() {
    showHowToPlay = true;
    setTimeout(refocusGrid, 100);
  }

  function closeHowToPlay() {
    showHowToPlay = false;
    setTimeout(refocusGrid, 100);
  }

  function handleReportIssue() {
    showReportIssue = true;
  }

  function handleCheckPuzzle() {
    const newIncorrectCells = new Set();
    
    // Check all filled cells against correct answers
    for (const clue of clues) {
      const { row, col, direction, answer } = clue;
      for (let i = 0; i < answer.length; i++) {
        const r = direction === 'across' ? row : row + i;
        const c = direction === 'across' ? col + i : col;
        const userLetter = userAnswers[r][c];
        
        // Mark as incorrect if filled and wrong
        if (userLetter && userLetter !== answer[i]) {
          newIncorrectCells.add(`${r}-${c}`);
        }
      }
    }
    
    incorrectCells = newIncorrectCells;
    setTimeout(refocusGrid, 100);
  }

  function clearIncorrectCell(row, col) {
    if (incorrectCells.has(`${row}-${col}`)) {
      incorrectCells.delete(`${row}-${col}`);
      incorrectCells = new Set(incorrectCells); // Trigger reactivity
    }
  }

  function handleKidModeToggle() {
    setTimeout(refocusGrid, 100);
  }

  function handleSoundToggle() {
    setTimeout(refocusGrid, 100);
  }

  function handlePlayClick() {
    showSplashScreen = false;
    // Focus first cell after user tap - this triggers mobile keyboard
    setTimeout(focusNextBlank, 100);
  }

  // Handle cell click - toggle between across/down if clicking same cell
  function handleCellClick(row, col) {
    const isSameCell = lastFocusedCell && lastFocusedCell.row === row && lastFocusedCell.col === col;
    
    if (isSameCell) {
      toggleClueDirection();
    } else {
      // New cell clicked - find a clue for this cell
      updateClueForCell(row, col);
    }
    
    lastFocusedCell = { row, col };
  }

  function handleInput(row, col, event) {
    let value = event.target.value;
    clearIncorrectCell(row, col);
    
    // If multiple chars (selection didn't work), take the last one (newly typed)
    if (value.length > 1) {
      value = value.slice(-1);
    }
    
    // Only process letters
    if (!/^[a-zA-Z]$/.test(value)) {
      // Reset to previous value if not a letter
      event.target.value = grid[row][col].letter || '';
      return;
    }
    
    const letter = value.toUpperCase();
    
    userAnswers[row][col] = letter;
    grid[row][col].letter = letter;
    event.target.value = letter; // Ensure uppercase in input
    
    // Check if puzzle is complete
    setTimeout(() => checkPuzzle(), 100);
    
    if (isCurrentWordComplete()) {
      // Move to next clue if word is complete
      nextClue();
    } else {
      // Otherwise, advance to next cell in the current word
      focusNextCell();
    }
  }

  function handleKeyDown(row, col, event) {
    // Handle special keys only - letter input is handled by oninput
    if (event.key === 'Backspace') {
      event.preventDefault();
      
      if (userAnswers[row][col]) {
        // If current cell has content, clear it
        userAnswers[row][col] = '';
        grid[row][col].letter = '';
        clearIncorrectCell(row, col);
        // Trigger reactivity
        userAnswers = userAnswers;
        grid = grid;
      } else {
        // If cell is empty, move to previous cell and clear it
        const prevCell = findPreviousCell(row, col);
        if (prevCell) {
          userAnswers[prevCell.row][prevCell.col] = '';
          grid[prevCell.row][prevCell.col].letter = '';
          updateClueForCell(prevCell.row, prevCell.col);
          focusCell(prevCell.row, prevCell.col);
          clearIncorrectCell(prevCell.row, prevCell.col);
          // Trigger reactivity
          userAnswers = userAnswers;
          grid = grid;
        }
      }
    } else if (event.key === 'Enter') {
      // Move to next clue
      nextClue();
      event.preventDefault();
    } else if (event.key === 'Tab') {
      // Toggle between across and down clues for this cell
      const cellClues = findCluesForCell(row, col);
      const currentClue = clues[currentClueIndex];
      
      // Find the other direction's clue
      const otherClue = cellClues.find(clue => clue.direction !== currentClue.direction);
      
      if (otherClue) {
        // Switch to the other clue
        const otherIndex = clues.indexOf(otherClue);
        if (otherIndex !== -1) {
          currentClueIndex = otherIndex;
        }
      }
      event.preventDefault();
    } else if (event.key === 'ArrowRight') {
      if (col + 1 < grid[row].length && !grid[row][col + 1].blocked) {
        updateClueForCell(row, col + 1);
        focusCell(row, col + 1);
      }
      event.preventDefault();
    } else if (event.key === 'ArrowLeft') {
      if (col - 1 >= 0 && !grid[row][col - 1].blocked) {
        updateClueForCell(row, col - 1);
        focusCell(row, col - 1);
      }
      event.preventDefault();
    } else if (event.key === 'ArrowDown') {
      if (row + 1 < grid.length && !grid[row + 1][col].blocked) {
        updateClueForCell(row + 1, col);
        focusCell(row + 1, col);
      }
      event.preventDefault();
    } else if (event.key === 'ArrowUp') {
      if (row - 1 >= 0 && !grid[row - 1][col].blocked) {
        updateClueForCell(row - 1, col);
        focusCell(row - 1, col);
      }
      event.preventDefault();
    }
  }
</script>

{#if showSplashScreen}
  <SplashScreen onPlay={handlePlayClick} />
{/if}

<main>
  <div class="container">
    <MenuBar 
      bind:kidMode
      bind:soundOn
      onNewGame={newGame}
      onShareGame={handleShareGame}
      onHowToPlay={handleHowToPlay}
      onReportIssue={handleReportIssue}
      onCheckPuzzle={handleCheckPuzzle}
      onKidModeToggle={handleKidModeToggle}
      onSoundToggle={handleSoundToggle}
    />
    {#if isLoading}
      <p>Loading puzzle...</p>
    {:else}
      <div class="game-area">
        <div class="grid-wrapper">
          <div 
            class="crossword-grid" 
            style="grid-template-columns: repeat({grid[0].length}, 1fr); --grid-cols: {grid[0].length}; --grid-rows: {grid.length};"
          >
            {#each grid as rowCells, rowIndex}
              {#each rowCells as cell, colIndex}
                {#if cell.blocked}
                  <div class="cell blocked"></div>
                {:else}
                  <div class="cell" class:highlighted={isHighlighted(rowIndex, colIndex)} class:wrong-answer={hasWrongAnswer(rowIndex, colIndex)} class:incorrect-cell={isIncorrectCell(rowIndex, colIndex)}>
                    {#if cell.clueIndex}
                      <span class="clue-number">{cell.clueIndex}</span>
                    {/if}
                    <input
                      type="text"
                      maxlength="1"
                      inputmode="text"
                      autocomplete="off"
                      autocorrect="off"
                      autocapitalize="characters"
                      spellcheck="false"
                      value={cell.letter}
                      placeholder={getGhostLetter(rowIndex, colIndex)}
                      oninput={(e) => handleInput(rowIndex, colIndex, e)}
                      onkeydown={(e) => handleKeyDown(rowIndex, colIndex, e)}
                      onfocus={(e) => handleCellFocus(rowIndex, colIndex, e)}
                      onclick={() => handleCellClick(rowIndex, colIndex)}
                      data-row={rowIndex}
                      data-col={colIndex}
                      class="cell-input"
                    />
                  </div>
                {/if}
              {/each}
            {/each}
          </div>
        </div>

        <div class="clue-display">
          <button class="clue-button" onclick={previousClue} onmousedown={(e) => e.preventDefault()} aria-label="Previous clue">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <polyline points="15 18 9 12 15 6"></polyline>
            </svg>
          </button>
          <!-- svelte-ignore a11y_click_events_have_key_events -->
          <!-- svelte-ignore a11y_no_static_element_interactions -->
          <div class="clue-content" onclick={cycleClue} onmousedown={(e) => e.preventDefault()} role="button" tabindex="0">
            <div class="clue-label">
              {clues[currentClueIndex]?.index} {clues[currentClueIndex]?.direction}
            </div>
            <div class="clue-text">
              {clues[currentClueIndex]?.clues?.[currentClueVariantIndex[currentClueIndex]]}
            </div>
          </div>
          <button class="clue-button" onclick={nextClue} onmousedown={(e) => e.preventDefault()} aria-label="Next clue">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <polyline points="9 18 15 12 9 6"></polyline>
            </svg>
          </button>
        </div>
      </div>
    {/if}
  </div>

  {#if showShareModal}
    <!-- svelte-ignore a11y_click_events_have_key_events -->
    <!-- svelte-ignore a11y_no_static_element_interactions -->
    <div class="modal-overlay" onclick={closeShareModal}>
      <!-- svelte-ignore a11y_click_events_have_key_events -->
      <!-- svelte-ignore a11y_no_static_element_interactions -->
      <div class="modal" onclick={(e) => e.stopPropagation()}>
        <h2>Share Game</h2>
        <p>Share this puzzle with a friend:</p>
        <div class="share-url-container">
          <input 
            type="text" 
            readonly 
            value={shareUrl}
            class="share-url-input"
          />
          <button class="copy-btn" onclick={copyShareUrl}>
            {copiedToClipboard ? 'Copied!' : 'Copy'}
          </button>
        </div>
        <div class="modal-buttons">
          <button class="modal-button" onclick={closeShareModal}>
            Close
          </button>
        </div>
      </div>
    </div>
  {/if}

  {#if showHowToPlay}
    <!-- svelte-ignore a11y_click_events_have_key_events -->
    <!-- svelte-ignore a11y_no_static_element_interactions -->
    <div class="modal-overlay" onclick={closeHowToPlay}>
      <!-- svelte-ignore a11y_click_events_have_key_events -->
      <!-- svelte-ignore a11y_no_static_element_interactions -->
      <div class="modal how-to-play-modal" onclick={(e) => e.stopPropagation()}>
        <h2>How to Play</h2>
        <div class="instructions">
          <p><strong>Objective:</strong> Fill in the crossword grid with the correct letters based on the clues.</p>
          
          <p><strong>Controls:</strong></p>
          <ul>
            <li><strong>Click a cell</strong> to focus it. Click again to toggle between across/down clues.</li>
            <li><strong>Type a letter</strong> to fill the cell and advance to the next blank.</li>
            <li><strong>Backspace</strong> to delete and move backward.</li>
            <li><strong>Arrow keys</strong> to navigate the grid.</li>
            <li><strong>Tab</strong> to toggle between across/down at the current cell.</li>
            <li><strong>Enter</strong> to move to the next clue.</li>
          </ul>
          
          <p><strong>Clue Navigation:</strong> Use the arrow buttons at the bottom to switch between clues. Click the clue text to cycle through alternate clues for the same word.</p>
          
          <p><strong>Completion:</strong> The puzzle will automatically check when all cells are filled!</p>
        </div>
        <div class="modal-buttons">
          <button class="modal-button primary" onclick={closeHowToPlay}>Got it!</button>
        </div>
      </div>
    </div>
  {/if}

  {#if showModal}
    <!-- svelte-ignore a11y_click_events_have_key_events -->
    <!-- svelte-ignore a11y_no_static_element_interactions -->
    <div class="modal-overlay" onclick={closeModal}>
      <!-- svelte-ignore a11y_click_events_have_key_events -->
      <!-- svelte-ignore a11y_no_static_element_interactions -->
      <div class="modal" onclick={(e) => e.stopPropagation()}>
        {#if isCorrect}
          <h2>🎉 Congratulations! 🎉</h2>
          <p>You solved the puzzle correctly!</p>
          <div class="modal-buttons">
            <button class="modal-button" onclick={closeModal}>Admire Puzzle</button>
            <button class="modal-button primary" onclick={newGame}>New Game</button>
          </div>
        {:else}
          <h2>Wrong Answer</h2>
          <p>Some answers are incorrect. Keep trying!</p>
          <div class="modal-buttons">
            <button class="modal-button primary" onclick={closeModal}>Keep Trying</button>
          </div>
        {/if}
      </div>
    </div>
  {/if}

  {#if showReportIssue}
    <ReportIssue 
      gameId={gameId}
      clue={clues[currentClueIndex]}
      onClose={() => {
        showReportIssue = false;
        setTimeout(refocusGrid, 100);
      }}
    />
  {/if}
</main>

<style>
  :global(body) {
    margin: 0;
    padding: 0;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
    background-color: #f5f5f5;
  }

  main {
    padding: 20px;
    display: flex;
    justify-content: center;
    height: 100vh;
    height: 100dvh;
    overflow: auto;
  }

  .container {
    background: white;
    border-radius: 8px;
    padding: 20px 0;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    max-width: 500px;
    width: 100%;
    container-type: inline-size;
    display: flex;
    flex-direction: column;
    max-height: 100%;
  }

  .game-area {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 20px;
    flex: 1;
    min-height: 0;
    overflow: hidden;
    padding: 0 20px;
  }

  .grid-wrapper {
    flex: 1;
    min-height: 0;
    width: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .crossword-grid {
    display: grid;
    gap: 0;
    border: none;
    max-width: 100%;
    max-height: 100%;
    aspect-ratio: var(--grid-cols) / var(--grid-rows);
  }

  .cell {
    width: 100%;
    aspect-ratio: 1 / 1;
    border: 1px solid #000;
    box-sizing: border-box;
    position: relative;
    background: white;
    transition: background-color 0.2s;
  }

  .cell.blocked {
    background: #000;
  }

  .cell.highlighted {
    background: #e3f2fd;
  }

  .cell.highlighted .cell-input:not(:focus) {
    background: #e3f2fd;
  }

  .clue-number {
    position: absolute;
    top: 2%;
    left: 2%;
    font-size: clamp(8px, 2.5cqi, 16px);
    font-weight: bold;
    color: #333;
    pointer-events: none;
    z-index: 1;
  }

  .cell-input {
    width: 100%;
    height: 100%;
    border: none;
    text-align: center;
    font-size: clamp(18px, 10cqi, 48px);
    font-weight: bold;
    text-transform: uppercase;
    background: transparent;
    outline: none;
    caret-color: transparent;
    padding: 0;
  }

  .cell-input::selection {
    background: transparent;
  }

  .cell-input:focus {
    background: #ffffcc;
  }

  .cell-input::placeholder {
    color: #d0d0d0;
    opacity: 1;
    font-weight: normal;
  }

  .cell.wrong-answer {
    background-color: #ffcccc !important;
  }

  .cell.wrong-answer .cell-input:not(:focus) {
    background-color: #ffcccc;
  }

  .cell.incorrect-cell {
    background-color: #ffcccc !important;
  }

  .cell.incorrect-cell .cell-input:not(:focus) {
    background-color: #ffcccc;
  }

  .clue-display {
    width: 100%;
    display: flex;
    align-items: center;
    gap: 15px;
    padding: 15px;
    background: #f8f9fa;
    border-radius: 8px;
    border: 1px solid #dee2e6;
    flex-shrink: 0;
  }

  .clue-button {
    flex-shrink: 0;
    width: 40px;
    height: 40px;
    border: 2px solid #333;
    background: white;
    border-radius: 50%;
    font-size: 20px;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.2s;
    user-select: none;
  }

  .clue-button:hover {
    background: #333;
    color: white;
  }

  .clue-button:active {
    transform: scale(0.95);
  }

  .clue-content {
    flex: 1;
    min-width: 0;
    cursor: pointer;
    outline: none;
    -webkit-tap-highlight-color: transparent;
    user-select: none;
  }

  .clue-label {
    font-size: 12px;
    font-weight: bold;
    color: #666;
    text-transform: uppercase;
    margin-bottom: 4px;
  }

  .clue-text {
    font-size: 16px;
    color: #333;
    line-height: 1.4;
  }

  .modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.6);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
  }

  .modal {
    background: white;
    border-radius: 12px;
    padding: 30px;
    max-width: 400px;
    width: 90%;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    text-align: center;
  }

  .how-to-play-modal {
    max-width: 500px;
    text-align: left;
  }

  .how-to-play-modal h2 {
    text-align: center;
  }

  .instructions {
    margin: 0 0 20px 0;
  }

  .instructions p {
    margin: 10px 0;
    text-align: left;
  }

  .instructions ul {
    margin: 10px 0;
    padding-left: 20px;
  }

  .instructions li {
    margin: 8px 0;
    line-height: 1.5;
  }

  .instructions strong {
    color: #333;
  }

  .modal h2 {
    margin: 0 0 15px 0;
    color: #333;
    font-size: 28px;
  }

  .modal p {
    margin: 0 0 25px 0;
    color: #666;
    font-size: 16px;
    line-height: 1.5;
  }

  .modal-buttons {
    display: flex;
    gap: 12px;
    justify-content: center;
    flex-wrap: wrap;
  }

  .modal-button {
    padding: 12px 24px;
    border: 2px solid #333;
    background: white;
    color: #333;
    border-radius: 8px;
    font-size: 16px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
  }

  .modal-button:hover {
    background: #f5f5f5;
  }

  .modal-button.primary {
    background: #333;
    color: white;
  }

  .modal-button.primary:hover {
    background: #555;
  }

  .share-url-container {
    display: flex;
    gap: 0.5rem;
    margin-bottom: 1.5rem;
  }

  .share-url-input {
    flex: 1;
    padding: 0.75rem;
    border-radius: 8px;
    border: 2px solid #ddd;
    background-color: #f5f5f5;
    color: #333;
    font-size: 0.875rem;
    font-family: monospace;
  }

  .copy-btn {
    padding: 0.75rem 1rem;
    border-radius: 8px;
    border: 2px solid #333;
    background-color: #333;
    color: white;
    font-weight: 600;
    cursor: pointer;
    transition: background-color 0.2s;
    white-space: nowrap;
  }

  .copy-btn:hover {
    background-color: #555;
  }

  @media (max-width: 480px) {
    main {
      padding: 0px;
    }

    .container {
      padding: 10px;
      border-radius: 0;
    }

    .clue-display {
      padding: 10px;
      gap: 10px;
    }

    .clue-button {
      width: 35px;
      height: 35px;
      font-size: 18px;
    }

    .clue-text {
      font-size: 14px;
    }

    .modal {
      padding: 20px;
    }

    .modal h2 {
      font-size: 24px;
    }

    .modal p {
      font-size: 14px;
    }

    .modal-button {
      padding: 10px 20px;
      font-size: 14px;
    }
  }
</style>
