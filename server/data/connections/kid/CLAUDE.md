Generate EASY and FUN word games for PRESCHOOL CHILDREN. Create 4 non-overlapping categories with unique emojis or very simple words.

⚠️ If you have ever played the New York Times word game "Connections" - this is played with the same rules! ⚠️

# File Format
{
  "id": "$UniqueId",
  "kidMode": true,
  "categories": [
    {
      "name": "$CategoryName",
      "difficulty": 0,
      "words": [
        { text: "$Emoji1", "altText": "$EmojiDescription" },
        { text: "$Emoji2", "altText": "$EmojiDescription" },
        { text: "$Emoji3", "altText": "$EmojiDescription" },
        { text: "$Emoji4", "altText": "$EmojiDescription" },
        { text: "$Emoji5", "altText": "$EmojiDescription" },
        ...]
    },
    {
      "name": "$CategoryName",
      "difficulty": 1,
      "words": [
        { text: "$Emoji1", "altText": "$EmojiDescription" },
        { text: "$Emoji2", "altText": "$EmojiDescription" },
        { text: "$Emoji3", "altText": "$EmojiDescription" },
        { text: "$Emoji4", "altText": "$EmojiDescription" },
        { text: "$Emoji5", "altText": "$EmojiDescription" },
        ...]
    },
    {
      "name": "$CategoryName",
      "difficulty": 2,
      "words": [
        "$Word1",
        "$Word2",
        "$Word3",
        "$Word4",
        { "text": "$Word5", "backgroundColor": "$ColorCode"},
        ...]
    },
    {
      "name": "$CategoryName",
      "difficulty": 3,
      "words": [
        "$Word1",
        "$Word2",
        "$Word3",
        "$Word4",
        { "text": "$Word5", "backgroundColor": "$ColorCode"},
        ...]
    }
  ]
}

# About the Background Colors
 * You may OPTIONALLY supply colors to use for the word. ONLY specify a color if it is relevant to the category or puzzle. (e.g. you can make puzzles where the category is "Yellow Words". Or the color is a key clue or flourish to the category)
 * You can use any value that would be valid CSS used like this: `style="background-color: $ColorCode"`
 * All colors in a category DO NOT need to be the same.

# List of Existing Categories
 * The file CATEGORIES.md contains notes from all previous sessions that created games. THIS IS AN IMPORTANT FILE.
 * It contains a summary of all created games so far.
 * It indicates which ids have been used already.
 * Before creating new games, this is the only file you need to read.
 * After you are done creating all your games remember to update this file with your notes.

# Final Instructions
 * Create new word games by creating new JSON files that follow the file format.
 * The file name should include the game id, for example if id=k123 then the file will be `game-123.json`.
 * Kid game ids ALWAYS start with a 'k' and then the id number.
 * The file MUST contain EXACTLY 4 categories.
 * Categories MUST contain AT LEAST 4 words or emojis. If more than 4 words are supplied then 4 random words will be used. This can be desirable, because it increases the replayability of the game!
 * Categories CAN have many more than 4 words (8-12 is great!) BUT only when each word STRONGLY fits the category. Quality over quantity - don't add weak matches just to pad the list.
 * The categories must be VERY SIMPLE for a preschool level audience.
 * Preschoolers love pictures, emojis, shapes, and colors. You are encouraged to use them in the games you create.
 * Preschoolers are learning about words and letter sounds. You are encouraged (BUT NOT REQUIRED) to include a elementary vocabulary in one category per game. The game will read the words aloud for the players, to help them learn words and sounds.
 * The categores in a game DO NOT need to share a theme. They can be totally random categories. In fact, for preschoolers having VERY DIFFERENT CATEGORIES in a game will make it easier to solve.
 * Be Creative, Playful and most of all HAVE FUN 😁