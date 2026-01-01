<script>
    let {
        kidMode = $bindable(false),
        soundOn = $bindable(false),
        hintMode = $bindable(false),
        onNewGame,
        onShareGame,
        onHowToPlay,
        onReportIssue
    } = $props();
    
    let menuOpen = $state(false);

    function toggleMenu() {
        menuOpen = !menuOpen;
    }

    function handleNewGame() {
        menuOpen = false;
        onNewGame?.();
    }

    function handleShareGame() {
        menuOpen = false;
        onShareGame?.();
    }

    function handleReportIssue() {
        menuOpen = false;
        onReportIssue?.();
    }

    function openHowToPlay() {
        onHowToPlay?.();
    }

    function handleKidModeToggle() {
        kidMode = !kidMode;
    }

    function toggleSoundOn() {
        soundOn = !soundOn;
    }

    function toggleHintMode() {
        hintMode = !hintMode;
    }

    // Close menu when clicking outside
    function handleClickOutside(event) {
        if (menuOpen && !event.target.closest('.menu-container')) {
            menuOpen = false;
        }
    }
</script>

<svelte:window onclick={handleClickOutside} />

<nav class="menu-bar">
    <div class="left-section">
        <button class="go-back-button" onclick={() => window.location.href = 'https://wordgames.goodsky.dev'} aria-label="Go back to home">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-chevron-left-icon lucide-chevron-left">
                <path d="m15 18-6-6 6-6"/>
            </svg>
        </button>
        <button class="kid-mode-button" class:active={kidMode} onclick={handleKidModeToggle}>
            Kid Mode
            <span class="status-box">{kidMode ? 'ON' : 'OFF'}</span>
        </button>
    </div>
    
    <div class="right-section">
        <div class="menu-container">
            <button class="help-button" onclick={openHowToPlay} title="How to Play">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-circle-question-mark-icon lucide-circle-question-mark">
                    <circle cx="12" cy="12" r="10"/>
                    <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/>
                    <path d="M12 17h.01"/>
                </svg>
            </button>
            <button class="menu-button" onclick={toggleMenu} aria-label="Open menu">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-menu-icon lucide-menu">
                    <path d="M4 5h16"/>
                    <path d="M4 12h16"/>
                    <path d="M4 19h16"/>
                </svg>
            </button>
            
            {#if menuOpen}
                <div class="dropdown-menu">
                    <button class="menu-item" onclick={handleNewGame}>
                        New Game
                    </button>
                    <button class="menu-item" onclick={handleShareGame}>
                        Share Game
                    </button>
                    <button class="menu-item" onclick={handleReportIssue}>
                        Report Issue
                    </button>
                    <button class="menu-item" onclick={toggleSoundOn}>
                        Sound: <span class="status-box">{soundOn ? 'ON' : 'OFF'}</span>
                    </button>
                    <button class="menu-item" class:active={hintMode} onclick={toggleHintMode}>
                        Hint Mode: <span class="status-box">{hintMode ? 'ON' : 'OFF'}</span>
                    </button>
                </div>
            {/if}
        </div>
    </div>
</nav>

<style>
    .menu-bar {
        width: 100%;
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.5rem 1.5rem 0.5rem 0;
        border-bottom: 1px solid #ddd;
        margin-bottom: 1rem;
    }

    .left-section,
    .right-section {
        display: flex;
        align-items: center;
    }

    .left-section {
        justify-content: flex-start;
    }

    .right-section {
        justify-content: flex-end;
    }

    /* Go Back Button */
    .go-back-button {
        background: none;
        border: none;
        color: #333;
        cursor: pointer;
        padding: 0.5rem 1rem 0.5rem 1rem;
        border-radius: 8px;
        margin-right: 1rem;
    }

    /* Kid Mode Button */
    .kid-mode-button {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.5rem 0.75rem;
        background-color: white;
        border: 2px solid #ddd;
        border-radius: 8px;
        color: #333;
        font-size: 0.875rem;
        font-weight: 500;
        white-space: nowrap;
        cursor: pointer;
        transition: all 0.2s;
    }

    .kid-mode-button:hover {
        background-color: #f0f0f0;
        border-color: #ccc;
    }

    .kid-mode-button.active {
        background-color: #ffd43b;
        border-color: #fcc419;
        color: #333;
    }

    .kid-mode-button.active:hover {
        background-color: #fcc419;
        border-color: #fab005;
    }

    .status-box {
        padding: 0.25rem 0.375rem;
        background-color: rgba(0, 0, 0, 0.1);
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: 600;
        transition: background-color 0.2s;
        width: 2.5rem;
        text-align: center;
    }

    .kid-mode-button.active .status-box {
        background-color: rgba(255, 255, 255, 0.3);
        color: #333;
    }

    .menu-container {
        position: relative;
        display: flex;
        gap: 0.5rem;
        align-items: center;
    }

    .help-button {
        background: none;
        border: none;
        color: #333;
        cursor: pointer;
        padding: 0.5rem;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.25rem;
        transition: all 0.2s;
    }

    .help-button:hover {
        background-color: #ffffff;
        transform: scale(1.10);
    }

    .menu-button {
        background: none;
        border: none;
        color: #333;
        cursor: pointer;
        padding: 0.5rem;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.2s;
    }

    .menu-button:hover {
        background-color: #fff;
        transform: scale(1.10);
    }

    .dropdown-menu {
        position: absolute;
        top: 100%;
        right: 0;
        margin-top: 0.5rem;
        background-color: white;
        border: 2px solid #ddd;
        border-radius: 8px;
        overflow: hidden;
        min-width: 150px;
        z-index: 100;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }

    .menu-item {
        display: block;
        width: 100%;
        padding: 0.75rem 1rem;
        background: none;
        border: none;
        color: #333;
        font-size: 0.875rem;
        text-align: left;
        cursor: pointer;
        transition: background-color 0.2s;
    }

    .menu-item:hover {
        background-color: #f0f0f0;
    }

    .menu-item.active {
        background: #ffd43b;
        color: #333;
    }

    .menu-item.active:hover {
        background: #fcc419;
    }

    .menu-item + .menu-item {
        border-top: 1px solid #ddd;
    }
</style>
