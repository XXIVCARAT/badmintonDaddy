"""
Badminton Daddy - Match tracking and ranking application.

A Flask web application for tracking badminton matches, maintaining player rankings,
and managing live scoreboard tracking for singles and doubles matches.
"""
import os
import logging
from flask import Flask, jsonify
from models import db
from routes import main_bp, api_bp
from database import init_db
from config import config_by_name
from errors import AppError, error_response


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


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
    
    # Register error handlers
    register_error_handlers(app)
    
    # Initialize database tables and sample data
    with app.app_context():
        init_db(app)
    
    logger.info(f"Application created in {config_name} mode")
    
    return app


def register_error_handlers(app: Flask) -> None:
    """Register error handlers for the application."""
    
    @app.errorhandler(AppError)
    def handle_app_error(error: AppError):
        """Handle custom application errors."""
        logger.warning(f"Application error: {error.message}")
        return error_response(error.message, error.status_code, error.data)
    
    @app.errorhandler(400)
    def handle_bad_request(error):
        """Handle 400 Bad Request errors."""
        return error_response("Bad Request", 400)
    
    @app.errorhandler(404)
    def handle_not_found(error):
        """Handle 404 Not Found errors."""
        return error_response("Resource not found", 404)
    
    @app.errorhandler(500)
    def handle_internal_error(error):
        """Handle 500 Internal Server errors."""
        logger.error(f"Internal server error: {str(error)}")
        return error_response("Internal server error", 500)
    
    @app.exception_handler(Exception)
    def handle_unexpected_error(error):
        """Handle unexpected exceptions."""
        logger.error(f"Unexpected error: {str(error)}", exc_info=True)
        return error_response("An unexpected error occurred", 500)


app = create_app()

if __name__ == '__main__':
    app.run(debug=True)