**# LICHESS DATABASE GAME ANALYSIS**

**## OVERVIEW**

This repository provides a tool to extract and analyze chess games from the Lichess database for a specific time control. It processes PGN files, extracts key features from each game, and generates structured data for analysis.

**## FEATURES**

- Extracts all games of a specified time control (e.g., Bullet, Blitz, Rapid, Classical)
- Parses PGN files efficiently
- Computes key game features such as:
  - Move accuracy
  - Blunders and mistakes
  - Opening classification
  - Average centipawn loss (ACPL)
  - Number of moves and game duration
  - Result and player ratings
- Outputs a structured CSV file for further analysis

**## REQUIREMENTS**

- Python 3.7+
- Required Python libraries:
  ```bash
  pip install python-chess pandas tqdm
  ```

**## USAGE**

1. Download the Lichess PGN database file for the desired time period.
2. Run the script specifying the time control and input file:
   ```bash
   python analyze_lichess.py --pgn lichess_games.pgn --time_control blitz --output results.csv
   ```
3. The script will process the games and generate `results.csv` with extracted features.

**## CSV OUTPUT FORMAT**

The generated CSV file contains the following columns:

| Column         | Description                        |
|----------------|------------------------------------|
| Game ID        | Unique identifier for each game    |
| White Player   | Username of White                  |
| Black Player   | Username of Black                  |
| White Rating   | Elo rating of White                |
| Black Rating   | Elo rating of Black                |
| Result         | 1-0, 0-1, or 1/2-1/2               |
| Time Control   | Time control of the game           |
| Opening        | ECO code and opening name          |
| Moves          | Number of moves played             |
| ACPL White     | Average centipawn loss for White   |
| ACPL Black     | Average centipawn loss for Black   |
| Blunders White | Count of blunders by White         |
| Blunders Black | Count of blunders by Black         |
| Mistakes White | Count of mistakes by White         |
| Mistakes Black | Count of mistakes by Black         |

**## EXAMPLE OUTPUT**

| Game ID | White Player | Black Player | White Rating | Black Rating | Result | Time Control | Opening          | Moves | ACPL White | ACPL Black | Blunders White | Blunders Black | Mistakes White | Mistakes Black |
|---------|---------------|--------------|--------------|--------------|--------|--------------|------------------|-------|-------------|-------------|----------------|----------------|----------------|----------------|
| xyz123  | Player1       | Player2      | 1800         | 1750         | 1-0    | Blitz        | Sicilian Defense | 40    | 32          | 45          | 1              | 2              | 3              | 4              |

**## TO-DO**

- Add support for additional feature extraction
- Optimize processing for large datasets
- Provide visualization tools for analyzed data

**## CONTRIBUTIONS**

Contributions are welcome! Feel free to submit a pull request or open an issue if you have suggestions or improvements.

**## LICENSE**

MIT License
