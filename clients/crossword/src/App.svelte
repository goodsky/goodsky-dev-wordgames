<script>
  import { onMount } from "svelte";

  let isLoading = $state(true);
  let gameId = $state(null);
  let rawGrid = $state([]); // 2D array from API: -1 = blocked, 0 = empty, N = clue index
  let clues = $state([]); // Array of clue objects
  let grid = $state([]); // 2D array of cell objects for display
  let userAnswers = $state([]); // 2D array of user input letters
  let currentClueIndex = $state(0); // Index in clues array
  let lastFocusedCell = $state(null); // Track last focused cell: {row, col}
  let showModal = $state(false);
  let isCorrect = $state(false);

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
      if (targetIndex !== -1) {
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

  // Check if the current word is completely filled
  function isCurrentWordComplete() {
    const cells = getCurrentClueCells();
    for (const cell of cells) {
      if (!userAnswers[cell.row][cell.col]) {
        return false;
      }
    }
    return cells.length > 0;
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

  function findNextCell(row, col) {
    // Try next column first
    if (col + 1 < grid[row].length && !grid[row][col + 1].blocked) {
      return { row, col: col + 1 };
    }
    // Try next row
    for (let r = row + 1; r < grid.length; r++) {
      for (let c = 0; c < grid[r].length; c++) {
        if (!grid[r][c].blocked) {
          return { row: r, col: c };
        }
      }
    }
    return null;
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

  function focusCell(row, col) {
    const cell = document.querySelector(`[data-row="${row}"][data-col="${col}"]`);
    if (cell instanceof HTMLElement) {
      cell.focus();
      lastFocusedCell = { row, col };
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

  function handleInput(row, col, event) {
    const value = event.target.value.toUpperCase();
    // Only allow single letters
    if (value.length <= 1 && /^[A-Z]*$/.test(value)) {
      userAnswers[row][col] = value;
      grid[row][col].letter = value;
      
      // Check if word is complete after entering a letter
      if (value.length === 1) {
        // Check if puzzle is complete
        setTimeout(() => checkPuzzle(), 100);
        
        if (isCurrentWordComplete()) {
          // Move to next clue if word is complete
          nextClue();
        } else {
          // Otherwise, advance to next blank cell in the current word
          focusNextBlank();
        }
      }
    } else {
      event.target.value = userAnswers[row][col];
    }
  }

  // Handle cell click - toggle between across/down if clicking same cell
  function handleCellClick(row, col) {
    const isSameCell = lastFocusedCell && lastFocusedCell.row === row && lastFocusedCell.col === col;
    
    if (isSameCell) {
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
    } else {
      // New cell clicked - find a clue for this cell
      updateClueForCell(row, col);
    }
    
    lastFocusedCell = { row, col };
  }

  function handleKeyDown(row, col, event) {
    if (event.key === 'Backspace') {
      event.preventDefault();
      
      if (userAnswers[row][col]) {
        // If current cell has content, clear it
        userAnswers[row][col] = '';
        grid[row][col].letter = '';
      } else {
        // If cell is empty, move to previous cell and clear it
        const prevCell = findPreviousCell(row, col);
        if (prevCell) {
          userAnswers[prevCell.row][prevCell.col] = '';
          grid[prevCell.row][prevCell.col].letter = '';
          updateClueForCell(prevCell.row, prevCell.col);
          focusCell(prevCell.row, prevCell.col);
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
      const nextCell = findNextCell(row, col);
      if (nextCell) {
        updateClueForCell(nextCell.row, nextCell.col);
        focusCell(nextCell.row, nextCell.col);
      }
      event.preventDefault();
    } else if (event.key === 'ArrowLeft') {
      const prevCell = findPreviousCell(row, col);
      if (prevCell) {
        updateClueForCell(prevCell.row, prevCell.col);
        focusCell(prevCell.row, prevCell.col);
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

<main>
  <div class="container">
    {#if isLoading}
      <p>Loading puzzle...</p>
    {:else}
      <div class="game-area">
        <div 
          class="crossword-grid" 
          style="grid-template-columns: repeat({grid[0].length}, 1fr); --grid-cols: {grid[0].length}; --grid-rows: {grid.length};"
          >
            {#each grid as rowCells, rowIndex}
              {#each rowCells as cell, colIndex}
                {#if cell.blocked}
                  <div class="cell blocked"></div>
                {:else}
                  <div class="cell" class:highlighted={isHighlighted(rowIndex, colIndex)}>
                    {#if cell.clueIndex}
                      <span class="clue-number">{cell.clueIndex}</span>
                    {/if}
                    <input
                      type="text"
                      maxlength="1"
                      value={cell.letter}
                      oninput={(e) => handleInput(rowIndex, colIndex, e)}
                      onkeydown={(e) => handleKeyDown(rowIndex, colIndex, e)}
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

        <div class="clue-display">
          <button class="clue-button" onclick={previousClue} aria-label="Previous clue">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <polyline points="15 18 9 12 15 6"></polyline>
            </svg>
          </button>
          <div class="clue-content">
            <div class="clue-label">
              {clues[currentClueIndex]?.index} {clues[currentClueIndex]?.direction}
            </div>
            <div class="clue-text">
              {clues[currentClueIndex]?.clue}
            </div>
          </div>
          <button class="clue-button" onclick={nextClue} aria-label="Next clue">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <polyline points="9 18 15 12 9 6"></polyline>
            </svg>
          </button>
        </div>
      </div>
    {/if}
  </div>

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
    padding: 20px;
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
    overflow: auto;
  }

  .crossword-grid {
    display: grid;
    gap: 0;
    border: none;
    width: 100%;
    max-width: 100%;
    aspect-ratio: var(--grid-cols) / var(--grid-rows);
    flex-shrink: 1;
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

  .cell-input:focus {
    background: #ffffcc;
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

  @media (max-width: 480px) {
    .container {
      padding: 15px;
      border-radius: 0;
    }

    h1 {
      font-size: 20px;
    }

    .clue-display {
      padding: 12px;
      gap: 10px;
    }

    .nav-button {
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
