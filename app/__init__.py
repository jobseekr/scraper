import dash
from flask import Flask
from flask.helpers import get_root_path
# from flask_login import login_required

# from config import BaseConfig


def create_app():
    server = Flask(__name__)
    # server.config.from_object(BaseConfig)

    register_dashapp(server)
    register_extensions(server)
    register_blueprints(server)

    return server


def register_dashapp(app):
    from app.dashapp.layout import serve_layout
    from app.dashapp.callbacks import register_callbacks

    # Meta tags for viewport responsiveness
    meta_viewport = {"name": "viewport", "content": "width=device-width, initial-scale=1, shrink-to-fit=no"}

    dashapp = dash.Dash(__name__,
                         server=app,
                         url_base_pathname='/dashboard/',
                         assets_folder=get_root_path(__name__) + '/dashboard/assets/',
                         meta_tags=[meta_viewport])

    with app.app_context():
        dashapp.title = 'Dashapp 1'
        dashapp.layout = serve_layout
        register_callbacks(dashapp)

    _protect_dashviews(dashapp)


def _protect_dashviews(dashapp):
    for view_func in dashapp.server.view_functions:
        if view_func.startswith(dashapp.config.url_base_pathname):
            dashapp.server.view_functions[view_func] = login_required(dashapp.server.view_functions[view_func])


def register_extensions(server):
    from app.extensions import db
    from app.extensions import login
    from app.extensions import migrate

    db.init_app(server)
    login.init_app(server)
    login.login_view = 'main.login'
    migrate.init_app(server, db)


def register_blueprints(server):
    from app.webapp import server_bp

    server.register_blueprint(server_bp)