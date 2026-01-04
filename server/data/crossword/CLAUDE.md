# Crossword Clue Difficulty Rating

Your task is to use the provided Python scripts to rate the difficulty of crossword clues for beginner solvers.

## Instructions
Follow the these steps in order. DO NOT use any other methods to rate the crossword clues. If these steps do not work, ask for help from the user.

1. Run the `judge_next.py` script to begin judging a new crossword puzzle. If the script says there are no new games to judge, then you are done and you can stop working! Otherwise, continue to the next step.

2. Read the `game_N.ratings.tsv` file.

3. For each row in the TSV, look at the CLUE and ANSWER column and then fill in the DIFFICULTY value with EASY, HARD, or REJECT. Use the Difficulty Guidelines section for detailed instructions.

5. Run the `edit_clues.py --find-hard <game_N.ratings.tsv>` when you are done to identify any answers that are missing an EASY difficulty clue.

6. (Optional) If you can think of an EASY clue for any of the answers that do not have one, you may run `edit_clues.py --add-clue <game_N.ratings.tsv> "<Answer>" "<Clue>" "EASY"` with your custom generated clue. Consider adding 3-5 if possible. If an answer has NO POSSIBLE easy clue, then skip this step for that answer.

4. Run the `judge_commit.py <game_N.ratings.tsv>` script once you are done to commit your work.

5. Return to step 1 to continue judging the next puzzle.

# Difficulty Guidelines

## Beginner Crossword Solvers
 - These crossword puzzles are intended for beginner solvers.
 - Our beginner solvers are more knowledgeable in math and science. Consider these categories as EASY.
 - Our beginner solvers do not get cultural references from before 2013. Consider those HARD. Cultural references from after 2013 may be EASY. Use your judgement.

## Difficulty Guidelines
### **1 (EASY)**:
   - Common knowledge
   - Straightforward definition
   - May be math, science, or post-2013 cultural references
   - No obscure references

### **2 (HARD)**:
   - Requires specific cultural references
   - Challenging wordplay
   - Cryptics

### **3 (REJECT)**:
   - References to other clues that are unavailable
   - Incorrect, offensive, or too obscure to expect new solvers to know

## Final Reminders
- Use the scripts to create new *.ratings.tsv files and then use the difficulty guidelines to fill in the DIFFICULTY column.
- Run the scripts to commit your ratings to the game file.
- Continue judging games until either you've been instructed to stop or the scripts say there are not games left
- Remember, crosswords are meant to be fun! So keep a playful and fun attitude while judging. Have fun!

