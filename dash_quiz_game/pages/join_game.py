import dash
from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate

dash.register_page(__name__, path="/join", title="Quiz Game - Join Game")

# Join game page layout
layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H2("Join Quiz Game", className="text-center mb-4"),
            html.P("Enter your name to start playing!", className="text-center mb-4")
        ], width=12)
    ]),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dbc.Input(
                        id="player-name",
                        placeholder="Your name",
                        type="text",
                        className="mb-3"
                    ),
                    html.Div(id="name-validation", className="text-danger mb-3"),
                    html.Div([
                        dbc.Button("Join Game", id="join-button", color="primary", className="me-2"),
                        dbc.Button("Back to Home", color="secondary", href="/")
                    ], className="d-flex justify-content-center")
                ])
            ], className="quiz-card")
        ], width={"size": 6, "offset": 3})
    ]),
    
    # For redirecting after form submission
    dcc.Location(id="url-redirect", refresh=True)
], fluid=True, className="py-4")

@callback(
    [Output("name-validation", "children"),
     Output("url-redirect", "href")],
    [Input("join-button", "n_clicks")],
    [State("player-name", "value")],
    prevent_initial_call=True
)
def validate_and_redirect(n_clicks, player_name):
    if not n_clicks:
        raise PreventUpdate
    
    if not player_name or len(player_name.strip()) == 0:
        return "Please enter your name", dash.no_update
    
    if len(player_name) > 20:
        return "Name must be 20 characters or less", dash.no_update
    
    # In a real app, you might store the player name in a session or database here
    # For now, we'll just redirect to the quiz page
    return "", f"/quiz?player={player_name}"