import dash
from dash import html, dcc, callback, Input, Output, State, ctx
import dash_bootstrap_components as dbc
import json
import os
import random
from dash.exceptions import PreventUpdate
from components.quiz_card import create_quiz_card
from utils.mock_server import get_current_question_id
from utils.helpers import load_quiz_data
from utils.score_manager import save_score

# Register the page
dash.register_page(__name__, title="Quiz Game - Play")

# Page layout
layout = dbc.Container([
    dcc.Store(id='quiz-state', data={
        'current_question': 0,
        'score': 0,
        'answered': [], 
        'quiz_complete': False,
        'player_name': None,
        'server_question': None  # Track server's current question
    }),
    
    dbc.Row([
        dbc.Col([
            html.H2("Quiz Challenge", className="text-center mb-4"),
            html.Div(id="quiz-player-info", className="text-center mb-3"),
            html.Div(id="quiz-container", className="p-3 border rounded")
        ], width={"size": 8, "offset": 2})
    ]),
    
    # Add a polling interval to check for server updates
    dcc.Interval(id="quiz-server-poll", interval=3000),
    
    # Hidden div for triggering callbacks
    dcc.Location(id='url', refresh=True),
    html.Div(id='page-load-trigger', style={'display': 'none'})
], fluid=True, className="py-4")

# Callback to initialize quiz and handle page load
@callback(
    Output("quiz-container", "children"),
    Output("quiz-player-info", "children"),
    Output("quiz-state", "data"),
    [Input("page-load-trigger", "children"),
     Input("url", "search")],
    [State("quiz-state", "data")]
)
def initialize_quiz(_, search, quiz_state):
    # Extract player name from URL if available
    player_name = "Player"
    if search and "player=" in search:
        player_name = search.split("player=")[1].split("&")[0]
    
    # Update player name in state
    new_state = quiz_state.copy()
    new_state["player_name"] = player_name
    
    # Get questions data
    quiz_data = load_quiz_data()
    questions = quiz_data.get("questions", [])
    
    if not questions:
        return html.Div("No questions found. Please check your data file.", className="text-center p-5"), html.Div(), new_state
    
    # Get first question
    question = questions[0]
    
    # Create quiz card for the first question
    quiz_card = create_quiz_card(
        question_text=question["question"],
        options=question["options"],
        question_number=1,
        total_questions=len(questions)
    )
    
    # Create player info component
    player_info = html.Div([
        html.H4(f"Player: {player_name}", className="mb-2"),
        html.Div([
            html.Span("Score: ", className="fw-bold"),
            html.Span("0", id="player-score")
        ], className="d-inline-block me-3"),
        dbc.Badge("Waiting for host...", color="warning", id="game-status-badge")
    ])
    
    return quiz_card, player_info, new_state

# Add a new callback for polling server updates
@callback(
    Output("quiz-container", "children", allow_duplicate=True),
    Output("quiz-state", "data", allow_duplicate=True),
    Output("game-status-badge", "children"),
    Output("game-status-badge", "color"),
    Input("quiz-server-poll", "n_intervals"),
    State("quiz-state", "data"),
    prevent_initial_call=True
)
def poll_server_updates(n_intervals, quiz_state):
    # Get current server question ID
    server_question_id = get_current_question_id()
    
    # If server question hasn't changed or we've already answered this question, do nothing
    if (quiz_state.get("server_question") == server_question_id or
            server_question_id in [a.get("question_id") for a in quiz_state.get("answered", [])]):
        return dash.no_update, dash.no_update, "In Progress", "success"
    
    # Get questions data
    quiz_data = load_quiz_data()
    questions = quiz_data.get("questions", [])
    
    if not questions or server_question_id >= len(questions):
        return dash.no_update, dash.no_update, "Error loading question", "danger"
    
    # Get the new question
    question = questions[server_question_id]
    
    # Update state with new server question
    new_state = quiz_state.copy()
    new_state["server_question"] = server_question_id
    new_state["current_question"] = server_question_id
    
    # Create new quiz card
    quiz_card = create_quiz_card(
        question_text=question["question"],
        options=question["options"],
        question_number=server_question_id + 1,
        total_questions=len(questions)
    )
    
    # Add a message showing the question has been updated
    updated_container = html.Div([
        dbc.Alert("The host has advanced to a new question!", color="info", dismissable=True),
        quiz_card
    ])
    
    return updated_container, new_state, "New Question", "info"

# Keep the main quiz logic callback with minor modifications
@callback(
    Output("quiz-container", "children", allow_duplicate=True),
    Output("quiz-state", "data", allow_duplicate=True),
    Output("url", "href", allow_duplicate=True),
    Output("player-score", "children"),
    [Input("submit-answer", "n_clicks")],
    [State("answer-options", "value"),
     State("quiz-state", "data")],
    prevent_initial_call=True
)
def update_quiz(n_clicks, selected_answer, quiz_state):
    if not n_clicks or selected_answer is None:
        raise PreventUpdate
    
    # Get questions data
    quiz_data = load_quiz_data()
    questions = quiz_data.get("questions", [])
    
    if not questions:
        return html.Div("No questions found."), quiz_state, dash.no_update, "0"
    
    # Get current question index
    current_idx = quiz_state.get("current_question", 0)
    current_question = questions[current_idx]
    
    # Check if answer is correct
    is_correct = selected_answer == current_question["correct_answer"]
    
    # Update quiz state
    new_score = quiz_state.get("score", 0) + (1 if is_correct else 0)
    answered = quiz_state.get("answered", [])
    answered.append({
        "question": current_question["question"],
        "question_id": current_idx,
        "user_answer": selected_answer,
        "correct_answer": current_question["correct_answer"],
        "is_correct": is_correct
    })
    
    # Update quiz state
    new_state = quiz_state.copy()
    new_state["score"] = new_score
    new_state["answered"] = answered
    
    # Check if this is the last question
    is_last_question = current_idx == len(questions) - 1
    quiz_complete = is_last_question and len(answered) == len(questions)
    
    # If quiz is complete, save score and redirect to results
    if quiz_complete:
        player_name = quiz_state.get("player_name", "Anonymous")
        save_score(player_name, new_score, len(questions))
        new_state["quiz_complete"] = True
        return html.Div("Redirecting to results..."), new_state, f"/results?player={player_name}&score={new_score}&total={len(questions)}", str(new_score)
        
    # Show feedback for the answer
    feedback = html.Div([
        dbc.Alert(
            f"{'Correct!' if is_correct else 'Incorrect.'} {current_question['correct_answer'] if not is_correct else ''}",
            color="success" if is_correct else "danger",
            className="mt-3"
        ),
        html.P("Waiting for the host to advance to the next question...", className="mt-3")
    ])
    
    # Disable the submit button in the current card
    disabled_card = html.Div([
        # Card content as before...
    ])
    
    return disabled_card, new_state, dash.no_update, str(new_score)
    
