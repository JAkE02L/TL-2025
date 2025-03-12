import dash
from dash import html, dcc, callback, Input, Output, State, ctx, ClientsideFunction
import dash_bootstrap_components as dbc
import json
import time
from dash.exceptions import PreventUpdate
from utils.helpers import load_quiz_data
from utils.mock_server import get_players, start_quiz, end_quiz, set_current_question
from components.quiz_card import create_quiz_card

dash.register_page(__name__, path="/host", title="Quiz Game - Host View")

# Host view layout
layout = dbc.Container([
    dcc.Store(id='host-state', data={
        'current_question': 0,
        'timer_running': False,
        'time_left': 30,
        'quiz_started': False,
        'quiz_ended': False,
        'last_player_count': 0  # Track player count to detect changes
    }),
    
    dbc.Row([
        # Left column: Question display
        dbc.Col([
            html.H2("Quiz Host Control Panel", className="text-center mb-4"),
            html.Div(id="host-question-display", className="mb-4"),
            
            # Quiz controls
            dbc.Card([
                dbc.CardBody([
                    html.H4("Quiz Controls", className="mb-3"),
                    
                    # Timer display and controls
                    html.Div([
                        html.H5([
                            "Time Remaining: ",
                            html.Span(id="timer-display", children="30")
                        ], className="d-inline-block me-3"),
                        
                        dbc.ButtonGroup([
                            dbc.Button("Start", id="start-timer-btn", color="success", 
                                      className="me-2", disabled=False),
                            dbc.Button("Pause", id="pause-timer-btn", color="warning", 
                                      className="me-2", disabled=True),
                            dbc.Button("Reset", id="reset-timer-btn", color="danger", 
                                      className="me-2")
                        ], className="mb-3 d-inline-block")
                    ], className="d-flex justify-content-between align-items-center mb-3"),
                    
                    # Navigation controls
                    dbc.ButtonGroup([
                        dbc.Button("Previous", id="prev-question-btn", color="secondary", 
                                  className="me-2"),
                        dbc.Button("Next", id="next-question-btn", color="primary")
                    ], className="mb-3 d-flex justify-content-center")
                ])
            ], className="mb-4")
        ], width=8),
        
        # Right column: Player list
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H4("Connected Players", className="mb-0")),
                dbc.CardBody([
                    html.Div(id="player-count", className="mb-3 fw-bold"),
                    
                    # Player list table
                    html.Div(
                        id="player-list-container",
                        className="table-responsive",
                        style={"maxHeight": "400px", "overflowY": "auto"}
                    ),
                    
                    # Action buttons
                    html.Div([
                        dbc.Button("Start Quiz", id="start-quiz-btn", color="success", 
                                  className="me-2"),
                        dbc.Button("End Quiz", id="end-quiz-btn", color="danger"),
                    ], className="d-flex justify-content-center mt-3")
                ])
            ])
        ], width=4)
    ]),
    
    # Interval for the timer
    dcc.Interval(id="timer-interval", interval=1000, disabled=True),
    
    # Interval for polling player data (every 2 seconds)
    dcc.Interval(id="player-poll-interval", interval=2000, disabled=False),
    
    # Hidden div for storing the questions
    html.Div(id="questions-store", style={"display": "none"}),
    
    # Toast for notifications
    dbc.Toast(
        id="host-notification",
        header="Notification",
        is_open=False,
        dismissable=True,
        duration=4000,
        icon="info",
        style={"position": "fixed", "top": 66, "right": 10, "width": 350},
    )
], fluid=True, className="py-4")

