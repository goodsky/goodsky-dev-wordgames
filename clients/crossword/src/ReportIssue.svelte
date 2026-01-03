<script>
    let { gameId, clue, onClose } = $props();
    
    let comment = $state('');
    let isSubmitting = $state(false);
    let submitSuccess = $state(false);
    let submitError = $state('');

    async function handleSubmit(e) {
        e.preventDefault();
        
        if (!gameId || !clue) {
            submitError = 'No clue data available to report';
            return;
        }

        isSubmitting = true;
        submitError = '';

        try {
            const response = await fetch('/api/crossword/report', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    gameId,
                    clueIndex: clue.index,
                    clueDirection: clue.direction,
                    clue: clue.clue,
                    answer: clue.answer,
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
                        <p><strong>{clue?.index} {clue?.direction?.toUpperCase()}:</strong> {clue?.clue}</p>
                    </div>

                    <div class="form-group">
                        <label for="comment">Describe the issue (optional):</label>
                        <textarea 
                            id="comment"
                            bind:value={comment}
                            placeholder="e.g., 'Clue is misleading' or 'Answer is incorrect'"
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
        font-size: 2rem;
        color: #888;
        cursor: pointer;
        padding: 0;
        width: 2rem;
        height: 2rem;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: color 0.2s;
        line-height: 1;
    }

    .close-button:hover {
        color: #ffffff;
    }

    .form-content {
        padding: 1.5rem;
    }

    .game-info {
        background-color: #2a2a2c;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1.5rem;
        border: 1px solid #3a3a3c;
    }

    .game-info p {
        margin: 0.5rem 0;
        color: #e0e0e0;
        font-size: 0.95rem;
    }

    .game-info p:first-child {
        margin-top: 0;
    }

    .game-info p:last-child {
        margin-bottom: 0;
    }

    .game-info strong {
        color: #ffffff;
    }

    .form-group {
        margin-bottom: 1rem;
    }

    .form-group label {
        display: block;
        margin-bottom: 0.5rem;
        color: #ffffff;
        font-weight: 500;
    }

    .form-group textarea {
        width: 100%;
        padding: 0.75rem;
        border: 1px solid #3a3a3c;
        border-radius: 6px;
        background-color: #2a2a2c;
        color: #ffffff;
        font-family: inherit;
        font-size: 0.95rem;
        resize: vertical;
        box-sizing: border-box;
    }

    .form-group textarea:focus {
        outline: none;
        border-color: #538d4e;
    }

    .form-group textarea::placeholder {
        color: #666;
    }

    .form-group textarea:disabled {
        opacity: 0.5;
        cursor: not-allowed;
    }

    .error-message {
        padding: 0.75rem;
        background-color: #dc3545;
        color: #ffffff;
        border-radius: 6px;
        font-size: 0.9rem;
        margin-top: 1rem;
    }

    .success-message {
        padding: 2rem 1.5rem;
        text-align: center;
    }

    .success-message p {
        margin: 0.5rem 0;
        color: #ffffff;
        font-size: 1.1rem;
    }

    .success-subtext {
        color: #888;
        font-size: 0.95rem !important;
    }

    .modal-footer {
        display: flex;
        gap: 0.75rem;
        padding: 1rem 1.5rem;
        border-top: 1px solid #3a3a3c;
        justify-content: flex-end;
    }

    .button {
        padding: 0.625rem 1.25rem;
        border: none;
        border-radius: 6px;
        font-size: 0.95rem;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.2s;
    }

    .button:disabled {
        opacity: 0.5;
        cursor: not-allowed;
    }

    .button-secondary {
        background-color: #3a3a3c;
        color: #ffffff;
    }

    .button-secondary:hover:not(:disabled) {
        background-color: #4a4a4c;
    }

    .button-primary {
        background-color: #538d4e;
        color: #ffffff;
    }

    .button-primary:hover:not(:disabled) {
        background-color: #629f58;
    }
</style>
