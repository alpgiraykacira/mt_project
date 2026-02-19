from flask import Blueprint, jsonify
from sqlalchemy import func
from models import db
from models.scorecard import ModelInventory, GiniHistory
from models.development import DevelopmentProject, DevelopmentStage

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/summary", methods=["GET"])
def get_summary():
    """Dashboard özet istatistikleri."""
    total_models = ModelInventory.query.count()
    active_models = ModelInventory.query.filter_by(status="active").count()
    under_review = ModelInventory.query.filter_by(status="under_review").count()

    total_projects = DevelopmentProject.query.count()
    active_projects = DevelopmentProject.query.filter_by(status="in_progress").count()
    completed_projects = DevelopmentProject.query.filter_by(status="completed").count()

    # Overdue stages (deadline passed but not completed)
    from datetime import date
    overdue_stages = DevelopmentStage.query.filter(
        DevelopmentStage.deadline < date.today(),
        DevelopmentStage.status != "completed"
    ).count()

    return jsonify({
        "models": {
            "total": total_models,
            "active": active_models,
            "under_review": under_review,
        },
        "development": {
            "total_projects": total_projects,
            "active_projects": active_projects,
            "completed_projects": completed_projects,
            "overdue_stages": overdue_stages,
        },
    })


@dashboard_bp.route("/model-types", methods=["GET"])
def model_type_distribution():
    """Model türü dağılımı."""
    results = db.session.query(
        ModelInventory.model_type,
        func.count(ModelInventory.id)
    ).group_by(ModelInventory.model_type).all()

    return jsonify([{"type": r[0], "count": r[1]} for r in results])


@dashboard_bp.route("/gini-overview", methods=["GET"])
def gini_overview():
    """Tüm modellerin güncel Gini değerleri."""
    models = ModelInventory.query.filter_by(status="active").all()
    return jsonify([{
        "model_name": m.model_name,
        "model_type": m.model_type,
        "gini_development": m.gini_development,
        "gini_validation": m.gini_validation,
        "gini_current": m.gini_current,
    } for m in models])


@dashboard_bp.route("/development-progress", methods=["GET"])
def development_progress():
    """Owner bazında geliştirme ilerleme durumu."""
    projects = DevelopmentProject.query.filter_by(status="in_progress").all()
    return jsonify([{
        "project_name": p.project_name,
        "owner": p.owner,
        "progress": p._calculate_progress(),
        "priority": p.priority,
        "target_end_date": p.target_end_date.isoformat() if p.target_end_date else None,
    } for p in projects])
