import chess.pgn
import chess.engine
import csv
import math
import time
from datetime import timedelta
# print("wtf")
def win_percent(cp):
    """Convert centipawn evaluation to Win% using Lichess's logistic function."""
    cp = max(min(cp, 1000), -1000)  # Cap evaluations at ±1000
    return 50 + 50 * ((2 / (1 + math.exp(-0.00368208 * cp))) - 1)

def calculate_move_accuracy(delta_win, centipawn_loss):
    """Calculate move accuracy based on both win percentage loss and centipawn loss."""
    if delta_win == 0 and centipawn_loss == 0:
        return 100
    
    win_based_accuracy = max(0, min(100, 100 - (delta_win * 3.5)))
    cp_based_accuracy = max(0, min(100, 100 - (centipawn_loss * 0.2)))
    base_accuracy = min(win_based_accuracy, cp_based_accuracy)
    
    if delta_win >= 20 or centipawn_loss >= 200:  # Blunder
        return min(19, base_accuracy * 0.15)
    elif delta_win >= 10 or centipawn_loss >= 100:  # Mistake
        return min(39, base_accuracy * 0.35)
    elif delta_win >= 5 or centipawn_loss >= 50:  # Inaccuracy
        return min(59, base_accuracy * 0.55)
    else:
        return min(94, base_accuracy * 0.95)

def analyze_game(game, engine):
    """Analyze a chess game and return key metrics."""
    board = game.board()
    stats = {
        'white': {'blunders': 0, 'mistakes': 0, 'inaccuracies': 0, 'total_centipawn_loss': 0, 
                 'total_accuracy': 0, 'best_move_count': 0, 'move_count': 0},
        'black': {'blunders': 0, 'mistakes': 0, 'inaccuracies': 0, 'total_centipawn_loss': 0, 
                 'total_accuracy': 0, 'best_move_count': 0, 'move_count': 0}
    }
    move_count = 0
    
    for move in game.mainline_moves():
        move_count += 1
        current_board = board.copy()
        is_white = current_board.turn
        player = 'white' if is_white else 'black'
        
        best_analysis = engine.analyse(current_board, chess.engine.Limit(time=0.1))
        best_move = best_analysis["pv"][0] if best_analysis["pv"] else None
        best_score = best_analysis["score"].white()
        best_eval = best_score.score() if not best_score.is_mate() else 1000 * (1 if best_score.mate() > 0 else -1)
        best_eval = max(min(best_eval, 1000), -1000)
        
        board.push(move)
        played_analysis = engine.analyse(board, chess.engine.Limit(time=0.1))
        played_score = played_analysis["score"].white()
        played_eval = played_score.score() if not played_score.is_mate() else 1000 * (1 if played_score.mate() > 0 else -1)
        played_eval = max(min(played_eval, 1000), -1000)
        
        if not is_white:
            best_eval = -best_eval
            played_eval = -played_eval
            
        centipawn_loss = max(best_eval - played_eval, 0)
        stats[player]['total_centipawn_loss'] += centipawn_loss
        
        best_win = win_percent(best_eval)
        played_win = win_percent(played_eval)
        delta_win = best_win - played_win
        
        move_accuracy = calculate_move_accuracy(delta_win, centipawn_loss)
        stats[player]['total_accuracy'] += move_accuracy
        stats[player]['move_count'] += 1
        
        if delta_win >= 20 or centipawn_loss >= 200:
            stats[player]['blunders'] += 1
        elif delta_win >= 10 or centipawn_loss >= 100:
            stats[player]['mistakes'] += 1
        elif delta_win >= 5 or centipawn_loss >= 50:
            stats[player]['inaccuracies'] += 1
        
        if move == best_move:
            stats[player]['best_move_count'] += 1

    results = {}
    for player in ['white', 'black']:
        move_count = stats[player]['move_count']
        if move_count > 0:
            avg_centipawn_loss = stats[player]['total_centipawn_loss'] / move_count
            avg_accuracy = stats[player]['total_accuracy'] / move_count
            best_move_percent = (stats[player]['best_move_count'] / move_count) * 100
        else:
            avg_centipawn_loss = avg_accuracy = best_move_percent = 0
            
        results.update({
            f"{player}_moves": move_count,
            f"{player}_blunders": stats[player]['blunders'],
            f"{player}_mistakes": stats[player]['mistakes'],
            f"{player}_inaccuracies": stats[player]['inaccuracies'],
            f"{player}_avg_centipawn_loss": round(avg_centipawn_loss, 1),
            f"{player}_accuracy": round(avg_accuracy, 1),
            f"{player}_best_move_percent": round(best_move_percent, 1)
        })
    
    return results

# Input PGN file
pgn_file = "first_10_games.pgn"

# Define output file
output_file = "lichess_600_games.csv"

# Initialize Stockfish engine
engine = chess.engine.SimpleEngine.popen_uci(r"C:\Users\sanya\OneDrive\Desktop\chess\stockfish\stockfish-windows-x86-64-avx2.exe")

# Open CSV file in append mode
csv_file = open(output_file, "a", newline="")
csv_writer = csv.writer(csv_file)

# Write headers only if file is empty
if csv_file.tell() == 0:
    headers = [
        "Game Link", "White Elo", "Black Elo", "White Rating Diff", "Black Rating Diff", 
        "Opening", "Time Control", "Result", "Termination",
        "White Accuracy", "Black Accuracy", 
        "White Blunders", "White Mistakes", "White Inaccuracies",
        "Black Blunders", "Black Mistakes", "Black Inaccuracies",
        "White Avg CPL", "Black Avg CPL",
        "White Best Move %", "Black Best Move %"
    ]
    csv_writer.writerow(headers)

