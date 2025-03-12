import dash
from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
import json
import pandas as pd
import plotly.express as px

dash.register_page(__name__, title="Quiz Game - My Scores")

# Mock user history data - in a real app, this would come from a database
# based on the authenticated user
mock_user_history = [
    {"date": "2023-04-01", "quiz_id": 1, "score": 4, "total": 5, "percentage": 80},
    {"date": "2023-04-02", "quiz_id": 2, "score": 7, "total": 10, "percentage": 70},
    {"date": "2023-04-05", "quiz_id": 1, "score": 5, "total": 5, "percentage": 100},
    {"date": "2023-04-10", "quiz_id": 3, "score": 8, "total": 15, "percentage": 53},
    {"date": "2023-04-15", "quiz_id": 2, "score": 9, "total": 10, "percentage": 90}
]

# My scores page layout
layout = dbc.Container([
    dcc.Store(id="user-scores-data"),
    
    dbc.Row([
        dbc.Col([
            html.H2("My Quiz Scores", className="text-center mb-4"),
            html.Div(id="user-info", className="text-center mb-4")
        ], width=12)
    ]),
    
    dbc.Row([
        # Left column: Score summary
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H4("Score Summary", className="mb-0")),
                dbc.CardBody([
                    html.Div([
                        html.H5("Latest Score"),
                        html.Div([
                            html.H2(id="latest-score", className="d-inline"),
                            html.Span(" points", className="text-muted")
                        ]),
                        dbc.Progress(id="latest-score-progress", className="mb-3"),
                    ]),
                    html.Hr(),
                    html.Div([
                        html.H5("Overall Statistics"),
                        dbc.Row([
                            dbc.Col([
                                html.Div("Quizzes Taken", className="text-muted"),
                                html.H4(id="quizzes-taken")
                            ], width=4),
                            dbc.Col([
                                html.Div("Average Score", className="text-muted"),
                                html.H4(id="average-score")
                            ], width=4),
                            dbc.Col([
                                html.Div("Best Score", className="text-muted"),
                                html.H4(id="best-score")
                            ], width=4)
                        ])
                    ])
                ])
            ])
        ], width=5),
        
        # Right column: Performance chart
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H4("Performance Over Time", className="mb-0")),
                dbc.CardBody([
                    dcc.Graph(id="score-history-graph")
                ])
            ])
        ], width=7)
    ]),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H4("Score History", className="mb-0")),
                dbc.CardBody([
                    html.Div(id="score-history-table")
                ])
            ])
        ], width=12)
    ], className="mt-4"),
    
    dbc.Row([
        dbc.Col([
            html.Div([
                dbc.Button("Play Again", color="primary", href="/join", className="me-2"),
                dbc.Button("Home", color="secondary", href="/"),
                dbc.Button("Leaderboard", color="info", href="/leaderboard", className="ms-2"),
            ], className="d-flex justify-content-center mt-4")
        ], width=12)
    ])
], fluid=True, className="py-4")

@callback(
    [Output("user-info", "children"),
     Output("user-scores-data", "data"),
     Output("latest-score", "children"),
     Output("latest-score-progress", "value"),
     Output("quizzes-taken", "children"),
     Output("average-score", "children"),
     Output("best-score", "children"),
     Output("score-history-graph", "figure"),
     Output("score-history-table", "children")],
    [Input("url", "search")]
)
def update_user_scores(search):
    # In a real app, we would get the user ID from session/auth
    # and load scores from a database
    
    # For now, use mock data
    scores = mock_user_history
    
    # Convert to DataFrame for easier manipulation
    df = pd.DataFrame(scores)
    
    # Calculate statistics
    quizzes_taken = len(df)
    avg_score_percent = df["percentage"].mean()
    best_score = df["percentage"].max()
    
    # Get latest score data
    latest = df.iloc[-1]
    latest_score = f"{latest['score']}/{latest['total']}"
    latest_percent = latest["percentage"]
    
    # Create performance graph
    fig = px.line(
        df, 
        x="date", 
        y="percentage", 
        title="Score Percentage Over Time",
        labels={"percentage": "Score %", "date": "Date"},
        markers=True
    )
    fig.update_layout(
        margin=dict(l=40, r=40, t=40, b=40),
        yaxis_range=[0, 100]
    )
    
    # Create history table
    table = dbc.Table([
        html.Thead(html.Tr([
            html.Th("Date"),
            html.Th("Quiz"),
            html.Th("Score"),
            html.Th("Performance")
        ])),
        html.Tbody([
            html.Tr([
                html.Td(entry["date"]),
                html.Td(f"Quiz #{entry['quiz_id']}"),
                html.Td(f"{entry['score']}/{entry['total']}"),
                html.Td([
                    dbc.Progress(
                        value=entry["percentage"], 
                        style={"height": "15px"},
                        className="mb-1"
                    ),
                    f"{entry['percentage']}%"
                ])
            ]) for entry in scores
        ])
    ], bordered=True, hover=True, responsive=True, striped=True)
    
    # User info with name (would come from URL params or session)
    player_name = "Player"
    user_info = html.Div([
        html.H4(f"Scores for: {player_name}"),
        html.P("View your quiz performance and history")
    ])
    
    return (
        user_info, 
        json.dumps(scores),
        latest_score,
        latest_percent, 
        quizzes_taken,
        f"{avg_score_percent:.1f}%",
        f"{best_score}%",
        fig,
        table
    )