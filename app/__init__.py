from flask import Flask

def create_app():
    app = Flask(__name__)

    # Import routes after creating app to avoid circular import issues
    from .routes import main
    app.register_blueprint(main)

    return app
