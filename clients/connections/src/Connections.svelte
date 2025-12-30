<script>
    import { onMount } from 'svelte';
    import MenuBar from './MenuBar.svelte';
    import SplashScreen from './SplashScreen.svelte';
    import ReportIssue from './ReportIssue.svelte';

    // Difficulty colors matching NYT (yellow, green, blue, purple)
    const DIFFICULTY_COLORS = [
        { bg: '#f9df6d', text: '#000000' }, // Yellow - easiest
        { bg: '#a0c35a', text: '#000000' }, // Green
        { bg: '#b0c4ef', text: '#000000' }, // Blue
        { bg: '#ba81c5', text: '#000000' }  // Purple - hardest
    ];

    // Game state
    let kidMode = $state(false);
    let requestedGameId = $state(null); // Specific game ID requested via URL
    let requestedWords = $state(null); // Specific words requested via URL

    let gameId = $state(null);      // Current game ID
    let words = $state([]);           // Current words in grid (not yet solved)
    let categories = $state([]);      // All category definitions
    let selectedWords = $state([]);   // Currently selected words
    let solvedCategories = $state([]); // Categories that have been solved
    let retriesLeft = $state(4);
    let shakingWords = $state([]);    // Words currently shaking (wrong guess)
    let celebratingWords = $state([]);  // Words celebrating (correct guess)
    let celebrationColor = $state(null); // Color for celebrating words
    let showOneAway = $state(false);     // Show "One away..." notification
    let showSplash = $state(true);       // Show splash screen on first load
    let isLoading = $state(true);
    
    // Game end states
    let gameWon = $state(false);
    let gameLost = $state(false);
    let revealingCategories = $state(false);
    let revealedCount = $state(0);

    // Share modal
    let showShareModal = $state(false);
    let showHowToPlayModal = $state(false);
    let showReportIssueModal = $state(false);
    let shareUrl = $state('');
    let copiedToClipboard = $state(false);

    const MAX_SELECTION = 4;
    const TOTAL_RETRIES = 4;

    // Track if initial load has happened
    let initialLoadDone = false;

    // Computed values
    let canSubmit = $derived(selectedWords.length === MAX_SELECTION);

    // Parse URL parameters on mount
    onMount(() => {
        const params = new URLSearchParams(window.location.search);
        const urlKidMode = params.get('kidmode') === 'true';
        const urlGameId = params.get('game');
        const urlWords = params.get('words');
        
        kidMode = urlKidMode;
        requestedGameId = urlGameId;
        requestedWords = urlWords;
        
        // Clear URL parameters to prevent them from persisting on refresh
        if (window.location.search) {
            const cleanUrl = window.location.origin + window.location.pathname;
            window.history.replaceState({}, '', cleanUrl);
        }
    });

    // Watch for kid mode changes to load a new game
    $effect(() => {
        loadGame(kidMode, requestedGameId, requestedWords);
    });

    async function loadGame(kidMode, specificGameId = null, specificWords = null) {
        console.log('Loading game with kidMode:', kidMode, 'gameId:', specificGameId, 'words:', specificWords);
        isLoading = true;
        
        try {
            let url = `/api/newgame?kidmode=${kidMode}`;
            if (specificGameId) {
                url += `&id=${specificGameId}`;
            }
            if (specificWords) {
                url += `&words=${encodeURIComponent(specificWords)}`;
            }
            
            const response = await fetch(url);
            if (!response.ok) {
                throw new Error('Failed to load game');
            }
            
            const data = await response.json();
            
            // Reset game state
            gameId = data.id;
            words = data.words;
            categories = data.categories;
            selectedWords = [];
            solvedCategories = [];
            retriesLeft = TOTAL_RETRIES;
            shakingWords = [];
            celebratingWords = [];
            celebrationColor = null;
            showOneAway = false;
            gameWon = false;
            gameLost = false;
            revealingCategories = false;
            revealedCount = 0;
        } catch (error) {
            console.error('Error loading game:', error);
        } finally {
            isLoading = false;
            initialLoadDone = true;
        }
    }

    function toggleWordSelection(word) {
        if (gameWon || gameLost || revealingCategories) return;
        
        const isSelected = selectedWords.some(w => w.text === word.text);
        if (isSelected) {
            selectedWords = selectedWords.filter(w => w.text !== word.text);
        } else if (selectedWords.length < MAX_SELECTION) {
            selectedWords = [...selectedWords, word];
            
            // In kid mode, speak the word aloud when selected
            if (kidMode) {
                speakWord(word.text);
            }
        }
    }

    function speakWord(word) {
        if ('speechSynthesis' in window) {
            // Cancel any currently speaking text
            window.speechSynthesis.cancel();
            
            // Keep only ASCII characters (removes emojis and other Unicode symbols)
            const textToSpeak = word.replace(/[^\x20-\x7E]/g, '').trim();
            
            // Only speak if there's text remaining after filtering
            if (textToSpeak) {
                const utterance = new SpeechSynthesisUtterance(textToSpeak);
                utterance.rate = 0.75;  // Slightly slower for kids
                utterance.pitch = 1.5; // Slightly higher pitch
                utterance.volume = 1.0;
                
                window.speechSynthesis.speak(utterance);
            }
        }
    }

    function shuffleWords() {
        const shuffled = [...words];
        for (let i = shuffled.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
        }
        words = shuffled;
    }

    function swapSolvedCategoryWords(category) {
        const categoryWordTexts = category.words.map(w => w.text);
        const categoryWordIndices = words
            .map((w, index) => categoryWordTexts.includes(w.text) ? index : -1)
            .filter((w) => w !== -1);

        console.log('Swapping solved category words:', categoryWordTexts, 'at indices:', categoryWordIndices);

        // Swap the solved category words into the front of the words array
        for (const categoryWordIndex of categoryWordIndices) {
            if (categoryWordIndex < 4) continue; // Already in front
            const firstNonCategoryIndex = words.findIndex((w, index) => !categoryWordTexts.includes(w.text) && index < 4);
            const temp = words[firstNonCategoryIndex];
            words[firstNonCategoryIndex] = words[categoryWordIndex];
            words[categoryWordIndex] = temp;
        }

        return words.slice(4);
    }

    function deselectAll() {
        selectedWords = [];
    }

    function submitGuess() {
        if (!canSubmit) return;

        // Check if selected words match any category
        const matchedCategory = categories.find(cat => {
            const catWords = cat.words;
            const selectedTexts = selectedWords.map(w => w.text);
            const catTexts = catWords.map(w => w.text);
            return selectedTexts.every(t => catTexts.includes(t)) &&
                   catTexts.every(t => selectedTexts.includes(t));
        });

        if (matchedCategory) {
            // Correct guess! Start celebration animation
            const wordsToRemove = [...selectedWords];
            celebratingWords = wordsToRemove;
            celebrationColor = DIFFICULTY_COLORS[matchedCategory.difficulty];
            selectedWords = [];

            // After color fade, add to solved and remove from grid
            setTimeout(() => {
                // Clear celebrating state first
                celebratingWords = [];
                celebrationColor = null;
                
                // Then add category and remove words
                solvedCategories = [...solvedCategories, matchedCategory];
                words = swapSolvedCategoryWords(matchedCategory);

                // In kid mode, announce the category name
                if (kidMode) {
                    speakWord(matchedCategory.name);
                }
                
                // Check for win with delay to let users admire the final board
                if (solvedCategories.length === 4) {
                    setTimeout(() => {
                        gameWon = true;
                    }, 1200);
                }
            }, 1000);
        } else {
            // Wrong guess - check if one away
            const isOneAway = categories.some(cat => {
                const catTexts = cat.words.map(w => w.text);
                const selectedTexts = selectedWords.map(w => w.text);
                const matchCount = selectedTexts.filter(t => catTexts.includes(t)).length;
                return matchCount === 3;
            });

            if (isOneAway) {
                showOneAway = true;
                setTimeout(() => {
                    showOneAway = false;
                }, 2000);
            }

            // Shake and decrement retries
            shakingWords = [...selectedWords];
            
            // Only decrement retries in non-kid mode
            if (!kidMode) {
                retriesLeft--;
                
                if (retriesLeft === 0) {
                    // Game over - reveal categories
                    setTimeout(() => {
                        shakingWords = [];
                        selectedWords = [];
                        startRevealingCategories();
                    }, 600);
                    return;
                }
            }

            // Clear shake after animation
            setTimeout(() => {
                shakingWords = [];
            }, 600);
        }
    }

    function startRevealingCategories() {
        gameLost = true;
        revealingCategories = true;
        revealedCount = 0;
        
        // Reveal unsolved categories one by one
        const unsolvedCategories = categories.filter(
            cat => !solvedCategories.some(solved => solved.name === cat.name)
        );
        
        // Sort by difficulty for reveal order
        unsolvedCategories.sort((a, b) => a.difficulty - b.difficulty);

        let revealIndex = 0;
        const revealInterval = setInterval(() => {
            if (revealIndex < unsolvedCategories.length) {
                const catToReveal = unsolvedCategories[revealIndex];
                solvedCategories = [...solvedCategories, catToReveal];
                const catWordTexts = catToReveal.words.map(w => w.text);
                words = words.filter(w => !catWordTexts.includes(w.text));
                revealedCount++;
                revealIndex++;
            } else {
                clearInterval(revealInterval);
                revealingCategories = false;
            }
        }, 1000);
    }

    function handleNewGame() {
        loadGame(kidMode, null);
    }

    function handleShareGame() {
        const baseUrl = window.location.origin + window.location.pathname;
        const params = new URLSearchParams();
        if (gameId) params.set('game', gameId);
        if (kidMode) params.set('kidmode', 'true');
        
        // Include all words from the current game (both solved and unsolved)
        const allGameWords = [
            ...solvedCategories.flatMap(cat => cat.words.map(w => w.text)),
            ...words.map(w => w.text)
        ];
        if (allGameWords.length > 0) {
            params.set('words', allGameWords.join(','));
        }
        
        shareUrl = params.toString() ? `${baseUrl}?${params.toString()}` : baseUrl;
        copiedToClipboard = false;
        showShareModal = true;
    }

    function handleHowToPlay() {
        showHowToPlayModal = true;
    }

    function handleReportIssue() {
        showReportIssueModal = true;
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
    }

    function closeHowToPlayModal() {
        showHowToPlayModal = false;
    }

    function closeWinModal() {
        gameWon = false;
    }

    function closeLoseModal() {
        gameLost = false;
        revealingCategories = false;
    }

    function handlePlayClick() {
        showSplash = false;
    }

    // Calculate font size based on word length and container size
    function getFontSize(word) {
        const length = word.length;

        // Check if word contains emojis (comprehensive Unicode ranges for emojis)
        const hasEmoji = /[\u{1F300}-\u{1FAFF}]|[\u{2600}-\u{27BF}]|[\u{1F900}-\u{1F9FF}]|[\u{1FA00}-\u{1FAFF}]/u.test(word);
        
        // Use clamp() to scale with container while maintaining readable sizes
        if (hasEmoji && length <= 4) return 'clamp(1.5rem, 4vw, 2.5rem)'; // Emoji-only words
        if (length <= 9) return 'clamp(0.75rem, 2.5vw, 1.0rem)';
        if (length <= 13) return 'clamp(0.625rem, 2.25vw, 0.9rem)';
        if (length <= 18) return 'clamp(0.5rem, 2.0vw, 0.8rem)';
        return 'clamp(0.5rem, 1.75vw, 0.7rem)';
    }
