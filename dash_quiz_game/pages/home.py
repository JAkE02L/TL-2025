import dash
from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc

dash.register_page(__name__, path="/", title="Quiz Game - Home")

# Home page layout
layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1("Welcome to the Quiz Game!", className="text-center mb-4"),
            html.P("Test your knowledge with our fun quiz challenges.", className="lead text-center"),
            # Add a host button in the buttons div:
            html.Div([
                dbc.Button("Start Quiz", color="primary", href="/join", size="lg", className="me-2"),
                dbc.Button("Host Quiz", color="secondary", href="/host", size="lg", className="me-2"),
                dbc.Button("View Leaderboard", color="info", href="/leaderboard", size="lg"),
                dbc.Button("My Scores", color="success", href="/my-scores", size="lg"),

            ], className="d-flex justify-content-center mt-4")
        ], width=12)
    ])
], fluid=True, className="py-4")