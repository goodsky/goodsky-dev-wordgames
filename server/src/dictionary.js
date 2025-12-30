const express = require('express');
const path = require('path');
const fs = require('fs');

const dictionaryReportRouter = require('./dictionaryReport');

const dictPath = path.join(__dirname, '../data/dictionary/dict.txt');

// Load dictionary on startup
const dictionary = loadDictionary();

function loadDictionary() {
  try {
    const dictContent = fs.readFileSync(dictPath, 'utf-8');
    const dictionary = dictContent.split('\n').map(word => word.trim().toUpperCase()).filter(word => word.length > 0);
    console.log(`Loaded ${dictionary.length} words from dictionary`);
    return dictionary;
  } catch (error) {
    console.error('Error loading dictionary:', error);
  }
}

function getValidWords(letters, minLength) {
  const availableLetters = letters.map(l => l.toUpperCase());
  const letterSet = new Set(availableLetters);

  const validWords = dictionary.filter(word => {
    if (word.length < minLength) return false;

    for (const char of word) {
      if (!letterSet.has(char)) return false;
    }

    return true;
  });

  return validWords;
}

const router = express.Router();

router.use('/report', dictionaryReportRouter);

// API endpoint to get valid words based on available letters and min length
router.post('/', (req, res) => {
  const { letters, minLength } = req.body;

  if (!letters || !Array.isArray(letters) || letters.length === 0) {
    return res.status(400).json({ error: 'letters array is required' });
  }

  if (!minLength || typeof minLength !== 'number' || minLength < 1) {
    return res.status(400).json({ error: 'valid minLength is required' });
  }

  const validWords = getValidWords(letters, minLength);

  res.json({ 
    validWords,
    count: validWords.length
  });
});

module.exports = { router, getValidWords };