</script>

<div class="game-container">
    {#if showSplash}
        <SplashScreen onPlay={handlePlayClick} />
    {/if}

    <MenuBar 
        bind:kidMode={kidMode}
        onNewGame={handleNewGame} 
        onShareGame={handleShareGame}
        onHowToPlay={handleHowToPlay}
        onReportIssue={handleReportIssue}
    />

    <main class="game-content">
        {#if isLoading}
            <div class="loading">Loading...</div>
        {:else}
            <p class="instructions">Create four groups of four!</p>

            <!-- One Away Notification -->
            {#if showOneAway}
                <div class="one-away-notification">
                    One away...
                </div>
            {/if}

            <!-- Game Grid - unified grid for solved categories and remaining tiles -->
            <div class="game-grid">
                <!-- Solved Categories -->
                {#each solvedCategories as category}
                    <div 
                        class="solved-category"
                        style="background-color: {DIFFICULTY_COLORS[category.difficulty].bg}; color: {DIFFICULTY_COLORS[category.difficulty].text};"
                    >
                        <div class="category-name">{category.name}</div>
                        <div class="category-words">{category.words.map(w => w.text).join(', ')}</div>
                    </div>
                {/each}

                <!-- Remaining Word Tiles -->
                {#each words as word}
                    {@const isSelected = selectedWords.some(w => w.text === word.text)}
                    {@const isCelebrating = celebratingWords.some(w => w.text === word.text)}
                    {@const wordColor = isCelebrating ? '' : (isSelected && word.lightColor ? word.lightColor : word.darkColor)}
                    <button
                        class="word-tile"
                        class:selected={isSelected}
                        class:shaking={shakingWords.some(w => w.text === word.text)}
                        class:celebrating={isCelebrating}
                        style="{isCelebrating && celebrationColor ? `background-color: ${celebrationColor.bg}; color: ${celebrationColor.text};` : ''}{wordColor ? ` color: ${wordColor};` : ''} font-size: {getFontSize(word.text)};"
                        onclick={() => toggleWordSelection(word)}
                        disabled={gameWon || revealingCategories || isCelebrating}
                    >
                        {word.text}
                    </button>
                {/each}
            </div>

            <!-- Retry Indicators (hidden in kid mode) -->
            {#if !kidMode}
                <div class="retries-container">
                    <span class="retries-label">Mistakes remaining:</span>
                    <div class="retries-dots">
                        {#each Array(TOTAL_RETRIES) as _, i}
                            <div 
                                class="retry-dot"
                                class:used={i >= retriesLeft}
                            ></div>
                        {/each}
                    </div>
                </div>
            {/if}

            <!-- Control Buttons -->
            <div class="controls">
                <button 
                    class="control-btn"
                    onclick={shuffleWords}
                    disabled={words.length === 0 || gameWon || revealingCategories}
                >
                    Shuffle
                </button>
                <button 
                    class="control-btn"
                    onclick={deselectAll}
                    disabled={selectedWords.length === 0 || gameWon || revealingCategories}
                >
                    Deselect All
                </button>
                <button 
                    class="control-btn submit-btn"
                    onclick={submitGuess}
                    disabled={!canSubmit || gameWon || revealingCategories}
                >
                    Submit
                </button>
            </div>
        {/if}
    </main>

    <!-- Win Modal -->
    {#if gameWon && !revealingCategories}
        <div class="modal-overlay" role="button" tabindex="0" onclick={closeWinModal} onkeydown={(e) => e.key === 'Enter' && closeWinModal()}>
            <div class="modal" role="dialog" aria-modal="true" tabindex="-1" onclick={(e) => e.stopPropagation()} onkeydown={(e) => e.stopPropagation()}>
                <h2>🎉 Congratulations! 🎉</h2>
                <p>You solved the puzzle!</p>
                <div class="modal-buttons">
                    <button class="modal-btn" onclick={closeWinModal}>
                        Admire Puzzle
                    </button>
                    <button class="modal-btn primary" onclick={handleNewGame}>
                        New Game
                    </button>
                </div>
            </div>
        </div>
    {/if}

    <!-- Lose Modal (shows after reveal) -->
    {#if gameLost && !revealingCategories}
        <div class="modal-overlay" role="button" tabindex="0" onclick={closeLoseModal} onkeydown={(e) => e.key === 'Enter' && closeLoseModal()}>
            <div class="modal" role="dialog" aria-modal="true" tabindex="-1" onclick={(e) => e.stopPropagation()} onkeydown={(e) => e.stopPropagation()}>
                <h2>Game Over</h2>
                <p>Better luck next time!</p>
                <div class="modal-buttons">
                    <button class="modal-btn" onclick={closeLoseModal}>
                        Admire Puzzle
                    </button>
                    <button class="modal-btn primary" onclick={handleNewGame}>
                        Try Again
                    </button>
                </div>
            </div>
        </div>
    {/if}

    <!-- Share Modal -->
    {#if showShareModal}
        <div class="modal-overlay" role="button" tabindex="0" onclick={closeShareModal} onkeydown={(e) => e.key === 'Enter' && closeShareModal()}>
            <div class="modal" role="dialog" aria-modal="true" tabindex="-1" onclick={(e) => e.stopPropagation()} onkeydown={(e) => e.stopPropagation()}>
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
                    <button class="modal-btn" onclick={closeShareModal}>
                        Close
                    </button>
                </div>
            </div>
        </div>
    {/if}

    <!-- How to Play Modal -->
    {#if showHowToPlayModal}
        <div class="modal-overlay" role="button" tabindex="0" onclick={closeHowToPlayModal} onkeydown={(e) => e.key === 'Enter' && closeHowToPlayModal()}>
            <div class="modal how-to-play-modal" role="dialog" aria-modal="true" tabindex="-1" onclick={(e) => e.stopPropagation()} onkeydown={(e) => e.stopPropagation()}>
                <h2>How to Play</h2>
                <div class="instructions-content">
                    <p>Find groups of four items that share something in common.</p>
                    <ul>
                        <li>Select four items and tap 'Submit' to check if your guess is correct.</li>
                        <li>Find all four groups without making 4 mistakes!</li>
                        <li>Category difficulty increases as you play: 🟨 → 🟩 → 🟦 → 🟪</li>
                        <li>Get 3 out of 4 correct? We'll let you know you're "One away..."</li>
                    </ul>
                    <h3>Kid Mode</h3>
                    <p>Turn on <strong>Kid Mode</strong> for a family-friendly experience:</p>
                    <ul>
                        <li>Age-appropriate categories for young players</li>
                        <li>Unlimited guesses - no mistakes counter</li>
                    </ul>
                    <h3>Credits</h3>
                    <ul>
                        <li>Developed by <a href="mailto:goodsky@outlook.com">Skyler Goodell</a></li>
                        <li>Inspired by the New York Times' Connections game</li>
                    </ul>
                </div>
                <div class="modal-buttons">
                    <button class="modal-btn primary" onclick={closeHowToPlayModal}>
                        Got it!
                    </button>
                </div>
            </div>
        </div>
    {/if}

    <!-- Report Issue Modal -->
    {#if showReportIssueModal}
        <ReportIssue 
            gameId={gameId}
            words={[...solvedCategories.flatMap(cat => cat.words), ...words]}
            onClose={() => showReportIssueModal = false}
        />
    {/if}
</div>

<style>
    :global(body) {
        margin: 0;
        padding: 0;
        background-color: #121213;
        color: #ffffff;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
    }

    .game-container {
        height: 100vh;
        height: 100dvh; /* Dynamic viewport height for mobile browsers */
        display: flex;
        flex-direction: column;
    }

    .game-content {
        flex: 1;
        display: flex;
        flex-direction: column;
        align-items: center;
        padding: 1.5rem;
        max-width: 600px;
        margin: 0 auto;
        width: 100%;
        box-sizing: border-box;
    }

    .loading {
        color: #818384;
        font-size: 1.25rem;
        margin-top: 4rem;
    }

    .instructions {
        color: #818384;
        font-size: 1rem;
        margin-bottom: 1.5rem;
    }

    /* One Away Notification */
    .one-away-notification {
        position: fixed;
        top: 5rem;
        left: 50%;
        transform: translateX(-50%);
        background-color: #3a3a3c;
        color: #ffffff;
        padding: 0.75rem 1.5rem;
        border-radius: 8px;
        font-size: 1rem;
        font-weight: 600;
        z-index: 100;
        animation: fadeInOut 2s ease-in;
    }

    @keyframes fadeInOut {
        0% { opacity: 0; transform: translateX(-50%) translateY(-10px); }
        10% { opacity: 1; transform: translateX(-50%) translateY(0); }
        90% { opacity: 1; transform: translateX(-50%) translateY(0); }
        100% { opacity: 0; transform: translateX(-50%) translateY(-10px); }
    }

    /* Unified Game Grid */
    .game-grid {
        width: 100%;
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 0.5rem;
    }

    /* Solved Category Row - spans all 4 columns */
    .solved-category {
        grid-column: 1 / -1;
        /* Calculate aspect ratio: width spans 4 columns + 3 gaps, height equals 1 column width */
        aspect-ratio: 4.01;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        text-align: center;
        box-sizing: border-box;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }

    .category-name {
        font-weight: 700;
        font-size: 1rem;
        text-transform: uppercase;
        margin-bottom: 0.25rem;
    }

    .category-words {
        font-size: 0.875rem;
        text-transform: uppercase;
    }

    /* Word Tiles */
    .word-tile {
        aspect-ratio: 1;
        display: flex;
        align-items: center;
        justify-content: center;
        background-color: #d6d6ca;
        border: none;
        border-radius: 8px;
        color: #000000;
        font-size: 0.875rem;
        font-weight: 600;
        text-transform: uppercase;
        cursor: pointer;
        transition: background-color 0.15s, transform 0.15s;
        padding: 0.25rem;
        text-align: center;
        word-break: break-word;
    }

    .word-tile:hover:not(:disabled) {
        background-color: #c9c3ba;
    }

    .word-tile.selected {
        background-color: #3a3a3c;
        color: #ffffff;
        transform: scale(0.98);
    }

    .word-tile.selected:hover:not(:disabled) {
        background-color: #4a4a4c;
    }

    .word-tile:disabled {
        cursor: default;
    }

    /* Celebrating animation for correct guesses */
    .word-tile.celebrating {
        transition: background-color 0.5s ease-in, color 0.5s ease-in;
    }

    /* Shake animation for wrong guesses */
    .word-tile.shaking {
        animation: shake 0.8s ease-in-out;
    }

    @keyframes shake {
        0%, 100% { transform: translateX(0); }
        10%, 30%, 50%, 70%, 90% { transform: translateX(-4px); }
        20%, 40%, 60%, 80% { transform: translateX(4px); }
    }

    /* Retries */
    .retries-container {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        margin: 1.5rem 0;
    }

    .retries-label {
        color: #818384;
        font-size: 0.875rem;
    }

    .retries-dots {
        display: flex;
        gap: 0.375rem;
    }

    .retry-dot {
        width: 12px;
        height: 12px;
        border-radius: 50%;
        background-color: #5a5a5c;
        transition: background-color 0.3s;
    }

    .retry-dot.used {
        visibility: hidden;
    }

    /* Control Buttons */
    .controls {
        display: flex;
        gap: 0.75rem;
        margin-top: 1.5rem;
    }

    .control-btn {
        padding: 0.75rem 1.5rem;
        border-radius: 24px;
        border: 2px solid #ffffff;
        background-color: transparent;
        color: #ffffff;
        font-size: 0.875rem;
        font-weight: 600;
        cursor: pointer;
        transition: background-color 0.15s, border-color 0.15s, opacity 0.15s;
    }

    .control-btn:hover:not(:disabled) {
        background-color: #3a3a3c;
    }

    .control-btn:disabled {
        opacity: 0.4;
        cursor: default;
    }

    .submit-btn:not(:disabled) {
        background-color: #ffffff;
        color: #121213;
        border-color: #ffffff;
    }

    .submit-btn:hover:not(:disabled) {
        background-color: #e0e0e0;
    }

    /* Modal */
    .modal-overlay {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background-color: rgba(0, 0, 0, 0.7);
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 1rem;
        z-index: 200;
        overflow-y: auto;
    }

    .modal {
        background-color: #1a1a1b;
        border-radius: 12px;
        padding: 1rem;
        max-width: 400px;
        width: 90%;
        margin: 0.75rem;
        text-align: center;
        border: 1px solid #3a3a3c;
    }

    .modal h2 {
        margin: 0 0 1rem 0;
        font-size: 1.5rem;
    }

    .modal p {
        color: #818384;
        margin: 0 0 1.5rem 0;
    }

    .modal-buttons {
        display: flex;
        gap: 0.75rem;
        justify-content: center;
        flex-shrink: 0;
        margin-top: 1rem;
    }

    .modal-btn {
        padding: 0.75rem 1.5rem;
        border-radius: 24px;
        border: 1px solid #5a5a5c;
        background-color: transparent;
        color: #ffffff;
        font-size: 0.875rem;
        font-weight: 600;
        cursor: pointer;
        transition: background-color 0.15s;
    }

    .modal-btn:hover {
        background-color: #3a3a3c;
    }

    .modal-btn.primary {
        background-color: #ffffff;
        color: #121213;
        border-color: #ffffff;
    }

    .modal-btn.primary:hover {
        background-color: #e0e0e0;
    }

    /* Share Modal */
    .share-url-container {
        display: flex;
        gap: 0.5rem;
        margin-bottom: 1.5rem;
    }

    .share-url-input {
        flex: 1;
        padding: 0.75rem;
        border-radius: 8px;
        border: 1px solid #3a3a3c;
        background-color: #121213;
        color: #ffffff;
        font-size: 0.75rem;
    }

    .copy-btn {
        padding: 0.75rem 1rem;
        border-radius: 8px;
        border: none;
        background-color: #538d4e;
        color: #ffffff;
        font-weight: 600;
        cursor: pointer;
        transition: background-color 0.15s;
        white-space: nowrap;
    }

    .copy-btn:hover {
        background-color: #6aaa5f;
    }

    /* How to Play Modal */
    .how-to-play-modal {
        max-width: 500px;
        text-align: left;
        max-height: 85vh;
        display: flex;
        flex-direction: column;
        overflow: hidden;
    }

    .how-to-play-modal h2 {
        text-align: center;
        flex-shrink: 0;
    }

    .how-to-play-modal h3 {
        color: #ffffff;
        font-size: 1.125rem;
        margin: 1.5rem 0 0.75rem 0;
    }

    .instructions-content {
        color: #e0e0e0;
        overflow-y: auto;
        flex: 1;
        padding-right: 0.5rem;
    }

    .instructions-content p {
        color: #e0e0e0;
        margin: 0 0 0.75rem 0;
        line-height: 1.5;
    }

    .instructions-content ul {
        margin: 0 0 1rem 0;
        padding-left: 1.5rem;
        line-height: 1.6;
    }

    .instructions-content li {
        margin-bottom: 0.5rem;
        color: #e0e0e0;
    }

    .instructions-content a {
        color: #ba81c5;
        text-decoration: none;
        border-bottom: 1px solid transparent;
        transition: border-color 0.2s;
    }

    .instructions-content a:hover {
        border-bottom-color: #ba81c5;
    }

    .instructions-content strong {
        color: #ba81c5;
    }
</style>