export interface WordEntry {
  emoji: string;
  word: string;
  rhymeSuffix: string;
  color: string;
}

export const WORD_ENTRIES: WordEntry[] = [
  // Simple CVC words
  { emoji: '🐱', word: 'CAT', rhymeSuffix: 'AT', color: '#FFB3BA' },
  { emoji: '🌞', word: 'SUN', rhymeSuffix: 'UN', color: '#FFFFBA' },
  { emoji: '🐶', word: 'DOG', rhymeSuffix: 'OG', color: '#BAFFC9' },
  { emoji: '🐛', word: 'BUG', rhymeSuffix: 'UG', color: '#BAE1FF' },
  { emoji: '🐷', word: 'PIG', rhymeSuffix: 'IG', color: '#FFB3FF' },
  { emoji: '🛏️', word: 'BED', rhymeSuffix: 'ED', color: '#E0BBE4' },
  { emoji: '🍯', word: 'POT', rhymeSuffix: 'OT', color: '#FFF5BA' },
  { emoji: '🦊', word: 'FOX', rhymeSuffix: 'OX', color: '#FFCC80' },
  { emoji: '🐝', word: 'BEE', rhymeSuffix: 'EE', color: '#FFF59D' },
  { emoji: '🥁', word: 'DRUM', rhymeSuffix: 'UM', color: '#CE93D8' },

  // Words with blends/digraphs
  { emoji: '🦈', word: 'SHARK', rhymeSuffix: 'ARK', color: '#B3E5FC' },
  { emoji: '🐚', word: 'SHELL', rhymeSuffix: 'ELL', color: '#FFCCBC' },
  { emoji: '⭐', word: 'STAR', rhymeSuffix: 'AR', color: '#FFF176' },
  { emoji: '🚂', word: 'TRAIN', rhymeSuffix: 'AIN', color: '#A5D6A7' },
  { emoji: '🐋', word: 'WHALE', rhymeSuffix: 'ALE', color: '#81D4FA' },
  { emoji: '🐌', word: 'SNAIL', rhymeSuffix: 'AIL', color: '#C5E1A5' },
  { emoji: '🐸', word: 'FROG', rhymeSuffix: 'OG', color: '#A5D6A7' },
  { emoji: '🦆', word: 'DUCK', rhymeSuffix: 'UCK', color: '#80DEEA' },
  { emoji: '🎂', word: 'CAKE', rhymeSuffix: 'AKE', color: '#F8BBD9' },
  { emoji: '🐤', word: 'CHICK', rhymeSuffix: 'ICK', color: '#FFF59D' },

  // More variety
  { emoji: '🌙', word: 'MOON', rhymeSuffix: 'OON', color: '#B39DDB' },
  { emoji: '⛵', word: 'BOAT', rhymeSuffix: 'OAT', color: '#90CAF9' },
  { emoji: '👑', word: 'KING', rhymeSuffix: 'ING', color: '#FFD54F' },
  { emoji: '🐻', word: 'BEAR', rhymeSuffix: 'EAR', color: '#BCAAA4' },
  { emoji: '🕐', word: 'CLOCK', rhymeSuffix: 'OCK', color: '#B0BEC5' },
  { emoji: '🪺', word: 'NEST', rhymeSuffix: 'EST', color: '#A1887F' },
  { emoji: '🌽', word: 'CORN', rhymeSuffix: 'ORN', color: '#FFE082' },
  { emoji: '🐭', word: 'MOUSE', rhymeSuffix: 'OUSE', color: '#CFD8DC' },
  { emoji: '🚗', word: 'CAR', rhymeSuffix: 'AR', color: '#EF9A9A' },
  { emoji: '⛺', word: 'TENT', rhymeSuffix: 'ENT', color: '#80CBC4' },
];

export const SOUNDS: string[] = [
  'A', 'B', 'C', 'D', 'E', 'F', 'G',
  'H', 'I', 'J', 'K', 'L', 'M', 'N',
  'O', 'P', 'Q', 'R', 'S', 'T', 'U',
  'V', 'W', 'X', 'Y', 'Z',
  'CH', 'SH', 'TH', 'WH'
];

export const RAINBOW_COLORS: string[] = [
  '#FF6B6B',
  '#FF8E53',
  '#FFEB3B',
  '#4CAF50',
  '#42A5F5',
  '#7E57C2',
];

export function makeRhyme(sound: string, rhymeSuffix: string): string {
  return sound + rhymeSuffix;
}
