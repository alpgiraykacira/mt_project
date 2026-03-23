import io
from datetime import date
from flask import Blueprint, request, jsonify, send_file
from sqlalchemy.orm import selectinload
from models import db
from models.scorecard import ModelInventory, TechnicalGuide, ValidationReport, GiniHistory, ModelRollout, ModelVariable

models_bp = Blueprint("models", __name__)


# ── Model Inventory CRUD ──

@models_bp.route("/", methods=["GET"])
def list_models():
    """Tüm modelleri listele, filtreleme ve sayfalama destekli."""
    query = ModelInventory.query

    # Filters
    scorecard_category = request.args.get("scorecard_category")
    product_type = request.args.get("product_type")
    status = request.args.get("status")
    owner = request.args.get("owner")
    search = request.args.get("search")

    if scorecard_category:
        query = query.filter(ModelInventory.scorecard_category == scorecard_category)
    if product_type:
        query = query.filter(ModelInventory.product_type == product_type)
    if status:
        query = query.filter(ModelInventory.status == status)
    if owner:
        query = query.filter(ModelInventory.owner == owner)
    if search:
        query = query.filter(ModelInventory.model_name.ilike(f"%{search}%"))

    query = query.order_by(ModelInventory.updated_at.desc())

    # Pagination (optional: omit page param to get all results for backward compat)
    page = request.args.get("page", type=int)
    per_page = request.args.get("per_page", 20, type=int)
    if page is not None:
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        return jsonify({
            "items": [m.to_dict() for m in pagination.items],
            "total": pagination.total,
            "page": pagination.page,
            "per_page": pagination.per_page,
            "pages": pagination.pages,
        })

    return jsonify([m.to_dict() for m in query.all()])


@models_bp.route("/", methods=["POST"])
def create_model():
    """Yeni model oluştur."""
    data = request.get_json()
    model = ModelInventory(
        model_name=data["model_name"],
        scorecard_category=data["scorecard_category"],
        product_type=data.get("product_type"),
        development_period_start=_parse_date(data.get("development_period_start")),
        development_period_end=_parse_date(data.get("development_period_end")),
        oot_period_start=_parse_date(data.get("oot_period_start")),
        oot_period_end=_parse_date(data.get("oot_period_end")),
        validation_submission_date=_parse_date(data.get("validation_submission_date")),
        development_table=data.get("development_table"),
        target_variable=data.get("target_variable"),
        gini_development=data.get("gini_development"),
        gini_train=data.get("gini_train"),
        gini_cv=data.get("gini_cv"),
        gini_itt=data.get("gini_itt"),
        gini_oot=data.get("gini_oot"),
        gini_validation=data.get("gini_validation"),
        gini_current=data.get("gini_current"),
        final_score=data.get("final_score"),
        status=data.get("status", "active"),
        owner=data.get("owner"),
        description=data.get("description"),
        connected_processes=data.get("connected_processes"),
        dependency_warning=data.get("dependency_warning"),
        psi_flag=data.get("psi_flag", False),
        alert_work_started=data.get("alert_work_started", False),
    )
    db.session.add(model)
    db.session.commit()
    return jsonify(model.to_dict()), 201


@models_bp.route("/<int:model_id>", methods=["GET"])
def get_model(model_id):
    """Tek bir modelin detaylarını getir."""
    model = ModelInventory.query.options(
        selectinload(ModelInventory.technical_details),
        selectinload(ModelInventory.validation_reports),
        selectinload(ModelInventory.gini_history),
        selectinload(ModelInventory.rollout_stages),
        selectinload(ModelInventory.model_variables),
    ).get_or_404(model_id)
    data = model.to_dict()
    data["technical_details"] = [t.to_dict() for t in model.technical_details]
    data["validation_reports"] = [v.to_dict() for v in model.validation_reports]
    data["gini_history"] = [g.to_dict() for g in model.gini_history]
    data["rollout_stages"] = sorted([r.to_dict() for r in model.rollout_stages], key=lambda x: x["rollout_percentage"])
    data["model_variables"] = sorted([v.to_dict() for v in model.model_variables], key=lambda x: (x["importance_rank"] or 9999))
    return jsonify(data)


@models_bp.route("/<int:model_id>", methods=["PUT"])
def update_model(model_id):
    """Model bilgilerini güncelle."""
    model = db.get_or_404(ModelInventory, model_id)
    data = request.get_json()

    for field in ["model_name", "scorecard_category", "product_type", "development_table",
                   "target_variable", "gini_development", "gini_train", "gini_cv",
                   "gini_itt", "gini_oot", "gini_validation", "gini_current", "final_score",
                   "status", "owner", "description", "connected_processes", "dependency_warning",
                   "psi_flag", "alert_work_started"]:
        if field in data:
            setattr(model, field, data[field])

    for date_field in ["development_period_start", "development_period_end",
                        "oot_period_start", "oot_period_end", "validation_submission_date"]:
        if date_field in data:
            setattr(model, date_field, _parse_date(data[date_field]))

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
    """Yeni validasyon raporu ekle (JSON veya multipart form)."""
    db.get_or_404(ModelInventory, model_id)

    if request.content_type and "multipart/form-data" in request.content_type:
        # File upload
        report_name = request.form.get("report_name", "")
        report_type = request.form.get("report_type", "")
        report_date = request.form.get("report_date")
        notes = request.form.get("notes")
        file_obj = request.files.get("file")

        report = ValidationReport(
            model_id=model_id,
            report_name=report_name,
            report_type=report_type,
            report_date=_parse_date(report_date),
            notes=notes,
        )
        if file_obj:
            report.file_data = file_obj.read()
            report.file_mimetype = file_obj.mimetype
            report.file_path = file_obj.filename
    else:
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


