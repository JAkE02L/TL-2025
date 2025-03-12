import dash
from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc
from utils.score_manager import get_leaderboard
import plotly.express as px
import pandas as pd

dash.register_page(__name__, title="Quiz Game - Leaderboard")

# Leaderboard page layout
layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H2("Leaderboard", className="text-center mb-4"),
            html.P("Top scorers from our quiz champions!", className="text-center mb-4")
        ], width=12)
    ]),
    
    dbc.Row([
        # Top scorer podium
        dbc.Col([
            html.Div(id="leaderboard-podium")
        ], width=12, className="mb-4")
    ]),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H4("Top Players", className="mb-0")),
                dbc.CardBody([
                    html.Div(id="leaderboard-table")
                ])
            ])
        ], width={"size": 10, "offset": 1})
    ]),
    
    dbc.Row([
        dbc.Col([
            html.Div([
                dbc.Button("Play Quiz", color="primary", href="/join", className="me-2"),
                dbc.Button("Home", color="secondary", href="/")
            ], className="d-flex justify-content-center mt-4")
        ], width=12)
    ])
], fluid=True, className="py-4")

@callback(
    [Output("leaderboard-podium", "children"),
     Output("leaderboard-table", "children")],
    Input("_", "children")  # Dummy input to trigger on page load
)
def update_leaderboard(_):
    # Get leaderboard data
    leaderboard_data = get_leaderboard(limit=10)
    
    # Create table display
    if not leaderboard_data:
        table = html.Div("No scores recorded yet!", className="text-center p-3")
    else:
        table = dbc.Table([
            html.Thead(html.Tr([
                html.Th("Rank"),
                html.Th("Player"),
                html.Th("Score"),
                html.Th("Performance")
            ])),
            html.Tbody([
                html.Tr([
                    html.Td(entry["rank"], className="fw-bold" if entry["rank"] <= 3 else ""),
                    html.Td(entry["player"]),
                    html.Td(f"{entry['score']}/{entry['total']}"),
                    html.Td([
                        dbc.Progress(
                            value=entry["percentage"], 
                            color="success" if entry["percentage"] >= 70 else "warning",
                            className="mb-1",
                            style={"height": "15px"}
                        ),
                        f"{entry['percentage']}%"
                    ])
                ]) for entry in leaderboard_data
            ])
        ], bordered=True, hover=True, responsive=True, striped=True)
    
    # Create podium visualization for top 3 players
    if len(leaderboard_data) >= 3:
        top_three = leaderboard_data[:3]
        
        # Calculate heights for visual representation
        heights = {
            1: 200,  # Winner
            2: 150,  # Second place
            3: 100,  # Third place
        }
        
        # Create podium component
        podium = dbc.Card([
            dbc.CardBody([
                html.H4("Champions Podium", className="text-center mb-4"),
                html.Div([
                    # Second place
                    html.Div([
                        html.Div([
                            html.H5(top_three[1]["player"], className="text-center text-nowrap"),
                            html.P(f"{top_three[1]['percentage']}%", className="mb-0 text-center"),
                            dbc.Badge("2", color="secondary", className="position-absolute top-0 start-50 translate-middle")
                        ], className="p-2"),
                    ], className="d-flex align-items-end", style={"height": f"{heights[2]}px"}),
                    
                    # First place
                    html.Div([
                        html.Div([
                            html.H4(top_three[0]["player"], className="text-center text-nowrap"),
                            html.P(f"{top_three[0]['percentage']}%", className="mb-0 text-center"),
                            dbc.Badge("1", color="warning", className="position-absolute top-0 start-50 translate-middle")
                        ], className="p-2"),
                    ], className="d-flex align-items-end", style={"height": f"{heights[1]}px"}),
                    
                    # Third place
                    html.Div([
                        html.Div([
                            html.H5(top_three[2]["player"], className="text-center text-nowrap"),
                            html.P(f"{top_three[2]['percentage']}%", className="mb-0 text-center"),
                            dbc.Badge("3", color="danger", className="position-absolute top-0 start-50 translate-middle")
                        ], className="p-2"),
                    ], className="d-flex align-items-end", style={"height": f"{heights[3]}px"}),
                ], className="d-flex justify-content-center align-items-end", 
                   style={"gap": "20px"}),
                
                # Podium base
                html.Div(className="bg-secondary w-100 mt-2", style={"height": "20px"})
            ])
        ], className="mb-4")
        
        return podium, table
    
    # Dummy podium if not enough players
    dummy_podium = html.Div()
    return dummy_podium, table