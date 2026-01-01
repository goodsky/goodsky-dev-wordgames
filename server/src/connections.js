const express = require('express');
const path = require('path');
const fs = require('fs');

const connectionsReportRouter = require('./connectionsReport');

const GAMES_DIR = path.join(__dirname, '../data/connections');

// Store all games in memory
const games = {
    regular: {},
    kid: {}
};

/**
 * Load all games from the games directory
 */
function loadGames() {
    // Load regular games
    const regularDir = path.join(GAMES_DIR, 'regular');
    if (fs.existsSync(regularDir)) {
        fs.readdirSync(regularDir).forEach(file => {
            if (file.endsWith('.json')) {
                const game = JSON.parse(fs.readFileSync(path.join(regularDir, file), 'utf8'));
                games.regular[game.id] = game;
            }
        });
    }

    // Load kid games
    const kidDir = path.join(GAMES_DIR, 'kid');
    if (fs.existsSync(kidDir)) {
        fs.readdirSync(kidDir).forEach(file => {
            if (file.endsWith('.json')) {
                const game = JSON.parse(fs.readFileSync(path.join(kidDir, file), 'utf8'));
                games.kid[game.id] = game;
            }
        });
    }

    console.log(`Loaded ${Object.keys(games.regular).length} regular games and ${Object.keys(games.kid).length} kid games`);
}

/**
 * Get all games for a specific mode
 * @param {boolean} kidMode - Whether to get kid games or regular games
 * @returns {Object} Object containing all games for the specified mode
 */
function getGames(kidMode) {
    return kidMode ? games.kid : games.regular;
}

/**
 * Get a specific game by ID and mode
 * @param {string} gameId - The ID of the game to retrieve
 * @param {boolean} kidMode - Whether to look in kid games or regular games
 * @returns {Object|null} The game object or null if not found
 */
function getGameById(gameId, kidMode) {
    const gamePool = getGames(kidMode);
    return gamePool[gameId] || null;
}

/**
 * Get a random game from the specified mode
 * @param {boolean} kidMode - Whether to get a kid game or regular game
 * @returns {Object|null} A random game object or null if no games available
 */
function getRandomGame(kidMode) {
    const gamePool = getGames(kidMode);
    const gameIds = Object.keys(gamePool);
    
    if (gameIds.length === 0) {
        return null;
    }
    
    const randomIndex = Math.floor(Math.random() * gameIds.length);
    return gamePool[gameIds[randomIndex]];
}

/**
 * Normalize a word to object format
 * @param {string|Object} word - Word as string or {text, lightColor, darkColor, backgroundColor, altText} object
 * @returns {Object} Normalized word object with {text, lightColor, darkColor, backgroundColor, altText}
 */
function normalizeWord(word) {
    if (typeof word === 'string') {
        return { text: word, lightColor: null, darkColor: null, backgroundColor: null, altText: null };
    }
    const lightColor = word.lightColor || word.color || null;
    const darkColor = word.darkColor || word.color || null;
    const backgroundColor = word.backgroundColor || null;
    const altText = word.altText || null;
    
    return { 
        text: word.text, 
        lightColor,
        darkColor,
        backgroundColor,
        altText
    };
}

/**
 * Get the text from a word (handles both string and object formats)
 * @param {string|Object} word - Word as string or {text, color} object
 * @returns {string} The word text
 */
function getWordText(word) {
    return typeof word === 'string' ? word : word.text;
}

/**
 * Randomly select 4 words from a category
 * @param {(string|Object)[]} words - Array of words in a category (strings or objects)
 * @returns {Object[]} Array of 4 randomly selected normalized word objects
 */
function selectRandomWords(words) {
    if (words.length <= 4) {
        return words.map(normalizeWord);
    }
    
    // Fisher-Yates shuffle and take first 4
    const shuffled = [...words];
    for (let i = shuffled.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
    }
    
    return shuffled.slice(0, 4).map(normalizeWord);
}

/**
 * Select specific words from categories or randomly select if not specified
 * @param {Object} game - The game object
 * @param {string[]|null} requestedWords - Array of specific words to use (or null for random selection)
 * @returns {Object} Game object with selected words (4 per category), all words normalized to objects
 */
function selectGameWords(game, requestedWords) {
    if (requestedWords && requestedWords.length > 0) {
        // Use specific requested words
        const requestedSet = new Set(requestedWords.map(w => w.toUpperCase()));
        
        // Validate that all requested words exist in the game
        const allGameWords = game.categories.flatMap(cat => cat.words);
        const allGameWordsUpperMap = new Map(
            allGameWords.map(w => [getWordText(w).toUpperCase(), w])
        );
        
        for (const word of requestedWords) {
            if (!allGameWordsUpperMap.has(word.toUpperCase())) {
                throw new Error(`Word '${word}' not found in game`);
            }
        }
        
        // Filter categories to only include requested words and normalize
        const selectedCategories = game.categories.map(cat => {
            const selectedWords = cat.words
                .filter(w => requestedSet.has(getWordText(w).toUpperCase()))
                .map(normalizeWord);
            return {
                ...cat,
                words: selectedWords
            };
        }).filter(cat => cat.words.length > 0);
        
        return {
            ...game,
            categories: selectedCategories
        };
    } else {
        // Randomly select 4 words from each category and normalize
        const selectedCategories = game.categories.map(cat => ({
            ...cat,
            words: selectRandomWords(cat.words)
        }));
        
        return {
            ...game,
            categories: selectedCategories
        };
    }
}

loadGames();

const router = express.Router();

router.use('/report', connectionsReportRouter);

// API endpoint to get a new game
// Query params:
//   - kidmode: "true" to get kid-friendly games
//   - id: specific game ID to load
//   - words: comma-separated list of specific words to use from the game
router.get('/newgame', (req, res) => {
    const kidMode = req.query.kidmode === 'true';
    const requestedId = req.query.id;
    const requestedWords = req.query.words ? req.query.words.split(',').map(w => w.trim()) : null;

    let game;
    if (requestedId) {
        // Load specific game by ID
        game = getGameById(requestedId, kidMode);
        if (!game) {
            return res.status(404).json({ error: `Game with id '${requestedId}' not found` });
        }
    } else {
        // Pick a random game
        game = getRandomGame(kidMode);
        if (!game) {
            return res.status(404).json({ error: 'No games available' });
        }
    }

    // Select words for the game (either specific requested words or random selection)
    try {
        game = selectGameWords(game, requestedWords);
    } catch (error) {
        return res.status(400).json({ error: error.message });
    }

    // Return game data (shuffle words so categories aren't obvious)
    // At this point, all words are normalized to {text, lightColor, darkColor} objects
    const allWords = game.categories.flatMap(cat => 
        cat.words.map(word => ({ ...word, category: cat.name }))
    );

    // Fisher-Yates shuffle
    for (let i = allWords.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [allWords[i], allWords[j]] = [allWords[j], allWords[i]];
    }

    res.json({
        id: game.id,
        kidMode: game.kidMode,
        words: allWords.map(w => ({ text: w.text, lightColor: w.lightColor, darkColor: w.darkColor, backgroundColor: w.backgroundColor, altText: w.altText })),
        categories: game.categories.map(cat => ({
            name: cat.name,
            difficulty: cat.difficulty,
            words: cat.words
        }))
    });
});

module.exports = router;
