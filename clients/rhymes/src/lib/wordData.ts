export interface WordEntry {
  emoji: string;
  word: string;
  rhymeSuffix: string;
  color: string;
}

export const WORD_ENTRIES: WordEntry[] = [
  { emoji: '🐱', word: 'CAT', rhymeSuffix: 'AT', color: '#FFB3BA' },
  { emoji: '🌞', word: 'SUN', rhymeSuffix: 'UN', color: '#FFFFBA' },
  { emoji: '🐶', word: 'DOG', rhymeSuffix: 'OG', color: '#BAFFC9' },
  { emoji: '🐛', word: 'BUG', rhymeSuffix: 'UG', color: '#BAE1FF' },
  { emoji: '🎩', word: 'HAT', rhymeSuffix: 'AT', color: '#D5B3FF' },
  { emoji: '🐷', word: 'PIG', rhymeSuffix: 'IG', color: '#FFB3FF' },
  { emoji: '🛏️', word: 'BED', rhymeSuffix: 'ED', color: '#E0BBE4' },
  { emoji: '🍯', word: 'POT', rhymeSuffix: 'OT', color: '#FFF5BA' },
  { emoji: '🦈', word: 'SHARK', rhymeSuffix: 'ARK', color: '#B3E5FC' },
  { emoji: '🐚', word: 'SHELL', rhymeSuffix: 'ELL', color: '#FFCCBC' },
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
