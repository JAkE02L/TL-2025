import random
import time
import json
import os

# Global variables to simulate server state
_connected_players = [
    {"id": 1, "name": "Alice", "status": "ready", "score": 0},
    {"id": 2, "name": "Bob", "status": "ready", "score": 0},
    {"id": 3, "name": "Charlie", "status": "joined", "score": 0}
]

_current_question_id = 0
_quiz_active = False
_last_update = time.time()

def get_players():
    """
    Simulates fetching current players from a server
    In a real app, this would make an API call
    """
    global _connected_players, _last_update
    
    # Occasionally add a new player or update status
    current_time = time.time()
    if current_time - _last_update > 5:
        _last_update = current_time
        
        # 30% chance to add a new player if quiz is active
        if _quiz_active and random.random() < 0.3 and len(_connected_players) < 10:
            new_names = ["David", "Emma", "Frank", "Grace", "Henry", "Isabel", "Jack"]
            available_names = [name for name in new_names 
                               if name not in [p["name"] for p in _connected_players]]
            
            if available_names:
                new_name = random.choice(available_names)
                new_id = max([p["id"] for p in _connected_players]) + 1
                _connected_players.append({
                    "id": new_id,
                    "name": new_name,
                    "status": "joined",
                    "score": 0
                })
                
        # 20% chance to change a player's status
        if random.random() < 0.2 and _connected_players:
            player = random.choice(_connected_players)
            if player["status"] == "joined":
                player["status"] = "ready"
            
        # 10% chance to update scores if quiz is active
        if _quiz_active and random.random() < 0.1:
            for player in _connected_players:
                if player["status"] == "ready" and random.random() < 0.5:
                    player["score"] += 1
    
    return _connected_players

def add_player(name):
    """
    Simulates adding a new player to the server
    """
    global _connected_players
    
    # Check if player already exists
    if name in [p["name"] for p in _connected_players]:
        return False
    
    new_id = max([p["id"] for p in _connected_players]) + 1 if _connected_players else 1
    
    _connected_players.append({
        "id": new_id,
        "name": name,
        "status": "joined",
        "score": 0
    })
    
    return True

def start_quiz():
    """
    Simulates starting the quiz on the server
    """
    global _quiz_active, _current_question_id
    _quiz_active = True
    _current_question_id = 0
    return {"success": True}

def end_quiz():
    """
    Simulates ending the quiz on the server
    """
    global _quiz_active
    _quiz_active = False
    return {"success": True}

def get_current_question_id():
    """
    Gets the current question ID from the server
    """
    return _current_question_id

def set_current_question(question_id):
    """
    Sets the current question ID on the server
    """
    global _current_question_id
    _current_question_id = question_id
    return {"success": True}

def reset_players():
    """
    Resets the player list for testing purposes
    """
    global _connected_players
    _connected_players = [
        {"id": 1, "name": "Alice", "status": "ready", "score": 0},
        {"id": 2, "name": "Bob", "status": "ready", "score": 0},
        {"id": 3, "name": "Charlie", "status": "joined", "score": 0}
    ]
    return True