const express = require('express');
const path = require('path');
const fs = require('fs');

const router = express.Router();

// Determine storage path based on environment
const STORAGE_PATH = process.env.NODE_ENV === 'production' 
  ? '/app/storage' 
  : path.join(__dirname, '../storage');

// Maximum number of reports that can be sent
const MAX_REPORTED_CLUES = 1000;

// Ensure storage directory exists
if (!fs.existsSync(STORAGE_PATH)) {
  fs.mkdirSync(STORAGE_PATH, { recursive: true });
}

const REPORTED_CLUES_FILE = path.join(STORAGE_PATH, 'crossword_reports.json');

function readReportedClues() {
  if (!fs.existsSync(REPORTED_CLUES_FILE)) {
    return [];
  }
  const content = fs.readFileSync(REPORTED_CLUES_FILE, 'utf-8');
  return JSON.parse(content);
}

function appendReportedClue(gameId, clueIndex, clueDirection, clue, answer, comment) {
  const existingReports = readReportedClues();
  
  if (existingReports.length >= MAX_REPORTED_CLUES) {
    return false;
  }
  
  existingReports.push({ 
    gameId, 
    clueIndex, 
    clueDirection,
    clue,
    answer,
    comment, 
    timestamp: new Date().toISOString() 
  });
  fs.writeFileSync(REPORTED_CLUES_FILE, JSON.stringify(existingReports), 'utf-8');
  return true;
}

function formatReportedClues() {
  const reportedClues = readReportedClues();
  const mergedReports = {};

  reportedClues.forEach(report => {
    if (!mergedReports[report.gameId]) {
      mergedReports[report.gameId] = {
        gameId: report.gameId,
        reports: []
      };
    }
    mergedReports[report.gameId].reports.push({
        clueIndex: report.clueIndex,
        clueDirection: report.clueDirection,
        clue: report.clue,
        answer: report.answer,
        comment: report.comment,
        timestamp: report.timestamp
    });
  });

  return Object.values(mergedReports);
}

// POST endpoint to report a clue
router.post('/', (req, res) => {
  const { gameId, clueIndex, clueDirection, clue, answer, comment } = req.body;

  if (!gameId || typeof gameId !== 'string') {
    return res.status(400).json({ error: 'gameId is required and must be a string' });
  }

  if (clueIndex === undefined || typeof clueIndex !== 'number') {
    return res.status(400).json({ error: 'clueIndex is required and must be a number' });
  }

  if (!clueDirection || !['across', 'down'].includes(clueDirection)) {
    return res.status(400).json({ error: 'clueDirection is required and must be either "across" or "down"' });
  }

  if (!clue || typeof clue !== 'string') {
    return res.status(400).json({ error: 'clue is required and must be a string' });
  }

  if (!answer || typeof answer !== 'string') {
    return res.status(400).json({ error: 'answer is required and must be a string' });
  }

  const success = appendReportedClue(gameId, clueIndex, clueDirection, clue, answer, comment || '');
  
  if (!success) {
    return res.status(429).json({ error: 'Maximum number of reported clues reached' });
  }

  res.status(200).end();
});

// GET endpoint to retrieve all reported clues
router.get('/', (req, res) => {
  const reportedClues = formatReportedClues();
  res.json(reportedClues);
});

// DELETE endpoint to clear all reported clues
router.delete('/', (req, res) => {
  // Clear reported clues file
  if (fs.existsSync(REPORTED_CLUES_FILE)) {
    fs.unlinkSync(REPORTED_CLUES_FILE);
  }

  res.status(200).end();
});

module.exports = router;
