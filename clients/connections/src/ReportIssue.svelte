<script>
    let { gameId, words, onClose } = $props();
    
    let comment = $state('');
    let isSubmitting = $state(false);
    let submitSuccess = $state(false);
    let submitError = $state('');

    async function handleSubmit(e) {
        e.preventDefault();
        
        if (!gameId || !words || words.length === 0) {
            submitError = 'No game data available to report';
            return;
        }

        isSubmitting = true;
        submitError = '';

        try {
            const response = await fetch('/api/report', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    gameId,
                    words: words.map(w => w.text),
                    comment: comment.trim() || 'No comment provided'
                })
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Failed to submit report');
            }

            submitSuccess = true;
            setTimeout(() => {
                onClose?.();
            }, 1500);
        } catch (error) {
            submitError = error.message;
            isSubmitting = false;
        }
    }

    function handleCancel() {
        onClose?.();
    }

    // Close modal when clicking outside
    function handleBackdropClick(e) {
        if (e.target === e.currentTarget) {
            onClose?.();
        }
    }
</script>

<div class="modal-backdrop" role="button" tabindex="0" onclick={handleBackdropClick} onkeydown={(e) => e.key === 'Enter' && handleBackdropClick(e)}>
    <div class="modal-content">
        <div class="modal-header">
            <h2>Report Issue</h2>
            <button class="close-button" onclick={handleCancel} aria-label="Close">&times;</button>
        </div>

        {#if submitSuccess}
            <div class="success-message">
                <p>✓ Report submitted successfully!</p>
                <p class="success-subtext">Thank you for your feedback.</p>
            </div>
        {:else}
            <form onsubmit={handleSubmit}>
                <div class="form-content">
                    <div class="game-info">
                        <p><strong>Game ID:</strong> {gameId || 'Unknown'}</p>
                        <p><strong>Words:</strong> {words.map(w => w.text).join(', ')}</p>
                    </div>

                    <div class="form-group">
                        <label for="comment">Describe the issue (optional):</label>
                        <textarea 
                            id="comment"
                            bind:value={comment}
                            placeholder="e.g., 'Word X doesn't fit the category' or 'Words are ambiguous'"
                            rows="4"
                            disabled={isSubmitting}
                        ></textarea>
                    </div>

                    {#if submitError}
                        <div class="error-message">
                            {submitError}
                        </div>
                    {/if}
                </div>

                <div class="modal-footer">
                    <button type="button" class="button button-secondary" onclick={handleCancel} disabled={isSubmitting}>
                        Cancel
                    </button>
                    <button type="submit" class="button button-primary" disabled={isSubmitting}>
                        {isSubmitting ? 'Submitting...' : 'Submit Report'}
                    </button>
                </div>
            </form>
        {/if}
    </div>
</div>

<style>
    .modal-backdrop {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background-color: rgba(0, 0, 0, 0.75);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 1000;
        padding: 1rem;
    }

    .modal-content {
        background-color: #1a1a1b;
        border: 1px solid #3a3a3c;
        border-radius: 12px;
        max-width: 500px;
        width: 100%;
        max-height: 90vh;
        overflow-y: auto;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
    }

    .modal-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 1.5rem;
        border-bottom: 1px solid #3a3a3c;
    }

    .modal-header h2 {
        margin: 0;
        font-size: 1.5rem;
        color: #ffffff;
        font-weight: 600;
    }

    .close-button {
        background: none;
        border: none;
        color: #818384;
        font-size: 2rem;
        line-height: 1;
        cursor: pointer;
        padding: 0;
        width: 2rem;
        height: 2rem;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 4px;
        transition: background-color 0.2s, color 0.2s;
    }

    .close-button:hover {
        background-color: #3a3a3c;
        color: #ffffff;
    }

    form {
        display: flex;
        flex-direction: column;
        height: 100%;
    }

    .form-content {
        padding: 1.5rem;
        flex: 1;
    }

    .game-info {
        background-color: #121213;
        border: 1px solid #3a3a3c;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 1.5rem;
    }

    .game-info p {
        margin: 0.5rem 0;
        color: #ffffff;
        font-size: 0.875rem;
        line-height: 1.5;
    }

    .game-info p:first-child {
        margin-top: 0;
    }

    .game-info p:last-child {
        margin-bottom: 0;
    }

    .game-info strong {
        color: #818384;
    }

    .form-group {
        margin-bottom: 1rem;
    }

    label {
        display: block;
        margin-bottom: 0.5rem;
        color: #ffffff;
        font-size: 0.875rem;
        font-weight: 500;
    }

    textarea {
        width: 100%;
        padding: 0.75rem;
        background-color: #121213;
        border: 1px solid #3a3a3c;
        border-radius: 8px;
        color: #ffffff;
        font-size: 0.875rem;
        font-family: inherit;
        resize: vertical;
        transition: border-color 0.2s;
        box-sizing: border-box;
    }

    textarea:focus {
        outline: none;
        border-color: #5a5a5c;
    }

    textarea:disabled {
        opacity: 0.5;
        cursor: not-allowed;
    }

    textarea::placeholder {
        color: #5a5a5c;
    }

    .error-message {
        padding: 0.75rem;
        background-color: rgba(220, 38, 38, 0.1);
        border: 1px solid rgba(220, 38, 38, 0.3);
        border-radius: 8px;
        color: #fca5a5;
        font-size: 0.875rem;
        margin-top: 1rem;
    }

    .success-message {
        padding: 3rem 1.5rem;
        text-align: center;
    }

    .success-message p {
        margin: 0;
        color: #86efac;
        font-size: 1.125rem;
        font-weight: 500;
    }

    .success-subtext {
        margin-top: 0.5rem !important;
        color: #818384 !important;
        font-size: 0.875rem !important;
        font-weight: 400 !important;
    }

    .modal-footer {
        display: flex;
        justify-content: flex-end;
        gap: 0.75rem;
        padding: 1.5rem;
        border-top: 1px solid #3a3a3c;
    }

    .button {
        padding: 0.75rem 1.5rem;
        border-radius: 8px;
        font-size: 0.875rem;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.2s;
        border: none;
    }

    .button:disabled {
        opacity: 0.5;
        cursor: not-allowed;
    }

    .button-secondary {
        background-color: transparent;
        border: 1px solid #3a3a3c;
        color: #ffffff;
    }

    .button-secondary:hover:not(:disabled) {
        background-color: #3a3a3c;
    }

    .button-primary {
        background-color: #5865f2;
        color: #ffffff;
    }

    .button-primary:hover:not(:disabled) {
        background-color: #4752c4;
    }
</style>