# New callback for polling player data
@callback(
    Output("player-list-container", "children"),
    Output("player-count", "children"),
    Output("host-notification", "children", allow_duplicate=True),
    Output("host-notification", "is_open", allow_duplicate=True),
    Output("host-notification", "header", allow_duplicate=True),
    Output("host-state", "data", allow_duplicate=True),
    Input("player-poll-interval", "n_intervals"),
    State("host-state", "data"),
    prevent_initial_call=True
)
def update_player_list(n_intervals, host_state):
    # Fetch players from our mock server
    players = get_players()
    
    # Create the table with player data
    player_table = dbc.Table([
        html.Thead(html.Tr([
            html.Th("#"),
            html.Th("Name"),
            html.Th("Status"),
            html.Th("Score")
        ])),
        html.Tbody(id="player-list-body", children=[
            html.Tr([
                html.Td(player["id"]),
                html.Td(player["name"]),
                html.Td(html.Span(
                    player["status"], 
                    className=f"badge bg-{'success' if player['status'] == 'ready' else 'warning'}"
                )),
                html.Td(player["score"])
            ]) for player in players
        ])
    ], bordered=True, hover=True, responsive=True, striped=True)
    
    # Update player count text
    player_count_text = f"Players: {len(players)}"
    
    # Check if player count changed for notification
    last_count = host_state.get("last_player_count", 0)
    new_state = host_state.copy()
    new_state["last_player_count"] = len(players)
    
    # If player count increased, show notification
    if len(players) > last_count and last_count > 0:
        # Find the new player(s)
        new_players = [p["name"] for p in players if p["id"] > last_count]
        if new_players:
            msg = f"New player joined: {', '.join(new_players)}"
            return player_table, player_count_text, msg, True, "Player Update", new_state
    
    # No notification
    return player_table, player_count_text, "", False, "", new_state

# Callback to initialize host view and load questions
@callback(
    Output("host-question-display", "children"),
    Output("questions-store", "children"),
    Input("host-state", "data")
)
def initialize_host_view(host_state):
    # Load quiz data
    quiz_data = load_quiz_data()
    questions = quiz_data.get("questions", [])
    
    if not questions:
        return html.Div("No questions found. Please check your data file.", className="text-center p-5"), ""
    
    # Get current question index
    current_idx = host_state.get("current_question", 0)
    
    # Make sure we don't go out of bounds
    if current_idx >= len(questions):
        current_idx = 0
    
    question = questions[current_idx]
    
    # Create a read-only version of the quiz card (no submit button)
    question_card = html.Div([
        dbc.Card([
            dbc.CardBody([
                html.H4(question["question"], className="card-title"),
                html.P(f"Question {current_idx + 1} of {len(questions)}", className="text-muted"),
                html.Hr(),
                html.Div([
                    dbc.ListGroup([
                        dbc.ListGroupItem(
                            option,
                            color="light",
                            className="d-flex align-items-center"
                        ) for option in question["options"]
                    ])
                ]),
                html.Div([
                    html.Small(f"Correct answer: {question['correct_answer']}", 
                              className="text-muted font-italic")
                ], className="mt-3")
            ])
        ], className="quiz-card")
    ])
    
    # Store the questions as JSON
    return question_card, json.dumps(questions)

# Updated callbacks - when navigation happens, update the "server" question ID
@callback(
    Output("host-question-display", "children", allow_duplicate=True),
    Output("host-state", "data", allow_duplicate=True),
    Output("host-notification", "children", allow_duplicate=True),
    Output("host-notification", "is_open", allow_duplicate=True),
    Output("host-notification", "header", allow_duplicate=True),
    Input("next-question-btn", "n_clicks"),
    Input("prev-question-btn", "n_clicks"),
    State("questions-store", "children"),
    State("host-state", "data"),
    prevent_initial_call=True
)
def navigate_questions(next_clicks, prev_clicks, questions_json, host_state):
    triggered_id = ctx.triggered_id
    
    # Parse questions data
    if not questions_json:
        return dash.no_update, dash.no_update, "No quiz data found", True, "Error"
    
    questions = json.loads(questions_json)
    
    # Get current question index
    current_idx = host_state.get("current_question", 0)
    
    # Navigate based on button click
    if triggered_id == "next-question-btn":
        current_idx += 1
        toast_message = "Advanced to next question"
        toast_header = "Navigation"
        toast_open = True
    elif triggered_id == "prev-question-btn":
        current_idx -= 1
        toast_message = "Returned to previous question"
        toast_header = "Navigation"
        toast_open = True
    else:
        return dash.no_update, dash.no_update, "", False, ""
    
    # Bounds checking
    if current_idx < 0:
        current_idx = 0
        toast_message = "Already at the first question"
    elif current_idx >= len(questions):
        current_idx = len(questions) - 1
        toast_message = "Already at the last question"
    
    # Update the "server" with current question ID
    set_current_question(current_idx)
    
    # Update host state
    new_state = host_state.copy()
    new_state["current_question"] = current_idx
    
    # Get the question to display
    question = questions[current_idx]
    
    # Create question card
    question_card = html.Div([
        dbc.Card([
            dbc.CardBody([
                html.H4(question["question"], className="card-title"),
                html.P(f"Question {current_idx + 1} of {len(questions)}", className="text-muted"),
                html.Hr(),
                html.Div([
                    dbc.ListGroup([
                        dbc.ListGroupItem(
                            option,
                            color="light",
                            className="d-flex align-items-center"
                        ) for option in question["options"]
                    ])
                ]),
                html.Div([
                    html.Small(f"Correct answer: {question['correct_answer']}", 
                              className="text-muted font-italic")
                ], className="mt-3")
            ])
        ], className="quiz-card")
    ])
    
    return question_card, new_state, toast_message, toast_open, toast_header

