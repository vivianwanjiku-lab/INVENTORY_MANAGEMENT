from flask import Flask

def create_app():
    """Application factory function"""
    app = Flask(__name__)
    app.config['DEBUG'] = True
    
    # Register blueprints
    from app.api.routes import api_blueprint
    app.register_blueprint(api_blueprint)
    
    return app
