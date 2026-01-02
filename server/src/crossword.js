const express = require('express');
const path = require('path');
const fs = require('fs');

const GAMES_DIR = path.join(__dirname, '../data/crossword');

const games = {};

/**
 * Load all games from the games directory
 */
function loadGames() {
    if (fs.existsSync(GAMES_DIR)) {
        fs.readdirSync(GAMES_DIR).forEach(file => {
            if (file.endsWith('.json')) {
                const game = JSON.parse(fs.readFileSync(path.join(GAMES_DIR, file), 'utf8'));
                // Extract game ID from filename (e.g., game_1.json -> "1")
                const gameId = file.replace('game_', '').replace('.json', '');
                games[gameId] = { ...game, id: gameId };
            }
        });
    }

    console.log(`Loaded ${Object.keys(games).length} crossword games`);
}

function getGameById(gameId) {
    return games[gameId] || null;
}

function getRandomGame() {
    const gameIds = Object.keys(games);
    
    if (gameIds.length === 0) {
        return null;
    }
    
    const randomIndex = Math.floor(Math.random() * gameIds.length);
    return games[gameIds[randomIndex]];
}

function populatePuzzleGrid(shape, clues) {
    // -1 = blocked cell
    // 0 = empty cell
    // N = clue index
    const grid = shape.map(
        row => row.map(cell => (cell === 1 ? 0 : -1))
    );

    clues.forEach(clueObj => {
        const { index, direction, row, col, answer } = clueObj;
        grid[row][col] = index;
    });

    return grid;
}

function selectRandomClue(clueObj) {
    const randomIndex = Math.floor(Math.random() * clueObj.clues.length);
    const clue = clueObj.clues[randomIndex];

    return {
        index: clueObj.index,
        direction: clueObj.direction,
        row: clueObj.row,
        col: clueObj.col,
        answer: clueObj.answer.toUpperCase(),
        clue: clue,
    };
}

loadGames();

const router = express.Router();

// API endpoint to get a new game
// Query params:
//   - id: specific game ID to load
router.get('/newgame', (req, res) => {
    const requestedId = req.query.id;

    let game;
    if (requestedId) {
        // Load specific game by ID
        game = getGameById(requestedId);
        if (!game) {
            return res.status(404).json({ error: `Game with id '${requestedId}' not found` });
        }
    } else {
        // Pick a random game
        game = getRandomGame();
        if (!game) {
            return res.status(404).json({ error: 'No games available' });
        }
    }

    game_object = {
        id: game.id,
        grid: populatePuzzleGrid(game.shape, game.clues),
        clues: game.clues.map(
            (clueObj) => selectRandomClue(clueObj)
        ),
    }

    res.json(game_object);
});

module.exports = router;