@models_bp.route("/<int:model_id>/validations/<int:report_id>/download", methods=["GET"])
def download_validation(model_id, report_id):
    """Validasyon raporunu indir."""
    report = db.get_or_404(ValidationReport, report_id)
    if not report.file_data:
        return jsonify({"error": "Dosya bulunamadı"}), 404

    mimetype = report.file_mimetype or "application/octet-stream"
    filename = report.file_path or report.report_name
    return send_file(
        io.BytesIO(report.file_data),
        mimetype=mimetype,
        as_attachment=True,
        download_name=filename,
    )


@models_bp.route("/<int:model_id>/validations/<int:report_id>", methods=["DELETE"])
def delete_validation(model_id, report_id):
    report = db.get_or_404(ValidationReport, report_id)
    db.session.delete(report)
    db.session.commit()
    return "", 204


# ── Gini History ──

@models_bp.route("/<int:model_id>/gini-history", methods=["GET"])
def list_gini_history(model_id):
    # Tarih filtresi
    period_from = request.args.get("period_from")
    period_to = request.args.get("period_to")
    query = GiniHistory.query.filter_by(model_id=model_id)
    if period_from:
        query = query.filter(GiniHistory.period >= period_from)
    if period_to:
        query = query.filter(GiniHistory.period <= period_to)
    records = query.order_by(GiniHistory.period.desc()).all()
    return jsonify([r.to_dict() for r in records])


@models_bp.route("/<int:model_id>/gini-history", methods=["POST"])
def create_gini_record(model_id):
    db.get_or_404(ModelInventory, model_id)
    data = request.get_json()
    record = GiniHistory(
        model_id=model_id,
        period=data["period"],
        gini_value=data["gini_value"],
        target_ratio=data.get("target_ratio"),
        sample_size=data.get("sample_size"),
        notes=data.get("notes"),
    )
    db.session.add(record)
    db.session.commit()
    return jsonify(record.to_dict()), 201


# NOT: Gini geçmişi kayıtları silinmez (feedback gereği)


# ── Model Rollout (İmplementasyon Kademeleri) ──

@models_bp.route("/<int:model_id>/rollout", methods=["GET"])
def list_rollout(model_id):
    stages = ModelRollout.query.filter_by(model_id=model_id).order_by(ModelRollout.rollout_percentage).all()
    return jsonify([s.to_dict() for s in stages])


@models_bp.route("/<int:model_id>/rollout", methods=["POST"])
def create_rollout(model_id):
    db.get_or_404(ModelInventory, model_id)
    data = request.get_json()
    stage = ModelRollout(
        model_id=model_id,
        rollout_percentage=data["rollout_percentage"],
        rollout_date=_parse_date(data["rollout_date"]),
        notes=data.get("notes"),
    )
    db.session.add(stage)
    db.session.commit()
    return jsonify(stage.to_dict()), 201


@models_bp.route("/<int:model_id>/rollout/<int:stage_id>", methods=["PUT"])
def update_rollout(model_id, stage_id):
    stage = db.get_or_404(ModelRollout, stage_id)
    data = request.get_json()
    if "rollout_percentage" in data:
        stage.rollout_percentage = data["rollout_percentage"]
    if "rollout_date" in data:
        stage.rollout_date = _parse_date(data["rollout_date"])
    if "notes" in data:
        stage.notes = data["notes"]
    db.session.commit()
    return jsonify(stage.to_dict())


@models_bp.route("/<int:model_id>/rollout/<int:stage_id>", methods=["DELETE"])
def delete_rollout(model_id, stage_id):
    stage = db.get_or_404(ModelRollout, stage_id)
    db.session.delete(stage)
    db.session.commit()
    return "", 204


# ── Model Variables (Feature Importance) ──

@models_bp.route("/<int:model_id>/variables", methods=["GET"])
def list_variables(model_id):
    variables = ModelVariable.query.filter_by(model_id=model_id).order_by(
        ModelVariable.importance_rank.asc().nullslast()
    ).all()
    return jsonify([v.to_dict() for v in variables])


@models_bp.route("/<int:model_id>/variables", methods=["POST"])
def create_variable(model_id):
    db.get_or_404(ModelInventory, model_id)
    data = request.get_json()
    variable = ModelVariable(
        model_id=model_id,
        variable_name=data["variable_name"],
        variable_description=data.get("variable_description"),
        iv_value=data.get("iv_value"),
        importance_rank=data.get("importance_rank"),
        median_train=data.get("median_train"),
        coefficient=data.get("coefficient"),
        woe_bin_count=data.get("woe_bin_count"),
        notes=data.get("notes"),
    )
    db.session.add(variable)
    db.session.commit()
    return jsonify(variable.to_dict()), 201


@models_bp.route("/<int:model_id>/variables/<int:var_id>", methods=["PUT"])
def update_variable(model_id, var_id):
    variable = db.get_or_404(ModelVariable, var_id)
    data = request.get_json()
    for field in ["variable_name", "variable_description", "iv_value", "importance_rank",
                   "median_train", "coefficient", "woe_bin_count", "notes"]:
        if field in data:
            setattr(variable, field, data[field])
    db.session.commit()
    return jsonify(variable.to_dict())


@models_bp.route("/<int:model_id>/variables/<int:var_id>", methods=["DELETE"])
def delete_variable(model_id, var_id):
    variable = db.get_or_404(ModelVariable, var_id)
    db.session.delete(variable)
    db.session.commit()
    return "", 204


# ── Helpers ──

def _parse_date(date_str):
    if not date_str:
        return None
    return date.fromisoformat(date_str)
