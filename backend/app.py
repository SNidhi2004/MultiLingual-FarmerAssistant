from flask import Flask
from flask_cors import CORS

from auth import auth_bp
from routes.session_routes import session_bp
from routes.plant_routes import plant_bp


def create_app():
    app = Flask(__name__)

    # Enable CORS for frontend (React)
    CORS(app)

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(session_bp)
    app.register_blueprint(plant_bp)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
