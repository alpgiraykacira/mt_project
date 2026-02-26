import os
from flask import Flask, jsonify
from flask_cors import CORS
from config import Config
from models import db


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # CORS - configurable via CORS_ORIGINS env variable
    cors_origins = os.getenv(
        "CORS_ORIGINS",
        "https://scorecard_dashboard_agk.onrender.com"
    ).split(",")
    CORS(app, origins=cors_origins)

    db.init_app(app)

    # Register blueprints
    from routes.models import models_bp
    from routes.development import development_bp
    from routes.dashboard import dashboard_bp

    app.register_blueprint(models_bp, url_prefix="/api/models")
    app.register_blueprint(development_bp, url_prefix="/api/development")
    app.register_blueprint(dashboard_bp, url_prefix="/api/dashboard")

    # Health check endpoint for testing connectivity
    @app.route("/")
    def index():
        return jsonify({"status": "ok", "message": "MT Dashboard API is running"})

    # Create tables and auto-seed if empty
    with app.app_context():
        import models.scorecard  # noqa: F401
        import models.development  # noqa: F401
        db.create_all()

        from models.scorecard import ModelInventory
        if ModelInventory.query.count() == 0:
            from seed_data import seed_db
            seed_db()

    return app


if __name__ == "__main__":
    app = create_app()
    # host=0.0.0.0 -> container/pod icinden proxy erisimi icin gerekli
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
