import json
import os
import random

def load_quiz_data():
    """
    Loads quiz questions from the JSON file
    """
    try:
        script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_path = os.path.join(script_dir, 'data', 'questions.json')
        
        with open(data_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading quiz data: {e}")
        return {"questions": []}

def get_random_questions(questions, count=5):
    """
    Get a random selection of questions
    """
    if len(questions) <= count:
        return questions
    return random.sample(questions, count)

def calculate_score(user_answers, correct_answers):
    """
    Calculate the user's score based on their answers
    """
    score = 0
    for user_ans, correct_ans in zip(user_answers, correct_answers):
        if user_ans == correct_ans:
            score += 1
    return score

def format_time_remaining(seconds):
    """
    Format seconds into a MM:SS display string
    """
    minutes = seconds // 60
    seconds_remainder = seconds % 60
    return f"{minutes}:{seconds_remainder:02d}"