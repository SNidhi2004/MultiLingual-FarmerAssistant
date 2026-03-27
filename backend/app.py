from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from auth import auth_bp
from routes.session_routes import session_bp
from routes.plant_routes import plant_bp
from config import JWT_SECRET


def create_app():
    app = Flask(__name__)
    
    # Configure JWT
    app.config['JWT_SECRET_KEY'] = JWT_SECRET
    
    CORS(app, origins=["http://localhost:5173", "https://mango-field-05b69e100.4.azurestaticapps.net"], supports_credentials=True)
    # Initialize JWT
    jwt = JWTManager(app)
    
    # Register blueprints - FIXED URL PREFIXES to match frontend
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(session_bp, url_prefix='/session')
    app.register_blueprint(plant_bp, url_prefix='/plant')
    
    print("\n=== REGISTERED ROUTES ===")
    for rule in app.url_map.iter_rules():
        print(f"{rule.endpoint}: {rule.rule}")
    print("========================")
    # ✅ Test route INSIDE the function
    @app.route('/cors-test', methods=['GET', 'OPTIONS'])
    def cors_test():
        return {"message": "CORS is working!", "status": "success"}, 200
    
    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)