TARGET_GAMES = 5000
GAMES_TO_SKIP = 5000  # Skip the first 5000 games that were already analyzed
game_count = 0
total_start_time = time.time()
games_analyzed = 0
total_analysis_time = 0
games_skipped = 0
games_to_skip_remaining = GAMES_TO_SKIP

print(f"\n🎮 Starting analysis of games {GAMES_TO_SKIP+1} to {GAMES_TO_SKIP+TARGET_GAMES}...")
print("=" * 60)

# Read PGN file and analyze games
with open(pgn_file, "r", encoding="utf-8") as f:
    while True:
        game = chess.pgn.read_game(f)
        if game is None or game_count >= TARGET_GAMES:  # Stop after target games
            break
        
        time_control = game.headers.get("TimeControl", "N/A")

        if time_control == "600+0":
            if games_to_skip_remaining > 0:
                games_to_skip_remaining -= 1
                continue
                
            white = game.headers.get("White", "Unknown")
            black = game.headers.get("Black", "Unknown")
            white_elo = game.headers.get("WhiteElo", "N/A")
            black_elo = game.headers.get("BlackElo", "N/A")
            result = game.headers.get("Result", "N/A")

            # Calculate estimated time remaining
            if games_analyzed > 0:
                avg_time = total_analysis_time / games_analyzed
                remaining_games = TARGET_GAMES - game_count
                est_remaining_time = avg_time * remaining_games
                eta = timedelta(seconds=int(est_remaining_time))
            else:
                eta = "Calculating..."

            print(f"\n{'='*60}")
            print(f"Analyzing Game {game_count + 1}/{TARGET_GAMES} (Overall game {GAMES_TO_SKIP + game_count + 1})")
            print(f"Players: {white} ({white_elo}) vs {black} ({black_elo})")
            print(f"Result: {result}")
            print(f"ETA: {eta}")
            print(f"{'='*60}")

            # Start timing this game's analysis
            game_start_time = time.time()

            # Extract game features
            site = game.headers.get("Site", "N/A")
            white_diff = game.headers.get("WhiteRatingDiff", "N/A")
            black_diff = game.headers.get("BlackRatingDiff", "N/A")
            opening = game.headers.get("Opening", "N/A")
            termination = game.headers.get("Termination", "N/A")

            # Analyze the game
            analysis = analyze_game(game, engine)

            # Calculate time taken for this game
            game_time = time.time() - game_start_time
            total_analysis_time += game_time

            # Print analysis results
            print("\nAnalysis Results:")
            print(f"White Accuracy: {analysis['white_accuracy']}% (Avg CPL: {analysis['white_avg_centipawn_loss']})")
            print(f"Black Accuracy: {analysis['black_accuracy']}% (Avg CPL: {analysis['black_avg_centipawn_loss']})")
            print("\nWhite Stats:")
            print(f"Blunders: {analysis['white_blunders']}, Mistakes: {analysis['white_mistakes']}, Inaccuracies: {analysis['white_inaccuracies']}")
            print(f"Best Moves: {analysis['white_best_move_percent']}%")
            print("\nBlack Stats:")
            print(f"Blunders: {analysis['black_blunders']}, Mistakes: {analysis['black_mistakes']}, Inaccuracies: {analysis['black_inaccuracies']}")
            print(f"Best Moves: {analysis['black_best_move_percent']}%")
            print(f"\nTime taken for this game: {timedelta(seconds=int(game_time))}")

            # Write to CSV
            csv_writer.writerow([
                site, white_elo, black_elo, white_diff, black_diff, 
                opening, time_control, result, termination,
                analysis['white_accuracy'], analysis['black_accuracy'],
                analysis['white_blunders'], analysis['white_mistakes'], analysis['white_inaccuracies'],
                analysis['black_blunders'], analysis['black_mistakes'], analysis['black_inaccuracies'],
                analysis['white_avg_centipawn_loss'], analysis['black_avg_centipawn_loss'],
                analysis['white_best_move_percent'], analysis['black_best_move_percent']
            ])
            
            game_count += 1
            games_analyzed += 1
            
            # Print progress update
            elapsed_time = timedelta(seconds=int(time.time() - total_start_time))
            print(f"\nProgress Update:")
            print(f"Games analyzed: {game_count}/{TARGET_GAMES} ({(game_count/TARGET_GAMES)*100:.1f}%)")
            print(f"Time elapsed: {elapsed_time}")
            
        else:
            games_skipped += 1
            if games_skipped % 1000 == 0:  # Print skipped games count every 1000 games
                print(f"\rSkipped games (non-600+0): {games_skipped}", end="")

# Close files
csv_file.close()
engine.quit()

total_time = time.time() - total_start_time
avg_time_per_game = total_analysis_time / games_analyzed if games_analyzed > 0 else 0

print("\n" + "="*60)
print("✅ Analysis complete!")
print("="*60)
print(f"Total 600+0 games analyzed: {game_count}/{TARGET_GAMES}")
print(f"Total games skipped: {games_skipped}")
print(f"\nTime Statistics:")
print(f"Total time taken: {timedelta(seconds=int(total_time))}")
print(f"Total analysis time: {timedelta(seconds=int(total_analysis_time))}")
print(f"Average time per game: {timedelta(seconds=int(avg_time_per_game))}")
print(f"Data saved to: {output_file}")
print("="*60)