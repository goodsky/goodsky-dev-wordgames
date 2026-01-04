const express = require('express');
const path = require('path');
const fs = require('fs');

const crosswordReportRouter = require('./crosswordReport');

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
                // Extract game ID from filename (e.g., game_1.json -> "1", game_1.new.json -> "1")
                const gameId = file.replace('game_', '').replace('.new.json', '').replace('.json', '');
                games[gameId] = { ...game, id: gameId };
            }
        });
    }

    const easyCount = Object.values(games).filter(g => g.difficulty === 'EASY').length;
    const hardCount = Object.values(games).filter(g => g.difficulty === 'HARD').length;
    console.log(`Loaded ${Object.keys(games).length} crossword games (${easyCount} easy, ${hardCount} hard)`);
}

function getGameById(gameId) {
    return games[gameId] || null;
}

function getRandomGame(difficulty = 'EASY') {
    const gameIds = Object.keys(games).filter(id => games[id].difficulty == difficulty)
    
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

function prepareClueObject(clueObj, includeHard = false) {
    let availableClues = [...clueObj.clues];
    
    // If includeHard is true, merge hardClues with clues
    if (includeHard && clueObj.hardClues && clueObj.hardClues.length > 0) {
        availableClues = [...availableClues, ...clueObj.hardClues];
    }

    // Shuffle the clues array
    for (let i = availableClues.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [availableClues[i], availableClues[j]] = [availableClues[j], availableClues[i]];
    }

    return {
        index: clueObj.index,
        direction: clueObj.direction,
        row: clueObj.row,
        col: clueObj.col,
        answer: clueObj.answer.toUpperCase(),
        clues: availableClues,
    };
}

loadGames();

const router = express.Router();

router.use('/report', crosswordReportRouter);

// API endpoint to get a new game
// Query params:
//   - id: specific game ID to load
//   - difficulty: 'easy' (default) or 'hard'
router.get('/newgame', (req, res) => {
    const requestedId = req.query.id;
    const requestedDifficulty = (req.query.difficulty || 'easy').toUpperCase();
    
    // Validate difficulty parameter
    if (requestedDifficulty !== 'EASY' && requestedDifficulty !== 'HARD') {
        return res.status(400).json({ error: 'Difficulty must be "easy" or "hard"' });
    }

    let game;
    if (requestedId) {
        // Load specific game by ID
        game = getGameById(requestedId);
        if (!game) {
            return res.status(404).json({ error: `Game with id '${requestedId}' not found` });
        }
    } else {
        // Pick a random game based on difficulty
        game = getRandomGame(requestedDifficulty);
        if (!game) {
            return res.status(404).json({ error: `No ${requestedDifficulty.toLowerCase()} games available` });
        }
    }

    const includeHard = requestedDifficulty === 'HARD';
    
    game_object = {
        id: game.id,
        grid: populatePuzzleGrid(game.shape, game.clues),
        clues: game.clues.map(
            (clueObj) => prepareClueObject(clueObj, includeHard)
        ),
    }

    res.json(game_object);
});

module.exports = router;
