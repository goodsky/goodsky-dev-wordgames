Use your extensive experience with crossword puzzle to judge the difficulty of new puzzles and reword, edit, or remove confusing clues from a puzzle to help curate a high quality game set for beginner crossword solvers.

# Crossword Game Files
In this directory are a list of crossword games in json format. New games will always have the file format game_N.new.json. Games that have already been reviewed will be in the file format game_N.json (without the .new.json extension). You can safely ignore all games that ahve already been reviewed. Your task involves ONLY new games.

The game files will contain an array of crossword ANSWERS each with an array of potential CLUES. You will be responsible for judging the difficulty of both the ANSWER word and the CLUE leading to the answer. The file may contain other fields, but you can safely ignore all other fields that are not the ANSWERS and the CLUES. A sample of the file format is provided below:

{
    "clues": [
        {
            "index": 1,
            "direction": "across",
            "row": 0,
            "col": 1,
            "length": 6,
            "answer": "ANSWER",
            "clues": [
                "$CLUE1",
                "$CLUE2",
                "$CLUE3",
                "$CLUE4",
                ...
            ]
        },
        ...
    ],
    ...
}

# Judging Criteria
You will be judging how challenging the crossword answers and clues would be to solve for beginner level crossword solvers. Answers that are obscure will have a higher difficulty rating. Clues that require specific pop culture references or tricky interpretations have a higher difficulty rating. The available categories for puzzles are as follows:
   - EASY: All answers and clues are solvable by beginner level crossword solvers
   - HARD: Some answers or clues are challenging and will require cross-word clues to solve
   - REJECT: Any answer or clue is UNREASONABLE to expect a beginner level crossword player to solve

After juding a puzzle, you MUST follow these steps:
 1. Rename the file from game_N.new.json to game_N.json. (i.e. remove the .new)
 2. Add a new field to the top of the JSON file with your judgement following the format shown below

{
    "difficulty": "$your_rating",
    "clues": [
        ...
    ],
    ...
}

# Additional Editing Options
You are encouraged to edit or remove CLUES that are increasing the difficulty rating of a puzzle. Especially if a clue is potentially causing a REJECT judgement. You are able to do all of the following actions:
 1. Remove obscure or misleading CLUES strings from the clue array
 2. Edit CLUE strings to remove ambiguity or fix errors

Note that if an ANSWER is UNREASONABLE or OBSCURE leading to a REJECT judgement, you will not be able to change it. NEVER change an ANSWER since that will break the puzzle.

# Final Guidelines
 * Judge the difficulty of crossword games based on the ANSWER words and CLUE strings
 * REJECT games that are too challenging for beginner crossword puzzle solvers.
 * EDIT the CLUE strings when you can help lower the difficulty of the crossword.
 * NEVER change the ANSWER words
 * NEVER remove an ANSWER word
 * Remember that crosswords are a playful and fun way to spend time. Be creative. And have fun!