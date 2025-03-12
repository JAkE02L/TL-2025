import json
import os
import datetime
import pandas as pd

# Path to store scores
SCORES_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'scores.json')

def initialize_scores_file():
    """Create scores file if it doesn't exist"""
    if not os.path.exists(SCORES_FILE):
        os.makedirs(os.path.dirname(SCORES_FILE), exist_ok=True)
        with open(SCORES_FILE, 'w') as f:
            json.dump({"scores": []}, f)

def load_scores():
    """Load all scores from storage"""
    initialize_scores_file()
    try:
        with open(SCORES_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading scores: {e}")
        return {"scores": []}

def save_score(player_name, score, total_questions, time_taken=None):
    """Save a new score entry"""
    scores_data = load_scores()
    
    # Generate timestamp
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Create new score entry
    new_score = {
        "id": len(scores_data["scores"]) + 1,
        "player": player_name,
        "score": score,
        "total": total_questions,
        "percentage": round((score / total_questions) * 100, 1),
        "timestamp": timestamp,
        "time_taken": time_taken or "N/A"  # Time taken to complete quiz
    }
    
    # Add to scores list
    scores_data["scores"].append(new_score)
    
    # Save back to file
    try:
        with open(SCORES_FILE, 'w') as f:
            json.dump(scores_data, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving score: {e}")
        return False

def get_player_scores(player_name):
    """Get scores for a specific player"""
    scores_data = load_scores()
    player_scores = [s for s in scores_data["scores"] if s["player"] == player_name]
    return player_scores

def get_leaderboard(limit=10):
    """Get the leaderboard data - top scores by percentage"""
    scores_data = load_scores()
    
    if not scores_data["scores"]:
        return []
    
    # Convert to DataFrame for easier manipulation
    df = pd.DataFrame(scores_data["scores"])
    
    # Get the highest score per player
    top_scores = df.sort_values("percentage", ascending=False).groupby("player", as_index=False).first()
    
    # Sort by percentage and add rank
    top_scores = top_scores.sort_values("percentage", ascending=False).head(limit)
    top_scores["rank"] = range(1, len(top_scores) + 1)
    
    return top_scores.to_dict('records')

def get_player_ranking(player_name):
    """Get ranking information for a specific player"""
    leaderboard = get_leaderboard(limit=None)
    
    if not leaderboard:
        return {"rank": "N/A", "total_players": 0}
    
    # Find player in leaderboard
    player_entry = next((entry for entry in leaderboard if entry["player"] == player_name), None)
    
    if player_entry:
        return {
            "rank": player_entry["rank"],
            "total_players": len(leaderboard)
        }
    else:
        return {"rank": "Not ranked", "total_players": len(leaderboard)}