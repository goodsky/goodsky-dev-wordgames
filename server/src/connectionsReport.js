const express = require('express');
const path = require('path');
const fs = require('fs');

const router = express.Router();

// Determine storage path based on environment
const STORAGE_PATH = process.env.NODE_ENV === 'production' 
  ? '/app/storage' 
  : path.join(__dirname, '../storage');

// Maximum number of reports that can be sent
const MAX_REPORTED_GAMES = 1000;

// Ensure storage directory exists
if (!fs.existsSync(STORAGE_PATH)) {
  fs.mkdirSync(STORAGE_PATH, { recursive: true });
}

const REPORTED_GAMES_FILE = path.join(STORAGE_PATH, 'reported.json');

function readReportedGames() {
  if (!fs.existsSync(REPORTED_GAMES_FILE)) {
    return [];
  }
  const content = fs.readFileSync(REPORTED_GAMES_FILE, 'utf-8');
  return JSON.parse(content);
}

function appendReportedGame(gameId, words, comment) {
  const existingGames = readReportedGames();
  
  if (existingGames.length >= MAX_REPORTED_GAMES) {
    return false;
  }
  
  existingGames.push({ gameId, words, comment, timestamp: new Date().toISOString() });
  fs.writeFileSync(REPORTED_GAMES_FILE, JSON.stringify(existingGames, null, 2), 'utf-8');
  return true;
}

function formatReportedGames() {
  const reportedGames = readReportedGames();
  const mergedReports = {};

  reportedGames.forEach(report => {
    if (!mergedReports[report.gameId]) {
      mergedReports[report.gameId] = {
        gameId: report.gameId,
        comments: [
          report.comment,
          report.words,
          report.timestamp
        ]
      };
    } else {
      mergedReports[report.gameId].comments.push([
        report.comment,
        report.words,
        report.timestamp
      ]);
    }
  });

  return reportedGames;
}

// POST endpoint to report a game
router.post('/', (req, res) => {
  const { gameId, words, comment } = req.body;

  if (!gameId || typeof gameId !== 'string') {
    return res.status(400).json({ error: 'gameId is required and must be a string' });
  }

  if (!words || !Array.isArray(words) || words.length === 0) {
    return res.status(400).json({ error: 'words must be a non-empty array' });
  }

  const success = appendReportedGame(gameId, words, comment);
  
  if (!success) {
    return res.status(429).json({ error: 'Maximum number of reported games reached' });
  }

  res.status(200).end();
});

// GET endpoint to retrieve all reported games
router.get('/', (req, res) => {
  const reportedGames = formatReportedGames();
  res.json(reportedGames);
});

// DELETE endpoint to clear all reported games
router.delete('/', (req, res) => {
  // Clear reported games file
  if (fs.existsSync(REPORTED_GAMES_FILE)) {
    fs.unlinkSync(REPORTED_GAMES_FILE);
  }

  res.status(200).end();
});

module.exports = router;
