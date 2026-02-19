from datetime import date
from flask import Blueprint, request, jsonify
from models import db
from models.scorecard import ModelInventory, TechnicalGuide, ValidationReport, GiniHistory

models_bp = Blueprint("models", __name__)


# ── Model Inventory CRUD ──

@models_bp.route("/", methods=["GET"])
def list_models():
    """Tüm modelleri listele, filtreleme destekli."""
    query = ModelInventory.query

    # Filters
    model_type = request.args.get("model_type")
    status = request.args.get("status")
    owner = request.args.get("owner")
    search = request.args.get("search")

    if model_type:
        query = query.filter(ModelInventory.model_type == model_type)
    if status:
        query = query.filter(ModelInventory.status == status)
    if owner:
        query = query.filter(ModelInventory.owner == owner)
    if search:
        query = query.filter(ModelInventory.model_name.ilike(f"%{search}%"))

    models = query.order_by(ModelInventory.updated_at.desc()).all()
    return jsonify([m.to_dict() for m in models])


@models_bp.route("/", methods=["POST"])
def create_model():
    """Yeni model oluştur."""
    data = request.get_json()
    model = ModelInventory(
        model_name=data["model_name"],
        model_type=data["model_type"],
        segment=data.get("segment"),
        development_period_start=_parse_date(data.get("development_period_start")),
        development_period_end=_parse_date(data.get("development_period_end")),
        development_table=data.get("development_table"),
        target_variable=data.get("target_variable"),
        gini_development=data.get("gini_development"),
        gini_validation=data.get("gini_validation"),
        gini_current=data.get("gini_current"),
        final_score=data.get("final_score"),
        status=data.get("status", "active"),
        owner=data.get("owner"),
        description=data.get("description"),
    )
    db.session.add(model)
    db.session.commit()
    return jsonify(model.to_dict()), 201


@models_bp.route("/<int:model_id>", methods=["GET"])
def get_model(model_id):
    """Tek bir modelin detaylarını getir."""
    model = db.get_or_404(ModelInventory, model_id)
    data = model.to_dict()
    data["technical_details"] = [t.to_dict() for t in model.technical_details]
    data["validation_reports"] = [v.to_dict() for v in model.validation_reports]
    data["gini_history"] = [g.to_dict() for g in model.gini_history]
    return jsonify(data)


@models_bp.route("/<int:model_id>", methods=["PUT"])
def update_model(model_id):
    """Model bilgilerini güncelle."""
    model = db.get_or_404(ModelInventory, model_id)
    data = request.get_json()

    for field in ["model_name", "model_type", "segment", "development_table",
                   "target_variable", "gini_development", "gini_validation",
                   "gini_current", "final_score", "status", "owner", "description"]:
        if field in data:
            setattr(model, field, data[field])

    if "development_period_start" in data:
        model.development_period_start = _parse_date(data["development_period_start"])
    if "development_period_end" in data:
        model.development_period_end = _parse_date(data["development_period_end"])

    db.session.commit()
    return jsonify(model.to_dict())


@models_bp.route("/<int:model_id>", methods=["DELETE"])
def delete_model(model_id):
    """Model sil."""
    model = db.get_or_404(ModelInventory, model_id)
    db.session.delete(model)
    db.session.commit()
    return "", 204


# ── Technical Guide ──

@models_bp.route("/<int:model_id>/technical", methods=["GET"])
def list_technical(model_id):
    guides = TechnicalGuide.query.filter_by(model_id=model_id).order_by(TechnicalGuide.order_index).all()
    return jsonify([g.to_dict() for g in guides])


@models_bp.route("/<int:model_id>/technical", methods=["POST"])
def create_technical(model_id):
    db.get_or_404(ModelInventory, model_id)
    data = request.get_json()
    guide = TechnicalGuide(
        model_id=model_id,
        section_title=data["section_title"],
        section_type=data.get("section_type"),
        content=data["content"],
        query_code=data.get("query_code"),
        order_index=data.get("order_index", 0),
    )
    db.session.add(guide)
    db.session.commit()
    return jsonify(guide.to_dict()), 201


@models_bp.route("/<int:model_id>/technical/<int:guide_id>", methods=["PUT"])
def update_technical(model_id, guide_id):
    guide = db.get_or_404(TechnicalGuide, guide_id)
    data = request.get_json()
    for field in ["section_title", "section_type", "content", "query_code", "order_index"]:
        if field in data:
            setattr(guide, field, data[field])
    db.session.commit()
    return jsonify(guide.to_dict())


@models_bp.route("/<int:model_id>/technical/<int:guide_id>", methods=["DELETE"])
def delete_technical(model_id, guide_id):
    guide = db.get_or_404(TechnicalGuide, guide_id)
    db.session.delete(guide)
    db.session.commit()
    return "", 204


# ── Validation Reports ──

@models_bp.route("/<int:model_id>/validations", methods=["GET"])
def list_validations(model_id):
    reports = ValidationReport.query.filter_by(model_id=model_id).order_by(ValidationReport.report_date.desc()).all()
    return jsonify([r.to_dict() for r in reports])


@models_bp.route("/<int:model_id>/validations", methods=["POST"])
def create_validation(model_id):
    db.get_or_404(ModelInventory, model_id)
    data = request.get_json()
    report = ValidationReport(
        model_id=model_id,
        report_name=data["report_name"],
        report_type=data["report_type"],
        file_path=data.get("file_path"),
        report_date=_parse_date(data.get("report_date")),
        notes=data.get("notes"),
    )
    db.session.add(report)
    db.session.commit()
    return jsonify(report.to_dict()), 201


@models_bp.route("/<int:model_id>/validations/<int:report_id>", methods=["DELETE"])
def delete_validation(model_id, report_id):
    report = db.get_or_404(ValidationReport, report_id)
    db.session.delete(report)
    db.session.commit()
    return "", 204


# ── Gini History ──

@models_bp.route("/<int:model_id>/gini-history", methods=["GET"])
def list_gini_history(model_id):
    records = GiniHistory.query.filter_by(model_id=model_id).order_by(GiniHistory.period).all()
    return jsonify([r.to_dict() for r in records])


@models_bp.route("/<int:model_id>/gini-history", methods=["POST"])
def create_gini_record(model_id):
    db.get_or_404(ModelInventory, model_id)
    data = request.get_json()
    record = GiniHistory(
        model_id=model_id,
        period=data["period"],
        gini_value=data["gini_value"],
        sample_size=data.get("sample_size"),
        notes=data.get("notes"),
    )
    db.session.add(record)
    db.session.commit()
    return jsonify(record.to_dict()), 201


@models_bp.route("/<int:model_id>/gini-history/<int:record_id>", methods=["DELETE"])
def delete_gini_record(model_id, record_id):
    record = db.get_or_404(GiniHistory, record_id)
    db.session.delete(record)
    db.session.commit()
    return "", 204


# ── Helpers ──

def _parse_date(date_str):
    if not date_str:
        return None
    return date.fromisoformat(date_str)
