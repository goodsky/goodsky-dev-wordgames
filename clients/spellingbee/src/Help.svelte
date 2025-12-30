<script>
  let { isOpen = $bindable(false), onClose } = $props();
</script>

{#if isOpen}
  <div class="modal-backdrop" onclick={onClose} onkeydown={onClose} role="button" tabindex="-1">
    <div class="modal-content" onclick={(e) => e.stopPropagation()} onkeydown={(e) => e.stopPropagation()} role="dialog" tabindex="-1">
      <div class="modal-header">
        <h2>How to Play</h2>
        <button class="modal-close" onclick={onClose}>&times;</button>
      </div>
      <div class="modal-body">
        <h3>Goal</h3>
        <p>Create words using the letters shown in the honeycomb. Each word must:</p>
        <ul>
          <li>Be at least 4 letters long (unless specified otherwise)</li>
          <li>Include the <strong>center letter (shown in yellow)</strong></li>
        </ul>
        
        <h3>Kid Assist Mode</h3>
        <p>Toggle this mode from the top left button. When enabled:</p>
        <ul>
          <li>Ghost letters appear to show you a valid word</li>
          <li>Perfect for learning or when stuck!</li>
        </ul>
        
        <h3>Hint Mode</h3>
        <p>Enable from the menu (☰). When active:</p>
        <ul>
          <li>A lightbulb button (💡) appears</li>
          <li>Click it to get the next letter of a valid word</li>
          <li>Shows an error if your current letters don't lead to any valid word</li>
        </ul>
        
        <h3>Report Words</h3>
        <p>Found a word that should be in the dictionary? Or found an invalid word?</p>
        <ul>
          <li>Use <strong>Report Word</strong> from the menu</li>
        </ul>
      </div>
      <div class="modal-header">
        <h2>Credits</h2>
      </div>
      <div class="modal-body">
        <ul>
          <li>Developed by <a href="mailto:goodsky@outlook.com">Skyler Goodell</a></li>
          <li>Inspired by the New York Times Spelling Bee</li>
          <li><a href="https://www.flaticon.com/free-icons/bee" title="bee icons">Bee icons created by juicy_fish - Flaticon</a></li>
        </ul>
      </div>
    </div>
  </div>
{/if}

<style>
  .modal-backdrop {
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 100;
    padding: 1rem;
  }

  .modal-content {
    background: white;
    border-radius: 12px;
    max-width: 600px;
    width: 100%;
    max-height: 90vh;
    overflow-y: auto;
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
  }

  .modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1.5rem;
    border-bottom: 1px solid #ddd;
  }

  .modal-header h2 {
    margin: 0;
    color: #333;
  }

  .modal-close {
    background: transparent;
    border: none;
    font-size: 2rem;
    color: #999;
    cursor: pointer;
    width: 40px;
    height: 40px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 4px;
    transition: all 0.2s;
  }

  .modal-close:hover {
    background: #f0f0f0;
    color: #333;
  }

  .modal-body {
    padding: 1.5rem;
  }

  .modal-body h3 {
    color: #333;
    margin-top: 1.5rem;
    margin-bottom: 0.5rem;
    font-size: 1.1rem;
  }

  .modal-body h3:first-child {
    margin-top: 0;
  }

  .modal-body p {
    margin: 0.5rem 0;
    line-height: 1.6;
    color: #555;
  }

  .modal-body ul {
    margin: 0.5rem 0;
    padding-left: 1.5rem;
  }

  .modal-body li {
    margin: 0.5rem 0;
    line-height: 1.6;
    color: #555;
  }

  .modal-body strong {
    color: #333;
    font-weight: 600;
  }
</style>
