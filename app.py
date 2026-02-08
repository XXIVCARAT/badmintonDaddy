"""
Badminton Daddy - Match tracking and ranking application.

A Flask web application for tracking badminton matches, maintaining player rankings,
and managing live scoreboard tracking for singles and doubles matches.
"""
import os
from flask import Flask
from models import db
from routes import main_bp, api_bp
from database import init_db
from config import config_by_name


def create_app(config_name: str = None) -> Flask:
    """
    Application factory function.
    
    Args:
        config_name: Configuration name ('development', 'production'). 
                    Defaults to environment variable or 'development'.
    
    Returns:
        Configured Flask application instance.
    """
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    config = config_by_name.get(config_name, config_by_name['default'])
    
    # Create Flask app
    app = Flask(__name__)
    app.config.from_object(config)
    
    # Initialize database
    db.init_app(app)
    
    # Register blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp)
    
    # Initialize database tables and sample data
    with app.app_context():
        init_db(app)
    
    return app


app = create_app()

if __name__ == '__main__':
    app.run(debug=True)