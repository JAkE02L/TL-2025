from dash import html, dcc
import dash_bootstrap_components as dbc

def create_quiz_card(question_text, options, question_number=None, total_questions=None):
    """
    Creates a card component for displaying quiz questions
    
    Args:
        question_text: The question text
        options: List of answer options
        question_number: Current question number (optional)
        total_questions: Total number of questions (optional)
    """
    header = html.Div([
        html.H4(question_text, className="card-title"),
        html.P(f"Question {question_number} of {total_questions}", className="text-muted") 
            if question_number and total_questions else None
    ])
    
    option_buttons = [
        dbc.RadioItems(
            options=[{"label": opt, "value": opt} for opt in options],
            id="answer-options",
            className="mb-3"
        )
    ]
    
    footer = dbc.Button("Submit Answer", id="submit-answer", color="primary", className="mt-2")
    
    card = dbc.Card([
        dbc.CardBody([header, html.Hr()] + option_buttons + [footer])
    ], className="quiz-card")
    
    return card