import re
from flask import Blueprint, jsonify
from sqlalchemy import func, case
from sqlalchemy.orm import selectinload
from models import db
from models.scorecard import ModelInventory
from models.development import DevelopmentProject, DevelopmentStage

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/summary", methods=["GET"])
def get_summary():
    """Dashboard özet istatistikleri."""
    from datetime import date

    # Single query for model counts
    total_models, active_models, under_review = db.session.query(
        func.count(ModelInventory.id),
        func.count(case((ModelInventory.status == "active", 1))),
        func.count(case((ModelInventory.status == "under_review", 1))),
    ).one()

    # Single query for project counts
    total_projects, active_projects, completed_projects = db.session.query(
        func.count(DevelopmentProject.id),
        func.count(case((DevelopmentProject.status == "in_progress", 1))),
        func.count(case((DevelopmentProject.status == "completed", 1))),
    ).one()

    overdue_stages = DevelopmentStage.query.filter(
        DevelopmentStage.deadline < date.today(),
        DevelopmentStage.status != "completed"
    ).count()

    response = jsonify({
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
    response.headers["Cache-Control"] = "public, max-age=30"
    return response


@dashboard_bp.route("/model-types", methods=["GET"])
def model_type_distribution():
    """Skorkart kategori dağılımı (Başvuru / Davranış)."""
    results = db.session.query(
        ModelInventory.scorecard_category,
        func.count(ModelInventory.id)
    ).group_by(ModelInventory.scorecard_category).all()

    response = jsonify([{"type": r[0], "count": r[1]} for r in results])
    response.headers["Cache-Control"] = "public, max-age=30"
    return response


@dashboard_bp.route("/gini-overview", methods=["GET"])
def gini_overview():
    """Tüm modellerin güncel Gini değerleri."""
    models = ModelInventory.query.filter_by(status="active").all()
    response = jsonify([{
        "model_name": m.model_name,
        "scorecard_category": m.scorecard_category,
        "product_type": m.product_type,
        "gini_development": m.gini_development,
        "gini_validation": m.gini_validation,
        "gini_current": m.gini_current,
    } for m in models])
    response.headers["Cache-Control"] = "public, max-age=30"
    return response


@dashboard_bp.route("/development-progress", methods=["GET"])
def development_progress():
    """Owner bazında geliştirme ilerleme durumu."""
    projects = DevelopmentProject.query.options(
        selectinload(DevelopmentProject.stages)
    ).filter_by(status="in_progress").all()
    return jsonify([{
        "project_name": p.project_name,
        "owner": p.owner,
        "progress": p._calculate_progress(),
        "priority": p.priority,
        "target_end_date": p.target_end_date.isoformat() if p.target_end_date else None,
    } for p in projects])


_MONTHLY_RE = re.compile(r'^\d{4}-\d{2}$')


@dashboard_bp.route("/gini-alerts", methods=["GET"])
def gini_alerts():
    """Son 3 aylık izleme Ginisi'nde geliştirme Gini'sinden ≥5 puan sapma olan modeller."""
    models = ModelInventory.query.options(
        selectinload(ModelInventory.gini_history)
    ).filter(ModelInventory.status.in_(["active", "under_review"])).all()

    alerts = []
    for model in models:
        if model.gini_development is None:
            continue
        monthly = sorted(
            [g for g in model.gini_history if _MONTHLY_RE.match(g.period)],
            key=lambda g: g.period,
            reverse=True,
        )
        if len(monthly) < 3:
            continue
        last3 = monthly[:3]
        diffs = [model.gini_development - g.gini_value for g in last3]
        # Kontrol: her 3 ayda da mutlak sapma ≥ 0.05 (5 Gini puanı)
        if not all(abs(d) >= 0.05 for d in diffs):
            continue
        # Yön: düşüş mü yoksa artış mı?
        direction = "drop" if diffs[0] > 0 else "rise"
        alerts.append({
            "model_id": model.id,
            "model_name": model.model_name,
            "scorecard_category": model.scorecard_category,
            "product_type": model.product_type,
            "status": model.status,
            "owner": model.owner,
            "gini_development": model.gini_development,
            "last3_periods": [g.period for g in last3],
            "last3_values": [round(g.gini_value, 4) for g in last3],
            "last3_diffs": [round(d, 4) for d in diffs],
            "direction": direction,
        })

    # Sapma büyüklüğüne göre sırala (en kritik önce)
    alerts.sort(key=lambda a: abs(a["last3_diffs"][0]), reverse=True)

    response = jsonify(alerts)
    response.headers["Cache-Control"] = "public, max-age=60"
    return response
