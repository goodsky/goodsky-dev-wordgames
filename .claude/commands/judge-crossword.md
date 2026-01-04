# Crossword Clue Difficulty Rating

Rate the difficulty of crossword clues for beginner solvers using the provided Python scripts.

## Instructions

Follow these steps in order. DO NOT use any other methods to rate the crossword clues. If these steps do not work, ask for help from the user.

⚠️These instructions assume your working directory is set to `server/data/crossword`. You may need to change your directory to find the scripts.⚠️

### Step 1: Get the Next Puzzle
Run the `judge_next.py` script to begin judging a new crossword puzzle.

```bash
./judge_next.py
```

If the script says there are no new games to judge, run `archive_clues.py 20 20` to archive old puzzles and stop working:

```bash
./archive_clues.py 20 20
```

Otherwise, continue to the next step.

### Step 2: Read the Ratings File
Read the generated `game_N.ratings.tsv` file that was created by the script.

### Step 3: Rate Each Clue
For each row in the TSV, look at the CLUE and ANSWER columns and fill in the DIFFICULTY value with one of:
- **EASY**
- **HARD**
- **REJECT**

Use the Difficulty Guidelines section below for detailed instructions.

### Step 4: Find Missing Easy Clues
Run the `edit_clues.py --find-hard` command to identify any answers that are missing an EASY difficulty clue:

```bash
./edit_clues.py --find-hard <game_N.ratings.tsv>
```

### Step 5: (Optional) Add Custom Easy Clues
If you can think of an EASY clue for any answers that do not have one, you MAY run the `edit_clues.py --add-clue` command to add an EASY clue for an answer.

⚠️ If an answer has NO POSSIBLE easy clue, skip this step for that answer. It is okay to skip if an answer is inherently obscure. ⚠️


```bash
./edit_clues.py --add-clue <game_N.ratings.tsv> "<Answer>" "<Clue>" "EASY"
```

Consider adding 3-5 custom clues if possible. 

### Step 6: Commit Your Ratings
Run the `judge_commit.py` script to commit your work:

```bash
./judge_commit.py <game_N.ratings.tsv>
```

### Step 7: Continue
Return to Step 1 to continue judging the next puzzle. Keep going until either:
- You've been instructed to stop
- The scripts say there are no games left

---

# Difficulty Guidelines

## Beginner Crossword Solvers
- These crossword puzzles are intended for beginner solvers.
- Our beginner solvers are more knowledgeable in math and science. Consider these categories as EASY.
- Our beginner solvers do not get cultural references from before 2013. Consider those HARD. Cultural references from after 2013 may be EASY. Use your judgement.

## Rating Criteria

### EASY
- Common knowledge
- Straightforward definition
- May be math, science, or post-2013 cultural references
- No obscure references

### HARD
- Requires specific cultural references
- Challenging wordplay
- Cryptics

### REJECT
- References to other clues that are unavailable
- Incorrect, offensive, or too obscure to expect new solvers to know

---

## Final Reminders
- Use the scripts to create new `*.ratings.tsv` files and then use the difficulty guidelines to fill in the DIFFICULTY column.
- Run the scripts to commit your ratings to the game file.
- Continue judging games until either you've been instructed to stop or the scripts say there are no games left.
- Remember, crosswords are meant to be fun! Keep a playful and fun attitude while judging. Have fun!
