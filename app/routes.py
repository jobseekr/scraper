"""Routes for parent Flask app."""
from flask import current_app as app


@app.route('/')
def home():
    """Landing page."""
    return "Hello, World"
