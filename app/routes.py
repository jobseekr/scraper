"""Routes for parent Flask app."""
from flask import current_app as app


@app.route('/')
def home():
    """Landing page."""
    return "Hello, World", 200


@app.route("/login")
def login():
    return "Login Page", 200

