const express = require('express');
const path = require('path');
const fs = require('fs');

const router = express.Router();

// Determine storage path based on environment
const STORAGE_PATH = process.env.NODE_ENV === 'production' 
  ? '/app/storage' 
  : path.join(__dirname, '../storage');

// Maximum number of words that can be reported per type
const MAX_REPORTED_WORDS = 1000;

// Ensure storage directory exists
if (!fs.existsSync(STORAGE_PATH)) {
  fs.mkdirSync(STORAGE_PATH, { recursive: true });
}

const REPORTED_ADD_FILE = path.join(STORAGE_PATH, 'reported_add.txt');
const REPORTED_REMOVE_FILE = path.join(STORAGE_PATH, 'reported_remove.txt');

// Helper functions for file operations
function readReportedWords(filePath) {
  if (!fs.existsSync(filePath)) {
    return [];
  }
  const content = fs.readFileSync(filePath, 'utf-8');
  return content.split('\n').filter(line => line.trim().length > 0);
}

function appendReportedWord(filePath, word) {
  const existingWords = readReportedWords(filePath);
  
  // Check if limit reached
  if (existingWords.length >= MAX_REPORTED_WORDS) {
    return false;
  }
  
  // Check if word already exists
  if (existingWords.includes(word)) {
    return true; // Already exists, consider it a success
  }
  
  fs.appendFileSync(filePath, word + '\n', 'utf-8');
  return true;
}

// POST endpoint to report a word (add or remove suggestion)
router.post('/', (req, res) => {
  const { word, type } = req.body;

  if (!word || typeof word !== 'string') {
    return res.status(400).json({ error: 'word is required and must be a string' });
  }

  if (!type || (type !== 'add' && type !== 'remove')) {
    return res.status(400).json({ error: 'type must be either "add" or "remove"' });
  }

  const normalizedWord = word.trim().toUpperCase();

  if (normalizedWord.length === 0) {
    return res.status(400).json({ error: 'word cannot be empty' });
  }

  // Append to appropriate file
  const filePath = type === 'add' ? REPORTED_ADD_FILE : REPORTED_REMOVE_FILE;
  const success = appendReportedWord(filePath, normalizedWord);
  
  if (!success) {
    return res.status(429).json({ error: 'Maximum number of reported words reached' });
  }

  res.status(200).end();
});

// GET endpoint to retrieve all reported words
router.get('/', (req, res) => {
  const addWords = readReportedWords(REPORTED_ADD_FILE);
  const removeWords = readReportedWords(REPORTED_REMOVE_FILE);

  res.json({
    add: addWords,
    remove: removeWords
  });
});

// DELETE endpoint to clear all reported words
router.delete('/', (req, res) => {
  // Clear both files by writing empty content
  if (fs.existsSync(REPORTED_ADD_FILE)) {
    fs.writeFileSync(REPORTED_ADD_FILE, '', 'utf-8');
  }
  if (fs.existsSync(REPORTED_REMOVE_FILE)) {
    fs.writeFileSync(REPORTED_REMOVE_FILE, '', 'utf-8');
  }

  res.status(200).end();
});

module.exports = router;
