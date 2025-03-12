import dash
from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
import plotly.express as px
import plotly.graph_objects as go
from utils.score_manager import get_player_scores, get_player_ranking

dash.register_page(__name__, title="Quiz Game - Results")

# Results page layout
layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H2("Quiz Results", className="text-center mb-4"),
            html.Div(id="results-player-info", className="text-center mb-3"),
            html.Div(id="results-container")
        ], width={"size": 10, "offset": 1})
    ]),
    
    # Hidden div for triggering callbacks
    dcc.Location(id='results-url', refresh=False),
], fluid=True, className="py-4")

@callback(
    Output("results-container", "children"),
    Output("results-player-info", "children"),
    Input("results-url", "search"),
)
def display_results(search):
    # Extract parameters from URL
    params = {}
    if search and search.startswith("?"):
        for param in search[1:].split("&"):
            if "=" in param:
                key, value = param.split("=", 1)
                params[key] = value
    
    player_name = params.get("player", "Anonymous")
    score = int(params.get("score", 0))
    total = int(params.get("total", 1))
    percentage = round((score / total) * 100, 1) if total > 0 else 0
    
    # Get player ranking information
    ranking = get_player_ranking(player_name)
    rank = ranking["rank"]
    total_players = ranking["total_players"]
    
    # Get player's historical scores
    player_scores = get_player_scores(player_name)
    
    # Create score gauge
    gauge = go.Figure(go.Indicator(
        domain = {'x': [0, 1], 'y': [0, 1]},
        value = percentage,
        mode = "gauge+number+delta",
        title = {'text': "Score"},
        delta = {'reference': 70},
        gauge = {
            'axis': {'range': [None, 100]},
            'bar': {'color': "darkblue"},
            'steps' : [
                {'range': [0, 50], 'color': "red"},
                {'range': [50, 70], 'color': "orange"},
                {'range': [70, 100], 'color': "green"},
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 70
            }
        }
    ))
    
    gauge.update_layout(height=300, margin=dict(t=0, b=0, l=0, r=0))
    
    # Create player info header
    player_info = html.Div([
        html.H4(f"Results for: {player_name}", className="mb-2"),
        html.Div([
            dbc.Badge(f"Rank: {rank}/{total_players}", 
                     color="primary", className="me-2"),
            dbc.Badge(f"Score: {score}/{total}", 
                     color="success" if percentage >= 70 else "warning"),
        ])
    ])
    
    # Create results container
    results = html.Div([
        dbc.Row([
            # Score card
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H4("Your Score", className="mb-0")),
                    dbc.CardBody([
                        html.Div([
                            html.H1(f"{score}/{total}", className="display-4 text-center"),
                            html.P(f"{percentage}%", className="text-center lead"),
                            dbc.Progress(value=percentage, className="mb-3"),
                        ]),
                        html.P(
                            "Excellent job! You're a quiz master!" 
                            if percentage >= 80 else
                            "Good effort! Keep practicing to improve!" 
                            if percentage >= 50 else
                            "Keep learning and try again soon!"
                        )
                    ])
                ]),
            ], md=6),
            
            # Score gauge visualization
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H4("Performance", className="mb-0")),
                    dbc.CardBody([
                        dcc.Graph(figure=gauge, config={"displayModeBar": False})
                    ])
                ])
            ], md=6)
        ], className="mb-4"),
        
        # Previous scores (if any)
        dbc.Card([
            dbc.CardHeader(html.H4("Your Score History", className="mb-0")),
            dbc.CardBody([
                html.Div([
                    "You haven't taken any quizzes before this one."
                ]) if len(player_scores) <= 1 else
                dbc.Table([
                    html.Thead(html.Tr([
                        html.Th("Date"),
                        html.Th("Score"),
                        html.Th("Performance"),
                    ])),
                    html.Tbody([
                        html.Tr([
                            html.Td(score["timestamp"]),
                            html.Td(f"{score['score']}/{score['total']}"),
                            html.Td([
                                dbc.Progress(
                                    value=score["percentage"], 
                                    color="success" if score["percentage"] >= 70 else "warning",
                                    style={"height": "15px"}
                                )
                            ])
                        ]) for score in player_scores[:5]  # Show latest 5 scores
                    ])
                ], bordered=True, hover=True)
            ])
        ], className="mb-4"),
        
        # Action buttons
        html.Div([
            dbc.Button("Play Again", color="primary", href="/join", className="me-2"),
            dbc.Button("View Leaderboard", color="info", href="/leaderboard", className="me-2"),
            dbc.Button("Home", color="secondary", href="/")
        ], className="d-flex justify-content-center mt-4")
    ])
    
    return results, player_info