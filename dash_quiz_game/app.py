import dash
from dash import Dash, html
import dash_bootstrap_components as dbc

# Initialize the app with bootstrap theme and multi-page support
app = Dash(__name__, 
           use_pages=True, 
           external_stylesheets=[dbc.themes.BOOTSTRAP],
           meta_tags=[{'name': 'viewport', 'content': 'width=device-width, initial-scale=1.0'}])

# App layout with navigation
app.layout = html.Div([
    # Navigation component
    html.Div(
        dbc.NavbarSimple(
            brand="Quiz Game",
            brand_href="/",
            color="primary",
            dark=True,
            # Pass nav items as children instead of using 'links'
            children=[
                dbc.NavItem(dbc.NavLink("Home", href="/")),
                dbc.NavItem(dbc.NavLink("Join Game", href="/join")),  # Add this line
                dbc.NavItem(dbc.NavLink("Quiz", href="/quiz")),
                dbc.NavItem(dbc.NavLink("Leaderboard", href="/leaderboard")),
                dbc.NavItem(dbc.NavLink("My Scores", href="/my-scores")),
                dbc.NavItem(dbc.NavLink("Host", href="/host")),  # Add this line

            ]
        )
    ),
    
    # Content for each page
    dash.page_container
])

if __name__ == '__main__':
    app.run_server(debug=True)