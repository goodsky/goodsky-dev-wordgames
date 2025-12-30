<script>
    let { kidMode = $bindable(false), onNewGame, onShareGame, onHowToPlay, onReportIssue } = $props();
    
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
        <button 
            class="kid-mode-button" 
            class:active={kidMode}
            onclick={handleKidModeToggle}
        >
            Kid Mode
            <span class="status-box">{kidMode ? 'ON' : 'OFF'}</span>
        </button>
    </div>
    
    <div class="right-section">
        <div class="menu-container">
            <button class="help-button" onclick={openHowToPlay} title="How to Play">ⓘ</button>
            <button class="menu-button" onclick={toggleMenu} aria-label="Open menu">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <circle cx="12" cy="12" r="1"></circle>
                    <circle cx="12" cy="5" r="1"></circle>
                    <circle cx="12" cy="19" r="1"></circle>
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
                </div>
            {/if}
        </div>
    </div>
</nav>

<style>
    .menu-bar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 1rem 1.5rem;
        border-bottom: 1px solid #3a3a3c;
        background-color: #121213;
    }

    .left-section,
    .right-section {
        flex: 1;
        display: flex;
    }

    .left-section {
        justify-content: flex-start;
    }

    .right-section {
        justify-content: flex-end;
    }

    /* Kid Mode Button */
    .kid-mode-button {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.5rem 0.75rem;
        background-color: transparent;
        border: 1px solid #3a3a3c;
        border-radius: 8px;
        color: #818384;
        font-size: 0.875rem;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.2s;
    }

    .kid-mode-button:hover {
        border-color: #5a5a5c;
        color: #ffffff;
    }

    .kid-mode-button.active {
        background-color: #ba81c5;
        border-color: #ba81c5;
        color: #000000;
    }

    .kid-mode-button.active:hover {
        background-color: #c99ad3;
        border-color: #c99ad3;
    }

    .status-box {
        padding: 0.125rem 0.375rem;
        background-color: #3a3a3c;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: 600;
        transition: background-color 0.2s;
        min-width: 1.75rem;
        text-align: center;
    }

    .kid-mode-button.active .status-box {
        background-color: rgba(0, 0, 0, 0.2);
        color: #000000;
    }

    /* Menu Button and Dropdown */
    .menu-container {
        position: relative;
        display: flex;
        gap: 0.5rem;
        align-items: center;
    }

    .help-button {
        background: none;
        border: none;
        color: #818384;
        cursor: pointer;
        padding: 0.5rem;
        border-radius: 4px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.25rem;
        transition: color 0.2s, background-color 0.2s;
    }

    .help-button:hover {
        color: #ffffff;
        background-color: #3a3a3c;
    }

    .menu-button {
        background: none;
        border: none;
        color: #818384;
        cursor: pointer;
        padding: 0.5rem;
        border-radius: 4px;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: color 0.2s, background-color 0.2s;
    }

    .menu-button:hover {
        color: #ffffff;
        background-color: #3a3a3c;
    }

    .dropdown-menu {
        position: absolute;
        top: 100%;
        right: 0;
        margin-top: 0.5rem;
        background-color: #1a1a1b;
        border: 1px solid #3a3a3c;
        border-radius: 8px;
        overflow: hidden;
        min-width: 150px;
        z-index: 100;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    }

    .menu-item {
        display: block;
        width: 100%;
        padding: 0.75rem 1rem;
        background: none;
        border: none;
        color: #ffffff;
        font-size: 0.875rem;
        text-align: left;
        cursor: pointer;
        transition: background-color 0.2s;
    }

    .menu-item:hover {
        background-color: #3a3a3c;
    }

    .menu-item + .menu-item {
        border-top: 1px solid #3a3a3c;
    }
</style>
