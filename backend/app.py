from flask import Flask
from flask_cors import CORS
from config import Config
from models import db


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # CORS for Vue.js dev server
    CORS(app, resources={r"/api/*": {"origins": ["http://localhost:5173", "http://localhost:3000"]}})

    db.init_app(app)

    # Register blueprints
    from routes.models import models_bp
    from routes.development import development_bp
    from routes.dashboard import dashboard_bp

    app.register_blueprint(models_bp, url_prefix="/api/models")
    app.register_blueprint(development_bp, url_prefix="/api/development")
    app.register_blueprint(dashboard_bp, url_prefix="/api/dashboard")

    # Create tables
    with app.app_context():
        import models.scorecard  # noqa: F401
        import models.development  # noqa: F401
        db.create_all()

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=5000)
