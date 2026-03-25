import re
from flask import Blueprint, jsonify
from sqlalchemy import func, case
from sqlalchemy.orm import selectinload
from models import db
from models.scorecard import ModelInventory
from models.development import DevelopmentProject, DevelopmentStage

dashboard_bp = Blueprint("dashboard", __name__)

# Kategori bazlı Gini alert eşikleri
GINI_ALERT_THRESHOLD = {
    "Başvuru": 0.50,
    "Davranış": 0.55,
}
# Ardışık ay sayısı ve minimum puan sapması
CONSECUTIVE_MONTHS = 3
MIN_GINI_DIFF = 0.05


@dashboard_bp.route("/summary", methods=["GET"])
def get_summary():
    """Dashboard özet istatistikleri - mevcut ve geliştirilen skorkartlar ayrımıyla."""
    from datetime import date

    _active_filter = ModelInventory.status.in_(["active", "under_review"])

    # Single query for all model counts
    total_models, active_models, under_review, basvuru_count, davranis_count, \
        psi_flag_count, cal_warning, cal_critical = db.session.query(
        func.count(ModelInventory.id),
        func.count(case((ModelInventory.status == "active", 1))),
        func.count(case((ModelInventory.status == "under_review", 1))),
        func.count(case((_active_filter, case((ModelInventory.scorecard_category == "Başvuru", 1))))),
        func.count(case((_active_filter, case((ModelInventory.scorecard_category == "Davranış", 1))))),
        func.count(case((_active_filter, case((ModelInventory.psi_flag == True, 1))))),
        func.count(case((_active_filter, case((ModelInventory.calibration_status == "warning", 1))))),
        func.count(case((_active_filter, case((ModelInventory.calibration_status == "critical", 1))))),
    ).one()

    # Single query for all development counts
    total_projects, active_projects, completed_projects, dev_basvuru, dev_davranis = db.session.query(
        func.count(DevelopmentProject.id),
        func.count(case((DevelopmentProject.status == "in_progress", 1))),
        func.count(case((DevelopmentProject.status == "completed", 1))),
        func.count(case((
            (DevelopmentProject.status == "in_progress") & (DevelopmentProject.scorecard_category == "Başvuru"), 1
        ))),
        func.count(case((
            (DevelopmentProject.status == "in_progress") & (DevelopmentProject.scorecard_category == "Davranış"), 1
        ))),
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
            "basvuru": basvuru_count,
            "davranis": davranis_count,
            "psi_flag_count": psi_flag_count,
            "cal_warning": cal_warning,
            "cal_critical": cal_critical,
        },
        "development": {
            "total_projects": total_projects,
            "active_projects": active_projects,
            "completed_projects": completed_projects,
            "overdue_stages": overdue_stages,
            "dev_basvuru": dev_basvuru,
            "dev_davranis": dev_davranis,
        },
    })
    response.headers["Cache-Control"] = "public, max-age=30"
    return response


@dashboard_bp.route("/gini-overview", methods=["GET"])
def gini_overview():
    """Aktif modellerin Gini değerleri — Başvuru ve Davranış olarak ayrı döner."""
    models = ModelInventory.query.filter_by(status="active").all()

    dev_projects = DevelopmentProject.query.filter_by(status="in_progress").all()
    dev_set = {(p.scorecard_category, p.product_type) for p in dev_projects}

    basvuru = []
    davranis = []
    for m in models:
        entry = {
            "model_id": m.id,
            "model_name": m.model_name,
            "scorecard_category": m.scorecard_category,
            "product_type": m.product_type,
            "gini_development": m.gini_development,
            "gini_current": m.gini_current,
            "psi_flag": m.psi_flag or False,
            "calibration_status": m.calibration_status or "ok",
            "in_development": (m.scorecard_category, m.product_type) in dev_set,
        }
        if m.scorecard_category == "Başvuru":
            basvuru.append(entry)
        else:
            davranis.append(entry)

    response = jsonify({"basvuru": basvuru, "davranis": davranis})
    response.headers["Cache-Control"] = "public, max-age=30"
    return response


@dashboard_bp.route("/development-progress", methods=["GET"])
def development_progress():
    """Owner bazında geliştirme ilerleme durumu."""
    projects = DevelopmentProject.query.options(
        selectinload(DevelopmentProject.stages)
    ).filter_by(status="in_progress").all()
    return jsonify([{
        "project_id": p.id,
        "project_name": p.project_name,
        "owner": p.owner,
        "scorecard_category": p.scorecard_category,
        "product_type": p.product_type,
        "progress": p._calculate_progress(),
        "priority": p.priority,
        "target_end_date": p.target_end_date.isoformat() if p.target_end_date else None,
    } for p in projects])


_MONTHLY_RE = re.compile(r'^\d{4}-\d{2}$')


@dashboard_bp.route("/gini-alerts", methods=["GET"])
def gini_alerts():
    """
    Gini alert sistemi:
    - Başvuru modelleri: güncel gini < 0.50 VEYA son 3 ayda ≥5pp ardışık sapma
    - Davranış modelleri: güncel gini < 0.55 VEYA son 3 ayda ≥5pp ardışık sapma
    - PSI flag bağımsız olarak ayrıca dönülür.
    """
    models = ModelInventory.query.options(
        selectinload(ModelInventory.gini_history)
    ).filter(ModelInventory.status.in_(["active", "under_review"])).all()

    alerts = []
    for model in models:
        if model.gini_development is None:
            continue

        # Son 3 aylık kayıt kontrolü
        monthly = sorted(
            [g for g in model.gini_history if _MONTHLY_RE.match(g.period)],
            key=lambda g: g.period,
            reverse=True,
        )

        threshold = GINI_ALERT_THRESHOLD.get(model.scorecard_category, 0.50)

        gini_alert = False
        alert_reason = []
        diffs = []
        last3 = []

        # Ardışık sapma kuralı
        if len(monthly) >= CONSECUTIVE_MONTHS:
            last3 = monthly[:CONSECUTIVE_MONTHS]
            diffs = [model.gini_development - g.gini_value for g in last3]
            if all(abs(d) >= MIN_GINI_DIFF for d in diffs):
                gini_alert = True
                alert_reason.append("consecutive_deviation")

        # Eşik kontrolü (güncel gini < threshold)
        if model.gini_current is not None and model.gini_current < threshold:
            gini_alert = True
            alert_reason.append("threshold_breach")

        if not gini_alert and not model.psi_flag:
            continue

        direction = None
        if diffs:
            direction = "drop" if diffs[0] > 0 else "rise"

        alerts.append({
            "model_id": model.id,
            "model_name": model.model_name,
            "scorecard_category": model.scorecard_category,
            "product_type": model.product_type,
            "status": model.status,
            "gini_development": model.gini_development,
            "gini_current": model.gini_current,
            "gini_threshold": threshold,
            "last3_periods": [g.period for g in last3],
            "last3_values": [round(g.gini_value, 4) for g in last3],
            "last3_diffs": [round(d, 4) for d in diffs],
            "direction": direction,
            "alert_reason": alert_reason,
            "gini_alert": gini_alert,
            "psi_flag": model.psi_flag or False,
            "alert_work_started": model.alert_work_started or False,
        })

    # Önce Gini alert olanlar, sonra sadece PSI flag olanlar; sapma büyüklüğüne göre
    alerts.sort(key=lambda a: (
        0 if a["gini_alert"] else 1,
        -(abs(a["last3_diffs"][0]) if a["last3_diffs"] else 0),
    ))

    response = jsonify(alerts)
    response.headers["Cache-Control"] = "public, max-age=60"
    return response
