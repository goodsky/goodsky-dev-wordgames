<script>
  let { 
    isOpen = false, 
    onClose = () => {}, 
    onSuccess = () => {},
    initialWord = '',
    initialType = 'remove'
  } = $props();
  
  let reportWord = $state('');
  let reportType = $state('remove');

  // Update form when modal opens with new initial values
  $effect(() => {
    if (isOpen) {
      reportWord = initialWord;
      reportType = initialType;
    }
  });

  async function submitReport() {
    if (!reportWord.trim()) {
      onSuccess({ success: false, message: 'Please enter a word', type: 'error' });
      return;
    }

    try {
      const response = await fetch('/api/dictionary/report', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          word: reportWord.trim().toUpperCase(), 
          type: reportType 
        })
      });

      if (response.ok) {
        onSuccess({ success: true, message: 'Word reported successfully!', type: 'success' });
        onClose();
      } else if (response.status === 429) {
        onSuccess({ success: false, message: 'Report limit reached', type: 'error' });
      } else {
        onSuccess({ success: false, message: 'Failed to report word', type: 'error' });
      }
    } catch (error) {
      console.error('Error reporting word:', error);
      onSuccess({ success: false, message: 'Failed to report word', type: 'error' });
    }
  }

  function handleBackdropClick() {
    onClose();
  }

  function handleModalClick(e) {
    e.stopPropagation();
  }

  function handleKeyPress(e) {
    if (e.key === 'Enter') {
      submitReport();
    }
  }
</script>

{#if isOpen}
  <div class="modal-backdrop" onclick={handleBackdropClick} onkeydown={handleBackdropClick} role="button" tabindex="-1">
    <div class="modal" onclick={handleModalClick} onkeydown={handleModalClick} role="dialog" tabindex="-1">
      <h2>Report a Word</h2>
      <div class="form-group">
        <label for="report-word">Word:</label>
        <input 
          id="report-word"
          type="text" 
          bind:value={reportWord} 
          placeholder="Enter word"
          onkeydown={handleKeyPress}
        />
        {#if reportWord.trim()}
          <a 
            href={`https://www.dictionary.com/browse/${reportWord.trim().toLowerCase()}`}
            target="_blank"
            rel="noopener noreferrer"
            class="dictionary-link"
          >
            ℹ️ Check on Dictionary.com
          </a>
        {/if}
      </div>
      <div class="form-group">
        <div class="form-label">Action:</div>
        <div class="radio-group">
          <label>
            <input type="radio" bind:group={reportType} value="add" />
            Suggest to ADD
          </label>
          <label>
            <input type="radio" bind:group={reportType} value="remove" />
            Suggest to REMOVE
          </label>
        </div>
      </div>
      <div class="modal-actions">
        <button onclick={() => onClose()}>Cancel</button>
        <button class="primary" onclick={submitReport}>Submit</button>
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
    align-items: center;
    justify-content: center;
    z-index: 100;
  }

  .modal {
    background: white;
    padding: 2rem;
    border-radius: 12px;
    max-width: 400px;
    width: 90%;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  }

  .modal h2 {
    margin: 0 0 1.5rem 0;
    font-size: 1.5rem;
  }

  .form-group {
    margin-bottom: 1.5rem;
  }

  .form-group label {
    display: block;
    margin-bottom: 0.5rem;
    font-weight: 600;
  }

  .form-group .form-label {
    display: block;
    margin-bottom: 0.5rem;
    font-weight: 600;
  }

  .form-group input[type="text"] {
    width: 100%;
    padding: 0.75rem;
    border: 2px solid #ddd;
    border-radius: 8px;
    font-size: 1rem;
    box-sizing: border-box;
  }

  .form-group input[type="text"]:focus {
    outline: none;
    border-color: #4dabf7;
  }

  .dictionary-link {
    display: inline-block;
    margin-top: 0.5rem;
    font-size: 0.9rem;
    color: #4dabf7;
    text-decoration: none;
    transition: color 0.2s;
  }

  .dictionary-link:hover {
    color: #339af0;
    text-decoration: underline;
  }

  .radio-group {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .radio-group label {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-weight: normal;
    cursor: pointer;
  }

  .modal-actions {
    display: flex;
    gap: 1rem;
    justify-content: flex-end;
  }

  .modal-actions button {
    padding: 0.75rem 1.5rem;
    border: 2px solid #ddd;
    border-radius: 8px;
    background: white;
    cursor: pointer;
    font-size: 1rem;
    transition: all 0.2s;
  }

  .modal-actions button:hover {
    background: #f0f0f0;
  }

  .modal-actions button.primary {
    background: #4dabf7;
    border-color: #339af0;
    color: white;
  }

  .modal-actions button.primary:hover {
    background: #339af0;
  }
</style>