# Updated callback for quiz control buttons - now updates the server
@callback(
    Output("host-notification", "children", allow_duplicate=True),
    Output("host-notification", "is_open", allow_duplicate=True),
    Output("host-notification", "header", allow_duplicate=True),
    Output("host-state", "data", allow_duplicate=True),
    Input("start-quiz-btn", "n_clicks"),
    Input("end-quiz-btn", "n_clicks"),
    State("host-state", "data"),
    prevent_initial_call=True
)
def quiz_control(start_clicks, end_clicks, host_state):
    triggered_id = ctx.triggered_id
    
    # Get current quiz state
    quiz_started = host_state.get("quiz_started", False)
    quiz_ended = host_state.get("quiz_ended", False)
    
    # Handle different button clicks
    if triggered_id == "start-quiz-btn":
        if not quiz_started:
            # Update the server
            start_quiz()
            
            new_state = host_state.copy()
            new_state["quiz_started"] = True
            new_state["quiz_ended"] = False
            new_state["current_question"] = 0  # Reset to first question
            return "Quiz has been started! Players can now join.", True, "Quiz Started", new_state
        else:
            return "Quiz is already in progress.", True, "Info", dash.no_update
    elif triggered_id == "end-quiz-btn":
        if quiz_started and not quiz_ended:
            # Update the server
            end_quiz()
            
            new_state = host_state.copy()
            new_state["quiz_ended"] = True
            return "Quiz has ended. Final scores will be calculated.", True, "Quiz Ended", new_state
        elif not quiz_started:
            return "Cannot end a quiz that hasn't started.", True, "Warning", dash.no_update
        else:
            return "Quiz has already ended.", True, "Info", dash.no_update
    
    return dash.no_update, dash.no_update, dash.no_update, dash.no_update

# Keep the timer callback
@callback(
    Output("timer-display", "children"),
    Output("host-state", "data", allow_duplicate=True),
    Output("timer-interval", "disabled"),
    Output("start-timer-btn", "disabled"),
    Output("pause-timer-btn", "disabled"),
    Input("timer-interval", "n_intervals"),
    Input("start-timer-btn", "n_clicks"),
    Input("pause-timer-btn", "n_clicks"),
    Input("reset-timer-btn", "n_clicks"),
    State("host-state", "data"),
    prevent_initial_call=True
)
def handle_timer(n_intervals, start_clicks, pause_clicks, reset_clicks, host_state):
    triggered_id = ctx.triggered_id
    
    # Get current timer state
    time_left = host_state.get("time_left", 30)
    timer_running = host_state.get("timer_running", False)
    
    # Handle different button clicks
    if triggered_id == "start-timer-btn":
        timer_running = True
    elif triggered_id == "pause-timer-btn":
        timer_running = False
    elif triggered_id == "reset-timer-btn":
        time_left = 30
        timer_running = False
    elif triggered_id == "timer-interval" and timer_running:
        # Decrease time if timer is running
        if time_left > 0:
            time_left -= 1
        else:
            # When timer reaches 0, stop it
            timer_running = False
    
    # Update host state
    new_state = host_state.copy()
    new_state["time_left"] = time_left
    new_state["timer_running"] = timer_running
    
    # Button states
    start_disabled = timer_running
    pause_disabled = not timer_running
    
    return time_left, new_state, not timer_running, start_disabled, pause_disabled