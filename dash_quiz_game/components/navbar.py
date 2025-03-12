from dash import html, dcc
import dash_bootstrap_components as dbc

def create_navbar():
    """
    Creates a navigation bar for the quiz application
    """
    return dbc.NavbarSimple(
        brand="Quiz Game",
        brand_href="/",
        color="primary",
        dark=True,
        links=[
            dbc.NavItem(dbc.NavLink("Home", href="/")),
            dbc.NavItem(dbc.NavLink("Quiz", href="/quiz")),
            dbc.NavItem(dbc.NavLink("Leaderboard", href="/leaderboard")),
        ]
    )